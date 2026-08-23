# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What sections 1, 3, 5 and 6 say a `pyproject.toml` holds, per tree.

Each of these is one line of section 15's tree block, asked of every
tree at once instead of the one in front of a person. Section 1's group
table is read as data, the way `grid_test.py` reads the calendar: the
rows are the rule, and a group the trees declare that no row describes
is the finding whichever side is wrong.
"""

from __future__ import annotations

import tomllib
from typing import Any

import pytest

from . import ROOT, Tier, by_hand, fenced, name, rows

pytestmark = pytest.mark.integration

URLS = {
    "homepage",
    "documentation",
    "download",
    "changelog",
    "repository",
    "issues",
    "pull_requests",
}
"""Section 3's `[project.urls]` list, in the spelling two publishers use.

The section names the seven in prose and not as keys, and
btclib-org/.github#133 is where the spelling is being decided; the set
is compared case-insensitively with spaces read as underscores, so the
one spelling the comparison refuses is a different name for the link.
"""


def groups() -> set[str]:
    """Read the dependency-group table of section 1.

    :returns: the group names the table describes.
    """
    return {
        name(row["group"]) for row in rows(ROOT / "README.md", "group", "what it holds")
    }


def parsed(repository: str, pyprojects: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return the parsed `pyproject.toml` of one repository.

    :param repository: the repository's name.
    :param pyprojects: the parsed files.
    :returns: the document.
    """
    return pyprojects[repository]


@pytest.mark.tier(Tier.PYTHON)
def test_every_dependency_group_is_a_row_of_section_1(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 1's table describes every group a tree declares.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    declared = set(parsed(repository, pyprojects).get("dependency-groups", {}))
    unknown = sorted(declared - groups())
    assert not unknown, (
        f"dependency groups no row of section 1 describes: {unknown}; "
        + by_hand(
            repository,
            "sed -n '/^\\[dependency-groups\\]/,/^\\[[a-z]/p' pyproject.toml"
            " | grep -oE '^[a-z-]+ ='",
        )
    )


@pytest.mark.tier(Tier.PUBLISHER)
def test_the_project_urls_are_the_seven_section_3_names(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 3: `[project.urls]` carries seven links, by name.

    PyPI renders the key as the link's label, so a key spelled another
    way is on the index as written, and a link absent from the table is
    absent from the index -- the changelog above all, being the link
    from a version already published back to what changed in it.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    urls = parsed(repository, pyprojects).get("project", {}).get("urls", {})
    spelled = {key.lower().replace(" ", "_") for key in urls}
    assert spelled == URLS, (
        f"missing {sorted(URLS - spelled)}, unexpected {sorted(spelled - URLS)}; "
        + by_hand(repository, "sed -n '/^\\[project.urls\\]/,/^\\[/p' pyproject.toml")
    )


@pytest.mark.tier(Tier.PYTHON)
def test_cpy_is_selected_with_a_notice_rgx(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 5: the copyright notice is a ruff rule, `CPY` with a regex.

    Whether the regex is `COPYRIGHT`'s text transcribed is
    `copyright_test.py`'s question; this asks the one before it, whether
    the rule runs at all. A tree that does not select it has no gate on
    its headers, whatever its `COPYRIGHT` says.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    lint = (
        parsed(repository, pyprojects).get("tool", {}).get("ruff", {}).get("lint", {})
    )
    command = by_hand(repository, "grep -n 'notice-rgx\\|\"CPY\"' pyproject.toml")
    assert "CPY" in lint.get("select", []), "CPY is not selected; " + command
    pattern = lint.get("flake8-copyright", {}).get("notice-rgx")
    assert pattern, "CPY is selected with no notice-rgx; " + command


def enabled() -> list[str]:
    """Read the error codes section 6's `[tool.mypy]` block enables.

    :returns: the codes, in the order the section gives them.
    """
    block = fenced(ROOT / "README.md", "## 6. The code is typed", "toml")
    codes = tomllib.loads(block)["tool"]["mypy"]["enable_error_code"]
    return [str(code) for code in codes]


@pytest.mark.tier(Tier.PYTHON)
def test_enable_error_code_is_section_6_s_list(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 6: the same optional codes in every tree, and no others.

    A code that finds nothing today is a ratchet on the line written
    after it, so a tree that skipped one finds out later than the rest;
    and a code mypy turns on itself states a check the list does not
    buy. Both directions are the finding.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    mypy = parsed(repository, pyprojects).get("tool", {}).get("mypy", {})
    declared = sorted(str(code) for code in mypy.get("enable_error_code", []))
    apart = {
        "missing": sorted(set(enabled()) - set(declared)),
        "not section 6's": sorted(set(declared) - set(enabled())),
    }
    assert not any(apart.values()), f"enable_error_code is {apart}; " + by_hand(
        repository, "sed -nE '/^enable_error_code/,/^]/p' pyproject.toml"
    )


@pytest.mark.tier(Tier.PYTHON)
def test_mypy_is_strict(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 6: `strict = true`, and not a subset of its flags.

    The section says why a trajectory toward the strictness is not the
    strictness; `hooks_test.py` asks the other half, whether anything
    runs it.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    strict = (
        parsed(repository, pyprojects).get("tool", {}).get("mypy", {}).get("strict")
    )
    assert strict is True, f"[tool.mypy] strict is {strict!r}; " + by_hand(
        repository, "grep -n '^strict = true' pyproject.toml"
    )
