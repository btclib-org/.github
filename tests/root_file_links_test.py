# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 14's verbatim part of `docs/source/conf.py`, `RootFileLinks`.

`SOURCE` holds the part below the line `START`. Every tree that tracks
`CONF` carries it byte for byte. It is a part of a file and not a file,
so `verbatim_test.py`, which compares copies by path, does not reach it:
section 14's *A part is held against this file* is the shape asked here.

The part reads a page's include fences as `check_included_links.py`
does, since that script refuses what the part leaves at `BLOB`: the two
fence readers are the same code, and are run on the script's own cases.
"""

from __future__ import annotations

import ast
import re
from typing import TYPE_CHECKING

import pytest

from . import ROOT, tracked
from .check_included_links_test import FENCES

if TYPE_CHECKING:
    from pathlib import Path

# Where this repository keeps the part, below the names a tree sets itself.
SOURCE = "shared/root_file_links.py"

# Where section 2 puts a tree's sphinx configuration.
CONF = "docs/source/conf.py"

# The line of `SOURCE` that the part follows, and that no copy carries.
START = b"# section 14's verbatim part of docs/source/conf.py starts below this line\n"

# How every tree's `setup` registers the transform today.
REGISTERED = b"app.add_post_transform(RootFileLinks)"

# The docs check whose fence reading the part shares.
SCRIPT = ".github/scripts/check_included_links.py"

# The names, top level in both files, that read a page's include fences.
READER = ("FENCE", "INCLUDE", "DIRECTIVE", "PARSED", "includes")


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


def reader(path: Path) -> dict[str, ast.stmt]:
    """Read the statements of a file that define `READER`, in file order.

    :param path: the file.
    :returns: each name of `READER` the file defines at top level,
        against the statement that defines it.
    """
    out: dict[str, ast.stmt] = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.FunctionDef):
            name = node.name
        elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
        else:
            continue
        if name in READER:
            out[name] = node
    return out


def test_the_part_reads_fences_with_the_script_s_code() -> None:
    """Both files define every name of `READER`, and define it alike.

    Compared as syntax trees, so a comment may differ and code may not.
    """
    ours, theirs = reader(ROOT / SOURCE), reader(ROOT / SCRIPT)
    assert tuple(ours) == READER
    assert [ast.dump(node) for node in ours.values()] == [
        ast.dump(node) for node in theirs.values()
    ]


@pytest.mark.parametrize(("page", "paths"), FENCES)
def test_the_part_finds_the_includes_the_script_finds(
    page: str, paths: list[str]
) -> None:
    """The part's own `includes`, run on each of the script's cases.

    :param page: the text of the page.
    :param paths: what the script reads as its include fences.
    """
    module = ast.Module(body=list(reader(ROOT / SOURCE).values()), type_ignores=[])
    namespace: dict[str, object] = {"re": re}
    # the part's own statements, not input: the part imports sphinx, which
    # this suite does not install, so it is not imported whole
    exec(compile(module, SOURCE, "exec"), namespace)  # noqa: S102
    includes = namespace["includes"]
    assert callable(includes)
    assert includes(page) == paths


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
    """A tree's `conf.py` holds the part byte for byte, and registers it.

    A tree that tracks no `conf.py` owes nothing here and is skipped.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    if not tracked(root, CONF):
        pytest.skip(f"{repository} tracks no {CONF}")
    conf = (root / CONF).read_bytes()
    assert part((ROOT / SOURCE).read_bytes()) in conf, (
        f"{CONF} does not carry, byte for byte, the part of btclib-org/.github's"
        f" {SOURCE} below its line {START.decode().strip()!r}"
    )
    assert REGISTERED in conf, f"{CONF} carries the part and no {REGISTERED.decode()}"
