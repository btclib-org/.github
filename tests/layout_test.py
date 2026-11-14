# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 7's layout, read off the tree rather than off the hook.

The hook is section 4's and `hooks_test.py` asks whether it runs; this
asks whether the tree keeps the rule the hook would enforce, which is
the half a gate that is not installed cannot answer for.

The per-repository tests carry the `integration` marker, which the
controls do not: they build a tree in a temporary directory and reach
nothing.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

import pytest

from . import Tier, by_hand

if TYPE_CHECKING:
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

The exception is a test run on several nodes, one module per node.
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


def defines_a_test(module: ast.Module) -> bool:
    """Say whether a module defines a test pytest collects by default.

    :param module: the parsed module.
    :returns: whether it defines a `test*` function or a `Test*` class.
    """
    return any(
        (
            isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
            and node.name.startswith("test")
        )
        or (isinstance(node, ast.ClassDef) and node.name.startswith("Test"))
        for node in module.body
    )


def imports(module: ast.Module, stem: str) -> bool:
    """Say whether a module imports from the module named `stem`.

    :param module: the parsed module.
    :param stem: the imported module's name, without its package.
    :returns: whether any import, at any depth, names that module.
    """
    for node in ast.walk(module):
        if isinstance(node, ast.ImportFrom):
            if (node.module or "").rsplit(".", 1)[-1] == stem:
                return True
            if any(alias.name == stem for alias in node.names):
                return True
        if isinstance(node, ast.Import) and any(
            alias.name.rsplit(".", 1)[-1] == stem for alias in node.names
        ):
            return True
    return False


def bodiless(root: Path) -> list[str]:
    """List the test modules that define no test and are no shared body.

    A `*_test.py` under `tests/`, its `_data` directories aside, that
    defines no test is section 7's exception only where it is the body of
    a test run on several nodes: at least `NODES` modules beside it,
    each named `<file>_<node>_test.py` for its own `<file>_test.py`,
    define a test and import from it. Anything else is shared code in a
    module whose name says "test", which section 7 puts in a package
    `__init__.py`.

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
        stem = path.name.removesuffix(".py")
        prefix = path.name.removesuffix(SUFFIX) + "_"
        callers = [
            other
            for other, tree in parsed.items()
            if other.parent == path.parent
            and other.name.startswith(prefix)
            and len(other.name) > len(prefix) + len(SUFFIX)
            and defines_a_test(tree)
            and imports(tree, stem)
        ]
        if len(callers) < NODES:
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
        f"<file>_<node>_test.py call: {wrong}; "
        + by_hand(
            repository,
            "for f in $(git ls-files 'tests/**_test.py'); do "
            'grep -qE \'^(async )?def test|^class Test\' "$f" || echo "$f"; '
            "done",
        )
    )


def _write(root: Path, name: str, text: str) -> None:
    """Write a module under `tests/integration/` of a stand-in tree.

    :param root: the stand-in tree.
    :param name: the module's file name.
    :param text: its source.
    """
    path = root / "tests" / "integration" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


BODY = "def a_block_reaches_every_node(adapter):\n    assert adapter\n"
"""A shared test body: a function without the `test_` prefix."""


def _caller(stem: str, node: str) -> str:
    """Return the source of a per-node module calling a body.

    :param stem: the body module's name, without `.py`.
    :param node: the node the module runs the body on.
    :returns: the module's source.
    """
    return (
        f"from tests.integration.{stem} import a_block_reaches_every_node\n\n\n"
        f"def test_a_block_reaches_every_node({node}_adapter):\n"
        f"    a_block_reaches_every_node({node}_adapter)\n"
    )


def test_a_body_its_node_modules_call_is_admitted(tmp_path: Path) -> None:
    """The layout section 7 admits, with an absolute and a relative import.

    :param tmp_path: where the stand-in tree is built.
    """
    _write(tmp_path, "p2p_block_sync_test.py", BODY)
    _write(
        tmp_path,
        "p2p_block_sync_bitcoind_test.py",
        _caller("p2p_block_sync_test", "bitcoind"),
    )
    _write(
        tmp_path,
        "p2p_block_sync_btcd_test.py",
        "from .p2p_block_sync_test import a_block_reaches_every_node\n\n\n"
        "def test_it(btcd_adapter):\n"
        "    a_block_reaches_every_node(btcd_adapter)\n",
    )
    _write(tmp_path, "rpc_net_test.py", "def test_rpc():\n    assert True\n")
    assert bodiless(tmp_path) == []


def test_a_body_stripped_of_its_callers_is_refused(tmp_path: Path) -> None:
    """The same body, with no per-node module, or with one only, is refused.

    :param tmp_path: where the stand-in trees are built.
    """
    bare = tmp_path / "bare"
    _write(bare, "p2p_block_sync_test.py", BODY)
    assert bodiless(bare) == ["tests/integration/p2p_block_sync_test.py"]
    one = tmp_path / "one"
    _write(one, "p2p_block_sync_test.py", BODY)
    _write(
        one,
        "p2p_block_sync_bitcoind_test.py",
        _caller("p2p_block_sync_test", "bitcoind"),
    )
    assert bodiless(one) == ["tests/integration/p2p_block_sync_test.py"]


def test_a_helper_other_tests_import_is_refused(tmp_path: Path) -> None:
    """A helper module named for tests is refused, whoever imports it.

    Modules that import it and define a test, but are not named
    `<file>_<node>_test.py` for it, are no per-node modules; and modules
    so named that import nothing from it do not call it.

    :param tmp_path: where the stand-in trees are built.
    """
    helper = tmp_path / "helper"
    _write(helper, "p2p_conns_test.py", "class Conn:\n    pass\n")
    for name in ("p2p_fingerprint_test.py", "p2p_sendheaders_test.py"):
        _write(
            helper,
            name,
            "from tests.integration.p2p_conns_test import Conn\n\n\n"
            "def test_conn():\n    assert Conn\n",
        )
    assert bodiless(helper) == ["tests/integration/p2p_conns_test.py"]
    unrelated = tmp_path / "unrelated"
    _write(unrelated, "p2p_block_sync_test.py", BODY)
    for node in ("bitcoind", "btcd"):
        _write(
            unrelated,
            f"p2p_block_sync_{node}_test.py",
            "def test_it():\n    assert True\n",
        )
    assert bodiless(unrelated) == ["tests/integration/p2p_block_sync_test.py"]


def test_a_module_defining_a_test_needs_no_caller(tmp_path: Path) -> None:
    """A module that defines a test or a test class is never reported.

    :param tmp_path: where the stand-in tree is built.
    """
    _write(tmp_path, "a_test.py", "def test_a():\n    assert True\n")
    _write(tmp_path, "b_test.py", "async def test_b():\n    assert True\n")
    _write(tmp_path, "c_test.py", "class TestC:\n    pass\n")
    (tmp_path / "tests" / "_data").mkdir()
    (tmp_path / "tests" / "_data" / "vendored_test.py").write_text(
        "X = 1\n", encoding="utf-8"
    )
    assert bodiless(tmp_path) == []
