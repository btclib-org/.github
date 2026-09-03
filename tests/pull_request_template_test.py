# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 2's `PULL_REQUEST_TEMPLATE.md`, asked of every repository.

The section's directories bullet names it among what `.github/` holds
and the sentence under that bullet gives `.github/` to every tier;
section 16's checklist gives the file to a repository being set up. So
it is owed whatever a tree is written in, which is why the question here
carries no `tier` marker.

The path is the assertion and not only the file. GitHub reads a template
from more than one place in a tree, and the same section fixes `.github/`
with the alternative beside it, so a copy kept elsewhere is served to a
reader and is still a tree of a shape that section decides against.

What the file says is not asked. The copy this repository carries names
the commands of a tree whose gates are its own, and says in itself that
a repository whose commands differ writes its own, so comparing the text
across the trees would be a verbatim rule section 14 does not state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import by_hand, tracked

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

TEMPLATE = ".github/PULL_REQUEST_TEMPLATE.md"

LISTING = f"git ls-files -- {TEMPLATE}"
"""How a reader asks a checkout whether the file is there."""


def test_a_repository_carries_a_pull_request_template(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """The file is tracked, at the path and under the name section 2 gives.

    `git ls-files` rather than the filesystem, so a copy left untracked
    in a checkout is not read as the repository's, and the pathspec is
    the whole path in the section's own spelling.

    What GitHub shows a reader does not answer it: a tree with no
    template of its own is shown this repository's, which is in no tree
    of the repository being asked about.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    assert tracked(trees[repository], TEMPLATE), (
        f"section 2 gives every tree {TEMPLATE} and this one does not track"
        " it; " + by_hand(repository, LISTING)
    )
