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

import functools
import re
import subprocess
import tomllib
from typing import TYPE_CHECKING, Any

import pytest

from . import ROOT, Tier, by_hand, fenced, name, rows
from .copyright_test import collective

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

RUNS = re.compile(r"[-_.]+")
"""PEP 503's normalization: runs of `-`, `_` and `.` folded to one `-`."""

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

UV_DOCKERFILE = "repos/dependabot/dependabot-core/contents/uv/Dockerfile"
"""Where the updater's own bundled uv is pinned, read the way section 1's
`required-version` line points at it: not this organization's API, but
the same `gh api` this suite already asks it with.
"""

UNREADABLE = "Not Found"
"""What `gh api` reports for a document the token cannot see or that moved.

The same message `protection_test.py` tells apart from every other `gh`
failure: a document missing is this suite's business, a throttled or
failing API is not, and the two are not the same finding.
"""

FLOOR = re.compile(r"^>=\s*(?P<version>[0-9]+(?:\.[0-9]+)*)$")
"""`required-version`, restricted to the bare floor every tree writes.

Section 1 calls the key the oldest uv that may read the lock, which is
`>=` or nothing checkable at all -- an exact pin or an upper bound asks
a different question than the one this test answers.
"""


@functools.cache
def dockerfile() -> str | None:
    """Fetch `dependabot-core`'s `uv/Dockerfile`, as text.

    Cached for the run, the way `names()` in `tests/__init__.py` caches
    the organization's own repository list: every tree asks the same
    question of the same file.

    :returns: the file's text, or `None` where `gh` reports it or its
        repository missing -- `dependabot-core` reorganising
        `uv/Dockerfile` is a tree this suite does not own, so a test
        reading it skips rather than fails on that day.
    :raises subprocess.CalledProcessError: any other `gh` failure --
        a throttled or failing API being neither this suite's business
        nor a reason to read the fetch as having found nothing.
    """
    try:
        return subprocess.run(
            ["gh", "api", "-H", "Accept: application/vnd.github.raw", UV_DOCKERFILE],
            capture_output=True,
            check=True,
            encoding="utf-8",
        ).stdout
    except subprocess.CalledProcessError as error:
        if UNREADABLE in error.stderr:
            return None
        raise


def bundled_uv() -> str | None:
    """Read the uv version `dependabot-core`'s updater runs off `dockerfile()`.

    Kept apart from the fetch so a caller can tell "the file could not
    be read" from "the file was read and held no pin" -- the second is
    not the first, and skipping both alike would hide the day the
    Dockerfile changed shape out from under the regex.

    :returns: the version dotted as `required-version` is, or `None`
        where `dockerfile()` did, or where its text held no
        `astral-sh/uv:` pin.
    """
    text = dockerfile()
    if text is None:
        return None
    match = re.search(r"astral-sh/uv:(?P<version>[0-9]+(?:\.[0-9]+)*)", text)
    return match["version"] if match else None


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


def project_table(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    """Return the `[project]` table of a tree that declares one, unscoped.

    Unlike `distribution`, no build backend is required: the `authors`
    rule reaches every file that declares the table, whether or not it
    builds anything.

    :param repository: the repository's name.
    :param pyprojects: the parsed files.
    :returns: the table, or `None` where the tree has no `pyproject.toml`
        at all, or one with no `[project]` table -- two different
        reasons a caller has nothing to ask.
    """
    document = pyprojects.get(repository)
    if document is None:
        return None
    project = document.get("project")
    return project if isinstance(project, dict) else None


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


def ruff_selects(lint: dict[str, Any], family: str) -> bool:
    """Say whether a `[tool.ruff.lint]` table turns a family's rules on.

    Section 5 leaves a tree two shapes for `select`: naming the family,
    or naming `"ALL"`, which turns every family on at once and is
    `.github`'s own choice. A test asking whether one family runs reads
    either.

    :param lint: the table `ruff_lint` returns.
    :param family: the family's code, spelled as `select` would hold it.
    :returns: whether `select` turns the family on, `ignore` unread: a
        family `select` turns on and `ignore` empties of every one of
        its rules is a question of the config's effect and not of this
        one key, and no test here asks it.
    """
    select = lint.get("select", [])
    return family in select or "ALL" in select


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


@pytest.mark.tier(Tier.PYTHON)
def test_the_uv_floor_is_not_above_what_dependabot_bundles(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 1: every tree with a lock names a floor, capped at the ceiling.

    A floor above the pin in `dependabot-core`'s `uv/Dockerfile` makes
    every lock update the `uv` ecosystem attempts a silent no-op --
    `tool_version_not_supported`, with no pull request and nothing red
    -- so a repository past this line is one whose Dependabot uv updates
    are not running, and finds out from no error anywhere. A tree with
    no floor at all is not exempt from that failure, only unmeasured
    against it: section 1 owes the key to every tree that commits
    `uv.lock`, so a repository holding one and naming none fails here
    rather than skipping past the question.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: the parsed files.
    """
    declared = (
        parsed(repository, pyprojects)
        .get("tool", {})
        .get("uv", {})
        .get("required-version")
    )
    if declared is None:
        assert not (trees[repository] / "uv.lock").is_file(), (
            f"{repository} commits uv.lock and names no [tool.uv] "
            "required-version; "
            + by_hand(repository, "grep -n required-version pyproject.toml")
        )
        pytest.skip(f"{repository} names no [tool.uv] required-version")
    text = dockerfile()
    if text is None:
        pytest.skip(f"could not read {UV_DOCKERFILE}")
    bundled = bundled_uv()
    if bundled is None:
        pytest.skip(f"{UV_DOCKERFILE} holds no astral-sh/uv: pin to read")
    match = FLOOR.match(declared)
    assert match, (
        f"required-version is {declared!r}, not a bare >=X.Y.Z floor; "
        + by_hand(repository, "grep -n required-version pyproject.toml")
    )
    floor = tuple(int(part) for part in match["version"].split("."))
    ceiling = tuple(int(part) for part in bundled.split("."))
    assert floor <= ceiling, (
        f"required-version is {declared!r}, above the uv dependabot-core"
        f" bundles ({bundled}), so {repository}'s uv-driven Dependabot"
        " updates are not running; "
        + by_hand(repository, "grep -n required-version pyproject.toml")
        + "; dependabot-core's own pin: gh api -H"
        " 'Accept: application/vnd.github.raw' " + UV_DOCKERFILE
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
def test_the_name_normalizes_to_the_repository(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 3: the repository is named after the distribution, hyphenated.

    PEP 503 folds `-`, `_` and `.` in a distribution name to a single
    `-` before comparing, so a `name` spelled with an underscore
    compares equal to the repository's hyphenated spelling.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    project = distribution(repository, pyprojects)
    command = by_hand(repository, "grep -n '^name = ' pyproject.toml")
    declared = project.get("name")
    assert isinstance(declared, str), f"name is {declared!r}; " + command
    normalized = RUNS.sub("-", declared).lower()
    assert normalized == repository, f"name normalizes to {normalized!r}; " + command


@pytest.mark.tier(Tier.PYTHON)
def test_the_name_is_the_canonical_spelling(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 3: `name` itself takes PEP 503's canonical hyphen.

    The test above folds the family together before comparing, which
    answers whether the repository and the distribution agree and
    nothing about which member of the family `name` itself picked;
    this asks that question directly.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    project = distribution(repository, pyprojects)
    command = by_hand(repository, "grep -n '^name = ' pyproject.toml")
    declared = project.get("name")
    assert isinstance(declared, str), f"name is {declared!r}; " + command
    canonical = RUNS.sub("-", declared).lower()
    assert declared == canonical, f"name is {declared!r}, not {canonical!r}; " + command


@pytest.mark.tier(Tier.PYTHON)
def test_the_licence_is_an_expression_with_its_files(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 3: PEP 639's two keys, the SPDX string and the two names.

    A tree declaring the deprecated table, or no key at all, passes
    `classifiers_test.py` -- which reads `license` to refuse the
    classifier beside an expression and so asks nothing of a tree that
    has none -- and is refused here.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    project = distribution(repository, pyprojects)
    command = by_hand(repository, "grep -n '^license' pyproject.toml")
    expression = project.get("license")
    assert isinstance(expression, str), f"license is {expression!r}; " + command
    files = project.get("license-files")
    named = set(files) if isinstance(files, list) else files
    assert named == {"LICENSE", "AUTHORS.md"}, f"license-files is {files!r}; " + command


def test_authors_names_the_copyright_s_collective(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 3: `authors` names what `COPYRIGHT` names, wherever declared.

    Unscoped by tier and by build backend both -- `project_table` asks
    for the `[project]` table without `distribution`'s requirement of a
    build backend, because the rule this asks reaches `bbt` and
    `.github` too, neither of which builds anything. A tree with no
    `pyproject.toml` at all (`portanode`) and one with a `pyproject.toml`
    but no `[project]` table are both skipped: the rule has no subject
    in either.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: the parsed files.
    """
    project = project_table(repository, pyprojects)
    if project is None:
        reason = (
            "has no pyproject.toml"
            if pyprojects.get(repository) is None
            else "declares no [project] table"
        )
        pytest.skip(f"{repository} {reason}")
    command = by_hand(repository, "grep -n '^authors' pyproject.toml")
    authors = project.get("authors")
    assert isinstance(authors, list), f"authors is {authors!r}; " + command
    assert len(authors) == 1, f"authors is {authors!r}, not a single entry; " + command
    entry = authors[0]
    declared = entry.get("name") if isinstance(entry, dict) else None
    expected = collective(trees[repository] / "COPYRIGHT")
    assert declared == expected, (
        f"authors names {declared!r}, not COPYRIGHT's {expected!r}; " + command
    )


def test_every_declared_authors_email_agrees(
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 3: every tree declaring `authors` answers the same address.

    No literal to compare against: `COPYRIGHT` carries the collective's
    name and nothing carries its address, so the declaring trees are
    each other's only authority, and one changed alone is what this
    catches.

    An address a tree does not declare is its own group rather than a
    tree dropped from the comparison: a suite that skips what it cannot
    read answers the same green whether the trees agree or none of them
    says anything, and the second is what this test exists to refuse.
    An empty comparison fails for the same reason.

    :param pyprojects: the parsed files.
    """
    by_address: dict[str | None, list[str]] = {}
    for repository, document in sorted(pyprojects.items()):
        project = document.get("project")
        if not isinstance(project, dict):
            continue
        authors = project.get("authors")
        if authors is None:
            continue
        entries = authors if isinstance(authors, list) else []
        addresses = tuple(
            entry.get("email") if isinstance(entry, dict) else None for entry in entries
        ) or (None,)
        for address in addresses:
            by_address.setdefault(address, []).append(repository)
    silent = by_address.pop(None, [])
    assert not silent, f"authors declares a name and no address: {', '.join(silent)}"
    assert by_address, "no tree declares an authors address: nothing here is measured"
    grouped = {email: ", ".join(names) for email, names in by_address.items()}
    assert len(by_address) == 1, f"authors email is not the same everywhere: {grouped}"


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
    assert ruff_selects(lint, "CPY"), "CPY is not selected; " + command
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
    assert ruff_selects(lint, "W"), "W is not selected; " + command
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
    assert ruff_selects(lint, "D"), "D is not selected; " + command
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
