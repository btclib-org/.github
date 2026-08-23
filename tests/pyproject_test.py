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

DOC_WIDTH = 80
"""Section 5's width for the half of a file `ruff-format` never rewrites.

The section's reason for this number rather than the 88 the formatter
reflows code to is that it is the width markdown is already held to.
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


def distribution(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return the `[project]` table of a tree that builds a distribution.

    Skipped where the file names no build backend: section 3's metadata
    is a distribution's and a file that builds none holds no subject for
    it, which is section 2's sentence about a rule whose subject the
    tree does not have.

    :param repository: the repository's name.
    :param pyprojects: the parsed files.
    :returns: the table, empty where the tree declares none.
    """
    document = parsed(repository, pyprojects)
    if "build-system" not in document:
        pytest.skip(f"{repository} names no build backend")
    project: dict[str, Any] = document.get("project", {})
    return project


def ruff_lint(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return the `[tool.ruff.lint]` table of one repository.

    :param repository: the repository's name.
    :param pyprojects: the parsed files.
    :returns: the table, empty where the tree declares none.
    """
    tool: dict[str, Any] = parsed(repository, pyprojects).get("tool", {})
    ruff: dict[str, Any] = tool.get("ruff", {})
    lint: dict[str, Any] = ruff.get("lint", {})
    return lint


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
def test_the_licence_is_an_expression_with_its_files(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 3: PEP 639's two keys, the SPDX string and `license-files`.

    A tree declaring the deprecated table, or no key at all, passes
    `classifiers_test.py` -- which reads `license` to refuse the
    classifier beside an expression and so asks nothing of a tree that
    has none -- and is refused here. What the list holds is section 3's
    rule; this asks that the key is declared, and asserting the names is
    what btclib-org/btclib-node#235 has to be closed for.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    project = distribution(repository, pyprojects)
    command = by_hand(repository, "grep -n '^license' pyproject.toml")
    expression = project.get("license")
    assert isinstance(expression, str), f"license is {expression!r}; " + command
    files = project.get("license-files")
    assert files, f"license-files is {files!r}; " + command


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
    lint = ruff_lint(repository, pyprojects)
    command = by_hand(repository, "grep -n 'notice-rgx\\|\"CPY\"' pyproject.toml")
    assert "CPY" in lint.get("select", []), "CPY is not selected; " + command
    pattern = lint.get("flake8-copyright", {}).get("notice-rgx")
    assert pattern, "CPY is selected with no notice-rgx; " + command


@pytest.mark.tier(Tier.PYTHON)
def test_w_is_selected_with_max_doc_length_at_80(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 5: the second width, on the half a formatter never touches.

    `ruff-format` reflows code and rewrites neither a comment nor a
    docstring, so what holds those to the width is W505 -- a rule of the
    "W" family, and inert without the key, ruff having no default doc
    length. Either half on its own gates nothing, which is why both are
    asked here.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    lint = ruff_lint(repository, pyprojects)
    command = by_hand(repository, "grep -n 'max-doc-length\\|\"W\"' pyproject.toml")
    assert "W" in lint.get("select", []), "W is not selected; " + command
    width = lint.get("pycodestyle", {}).get("max-doc-length")
    assert width == DOC_WIDTH, f"max-doc-length is {width!r}; " + command


@pytest.mark.tier(Tier.PYTHON)
def test_d_is_selected_with_the_pep257_convention(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 5: docstrings are gated, at the convention it names.

    The convention decides which of the family runs, so a tree selecting
    `D` without one asks its docstrings the whole of what ruff writes
    under that letter rather than what pep257 states --
    `missing-terminal-punctuation` among it, over the end of a summary
    line `missing-trailing-period` has already reported.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    lint = ruff_lint(repository, pyprojects)
    command = by_hand(repository, "grep -n 'convention\\|\"D\"' pyproject.toml")
    assert "D" in lint.get("select", []), "D is not selected; " + command
    convention = lint.get("pydocstyle", {}).get("convention")
    assert convention == "pep257", f"convention is {convention!r}; " + command


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
