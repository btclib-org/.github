# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 2's `ISSUE_TEMPLATE/`, asked of every repository.

The section's directories bullet names it among what `.github/` holds
and the sentence under that bullet gives `.github/` to every tier;
section 16's checklist gives the directory to a repository being set up.
So it is owed whatever a tree is written in, which is why the question
here carries no `tier` marker.

What is owed is the directory. Nothing in the standard names a form
under it, so a test asking for `bug_report.yml` or any other file by
name would be where a convention this standard does not carry got
written down.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import by_hand, tracked

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

DIRECTORY = ".github/ISSUE_TEMPLATE"

FORMS = f"git ls-files -- {DIRECTORY}"
"""How a reader asks a checkout what the directory holds."""


def test_a_repository_carries_an_issue_template_directory(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """The directory is in the tree, with a form in it.

    One question rather than two: git tracks no empty directory, so a
    tree that answers with a path has both, and a tree that answers with
    nothing is short of the directory or of everything under it.

    A default rendered from another repository is not a directory this
    one has, so what a reader is shown does not answer it.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    forms = tracked(trees[repository], DIRECTORY)
    assert forms, (
        f"section 2 gives every tree {DIRECTORY}/ and this one tracks nothing"
        " under it; " + by_hand(repository, FORMS)
    )
