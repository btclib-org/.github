# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What section 10 says every workflow does, asked of every workflow.

The three findings section 15 names as findings on their own -- an
action not pinned to a commit, a workflow with no `permissions:` block,
a step passing `--frozen` -- each read from the document rather than
grepped for: a comment arguing against `--frozen` is not a step passing
it, and the grep section 15 gives reports both alike. The grep is what
the failure message carries, because it is what a person runs.

A tag comment is a YAML comment, and the parser has dropped it by the
time it returns. `pinned` reads it off the file's text instead, counting
what the text gives against what the document uses so that a pattern
which stops matching is an error rather than a run over nothing.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
from collections import Counter
from typing import TYPE_CHECKING, Any, NamedTuple

import pytest
import yaml

from . import ORG, ROOT, SELF, by_hand

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

PINNED = re.compile(r"@[0-9a-f]{40}$")
"""Forty hex digits after the `@`, which is what a tag is not."""

LOCAL = "./"
"""A `uses:` into this tree, which has no revision to pin.

A composite action or a reusable workflow called by path runs at the
calling commit, so there is nothing its owner could move.
"""

REUSABLE = re.compile(
    rf"^{re.escape(ORG)}/{re.escape(SELF)}/\.github/workflows/reusable-[\w-]+\.yml@main$"
)
"""A call to a reusable workflow of this repository, at section 10's `@main`."""


def workflows(root: Path) -> list[Path]:
    """List every workflow file of a tree, both suffixes, sorted.

    :param root: the root of the checkout.
    :returns: the files, empty where the tree has none.
    """
    here = root / ".github" / "workflows"
    return sorted(path for suffix in ("*.yml", "*.yaml") for path in here.glob(suffix))


def document(workflow: Path) -> dict[Any, Any]:
    """Parse a workflow file.

    Keyed on whatever YAML read rather than on `str`, for the key
    `triggers` looks up.

    :param workflow: the file to read.
    :returns: the document, empty where the file parses to nothing.
    """
    parsed = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    return parsed if isinstance(parsed, dict) else {}


def triggers(workflow: Path) -> dict[str, Any]:
    """Read the `on:` block of a workflow file.

    YAML 1.1 reads a bare `on` as the boolean it also spells `true`,
    which is why the key is looked for twice: what the file means is the
    same either way, and which one the parser hands back depends on how
    the file happens to quote it.

    :param workflow: the file to read.
    :returns: the trigger block, empty if the file declares none.
    """
    parsed = document(workflow)
    on = parsed.get("on", parsed.get(True, {}))
    return on if isinstance(on, dict) else {}


def jobs(workflow: Path) -> dict[str, dict[str, Any]]:
    """Read a workflow's jobs, by id.

    :param workflow: the file to read.
    :returns: the job mappings, empty where the file declares none.
    """
    return document(workflow).get("jobs") or {}


def steps(workflow: Path) -> list[dict[str, Any]]:
    """List every step of every job of a workflow, in file order.

    :param workflow: the file to read.
    :returns: the step mappings, empty for a workflow of calls alone.
    """
    return [
        step for job in jobs(workflow).values() for step in (job.get("steps") or [])
    ]


def uses(workflow: Path) -> list[str]:
    """List what a workflow `uses:`, its jobs' calls and its steps' actions.

    Section 10's rule on what a `uses:` may name does not tell the two
    apart: a job calling another workflow names a revision as a step
    naming an action does.

    :param workflow: the file to read.
    :returns: the values, the jobs' after the steps'.
    """
    return [
        *(step["uses"] for step in steps(workflow) if "uses" in step),
        *(job["uses"] for job in jobs(workflow).values() if "uses" in job),
    ]


def gated(repository: str, trees: dict[str, Path]) -> list[Path]:
    """List the workflows of one repository, or skip where it has none.

    A tree with no `.github/workflows/` has nothing section 10 can be
    asked about, and whether it owes one follows from its tier in
    section 2 rather than from anything here; btclib-org/.github#107 is
    where that was settled. Skipped with the reason so the cell says so.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the workflow files.
    """
    found = workflows(trees[repository])
    if not found:
        pytest.skip(f"{repository} has no .github/workflows/")
    return found


NEEDS_OUTPUT = re.compile(r"\bneeds\.([\w-]+)\.outputs\.([\w-]+)")
"""A job's read of another job's output through the `needs` context.

Searched over a job's whole text and not one step's, for the reason
`shape` gives below: the read can sit in a step's `env:`, in a shell
`run:`, or in an `if:` at either level, and all carry the same
substring.
"""

REMOTE_CALL = re.compile(
    r"^(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)/\.github/workflows/"
    r"(?P<file>[\w.-]+\.ya?ml)@"
)
"""A `uses:` naming a reusable workflow of some repository, owner/repo open.

What `REUSABLE` narrows to this organization's own workflows at `@main`,
this reads for any owner, any repository and any ref: the callee a
`uses:` names can be anybody's, and resolving it against `trees` is what
decides whether it can be checked at all.
"""


def callee(
    value: str, repository: str, trees: dict[str, Path]
) -> tuple[str, Path] | None:
    """Resolve a job's `uses:` to its owner and the workflow file it calls.

    A `./`-path resolves inside the calling tree -- the one shape
    `actionlint` already types, and its owner is the calling repository
    itself. A remote call resolves through `trees`, which holds a
    checkout of every repository this suite fetched, so a caller in one
    tree and a callee declared in another are one lookup apart -- the
    half no single checkout can do, and the reason this cell lives in
    this repository (btclib-org/.github#1132). Either way the owner
    names the one checkout that holds the file, the same single-tree
    answer `lychee` in `links_test.py` resolves its own call to.

    :param value: the calling job's `uses:` value.
    :param repository: the calling tree's own name.
    :param trees: every checkout this suite holds, keyed by name.
    :returns: the callee's owner and path, or None where the call
        cannot be resolved to a file this suite holds -- outside the
        organization, naming a repository `trees` does not hold, or a
        file that tree does not carry.
    """
    if value.startswith(LOCAL):
        owner = repository
        target = trees[repository] / value[len(LOCAL) :]
    else:
        found = REMOTE_CALL.match(value)
        if found is None or found["owner"] != ORG or found["repo"] not in trees:
            return None
        owner = found["repo"]
        target = trees[owner] / ".github" / "workflows" / found["file"]
    return (owner, target) if target.is_file() else None


def declared_outputs(workflow: Path) -> set[str]:
    """Read the outputs a workflow declares under `workflow_call`.

    :param workflow: the file to read.
    :returns: the names it declares, empty where it declares none.
    """
    call = triggers(workflow).get("workflow_call")
    given = call.get("outputs") if isinstance(call, dict) else None
    return set(given) if isinstance(given, dict) else set()


def test_a_read_output_is_declared_by_its_callee(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """A `needs.<job>.outputs.<name>` read names something its callee declares.

    Undeclared, it is the empty string a green run cannot tell from a
    real one. Measured by dispatch rather than argued: a job reading
    `needs.changes.outputs.nosuch` from a callee declaring only `code`
    printed `undeclared: []` and the run's conclusion was `success`
    (btclib-org/.github#1132, run 35084268912). `actionlint` already
    refuses this for a `./`-path call, and a remote call is the shape
    `callee` resolves and no local checker does.

    Asked only where the named job calls a workflow -- `callee` answers
    nothing for a job that runs its own steps and maps their outputs by
    hand, which is a different mechanism and a different question.

    `callee` resolves each read to the one owner and file that declare
    it, the same pair `links_test.py`'s `lychee` resolves a call to
    before naming `call.owner` rather than `repository` in its own
    `by_hand` calls -- a `./`-call's owner is `repository` itself, a
    remote call's is whichever tree `trees` holds it in, and either way
    it is a single checkout, so the by-hand command below names it.
    Every `needs.<job>.outputs` read the organization writes today calls
    a remote workflow of `.github`, so `owner` above has so far always
    been `.github` and never `repository` itself -- no `./`-call in this
    tree has a job reading its outputs. The
    per-entry form is for the mechanism `callee` resolves, not for a
    two-owner case yet on the ground.

    Section 15 carries no line for this cell, decided rather than
    overlooked: the reads it resolves name a remote `uses:`, so such a
    read resolves through a second checkout and is not a question section 15's
    own opening reserves its commands for -- "the tree in front of you" --
    which is why `links_test.py`'s `lychee`, resolving a call the same
    way, carries none either.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    undeclared: set[str] = set()
    for workflow in gated(repository, trees):
        job_map = jobs(workflow)
        for job in job_map.values():
            for text in scalars(job):
                for job_id, name in NEEDS_OUTPUT.findall(text):
                    called = job_map.get(job_id)
                    if not isinstance(called, dict) or "uses" not in called:
                        continue
                    resolved = callee(called["uses"], repository, trees)
                    if resolved is None:
                        continue
                    owner, target = resolved
                    if name not in declared_outputs(target):
                        undeclared.add(
                            f"{workflow.name}: needs.{job_id}.outputs.{name}"
                            f" not declared by {target.name}; "
                            + by_hand(
                                owner,
                                "grep -n -A8 'outputs:' "
                                f".github/workflows/{target.name}",
                            )
                        )
    assert not undeclared, f"reads no callee declares: {sorted(undeclared)}"


def test_no_step_passes_frozen(repository: str, trees: dict[str, Path]) -> None:
    """Section 1: `--locked`, never `--frozen`; section 10 restates it.

    Read from each step's `run:` and not from the file, so a comment
    naming the flag to argue against it is not a finding.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    frozen = [
        f"{workflow.name}: {step.get('name') or step['run'].splitlines()[0]}"
        for workflow in gated(repository, trees)
        for step in steps(workflow)
        if "run" in step and "--frozen" in step["run"]
    ]
    assert not frozen, f"steps passing --frozen: {frozen}; " + by_hand(
        repository, "grep -rn -- '--frozen' .github/workflows/"
    )


def test_every_action_is_pinned_to_a_commit(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 10: every action is pinned to a commit SHA.

    A `uses:` naming a tag or a branch is a name its owner can move, in
    a job that can read the workflow token. A path into this tree is
    not one, for the reason `LOCAL` gives, and a call `REUSABLE` matches
    is section 10's exception.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    unpinned = [
        f"{workflow.name}: {value}"
        for workflow in gated(repository, trees)
        for value in uses(workflow)
        if not value.startswith(LOCAL)
        and not PINNED.search(value)
        and not REUSABLE.match(value)
    ]
    assert not unpinned, f"actions not pinned to a commit: {unpinned}; " + by_hand(
        repository,
        r"grep -hoE 'uses: [^ ]+' .github/workflows/*.yml | grep -v '@[0-9a-f]\{40\}'",
    )


TAG = re.compile(r"^[ \t]*#[ \t]*(\S+)[ \t]*$")
"""A comment that is one word, which is the shape a tag comment takes.

Section 10 asks a pin for the tag it sits at and for nothing else, so a
comment of several words is prose about the step rather than the tag.
One shape for both places the section allows: trailing the pin, or alone
on the line above it.
"""

PIN_LINE = re.compile(
    r"^[ \t]*(?:-[ \t]+)?uses:[ \t]*(?P<value>\S+@[0-9a-f]{40})(?P<rest>[ \t].*|)$"
)
"""Where a pin is written, anchored on the `uses:` key that opens it.

A commented-out `uses:` carries a `#` before that anchor and does not
match, which is the difference between reading a rule about text and
grepping for a substring. A `uses:` written inside a `run:` block scalar
is `pinned`'s to settle.
"""


class Pin(NamedTuple):
    """A pinned `uses:` as the file writes it, with the comments beside it.

    `trailing` and `above` are the tag each comment names, None where
    that comment is absent or is prose. `width` is what the line already
    takes, which is what decides whether the tag can trail.
    """

    value: str
    trailing: str | None
    above: str | None
    width: int
    where: str


def pinned(workflow: Path) -> list[Pin]:
    """Read every pin of a workflow off its text, with the comments beside it.

    Off the text and not off `document`: a tag comment is a YAML comment,
    and the parser has dropped it by the time it returns.

    What the text gives is counted against what the document uses, so a
    line this matches that the document does not use -- one written
    inside a `run:` block scalar, say -- is an error here rather than a
    finding against the tree, and a pattern that stops matching is an
    error too rather than a run that classifies nothing and passes.

    :param workflow: the file to read.
    :returns: the pins, in file order.
    :raises LookupError: where the text and the document disagree about
        what the file pins.
    """
    lines = workflow.read_text(encoding="utf-8").splitlines()
    found: list[Pin] = []
    for number, line in enumerate(lines, start=1):
        written = PIN_LINE.match(line)
        if written is None:
            continue
        trailing = TAG.match(written["rest"])
        above = TAG.match(lines[number - 2]) if number > 1 else None
        found.append(
            Pin(
                value=written["value"],
                trailing=trailing.group(1) if trailing else None,
                above=above.group(1) if above else None,
                width=len(line),
                where=f"{workflow.name}:{number}",
            )
        )
    read = Counter(pin.value for pin in found)
    used = Counter(value for value in uses(workflow) if PINNED.search(value))
    if read != used:
        msg = (
            f"{workflow.name}: {sorted((read - used).elements())} is pinned to"
            f" the text alone and {sorted((used - read).elements())} to the"
            " document alone"
        )
        raise LookupError(msg)
    return found


def budget(root: Path) -> int:
    """Read the columns a tree's yamllint allows a yaml line to take.

    Off that tree's own `.yamllint.yaml`, which section 14 owes every
    repository, rather than off a number written here: the width is what
    decides where a pin's tag comment sits, so both read it in one place.

    :param root: the root of the checkout.
    :returns: the columns a line may take.
    """
    configured = yaml.safe_load((root / ".yamllint.yaml").read_text(encoding="utf-8"))
    return int(configured["rules"]["line-length"]["max"])


def above_instead(pin: Pin, width: int) -> bool:
    """Say whether section 10 puts a pin's tag on the line above it.

    Where the pin plus the comment would take the line past the width,
    which is a property of the columns the pin spends and not of which
    action it names. That is what keeps this from excusing a pin whose
    tag was simply dropped: a pin with room for the comment is owed it
    wherever anything is written above.

    :param pin: the pin, as `pinned` read it.
    :param width: the columns the tree's yamllint allows a line.
    :returns: whether the comment above is where section 10 wants it.
    """
    return pin.above is not None and pin.width + len(f" # {pin.above}") > width


def pins(workflow: Path) -> list[tuple[str, str]]:
    """Read every action a workflow pins, against the commit it names.

    Keyed on the action's repository and not on the whole `uses:`: two
    paths into one repository -- `github/codeql-action/init` beside
    `.../analyze` -- name one repository at one commit, so a `uses:`
    into a subdirectory is the same pin as one into another.

    :param workflow: the file to read.
    :returns: each pinned `owner/name` with the commit, in file order,
        a `uses:` naming no commit left out.
    """
    return [
        ("/".join(value.split("@")[0].split("/")[:2]), value.rpartition("@")[2])
        for value in uses(workflow)
        if PINNED.search(value)
    ]


def tags(workflow: Path) -> dict[str, str]:
    """Read the tag comment written beside each pin of a workflow.

    For the failure message and nothing else: what a job runs is the
    commit, and the tag is how section 10 asks a reader to be able to
    name it. From either place that section allows the comment, so a pin
    at the width names its tag here as any other pin does.

    :param workflow: the file to read.
    :returns: each commit against the tag beside it, a pin with no tag
        comment left out.
    """
    beside = {
        pin.value.rpartition("@")[2]: pin.trailing or pin.above
        for pin in pinned(workflow)
    }
    return {commit: tag for commit, tag in beside.items() if tag is not None}


def test_every_pin_names_its_tag_in_a_comment(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 10: the tag beside every pin, trailing it or above it.

    A commit is what a job runs and is no version a reader can name, so
    a pin carrying neither comment leaves which release a job runs
    unreadable off the file. Which of the two places the comment takes
    is `above_instead`'s question, and turns on the width alone.

    What keeps this from passing over nothing is `pinned`, whose count
    against the parsed document a broken pattern does not survive, and
    the pins themselves: a tree with workflows and no pin in them is a
    tree this cannot ask, not one that keeps the rule.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    read = [pin for workflow in gated(repository, trees) for pin in pinned(workflow)]
    assert read, (
        f"{repository} has workflows and no pin in them, so this classified"
        " nothing and is asking the tree nothing"
    )
    width = budget(trees[repository])
    unnamed = [
        pin.where
        for pin in read
        if pin.trailing is None and not above_instead(pin, width)
    ]
    assert not unnamed, f"pins naming no tag: {unnamed}; " + by_hand(
        repository,
        "grep -nE -B1 'uses: [^ ]+@[0-9a-f]{40}[^#]*$' .github/workflows/*.yml",
    )


def test_a_tree_pins_an_action_at_one_commit(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 10: one commit per action across a tree's own workflows.

    A tree naming two commits of one action runs two versions of it at
    once, and neither file says so. What splits a tree is a pin written
    by hand, a new workflow taking the newest release while the tree
    around it sits on what section 11's grouped bump last landed.

    Asked within a tree and not across the organization, which is the
    other half of section 10's rule and the half no reading of one
    checkout decides: a caller runs the callee's pins, and the callee is
    another repository.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    named: dict[str, dict[str, str]] = {}
    for workflow in gated(repository, trees):
        beside = tags(workflow)
        for action, commit in pins(workflow):
            named.setdefault(action, {})[commit] = beside.get(commit, commit[:7])
    split = [
        f"{action} at {sorted(seen.values())}"
        for action, seen in sorted(named.items())
        if len(seen) > 1
    ]
    assert not split, f"actions this tree pins two ways: {split}; " + by_hand(
        repository,
        "grep -hoE 'uses: [^ ]+@[0-9a-f]{40}' .github/workflows/*.yml"
        " | sed -E 's|uses: ([^/]+/[^/@]+)[^@]*@|\\1 |'"
        " | sort -u | cut -d' ' -f1 | uniq -d",
    )


def test_every_workflow_declares_permissions(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 10: `permissions:` at the workflow level, in every workflow.

    A workflow without the block runs with whatever the repository's
    default grants, which is a setting rather than a line in the file.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    without = [
        workflow.name
        for workflow in gated(repository, trees)
        if "permissions" not in document(workflow)
    ]
    assert not without, f"workflows with no permissions block: {without}; " + by_hand(
        repository, "grep -L '^permissions:' .github/workflows/*.yml"
    )


def test_every_job_that_runs_steps_is_bounded(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 10: `timeout-minutes` on every job that runs steps.

    Asked of those jobs and of no others, which is the whole of the rule
    rather than an exemption written beside it: a job calling a reusable
    workflow may not carry the keyword, so the bound it would have set
    is the callee's own job's, and a cell asking every job alike would
    be asking for a file actionlint refuses.

    Nothing falls between the two and goes unasked. A job carrying both
    `steps` and `uses` is refused the same way, and one carrying neither
    is refused for a missing `runs-on`, so the two are a partition and
    not merely what the trees happen to hold today.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    unbounded = [
        f"{workflow.name}: {job}"
        for workflow in gated(repository, trees)
        for job, block in jobs(workflow).items()
        if "steps" in block and "timeout-minutes" not in block
    ]
    assert not unbounded, f"jobs that run steps unbounded: {unbounded}; " + by_hand(
        repository,
        "grep -n -e '^  [a-z].*:$' -e '^    steps:'"
        " -e '^    timeout-minutes:' .github/workflows/*.yml",
    )


def test_paths_ignore_is_only_on_push(repository: str, trees: dict[str, Path]) -> None:
    """Section 10: `paths-ignore` only on `push`.

    "On `pull_request` it would produce no run for a prose-only diff, and
    a required check that produces no run blocks the merge instead of
    passing it." Asked of every trigger but `push`,
    as the rule is written, rather than of `pull_request` alone: GitHub's
    workflow syntax gives the filter to `pull_request_target` as well,
    and a required check on that trigger is blocked the same way. A
    `paths` list is another question, the one section 10 asks of a
    calendar workflow's `pull_request`.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    ignoring = [
        f"{workflow.name}: {trigger}"
        for workflow in gated(repository, trees)
        for trigger, filters in triggers(workflow).items()
        if trigger != "push" and isinstance(filters, dict) and "paths-ignore" in filters
    ]
    assert not ignoring, f"paths-ignore off push: {ignoring}; " + by_hand(
        repository, "grep -n 'paths-ignore' .github/workflows/*.yml"
    )


CONDITIONAL = re.compile(r"^\s*`(\$\{\{ !\(.+\) \}\})`$", re.MULTILINE)
"""A line of the standard that is one negated expression and nothing else.

Section 10 writes the expression on a line of its own, the margin
leaving it nowhere else to go, so the pattern is anchored on the line
rather than searched for in the prose, and on the `!(` opening it: the
aggregate's condition, `GUARD`'s, stands on a line of its own too.
"""

COMMENTING = "claude-review.yml"
"""The workflow section 10 exempts, whose product is a comment.

Named as that section names it. What the exemption turns on is what a
run produces, which no reading of a workflow file answers, so the one
file the organization writes that way is the exemption's whole extent.
"""


def conditional(
    pattern: re.Pattern[str] = CONDITIONAL, standard: Path = ROOT / "README.md"
) -> str:
    """Read an expression section 10 writes on a line of its own.

    Off the standard rather than transcribed here: that file is what a
    port is made against, and a copy in this module is a second place
    for the expression to be edited in.

    :param pattern: the line's shape, by default the one given at
        `cancel-in-progress`.
    :param standard: the file to read, this tree's own `README.md`.
    :returns: the expression, spaced as the file writes it.
    :raises LookupError: where the file does not write it exactly once,
        which is a pattern that has stopped matching rather than a
        finding against any tree.
    """
    found: list[str] = pattern.findall(standard.read_text(encoding="utf-8"))
    if len(found) != 1:
        msg = f"{standard.name} writes {len(found)} lines of that shape"
        raise LookupError(msg)
    return found[0]


def closing(workflow: Path) -> bool:
    """Say whether a workflow takes the closing event of a pull request.

    :param workflow: the file to read.
    :returns: whether its `pull_request` types name `closed`.
    """
    trigger = triggers(workflow).get("pull_request")
    types = trigger.get("types") if isinstance(trigger, dict) else None
    return "closed" in types if isinstance(types, list) else False


def cancels(workflow: Path) -> str | bool | None:
    """Read what a workflow's concurrency group does with the run in flight.

    :param workflow: the file to read.
    :returns: the value at `cancel-in-progress`, None where the workflow
        declares no group or gives the group as a bare name.
    """
    group = document(workflow).get("concurrency")
    return group.get("cancel-in-progress") if isinstance(group, dict) else None


def test_a_workflow_taking_closed_without_push_writes_the_conditional(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 10's third shape at `cancel-in-progress`, asked per tree.

    Read as the section writes the rule, on the `push` trigger a file
    declares rather than on the commits a trigger reaches: a `push`
    narrowed by `paths` is a trigger the file declares, and asking which
    commits it runs on would make a port a judgement about path filters
    (btclib-org/.github#1238).

    The population is the workflows whose `pull_request` takes `closed`,
    that being the event the expression turns on: without the type the
    expression is true at everything such a workflow receives, and a
    group meaning false there is the bullet below section 10's, whose
    shape is `false` with `closed` omitted. Keying the exemption on the
    value found instead would excuse the value this asks for.

    A tree carrying no workflow of the shape is asked nothing here.
    Which sentinels it owes is section 10's record, and `grid_test.py`
    reads that against each tree.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    wanted = conditional()
    wrong: list[str] = []
    for workflow in gated(repository, trees):
        if workflow.name == COMMENTING or "push" in triggers(workflow):
            continue
        found = cancels(workflow)
        if closing(workflow) and found != wanted:
            wrong.append(f"{workflow.name}: {found!r}")
    assert not wrong, f"a merge cancels the run reading it: {wrong}; " + by_hand(
        repository, "grep -n -A2 '^concurrency:' .github/workflows/*.yml"
    )


AGGREGATE = re.compile(r": every job passed$")
"""How section 10 names an aggregate job, with its own workflow."""


def aggregates(workflow: Path) -> dict[str, dict[str, Any]]:
    """Every aggregate job of a workflow, by id.

    :param workflow: the file to read.
    :returns: each aggregate job's id against its own mapping.
    """
    jobs = document(workflow).get("jobs") or {}
    return {
        job_id: job
        for job_id, job in jobs.items()
        if isinstance(job, dict) and AGGREGATE.search(str(job.get("name", "")))
    }


def calls(root: Path, name: str) -> bool:
    """Say whether some workflow of this tree calls another, by file name.

    :param root: the root of the checkout.
    :param name: the called file's own name, `test.yml` and the like.
    :returns: whether a job of any workflow of the tree `uses:` it.
    """
    target = f"{LOCAL}.github/workflows/{name}"
    return any(
        job.get("uses") == target
        for workflow in workflows(root)
        for job in (document(workflow).get("jobs") or {}).values()
        if isinstance(job, dict)
    )


LISTING = "actions/runs"
"""What an aggregate reading the run's own job listing asks the API for."""

NEEDS = "needs.*.result"
"""What an aggregate reading `needs` decides over, in either shape."""

CHECK_SCRIPT = "check_run_jobs.py"
"""The script that reads the listing for an aggregate that calls it.

Such an aggregate has neither `LISTING` nor `NEEDS` in its own text, the
read and the decision being the script's, so `shape` names it by this.
"""


SHELL_OPERATORS = frozenset({";", "&&", "||", "|", "&"})
"""What ends one command of a `run:` block and starts the next."""

SCRIPT_OPTIONS = frozenset(
    {
        "--results-env",
        "--rows-env",
        "--row",
        "--prefix",
        "--timeout",
        "--interval",
        "--repository",
        "--run-id",
    }
)
"""The options `CHECK_SCRIPT` takes a value for, in the spaced form."""


def commands(run: str) -> list[list[str]]:
    """Split a `run:` block into the words of each command it runs.

    A comment is no command, and neither is what an `echo` prints: the
    words are the shell's own, so a pair quoted in either is not one the
    script was given.

    :param run: the step's `run:` text.
    :returns: one list of words per command, empty ones left out.
    :raises ValueError: where a line does not lex, an unclosed quote
        among them, which a string holding several lines is.
    """
    found: list[list[str]] = [[]]
    for line in re.sub(r"\\\n", " ", run).splitlines():
        lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
        for word in lexer:
            if word in SHELL_OPERATORS:
                found.append([])
            else:
                found[-1].append(word)
        found.append([])
    return [words for words in found if words]


def script_words(step: dict[str, Any]) -> list[str] | None:
    """Return the script's path and arguments where a step runs it.

    :param step: a step's own mapping.
    :returns: the words from the script's path on, or None where no
        command of the step is `CHECK_SCRIPT` itself or run by a python,
        or where the step does not lex, which `unparsed` says.
    """
    try:
        found = commands(str(step.get("run", "")))
    except ValueError:
        return None
    for words in found:
        if words[0].endswith(CHECK_SCRIPT):
            return words
        if (
            words[0].rpartition("/")[2].startswith("python")
            and len(words) > 1
            and words[1].endswith(CHECK_SCRIPT)
        ):
            return words[1:]
    return None


def unparsed(step: dict[str, Any]) -> bool:
    """Say whether a step names `CHECK_SCRIPT` and cannot be read as shell.

    A `run:` holding a string over several lines, an awk program say,
    does not lex a line at a time. Such a step is not taken for a step
    that never calls the script: it is one whose call cannot be read.

    :param step: a step's own mapping.
    :returns: whether the step names the script and `commands` refuses it.
    """
    run = str(step.get("run", ""))
    if CHECK_SCRIPT not in run:
        return False
    try:
        commands(run)
    except ValueError:
        return True
    return False


def scripted(job: dict[str, Any]) -> bool:
    """Say whether an aggregate hands the listing to `CHECK_SCRIPT`.

    :param job: the aggregate job's own mapping.
    :returns: whether some step runs the script as a command, or names it
        in a `run:` that cannot be read.
    """
    return any(
        isinstance(step, dict) and (script_words(step) is not None or unparsed(step))
        for step in job.get("steps") or []
    )


def shape(job: dict[str, Any]) -> str | None:
    """Read which of section 10's two shapes an aggregate decides with.

    Searched over the job's whole text rather than one step's `run:`,
    because the decision is written three ways across the organization
    -- a shell loop's `env:`, a shell loop inline, or a step's own
    boolean `if:` -- and all three carry the same substring wherever
    they read `needs` at all.

    :param job: the aggregate job's own mapping.
    :returns: "listing", "needs", or None where neither is found. An
        aggregate calling `CHECK_SCRIPT` reads the listing.
    :raises LookupError: where the job's text carries both, which a
        substring search cannot decide between.
    """
    if scripted(job):
        return "listing"
    blob = str(job)
    listing = LISTING in blob
    needs = NEEDS in blob
    if listing and needs:
        msg = f"an aggregate job's text carries both {LISTING!r} and {NEEDS!r}"
        raise LookupError(msg)
    if listing:
        return "listing"
    if needs:
        return "needs"
    return None


def test_a_called_aggregate_reads_needs_and_an_uncalled_one_the_listing(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 10's two shapes, asked of every aggregate of a tree.

    A workflow something in the tree calls has no job listing of its own
    run -- the caller's jobs and the called workflow's are one run -- so
    its aggregate reads `needs` instead, which stays scoped to the
    workflow that declares it either way; a workflow nothing calls reads
    the listing, which also catches a job `needs.*.result` misreports
    (btclib-org/btclib#1001).

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    wrong: list[str] = []
    for workflow in gated(repository, trees):
        wanted = "needs" if calls(root, workflow.name) else "listing"
        for job_id, job in aggregates(workflow).items():
            found = shape(job)
            if found is not None and found != wanted:
                wrong.append(f"{workflow.name}:{job_id} reads {found}, wants {wanted}")
    assert not wrong, f"{wrong}; " + by_hand(
        repository, "grep -n 'needs.\\*.result\\|actions/runs' .github/workflows/*.yml"
    )


ACCEPTED = ("success", "skipped")
"""The conclusions section 10 fixes a listing aggregate's allowlist to.

Both names whatever the workflow's own jobs can report today: what keeps
a `skipped` row out of such a listing is a condition the tree can lose,
and this constant is what the section says a check reads rather than
re-deriving each workflow's condition graph.
"""

COMMENT = re.compile(r"^[ \t]*#.*$", re.MULTILINE)
"""A whole-line shell comment, which a `run:` block scalar keeps.

A comment above a step belongs to the YAML and is gone by the time
`document` returns; one inside a block scalar is part of the string, and
that is where these workflows argue about the allowlist --
`btclib-benchmarks`' aggregate says in one that `skipped` is a
conclusion it accepts. Reading that would answer for the argument rather
than for the filter, which is this module's docstring on `--frozen` in
the shape a block scalar gives it.
"""


def scalars(node: object) -> list[str]:
    """List every string a job's mapping holds, at any depth.

    `str(job)`, which `shape` searches, renders a newline as two
    characters, so a pattern anchored on a line start matches nothing in
    it; the strings themselves keep their lines.

    :param node: a job's mapping, or anything nested inside one.
    :returns: the strings, in the order the document holds them.
    """
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        return [text for value in node.values() for text in scalars(value)]
    if isinstance(node, list):
        return [text for value in node for text in scalars(value)]
    return []


def allowlist(job: dict[str, Any]) -> str:
    r"""Read the text a job's allowlist is written in, its comments dropped.

    The job's whole text and not one step's `run:`, for the reason
    `shape` gives. What is searched in it is the two words rather than
    `"success"` with its quotes: `awk -F'\t' '$1 != "success"'` and
    `case ... success | skipped) ;;` are one filter spelled two ways,
    and both are section 10's.

    :param job: the aggregate job's own mapping.
    :returns: the job's strings joined, without their comment lines.
    """
    return COMMENT.sub("", "\n".join(scalars(job)))


def test_a_listing_aggregate_accepts_success_and_skipped(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 10's allowlist, asked of the aggregates that read a listing.

    `shape` is what selects them: the bullet fixing the allowlist is the
    one about an aggregate reading its own run's job listing, where an
    aggregate reading `needs` judges a join and is the bullet below it.
    An aggregate calling `CHECK_SCRIPT` is left to
    `tests/check_run_jobs_test.py`, which is where its allowlist is read.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    wrong: list[str] = []
    for workflow in gated(repository, trees):
        for job_id, job in aggregates(workflow).items():
            if shape(job) != "listing" or scripted(job):
                continue
            missing = [name for name in ACCEPTED if name not in allowlist(job)]
            if missing:
                wrong.append(f"{workflow.name}:{job_id} does not name {missing}")
    assert not wrong, f"{wrong}; " + by_hand(
        repository, "grep -n 'success' .github/workflows/*.yml"
    )


EXPRESSION = re.compile(r"\$\{\{([^}]*)\}\}")
"""The inside of a `${{ }}` expression, which is what GitHub evaluates.

A plain-text mention outside the delimiters -- a comment quoting the
reference for a reader, or the reference sitting unevaluated in prose --
is not a read of anything, so only what sits inside these is searched
for a `needs` id's own result.
"""

NEEDS_RESULT = re.compile(r"\bneeds\.([\w-]+)\.result\b")
"""A `needs` id's own `result`, read inside a `${{ }}` expression.

Section 10 names this reference and not `needs.*.result`: that one is an
unlabelled list of every result `needs:` carries, with no way to pair
one entry back to the job it answers for, so it cannot tell this
aggregate's own tolerated row from another job's failure. `[\\w-]` so a
hyphenated id, which a bare `\\w` would cut short, still matches whole.
"""


def excluding(job: dict[str, Any], *keys: str) -> list[str]:
    """List a job's scalars, with the mapping's own named keys left out.

    :param job: the aggregate job's own mapping.
    :param keys: the top-level keys to leave out.
    :returns: the strings `scalars` finds under everything else.
    """
    return scalars({key: value for key, value in job.items() if key not in keys})


def unread(job: dict[str, Any]) -> list[str]:
    """List a listing aggregate's own `needs` ids never read for their result.

    :param job: the aggregate job's own mapping.
    :returns: the `needs` ids with no `${{ }}` expression, outside the
        job's own `if:` and `needs:`, reading `needs.<id>.result`.
    """
    declared = job.get("needs") or []
    ids = [declared] if isinstance(declared, str) else declared
    read = {
        result
        for text in excluding(job, "if", "needs")
        for expression in EXPRESSION.findall(text)
        for result in NEEDS_RESULT.findall(expression)
    }
    return [job_id for job_id in ids if job_id not in read]


def test_a_listing_aggregate_that_tolerates_a_needs_row_reads_its_result(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 10's result requirement, asked of every listing aggregate.

    The tolerated row's own result has to come from `needs`, for every
    id the aggregate's own `needs:` names -- not only for one of them,
    and not through an output or any other reference that is not this
    one.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    wrong: list[str] = []
    for workflow in gated(repository, trees):
        for job_id, job in aggregates(workflow).items():
            if shape(job) != "listing" or scripted(job):
                continue
            ids = unread(job)
            if ids:
                wrong.append(f"{workflow.name}:{job_id} does not read {ids}")
    assert not wrong, f"{wrong}; " + by_hand(
        repository, "grep -n -A40 'every job passed' .github/workflows/*.yml"
    )


QUOTED = re.compile(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"")
"""A shell string in single or double quotes, which a keyword never is.

An awk program or an `echo` can hold `done` as a word, and quoted it is
text rather than the end of a loop.
"""

TOKEN = re.compile(r"\n|&&|\|\||[;&|(){}]|[^\s;&|(){}]+")
"""A shell token as far as `looped` needs one: an operator or a word.

The newline is a token of its own, being what ends a command where no
`;` does.
"""

COMMAND = frozenset({"\n", ";", "&&", "||", "|", "&", "(", "{", "do", "then", "else"})
"""What a word follows where it starts a command.

`do` and `done` are keywords only there, and `sleep` a command, so an
unquoted `echo done` does not close the loop it sits in and `echo sleep`
waits for nothing.
"""

LOOPED = "LISTING"
"""What `looped` puts in place of a quoted string holding `LISTING`'s path."""


def looped(script: str) -> bool:
    """Say whether a script reads the listing inside a loop that sleeps.

    The script's comment lines are dropped and its quoted strings
    blanked first, a string holding the listing's path standing in as
    one word. A loop is its `do` and its `done` where a command starts,
    whichever of `for`, `while` and `until` opened it, and a wait is
    `sleep` there too; a loop nested in another counts toward the outer
    one.

    :param script: one `run:` block's text.
    :returns: whether one loop's body holds both the listing's path and a
        `sleep`.
    """

    def blank(match: re.Match[str]) -> str:
        return f" {LOOPED} " if LISTING in match.group() else " '' "

    text = QUOTED.sub(blank, COMMENT.sub("", script))
    frames: list[set[str]] = []
    previous = "\n"
    for word in TOKEN.findall(text):
        start = previous in COMMAND
        if start and word == "do":
            frames.append(set())
        elif start and word == "done" and frames:
            body = frames.pop()
            if {LOOPED, "sleep"} <= body:
                return True
            if frames:
                frames[-1] |= body
        elif frames and (word == LOOPED or LISTING in word):
            frames[-1].add(LOOPED)
        elif frames and start and word == "sleep":
            frames[-1].add(word)
        previous = word
    return False


def rereads(job: dict[str, Any]) -> bool:
    """Say whether a listing aggregate reads the listing again after a wait.

    Asked of each of the job's strings rather than of their join, a loop
    being one script's.

    :param job: the aggregate job's own mapping.
    :returns: whether some script of the job has the shape `looped` reads.
    """
    return any(looped(text) for text in scalars(job))


def test_a_listing_aggregate_that_tolerates_a_needs_row_rereads_it(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 10's re-read, asked of every listing aggregate with `needs:`.

    Recognised by its shape, a loop whose body both asks for the listing
    and sleeps, rather than by the count or the interval it waits: those
    are section 10's numbers, and a reader copying them would be a second
    place to change them.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    wrong: list[str] = []
    for workflow in gated(repository, trees):
        for job_id, job in aggregates(workflow).items():
            if shape(job) != "listing" or scripted(job) or not job.get("needs"):
                continue
            if not rereads(job):
                wrong.append(f"{workflow.name}:{job_id}")
    assert not wrong, f"read once, not again after a wait: {wrong}; " + by_hand(
        repository, "grep -n -B2 -A4 'actions/runs/' .github/workflows/*.yml"
    )


STUB_GH = """#!/bin/sh
while [ "$#" -gt 0 ]; do
  if [ "$1" = --jq ]; then exec jq -r "$2" "$LISTING"; fi
  shift
done
echo "the stub answers only a call carrying --jq" >&2
: > "$REFUSED"
exit 2
"""
"""A `gh` answering `gh api ... --jq <filter>` with the filter over `LISTING`.

`jq -r` because `--jq` prints a string raw, as the step's rows are. A
call it cannot answer leaves `REFUSED` behind, so that its exit status,
which a step may read as anything, is not taken for the step's verdict.
"""

STUB_SLEEP = "#!/bin/sh\nexit 0\n"
"""A `sleep` that returns at once, the listing having no row to wait for."""

PROBES = ("failure", "cancelled")
"""The results each `needs` job is set to in turn, for its step to refuse.

Two, a step refusing `failure` alone being one that passes `cancelled`
(btclib-org/.github#1424).
"""


class Ran(NamedTuple):
    """What running an aggregate's listing step against the stubs gave."""

    status: int
    """The step's exit status."""

    stubbed: bool
    """Whether the step made a call the stub could not answer."""

    output: str
    """The step's output and its errors, in that order."""


def listing_step(job: dict[str, Any]) -> dict[str, Any]:
    """Return the one step of an aggregate that asks for the listing.

    :param job: the aggregate job's own mapping.
    :returns: the step's mapping.
    :raises LookupError: where no step, or more than one, names it.
    """
    found = [
        step
        for step in job.get("steps") or []
        if isinstance(step, dict) and LISTING in str(step.get("run", ""))
    ]
    if len(found) != 1:
        msg = f"{len(found)} steps of the aggregate ask for {LISTING!r}"
        raise LookupError(msg)
    return found[0]


def needed(job: dict[str, Any]) -> list[str]:
    """List the ids an aggregate's own `needs:` names.

    :param job: the aggregate job's own mapping.
    :returns: the ids, one where `needs:` is a bare string.
    """
    declared = job.get("needs") or []
    return [declared] if isinstance(declared, str) else list(declared)


def verdict(
    workflow: Path,
    job: dict[str, Any],
    results: dict[str, str],
    scratch: Path,
) -> Ran:
    """Run an aggregate's listing step against a run where every row passed.

    The step's `env:` is what it runs with, each `needs.<id>.result` in
    it reading that id's entry in `results` and any other expression
    reading empty; nothing of this process's own environment reaches it
    but `PATH`, behind the stubs. It runs in a directory of its own under
    `scratch`, so a relative path it writes lands there. The listing
    holds one finished `success` row per `needs` id, named as that job
    declares itself, and the aggregate's own row unfinished: every row
    passes, so what is left to fail the step is the results alone.

    :param workflow: the file the job is read from.
    :param job: the aggregate job's own mapping.
    :param results: what each `needs.<id>.result` reads, by id.
    :param scratch: an empty directory for the stubs and the listing.
    :returns: the step's exit status, whether the stub refused a call,
        and what the step printed.
    """
    declared = jobs(workflow)
    rows: list[dict[str, str | None]] = [
        {
            "name": str(declared.get(i, {}).get("name", i)),
            "status": "completed",
            "conclusion": "success",
        }
        for i in needed(job)
    ]
    rows.append(
        {"name": str(job.get("name")), "status": "in_progress", "conclusion": None}
    )
    listing = scratch / "listing.json"
    listing.write_text(json.dumps({"jobs": rows}), encoding="utf-8")
    stubs = scratch / "bin"
    stubs.mkdir()
    for name, body in (("gh", STUB_GH), ("sleep", STUB_SLEEP)):
        (stubs / name).write_text(body, encoding="utf-8")
        (stubs / name).chmod(0o755)
    refused = scratch / "refused"
    here = scratch / "cwd"
    here.mkdir()

    def evaluate(match: re.Match[str]) -> str:
        read = NEEDS_RESULT.fullmatch(match.group(1).strip())
        return results.get(read.group(1), "") if read else ""

    step = listing_step(job)
    env = {
        str(key): EXPRESSION.sub(evaluate, str(value))
        for key, value in (step.get("env") or {}).items()
    }
    env |= {
        "PATH": f"{stubs}{os.pathsep}{os.environ.get('PATH', '')}",
        "LISTING": str(listing),
        "REFUSED": str(refused),
        "GITHUB_REPOSITORY": f"{ORG}/stub",
        "GITHUB_RUN_ID": "1",
    }
    script = scratch / "step.sh"
    script.write_text(str(step["run"]), encoding="utf-8")
    done = subprocess.run(
        ["bash", "--noprofile", "--norc", "-eo", "pipefail", str(script)],
        cwd=here,
        env=env,
        capture_output=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    return Ran(done.returncode, refused.exists(), done.stdout + done.stderr)


def probes(job: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Name each run the result rule asks for, against its results by id.

    :param job: the aggregate job's own mapping.
    :returns: every id `success` first, the control; then, per id and per
        result in `PROBES`, that id at that result and every other at
        `success`.
    """
    ids = needed(job)
    runs = {"control": dict.fromkeys(ids, "success")}
    for job_id in ids:
        for result in PROBES:
            runs[f"{job_id}={result}"] = dict.fromkeys(ids, "success") | {
                job_id: result
            }
    return runs


def refusals(workflow: Path, job: dict[str, Any], scratch: Path) -> list[str]:
    """Run every probe of an aggregate and say what the step got wrong.

    :param workflow: the file the job is read from.
    :param job: the aggregate job's own mapping.
    :param scratch: an empty directory, one subdirectory per run.
    :returns: one line per run that went wrong, empty where none did.
    """
    wrong: list[str] = []
    for name, results in probes(job).items():
        (scratch / name).mkdir()
        ran = verdict(workflow, job, results, scratch / name)
        if ran.stubbed:
            wrong.append(f"{name}: called gh without --jq, which the stub refuses")
        elif name == "control" and ran.status:
            wrong.append(f"{name}: fails a passing run: {ran.output[-300:]}")
        elif name != "control" and not ran.status:
            wrong.append(f"{name}: passes")
    return wrong


def test_a_listing_aggregate_fails_on_a_failed_needs_result(
    repository: str,
    trees: dict[str, Path],
    tmp_path: Path,
) -> None:
    """Section 10's result rule, asked by running each listing aggregate.

    Run rather than read, the aggregates matching their own rows in
    shapes no one pattern covers. Every row passes, and each `needs` job
    in turn reads every result in `PROBES` with the others at `success`,
    which the step has to refuse; the run with every result `success` has
    to pass, or the stub is not a run the step can judge and the refusals
    would say nothing.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param tmp_path: where each run's stubs are written.
    """
    wrong: list[str] = []
    for workflow in gated(repository, trees):
        for job_id, job in aggregates(workflow).items():
            if shape(job) != "listing" or scripted(job) or not needed(job):
                continue
            where = tmp_path / workflow.stem / job_id
            where.mkdir(parents=True)
            wrong += [
                f"{workflow.name}:{job_id} {line}"
                for line in refusals(workflow, job, where)
            ]
    assert not wrong, f"{wrong}; " + by_hand(
        repository, "grep -n -A12 'every job passed' .github/workflows/*.yml"
    )


def script_call(job: dict[str, Any]) -> tuple[int, list[dict[str, Any]]]:
    """Find the step of an aggregate that runs `CHECK_SCRIPT`.

    :param job: the aggregate job's own mapping.
    :returns: the step's index among the job's steps, and the steps.
    """
    steps = [step for step in job["steps"] if isinstance(step, dict)]
    call = next(
        i
        for i, step in enumerate(steps)
        if script_words(step) is not None or unparsed(step)
    )
    return call, steps


def script_arguments(words: list[str]) -> tuple[list[str], dict[str, str], list[str]]:
    """Split the script's own arguments into positionals and options.

    :param words: the words from the script's path on.
    :returns: the positional arguments, the options with their values,
        and every word starting `--` that is not a spaced option, which
        includes `--option=value`.
    """
    positional: list[str] = []
    options: dict[str, str] = {}
    unread: list[str] = []
    rest = iter(words[1:])
    for word in rest:
        if word in SCRIPT_OPTIONS:
            options[word] = next(rest, "")
        elif word.startswith("--"):
            unread.append(word)
        else:
            positional.append(word)
    return positional, options, unread


def result_lines(step: dict[str, Any], variable: str | None) -> set[str]:
    """List the ids whose result the `--results-env` variable holds a line for.

    :param step: the step running `CHECK_SCRIPT`.
    :param variable: the variable the call names, or None.
    :returns: the ids, each with a line `<id> ${{ needs.<id>.result }}`.
    """
    if variable is None:
        return set()
    value = str((step.get("env") or {}).get(variable, ""))
    return {
        job
        for line in value.splitlines()
        for job, _, rest in [line.strip().partition(" ")]
        if EXPRESSION.fullmatch(rest.strip()) and NEEDS_RESULT.findall(rest) == [job]
    }


def command_faults(job: dict[str, Any]) -> list[str]:
    """Say what is wrong with the arguments, the environment and the grant.

    Each `needs` id has its result read either from an environment
    variable holding that one expression and given beside the id, or from
    a line of the variable `--results-env` names. Both are looked for in
    the script's own arguments and nowhere else in the step: a comment
    or an `echo` holding the pair is not a call that passes it
    (btclib-org/.github#1424's shape). The options are read in the spaced
    form, so `--results-env=NR` is refused; that fails closed.

    :param job: the aggregate job's own mapping.
    :returns: one line per fault, empty where the call is as it should be.
    """
    call, steps = script_call(job)
    step = steps[call]
    if unparsed(step):
        return [f"names {CHECK_SCRIPT} in a run: block that does not lex as shell"]
    words = script_words(step) or []
    positional, options, unread = script_arguments(words)
    given = dict(zip(positional[::2], positional[1::2], strict=False))
    env = step.get("env") or {}
    ids = needed(job)
    faults: list[str] = [f"gives {word}, which is not read" for word in unread]
    if not ids:
        faults.append("needs nothing, and the script takes a job")
    held = result_lines(step, options.get("--results-env"))
    for needs in ids:
        holders = [
            key
            for key, value in env.items()
            if EXPRESSION.fullmatch(str(value).strip())
            and [needs] == NEEDS_RESULT.findall(str(value))
        ]
        if needs in held:
            continue
        if len(holders) != 1:
            faults.append(f"has {holders} holding needs.{needs}.result")
        elif given.get(needs) != f"${{{holders[0]}}}":
            faults.append(
                f'does not pass {needs} "${{{holders[0]}}}" to {CHECK_SCRIPT}'
            )
    if env.get("GH_TOKEN") != "${{ github.token }}":
        faults.append("does not pass GH_TOKEN")
    if (job.get("permissions") or {}).get("actions") != "read":
        faults.append("does not declare actions: read")
    return faults


def checkout_faults(job: dict[str, Any]) -> list[str]:
    """Say what is wrong with the checkout the script is served from.

    :param job: the aggregate job's own mapping.
    :returns: one line per fault, empty where the checkout is as it should be.
    """
    call, steps = script_call(job)
    checkouts = [
        step["with"]
        for step in steps[:call]
        if str(step.get("uses", "")).startswith("actions/checkout@")
        and (step.get("with") or {}).get("repository") == f"{ORG}/.github"
    ]
    if len(checkouts) != 1:
        return [f"has {len(checkouts)} checkouts of {ORG}/.github before the script"]
    given = checkouts[0]
    faults: list[str] = []
    if given.get("ref") != "main" or given.get("sparse-checkout") != ".github/scripts":
        faults.append("does not check out .github/scripts at main")
    if given.get("persist-credentials") is not False:
        faults.append("persists the checkout's credentials")
    words = script_words(steps[call]) or [""]
    if words[0] != f"{given.get('path')}/.github/scripts/{CHECK_SCRIPT}":
        faults.append("runs the script from somewhere its checkout's path is not")
    return faults


def test_a_scripted_aggregate_names_the_checkout_the_arguments_and_the_result(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """What only a tree can answer of an aggregate calling `CHECK_SCRIPT`.

    The allowlist, the re-read and the refusal of a failed result are the
    script's, and `tests/check_run_jobs_test.py` asks them. What is left
    to the tree is what the script cannot see of its caller: that the
    script is checked out of `btclib-org/.github` at `main`, sparse, under
    the `path:` the command names; that the command names each `needs`
    job's id and an environment variable holding that job's own result;
    and that the token and the `actions: read` the read takes are there.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    wrong = [
        f"{workflow.name}:{job_id} {fault}"
        for workflow in gated(repository, trees)
        for job_id, job in aggregates(workflow).items()
        if scripted(job)
        for fault in command_faults(job) + checkout_faults(job)
    ]
    assert not wrong, f"{wrong}; " + by_hand(
        repository, "grep -n -B12 -A6 'check_run_jobs' .github/workflows/*.yml"
    )


GUARD = re.compile(r"^\s*`(\$\{\{ !cancelled\(\) && .+ \}\})`$", re.MULTILINE)
"""The line of the standard giving an aggregate job's own `if:`.

Anchored on `!cancelled()` opening it, which `CONDITIONAL`'s line does
not.
"""


def test_an_aggregate_carries_the_condition_section_10_gives(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 10's `if:` on the aggregate job, asked of every aggregate.

    Compared as a string, spacing included, the way the conditional at
    `cancel-in-progress` is: a port copies the line, and an expression
    that means the same but reads differently is one this cannot tell
    from a stale one. The draft flag the job's own step reads is not
    asked here, having no one line to compare against.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    wanted = conditional(GUARD)
    wrong = [
        f"{workflow.name}:{job_id}: {job.get('if')!r}"
        for workflow in gated(repository, trees)
        for job_id, job in aggregates(workflow).items()
        if job.get("if") != wanted
    ]
    assert not wrong, f"an aggregate's if: is not section 10's: {wrong}; " + by_hand(
        repository, "grep -n -B1 -A1 'every job passed' .github/workflows/*.yml"
    )
