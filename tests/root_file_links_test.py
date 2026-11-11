# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 14's verbatim part of `docs/source/conf.py`, `RootFileLinks`.

`SOURCE` holds the part below the line `START`. Every tree that tracks
`CONF` carries it byte for byte. It is a part of a file and not a file,
so `verbatim_test.py`, which compares copies by path, does not reach it:
section 14's *A part is held against this file* is the shape asked here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import ROOT, tracked

if TYPE_CHECKING:
    from pathlib import Path

# Where this repository keeps the part, below the names a tree sets itself.
SOURCE = "shared/root_file_links.py"

# Where section 2 puts a tree's sphinx configuration.
CONF = "docs/source/conf.py"

# The line of `SOURCE` that the part follows, and that no copy carries.
START = b"# section 14's verbatim part of docs/source/conf.py starts below this line\n"


def part(source: bytes) -> bytes:
    """Read the part out of the source.

    :param source: the bytes of `SOURCE`.
    :returns: everything after `START`.
    :raises LookupError: where the source holds no `START` line.
    """
    at = source.find(START)
    if at < 0:
        msg = f"{SOURCE} holds no line {START!r}"
        raise LookupError(msg)
    return source[at + len(START) :]


def test_the_part_is_what_follows_its_start_line() -> None:
    """The line itself is out, and a source without it raises."""
    assert part(b"ROOT = 1\n" + START + b"INCLUDE = 2\n") == b"INCLUDE = 2\n"
    with pytest.raises(LookupError, match="holds no line"):
        part(b"INCLUDE = 2\n")


def test_the_source_holds_the_transform() -> None:
    """The part read off `SOURCE` holds the class: the line is above it."""
    assert b"\nclass RootFileLinks(SphinxPostTransform):\n" in part(
        (ROOT / SOURCE).read_bytes()
    )


def test_a_copy_differing_by_a_byte_is_not_the_part() -> None:
    """A planted copy holds the part; with one byte changed, it does not.

    The planted copy has a tree's own lines around the part, as a
    `conf.py` does.
    """
    shared = part((ROOT / SOURCE).read_bytes())
    assert shared in b"ROOT = 1\n\n\n" + shared + b"\n\ndef setup(): ...\n"
    changed = shared.replace(b"default_priority = 5", b"default_priority = 6")
    assert changed != shared
    assert shared not in b"ROOT = 1\n\n\n" + changed


def test_a_conf_py_carries_section_14_s_root_file_links(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """A tree's `conf.py` holds the part byte for byte.

    A tree that tracks no `conf.py` owes nothing here and is skipped.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    if not tracked(root, CONF):
        pytest.skip(f"{repository} tracks no {CONF}")
    assert part((ROOT / SOURCE).read_bytes()) in (root / CONF).read_bytes(), (
        f"{CONF} does not carry, byte for byte, the part of btclib-org/.github's"
        f" {SOURCE} below its line {START.decode().strip()!r}"
    )
