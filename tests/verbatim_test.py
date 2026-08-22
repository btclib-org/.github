"""The files section 14 calls verbatim are byte-identical.

The list is prose with a reason under each entry, which is what a person
reading it needs; the subject of each bullet is a path, which is what
this needs. Nothing else in the organization compares those copies, and
the failure they hide is silent by construction: a hook config that
drifts still lints, it just stops asking the same question everywhere.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from .organization import ROOT
from .tables import subjects

pytestmark = pytest.mark.integration


def verbatim() -> list[str]:
    """Read the whole-file half of section 14.

    :returns: the paths, relative to a repository root.
    """
    return subjects(
        ROOT / "README.md",
        "**The same file in every repository**",
        "**Verbatim in part**",
    )


def test_section_14_names_files(trees: dict[str, Path]) -> None:
    """A path in the list that no repository carries is a stale entry.

    :param trees: the checkouts.
    """
    unknown = [
        path
        for path in verbatim()
        if not any((root / path).is_file() for root in trees.values())
    ]
    assert not unknown, f"section 14 names paths no repository has: {unknown}"


def test_every_copy_of_a_verbatim_file_is_the_same_copy(
    trees: dict[str, Path],
) -> None:
    """Where two repositories carry one of these files, it is one file.

    A repository that carries none of a given file is not a finding:
    section 14 is about what the copies agree on, and which repositories
    need a copy at all is that file's own bullet to say.

    :param trees: the checkouts.
    """
    drifted: dict[str, list[str]] = {}
    for path in verbatim():
        copies: dict[bytes, list[str]] = {}
        for repository, root in sorted(trees.items()):
            here = root / path
            if here.is_file():
                copies.setdefault(here.read_bytes(), []).append(repository)
        if len(copies) > 1:
            drifted[path] = [", ".join(holders) for holders in copies.values()]
    assert not drifted, f"verbatim files that differ between trees: {drifted}"
