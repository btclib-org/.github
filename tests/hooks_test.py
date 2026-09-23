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

One hook is read for its pin as well: `uv-lock` runs the uv its `rev:`
names, so section 1's floor is what that pin answers to.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import ORG, SELF, Tier, by_hand, tracked
from .pyproject_test import FLOOR, parsed

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

UV_LOCK = "uv-lock"
"""Section 4's packaging hook, which runs the uv its block pins.

That uv is the hook's own and not the project's, so a floor above it
leaves the hook exiting rather than locking, and the lint gate red.
"""

UV_PRE_COMMIT = "/uv-pre-commit"
"""The end of the url of the block that carries the pin.

A `rev:` is the block's key and not the hook's, so it is taken from the
block the hook was read out of: the `rev:` nearest the id in the file
is a neighbouring block's as readily as this one's.
"""

RELEASE = re.compile(r"^[0-9]+(?:\.[0-9]+)*$")
"""The dotted release a pin of that block names, `0.12.17`.

`uv-pre-commit` tags a release per uv version and carries a `v`-prefixed
tag of its own as well, `v0.1.24`, so a pin outside this shape names no
uv to compare and is this module's finding rather than a skip: the pin
is what it reads.
"""

CHANGELOG_HOOK = "check-changelog"
"""The local hook whose keys section 4 states one at a time.

Section 14 has a part of a repository-owned file held against the
standard rather than against the copies of it in the other trees, and
this is the part that decision was settled on.
"""

STATED = {
    "entry": ".github/scripts/check_changelog.py",
    "language": "script",
    "pass_filenames": False,
    "always_run": True,
}
"""What section 4's `check-changelog` bullet says that hook is, by key.

These are the manifest's own keys, so they read the same in the tree
that serves the hook and in the tree that takes it. `SERVED`, `PIN` and
`COUNT` below are the three the two shapes differ on.

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

SERVED = f"https://github.com/{ORG}/{SELF}"
"""The repository section 4 says the hook is taken from.

Asked of every tree but that one: a hook repository pinning itself
would gate a branch on the revision the pin names rather than on the
branch, which is why section 4 leaves `.github`'s own copy `local`.
"""

PIN = re.compile(r"^[0-9a-f]{40}$")
"""The `rev:` shape section 4 asks of a tree taking that hook.

A commit and not a tag, this repository cutting none, and forty hex
characters is what `pinned-rev` accepts and what `autoupdate` moves by
`git rev-parse FETCH_HEAD`.
"""

COUNT = "--grandfathered"
"""The flag section 4 says the stanza's `args:` opens with.

The number behind it is that repository's own history and is not read
against anything here: what this asks is that the flag is passed and
carries a number, a stanza without one measuring against the script's
default instead.
"""

REFUSED = {
    "id": CHANGELOG_HOOK,
    "repo": "local",
    "rev": None,
    "entry": "python3 .github/scripts/check_changelog.py",
    "language": "system",
    "pass_filenames": False,
    "files": r"^(CHANGELOG\.md|\.github/scripts/check_changelog\.py)$",
}
"""A stanza carrying every finding this module reads, as a literal.

A check reading the trees alone is green wherever the gates agree and
are wrong together, which is what this is asked of instead. `repo` and
`rev` are what `hooks()` gives a hook read out of a `local` block, the
entry and the language are the shape a copy in the tree wants, the
filter stands where `always_run:` belongs -- btclib-org/.github#1138 --
and there is no `args:`. `name:` is left out as a key nothing here reads.
"""


def hooks(repository: str, trees: dict[str, Path]) -> list[dict[str, Any]]:
    """Every hook a repository's lint gate names, in file order.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the hook mappings, each with the url and the pin of the
        block it was read out of, under `repo` and `rev`.
    :raises FileNotFoundError: where the tree has no lint gate at all,
        section 4 naming the file as every repository's.
    """
    path = trees[repository] / CONFIG
    if not path.is_file():
        msg = f"{repository} has no {CONFIG}; " + by_hand(repository, f"ls {CONFIG}")
        raise FileNotFoundError(msg)
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [
        {**hook, "repo": entry["repo"], "rev": entry.get("rev")}
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


PYROMA = "pyroma"
"""Section 4's packaging hook that reads a distribution's metadata."""

PYROMA_STATED = {
    "repo": "local",
    "entry": "uv run --locked --only-group check pyroma",
    "language": "system",
    "args": ["-d", "--min=10", "."],
    "pass_filenames": False,
    "always_run": True,
}
"""What section 4's *packaging* bullet says that hook is, by key.

`repo` is among them because the shape is the whole point: `autoupdate`
rewrites the `rev:` of every block but `local` and `meta`, so a hook
declared anywhere else is the one this refuses however its other keys
read. The rest are the upstream hook's own definition, which a local
hook states rather than inherits, with `entry` naming the group the
version comes from.
"""

PYROMA_REFUSED = {
    "id": PYROMA,
    "repo": "https://github.com/regebro/pyroma",
    "rev": "5.0.1",
    "additional_dependencies": ["uv_build>=0.12.0,<0.13"],
}
"""The stanza a gate carries where the hook is still `autoupdate`'s.

A literal, for the reason `REFUSED` above is one: every gate answering
section 4 would leave a check read off the trees green however its
reading behaved. `entry` and `language` are absent here because an
upstream block states neither, which is two of the findings this owes.
"""

CHECK_SDIST = "check-sdist"
"""Section 4's packaging hook that diffs the sdist against what git tracks."""

PACKAGING = (UV_LOCK, PYROMA, CHECK_SDIST)
"""Section 4's *packaging* bullet, each hook with a subject of its own.

`uv-lock` moves `uv.lock`, so it is owed wherever that file is
committed. `pyroma` and `check-sdist` both build the project through
the backend `[build-system]` names -- section 12's own paragraph on the
two hooks that do -- so the pair shares one subject: whether the tree
declares a build backend at all, which is `pyproject_test.py`'s
`distribution` skips on, read here as a condition rather than a second
one.
"""


def owed(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> dict[str, bool]:
    """Say, per packaging hook, whether a tree has a subject for it.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :param pyprojects: the parsed files.
    :returns: each hook id of `PACKAGING` against whether the tree owes it.
    """
    distributes = "build-system" in parsed(repository, pyprojects)
    return {
        UV_LOCK: bool(tracked(trees[repository], "uv.lock")),
        PYROMA: distributes,
        CHECK_SDIST: distributes,
    }


def missing_packaging_hooks(running: set[str], subjects: dict[str, bool]) -> list[str]:
    """Return the packaging hooks a tree owes and its gate does not run.

    :param running: the hook ids the tree's gate names.
    :param subjects: each hook id against whether the tree owes it,
        `owed`'s shape.
    :returns: the ids the tree owes and does not run, sorted.
    """
    return sorted(
        hook for hook, is_owed in subjects.items() if is_owed and hook not in running
    )


@pytest.mark.tier(Tier.PYTHON)
def test_the_packaging_hooks_run(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 4's *packaging* bullet, each hook against its own subject.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: the parsed files.
    """
    missing = missing_packaging_hooks(
        set(ids(repository, trees)), owed(repository, trees, pyprojects)
    )
    assert not missing, f"packaging hooks the gate does not run: {missing}; " + by_hand(
        repository, f"grep -oE 'id: ({'|'.join(PACKAGING)})' {CONFIG}"
    )


def test_a_missing_packaging_hook_would_be_reported() -> None:
    """The cell above is green on a gate that runs every hook it owes.

    Each hook is asked both ways a wrong reading would be green on:
    running and owed, which a comparison blind to `running` would still
    report missing; and owed with nothing running, which a comparison
    blind to `subjects` would report on a hook nothing owes.
    """
    for hook in PACKAGING:
        owed_only_this = {h: h == hook for h in PACKAGING}
        assert missing_packaging_hooks({hook}, owed_only_this) == [], (
            f"{hook} running and owed is reported missing"
        )
        assert missing_packaging_hooks(set(), owed_only_this) == [hook], (
            f"{hook} owed and not running is not reported"
        )
    unowed = dict.fromkeys(PACKAGING, False)
    assert missing_packaging_hooks(set(), unowed) == [], (
        "a hook nothing owes is reported missing"
    )


def stated_departures(hook: dict[str, Any], stated: dict[str, Any]) -> list[str]:
    """List where a hook mapping says something other than a section does.

    The mapping to hold it against is the caller's, section 4 stating
    the keys of more than one hook and each bullet stating its own: a
    default here would answer for whichever hook was written first.

    :param hook: a hook as the gate's yaml gives it, `hooks()`'s shape.
    :param stated: the keys that section states, against their values.
    :returns: one line per key that differs, empty where none does.
    """
    return [
        f"{key}: {hook.get(key)!r} rather than {value!r}"
        for key, value in stated.items()
        if hook.get(key) != value
    ]


def served_departures(hook: dict[str, Any]) -> list[str]:
    """List where a hook is not taken from the repository that serves it.

    :param hook: a hook as the gate's yaml gives it, `hooks()`'s shape.
    :returns: one line per finding, empty where the stanza agrees.
    """
    found = []
    if hook.get("repo") != SERVED:
        found.append(f"repo: {hook.get('repo')!r} rather than {SERVED!r}")
    rev = hook.get("rev")
    if not isinstance(rev, str) or PIN.match(rev) is None:
        found.append(f"rev: {rev!r}, where section 4 asks for a commit sha")
    return found


def counted_departures(hook: dict[str, Any]) -> list[str]:
    """List where a stanza's `args:` is not the count section 4 asks for.

    :param hook: a hook as the gate's yaml gives it.
    :returns: one line per finding, empty where the flag carries a number.
    """
    args = [str(argument) for argument in hook.get("args", [])]
    # the flag and its number, which is what `args:` holds and all it
    # holds -- a length read as a magic value is the shape of the list
    if args[:1] != [COUNT] or len(args) != 2 or not args[1].isdigit():  # noqa: PLR2004
        return [f"args: {args!r} rather than {COUNT} and a number"]
    return []


def departures(hook: dict[str, Any], repository: str) -> list[str]:
    """List where a hook mapping says something other than section 4 does.

    :param hook: a hook as the gate's yaml gives it.
    :param repository: the repository the gate belongs to, which decides
        whether the stanza is read for the repository it is served from.
    :returns: one line per key that differs, empty where none does.
    """
    found = stated_departures(hook, STATED)
    if UNFILTERED in hook:
        found.append(f"{UNFILTERED}: {hook[UNFILTERED]!r}, where section 4 has none")
    found.extend(counted_departures(hook))
    if repository != SELF:
        found.extend(served_departures(hook))
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
    drifted = [line for hook in found for line in departures(hook, repository)]
    assert not drifted, (
        f"{CHANGELOG_HOOK} says what section 4 does not: {drifted}; "
        + by_hand(repository, f"grep -n -A6 '^ *- id: {CHANGELOG_HOOK}' {CONFIG}")
    )


def test_a_gate_that_had_drifted_would_be_reported() -> None:
    """The cell above is green on gates that agree, however it reads.

    Asked of the literal `REFUSED` names, once for each finding it
    carries: a key section 4 states and the hook does not, a key the
    hook states and section 4 gives it none of, a stanza declared where
    the hook is not served from, a `rev:` that is no commit, and an
    `args:` naming no count. `SELF` is asked separately, that tree
    being the one the last two are not read of.
    """
    refused = departures(REFUSED, "btclib")
    assert any("always_run" in line for line in refused), (
        f"{REFUSED} read as carrying always_run: either a key section 4"
        " states is no longer read, or the literal wants another"
    )
    assert any(line.startswith(f"{UNFILTERED}:") for line in refused), (
        f"{REFUSED} read as carrying no {UNFILTERED}: either the key"
        " section 4 gives this hook none of is no longer read, or the"
        " literal wants another"
    )
    assert any(line.startswith("repo:") for line in refused), (
        f"{REFUSED} read as taken from {SERVED}: either the key that"
        " says where the hook comes from is no longer read, or the"
        " literal wants another"
    )
    assert any(line.startswith("rev:") for line in refused), (
        f"{REFUSED} read as pinned at a commit: either the pin is no"
        " longer read, or the literal wants another"
    )
    assert any(line.startswith("args:") for line in refused), (
        f"{REFUSED} read as naming a count: either the flag is no"
        " longer read, or the literal wants another"
    )
    assert not any(
        line.startswith(("repo:", "rev:")) for line in departures(REFUSED, SELF)
    ), f"{SELF} is read for a repository it serves the hook from"
    agreeing = {
        "id": CHANGELOG_HOOK,
        "repo": SERVED,
        "rev": "0" * 40,
        "args": [COUNT, "7"],
        **STATED,
    }
    assert departures(agreeing, "btclib") == [], (
        f"{agreeing} is read as drift from the keys it is built of"
    )


def test_pyroma_says_what_section_4_says(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 4's `pyroma` keys, read off each tree's gate.

    The hook is resolved by its `id`, as the cell above resolves
    `check-changelog`: where a gate keeps the stanza is no drift in it.
    A tree whose gate names no such hook is
    `test_the_packaging_hooks_run`'s finding where the tree owes one,
    and this reports nothing about it: one finding to a cell.

    What it cannot ask is the version the entry resolves to. That is
    the `check` group's bound, which no key of this file carries and
    which section 4 leaves to whoever writes the bound.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    found = [hook for hook in hooks(repository, trees) if hook["id"] == PYROMA]
    if not found:
        pytest.skip(f"{repository}'s gate names no {PYROMA} hook")
    drifted = [
        line for hook in found for line in stated_departures(hook, PYROMA_STATED)
    ]
    assert not drifted, f"{PYROMA} says what section 4 does not: {drifted}; " + by_hand(
        repository, f"grep -n -B8 -A6 '^ *- id: {PYROMA}' {CONFIG}"
    )


def test_a_pyroma_hook_that_had_drifted_would_be_reported() -> None:
    """The cell above is green on a gate that agrees, however it reads.

    Asked of the literal `PYROMA_REFUSED` for the two findings that
    stanza carries -- the block it is declared in, and the entry an
    upstream block has none of -- and of the stated keys themselves,
    which a comparison inverted somewhere would report as drift.
    """
    refused = stated_departures(PYROMA_REFUSED, PYROMA_STATED)
    assert any(line.startswith("repo:") for line in refused), (
        f"{PYROMA_REFUSED} read as declared locally: either the key the"
        " shape turns on is no longer read, or the literal wants another"
    )
    assert any(line.startswith("entry:") for line in refused), (
        f"{PYROMA_REFUSED} read as carrying an entry: either the key"
        " naming the group is no longer read, or the literal wants another"
    )
    agreeing = {"id": PYROMA, **PYROMA_STATED}
    assert stated_departures(agreeing, PYROMA_STATED) == [], (
        f"{agreeing} is read as drift from the keys it is built of"
    )


def version(release: str) -> tuple[int, ...]:
    """Order a dotted release by its parts rather than by its text.

    :param release: the release, as a pin or a floor spells it.
    :returns: the parts as numbers, so that `0.12.9` sorts below
        `0.12.17`, where their text sorts it above.
    """
    return tuple(int(part) for part in release.split("."))


def admitted(rev: str, declared: str) -> bool | None:
    """Say whether the uv a pin bundles is one a floor admits.

    At least the floor, and not an equality: `autoupdate` moves the pin
    on its own schedule while the floor waits on the ceiling section 1
    sets it by, so a pin above the floor is the ordinary state and
    equality here would be red at each of those moves.

    :param rev: the pin of the block the hook was read out of.
    :param declared: the tree's `[tool.uv] required-version`.
    :returns: whether the floor admits that uv, or `None` where the
        floor is not the bare `>=` shape section 1 asks for, which is
        `test_the_uv_floor_is_what_dependabot_bundles`'s finding.
    """
    floor = FLOOR.match(declared)
    if floor is None:
        return None
    return version(rev) >= version(floor["version"])


def bundling(repository: str, trees: dict[str, Path]) -> list[dict[str, Any]]:
    """Return the `uv-lock` hooks a gate takes from `uv-pre-commit`.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the hooks, each carrying its own block's pin under `rev`.
    """
    return [
        hook
        for hook in hooks(repository, trees)
        if hook["id"] == UV_LOCK and str(hook["repo"]).endswith(UV_PRE_COMMIT)
    ]


def floor_of(repository: str, pyprojects: dict[str, dict[str, Any]]) -> str | None:
    """Return the uv floor a tree declares.

    :param repository: the repository's name.
    :param pyprojects: the parsed files.
    :returns: `[tool.uv] required-version`, or `None` where the tree
        names none or has no `pyproject.toml` at all.
    """
    declared = (
        pyprojects.get(repository, {})
        .get("tool", {})
        .get("uv", {})
        .get("required-version")
    )
    return None if declared is None else str(declared)


@pytest.mark.tier(Tier.PYTHON)
def test_the_uv_lock_hook_bundles_a_uv_the_floor_admits(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 1: the `uv-lock` pin is at or above the tree's uv floor.

    The hook runs the uv its pin names, so a floor above that uv makes
    it exit rather than lock -- `Required uv version ... does not match
    the running version ...` -- and the lint check the tree requires is
    red until one of the two moves. A tree carrying one of the pair
    alone is skipped: whether it owes the floor is
    `test_the_uv_floor_is_what_dependabot_bundles`'s question, and
    whether it owes the hook is section 4's packaging bullet.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: the parsed files.
    """
    pinned = bundling(repository, trees)
    if not pinned:
        pytest.skip(f"{repository}'s gate takes no {UV_LOCK} from uv-pre-commit")
    declared = floor_of(repository, pyprojects)
    if declared is None:
        pytest.skip(f"{repository} names no [tool.uv] required-version")
    reading = by_hand(
        repository,
        f"grep -n -B3 'id: {UV_LOCK}' {CONFIG};"
        " grep -n required-version pyproject.toml",
    )
    for hook in pinned:
        rev = str(hook["rev"])
        assert RELEASE.match(rev), (
            f"{UV_LOCK} is pinned at {rev!r}, which names no uv release; " + reading
        )
        verdict = admitted(rev, declared)
        if verdict is None:
            pytest.skip(f"{repository}'s required-version is {declared!r}")
        assert verdict, (
            f"{UV_LOCK} bundles uv {rev} and the floor is {declared!r}, so the"
            f" hook exits rather than locking in {repository}'s gate; " + reading
        )


def test_a_pin_below_the_floor_would_be_reported(
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """The cell above is green in every tree today, however it reads.

    Both ways it could be green having measured nothing are asked here:
    no tree carrying the pair for it to compare, and a comparison that
    reports nothing. The literals are the readings a wrong comparison
    is green on -- a pin under the floor read as text, where `0.12.9`
    sorts above `0.12.17`; a pin over the floor read as a finding,
    which is the equality that turns an autoupdate red; the pin the
    trees sit at, which a strict `>` would refuse; and a floor whose
    shape this module does not read.

    :param trees: the checkouts.
    :param pyprojects: the parsed files.
    """
    measured = [
        repository
        for repository in trees
        if bundling(repository, trees) and floor_of(repository, pyprojects) is not None
    ]
    assert measured, (
        "no tree carries both the pin and the floor, so the cell above compares nothing"
    )
    assert admitted("0.12.9", ">=0.12.17") is False, (
        "a pin below the floor reads as admitted: the releases are"
        " compared as text rather than as versions"
    )
    assert admitted("0.12.20", ">=0.12.17") is True, (
        "a pin above the floor reads as a finding: the comparison is an"
        " equality, and every autoupdate is red under it"
    )
    assert admitted("0.12.17", ">=0.12.17") is True, (
        "a pin at the floor reads as a finding: the comparison is"
        " strict, and the trees sitting at the floor are red under it"
    )
    assert admitted("0.12.17", ">=0.12.17,<0.13") is None, (
        "a floor this module does not read returns a verdict, where the"
        " shape is another cell's finding"
    )
