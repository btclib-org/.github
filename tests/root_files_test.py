# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What section 2 says a tier's tree holds, and what it keeps out of one.

The root-files table's last column is which tiers owe the row, and a
tier is a floor: a row that stops short of a tier says nothing about a
tree that carries the file anyway. So the table answers one direction,
and the sentence keeping the release documents out of a tier-2
repository is the other -- one rule, stated where the tier is decided
rather than in a column, and read here as prose.

`tiers_test.py` asks the other table of the same section, which tier a
repository is. What a row's file then says is asked elsewhere:
`security_test.py` reads the address the `SECURITY.md` row promises, and
`verbatim_test.py` compares the copies of the rows section 14 also owes
of every repository -- those rows are asked for presence twice, once
against the tier here and once against the clause there.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from . import ROOT, Tier, name, rows, sole

pytestmark = pytest.mark.integration

CEILING = "A tier-2 repository carries neither"
"""How section 2 opens the rule its root-files table cannot carry.

The rule is a ceiling where the table states floors, so no cell of it
answers for one: the two files it names are the table's tier-1 rows, and
`portanode` carries both at tier 3 without contradicting either
statement. It is read out of the section rather than copied here, for
the reason `fenced` in `tests/__init__.py` gives -- a transcription is
the copy that goes stale.
"""

BACKTICKED = re.compile(r"`([^`]+)`")
"""How that sentence names a file."""

CLOSING = ".**"
"""Where the sentence ends: it is bold, and this closes the bold."""


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


def forbidden() -> list[str]:
    """Read the files section 2 keeps out of a tier-2 repository.

    The sentence is bold, so it runs from the phrase that opens it to
    the `.**` that closes the bold, and the files are what it names in
    backticks between the two. The search for that close stops at the
    end of the paragraph: the next one in the document would be found
    just as well, and every file named in between would be read as
    forbidden. A sentence rewritten into a shape this cannot read is the
    failure rather than a run that asks nothing.

    :returns: the paths, in the order the sentence names them.
    :raises LookupError: where the sentence is not there exactly once,
        the bold it opens is not closed in its own paragraph, or it
        names no file.
    """
    document = ROOT / "README.md"
    lines = document.read_text(encoding="utf-8").splitlines()
    start = sole(document, lines, CEILING)
    paragraph = ""
    for line in lines[start:]:
        if not line:
            break
        paragraph += line + "\n"
    sentence = paragraph[paragraph.index(CEILING) :]
    end = sentence.find(CLOSING)
    if end < 0:
        msg = f"{document.name} opens {CEILING!r} and does not close the bold"
        raise LookupError(msg)
    out = BACKTICKED.findall(sentence[:end])
    if not out:
        msg = f"{document.name} states {CEILING!r} and names no file"
        raise LookupError(msg)
    return out


def test_a_tier_2_repository_carries_neither_release_document(
    repository: str,
    trees: dict[str, Path],
    tiers: dict[str, Tier],
) -> None:
    """What section 2 keeps out of a tier-2 tree is out of it.

    A rule whose whole content is an absence, and an absence is what
    nothing notices. Asked of tier 2 alone, which is what the `tier`
    marker cannot say: that marker names the tier a rule applies *down
    to*, and this one reaches neither the tier that owes both files nor
    the tier that may carry them by its own practice. A repository of
    either is skipped with the reason, so the report says which cells
    were not asked.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param tiers: the tier of each repository, measured.
    """
    here = tiers[repository]
    if here != Tier.PYTHON:
        pytest.skip(f"{repository} is tier {here}, and this asks tier 2 alone")
    root = trees[repository]
    held = [path for path in forbidden() if (root / path).is_file()]
    assert not held, f"a tier-2 tree carrying what section 2 keeps out of one: {held}"


def test_the_ceiling_and_the_table_name_the_same_rows() -> None:
    """What section 2 forbids a tier-2 tree, its table gives to tier 1.

    The two statements are the same rule read from either side, and
    nothing but this makes them stay that way: a row moved to `1, 2`
    would leave the table asking a tier-2 repository for a file the
    sentence above it forbids, and the trees would carry the report for
    a contradiction that is the standard's.
    """
    rows_by_tier = owed()
    apart = {
        path: rows_by_tier.get(path)
        for path in forbidden()
        if rows_by_tier.get(path) is not Tier.PUBLISHER
    }
    assert not apart, f"section 2 forbids what its table does not give tier 1: {apart}"
