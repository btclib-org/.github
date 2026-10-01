# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 2's second location for the `python` intersphinx inventory.

The documentation build runs `-n -W`, and while `docs.python.org` does
not answer, every standard-library reference warns and the build fails.
Section 2 has the `python` mapping name a copy kept in the tree as well,
which sphinx reads only where the URL fails. This asks every tree whose
`docs/source/conf.py` maps `python` for that entry, and for the copy to
be tracked: an entry naming a file git does not carry passes on a
checkout and fails on a runner during an outage.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

import pytest

from . import by_hand, output, tracked

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

# Where section 2 puts a tree's sphinx configuration.
CONF = "docs/source/conf.py"

# The copy, as a path from the root; `conf.py` names it from its own directory.
INVENTORY = "docs/source/_inventories/python.inv"

# What the `python` key maps to, as section 2 writes it.
ENTRY = ("https://docs.python.org/3", (None, "_inventories/python.inv"))

# How the same question is decided in a checkout.
BY_HAND = f"grep -n '\"python\"' {CONF}; git ls-files {INVENTORY}"


def python_entry(source: str) -> object | None:
    """Read what a `conf.py` maps `python` to.

    The source is parsed and not executed: the trees are not installed,
    and a `conf.py` imports the package it documents.

    :param source: the text of `conf.py`.
    :returns: the entry, evaluated as a literal, or None where the file
        has no `intersphinx_mapping` dict literal with a `python` key.
    """
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names = [node.target.id]
        else:
            continue
        if "intersphinx_mapping" not in names or not isinstance(node.value, ast.Dict):
            continue
        for key, value in zip(node.value.keys, node.value.values, strict=True):
            if isinstance(key, ast.Constant) and key.value == "python":
                found: object = ast.literal_eval(value)
                return found
    return None


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param(
            f"intersphinx_mapping = {{'python': {ENTRY!r}}}\n", ENTRY, id="entry"
        ),
        pytest.param(
            "intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}\n",
            ("https://docs.python.org/3", None),
            id="no-fallback",
        ),
        pytest.param(
            "intersphinx_mapping = {'btclib': ('https://x/', None)}\n",
            None,
            id="no-python",
        ),
        pytest.param(
            "intersphinx_mapping: dict = {'python': ('https://x/', None)}\n",
            ("https://x/", None),
            id="annotated",
        ),
        pytest.param("extensions = []\n", None, id="no-mapping"),
    ],
)
def test_a_conf_py_is_read_for_its_python_entry(
    source: str, expected: object | None
) -> None:
    """Each state a `conf.py` can be in, and what is read from it.

    :param source: the planted file's text.
    :param expected: what `python_entry` owes for it.
    """
    assert python_entry(source) == expected


def test_a_tracked_inventory_is_asked_of_git(tmp_path: Path) -> None:
    """`tracked` answers nothing for a file an untracked directory holds.

    The control for the assertion below: a file present on disk and not
    in the index is what the check has to refuse.

    :param tmp_path: where the repository is built.
    """
    output("git", "-C", str(tmp_path), "init", "--quiet")
    (tmp_path / "docs" / "source" / "_inventories").mkdir(parents=True)
    (tmp_path / INVENTORY).write_bytes(b"x")
    assert tracked(tmp_path, INVENTORY) == []
    output("git", "-C", str(tmp_path), "add", INVENTORY)
    assert tracked(tmp_path, INVENTORY) == [INVENTORY]


def test_the_python_mapping_has_a_copy_kept_in_the_tree(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 2: `python` maps to the URL and to the tracked copy.

    A tree with no tracked `docs/source/conf.py`, or one that maps no
    `python`, owes nothing here and is skipped.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    if not tracked(root, CONF):
        pytest.skip(f"{repository} tracks no {CONF}")
    entry = python_entry((root / CONF).read_text(encoding="utf-8"))
    if entry is None:
        pytest.skip(f"{repository}'s {CONF} maps no python")
    assert entry == ENTRY, (
        f"{CONF} maps python to {entry!r}, expected {ENTRY!r}; "
        + by_hand(repository, BY_HAND)
    )
    assert tracked(root, INVENTORY), (
        f"{CONF} names {INVENTORY}, which git does not track; "
        + by_hand(repository, BY_HAND)
    )
