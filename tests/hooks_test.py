# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The hooks section 4 says every lint gate runs, read off each gate.

`.pre-commit-config.yaml` is the lint gate, and a hook it does not name
does not run: a hook commented out with a reason beside it is read here
exactly as one never added, which is the point -- section 4 lists these
without a condition, so where a tree declines one the finding is either
the tree's or the section's, and a `BACKLOG` row is where that finding
is recorded.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import Tier, by_hand, tracked

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

CONFIG = ".pre-commit-config.yaml"

SYNTAX = {
    "check-yaml": ("*.yml", "*.yaml"),
    "check-json": ("*.json", "*.ipynb"),
    "check-toml": ("*.toml",),
    "pretty-format-json": ("*.json", "*.ipynb"),
}
"""Section 4's *syntax* bullet, each hook against the files it reads.

The pathspecs are `identify`'s tags as git sees them -- a notebook is
tagged `json` and a `.jsonc` is tagged nothing -- because the bullet is
conditional on the tree through section 4's *file checking itself*:
`check-hooks-apply` refuses a hook that matches nothing, so a syntax
hook is owed exactly where the tree tracks its file type.
"""

LOCAL = (
    "toml-comment-width",
    "decoded-subprocess-encoding",
    "reasonless-coverage-pragma",
    "local-link-prefix",
    "no-hyphen-at-end-of-line",
    "unquoted-placeholder",
    "check-changelog",
)
"""Section 4's *The local hooks*, each with a subject in any Python tree.

mypy is the one bullet of that list not named here: it is
`test_the_gate_runs_mypy`'s subject below, section 6 asking for it by name.
"""

MYPY = ("mypy", "mirrors-mypy")
"""The two shapes section 4 gives the mypy hook: local, or the mirror.

The mirror's hook id is `mypy` as well; the repository url is what tells
the two apart, and either answers section 6.
"""

CHANGELOG_HOOK = "check-changelog"
"""The local hook whose keys section 4 states one at a time.

Section 14 has a part of a repository-owned file held against the
standard rather than against the copies of it in the other trees, and
this is the part that decision was settled on.
"""

STATED = {
    "entry": "python3 .github/scripts/check_changelog.py",
    "language": "system",
    "pass_filenames": False,
    "always_run": True,
}
"""What section 4's `check-changelog` bullet says that hook is, by key.

Read into a mapping rather than left to a comparison between the trees:
copies compared with each other agree while each of them is wrong, which
is what `REFUSED` below is an instance of.
"""

UNFILTERED = "files"
"""The key section 4 says that hook carries none of.

Read as a finding of its own rather than folded into `STATED`: a key
absent is what the section asks for here, and a mapping is no place to
say that. The reason a filter is refused is section 4's.
"""

REFUSED = {
    "id": CHANGELOG_HOOK,
    "entry": "python3 .github/scripts/check_changelog.py",
    "language": "system",
    "pass_filenames": False,
    "files": r"^(CHANGELOG\.md|\.github/scripts/check_changelog\.py)$",
}
"""The stanza btclib-org/.github#1138 refuses, as a literal.

Every gate answers section 4 today, so a check reading the trees alone
is green however its reading behaves; this is what the reading is asked
of instead. The keys are the ones every tree carries at the parent of
its port of that issue, a filter standing where `always_run:` belongs,
and `name:` is left out as a key nothing here reads. A comparison of
the copies with each other passes on it, every copy carrying it there.
"""


def hooks(repository: str, trees: dict[str, Path]) -> list[dict[str, Any]]:
    """Every hook a repository's lint gate names, in file order.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the hook mappings, each with its repository url under `repo`.
    :raises FileNotFoundError: where the tree has no lint gate at all,
        section 4 naming the file as every repository's.
    """
    path = trees[repository] / CONFIG
    if not path.is_file():
        msg = f"{repository} has no {CONFIG}; " + by_hand(repository, f"ls {CONFIG}")
        raise FileNotFoundError(msg)
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [
        {**hook, "repo": entry["repo"]}
        for entry in parsed.get("repos", [])
        for hook in entry.get("hooks", [])
    ]


def ids(repository: str, trees: dict[str, Path]) -> set[str]:
    """Return the ids of every hook a repository's lint gate names.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the ids.
    """
    return {hook["id"] for hook in hooks(repository, trees)}


def test_the_syntax_hooks_run(repository: str, trees: dict[str, Path]) -> None:
    """Section 4's *syntax* bullet, wherever the tree has the file type.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    running = ids(repository, trees)
    missing = sorted(
        hook
        for hook, patterns in SYNTAX.items()
        if hook not in running and tracked(trees[repository], *patterns)
    )
    assert not missing, (
        f"syntax hooks the gate does not run over files it tracks: {missing}; "
        + by_hand(
            repository,
            f"grep -nE '^ *- id: ({'|'.join(SYNTAX)})' {CONFIG};"
            " git ls-files '*.json' '*.ipynb' '*.toml' '*.yml' '*.yaml'",
        )
    )


@pytest.mark.tier(Tier.PYTHON)
def test_name_tests_test_runs_at_its_default(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Sections 4 and 7: `name-tests-test` at its default, `*_test.py`.

    The default is what the hook enforces when given no argument, and
    section 7 makes it the one spelling of the organization rather than
    the only one pytest collects, so an argument selecting the other
    collection pattern is a divergence the hook's presence does not
    answer. Asked only of a tree with a `tests/` directory: the
    hook matches nothing elsewhere, and `check-hooks-apply` would refuse
    it there.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    if not (trees[repository] / "tests").is_dir():
        pytest.skip(f"{repository} has no tests/ directory")
    found = [
        hook for hook in hooks(repository, trees) if hook["id"] == "name-tests-test"
    ]
    command = by_hand(repository, f"grep -n -A1 '^ *- id: name-tests-test' {CONFIG}")
    assert found, "name-tests-test is not in the gate; " + command
    arguments = [argument for hook in found for argument in hook.get("args", [])]
    assert not arguments, (
        f"name-tests-test is given {arguments}, not its default; " + command
    )


@pytest.mark.tier(Tier.PYTHON)
def test_the_local_hooks_run(repository: str, trees: dict[str, Path]) -> None:
    """Section 4's local hooks with a subject in every Python tree.

    `toml-comment-width` has one wherever there is a `pyproject.toml`, which
    is what the tier says there is; section 3 names it as what holds that
    file's comments to 80 columns, and section 4 says the pattern reads them
    as bytes.
    `decoded-subprocess-encoding` has one wherever a child process is
    decoded, and a tree that decodes none today is the tree in which the
    first locale-decoded call is refused by nothing. Not spelled as the
    keyword here: the hook is a pygrep over every Python line, a
    docstring's included, and this one is in its own file set.
    `reasonless-coverage-pragma` has one wherever there is a Python file
    at all, `types: [python]` rather than a narrower set: a tree with no
    site today is the tree in which the first reasonless one is refused
    by nothing, same as the hook above.
    `local-link-prefix` has one wherever there is a markdown file,
    `types: [markdown]`, and section 2's table owes every tier a
    `README.md`.
    `no-hyphen-at-end-of-line` has one wherever there is a markdown file
    too, markdown being among the types every gate gives it; what else a
    gate gives it is btclib-org/.github#921's question and not this test's.
    `unquoted-placeholder` has one wherever there is a markdown file,
    `types: [markdown]` rather than a narrower set: a tree with no
    quoted placeholder today is the tree in which the first one pasted
    is refused by nothing, same as `decoded-subprocess-encoding` and
    `reasonless-coverage-pragma` above.
    `check-changelog` has one wherever there is a `CHANGELOG.md`, which
    section 2's table owes every tier.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    missing = sorted(set(LOCAL) - ids(repository, trees))
    assert not missing, f"local hooks the gate does not run: {missing}; " + by_hand(
        repository, f"grep -oE 'id: ({'|'.join(LOCAL)})' {CONFIG}"
    )


@pytest.mark.tier(Tier.PYTHON)
def test_the_gate_runs_mypy(repository: str, trees: dict[str, Path]) -> None:
    """Section 6: configured is not enforced, and the gate runs mypy.

    Either of section 4's two shapes answers. `strict = true` with no
    hook running it is the finding section 15 names on its own: the
    strictness is declared and the code is unchecked.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    runs = [
        hook["id"]
        for hook in hooks(repository, trees)
        if hook["id"] in MYPY or hook["repo"].endswith("/mirrors-mypy")
    ]
    assert runs, "no hook runs mypy; " + by_hand(
        repository, f"grep -n 'mirrors-mypy\\|id: mypy' {CONFIG}"
    )


def departures(hook: dict[str, Any]) -> list[str]:
    """List where a hook mapping says something other than section 4 does.

    :param hook: a hook as the gate's yaml gives it.
    :returns: one line per key that differs, empty where none does.
    """
    found = [
        f"{key}: {hook.get(key)!r} rather than {value!r}"
        for key, value in STATED.items()
        if hook.get(key) != value
    ]
    if UNFILTERED in hook:
        found.append(f"{UNFILTERED}: {hook[UNFILTERED]!r}, where section 4 has none")
    return found


def test_check_changelog_says_what_section_4_says(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 4's `check-changelog` keys, read off each tree's gate.

    The hook is resolved by its `id`, so where a gate keeps it is not
    read as drift; that it runs ahead of `markdownlint-cli2` is that
    section's separate rule. A tree whose gate names no such hook is
    `test_the_local_hooks_run`'s finding where the tier binds it, and
    this cell reports nothing about it: one finding to a cell.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    found = [hook for hook in hooks(repository, trees) if hook["id"] == CHANGELOG_HOOK]
    if not found:
        pytest.skip(f"{repository}'s gate names no {CHANGELOG_HOOK} hook")
    drifted = [line for hook in found for line in departures(hook)]
    assert not drifted, (
        f"{CHANGELOG_HOOK} says what section 4 does not: {drifted}; "
        + by_hand(repository, f"grep -n -A6 '^ *- id: {CHANGELOG_HOOK}' {CONFIG}")
    )


def test_a_gate_that_had_drifted_would_be_reported() -> None:
    """The cell above is green on gates that agree, however it reads.

    Asked of the literal `REFUSED` names, and of each of the two
    findings that literal carries: a key section 4 states and the hook
    does not, and a key the hook states and section 4 gives it none of.
    """
    refused = departures(REFUSED)
    assert any("always_run" in line for line in refused), (
        f"{REFUSED} read as carrying always_run: either a key section 4"
        " states is no longer read, or the literal wants another"
    )
    assert any(line.startswith(f"{UNFILTERED}:") for line in refused), (
        f"{REFUSED} read as carrying no {UNFILTERED}: either the key"
        " section 4 gives this hook none of is no longer read, or the"
        " literal wants another"
    )
