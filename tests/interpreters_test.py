# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 1's interpreter window, asked across the repositories.

A library covers every interpreter still in support and an application
takes the newest its dependencies allow, which is section 1's rule and
the reason the two halves are asked differently here.

Each tree that publishes holds a module of this name reading its own
declarations against one another -- `requires-python` against the
classifiers, the classifiers against the platform sweeps -- which is
what section 15 means by a repository answering for itself. It is a
published tree's, which section 3 states where it states the convention
and section 15 gives the reason for.

Two questions are left here. The one no tree can ask: the window a
library covers is python.org's release cycle rather than that library's
choice, so the libraries name one window and a tree that disagrees with
the others is out of step with the cycle. And the ends of that window,
where the tree that would compare them holds no module of its own: they
are declared in `pyproject.toml` and in `.python-version` whatever the
tree is, and this reads them against one another. Which tree is a
library is `library` below, section 1 giving the rule and the reason.

The calendar itself is asked of nothing here. What decides it is
python.org's, a date in it is a date this suite would have to be told,
and what the trees can be held to without one is that they agree.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest

from . import Tier, by_hand, tracked

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

CLASSIFIER = re.compile(r"^Programming Language :: Python :: (3\.\d+)$")
"""A classifier naming one interpreter version.

`:: 3` and `:: 3 :: Only` say something about the major version, and
`:: Implementation :: PyPy` about an implementation: neither is a
version this compares.
"""

OWN_MODULE = "tests/interpreters_test.py"
"""The module a published tree holds to keep its declarations in step."""

LIBRARY = "Topic :: Software Development :: Libraries :: Python Modules"
"""The classifier a distribution declares to say it is a library.

Section 1 keys the interpreter window on which of the two a repository
is, and this is where a repository says so. One string exactly: the
family it belongs to holds other languages' modules and
`:: Application Frameworks` besides, so a prefix would read a claim
nobody made.
"""


def library(parsed: dict[str, Any], repository_tier: Tier) -> bool:
    """Say whether a tree is a library, as section 1 decides it.

    Both halves are the same question asked of the two parties to an
    import: the tier is whether an index carries the distribution, and
    the classifier is what the distribution on it says it is.

    :param parsed: the tree's parsed `pyproject.toml`.
    :param repository_tier: the repository's tier.
    :returns: whether it publishes and declares itself a library.
    """
    if not Tier.PUBLISHER.binds(repository_tier):
        return False
    classifiers: list[str] = parsed.get("project", {}).get("classifiers", [])
    return LIBRARY in classifiers


def versions(parsed: dict[str, Any]) -> tuple[str, tuple[str, ...]]:
    """Read the floor and the per-version classifiers of one tree.

    :param parsed: the tree's parsed `pyproject.toml`.
    :returns: the floor `requires-python` names, and the classified
        versions in the order the file gives them.
    """
    project: dict[str, Any] = parsed.get("project", {})
    floor = str(project.get("requires-python", "")).removeprefix(">=")
    classifiers: list[str] = project.get("classifiers", [])
    found = (CLASSIFIER.match(classifier) for classifier in classifiers)
    return floor, tuple(match[1] for match in found if match)


def pinned(root: Path) -> str:
    """Read the interpreter version `.python-version` names.

    Whole-line comments are what that file takes, section 1 saying why,
    so what is left of it once they are dropped is the pin. A `t` suffix
    is dropped with them: it asks for that version built without the
    GIL, which is the same version as far as a classifier is concerned.

    :param root: the root of the checkout.
    :returns: the version, empty where the tree holds no such file.
    """
    path = root / ".python-version"
    if not path.is_file():
        return ""
    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    return lines[0].removesuffix("t") if lines else ""


def ordered(version: str) -> tuple[int, ...]:
    """Return a version as the numbers that sort it.

    :param version: a version as it is written, `3.10` and the like.
    :returns: its parts, so that `3.9` sorts below `3.10`.
    """
    return tuple(int(part) for part in version.split("."))


def test_the_libraries_name_one_interpreter_window(
    pyprojects: dict[str, dict[str, Any]],
    tiers: dict[str, Tier],
) -> None:
    """Section 1: the window is python.org's, so it is one for all of them.

    A floor or a classifier list only one of them declares is that tree
    left behind by a cycle that moved, and which of them is wrong is the
    cycle's answer rather than this suite's. A tree that publishes a
    program rather than a library is out of the comparison instead of
    wrong in it, its own window being its dependencies'.

    :param pyprojects: the parsed files.
    :param tiers: each repository's tier.
    """
    declared: dict[str, list[str]] = {}
    for repository, parsed in sorted(pyprojects.items()):
        if not library(parsed, tiers[repository]):
            continue
        floor, classified = versions(parsed)
        listed = ",".join(sorted(classified, key=ordered))
        window = f">={floor}, classifiers {listed or 'none'}"
        declared.setdefault(window, []).append(repository)
    assert declared, (
        "no repository declares itself a library, and this compared nothing"
    )
    assert len(declared) == 1, f"section 1's one window, declared as {declared}"


@pytest.mark.tier(Tier.PUBLISHER)
def test_every_publisher_holds_the_module_that_reads_its_declarations(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 15: a repository answers for itself where it can.

    That sentence names this module, in each tree that publishes, as
    what reads the three declarations of one tree against one another.
    A tree without it declares them in three files and compares them
    nowhere, and this suite asks only whether they agree across the
    trees. Publishing and not section 1's library is what decides the
    population, for the reason section 15 gives.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    assert tracked(trees[repository], OWN_MODULE), f"no {OWN_MODULE}; " + by_hand(
        repository, f"git ls-files {OWN_MODULE}"
    )


@pytest.mark.tier(Tier.PYTHON)
def test_the_floor_is_the_lowest_interpreter_the_tree_declares(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 1: `requires-python` is the oldest interpreter supported.

    A floor and a classifier list in one file are two statements of one
    end of the window, whatever the tree is, so the lowest classifier is
    what the floor names. Section 15 is where a tree holding no module
    of its own is answered for, and why.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    floor, classified = versions(pyprojects[repository])
    if not classified:
        pytest.skip(f"{repository} declares no per-version Python classifier")
    lowest = min(classified, key=ordered)
    command = by_hand(
        repository, "grep -n 'requires-python\\|Python :: 3\\.' pyproject.toml"
    )
    assert floor == lowest, (
        f"requires-python is >={floor} and the lowest classifier is {lowest}; "
        + command
    )


@pytest.mark.tier(Tier.PYTHON)
def test_the_pin_is_the_newest_interpreter_the_tree_declares(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 1: `.python-version` is the newest interpreter covered.

    The classifiers are what a tree says it covers, so the newest of
    them is the same end of the window as the pin, in another file. A
    library's own module reads the classifiers against `requires-python`
    and against the sweeps, and the pin is in neither comparison.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: the parsed files.
    """
    _, classified = versions(pyprojects[repository])
    if not classified:
        pytest.skip(f"{repository} declares no per-version Python classifier")
    newest = max(classified, key=ordered)
    pin = pinned(trees[repository])
    assert pin == newest, (
        f".python-version is {pin!r} and the newest classifier is {newest}; "
        + by_hand(repository, "cat .python-version")
    )
