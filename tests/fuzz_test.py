# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""When `fuzz` runs, and what a fuzz tree's suite asks of its harnesses.

Each tree that section 10's record names under `fuzz` is asked two
things. Its `fuzz.yml` runs from the calendar and on a dispatch, and on
no `pull_request` or `pull_request_target`, and its `release.yml` does
not call it: section 10's `fuzz` entry says when the run happens, and
section 12 says a release dispatches none. Its suite holds a module that
runs a harness's `fuzz_target` under an empty stand-in `atheris`, as
section 7's *A fuzz harness runs on its seeds* asks.

Both are read off configuration and source, not prose. The second is
read with `ast`, not by running the tree's suite: it asks that a module
builds the stand-in and reads `fuzz_target` off what it loaded. Whether
that module reaches every harness and every seed is the tree's own suite
to say.
"""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

import pytest

from . import by_hand, tracked
from .grid_test import record
from .workflows_test import jobs, triggers

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

WORKFLOW = "fuzz.yml"

# the triggers section 10's `fuzz` entry gives the run, and those it refuses
OWED = frozenset({"schedule", "workflow_dispatch"})
REFUSED = frozenset({"pull_request", "pull_request_target"})


def refusals(on: dict[str, object]) -> list[str]:
    """Say what a `fuzz.yml` trigger block lacks or holds against the entry.

    :param on: the workflow's `on:` block.
    :returns: one line per trigger missing or refused, empty where none.
    """
    missing = [f"no {name}" for name in sorted(OWED - on.keys())]
    held = [f"a {name}" for name in sorted(REFUSED & on.keys())]
    return missing + held


def calls_fuzz(release: Mapping[str, Mapping[str, object]]) -> list[str]:
    """List the jobs of a `release.yml` that call `fuzz.yml`.

    :param release: the release workflow's jobs, by id.
    :returns: the ids of the jobs whose `uses:` names `fuzz.yml`.
    """
    return [
        job
        for job, body in release.items()
        if str(body.get("uses", "")).split("@")[0].endswith(f"/{WORKFLOW}")
    ]


def runs_a_harness(source: str) -> bool:
    """Say whether a module builds a stand-in atheris and reads `fuzz_target`.

    The stand-in is a `ModuleType("atheris")` call, whatever names the
    class; the read is an attribute `fuzz_target` of anything, which a
    test that walks a harness with `ast` and compares node names never
    makes.

    :param source: a test module's source.
    :returns: whether the module does both.
    """
    nodes = list(ast.walk(ast.parse(source)))
    stand_in = any(
        isinstance(node, ast.Call)
        and (
            (isinstance(node.func, ast.Name) and node.func.id == "ModuleType")
            or (isinstance(node.func, ast.Attribute) and node.func.attr == "ModuleType")
        )
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and node.args[0].value == "atheris"
        for node in nodes
    )
    target = any(
        isinstance(node, ast.Attribute) and node.attr == "fuzz_target" for node in nodes
    )
    return stand_in and target


def test_a_trigger_block_is_read_against_the_entry() -> None:
    """The calendar and a dispatch pass; a pull request or a gap does not."""
    assert refusals({"schedule": [], "workflow_dispatch": None}) == []
    assert refusals({"schedule": [], "workflow_dispatch": None, "push": {}}) == []
    assert refusals({"schedule": [], "pull_request": {}}) == [
        "no workflow_dispatch",
        "a pull_request",
    ]
    assert refusals({"workflow_call": {}, "workflow_dispatch": None}) == ["no schedule"]
    target: dict[str, object] = {
        "schedule": [],
        "workflow_dispatch": None,
        "pull_request_target": {},
    }
    assert refusals(target) == ["a pull_request_target"]


def test_a_call_of_fuzz_is_found_in_a_release() -> None:
    """A job calling `fuzz.yml` is found at any ref; another call is not."""
    release = {
        "test": {"uses": "./.github/workflows/test.yml"},
        "fuzz": {"uses": "./.github/workflows/fuzz.yml"},
        "pinned": {"uses": "btclib-org/x/.github/workflows/fuzz.yml@v1"},
        "oracle": {"uses": "./.github/workflows/btcd-fuzz.yml"},
        "build": {"runs-on": "ubuntu-latest"},
    }
    assert calls_fuzz(release) == ["fuzz", "pinned"]


def test_a_harness_run_is_told_from_an_ast_reading() -> None:
    """Only a module that loads a harness and reads its target counts."""
    runs = (
        "import types\n"
        "stand_in = types.ModuleType('atheris')\n"
        "module.fuzz_target(seed)\n"
    )
    reads = (
        "from types import ModuleType\n"
        "sys.modules['atheris'] = ModuleType('atheris')\n"
        "module.arguments(seed)\n"
        "if node.name == 'fuzz_target': pass\n"
    )
    assert runs_a_harness(runs)
    assert not runs_a_harness(reads)


# lists the modules that both build the stand-in and read `fuzz_target`
COMMAND = (
    "git grep -l --all-match -e 'ModuleType(.atheris.)' -e '[.]fuzz_target' -- tests"
)


def fuzz_tree(repository: str) -> None:
    """Skip a repository the record does not name under `fuzz`.

    :param repository: the repository asked about.
    """
    if repository not in record()["fuzz"]:
        pytest.skip(f"section 10's fuzz entry does not name {repository}")


@pytest.mark.integration
def test_fuzz_runs_from_the_calendar_and_no_release(
    repository: str, trees: dict[str, Path]
) -> None:
    """`fuzz.yml` runs on a schedule and a dispatch; no `release.yml` calls it.

    A tree with no `release.yml` publishes nothing, and is asked only of
    the triggers.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    fuzz_tree(repository)
    here = trees[repository] / ".github" / "workflows"
    wrong = refusals(triggers(here / WORKFLOW))
    command = f"sed -n '/^on:/,/^[a-z]/p' .github/workflows/{WORKFLOW}"
    found = f"{repository}'s {WORKFLOW} has {', '.join(wrong)}"
    assert not wrong, f"{found}; {by_hand(repository, command)}"
    release = here / "release.yml"
    callers = calls_fuzz(jobs(release)) if release.is_file() else []
    assert not callers, (
        f"{repository}'s release.yml calls {WORKFLOW} from {callers}; "
        + by_hand(repository, f"git grep -n 'uses:.*{WORKFLOW}' -- .github/workflows")
    )


@pytest.mark.integration
def test_the_suite_runs_each_harness(repository: str, trees: dict[str, Path]) -> None:
    """A test module loads a harness under a stand-in atheris and runs it.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    fuzz_tree(repository)
    root = trees[repository]
    modules = [
        path
        for path in tracked(root, "tests/*.py", "tests/**/*.py")
        if runs_a_harness((root / path).read_text(encoding="utf-8"))
    ]
    assert modules, (
        f"no module of {repository}'s tests/ runs a harness's fuzz_target "
        "under a stand-in atheris; " + by_hand(repository, COMMAND)
    )
