# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 7's layout, read off the tree rather than off the hook.

The hook is section 4's and `hooks_test.py` asks whether it runs; this
asks whether the tree keeps the rule the hook would enforce, which is
the half a gate that is not installed cannot answer for. It also asks
what no hook reads: that a module named for tests defines a test, or is
the test body section 7 admits.

The per-repository tests carry the `integration` marker, which the
controls do not: they build a tree in a temporary directory and reach
nothing.
"""

from __future__ import annotations

import ast
from collections import Counter
from typing import TYPE_CHECKING

import pytest

from . import ORG, Tier, by_hand

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

EXEMPT = ("__init__.py", "conftest.py")
"""The two names `name-tests-test` passes over at any setting.

The package file and pytest's own, neither of which is a test module
and both of which section 7 puts under `tests/`.
"""

DATA = "_data"
"""The directory whose files section 7 counts as data, at any depth."""

SUFFIX = "_test.py"
"""Section 7's spelling of a test module's name."""

NODES = 2
"""The fewest per-node modules that make a test body section 7's exception.

The exception is a test run on several node implementations, one module
per node.
"""


@pytest.mark.integration
@pytest.mark.tier(Tier.PYTHON)
def test_every_test_file_is_named_so_pytest_collects_it(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 7: `*_test.py`, which is what `name-tests-test` enforces.

    Every `.py` under `tests/` but the two exempt names and the data
    under its `_data` directories: a helper module goes in the package
    `__init__.py` by section 7's next bullet, so a module named any
    other way is what the hook refuses -- a test spelled some other way,
    or shared code in the wrong file.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    if not (root / "tests").is_dir():
        pytest.skip(f"{repository} has no tests/ directory")
    wrong = sorted(
        str(path.relative_to(root))
        for path in (root / "tests").rglob("*.py")
        if path.name not in EXEMPT
        and not path.name.endswith(SUFFIX)
        and DATA not in path.relative_to(root / "tests").parts[:-1]
    )
    assert not wrong, f"files under tests/ not named *_test.py: {wrong}; " + by_hand(
        repository,
        "git ls-files 'tests/**.py' | grep -vE '^tests/(.*/)?_data/' "
        "| grep -vE '(_test|/__init__|/conftest)\\.py$'",
    )


BLOCKS: dict[type[ast.stmt], tuple[str, ...]] = {
    ast.If: ("body", "orelse"),
    ast.Try: ("body", "orelse", "finalbody"),
    ast.TryStar: ("body", "orelse", "finalbody"),
    ast.With: ("body",),
}
"""The blocks `module_level` walks into, each with its fields of statements.

A `for`, `while` or `match` body also runs on import, and is not read."""


def module_level(body: list[ast.stmt]) -> Iterator[ast.stmt]:
    """Yield the statements a module runs on import, blocks included.

    The top level, and inside each `if`, `try` and `with` there, the
    handlers of a `try` included; never inside a function or a class.

    :param body: the module's own statements.
    :yields: each statement, outermost first.
    """
    for node in body:
        yield node
        for field in BLOCKS.get(type(node), ()):
            yield from module_level(getattr(node, field))
        if isinstance(node, ast.Try | ast.TryStar):
            for handler in node.handlers:
                yield from module_level(handler.body)


def defines_a_test(module: ast.Module) -> bool:
    """Say whether a module defines a test pytest's defaults collect.

    What is read is each definition the module runs on import, as
    `module_level` walks them: a function whose name starts `test`, a
    class whose name starts `Test`, and a class with a base named
    `TestCase` or ending `.TestCase`, which pytest collects as
    unittest's whatever its name.

    :param module: the parsed module.
    :returns: whether it defines one.
    """
    for node in module_level(module.body):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            if node.name.startswith("test"):
                return True
        elif isinstance(node, ast.ClassDef) and (
            node.name.startswith("Test")
            or any(
                ast.unparse(base).split(".")[-1] == "TestCase" for base in node.bases
            )
        ):
            return True
    return False


def dotted(root: Path, path: Path) -> str:
    """Return the module name a path has from the root of its checkout.

    :param root: the root of the checkout.
    :param path: a `.py` file under it.
    :returns: the dotted name, `tests.integration.x_test` for instance.
    """
    return ".".join(path.relative_to(root).with_suffix("").parts)


SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)
"""The nodes `own_scope` does not descend into: a nested `def`, `async def`,
`lambda` or `class`."""


def own_scope(test: ast.FunctionDef | ast.AsyncFunctionDef) -> Iterator[ast.AST]:
    """Yield the nodes of a test's body that belong to its own scope.

    Every node under the test's statements, down to but not into a
    nested `def`, `async def`, `lambda` or `class`: those are yielded,
    and what they hold is not.

    :param test: the test function.
    :yields: each node, in no particular order.
    """
    stack: list[ast.AST] = list(test.body)
    while stack:
        node = stack.pop()
        yield node
        if not isinstance(node, SCOPES):
            stack.extend(ast.iter_child_nodes(node))


def bound(test: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """Return the names a test binds in its own scope.

    Each `arg` of its signature, and in `own_scope` each name stored or
    deleted, each name an `import` binds, each nested `def` or `class`,
    and each `except ... as` name. A name stored as a comprehension's
    target, or declared `global` or `nonlocal`, is listed too, though
    Python does not make it local to the test.

    :param test: the test function.
    :returns: the names.
    """
    names = {node.arg for node in ast.walk(test.args) if isinstance(node, ast.arg)}
    for node in own_scope(test):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store | ast.Del):
            names.add(node.id)
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            names.add(node.name)
        elif isinstance(node, ast.alias):
            names.add((node.asname or node.name).split(".")[0])
        elif isinstance(node, ast.ExceptHandler) and node.name:
            names.add(node.name)
    return names


def called(root: Path, body: Path, parsed: ast.Module, caller: ast.Module) -> set[str]:
    """Return the functions of the body module a module calls from a test.

    A function is a top-level `def` of the body, imported by a top-level
    `from` statement of the caller in one of two forms: the body's full
    name from the checkout's root (`from tests.integration.x_test import
    f`), or the body's own name relative to its directory (`from .x_test
    import f`). A test, a top-level function whose name starts `test`,
    calls it by the name it was imported as, in its `own_scope`, and
    binds no such name itself (`bound`).

    :param root: the root of the checkout.
    :param body: the body module's path.
    :param parsed: the body module, parsed.
    :param caller: the parsed module that may call it.
    :returns: the names, as the body defines them, of the functions called.
    """
    functions = {
        node.name
        for node in parsed.body
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    }
    stem = body.name.removesuffix(".py")
    imported = {
        alias.asname or alias.name: alias.name
        for node in caller.body
        if isinstance(node, ast.ImportFrom)
        and (
            (node.level == 0 and node.module == dotted(root, body))
            or (node.level == 1 and node.module == stem)
        )
        for alias in node.names
        if alias.name in functions
    }
    out: set[str] = set()
    for test in caller.body:
        if not (
            isinstance(test, ast.FunctionDef | ast.AsyncFunctionDef)
            and test.name.startswith("test")
        ):
            continue
        shadowed = bound(test)
        out.update(
            imported[node.func.id]
            for node in own_scope(test)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in imported
            and node.func.id not in shadowed
        )
    return out


def bodiless(root: Path) -> list[str]:
    """List the test modules that define no test and are no shared body.

    A `*_test.py` under `tests/`, its `_data` directories aside, that
    defines no test is section 7's exception only where it is the body of
    a test run on several node implementations: at least `NODES` modules
    in its own directory, each named `<file>_<node>_test.py` for its own
    `<file>_test.py`, call the same function of it from a test, as
    `called` reads a call. Anything else is shared code in a module whose
    name says "test", which section 7 puts in a package `__init__.py`.

    :param root: the root of the checkout.
    :returns: the offending paths, relative to the root, sorted.
    """
    tests = root / "tests"
    parsed = {
        path: ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for path in tests.rglob(f"*{SUFFIX}")
        if DATA not in path.relative_to(tests).parts[:-1]
    }
    wrong = []
    for path, module in parsed.items():
        if defines_a_test(module):
            continue
        prefix = path.name.removesuffix(SUFFIX) + "_"
        callers = Counter(
            function
            for other, tree in parsed.items()
            if other.parent == path.parent and other.name.startswith(prefix)
            for function in called(root, path, module, tree)
        )
        if max(callers.values(), default=0) < NODES:
            wrong.append(str(path.relative_to(root)))
    return sorted(wrong)


@pytest.mark.integration
@pytest.mark.tier(Tier.PYTHON)
def test_a_test_module_defining_no_test_is_a_body_its_node_modules_call(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 7: no test-named module holds only shared code.

    Its one exception, a test body that per-node modules call, is what
    `bodiless` admits.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    if not (root / "tests").is_dir():
        pytest.skip(f"{repository} has no tests/ directory")
    wrong = bodiless(root)
    assert not wrong, (
        f"modules under tests/ that define no test and that no two "
        f"<file>_<node>_test.py call: {wrong}. The candidates, listed in a "
        f"checkout of {ORG}/{repository}: "
        "for f in $(git ls-files 'tests/**_test.py' "
        "| grep -vE '^tests/(.*/)?_data/'); do "
        'grep -qE \'^(async )?def test|^class Test\' "$f" || echo "$f"; done. '
        "Of those, a module is admitted that defines a test inside an if, try "
        "or with block or subclasses TestCase, and so is a body whose function "
        "two <file>_<node>_test.py of its own directory import by name and call "
        "from a test."
    )


def _write(root: Path, name: str, text: str) -> None:
    """Write a module under `tests/` of a stand-in tree.

    :param root: the stand-in tree.
    :param name: the module's path under `tests/`, `integration/` by
        default.
    :param text: its source.
    """
    path = root / "tests" / (name if "/" in name else f"integration/{name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


STEM = "p2p_block_sync_test"
"""The stand-in body module's name."""

BODY = "def a_block_reaches_every_node(adapter):\n    assert adapter\n"
"""A shared test body: a function without the `test_` prefix."""

CALL = (
    "def test_a_block_reaches_every_node(adapter):\n"
    "    a_block_reaches_every_node(adapter)\n"
)
"""A test calling the body."""

ABSOLUTE = f"from tests.integration.{STEM} import a_block_reaches_every_node\n"
"""The body imported by its full name."""

RELATIVE = f"from .{STEM} import a_block_reaches_every_node\n"
"""The body imported by its name relative to its directory."""

OTHER = "\n\ndef test_other():\n    assert True\n"
"""A test that calls nothing of the body."""

MODULE_IMPORTED = (
    f"from tests.integration import {STEM}\n\n\n"
    "def test_it(adapter):\n"
    f"    {STEM}.a_block_reaches_every_node(adapter)\n"
)
"""A caller importing the body module rather than its function."""

PLAIN_IMPORT = (
    f"import tests.integration.{STEM}\n\n\n"
    "def test_it(adapter):\n"
    f"    tests.integration.{STEM}.a_block_reaches_every_node(adapter)\n"
)
"""A caller importing the body module with a plain `import`."""

NESTED_IMPORT = (
    "def test_a_block_reaches_every_node(adapter):\n"
    f"    {ABSOLUTE.strip()}\n"
    "    a_block_reaches_every_node(adapter)\n"
)
"""A caller importing the function inside its test."""

GUARDED_IMPORT = (
    f"from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    {ABSOLUTE}{CALL}"
)
"""A caller importing the function under `if TYPE_CHECKING:` only."""

NESTED_DEF = (
    ABSOLUTE + "def test_it(adapter):\n"
    "    def unused():\n"
    "        a_block_reaches_every_node(adapter)\n"
)
"""A caller whose call is in a function its test defines and never runs."""

NESTED_LAMBDA = (
    ABSOLUTE + "def test_it(adapter):\n"
    "    unused = lambda: a_block_reaches_every_node(adapter)\n"
)
"""A caller whose call is in a lambda its test never calls."""

NESTED_ASYNC_DEF = (
    ABSOLUTE + "def test_it(adapter):\n"
    "    async def unused():\n"
    "        a_block_reaches_every_node(adapter)\n"
)
"""A caller whose call is in a coroutine function its test never awaits."""

NESTED_CLASS = (
    ABSOLUTE + "def test_it(adapter):\n"
    "    class Unused:\n"
    "        a_block_reaches_every_node(adapter)\n"
)
"""A caller whose call is in the body of a class its test defines."""

SHADOWING_PARAMETER = (
    ABSOLUTE + "def test_it(a_block_reaches_every_node):\n"
    "    a_block_reaches_every_node(None)\n"
)
"""A caller whose test takes a fixture of the body's name, and calls that."""

SHADOWING_ASSIGNMENT = (
    ABSOLUTE + "def test_it(adapter):\n"
    "    a_block_reaches_every_node = print\n"
    "    a_block_reaches_every_node(adapter)\n"
)
"""A caller whose test assigns the body's name before calling it."""

SHADOWS = {
    "keyword-only parameter": "def test_it(*, a_block_reaches_every_node):\n",
    "deletion": "def test_it(adapter):\n    del a_block_reaches_every_node\n",
    "nested def": "def test_it(adapter):\n"
    "    def a_block_reaches_every_node(adapter):\n        pass\n",
    "nested class": "def test_it(adapter):\n"
    "    class a_block_reaches_every_node:\n        pass\n",
    "import": "def test_it(adapter):\n    import os as a_block_reaches_every_node\n",
    "except as": "def test_it(adapter):\n    try:\n        pass\n"
    "    except ImportError as a_block_reaches_every_node:\n        pass\n",
}
"""Each way a test binds the body's name, its call then following."""

REFUSED = [f"tests/integration/{STEM}.py"]
"""What `bodiless` answers on a stand-in tree whose body it refuses."""


def _tree(
    root: Path, *callers: str, body: str = BODY, where: str = "integration"
) -> Path:
    """Build a stand-in tree: the body, and a caller per source.

    :param root: where the tree goes.
    :param callers: the source of each caller, the first named for
        `bitcoind`, the second for `btcd`.
    :param body: the body module's source.
    :param where: the directory under `tests/` the callers go in.
    :returns: the root.
    """
    _write(root, f"{STEM}.py", body)
    for node, source in zip(("bitcoind", "btcd"), callers, strict=False):
        _write(root, f"{where}/p2p_block_sync_{node}_test.py", source)
    return root


def test_a_body_its_node_modules_call_is_admitted(tmp_path: Path) -> None:
    """The layout section 7 admits, with an absolute and a relative import.

    :param tmp_path: where the stand-in tree is built.
    """
    _tree(tmp_path, ABSOLUTE + CALL, RELATIVE + CALL)
    _write(tmp_path, "rpc_net_test.py", "def test_rpc():\n    assert True\n")
    assert bodiless(tmp_path) == []


@pytest.mark.parametrize(
    "callers",
    [
        pytest.param((), id="no caller"),
        pytest.param((ABSOLUTE + CALL,), id="one caller"),
        pytest.param(
            (ABSOLUTE + CALL.replace("def test_", "def check_") + OTHER,) * 2,
            id="callers calling it from no test",
        ),
        pytest.param(
            (
                "def test_it():\n    assert True\n",
                "def test_it():\n    assert True\n",
            ),
            id="callers not importing it",
        ),
        pytest.param((MODULE_IMPORTED,) * 2, id="the module imported"),
        pytest.param((PLAIN_IMPORT,) * 2, id="a plain import"),
        pytest.param((NESTED_IMPORT,) * 2, id="an import inside the test"),
        pytest.param((GUARDED_IMPORT,) * 2, id="an import under TYPE_CHECKING"),
        pytest.param((NESTED_DEF,) * 2, id="a call in a nested def"),
        pytest.param((NESTED_LAMBDA,) * 2, id="a call in a lambda"),
        pytest.param((NESTED_ASYNC_DEF,) * 2, id="a call in a nested async def"),
        pytest.param((NESTED_CLASS,) * 2, id="a call in a nested class body"),
        pytest.param((SHADOWING_PARAMETER,) * 2, id="a parameter of the name"),
        pytest.param((SHADOWING_ASSIGNMENT,) * 2, id="an assignment of the name"),
        pytest.param(
            (f"from tests.other.{STEM} import a_block_reaches_every_node\n{CALL}",) * 2,
            id="a same-named module of another directory, by its full name",
        ),
        pytest.param(
            (f"from ..other.{STEM} import a_block_reaches_every_node\n{CALL}",) * 2,
            id="a same-named module of another directory, relatively",
        ),
    ],
)
def test_a_body_not_called_from_per_node_tests_is_refused(
    tmp_path: Path, callers: tuple[str, ...]
) -> None:
    """The body is refused unless two per-node tests beside it call it.

    Each case moves one condition of `bodiless` or `called` off.

    :param tmp_path: where the stand-in tree is built.
    :param callers: the per-node modules' sources.
    """
    assert bodiless(_tree(tmp_path, *callers)) == REFUSED


def test_per_node_tests_of_another_directory_are_no_callers(tmp_path: Path) -> None:
    """Callers of the right name and form, but in another directory.

    :param tmp_path: where the stand-in tree is built.
    """
    _tree(tmp_path, ABSOLUTE + CALL, ABSOLUTE + CALL, where="other")
    assert bodiless(tmp_path) == REFUSED


@pytest.mark.parametrize("binding", SHADOWS.values(), ids=SHADOWS.keys())
def test_a_call_of_a_name_the_test_binds_is_refused(
    tmp_path: Path, binding: str
) -> None:
    """A test that binds the body's name calls its own, not the body.

    :param tmp_path: where the stand-in tree is built.
    :param binding: the test's opening, up to the call.
    """
    caller = ABSOLUTE + binding + "    a_block_reaches_every_node(None)\n"
    _tree(tmp_path, caller, caller)
    assert bodiless(tmp_path) == REFUSED


def test_a_call_in_a_block_of_the_test_counts(tmp_path: Path) -> None:
    """A call under an `if` or a `with` of the test is in its own scope.

    :param tmp_path: where the stand-in tree is built.
    """
    under_if = (
        ABSOLUTE + "def test_it(adapter):\n"
        "    if adapter:\n"
        "        a_block_reaches_every_node(adapter)\n"
    )
    under_with = (
        ABSOLUTE + "def test_it(adapter):\n"
        "    with adapter:\n"
        "        a_block_reaches_every_node(adapter)\n"
    )
    _tree(tmp_path, under_if, under_with)
    assert bodiless(tmp_path) == []


def test_two_functions_each_called_by_one_node_are_refused(tmp_path: Path) -> None:
    """Each node module calls the body: one function of it, called by both.

    A body module whose one function only the bitcoind module calls,
    and whose other only the btcd module calls, is no shared body.

    :param tmp_path: where the stand-in tree is built.
    """
    body = BODY + "\n\ndef another(adapter):\n    assert adapter\n"
    other = (
        f"from tests.integration.{STEM} import another\n\n\n"
        "def test_it(adapter):\n    another(adapter)\n"
    )
    _tree(tmp_path, ABSOLUTE + CALL, other, body=body)
    assert bodiless(tmp_path) == REFUSED
    _tree(
        tmp_path,
        ABSOLUTE + CALL,
        ABSOLUTE + CALL + other.replace("test_it", "test_too"),
        body=body,
    )
    assert bodiless(tmp_path) == []


def test_a_body_that_is_a_class_is_refused(tmp_path: Path) -> None:
    """Section 7's body is a function: a class its callers use is refused.

    :param tmp_path: where the stand-in tree is built.
    """
    body = (
        "class a_block_reaches_every_node:\n"
        "    def __init__(self, adapter):\n"
        "        self.adapter = adapter\n"
    )
    _tree(tmp_path, ABSOLUTE + CALL, RELATIVE + CALL, body=body)
    assert bodiless(tmp_path) == REFUSED


def test_a_helper_other_tests_import_is_refused(tmp_path: Path) -> None:
    """A helper module named for tests is refused, whoever imports it.

    :param tmp_path: where the stand-in tree is built.
    """
    _write(tmp_path, "p2p_conns_test.py", "def conn():\n    return 1\n")
    for name in ("p2p_fingerprint_test.py", "p2p_sendheaders_test.py"):
        _write(
            tmp_path,
            name,
            "from tests.integration.p2p_conns_test import conn\n\n\n"
            "def test_conn():\n    assert conn()\n",
        )
    assert bodiless(tmp_path) == ["tests/integration/p2p_conns_test.py"]


@pytest.mark.parametrize(
    "source",
    [
        pytest.param("def test_a():\n    assert True\n", id="function"),
        pytest.param("async def test_b():\n    assert True\n", id="async function"),
        pytest.param("class TestC:\n    pass\n", id="Test class"),
        pytest.param(
            "import sys\nif sys:\n    def test_d():\n        assert True\n",
            id="function under an if",
        ),
        pytest.param(
            "import sys\nif not sys:\n    pass\nelse:\n"
            "    def test_d():\n        assert True\n",
            id="function in an else",
        ),
        pytest.param(
            "with open(__file__):\n    def test_w():\n        assert True\n",
            id="function under a with",
        ),
        pytest.param(
            "try:\n    def test_t():\n        assert True\n"
            "except ImportError:\n    pass\n",
            id="function in a try",
        ),
        pytest.param(
            "try:\n    pass\nexcept ImportError:\n    pass\n"
            "else:\n    def test_t():\n        assert True\n",
            id="function in a try's else",
        ),
        pytest.param(
            "try:\n    pass\nfinally:\n    def test_t():\n        assert True\n",
            id="function in a finally",
        ),
        pytest.param(
            "try:\n    def test_t():\n        assert True\n"
            "except* ImportError:\n    pass\n",
            id="function in a try with except*",
        ),
        pytest.param(
            "try:\n    pass\nexcept* ImportError:\n    pass\n"
            "else:\n    def test_t():\n        assert True\n",
            id="function in a try-except*'s else",
        ),
        pytest.param(
            "try:\n    pass\nexcept* ImportError:\n    pass\n"
            "finally:\n    def test_t():\n        assert True\n",
            id="function in a try-except*'s finally",
        ),
        pytest.param(
            "try:\n    pass\nexcept* ImportError:\n"
            "    def test_t():\n        assert True\n",
            id="function in an except* handler",
        ),
        pytest.param(
            "try:\n    pass\nexcept ImportError:\n"
            "    def test_e():\n        assert True\n",
            id="function in a handler",
        ),
        pytest.param(
            "import unittest\nclass Checks(unittest.TestCase):\n    pass\n",
            id="TestCase subclass",
        ),
        pytest.param(
            "from unittest import TestCase\nclass Checks(TestCase):\n    pass\n",
            id="TestCase subclass by its bare name",
        ),
    ],
)
def test_a_module_defining_a_test_needs_no_caller(tmp_path: Path, source: str) -> None:
    """A module defining a test pytest collects is never reported.

    :param tmp_path: where the stand-in tree is built.
    :param source: the module's source.
    """
    _write(tmp_path, "a_test.py", source)
    assert bodiless(tmp_path) == []


@pytest.mark.parametrize(
    "source",
    [
        pytest.param("def check():\n    def test_f():\n        pass\n", id="nested"),
        pytest.param(
            "class Checks:\n    def test_g(self):\n        pass\n", id="class"
        ),
    ],
)
def test_a_test_pytest_does_not_collect_is_no_test(tmp_path: Path, source: str) -> None:
    """A `test_` inside a function or a non-test class defines no test.

    :param tmp_path: where the stand-in tree is built.
    :param source: the module's source.
    """
    _write(tmp_path, "a_test.py", source)
    assert bodiless(tmp_path) == ["tests/integration/a_test.py"]


def test_data_is_not_read(tmp_path: Path) -> None:
    """A module under a `_data` directory is data, whatever it defines.

    :param tmp_path: where the stand-in tree is built.
    """
    _write(tmp_path, "_data/vendored_test.py", "X = 1\n")
    assert bodiless(tmp_path) == []
