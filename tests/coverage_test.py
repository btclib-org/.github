# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 8's clause on a statement only some invocations execute.

Such a statement is covered on the invocations that execute it and
reads as a miss on the others, so under a floor with no slack the
runner's flags decide whether the gate passes. The section answers with
a test of the statement rather than a pragma over it, and this asks the
trees for that test.

What a suite holds of that class is a hook pytest calls under one set of
flags and not another. `pytest_report_header` is one: pytest calls it to
write the header block, and a run under `-q` or under `--no-header`
writes no such block and makes no such call. A hook pytest calls
whatever the flags -- `pytest_configure`, `pytest_generate_tests` -- is
outside the class, and a check keyed on a conftest hook no test module
names would report those too, in trees where nothing is wrong.

Asked of a tree that declares a coverage floor rather than of a tier:
section 8 reads which gate applies off what the tree installs, and where
no total is gated on, no flag turns a hook into a red build.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING, Any

import pytest

from . import by_hand

if TYPE_CHECKING:
    from pathlib import Path

TESTS = "tests"
"""Section 2's directory for a tree's suite."""

CONFTEST = "conftest.py"
"""pytest's own file, which section 7 puts under `tests/`."""

BY_FLAG = ("pytest_report_header",)
"""The hooks whose invocation the runner's flags decide.

A name belongs here where pytest's call to the hook is behind a flag
rather than in the protocol every run follows. The class is the property
section 8 names, so a hook pytest gives that shape next enters by being
written here.
"""

BY_HAND = f"git grep -nE '{'|'.join(BY_FLAG)}' -- '{TESTS}'"
"""How the same question is decided in a checkout.

The conftest's definition and every test module naming it come back
together, so a single line naming the conftest is the finding.
"""

HOOK = BY_FLAG[0]
"""A hook of the class, for the plantings below."""

WHATEVER_THE_FLAGS = "pytest_configure"
"""A hook pytest calls on every invocation, which the class leaves out."""

SILENT = "from . import nothing"
"""A planted test module that names no hook."""


def defined(conftest: Path) -> set[str]:
    """Return the names of the functions a file defines.

    The source is parsed rather than the module imported: nothing
    installs the trees this suite clones, so a conftest importing the
    package it configures could not be imported to be asked.

    :param conftest: the file to read.
    :returns: every function name it defines, nested ones included.
    """
    tree = ast.parse(conftest.read_text(encoding="utf-8"), filename=str(conftest))
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    }


def stranded(root: Path) -> list[str]:
    """Return the hooks of the class a tree leaves to the runner's flags.

    Every `conftest.py` under `tests/` is read, a per-directory one being
    as much pytest's file as the suite's own, and a hook is exercised
    where a test module names it -- which is what a test of the statement
    does, whether it calls the hook or reads a run's output for it.

    :param root: the root of the checkout.
    :returns: the hooks it defines and no test module names, in the order
        `BY_FLAG` gives them.
    """
    tests = root / TESTS
    hooks = {name for path in sorted(tests.rglob(CONFTEST)) for name in defined(path)}
    modules = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(tests.rglob("*_test.py"))
    )
    return [hook for hook in BY_FLAG if hook in hooks and hook not in modules]


def floor(config: dict[str, Any]) -> float | None:
    """Return the coverage floor a parsed `pyproject.toml` declares.

    :param config: the parsed file, empty where the tree keeps none.
    :returns: what `fail_under` is set to, or None where nothing is.
    """
    report = config.get("tool", {}).get("coverage", {}).get("report", {})
    total: float | None = report.get("fail_under")
    return total


@pytest.mark.integration
def test_a_hook_the_flags_can_strand_carries_a_test_of_its_own(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 8: the statement is exercised where a floor makes it red.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: each tree's parsed `pyproject.toml`.
    """
    total = floor(pyprojects.get(repository, {}))
    if total is None:
        pytest.skip(f"{repository} declares no coverage floor")
    left = stranded(trees[repository])
    assert not left, (
        f"{TESTS}/{CONFTEST} defines {left}, which pytest calls on some"
        f" invocations and not others, and no test module names it: under"
        f" fail_under = {total} the flags decide whether the gate passes; "
        + by_hand(repository, BY_HAND)
    )


def plant(root: Path, hook: str, module: str) -> None:
    """Build a tree whose suite defines a hook and holds one test module.

    :param root: where to build it.
    :param hook: the hook the conftest defines.
    :param module: the test module's source.
    """
    tests = root / TESTS
    tests.mkdir(parents=True)
    body = f"def {hook}() -> str:\n    return ''\n"
    (tests / CONFTEST).write_text(body, encoding="utf-8")
    (tests / "planted_test.py").write_text(f"{module}\n", encoding="utf-8")


@pytest.mark.parametrize(
    ("hook", "module", "expected"),
    [
        pytest.param(HOOK, SILENT, [HOOK], id="stranded"),
        pytest.param(HOOK, f"from .conftest import {HOOK}", [], id="tested"),
        pytest.param(WHATEVER_THE_FLAGS, SILENT, [], id="unconditional"),
    ],
)
def test_a_planted_tree_reddens_only_where_the_flags_can_strand_a_hook(
    tmp_path: Path,
    hook: str,
    module: str,
    expected: list[str],
) -> None:
    """Each state a tree can be in against the clause, and the finding.

    A hook of the class no test module names is the finding; the same
    hook named by one is what says the reading cannot report every tree
    that defines a hook; and a hook pytest calls whatever the flags is
    outside the class, which is what keeps this off the trees the
    section has nothing to say about.

    :param tmp_path: where the tree is built.
    :param hook: the hook the planted conftest defines.
    :param module: the planted test module's source.
    :param expected: what `stranded` owes for that tree.
    """
    plant(tmp_path, hook, module)
    assert stranded(tmp_path) == expected
