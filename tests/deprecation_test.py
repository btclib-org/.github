# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 12: no published package keeps a deprecation window.

What is refused here is an identifier a window is written with:
`FutureWarning`, `deprecated`, and any name ending in
`DeprecationWarning`. The module's syntax tree is parsed rather than
grepped, so a comment, a string literal or a docstring that mentions
the words is not read as code.
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

NOT_IDENTIFIERS = frozenset(
    {
        ("Constant", "kind"),
        ("Constant", "value"),
        ("Interpolation", "str"),
        ("TypeIgnore", "tag"),
    }
)
"""The string fields that hold text rather than an identifier.

A literal or a docstring is a `Constant`'s value, and its `u` prefix is
its kind. A template string keeps each interpolation's source text, and
a `# type: ignore` comment keeps its tag. `window` parses without
`type_comments=True`, so `TypeIgnore.tag` and `TYPE_COMMENT` are never
filled there: they are listed for `test_only_identifier_fields_are_read`.
"""

TYPE_COMMENT = "type_comment"
"""The field a node keeps its `# type:` comment in."""

NEVER_STR = frozenset({("MatchSingleton", "value")})
"""The `object` fields that never hold a string.

A `MatchSingleton` holds `True`, `False` or `None`.
"""


def keeps_a_window(name: str) -> bool:
    """Say whether a name is one a deprecation window is written with.

    :param name: a name the module's code holds.
    :returns: whether it is in `WINDOW` or ends in `SUFFIX`.
    """
    return name in WINDOW or name.endswith(SUFFIX)


def identifiers(source: str) -> list[str]:
    """List every identifier a module's code holds.

    Every string field of every node is read, and every string in a list
    field, except the fields `NOT_IDENTIFIERS` and `TYPE_COMMENT` name.
    A dotted import counts once per part.

    :param source: the module's text.
    :returns: each identifier, in the order the tree is walked.
    """
    found = []
    for node in ast.walk(ast.parse(source)):
        kind = type(node).__name__
        for field, value in ast.iter_fields(node):
            if field == TYPE_COMMENT or (kind, field) in NOT_IDENTIFIERS:
                continue
            for item in value if isinstance(value, list) else [value]:
                if isinstance(item, str):
                    found.extend(item.split("."))
    return found


def window(source: str) -> list[str]:
    """List the identifiers `keeps_a_window` refuses in a module's code.

    :param source: the module's text.
    :returns: each identifier, in the order the tree is walked.
    """
    return [name for name in identifiers(source) if keeps_a_window(name)]


def test_only_identifier_fields_are_read() -> None:
    """The fields `identifiers` reads are this `ast`'s identifier fields.

    Every field annotated with `str` or `object` is asked, so one that a
    later Python adds fails here until it is listed as an identifier or
    left out.
    """
    read = {
        (kind.__name__, field)
        for kind in vars(ast).values()
        if isinstance(kind, type) and issubclass(kind, ast.AST)
        for field, annotation in getattr(kind, "_field_types", {}).items()
        if ("str" in repr(annotation) or annotation is object)
        and field != TYPE_COMMENT
        and (kind.__name__, field) not in NOT_IDENTIFIERS | NEVER_STR
    }
    assert read == {
        ("AsyncFunctionDef", "name"),
        ("Attribute", "attr"),
        ("ClassDef", "name"),
        ("ExceptHandler", "name"),
        ("FunctionDef", "name"),
        ("Global", "names"),
        ("ImportFrom", "module"),
        ("MatchAs", "name"),
        ("MatchClass", "kwd_attrs"),
        ("MatchMapping", "rest"),
        ("MatchStar", "name"),
        ("Name", "id"),
        ("Nonlocal", "names"),
        ("ParamSpec", "name"),
        ("TypeVar", "name"),
        ("TypeVarTuple", "name"),
        ("alias", "asname"),
        ("alias", "name"),
        ("arg", "arg"),
        ("keyword", "arg"),
    }


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


@pytest.mark.parametrize(
    "source",
    [
        "def f(*, deprecated=None): ...\n",
        "p.add_argument('--old', deprecated=True)\n",
        "import foo as deprecated\n",
        "import deprecated.sphinx\n",
        "from deprecated import sphinx\n",
        "try: ...\nexcept E as deprecated: ...\n",
        "match x:\n    case deprecated: ...\n",
        "global deprecated\n",
        "def g():\n    deprecated = 1\n    def h():\n        nonlocal deprecated\n",
        "match x:\n    case C(deprecated=1): ...\n",
        "match x:\n    case {**deprecated}: ...\n",
        "match x:\n    case [*deprecated]: ...\n",
        "def f[deprecated](): ...\n",
        "def f[**deprecated](): ...\n",
        "def f[*deprecated](): ...\n",
    ],
    ids=[
        "parameter",
        "keyword",
        "asname",
        "dotted",
        "module",
        "except",
        "match",
        "global",
        "nonlocal",
        "match keyword",
        "match rest",
        "match star",
        "type variable",
        "parameter specification",
        "variadic type variable",
    ],
)
def test_window_reads_any_identifier(source: str) -> None:
    """`deprecated` is found as each kind of identifier.

    A `nonlocal` needs a binding in an enclosing function, which is a
    second identifier, so what is asked is the set of names found.

    :param source: a module holding it as one kind of identifier.
    """
    assert set(window(source)) == {"deprecated"}


@pytest.mark.parametrize(
    "source",
    [
        "MESSAGE = 'deprecated'\n",
        '"""The deprecated API is gone."""\n',
        'def f():\n    """Return what is deprecated."""\n',
        "x = t'{y!r} deprecated'\n",
        "x = t'{\"a.deprecated.b\"}'\n",
    ],
    ids=["string", "module docstring", "docstring", "template", "interpolation"],
)
def test_window_reads_no_text(source: str) -> None:
    """`deprecated` in a literal, a docstring or a template is not read.

    :param source: a module holding the word as text only.
    """
    assert window(source) == []


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
