# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""`bulleted` reads every item of a list, or refuses the list.

Section 14's list of verbatim files is read by `bulleted`, and an item it
passes over is a copy nothing compares. These tests reach nothing outside
this tree, so they carry no `integration` marker and run in `lint.yml`'s
suite, on the pull request that changes the list.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import ROOT, bulleted
from .verbatim_test import verbatim

if TYPE_CHECKING:
    from pathlib import Path

FIRST = "- `A.md` — owed by every repository; it wraps"
"""The bullet every fixture opens with, wrapped over `WRAP`."""

WRAP = "  over a second line."

READ = f"{FIRST} {WRAP.strip()}"
"""`FIRST` and `WRAP` as `bulleted` returns them, joined by a space."""

PARAGRAPH = ["", "A paragraph closes the list above.", ""]

ITEM = "`B.md` — owed by every repository."
"""What each fixture's second item says after its marker."""

REFUSED = {
    "asterisk": [f"* {ITEM}"],
    "plus": [f"+ {ITEM}"],
    "dot": [f"1. {ITEM}"],
    "parenthesis": [f"1) {ITEM}"],
    "dash after one space": [f" - {ITEM}"],
    "dash nested under the bullet": [f"  - {ITEM}"],
    "dot nested by four spaces": [f"    1. {ITEM}"],
    "dot nested by a tab after a blank line": ["", f"\t1. {ITEM}"],
    "asterisk after a paragraph": [*PARAGRAPH, f"  * {ITEM}"],
    "dash after a paragraph": [*PARAGRAPH, f"  - {ITEM}"],
}
"""Each list item `bulleted` cannot read, after the opening bullet.

Every one is an item to Markdown: micromark, the parser markdownlint-cli2
runs, renders each as a list item, nested in the bullet or of its own.
"""


OPENED = {
    "indented line": "  more.",
    "heading": "# Heading",
    "table row": "| a | b |",
    "table delimiter row": "--- | ---",
    "html": "<div>",
    "backtick fence": "```",
    "tilde fence": "~~~",
    "thematic break of asterisks": "***",
    "thematic break of underscores": "___",
    "setext underline": "===",
    "footnote": f"[^1]: - {ITEM}",
}
"""A line opening a block that is no paragraph, put after a paragraph."""

UNREAD = "is no bullet and no paragraph"
"""What `bulleted` says of a line opening such a block."""

UNPLACED = {
    "block quote": ([f"> - {ITEM}"], "opens a block quote"),
    "block quote after a paragraph": (
        [*PARAGRAPH, f"> - {ITEM}"],
        "opens a block quote",
    ),
    "block quote under the bullet": ([f"  > - {ITEM}"], "opens a block quote"),
    **{
        f"{name} after a paragraph": ([*PARAGRAPH, line], UNREAD)
        for name, line in OPENED.items()
    },
}
"""Each line `bulleted` cannot place, against what it says of it.

A block quote may hold a list item, and so may a footnote; the rest open
a block this does not read. Each is refused rather than passed over.
"""

PROSE = {
    "em dash": "— This remains optional.",
    "colon": ": This remains optional.",
    "digit": "15's loop is what checks it.",
    "non-ASCII letter": "Élan is a word.",
    "link": "[A link](https://example.org) opens it.",
    "emphasis": "**Bold** opens it, and _this_ too.",
    "code": "`code` opens it.",
}
"""Paragraph openings `bulleted` reads: micromark renders each as a `<p>`."""


def planted(tmp_path: Path, lines: list[str]) -> Path:
    """Write a list between the two lines `bulleted` is given.

    :param tmp_path: where the file is written.
    :param lines: what follows the opening bullet and its wrapped line.
    :returns: the file.
    """
    document = tmp_path / "list.md"
    body = ["Opening.", "", FIRST, WRAP, *lines, "", "Closing."]
    document.write_text("\n".join(body) + "\n", encoding="utf-8")
    return document


def read(document: Path) -> list[str]:
    """Read the planted list.

    :param document: the file `planted` wrote.
    :returns: its bullets.
    """
    return bulleted(document, "Opening.", "Closing.")


def test_a_bullet_is_read_with_its_wrapped_lines(tmp_path: Path) -> None:
    """The control: a second bullet is read, at the margin or after prose.

    :param tmp_path: where the file is written.
    """
    second = f"- {ITEM}"
    assert read(planted(tmp_path, [second])) == [READ, second]
    assert read(planted(tmp_path, [*PARAGRAPH, second])) == [READ, second]
    assert read(planted(tmp_path, PARAGRAPH)) == [READ]
    assert read(planted(tmp_path, ["", "\tmore."])) == [f"{READ} more."]


def test_a_nested_item_is_read_as_part_of_its_bullet_where_asked(
    tmp_path: Path,
) -> None:
    """With `nested`, an item under a bullet joins it; after a paragraph, not.

    :param tmp_path: where the file is written.
    """
    document = planted(tmp_path, [f"    - {ITEM}"])
    joined = [f"{READ} - {ITEM}"]
    assert bulleted(document, "Opening.", "Closing.", nested=True) == joined
    document = planted(tmp_path, ["  > quoted."])
    quoted = [f"{READ} > quoted."]
    assert bulleted(document, "Opening.", "Closing.", nested=True) == quoted
    document = planted(tmp_path, [*PARAGRAPH, f"  * {ITEM}"])
    with pytest.raises(LookupError, match="opens an item, not a bullet"):
        bulleted(document, "Opening.", "Closing.", nested=True)


@pytest.mark.parametrize("lines", REFUSED.values(), ids=REFUSED.keys())
def test_an_item_that_is_not_a_bullet_is_refused(
    tmp_path: Path, lines: list[str]
) -> None:
    """A list item with any other marker raises, naming its line.

    :param tmp_path: where the file is written.
    :param lines: the lines that follow the opening bullet.
    """
    with pytest.raises(LookupError, match=r"list\.md:\d+ opens an item, not a bullet"):
        read(planted(tmp_path, lines))


@pytest.mark.parametrize(("lines", "message"), UNPLACED.values(), ids=UNPLACED.keys())
def test_a_line_that_is_no_bullet_and_no_paragraph_is_refused(
    tmp_path: Path, lines: list[str], message: str
) -> None:
    """A line `bulleted` cannot place raises, naming its line.

    :param tmp_path: where the file is written.
    :param lines: the lines that follow the opening bullet.
    :param message: what the refusal says of the line.
    """
    with pytest.raises(LookupError, match=rf"list\.md:\d+ {message}"):
        read(planted(tmp_path, lines))


@pytest.mark.parametrize("line", PROSE.values(), ids=PROSE.keys())
def test_a_paragraph_is_read_past_whatever_it_opens_with(
    tmp_path: Path, line: str
) -> None:
    """A paragraph line is passed over, alone, after a paragraph, or within one.

    :param tmp_path: where the file is written.
    :param line: the paragraph's opening.
    """
    assert read(planted(tmp_path, ["", line])) == [READ]
    assert read(planted(tmp_path, [*PARAGRAPH, line])) == [READ]
    assert read(planted(tmp_path, [*PARAGRAPH[:2], line])) == [READ]


def test_a_line_at_the_margin_right_after_a_bullet_is_refused(
    tmp_path: Path,
) -> None:
    """Markdown reads it as part of the bullet, so it is not prose to skip.

    The same line after a blank line is a paragraph, and is passed over.

    :param tmp_path: where the file is written.
    """
    line = "a line at the margin."
    with pytest.raises(LookupError, match=r"list\.md:5 continues a bullet unindented"):
        read(planted(tmp_path, [line]))
    assert read(planted(tmp_path, ["", line])) == [READ]


def test_section_14_names_each_verbatim_file_by_a_bullet() -> None:
    """Section 14's list of verbatim files is one `bulleted` reads whole.

    `verbatim` raises where a line of the list is an item `bulleted`
    cannot read, so this fails on the change that writes one.
    """
    assert verbatim()


def test_an_item_nested_in_section_14_is_refused(tmp_path: Path) -> None:
    """An ordered item nested under a real bullet raises, and is not dropped.

    :param tmp_path: where the copy of `README.md` is written.
    """
    lines = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
    yamllint = "- `.yamllint.yaml`"
    (at,) = [i for i, line in enumerate(lines) if line.startswith(yamllint)]
    lines.insert(at, f"    1. {ITEM}")
    document = tmp_path / "README.md"
    document.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(LookupError, match=r"README\.md:\d+ opens an item"):
        verbatim(document)


def test_a_block_quote_in_section_14_is_refused(tmp_path: Path) -> None:
    """A real bullet put in a block quote raises, and is not dropped.

    :param tmp_path: where the copy of `README.md` is written.
    """
    lines = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
    markdownlint = "- `.markdownlint.jsonc`"
    (at,) = [i for i, line in enumerate(lines) if line.startswith(markdownlint)]
    lines[at] = f"> {lines[at]}"
    document = tmp_path / "README.md"
    document.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(LookupError, match=r"README\.md:\d+ opens a block quote"):
        verbatim(document)
