# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 7's rule on a test that bounds time.

An assertion comparing a clock difference with a literal number of
seconds is the finding: the same code runs many times slower on one
runner than on another. A duration bounded by a reference measured in
the same process, or by a timeout named in the code, passes.

The trees' test files are parsed rather than imported, nothing
installing the trees this suite clones. A duration is a clock reading
minus another value, a name assigned one, a function returning one, or
the `min` or `max` of one; a division makes it a ratio.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

import pytest

from . import by_hand, tracked

if TYPE_CHECKING:
    from pathlib import Path

# the functions of `time` that read a clock
CLOCKS = frozenset(
    clock + suffix
    for clock in ("monotonic", "perf_counter", "process_time", "time")
    for suffix in ("", "_ns")
)

# candidate lines in a checkout, the direct form only; a named bound passes
BY_HAND = r"git grep -nE 'assert .*(monotonic|perf_counter|time)\(\) - ' -- tests"


def _is_clock(node: ast.expr) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr in CLOCKS and isinstance(func.value, ast.Name)
    return isinstance(func, ast.Name) and func.id in CLOCKS


def _is_duration(node: ast.expr, names: set[str]) -> bool:
    if isinstance(node, ast.Await):
        node = node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub):
        return _is_clock(node.left) or _is_clock(node.right)
    if isinstance(node, ast.Name):
        return node.id in names
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id in {"min", "max"}:
            return any(_is_duration(arg, names) for arg in node.args)
        return node.func.id in names
    if isinstance(node, ast.GeneratorExp | ast.ListComp):
        return _is_duration(node.elt, names)
    return False


def _durations(tree: ast.Module) -> set[str]:
    """Return the names, of variables and of functions, holding a duration.

    :param tree: the parsed module.
    :returns: every name assigned or returning a duration, to a fixed point.
    """
    names: set[str] = set()
    while True:
        found = set(names)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and _is_duration(node.value, names):
                found.update(t.id for t in node.targets if isinstance(t, ast.Name))
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and any(
                isinstance(ret, ast.Return)
                and ret.value is not None
                and _is_duration(ret.value, names)
                for ret in ast.walk(node)
            ):
                found.add(node.name)
        if found == names:
            return names
        names = found


def _is_seconds(node: ast.expr) -> bool:
    if isinstance(node, ast.UnaryOp):
        node = node.operand
    return (
        isinstance(node, ast.Constant)
        and type(node.value) in {int, float}
        and node.value != 0
    )


def absolute(source: str) -> list[int]:
    """Return the lines of the assertions bounding a duration by seconds.

    :param source: a Python module's text.
    :returns: the line of each such `assert`, in the order of the file.
    """
    tree = ast.parse(source)
    names = _durations(tree)
    lines = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assert):
            continue
        for compare in ast.walk(node.test):
            if not isinstance(compare, ast.Compare):
                continue
            sides = [compare.left, *compare.comparators]
            if any(_is_duration(side, names) for side in sides) and any(
                _is_seconds(side) for side in sides
            ):
                lines.append(node.lineno)
                break
    return sorted(lines)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("start = monotonic()\nassert monotonic() - start < 10\n", [2]),
        ("s = time.perf_counter()\nd = time.perf_counter() - s\nassert d < 5\n", [3]),
        (
            (
                "def f():\n    s = perf_counter()\n    return perf_counter() - s\n"
                "assert min(f() for _ in range(3)) < 0.5\n"
            ),
            [4],
        ),
        ("t = 10\nassert time.monotonic() - start < t\n", []),
        ("assert time.monotonic() - start >= timeout\n", []),
        ("assert min(f(), g()) / min(h(), k()) < 10\n", []),
        ("assert best(slow) < 12 * best(reference)\n", []),
        ("assert time.monotonic() - start > 0\n", []),
        (
            (
                "async def f():\n    s = loop.time()\n    return loop.time() - s\n"
                "assert await f() < 2\n"
            ),
            [4],
        ),
        ("assert len(x) < 10\n", []),
    ],
)
def test_absolute_finds_a_bound_in_seconds_and_nothing_else(
    source: str, expected: list[int]
) -> None:
    """Seconds against a duration are found; a ratio or a named timeout is not.

    :param source: a planted module.
    :param expected: the lines owed.
    """
    assert absolute(source) == expected


@pytest.mark.integration
def test_a_test_bounds_time_by_a_ratio_or_a_named_timeout(
    repository: str, trees: dict[str, Path]
) -> None:
    """Section 7: no assertion bounds a measured duration by seconds.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    found = [
        f"{path}:{line}"
        for path in tracked(root, "tests/*.py")
        for line in absolute((root / path).read_text(encoding="utf-8"))
    ]
    assert not found, (
        f"{found} bound a duration by seconds, which section 7 refuses: bound"
        " it by a reference timed in the same process, or by the timeout the"
        " code is given, by name; " + by_hand(repository, BY_HAND)
    )
