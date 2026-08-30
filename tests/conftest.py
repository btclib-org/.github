# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What every module here needs fetched, fetched once."""

from __future__ import annotations

import importlib
import inspect
import os
import subprocess
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from . import BACKLOG, ORG, ROOT, SELF, Tier, filed, gh_json, names, tier

if TYPE_CHECKING:
    from collections.abc import Generator

SWITCH = "BTCLIB_INTEGRATION"
"""The environment variable without which this suite skips itself."""

REPOSITORY = "repository"
"""The argument a test takes to be asked once per repository.

A test that names it is parametrized over the organization at
collection, by `pytest_generate_tests` below, and is what the tier
marker and the backlog apply to. The cross-repository tests take the
session fixtures instead and run once.
"""


def opted_in() -> bool:
    """Say whether the switch is set.

    :returns: whether the run may reach GitHub.
    """
    return bool(os.environ.get(SWITCH))


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Ask every per-repository test of every repository, by name.

    Each repository is one parameter and so one row of the report,
    which is what makes the run a matrix rather than one assertion over
    a dict: a reader sees which tree failed which question without
    parsing a message. A failure the tracker already records carries the
    issue as a strict expected failure, read off the backlog here and not
    in the test, so the test states the rule and this says who is known
    not to keep it yet. Only an assertion counts as the expected
    failure: a repository that errors before the assertion -- a file it
    no longer has, a key it dropped -- is reported as the error it is
    rather than passing for the wrong reason, and one that skips before
    it is failed by `pytest_runtest_makereport`.

    Without the switch the parameter is one placeholder, which
    `pytest_collection_modifyitems` then skips with everything else: the
    list is fetched from the API, and a run that may not reach it has no
    names to parametrize on.

    :param metafunc: the test function being collected.
    """
    if REPOSITORY not in metafunc.fixturenames:
        return
    if not opted_in():
        metafunc.parametrize(REPOSITORY, [pytest.param("", id="unset")])
        return
    test = metafunc.definition.originalname
    params = []
    for name in names():
        issues = filed(test, name)
        marks = []
        if issues:
            marks.append(pytest.mark.backlog(*issues))
            marks.append(
                pytest.mark.xfail(
                    strict=True, raises=AssertionError, reason=cited(issues)
                )
            )
        params.append(pytest.param(name, id=name, marks=marks))
    metafunc.parametrize(REPOSITORY, params)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Skip the run without the switch, and refuse an orphaned backlog row.

    The switch is read here and not in a fixture because a skip marked
    at collection is decided before any fixture is set up, where a
    fixture that skips runs after every session fixture the test asked
    for: the rulesets fetched and the trees cloned, and then the test
    skipped. This whole suite being integration, a run without the
    switch reaches nothing.

    A backlog row keyed on a test that was renamed, or on a repository
    that was, would match nothing and excuse nothing, and the strict
    expected failure it was meant to be would never be asked: the run
    would be green with a finding unfiled. So a row naming a test no
    module of this suite asks per repository, or a repository the API
    does not list, is an error of the collection and not a quiet no-op.
    Per repository, because a test that runs once has no cell for the
    row to excuse, and a row naming one would pass this check and
    change nothing. The modules are read rather than the collected
    items, so that a run narrowed to one test by its id is not refused
    for the rows it left out.

    :param items: the collected tests, parametrized.
    :raises pytest.UsageError: where a backlog row names nothing.
    """
    if not opted_in():
        for item in items:
            item.add_marker(
                pytest.mark.skip(reason=f"set {SWITCH}=1 to run the alignment tests")
            )
        return
    defined = {
        attribute
        for path in sorted(Path(__file__).parent.glob("*_test.py"))
        for attribute, function in vars(
            importlib.import_module(f"{__package__}.{path.stem}")
        ).items()
        if attribute.startswith("test_")
        and REPOSITORY in inspect.signature(function).parameters
    }
    orphans = [
        f"#{issue}: {test} on {repository}"
        for issue, test, repositories in BACKLOG
        for repository in repositories
        if test not in defined or repository not in names()
    ]
    if orphans:
        msg = f"BACKLOG in tests/__init__.py lists rows no test answers to: {orphans}"
        raise pytest.UsageError(msg)


def cited(issues: tuple[int, ...] | list[int]) -> str:
    """Name the issues a backlog row carries, qualified.

    :param issues: the issue numbers.
    :returns: the numbers as section 9 spells a reference to this tree.
    """
    return ", ".join(f"btclib-org/.github#{issue}" for issue in issues)


# pytest's own hook spec names this parameter, and pluggy matches a
# hook implementation's signature against it -- dropping the name is
# dropping the hook, not narrowing an argument nothing here reads.
@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[None],  # noqa: ARG001
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Fail a backlog cell this run skipped instead of asking.

    A row excuses a failure, and a strict expected failure is what turns
    a repository that catches up into a red cell. A cell the run skips
    -- the tree dropped the file the test reads, or its tier moved past
    the one the test asks -- is neither: pytest reports a skip, the
    expected failure is never asked, and the row excuses nothing while
    reading as a finding. So a skip on a cell the `backlog` marker names
    is reported as a failure naming the row, in whichever phase it
    happens: the tier fixture skips at setup, a test at call. An
    expected failure that held is a skip too in pytest's report,
    `wasxfail` telling it apart; and the marker is what keeps this off
    the expected failures `verbatim_test.py` marks on its own.

    `tryfirst` makes this the outermost wrapper, so the report it reads
    is the one pytest's own xfail handling has finished with.

    :param item: the test asked.
    :param call: the phase that ran.
    :returns: the report, its outcome rewritten where the row excuses
        a cell the run did not ask.
    """
    report = yield
    marker = item.get_closest_marker("backlog")
    if marker is None or not report.skipped or hasattr(report, "wasxfail"):
        return report
    reason = report.longrepr[2] if isinstance(report.longrepr, tuple) else ""
    reason = reason.removeprefix("Skipped: ")
    report.outcome = "failed"
    report.longrepr = (
        f"the backlog excuses {item.nodeid} for {cited(marker.args)}, "
        f"and this run did not ask it: {reason}. A row excuses a failure; "
        "take the repository out of the row, or the test's question "
        "has changed under it."
    )
    return report


@pytest.fixture(autouse=True)
def _in_tier(request: pytest.FixtureRequest) -> None:
    """Skip a per-repository test asked of a repository its tier does not bind.

    The `tier` marker names the tier a test applies down to, and a test
    without one applies to every repository. Skipped with the reason
    rather than passed, so the report says which cells of the matrix
    were not asked and why, and a repository whose tier moves shows as
    a change in the skips rather than in nothing.

    :param request: the test being set up.
    """
    marker = request.node.get_closest_marker("tier")
    if marker is None or REPOSITORY not in request.fixturenames:
        return
    (asked,) = marker.args
    repository = request.getfixturevalue(REPOSITORY)
    tiers: dict[str, Tier] = request.getfixturevalue("tiers")
    if not asked.binds(tiers[repository]):
        pytest.skip(
            f"{repository} is tier {tiers[repository]}, and this asks tier {asked}"
        )


@pytest.fixture(scope="session")
def repositories() -> list[str]:
    """Return the names `pytest_generate_tests` parametrized on.

    :returns: the repository names, `.github` among them.
    """
    return names()


@pytest.fixture(scope="session")
def settings(repositories: list[str]) -> dict[str, dict[str, Any]]:
    """Ask the API for the repository document of every repository.

    One document answers more than one of this suite's questions -- the
    topics are in it, the merge method and the homepage -- so it is
    fetched here rather than once per module.

    :param repositories: the names to ask about.
    :returns: each name against its repository document.
    """
    return {
        repository: gh_json(f"repos/{ORG}/{repository}") for repository in repositories
    }


@pytest.fixture(scope="session")
def trees(
    repositories: list[str],
    tmp_path_factory: pytest.TempPathFactory,
) -> dict[str, Path]:
    """Check out every repository, and use this working tree for `.github`.

    Shallow and tagless: every question here is about the tip of the
    default branch. Submodules are left unfetched -- the one repository
    that has any vendors a C library, which nothing here reads.

    :param repositories: the names to fetch.
    :param tmp_path_factory: pytest's per-session temporary directory.
    :returns: each name against the root of its tree.
    """
    base = tmp_path_factory.mktemp("trees")
    out: dict[str, Path] = {}
    for repository in repositories:
        if repository == SELF:
            out[repository] = ROOT
            continue
        target = base / repository
        subprocess.run(
            [
                "git",
                "clone",
                "--depth=1",
                "--no-tags",
                "--quiet",
                f"https://github.com/{ORG}/{repository}.git",
                str(target),
            ],
            check=True,
        )
        out[repository] = target
    return out


@pytest.fixture(scope="session")
def tiers(trees: dict[str, Path]) -> dict[str, Tier]:
    """Measure the tier of every repository off its tree.

    :param trees: the checkouts.
    :returns: each name against its tier.
    """
    return {repository: tier(root) for repository, root in trees.items()}


@pytest.fixture(scope="session")
def pyprojects(trees: dict[str, Path]) -> dict[str, dict[str, Any]]:
    """Parse the `pyproject.toml` of every tree that has one.

    :param trees: the checkouts.
    :returns: each name against its parsed file, the others left out.
    """
    out: dict[str, dict[str, Any]] = {}
    for repository, root in trees.items():
        path = root / "pyproject.toml"
        if path.is_file():
            out[repository] = tomllib.loads(path.read_text(encoding="utf-8"))
    return out
