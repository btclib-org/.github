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

A count a relative clause follows -- *two entries that each close one
issue* -- is a shape rather than a total: the clause restricts the
parts to the ones doing what it says, and how many of those there are
is what an entry says of a change, not of the file. Where the file is
named in front of such a count, the count is reported all the same, the
pattern for an owned count reading the owner and not the clause.

This rule is wrong on the other side from the owner rule above. A
genuine total the writer follows with such a clause -- *twenty-nine
entries, each closing one issue* -- goes unreported, and the file is
left free to state it in that shape. That is the cheaper mistake of the
two here: the shape is what an entry describing what several entries do
writes, so marking it would put a false report against work the entry
is about, where the total it lets through is a sentence about the file
that somebody has to write on purpose.

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

SHAPE = re.compile(r"(?i),?[^\S\n]*\n?[^\S\n]*(?:that|which|each)\b")
"""What says a count is of the parts of one kind, not the file's total.

A relative clause after the count -- *two entries that each close one
issue*, *two entries, each closing one* -- restricts the parts counted
to the ones doing what the clause says. Matched at the count's end, so
it reads what follows the match and nothing further, the way
`ELSEWHERE` reads what precedes it; a full stop or a semicolon between
the count and the word is not crossed, that being a new sentence about
the same parts, and neither is a blank line, which is the stronger
boundary of the two. One line break is crossed and a second is not: the
file wraps at eighty columns, so the clause is as often on the next line
as on the same one, where a paragraph break is a writer starting again.
"""

ITS_OWN = re.compile(
    rf"(?i)(?:this file|this changelog|the changelog|CHANGELOG\.md)[^.]{{0,120}}?"
    rf"\b{CARDINAL}\s+{PARTS}\b"
    rf"|\b{CARDINAL}\s+{PARTS}\b[^.]{{0,60}}?(?:here|above|below|in this file)"
)
"""A count of parts the sentence claims for the file it is written in.

`ELSEWHERE` drops a count whose parts carry an owner and `SHAPE` one a
clause follows, and this is why both are safe: a possessive naming
*this* file is caught here instead, and so is a clause after a count
the file is named in front of. The two orders are both written -- the
file before the number and the number before the place -- and the bound
on either side keeps the match inside one sentence, a full stop being
what ends it.
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
    "This file holds two entries that each close one issue.",
    "The open section holds forty-one entries\n\nEach of them closes one.",
)
"""Counts of the file itself, in the shapes a hand or a rebase writes.

The compound closing on `one` is here because that word earns its place
in `WORDS` only through such a compound: a control short of one leaves
every total ending that way unguarded while the rest still match. The
last carries the clause `PERMITTED`'s third does, with the file named
in front of the count: `SHAPE` drops the count and `ITS_OWN` reports
it, and a change to `ITS_OWN` that stops it reporting fails here rather
than leaving the file free to state its total in that shape. The last
puts a paragraph break where the clause would stand, which is a total
and a new sentence rather than a shape; a `SHAPE` that crossed it would
drop the count and fail here.
"""

PERMITTED = (
    "`REVIEWING.md` and `.claude/commands/review.md` are section 14\nentries.",
    "*Which trees carry which\nsentinel*'s two entries named neither",
    (
        "A rule refuses a heading repeated in the open section, two entries"
        " that each close one issue, and a third shape."
    ),
    "an open section of two entries,\neach closing one issue",
    "two entries which each close one issue",
)
"""Counts of parts belonging elsewhere, or of what several entries do.

The first counts nothing, `14` being a section's number; the second
counts the rows of a table in `README.md`; the last three count what
several entries do, a clause after the count saying which ones, the
third being the sentence btclib-org/.github#980 reproduces with. The
first two are here as well as in the file so that a pattern widened
past an exclusion fails a test saying which shape it broke, rather than
the one saying a history file states a count of itself. The last three
carry one word of `SHAPE`'s alternation each, so that dropping any of
the three from the pattern reddens this test; the entry this branch
writes carries the `that` shape as well, which guards that word here
and in the file both.
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
        and not SHAPE.match(text, found.end())
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
