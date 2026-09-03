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

LISTING = f"git ls-files -- {DIRECTORY}"
"""How a reader asks a checkout what the directory holds."""


def test_a_repository_carries_an_issue_template_directory(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """The directory is tracked.

    git tracks no empty directory, so listing what is under the
    directory is how a checkout is asked whether the directory is there
    at all, and a tree answering with nothing has none.

    A default rendered from another repository is not a directory this
    one has, so what a reader is shown does not answer it.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    paths = tracked(trees[repository], DIRECTORY)
    assert paths, (
        f"section 2 gives every tree {DIRECTORY}/ and this one tracks nothing"
        " under it; " + by_hand(repository, LISTING)
    )
