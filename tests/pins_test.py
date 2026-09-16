# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for `workflows_test.py`'s pin reader, on workflows built here.

That module asks section 10 of every repository, and a clean run over
the organization is what cannot show that the reader tells the cases
apart: every tree keeps the rule, so the passes read the same whether
the reading is the narrow one or admits anything written above a pin.
These build the inputs the two disagree about instead -- a tag above a
pin with room on the line for a trailing comment, prose above a pin
without it, a `uses:` a comment or a `run:` block holds -- and the
column the width turns on, where one character decides.

Nothing here reaches GitHub, so no `integration` marker; the switch
`conftest.py` reads skips these with the rest of the suite all the same.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from . import workflows_test
from .workflows_test import above_instead, budget, pinned

if TYPE_CHECKING:
    from pathlib import Path

SHA = "0" * 40
"""Forty hex digits, which is the whole of what a pin's commit has to be."""

STEP = "      - uses: "
"""What a step's `uses:` line spends before the action's name."""

BESIDE = " # v1"
"""A trailing tag comment, whose width is what a pin needs room for."""

ELSEWHERE = 73
"""A width no configuration of this organization sets.

What `budget` reads has to be the file's rather than a default it could
return, and a number this tree also holds would pass either way.
"""

WIDTH = 70
"""The width these fragments are measured against.

Not the number `.yamllint.yaml` holds: `above_instead` takes the width
as an argument and `budget` is what reads a tree's own, so a fragment
picks whatever keeps its lines readable. What is under test is the
column the answer turns on, not which column the organization chose.
"""


def workflow(root: Path, *steps: str) -> Path:
    """Write a one-job workflow whose steps are these lines, and return it.

    The document has to parse, `pinned` counting what the text gives
    against what the parser returns, so the job around the lines is
    whatever makes that true and no test here reads it.

    :param root: the directory to write into.
    :param steps: the lines under `steps:`, each indented as written.
    :returns: the file.
    """
    body = "\n".join(steps)
    path = root / "fragment.yml"
    path.write_text(
        "---\non: push\npermissions: {}\njobs:\n  j:\n"
        f"    runs-on: ubuntu-latest\n    timeout-minutes: 1\n    steps:\n{body}\n",
        encoding="utf-8",
    )
    return path


def pin_at(width: int) -> str:
    """Return a `uses:` line of exactly this many columns.

    The action's name is what varies, the indent, the keyword, the `@`
    and the digits being fixed, so a caller names the column its case
    turns on rather than counting a name out by hand.

    :param width: the columns the line is to take.
    :returns: the line.
    """
    name = "a" * (width - len(STEP) - len(SHA) - 1)
    return f"{STEP}{name}@{SHA}"


def test_a_pin_is_read_with_the_tag_trailing_it(tmp_path: Path) -> None:
    """A pin written as section 10 asks, which is the positive control.

    Every rejection below refuses something this accepts, so a reader
    that had stopped reading anything would pass them all and fail here.

    :param tmp_path: the directory the fragment is written in.
    """
    (pin,) = pinned(workflow(tmp_path, f"{pin_at(WIDTH)}{BESIDE}"))
    assert pin.trailing == "v1"
    assert pin.above is None
    assert pin.width == WIDTH + len(BESIDE)


def test_a_commented_out_uses_is_no_pin(tmp_path: Path) -> None:
    """A `#` before the key, which `PIN_LINE`'s anchor does not admit.

    A grep for the substring reports this line, and that difference is
    the reason the reader anchors rather than searching.

    :param tmp_path: the directory the fragment is written in.
    """
    lines = (f"      # uses: a/b@{SHA}", "      - run: true")
    assert pinned(workflow(tmp_path, *lines)) == []


def test_a_uses_line_inside_a_run_block_is_refused(tmp_path: Path) -> None:
    """A line the text reads as a pin and the document does not.

    A block scalar keeps its own indentation, so a line inside one can
    open with the keyword and reach the anchor. Counting the text's pins
    against the document's is what makes that an error here rather than
    a finding against the tree that wrote it.

    :param tmp_path: the directory the fragment is written in.
    """
    with pytest.raises(LookupError, match="the text alone"):
        pinned(workflow(tmp_path, "      - run: |", f"          uses: a/b@{SHA}"))


def test_a_pattern_that_reaches_no_pin_is_refused(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A reader that stops matching errors rather than classifying nothing.

    This is what `test_every_pin_names_its_tag_in_a_comment` leans on: a
    run reading no pin finds no pin lacking a tag, and would report a
    tree as keeping a rule nothing had asked it.

    :param tmp_path: the directory the fragment is written in.
    :param monkeypatch: what replaces the pattern for this test.
    """
    path = workflow(tmp_path, f"{pin_at(WIDTH)}{BESIDE}")
    monkeypatch.setattr(workflows_test, "PIN_LINE", re.compile("^$"))
    with pytest.raises(LookupError, match="the document alone"):
        pinned(path)


@pytest.mark.parametrize(
    ("width", "wanted"),
    [
        pytest.param(WIDTH - len(BESIDE), False, id="room-for-the-comment"),
        pytest.param(WIDTH - len(BESIDE) + 1, True, id="one-column-past"),
    ],
)
def test_the_tag_goes_above_only_where_the_line_has_no_room(
    tmp_path: Path,
    width: int,
    *,
    wanted: bool,
) -> None:
    """One column decides, which is the whole of section 10's exception.

    The two fragments differ in the length of the action's name and in
    nothing else, the comment above being the same text either way, so a
    reading that excused a tag above wherever one was written would
    answer both alike.

    :param tmp_path: the directory the fragment is written in.
    :param width: the columns the pin's line takes.
    :param wanted: where section 10 puts the tag at that width.
    """
    (pin,) = pinned(workflow(tmp_path, "      # v1", pin_at(width)))
    assert pin.trailing is None
    assert pin.above == "v1"
    assert above_instead(pin, WIDTH) is wanted


def test_prose_above_a_pin_is_no_tag(tmp_path: Path) -> None:
    """A comment of several words is not the tag, whatever the width.

    The pin is one the width does excuse, so the comment is the whole of
    what this isolates: `TAG` reads one word, and prose leaves the tag
    above unread.

    :param tmp_path: the directory the fragment is written in.
    """
    (pin,) = pinned(
        workflow(tmp_path, "      # the action that builds them", pin_at(WIDTH))
    )
    assert pin.above is None
    assert above_instead(pin, WIDTH) is False


def test_budget_reads_the_width_a_tree_sets(tmp_path: Path) -> None:
    """The width comes off `.yamllint.yaml`, not from a number written here.

    :param tmp_path: the tree the configuration is written in.
    """
    (tmp_path / ".yamllint.yaml").write_text(
        f"---\nextends: default\nrules:\n  line-length:\n    max: {ELSEWHERE}\n",
        encoding="utf-8",
    )
    assert budget(tmp_path) == ELSEWHERE
