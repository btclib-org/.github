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


def document(workflow: Path) -> dict[str, Any]:
    """Parse a workflow file.

    :param workflow: the file to read.
    :returns: the document, empty where the file parses to nothing.
    """
    parsed = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    return parsed if isinstance(parsed, dict) else {}


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
    asked about, and btclib-org/.github#107 is where whether it owes one
    is being decided; skipped with the reason so the cell says so.

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
