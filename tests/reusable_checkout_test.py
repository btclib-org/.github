# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 10: a reusable workflow serves its scripts at its own commit.

A job of a reusable workflow checks out the caller's tree by default, so
a step that serves a script of this repository names `repository:` and
`ref:`. `job.workflow_sha` is the commit of the workflow file that runs,
which is the commit a tree's pin names; `main` is whatever has landed
since, and `github.workflow_sha` is the caller's commit
(btclib-org/.github#1871 has the measurement).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import ORG, ROOT, SELF
from .workflows_test import steps

if TYPE_CHECKING:
    from pathlib import Path

# the files a tree's call into this repository runs
REUSABLE = sorted((ROOT / ".github" / "workflows").glob("reusable-*.yml"))

# the ref of a checkout of this repository, as section 10 gives it
COMMIT = "${{ job.workflow_sha }}"


def served(workflow: Path) -> list[dict[str, str]]:
    """List the `with:` of each step checking out this repository.

    :param workflow: the file to read.
    :returns: the mappings, in file order.
    """
    return [
        step["with"]
        for step in steps(workflow)
        if str(step.get("uses", "")).startswith("actions/checkout@")
        and (step.get("with") or {}).get("repository") == f"{ORG}/{SELF}"
    ]


def test_the_reader_sees_a_checkout_that_names_main(tmp_path: Path) -> None:
    """A stand-in with `ref: main` is a checkout `served` reports.

    :param tmp_path: where the stand-in is written.
    """
    stand_in = tmp_path / "reusable-stand-in.yml"
    stand_in.write_text(
        "on: workflow_call\n"
        "jobs:\n"
        "  job:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: actions/checkout@" + "0" * 40 + "\n"
        "        with:\n"
        f"          repository: {ORG}/{SELF}\n"
        "          ref: main\n",
        encoding="utf-8",
    )
    assert served(stand_in) == [{"repository": f"{ORG}/{SELF}", "ref": "main"}]


def test_every_checkout_of_this_repository_reads_the_workflows_own_commit() -> None:
    """No `reusable-*.yml` serves a script at a ref other than `COMMIT`."""
    found = {path.name: served(path) for path in REUSABLE}
    assert any(found.values()), "no checkout of this repository was found"
    wrong = [
        f"{name}: ref {given.get('ref')!r}"
        for name, checkouts in found.items()
        for given in checkouts
        if given.get("ref") != COMMIT
    ]
    assert not wrong, f"checkouts not at {COMMIT}: {wrong}"
