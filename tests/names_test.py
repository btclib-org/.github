# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""How a requirement naming a distribution of the organization spells it.

Section 3 says the name in `[project]` is the distribution's, spelled
PEP 503's canonical way, and that the repository takes that spelling
too. What that bullet does not reach is the same name written down by
another tree, or by this one anywhere but that key, and section 14 is
what reaches it: a name spelled two ways is a convention differing
between two repositories, and neither of that section's lists carries
it.

Nothing reports the difference on its own. PEP 503 folds runs of `-`,
`_` and `.` to a single `-` before a resolver matches a requirement, so
both spellings resolve and install the same distribution, and the gate
of the tree carrying the odd one is green. That is what makes this a
test rather than a sweep of the trees: a sweep is true on the day it
runs.

**The position is read and never the spelling.** The underscore
spelling of a hyphenated distribution is also correct, twice over: it
is the import package the distribution installs, and it is what PEP 427
escapes the name to for a wheel or an sdist filename, whatever the
project calls itself. A test reading the spelling reports both, and the
list of exceptions it then carries is the sweep again. So a name is a
requirement where a table declares it as one, or where a version
specifier or an extras bracket follows it, and an import package is
written in neither position. What no position tells apart is a bare
name on an installer's command line, which reads as prose does.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest

from . import by_hand, tracked
from .pyproject_test import RUNS

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

SPECIFIED = r"(?=[<>=!~[])"
"""What follows a name written as a requirement rather than as prose.

PEP 508's operators are `<`, `<=`, `!=`, `==`, `===`, `>=`, `>` and
`~=`, so the character a specifier opens with is in this class whichever
of them it is, and a bracket opens an extras list. The class asks
whether the token is a requirement without asking which requirement it
is. It is a lookahead: the name is what an assertion reports, and the
specifier is only the evidence that a name is what was written.
"""

BOUNDARY = r"(?<![A-Za-z0-9_.-])"
"""What keeps a name from answering where it is the tail of a longer one.

The family of `btclib` would otherwise find itself in
`python_btclib>=1`, which is somebody else's distribution. No tree
writes a requirement of that shape, so this selects nothing out and is a
guard rather than a description.
"""

REQUIREMENT = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")
"""The name PEP 508 opens a requirement with, ahead of extras and specifier."""

DISTRIBUTION = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$")
"""PEP 508's grammar for a name, which not every repository name answers.

`.github` does not, and section 3 says why where it says the repository
is named after the distribution: PEP 503 folds that name to `-github`,
which no requirement may be. A repository no requirement can name is
one this module has no question about.
"""

HISTORIES = ("CHANGELOG.md", "RELEASE_NOTES.md")
"""The two files section 9 says nothing already written in is rewritten.

A rule they could keep only by editing an entry that has landed is no
rule, so what they hold is out of the comparison rather than excused in
it.
"""


def family(name: str) -> str:
    """Return the pattern matching every spelling of a name.

    PEP 503 folds a run of `-`, `_` or `.` to a single `-` and lowercases
    before matching, so the family is the folded name with each `-`
    widened back to a run of any of the three.

    :param name: the name, in any spelling.
    :returns: the pattern, without the boundary or the lookahead.
    """
    parts = RUNS.sub("-", name).lower().split("-")
    return "[-_.]+".join(re.escape(part) for part in parts)


def declared(parsed: dict[str, Any]) -> list[tuple[str, str]]:
    """Return every requirement a parsed `pyproject.toml` names.

    A `[tool.uv.sources]` key is one: it is matched against a name in a
    requirement table, so it is a name written down rather than a label
    the table chooses. An entry that is a table rather than a string --
    `include-group` -- names a group of this file and no distribution.

    :param parsed: the file, parsed.
    :returns: one table path and one name per entry, in the file's order.
    """
    project = parsed.get("project", {})
    uv = parsed.get("tool", {}).get("uv", {})
    tables: dict[str, Any] = {
        "project.dependencies": project.get("dependencies"),
        "build-system.requires": parsed.get("build-system", {}).get("requires"),
    }
    for extra, entries in (project.get("optional-dependencies") or {}).items():
        tables[f"project.optional-dependencies.{extra}"] = entries
    for group, entries in (parsed.get("dependency-groups") or {}).items():
        tables[f"dependency-groups.{group}"] = entries
    for key in ("constraint-dependencies", "override-dependencies"):
        tables[f"tool.uv.{key}"] = uv.get(key)
    out = [
        (table, found.group(1))
        for table, entries in tables.items()
        for entry in entries or []
        if isinstance(entry, str) and (found := REQUIREMENT.match(entry))
    ]
    out.extend(("tool.uv.sources", key) for key in uv.get("sources", {}))
    return out


def written(root: Path, name: str, pattern: re.Pattern[str]) -> list[str]:
    """Find every requirement in a tree that spells a name another way.

    Read out of the files a reader or a resolver meets, which is what the
    tree tracks less the two histories and less its Python: a requirement
    inside Python source is a string the program uses, an argument it
    assembles or a fixture it feeds, so what that string is, is the
    program's to say. A file this cannot decode is not one a reader reads
    as prose either.

    :param root: the root of the checkout.
    :param name: the canonical spelling.
    :param pattern: the family of that name.
    :returns: one `path:line spells <name> <spelling>` per occurrence.
    """
    out: list[str] = []
    for path in tracked(root):
        if path in HISTORIES or path.endswith(".py"):
            continue
        try:
            text = (root / path).read_text(encoding="utf-8")
        except OSError, UnicodeDecodeError:
            continue
        for found in pattern.finditer(text):
            if found.group(0) != name:
                line = text.count("\n", 0, found.start()) + 1
                out.append(f"{path}:{line} spells {name} {found.group(0)}")
    return out


def decides(repository: str, names: list[str], where: str) -> str:
    """Say which command answers for a name by hand, in one checkout.

    The alternatives are built from the names the run found rather than
    written down, so the command asks about what failed and stays right
    as the organization gains a repository.

    :param repository: the repository the assertion was asked of.
    :param names: the canonical spellings to look for.
    :param where: the pathspec or file the command reads.
    :returns: the text an assertion message ends with.
    """
    alternatives = "|".join(family(name) for name in names)
    return by_hand(repository, f"git grep -nE '({alternatives})[<>=!~[]' -- {where}")


@pytest.fixture(scope="session")
def canonical(
    repositories: list[str],
    pyprojects: dict[str, dict[str, Any]],
) -> dict[str, re.Pattern[str]]:
    """Return every name of the organization against the family of it.

    Two kinds of name answer to this, and section 3 states both: a
    repository is named after the distribution it holds, and `[project]`
    names the distribution. A tree declaring `package = false` builds no
    distribution, so its `name` is its own and is left out -- the
    condition section 3's own bullet carries. The two kinds are one set
    because the question is the spelling and not which of them was
    meant: they are the same string wherever both exist.

    :param repositories: the names the API answered with.
    :param pyprojects: the parsed files.
    :returns: each name against the compiled pattern of its family.
    """
    names = set(repositories)
    for parsed in pyprojects.values():
        if parsed.get("tool", {}).get("uv", {}).get("package") is False:
            continue
        name = parsed.get("project", {}).get("name")
        if isinstance(name, str):
            names.add(name)
    return {
        name: re.compile(BOUNDARY + family(name) + SPECIFIED, re.IGNORECASE)
        for name in sorted(names)
        if DISTRIBUTION.match(name)
    }


def test_every_requirement_a_tree_declares_spells_the_name_canonically(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
    canonical: dict[str, re.Pattern[str]],
) -> None:
    """Section 14: one spelling of a name, in the tables a resolver parses.

    A requirement table is where a name is a name whether or not a
    specifier follows it, so this is asked of the parsed file and the
    test below of the text.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    :param canonical: each name against its family.
    """
    parsed = pyprojects.get(repository)
    if parsed is None:
        pytest.skip(f"{repository} has no pyproject.toml")
    spellings = {RUNS.sub("-", name).lower(): name for name in canonical}
    odd = {
        f"{table} names {entry}, and the distribution is {name}": name
        for table, entry in declared(parsed)
        if (name := spellings.get(RUNS.sub("-", entry).lower())) and entry != name
    }
    assert not odd, f"{sorted(odd)}; " + decides(
        repository, sorted(set(odd.values())), "pyproject.toml"
    )


def test_every_requirement_a_tree_writes_down_spells_the_name_canonically(
    repository: str,
    trees: dict[str, Path],
    canonical: dict[str, re.Pattern[str]],
) -> None:
    """Section 14: one spelling of a name, in what a reader is given.

    A resolver takes either spelling, so what the written form decides
    is what a reader copies out and types.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param canonical: each name against its family.
    """
    odd = {
        line: name
        for name, pattern in canonical.items()
        for line in written(trees[repository], name, pattern)
    }
    assert not odd, f"{sorted(odd)}; " + decides(
        repository, sorted(set(odd.values())), "."
    )
