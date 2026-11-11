# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 12's rehearsal left waiting, read off each publisher's group.

The bullet says a rehearsal not to be approved is closed by rejecting
its `testpypi` deployment, and that is a person's act, which no test
reads. Its reason is the tree's half: `release.yml` keeps one
concurrency group per ref and does not cancel the run in flight, so a
run waiting at the approval holds the group. That half is configuration,
and this reads it. The tests below the first run offline and hold the
reader to the blocks it has to refuse.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import Tier, by_hand
from .release_test import released
from .workflows_test import cancels, document

if TYPE_CHECKING:
    from pathlib import Path

GROUP = "release-${{ github.ref }}"
"""The group a publisher's `release.yml` names: one per ref."""


def refusals(workflow: Path) -> list[str]:
    """Say how a release workflow's concurrency group differs from section 12's.

    :param workflow: the `release.yml` to read.
    :returns: one line per difference, empty where there is none.
    """
    group = document(workflow).get("concurrency")
    name = group.get("group") if isinstance(group, dict) else group
    found: list[str] = []
    if name != GROUP:
        found.append(f"the group is {name!r}, not {GROUP!r}")
    if cancels(workflow) is not False:
        found.append(f"cancel-in-progress is {cancels(workflow)!r}, not False")
    return found


@pytest.mark.integration
@pytest.mark.tier(Tier.PUBLISHER)
def test_a_waiting_rehearsal_holds_its_refs_group(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 12: one group per ref, and the run in flight is kept.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    found = refusals(released(trees[repository]))
    assert not found, f"{'; '.join(found)}; " + by_hand(
        repository, "grep -n -A2 '^concurrency:' .github/workflows/release.yml"
    )


KEPT = f"concurrency:\n  group: {GROUP}\n  cancel-in-progress: false\n"
"""The block every publisher writes, which the reader passes."""


@pytest.mark.parametrize(
    "block",
    [
        "",
        "concurrency: release\n",
        KEPT.replace("github.ref", "github.sha"),
        KEPT.replace("false", "true"),
        KEPT.replace("  cancel-in-progress: false\n", ""),
    ],
    ids=["no group", "a bare name", "per commit", "cancelling", "no cancel key"],
)
def test_a_group_that_lets_a_waiting_run_go_is_refused(
    tmp_path: Path, block: str
) -> None:
    """Each block that would not hold the group per ref is refused.

    :param tmp_path: where the workflow is written.
    :param block: what the workflow declares above its jobs.
    """
    workflow = tmp_path / "release.yml"
    workflow.write_text(f"{block}jobs: {{}}\n", encoding="utf-8")
    assert refusals(workflow)


def test_the_block_every_publisher_writes_passes(tmp_path: Path) -> None:
    """The control: the reader passes the block it is asked to keep.

    :param tmp_path: where the workflow is written.
    """
    workflow = tmp_path / "release.yml"
    workflow.write_text(f"{KEPT}\njobs: {{}}\n", encoding="utf-8")
    assert refusals(workflow) == []
