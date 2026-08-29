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

The claim is read out of section 11 rather than written down here, for
the reason `fenced` in `tests/__init__.py` gives: a transcription is the
copy that goes stale, and the sentence a copy may not carry belongs
where the rule that refuses it is.

What this does not reach is the same promise in words of its own. A
string finds the sentence and not the claim, so a copy promising
completeness some other way is a reading, as a claim of this standard
that no command re-derives is anywhere else.
"""

from __future__ import annotations

import re
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

QUOTED = re.compile(r"`([^`]+)`")
"""How that sentence carries the claim."""

WRAPPED = re.compile(r"\s+")
"""What a claim wrapped at eighty columns has between its words.

Both sides of the comparison are folded on it, so a copy is asked for
the sentence rather than for the line breaks its own margin gave it.
"""


def rejected() -> str:
    """Read the claim section 11 refuses, out of the standard.

    :returns: the claim, as that section quotes it.
    :raises LookupError: where the sentence quotes none, or several.
    """
    document = ROOT / "README.md"
    lines = document.read_text(encoding="utf-8").splitlines()
    found = QUOTED.findall(lines[sole(document, lines, REJECTED)])
    if len(found) != 1:
        msg = f"{document.name} quotes {len(found)} claims after {REJECTED!r}"
        raise LookupError(msg)
    return WRAPPED.sub(" ", found[0])


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
        + by_hand(repository, f"tr '\\n' ' ' < {SETTINGS} | grep -c '{claim}'")
    )
