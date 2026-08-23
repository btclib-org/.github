# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 7's public surface, asked of the packages that publish.

A repository needs the convention tests its own prose states, and
section 7 takes the public surface out of that clause where the package
is published: `py.typed` promises the types are supported, and which
names are public is the other half of that promise. What is asked here
is the standard's side of it -- that the modules declare `__all__` at
all. The census section 7 asks for beside it walks an installed package
and belongs to the suite of the tree that ships it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from . import Tier, by_hand, tracked

pytestmark = pytest.mark.integration

MARKER = "*py.typed"
"""The pathspec that finds the package directory, as section 2 names it."""

DECLARED = re.compile(r"^__all__\s*(?::[^=]+)?=", re.MULTILINE)
"""A module-level `__all__`, read rather than imported.

Nothing installs the trees this suite clones, so a module importing a
compiled extension could not be imported to be asked for the attribute.
An assignment at the left margin is what the declaration looks like,
its annotated form included.
"""


def is_public(path: str) -> bool:
    """Say whether a module's dotted name is public at every part.

    `__init__` names the package rather than a module of its own, so
    the directory holding it is what decides that part.

    :param path: the module's path, relative to the checkout.
    :returns: whether no part of the dotted name is private.
    """
    parts = (*Path(path).parts[:-1], Path(path).stem)
    return not any(part.startswith("_") for part in parts if part != "__init__")


def package(repository: str, trees: dict[str, Path]) -> Path:
    """Return the package directory of a repository that publishes.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the directory, relative to the checkout.
    :raises FileNotFoundError: where no one directory holds `py.typed`,
        section 2 giving the package directory that file.
    """
    markers = tracked(trees[repository], MARKER)
    if len(markers) != 1:
        msg = f"{repository} has {markers} and section 2 asks for one; " + by_hand(
            repository, f"git ls-files '{MARKER}'"
        )
        raise FileNotFoundError(msg)
    return Path(markers[0]).parent


@pytest.mark.tier(Tier.PUBLISHER)
def test_every_published_module_declares_its_public_surface(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 7: `__all__` in every public module of a published package.

    A module under a private name is no part of the surface and is not
    asked, which is the exception the bullet states and the one
    `btclib`'s own census keeps.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    directory = package(repository, trees)
    silent = sorted(
        path
        for path in tracked(root, f"{directory}/*.py")
        if is_public(path)
        and not DECLARED.search((root / path).read_text(encoding="utf-8"))
    )
    assert not silent, (
        f"public modules of a published package declaring no __all__: {silent}; "
        + by_hand(
            repository,
            f"git ls-files '{directory}/*.py'"
            r" | grep -vE '/_[^_]' | xargs grep -L '^__all__'",
        )
    )
