"""What every module here needs fetched, fetched once."""

from __future__ import annotations

import os
import subprocess
import tomllib
from pathlib import Path
from typing import Any

import pytest

from .organization import ORG, ROOT, SELF, gh, gh_json


@pytest.fixture(autouse=True)
def _opt_in() -> None:
    """Skip unless the switch is set, this whole suite being integration."""
    if not os.environ.get("BTCLIB_INTEGRATION"):
        pytest.skip("set BTCLIB_INTEGRATION=1 to run the alignment tests")


@pytest.fixture(scope="session")
def repositories() -> list[str]:
    """Ask the API for every repository, rather than listing them here.

    A list written down here would be one more place to remember a new
    repository, and the one place nobody would think to look: a tree that
    joins the organization is in scope for this suite the moment it
    exists. Archived repositories are out -- what they agree with is the
    standard of the day they were archived.

    Forks are not, though they were: the reason given was that a fork's
    conventions are upstream's, and that is false for a fork the
    organization has taken over. `bbt` is one -- its upstream has not
    been pushed since 2022, every commit since is the organization's, and
    the nine forks downstream are of this copy rather than of that one.
    Excluding it meant the one repository furthest from the standard was
    the one nothing measured.

    The filter is right in general and was wrong for one repository, so
    it comes back the day that repository is detached from its upstream:
    btclib-org/bbt#13 carries the request GitHub's support grants, and
    the last box on it is this line.

    :returns: the repository names, `.github` among them.
    """
    return gh(
        f"orgs/{ORG}/repos?per_page=100",
        ".[] | select(.archived == false) | .name",
    )


@pytest.fixture(scope="session")
def settings(repositories: list[str]) -> dict[str, dict[str, Any]]:
    """Ask the API for the repository document of every repository.

    One document answers two of this suite's questions -- the topics are
    in it and so is the merge method -- so it is fetched here rather than
    once per module.

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
