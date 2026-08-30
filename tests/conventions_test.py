# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The convention-test declaration in `tests/README.md` is true.

Section 7 lists the conventions a suite can turn into a red test and
closes with the clause that makes the list usable: a repository needs
the ones its own prose states rather than all of them. The price of that
clause is that an absent convention test cannot be told from a
convention the repository does not have, and the declaration is what
tells them apart. This module is what keeps the declaration from being
prose -- section 7's own rule, that a convention worth stating is worth
a test, asked of section 7 itself.

The conventions are read off `README.md` rather than transcribed here.
A sibling suite transcribes them because the standard is in another
repository and a copy is the only form it can hold there; in this tree
the standard and the declaration are the same commit, so a copy would be
the second statement section 9 refuses, and it would be the one that
goes stale -- a bullet added to section 7 lands with nothing to notice
that neither half of the declaration accounts for it.

What this cannot check is whether a module named against a convention
tests that convention. Nothing short of reading it can, and the
assertions below are the ones that fail on the ways a declaration rots:
a convention invented here rather than taken from section 7, a module
renamed or deleted with the row left behind, a module emptied of its
tests, and a bullet that quietly stops being accounted for by either
half.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from . import EMPHASISED, ROOT, name, rows, subjects

TESTS = Path(__file__).parent

DECLARATION = TESTS / "README.md"
"""The file section 7 asks each repository to declare its testing in."""

OPENING = "carries an exemption list that is allowed to grow"
"""The prose section 7's list of conventions follows."""

CLOSING = "A new repository does not need all of these"
"""The prose section 7's list of conventions stops at.

The escape clause itself, which is the sentence the declaration exists
for: a repository takes the bullets its own conventions state, and
nothing after this line is one of them.
"""

NOT_TESTED = re.compile(r"^Not tested here: (.+?)\.$", re.MULTILINE | re.DOTALL)
"""The half of the declaration that names what carries no test.

DOTALL as well as MULTILINE because eighty columns wrap the list of
names across lines, and the non-greedy match then stops at the first
full stop ending one -- which is why no name in it may carry a full stop
of its own. The names are separated by semicolons, a comma appearing
inside one, and the wrap is taken out of a name before it is compared:
a line break falls wherever eighty columns put it.
"""

CONVENTIONS = tuple(subjects(ROOT / "README.md", OPENING, CLOSING, EMPHASISED))
"""Section 7's conventions, in its order and its words."""

ROWS = tuple(
    (row["convention"], name(row["module"]))
    for row in rows(DECLARATION, "convention", "module")
)
"""The half of the declaration that names a module for a convention."""


@pytest.mark.parametrize(("convention", "module"), ROWS, ids=lambda value: value)
def test_every_convention_named_is_one_of_section_sevens(
    convention: str, module: str
) -> None:
    """A convention invented here is not a convention the standard has.

    :param convention: the row's first cell.
    :param module: the row's second cell, for the message.
    """
    assert convention in CONVENTIONS, (
        f"{module} is declared against {convention!r}, which is not one of"
        f" section 7's: {', '.join(CONVENTIONS)}"
    )


@pytest.mark.parametrize(("convention", "module"), ROWS, ids=lambda value: value)
def test_every_module_named_exists(convention: str, module: str) -> None:
    """A row outliving the file it names is the ordinary way this rots.

    :param convention: the row's first cell, for the message.
    :param module: the row's second cell.
    """
    assert (TESTS / module).is_file(), (
        f"{DECLARATION.name} declares {convention!r} tested in {module},"
        " which is not a file in this directory"
    )


@pytest.mark.parametrize(("convention", "module"), ROWS, ids=lambda value: value)
def test_every_module_named_holds_a_test(convention: str, module: str) -> None:
    """A file emptied of its tests still satisfies the check above.

    The source is parsed rather than the suite queried: an import would
    make this module's result depend on every other module's import
    side effects, and pytest's own collection is not available to a test
    it has already collected.

    :param convention: the row's first cell, for the message.
    :param module: the row's second cell.
    """
    # no guard for a missing file: the test above is what reports that,
    # and a guard here would be a branch nothing can reach while it passes
    path = TESTS / module
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found = any(
        isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        and node.name.startswith("test_")
        for node in ast.walk(tree)
    )
    assert found, (
        f"{module} is declared to test {convention!r} and defines no"
        " function whose name begins with test_"
    )


def test_the_two_halves_account_for_every_convention() -> None:
    """The table and the *Not tested here* line partition section 7's set.

    This is the assertion the declaration exists for. Either half alone
    is satisfiable by saying less: a table naming one convention is true
    about that one and silent about the rest, and silence is exactly
    what section 7's escape clause makes unreadable. Together they have
    to name each convention once.

    A table this module's reader stopped seeing is the failure that
    would hide here, every assertion above quantifying over the rows and
    so passing on an empty set. `rows` refuses a header it cannot find
    exactly once, which leaves a header it finds and a body of no rows,
    and this is where that shows: every convention is then unaccounted
    for unless the other half names it.
    """
    found = NOT_TESTED.findall(DECLARATION.read_text(encoding="utf-8"))
    assert len(found) == 1, (
        f'{DECLARATION.name} holds {len(found)} "Not tested here: ...."'
        " lines; the declaration is half of one"
    )
    listed = " ".join(found[0].split())
    absent = () if listed == "none" else tuple(listed.split("; "))
    tested = {convention for convention, _ in ROWS}

    overlap = tested.intersection(absent)
    assert not overlap, (
        f"{', '.join(sorted(overlap))} is both declared tested and listed as not tested"
    )

    unknown = [convention for convention in absent if convention not in CONVENTIONS]
    assert not unknown, (
        f"{', '.join(unknown)} is listed as not tested and is not one of"
        f" section 7's: {', '.join(CONVENTIONS)}"
    )

    unaccounted = [
        convention
        for convention in CONVENTIONS
        if convention not in tested and convention not in absent
    ]
    assert not unaccounted, (
        f"{', '.join(unaccounted)} is neither declared tested nor listed as"
        " not tested; section 7's conventions are what the two halves"
        " must cover"
    )
