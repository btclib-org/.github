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
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import by_hand

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


def steps(workflow: Path) -> list[dict[str, Any]]:
    """List every step of every job of a workflow, in file order.

    :param workflow: the file to read.
    :returns: the step mappings, empty for a workflow of calls alone.
    """
    jobs = document(workflow).get("jobs") or {}
    return [step for job in jobs.values() for step in (job.get("steps") or [])]


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
    not one, for the reason `LOCAL` gives.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    unpinned = [
        f"{workflow.name}: {uses}"
        for workflow in gated(repository, trees)
        for uses in [
            *(step["uses"] for step in steps(workflow) if "uses" in step),
            *(
                job["uses"]
                for job in (document(workflow).get("jobs") or {}).values()
                if "uses" in job
            ),
        ]
        if not uses.startswith(LOCAL) and not PINNED.search(uses)
    ]
    assert not unpinned, f"actions not pinned to a commit: {unpinned}; " + by_hand(
        repository,
        r"grep -hoE 'uses: [^ ]+' .github/workflows/*.yml | grep -v '@[0-9a-f]\{40\}'",
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


def test_paths_ignore_is_only_on_push(repository: str, trees: dict[str, Path]) -> None:
    """Section 10: `paths-ignore` only on `push`.

    "The same list on `pull_request` would produce no run at all for a
    prose-only diff, and a required check that produces no run blocks
    the merge instead of passing it." Asked of every trigger but `push`,
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
