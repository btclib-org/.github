# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 2's root-files table is asked of the trees its tiers bind.

The table's last column is which tiers owe the row, which makes it the
one statement in that section of what a repository has to carry, file by
file. `tiers_test.py` asks the other table of the same section -- which
tier a repository is -- and this asks what that tier then owes.

The rows are asked here and their contents elsewhere: `verbatim_test.py`
compares the copies of the rows section 14 also owes of every
repository, and `security_test.py` reads the address the `SECURITY.md`
row's file promises.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from . import ROOT, Tier, name, rows

pytestmark = pytest.mark.integration


def owed() -> dict[str, Tier]:
    """Read the root-files table, by the tier each row reaches.

    The tiers nest, so a row's cell is the tiers from 1 down to the last
    one that owes the file, and that last tier is the row: `binds` then
    answers for it the way the `tier` marker of a test does. A cell
    written any other way is refused rather than read as the tiers it
    happens to parse to, and so is a file the table gives a row twice,
    which a mapping would otherwise read once and drop the other.

    :returns: each path against the tier its row reaches.
    :raises LookupError: where a cell is not the tiers from 1 down, or
        two rows name the same file.
    """
    nested = [str(int(asked)) for asked in Tier]
    out: dict[str, Tier] = {}
    repeated: list[str] = []
    for row in rows(ROOT / "README.md", "file", "what it is", "tiers"):
        path = name(row["file"])
        listed = [cell.strip() for cell in row["tiers"].split(",")]
        if listed != nested[: len(listed)]:
            msg = f"section 2 gives {path} the tiers {row['tiers']!r}"
            raise LookupError(msg)
        if path in out:
            repeated.append(path)
        out[path] = Tier(len(listed))
    if repeated:
        msg = f"section 2's root-files table names these files twice: {repeated}"
        raise LookupError(msg)
    return out


def test_a_repository_carries_the_root_files_its_tier_owes(
    repository: str,
    trees: dict[str, Path],
    tiers: dict[str, Tier],
) -> None:
    """A row the repository's tier binds is a file in its tree.

    That direction and not the other. A tier is a floor rather than a
    ceiling, so a row that does not reach a repository says nothing
    about whether it may carry the file anyway: `portanode` is tier 3
    and carries the `RELEASING.md` and `RELEASE_NOTES.md` its own
    practice needs, and this repository is tier 2 and carries the
    `SECURITY.md` GitHub shows for a repository of the organization with
    none of its own. Section 2 states both, and a test reading the table
    in reverse would report them as findings.

    A publisher with no `SECURITY.md` fails here and in
    `security_test.py`, which needs the file before it can read the
    address out of it.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param tiers: the tier of each repository, measured.
    """
    root = trees[repository]
    here = tiers[repository]
    missing = [
        path
        for path, asked in owed().items()
        if asked.binds(here) and not (root / path).is_file()
    ]
    assert not missing, f"root files this tree's tier owes and it lacks: {missing}"
