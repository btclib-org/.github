# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What a `REPOSITORY.md` claims to cover, which is section 11's rule.

That section bounds the file at the settings the standard asks about --
section 16's checklist, and the sections that state a rule -- and
rejects the copy claiming to be the whole of what is set outside the
tree. The rejected claim is the half a command decides: a file makes it
in its own text, where whether its coverage reaches the perimeter is a
reading, which fields of the repository document are settings rather
than URLs, counts and derived state being what nothing answers.

The section says what falls outside that scope too, under the heading
section 11 names, and that heading is the half of it a command decides:
a copy carries the section or does not, where what the section says
about the perimeter is the same reading.

A third claim of the same kind is the paragraph naming what the scope is
drawn from -- section 16's checklist, a section stating a rule, a
behaviour one rests on -- and section 11 asks a copy to carry those
three limbs in the standard's own words. The paragraph has no backtick
and wraps across several lines, so it is read anchored on its bold
opening rather than on a quoted phrase, the clause taken from between
the paragraph's two em dashes and folded as the other strings are. A
copy may link a limb to the section it names without failing this: the
link is decoration around the same words, not a rewording of them, so
the comparison reads through `[text](url)` and `[text][ref]` alike, the
way a reader's eye does.

The claim, the heading and the limbs are read out of section 11 rather
than written down here, for the reason `fenced` in `tests/__init__.py`
gives: a transcription is the copy that goes stale, and the sentence a
copy may not carry belongs where the rule that refuses it is.

The command a failure names quotes each with `shlex.quote` rather than
writing a shell word around them. Their content is section 11's, and an
apostrophe -- ordinary in an English sentence -- ends a single-quoted
word early.

What this does not reach is the same promise in words of its own, or a
section that names the heading and passes nothing over. A string finds
the sentence and not the claim, so a copy promising completeness some
other way is a reading -- as a claim of this standard that no command
re-derives is anywhere else. Nor does it reach whether a copy is honest
about which of its own settings the limbs cover; that a copy carries the
sentence is what a command asks, and whether the sentence holds for what
follows it is still a reading.
"""

from __future__ import annotations

import re
import shlex
from typing import TYPE_CHECKING

import pytest

from . import ROOT, by_hand, sole

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

SETTINGS = "REPOSITORY.md"
"""The root file section 2's table owes every tier."""

REJECTED = "The claim rejected is"
"""How section 11 opens the sentence that quotes the claim it refuses.

The quotation is read off that one line, so a section wrapping the claim
away from this phrase raises rather than answering with nothing.
"""

HEADED = "The section headed"
"""How section 11 opens the sentence that names the heading a copy carries.

The heading is read off that one line, as the claim is off its own.
"""

LIMBS = "What that file covers is the settings this standard asks about"
"""How section 11 opens the paragraph naming the three limbs.

The paragraph carries no backtick, so this is the anchor `limbs` reads
forward from rather than a phrase `quoted` extracts a text after.
"""

EM_DASH = "—"
"""What delimits the limbs clause on each side of the paragraph."""

EM_DASHES = 2
"""How many of them the paragraph holds, one on each side of the clause."""

QUOTED = re.compile(r"`([^`]+)`")
"""How each of those sentences carries what it quotes."""

LINKED = re.compile(r"\[([^\]]+)\]\([^)]*\)|\[([^\]]+)\]\[[^\]]*\]")
"""A markdown link, inline or by reference, around the words it names.

A copy may wrap a limb in a link to the section it names; the words
inside the brackets are what section 11 asks a copy to carry, and the
link around them is decoration a comparison reads through.
"""

WRAPPED = re.compile(r"\s+")
"""What a claim wrapped at eighty columns has between its words.

Both sides of the comparison are folded on it, so a copy is asked for
the sentence rather than for the line breaks its own margin gave it.

The failure names a command that folds the same way: `tr -s` squeezes
the run an indented continuation leaves, where translating the newline
alone leaves the indent's own spaces beside the one it writes. It asks
for the claim as a string and counts occurrences rather than lines, a
folded file being one line.
"""


def quoted(opening: str) -> str:
    """Read what the one line of section 11 holding a phrase quotes.

    :param opening: the phrase naming the line.
    :returns: the one backticked text on that line.
    :raises LookupError: where the line quotes none, or several.
    """
    document = ROOT / "README.md"
    lines = document.read_text(encoding="utf-8").splitlines()
    found: list[str] = QUOTED.findall(lines[sole(document, lines, opening)])
    if len(found) != 1:
        msg = f"{document.name} quotes {len(found)} texts after {opening!r}"
        raise LookupError(msg)
    return found[0]


def rejected() -> str:
    """Read the claim section 11 refuses, out of the standard.

    :returns: the claim, as that section quotes it, folded.
    """
    return WRAPPED.sub(" ", quoted(REJECTED))


def heading() -> str:
    """Read the heading section 11 asks a copy for, out of the standard.

    The failure names a command asking for the heading as a fixed
    string on a whole line, which is the equality the assertion makes.
    Its wording is section 11's, and a `*` or a `[` -- markdown's
    emphasis and its link -- is an expression to a `grep` reading a
    pattern rather than the character the assertion compares.

    :returns: the heading line, as that section quotes it.
    """
    return quoted(HEADED)


def unlinked(text: str) -> str:
    """Replace a markdown link with the words inside its brackets.

    :param text: the text to strip links from.
    :returns: the text with every `[words](url)` and `[words][ref]`
        replaced by ``words``.
    """
    return LINKED.sub(lambda match: match.group(1) or match.group(2), text)


def limbs() -> str:
    """Read the em-dashed clause naming section 11's three limbs.

    The paragraph is found by its bold opening, `sole` raising where that
    is not exactly one line; the clause is what sits between its first
    two em dashes, folded the way a copy's own wrapping is.

    :returns: the clause, folded and read through `unlinked`.
    :raises LookupError: where the paragraph does not hold exactly two
        em dashes.
    """
    document = ROOT / "README.md"
    lines = document.read_text(encoding="utf-8").splitlines()
    block: list[str] = []
    for line in lines[sole(document, lines, LIMBS) :]:
        if not line.strip():
            break
        block.append(line)
    text = WRAPPED.sub(" ", " ".join(block))
    parts = text.split(EM_DASH)
    if len(parts) != EM_DASHES + 1:
        msg = (
            f"{document.name}'s limbs paragraph holds {len(parts) - 1} "
            f"em dashes, not {EM_DASHES}"
        )
        raise LookupError(msg)
    return unlinked(parts[1].strip())


def test_the_settings_file_does_not_claim_to_be_the_whole_of_them(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 11: a `REPOSITORY.md` covers what the standard asks about.

    A copy carrying the claim is answerable for every setting the
    endpoint has, which is the set nothing enumerates. What it records
    is read back by the commands beside the answers; what it never
    mentions is what the claim covers and nothing reports.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    path = trees[repository] / SETTINGS
    if not path.is_file():
        pytest.skip(f"{repository} has no {SETTINGS}")
    claim = rejected()
    text = WRAPPED.sub(" ", path.read_text(encoding="utf-8"))
    assert claim not in text, (
        f"{SETTINGS} says {claim!r}, which section 11 rejects; "
        + by_hand(
            repository,
            f"tr -s '[:space:]' ' ' < {SETTINGS}"
            f" | grep -oF {shlex.quote(claim)} | wc -l",
        )
    )


def test_the_settings_file_says_what_it_passes_over(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 11: a `REPOSITORY.md` says what falls outside its scope.

    The section is asked for by its heading, a line of the copy, so
    that a copy narrowing its claim and stopping there is not reported
    as converged; what the section says under it is a reading.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    path = trees[repository] / SETTINGS
    if not path.is_file():
        pytest.skip(f"{repository} has no {SETTINGS}")
    wanted = heading()
    lines = path.read_text(encoding="utf-8").splitlines()
    assert wanted in lines, (
        f"{SETTINGS} has no {wanted!r} section, which section 11 asks for; "
        + by_hand(repository, f"grep -cxF {shlex.quote(wanted)} {SETTINGS}")
    )


def test_the_settings_file_carries_section_11s_three_limbs(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 11: a `REPOSITORY.md` carries the three limbs verbatim.

    The clause names what the file's scope is drawn from, and a copy
    wording it for itself is what section 11 forecloses: this asks for
    the clause as one folded string, so a copy naming the same three
    things in another order or joining them with its own connective is
    not this string and fails, the way the standard says it must.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    path = trees[repository] / SETTINGS
    if not path.is_file():
        pytest.skip(f"{repository} has no {SETTINGS}")
    clause = limbs()
    text = unlinked(WRAPPED.sub(" ", path.read_text(encoding="utf-8")))
    assert clause in text, (
        f"{SETTINGS} does not carry section 11's three limbs verbatim "
        f"({clause!r}); "
        + by_hand(
            repository,
            f"tr -s '[:space:]' ' ' < {SETTINGS} | sed -E "
            "'s/\\[([^]]+)\\]\\([^)]*\\)/\\1/g; "
            "s/\\[([^]]+)\\]\\[[^]]*\\]/\\1/g' "
            f"| grep -oF {shlex.quote(clause)} | wc -l",
        )
    )
