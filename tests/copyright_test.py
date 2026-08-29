# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The `notice-rgx` of every repository is its `COPYRIGHT`, transcribed.

Section 5 makes the copyright header a ruff rule: `CPY` checks every
source file against `notice-rgx`, and `notice-rgx` is `COPYRIGHT`'s text
escaped into a regex by hand. ruff reads the regex and never the file,
so the second link of that chain is checked in every repository that
selects the rule and the first is checked nowhere: a tree whose
`COPYRIGHT` and whose `notice-rgx` disagree passes its own gate. This is
the first link -- section 7's shape, a generated thing compared against
its source -- asked of every tree at once, because `COPYRIGHT` is a
section 14 file and the transcription is owed to be the same wherever
the file is.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from . import Tier, by_hand

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

METACHARACTERS = frozenset(r"\.^$|?*+()[]{}")
"""What a transcription escapes: the characters a regex reads as syntax.

Not `re.escape`, which also escapes a space and a `#`, neither of which
means anything outside verbose mode and both of which open every line of
the file. The transcription is one spelling rather than any regex that
happens to match, so that the copies can be compared byte for byte and a
drifted one names its own difference.
"""


def transcribed(source: Path) -> str:
    r"""Derive the `notice-rgx` a `COPYRIGHT` file asks for.

    Each line with its metacharacters escaped, the lines joined by a
    literal `\n`, the whole anchored with `^`: the header is the file's
    text and it opens the source file, which is what the anchor says.

    :param source: the `COPYRIGHT` file to transcribe.
    :returns: the regex, as `pyproject.toml` holds it once parsed.
    """
    lines = source.read_text(encoding="utf-8").splitlines()
    escaped = (
        "".join(f"\\{char}" if char in METACHARACTERS else char for char in line)
        for line in lines
    )
    return "^" + r"\n".join(escaped)


def collective(source: Path) -> str:
    """Read the name a `COPYRIGHT` file's first line credits.

    `transcribed` turns the whole file, that line included, into
    `notice-rgx`; this reads the line alone, for `[project].authors`,
    which section 3 ties to this file so that the two names cannot drift
    apart unseen. `pyproject_test.py` asks the question the derivation
    is for; this stays here, beside `transcribed`, because both derive
    from `COPYRIGHT` rather than from a literal of their own.

    :param source: the `COPYRIGHT` file to read.
    :returns: the name after `Copyright (c) `.
    """
    first = source.read_text(encoding="utf-8").splitlines()[0]
    return first.removeprefix("# Copyright (c) ")


def declared(parsed: dict[str, Any]) -> str | None:
    """Read the `notice-rgx` a parsed `pyproject.toml` declares.

    :param parsed: the file, parsed.
    :returns: the regex, or None where the table or the key is absent.
    """
    table = parsed.get("tool", {}).get("ruff", {}).get("lint", {})
    value = table.get("flake8-copyright", {}).get("notice-rgx")
    return value if isinstance(value, str) else None


@pytest.mark.tier(Tier.PYTHON)
def test_every_notice_rgx_is_its_copyright_transcribed(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Where a repository declares the regex, it is its own file's text.

    A repository that declares none is skipped rather than failed:
    whether it selects `CPY` at all is section 5's question of that
    tree, asked in `pyproject_test.py`, and a tree that selects the rule
    without the key fails its own gate on every file, ruff's default
    regex asking for a year the notice does not carry.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: the parsed files.
    """
    regex = declared(pyprojects[repository])
    if regex is None:
        pytest.skip(f"{repository} declares no notice-rgx")
    expected = transcribed(trees[repository] / "COPYRIGHT")
    assert regex == expected, (
        f"notice-rgx is not COPYRIGHT transcribed: declared {regex!r},"
        f" expected {expected!r}; "
        + by_hand(repository, "grep -n 'notice-rgx' pyproject.toml; cat COPYRIGHT")
    )
