# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 12: no published package keeps a deprecation window.

What is refused here is a name a window is written with:
`FutureWarning`, `deprecated`, and any name ending in
`DeprecationWarning`. The module's syntax tree is parsed rather than
grepped, so a comment or a message that mentions the words is not read
as code.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING, Any

import pytest

from . import Tier, by_hand, tracked
from .surface_test import package

if TYPE_CHECKING:
    from pathlib import Path

WINDOW = frozenset({"FutureWarning", "deprecated"})
"""The names a deprecation window is written with, beside `SUFFIX`."""

SUFFIX = "DeprecationWarning"
"""The ending of `DeprecationWarning`, `PendingDeprecationWarning` and a
project's own categories.
"""


def keeps_a_window(name: str) -> bool:
    """Say whether a name is one a deprecation window is written with.

    :param name: a name the module's code holds.
    :returns: whether it is in `WINDOW` or ends in `SUFFIX`.
    """
    return name in WINDOW or name.endswith(SUFFIX)


def window(source: str) -> list[str]:
    """List the names `keeps_a_window` refuses that a module's code holds.

    A name is read as a name, an attribute, an imported name, a class or
    a function; the name an import binds with `as` is not read.

    :param source: the module's text.
    :returns: each name, in the order the tree is walked.
    """
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name):
            found.append(node.id)
        elif isinstance(node, ast.Attribute):
            found.append(node.attr)
        elif isinstance(
            node, ast.alias | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
        ):
            found.append(node.name)
    return [name for name in found if keeps_a_window(name)]


def test_window_reads_code_and_not_prose() -> None:
    """A use is found in code, and the same words in prose are not."""
    source = (
        "from warnings import deprecated\n"
        "import warnings\n"
        "# a DeprecationWarning in a comment\n"
        "MESSAGE = 'deprecated'\n"
        "warnings.warn('gone', DeprecationWarning)\n"
        "warnings.warn('going', warnings.PendingDeprecationWarning)\n"
        "warnings.warn('changing', FutureWarning)\n"
        "warnings.warn('ours', OwnDeprecationWarning)\n"
        "warnings.warn('kept', UserWarning)\n"
    )
    assert sorted(window(source)) == [
        "DeprecationWarning",
        "FutureWarning",
        "OwnDeprecationWarning",
        "PendingDeprecationWarning",
        "deprecated",
    ]


def test_window_reads_a_definition_on_its_own() -> None:
    """A definition is found where the module never uses the name."""
    source = (
        "class OwnDeprecationWarning(UserWarning): ...\n"
        "def deprecated(f): return f\n"
        "async def FutureWarning(): ...\n"
        "class Kept(UserWarning): ...\n"
    )
    assert sorted(window(source)) == [
        "FutureWarning",
        "OwnDeprecationWarning",
        "deprecated",
    ]


@pytest.mark.tier(Tier.PUBLISHER)
def test_no_module_keeps_a_deprecation_window(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 12: no module of a published package keeps a window.

    A tree that publishes nothing has no `RELEASE_NOTES.md` to carry the
    break, so the rule and this test are a publisher's.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: each tree's parsed `pyproject.toml`.
    """
    root = trees[repository]
    directory = package(repository, trees, pyprojects)
    if directory is None:
        pytest.skip(f"{repository} installs no importable package")
    found = {
        path: names
        for path in tracked(root, f"{directory}/*.py")
        if (names := window((root / path).read_text(encoding="utf-8")))
    }
    candidates = by_hand(
        repository,
        f"git grep -nE 'DeprecationWarning|FutureWarning"
        f"|deprecated' -- '{directory}/*.py'",
    )
    assert not found, (
        f"modules keeping a deprecation window: {found}; the grep lists"
        f" candidates, comments and docstrings included, {candidates}"
    )
