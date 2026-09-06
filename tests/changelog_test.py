# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Neither history file of this tree states a count of itself.

Section 7's changelog bullet, and section 9's *Measure, don't assert* in
this repository's own prose: a number nothing derives is right or wrong
invisibly, a stated total is a line every open branch has to edit, and
two branches moving it to the same wrong number merge without a
conflict. `.gitattributes` marks both files `merge=union`, which is the
half no local command reports: under that driver the two branches do not
conflict at all, and neither does a rebase that carries an edit to a
count paragraph back over the file.

Section 11 says a count is not reachable by a pattern, a number being a
defect for what it counts rather than for the string it is, and that is
a rule about counts of anything. What this module reads is narrower and
is reachable: a count of the file's *own* parts, which are its entries
and their bullets. The two patterns divide that question by whom the
parts are said to belong to -- a sentence naming the file as their
owner, and a sentence naming no owner at all, a count with none being a
count of the file it is written in. What section 9 permits is the third
case: an entry counting something in the world, which is a fact about a
change and not about the file.

An owner is read only where it stands in front of the count, which is
where the entries of this file put one. So a sentence putting it after
the count instead -- *four entries in `README.md`* -- is reported, and
wrongly. That is the side to be wrong on: reading the whole sentence
for an owner would suppress a count of this file whenever a filename
stood anywhere near it, and this way the report names the sentence it
objects to.

Asked of this tree alone, where the rest of this suite asks every
repository at once: section 7 puts a convention test in the suite of the
tree whose convention it is, and `btclib`'s `tests/README.md` declares
the changelog bullet against a module of its own.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from . import ROOT
from .names_test import HISTORIES

if TYPE_CHECKING:
    from pathlib import Path

WORDS = (
    "hundred|thousand|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
    "|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen"
    "|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|one"
)
"""The number words prose spells a total in.

`one` is there for the compounds that close on it -- forty-one, a
hundred and one -- and not for a total of one, which `PARTS` being
plural leaves no way to write.
"""

CARDINAL = rf"(?:\d[\d,]*|(?:a |an )?(?:{WORDS})(?:[ -](?:and[ -])?(?:{WORDS}))*)"
"""A total, in digits or in words, hyphenated and joined runs included."""

PARTS = r"(?:entries|bullets)"
"""What a history file's own parts are called."""

UNATTRIBUTED = re.compile(rf"(?i)\b{CARDINAL}\s+{PARTS}\b")
"""A count of parts with no owner: the owner is then the file it is in."""

ELSEWHERE = re.compile(r"(?:'s|\bsections?)\s*\Z", re.IGNORECASE)
"""What says the parts counted are somebody else's.

A possessive gives them an owner, and a number a section's name ends
with is a name rather than a count. Read from the text before the match
and not from the sentence: the file wraps at eighty columns, so the
words either side of a count are as often on two lines as on one.
"""

ITS_OWN = re.compile(
    rf"(?i)(?:this file|this changelog|the changelog|CHANGELOG\.md)[^.]{{0,120}}?"
    rf"\b{CARDINAL}\s+{PARTS}\b"
    rf"|\b{CARDINAL}\s+{PARTS}\b[^.]{{0,60}}?(?:here|above|below|in this file)"
)
"""A count of parts the sentence claims for the file it is written in.

The exclusion above drops a count whose parts carry an owner, and this
is why that is safe: a possessive naming *this* file is caught here
instead. The two orders are both written -- the file before the number
and the number before the place -- and the bound on either side keeps
the match inside one sentence, a full stop being what ends it.
"""

WINDOW = 40
"""How far back the exclusion looks for the owner of what is counted."""

FILES = tuple(ROOT / history for history in HISTORIES if (ROOT / history).is_file())
"""The history files this tree carries.

`root_files_test.py` is what makes `CHANGELOG.md`'s absence red, section
2 owing it of every tier, so this cannot become an empty parametrization
without that failing first. `RELEASE_NOTES.md` is owed by no tier and
joins the moment a tree writes one.
"""

RESURRECTED = (
    "A hundred and eighty entries, grouped. The order runs from what breaks",
    "The largest yet: a hundred and eighty\nentries, and every one of them",
    "115 entries so far, and the count is in the header.",
    "This file holds a hundred and twelve\nentries.",
    "the changelog's twenty-nine entries",
    "the twenty-nine entries here",
    "Forty-one entries, grouped by subject.",
)
"""Counts of the file itself, in the shapes a hand or a rebase writes.

The compound closing on `one` is here because that word earns its place
in `WORDS` only through such a compound: a control short of one leaves
every total ending that way unguarded while the rest still match.
"""

PERMITTED = (
    "`REVIEWING.md` and `.claude/commands/review.md` are section 14\nentries.",
    "*Which trees carry which\nsentinel*'s two entries named neither",
)
"""Counts of parts belonging elsewhere, as `CHANGELOG.md` states them.

The first counts nothing, `14` being a section's number; the second
counts the rows of a table in `README.md`. They are here as well as in
the file so that a pattern widened past the exclusion fails a test
saying which shape it broke, rather than the one saying a history file
states a count of itself.
"""


def counts(text: str) -> list[str]:
    """Return every count of itself a piece of prose states.

    :param text: the prose to read.
    :returns: the text of each count, empty where there is none.
    """
    out = [
        found[0]
        for found in UNATTRIBUTED.finditer(text)
        if not ELSEWHERE.search(text[max(0, found.start() - WINDOW) : found.start()])
    ]
    out += [found[0] for found in ITS_OWN.finditer(text)]
    return out


@pytest.mark.parametrize("path", FILES, ids=lambda path: path.name)
def test_the_file_states_no_count_of_itself(path: Path) -> None:
    """Written by hand, or put back by a union merge with nothing to decide.

    :param path: the history file to read.
    """
    stated = counts(path.read_text(encoding="utf-8"))
    assert not stated, (
        f"{path.name} states a count of itself: {stated}."
        " Take it out rather than correcting it -- a reader who wants"
        " the number counts the entries, and under `merge=union` such a"
        " paragraph comes back in silence."
    )


def test_the_patterns_still_match() -> None:
    """The guard above passes for free if its patterns match nothing.

    Which is the failure mode of every assertion written in the
    negative, and the one the file it reads cannot reveal: a pattern
    reworded past the text it forbids leaves a green test guarding an
    empty set.
    """
    for text in RESURRECTED:
        assert counts(text), text
    for pattern in (UNATTRIBUTED, ITS_OWN):
        assert any(pattern.search(text) for text in RESURRECTED), pattern.pattern


def test_a_count_of_somebody_elses_parts_is_not_reported() -> None:
    """The other half: a guard that reports everything is no guard.

    An entry counting what a change did is what section 9 keeps, so a
    pattern that cannot tell those from a count of the file would make
    the assertion above red on prose the standard permits.
    """
    for text in PERMITTED:
        assert not counts(text), text
