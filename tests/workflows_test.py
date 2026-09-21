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

import re
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
rather than searched for in the prose: every other `${{ ... }}` that
file shows sits inside a sentence.
"""

COMMENTING = "claude-review.yml"
"""The workflow section 10 exempts, whose product is a comment.

Named as that section names it. What the exemption turns on is what a
run produces, which no reading of a workflow file answers, so the one
file the organization writes that way is the exemption's whole extent.
"""


def conditional(standard: Path = ROOT / "README.md") -> str:
    """Read the expression section 10 gives at `cancel-in-progress`.

    Off the standard rather than transcribed here: that file is what a
    port is made against, and a copy in this module is a second place
    for the expression to be edited in.

    :param standard: the file to read, this tree's own `README.md`.
    :returns: the expression, spaced as the file writes it.
    :raises LookupError: where the file does not write it exactly once,
        which is a pattern that has stopped matching rather than a
        finding against any tree.
    """
    found: list[str] = CONDITIONAL.findall(standard.read_text(encoding="utf-8"))
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


def shape(job: dict[str, Any]) -> str | None:
    """Read which of section 10's two shapes an aggregate decides with.

    Searched over the job's whole text rather than one step's `run:`,
    because the decision is written three ways across the organization
    -- a shell loop's `env:`, a shell loop inline, or a step's own
    boolean `if:` -- and all three carry the same substring wherever
    they read `needs` at all.

    :param job: the aggregate job's own mapping.
    :returns: "listing", "needs", or None where neither is found.
    :raises LookupError: where the job's text carries both, which a
        substring search cannot decide between.
    """
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

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    wrong: list[str] = []
    for workflow in gated(repository, trees):
        for job_id, job in aggregates(workflow).items():
            if shape(job) != "listing":
                continue
            missing = [name for name in ACCEPTED if name not in allowlist(job)]
            if missing:
                wrong.append(f"{workflow.name}:{job_id} does not name {missing}")
    assert not wrong, f"{wrong}; " + by_hand(
        repository, "grep -n 'success' .github/workflows/*.yml"
    )
