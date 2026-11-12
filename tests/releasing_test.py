# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 14's `python=` line of `RELEASING.md`, held against the source.

Section 14 has every copy carry the line of the source's names block
that sets `python`, which reads `.python-version` rather than repeating
its value. The line sits under `MARKER`, where `verbatim_test.py` stops
comparing, so that test does not reach it: section 14's *A part is held
against this file* is the shape asked here. The line is read off the
source, never written here, so this file holds no second copy of it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import ROOT
from .verbatim_test import MARKER, RELEASING, owed, verbatim, verbatim_source

if TYPE_CHECKING:
    from pathlib import Path

# How the names block's line setting `python` opens.
PYTHON = b"python="


def python_lines(body: bytes) -> list[bytes]:
    """Read the lines under a copy's `MARKER` that open by assigning `python`.

    All of them and not the first: a second line setting it overrides
    the first when the block runs. A line is read without its indent and
    without an `export`, since a block inside a list step is indented and
    an `export` sets the name all the same. A line that sets it any other
    way, as `readonly python=…` or `repo=x python=…`, is not read.

    :param body: the bytes of a `RELEASING.md`.
    :returns: each line under the marker that opens with `PYTHON` once
        its indent and an `export` are stripped, as stripped, in file
        order; none where the copy carries no marker.
    """
    cut = body.find(MARKER)
    if cut < 0:
        return []
    own = body[cut + len(MARKER) :].splitlines()
    bare = (line.lstrip().removeprefix(b"export ").lstrip() for line in own)
    return [line for line in bare if line.startswith(PYTHON)]


def source_line() -> bytes:
    """Read the source's line setting `python`.

    :returns: the one line the source's own half sets `python` with.
    :raises LookupError: where that half sets it on no line or on several.
    """
    found = python_lines((ROOT / verbatim_source()).read_bytes())
    if len(found) != 1:
        msg = f"the source sets python on {len(found)} lines under its marker"
        raise LookupError(msg)
    return found[0]


def test_the_source_reads_python_from_python_version() -> None:
    """The source's line reads the file, and does not write a value."""
    line = source_line()
    assert line.startswith(PYTHON + b"$(")
    assert line.endswith(b" .python-version)")


def test_a_copy_writing_the_value_out_is_not_the_source_s_line() -> None:
    """A planted copy carries the line; a literal or a second line does not.

    A second line counts indented, as in a list step's block, or
    exported. Each copy has a tree's own lines around the block, as a
    copy does. A copy with the line and no `MARKER` sets nothing under it.
    """
    line = source_line()
    above = b"# Release process\n\nSteps.\n"
    good = above + MARKER + b"\n```shell\nrepo=x\n" + line + b"\nsmoke=y\n```\n"
    assert python_lines(good) == [line]
    literal = good.replace(line, PYTHON + b"3.15")
    assert python_lines(literal) != [line]
    twice = good.replace(line, line + b"\n" + PYTHON + b"3.15")
    assert python_lines(twice) != [line]
    exported = good.replace(line, line + b"\nexport " + PYTHON + b"3.15")
    assert python_lines(exported) == [line, PYTHON + b"3.15"]
    indented = good.replace(line, line + b"\n\n  ```shell\n  " + PYTHON + b"3.15")
    assert python_lines(indented) == [line, PYTHON + b"3.15"]
    assert not python_lines(above + b"\n" + line + b"\n")


def test_a_releasing_md_reads_python_as_the_source_does(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """A copy section 14 owes sets `python` with the source's line.

    It opens no other line by assigning `python`, as `python_lines` reads
    one.

    A tree section 14 owes no copy is skipped.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    if not owed(root, RELEASING, verbatim()[RELEASING]):
        pytest.skip(f"section 14 owes {repository} no {RELEASING}")
    path = root / RELEASING
    found = python_lines(path.read_bytes()) if path.is_file() else []
    line = source_line()
    assert found == [line], (
        f"{RELEASING} sets python under its own heading with {found!r}, and"
        f" section 14 asks for the source's line: {line!r}"
    )
