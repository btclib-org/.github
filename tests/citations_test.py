# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Every citation of a section names words the document it cites holds.

Section 9 has a citation carry what its target's stability requires, and
a section is the case where nothing else can tell: a path resolves or it
does not, and a line number brings the revision that fixes it, where a
heading resolves for nobody. It is prose, it reads as durable, and it is
retitled by whoever improves a sentence. So the words are what a
citation is checked by, and this is what checks them -- in every tree,
because the run that would notice is the one over the file holding the
citation rather than the one over the document cited.

Two shapes, because the organization writes two. A section of this
standard is cited by its number -- `section 11's *Review*` -- so the
words are looked for in that section of this tree's `README.md`,
whichever tree the citation is written in. A section of a tree's own
document is cited by the file -- `CONTRIBUTING.md`'s *The issue
tracker* -- so they are looked for in that tree's file of that name, at
whatever path it keeps it.

The words may be the heading's own, a bullet's opening or a sentence:
what fails here is a citation whose words the document holds nowhere,
which is the citation that has stopped answering a reader too. Matching
against the headings alone would report the organization's commonest
citation, a bullet cited by its bold opening, as a defect.

What this does not read is `CHANGELOG.md`, `RELEASE_NOTES.md` and an
archived `changelog/`: section 9 has nothing already written in them
rewritten, so an entry citing a heading that has since moved is a record
of its own day, and no edit answers a failure here.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from . import ROOT, SELF, by_hand, tracked

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from pathlib import Path

pytestmark = pytest.mark.integration

STANDARD = ROOT / "README.md"
"""The file a citation by section number names, whoever writes it."""

QUOTED = r"""(?P<mark>[*"])(?P<cited>[^*"]{3,90}?)(?P=mark)"""
"""How a citation sets the words off: emphasis, or a pair of quotes."""

NUMBERED = re.compile(
    r"[Ss]ection (?P<number>\d+)"
    r"""(?: of (?:(?!ection)[^*"]){0,40}?)?'s """ + QUOTED
)
"""A section of the standard, cited by its number.

The optional middle is the form naming the document as well -- *section
2 of the organization standard's `The documentation`* -- and it refuses
a second `ection`, so that a sentence naming one section and citing
another is read as the citation in it rather than as a citation of the
first number in it.
"""

DOCUMENT = re.compile(r"""`?(?P<document>[A-Za-z0-9_.-]+\.md)`?'s """ + QUOTED)
"""A section of a document of the tree the citation is written in."""

OPENING = re.compile(r"(?m)^## (\d+)\. ")
"""How the standard opens a numbered section."""

HISTORY = re.compile(r"^(CHANGELOG|RELEASE_NOTES)\.md$|^changelog/")
"""What section 9 keeps as written, so a citation in it is a record."""


def flattened(text: str) -> str:
    """Reduce prose to the words in it, whatever lies between them.

    A citation is prose and prose wraps, so a line is the wrong unit:
    the eighty-column margin falls inside a citation as readily as
    between two, and a comment continued on the next line carries that
    line's own `#` into the middle of the quotation. Dropping everything
    that is not a word takes both, and takes the backticks and the
    apostrophe a citation renders with as well.

    :param text: the file's text.
    :returns: its words, lowercased, one space apart.
    """
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text)).strip().lower()


def sections(standard: str) -> dict[str, str]:
    """Split the standard into its numbered sections.

    :param standard: this tree's `README.md`.
    :returns: each section's number against the words under its heading.
    """
    parts = OPENING.split(standard)
    return {parts[i]: flattened(parts[i + 1]) for i in range(1, len(parts), 2)}


def prose(root: Path, paths: list[str]) -> Iterator[tuple[str, str]]:
    """Read every tracked file a citation of section 9's is answerable for.

    A file holding no possessive holds no citation of either shape, and
    the test data a tree vendors is megabytes of it: the substring is
    what keeps this from rewriting them all a whitespace run at a time.

    :param root: the root of the checkout.
    :param paths: what the tree tracks.
    :yields: each path against its text, on one line.
    """
    for path in paths:
        if HISTORY.search(path):
            continue
        try:
            text = (root / path).read_text(encoding="utf-8")
        except OSError, UnicodeDecodeError:
            # a submodule's gitlink, which `git ls-files` names and the
            # clones here leave unfetched, and a file that is not text
            continue
        if "'s" not in text:
            continue
        yield path, re.sub(r"\s+", " ", text)


def unresolved(
    path: str,
    text: str,
    standard: dict[str, str],
    holds: Callable[[str], str],
) -> list[str]:
    """Name the citations of one file that resolve nowhere.

    :param path: the file, for the message.
    :param text: its text, on one line.
    :param standard: each section number of the standard against its words.
    :param holds: the words of a document of the tree, by file name.
    :returns: one line per citation resolving nowhere.
    """
    out: list[str] = []
    for found in NUMBERED.finditer(text):
        number, cited = found["number"], found["cited"]
        if flattened(cited) not in standard.get(number, ""):
            out.append(f"{path}: section {number}'s *{cited}*")
    for found in DOCUMENT.finditer(text):
        document, cited = found["document"], found["cited"]
        if flattened(cited) not in holds(document):
            out.append(f"{path}: {document}'s *{cited}*")
    return out


def dead(root: Path, standard: dict[str, str]) -> list[str]:
    """List the citations of a tree that name words nothing holds.

    :param root: the root of the checkout.
    :param standard: each section number of the standard against its words.
    :returns: one line per citation resolving nowhere, sorted.
    """
    paths = tracked(root)
    documents: dict[str, str] = {}

    def holds(document: str) -> str:
        if document not in documents:
            documents[document] = words(root, paths, document)
        return documents[document]

    return sorted(
        line
        for path, text in prose(root, paths)
        for line in unresolved(path, text, standard, holds)
    )


def words(root: Path, paths: list[str], document: str) -> str:
    """Read every file of a tree that a citation naming one could mean.

    A citation names the file and not the path, and a tree keeps more
    than one `README.md`, so the copies are read together: which of them
    was meant is a question a reader answers and this does not have to.

    :param root: the root of the checkout.
    :param paths: what the tree tracks.
    :param document: the file name the citation gives.
    :returns: the words of every tracked file of that name.
    """
    return " ".join(
        flattened((root / path).read_text(encoding="utf-8"))
        for path in paths
        if path == document or path.endswith(f"/{document}")
    )


POSSESSIVE = "'s"
"""What a citation puts after the thing it names.

Held apart from the words below it so that this module's own source
carries no citation of a section the standard does not have: the cell
over this tree reads this file like any other, and a dead citation
planted here as a control would be reported as the defect it is made to
look like -- the check working, and a red run to explain every time.
"""


def test_a_sentence_naming_two_sections_is_read_as_citing_the_second() -> None:
    """The pattern's own control: two sections in one sentence.

    A number and a citation of another section in one sentence are what
    a pattern reading from the first number to the first emphasis pairs
    wrongly, and the pair it invents resolves in neither section -- a
    defect reported against prose holding none.
    """
    both = "Section 7's changelog bullet, and section 9's *Measure, don't assert*"
    assert [found["cited"] for found in NUMBERED.finditer(both)] == [
        "Measure, don't assert"
    ]


def test_a_citation_of_words_the_standard_does_not_hold_is_named() -> None:
    """The perturbation: what the cell below reports, planted here.

    The check is an absence over every tree, and an absence passes for
    the wrong reason as readily as for the right one -- a pattern that
    matched nothing would report every tree clean. So a citation the
    standard cannot answer is built and asked about, against the same
    section 9 the trees are asked about.
    """
    planted = f"section 9{POSSESSIVE} *a rule the standard does not carry*"
    standard = sections(STANDARD.read_text(encoding="utf-8"))
    assert unresolved("planted.md", planted, standard, lambda _: "") == [
        f"planted.md: {planted}"
    ]


def test_the_standard_is_read_as_the_sections_it_numbers() -> None:
    """`sections()` answers for each numbered heading, and for it alone.

    A split taking the `###` headings too would answer words the section
    above them holds; one taking none would answer the whole file for
    every number, which is a check that cannot fail. The two phrases are
    read off the file, one per section, and asked of both.
    """
    numbered = sections(STANDARD.read_text(encoding="utf-8"))
    assert sorted(numbered, key=int) == [str(number) for number in range(1, 17)]
    assert "tone neutral factual dry" in numbered["9"]
    assert "tone neutral factual dry" not in numbered["10"]
    assert "lychee" in numbered["10"]
    assert "lychee" not in numbered["9"]


def test_every_citation_of_a_section_resolves_in_what_it_names(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """A citation quotes words the document it names holds.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    standard = sections((trees[SELF] / "README.md").read_text(encoding="utf-8"))
    broken = dead(trees[repository], standard)
    assert not broken, (
        f"citations naming words no document holds: {broken}; "
        + by_hand(repository, """grep -rEn "'s [*\\"]" .""")
    )
