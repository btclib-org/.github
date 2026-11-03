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

`uv-lock` runs the uv its `rev:` names, so section 1's floor is what that
pin answers to.
"""

from __future__ import annotations

import copy
import fnmatch
import json
import re
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import ORG, ROOT, SELF, Tier, by_hand, gh_json, tracked
from .pyproject_test import FLOOR, FLOOR_BOUND, parsed
from .workflows_test import LOCAL as LOCAL_PREFIXES
from .workflows_test import calls_here, jobs, triggers, workflows

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
hook is owed exactly where the tree tracks its file type. `VSCODE`
below is the same conditioning applied to a `.json`-named path that is
not JSON.
"""

VSCODE = re.compile(r"^\.vscode/")
"""The `.vscode/` prefix, named once and checked against all four of
`SYNTAX`'s patterns rather than kept as a per-repository list of
exemptions. Every tree that tracks `.vscode/` excludes this prefix from
`check-json` and `pretty-format-json` -- alone in some, inside a larger
alternation with a tree's own other exclusions in others -- and a tree
that tracks no `.vscode/` carries no such exclusion because it has
nothing to exclude.

`.vscode/settings.json` and `.vscode/extensions.json` are jsonc: VSCode
reads a comment in its own configuration, and a json parser rejects the
file at the first one. A `.vscode/`-named path `tracked()` answers is
therefore not a file any syntax hook is asked to read, in a tree that
runs the hook or in one that does not, and does not decide whether the
hook is owed.
"""

LOCAL = (
    "toml-comment-width",
    "decoded-subprocess-encoding",
    "reasonless-coverage-pragma",
    "local-link-prefix",
    "readme-absolute-link",
    "no-hyphen-at-end-of-line",
    "unquoted-placeholder",
    "check-changelog",
)
"""Section 4's *The local hooks*, each with a subject in any Python tree.

mypy and `bare-sourcery-skip` are the bullets of that list not named
here: mypy is `test_the_gate_runs_mypy`'s subject below, section 6 asking
for it by name, and `bare-sourcery-skip` is held with the `sourcery` job
it guards, by `guard_departures`.
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
    "verbose": True,
}
"""What section 4's `check-changelog` bullet says that hook is, by key.

These are the manifest's keys, declared once in `MANIFEST` and restated
in `.github`'s own `local` stanza; a tree taking the hook restates none
of them, its stanza being `SERVED`, `PIN` and `COUNT` below.

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

MANIFEST = ".pre-commit-hooks.yaml"
"""The file section 4 says serves the hook, at the root of `SELF`."""

SERVED = f"https://github.com/{ORG}/{SELF}"
"""The repository section 4 says the hook is taken from.

Asked of every tree but that one: a hook repository pinning itself
would gate a branch on the revision the pin names rather than on the
branch, which is why section 4 leaves `.github`'s own copy `local`.
"""

PIN = re.compile(r"^[0-9a-f]{40}$")
"""The `rev:` shape section 4 asks of `check-changelog` and of `ACTIONLINT`.

A sha and not a tag name: the annotated tag's own object, which
`autoupdate --freeze` writes as `git rev-parse <tag>`. Forty hex
characters is what `pinned-rev` accepts.
"""

FROZEN = re.compile(
    r"^\s*rev: (?P<sha>[0-9a-f]{40}) # frozen: "
    r"(?P<tag>v\d{4}\.\d{1,2}\.\d{1,2})$"
)
"""The `rev:` line section 4 asks of a stanza taking `check-changelog`.

Read off the text: the `# frozen:` comment is YAML's, and the parser has
dropped it by the time `hooks()` returns. One space before the `#`, the
form prettier writes, where pre-commit writes two.
"""

REPO_LINE = re.compile(r"^\s*-\s*repo:\s*(?P<repo>\S+)\s*$")
"""The line that opens a block of the gate, naming its repository."""

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


def gate(repository: str, trees: dict[str, Path]) -> dict[str, Any]:
    """Read and parse a repository's lint gate.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the document, its `ci:` block and its `repos:` both.
    :raises FileNotFoundError: where the tree has no lint gate at all,
        section 4 naming the file as every repository's.
    """
    path = trees[repository] / CONFIG
    if not path.is_file():
        msg = f"{repository} has no {CONFIG}; " + by_hand(repository, f"ls {CONFIG}")
        raise FileNotFoundError(msg)
    document: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    return document


def flattened(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Every hook a parsed gate names, in file order.

    :param document: the gate, as `gate()` returns it.
    :returns: the hook mappings, each with the url and the pin of the
        block it was read out of, under `repo` and `rev`.
    """
    return [
        {**hook, "repo": entry["repo"], "rev": entry.get("rev")}
        for entry in document.get("repos", [])
        for hook in entry.get("hooks", [])
    ]


def hooks(repository: str, trees: dict[str, Path]) -> list[dict[str, Any]]:
    """Every hook a repository's lint gate names, in file order.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the hook mappings, as `flattened()` gives them.
    """
    return flattened(gate(repository, trees))


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
        if hook not in running
        and any(
            not VSCODE.match(path) for path in tracked(trees[repository], *patterns)
        )
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
    `CONTRIBUTING.md`; `readme-absolute-link` has the root `README.md`
    that hook excludes, which the table owes every tier as well.
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


SOURCERY_CONFIG = ".sourcery.yaml"
"""The file Sourcery reads, at the root of a tree."""

SOURCERY_CALLED = "reusable-sourcery.yml"
"""The workflow of this repository section 10 has a Python tree call."""

TURNED_OFF = {
    "reintroduce-else": "undoes superfluous-else-return",
    "use-fstring-for-concatenation": "folds a by_hand hint into the f-string it joins",
    "dont-import-test-modules": "refuses `from tests import`, the shared helpers' path",
    "assign-if-exp": "if-else-block-instead-of-if-exp",
    "comprehension-to-generator": "unnecessary-comprehension-in-call",
    "de-morgan": "negate-equal-op, negate-not-equal-op, double-negation, not-in-test",
    "equality-identity": "comparison-with-itself",
    "for-append-to-extend": "manual-list-copy, manual-list-comprehension",
    "identity-comprehension": "unnecessary-comprehension",
    "list-comprehension": "manual-list-comprehension",
    "merge-comparisons": "repeated-equality-comparison",
    "merge-duplicate-blocks": "if-with-same-arms",
    "merge-else-if-into-elif": "collapsible-else-if",
    "remove-redundant-fstring": "f-string-missing-placeholders",
    "remove-unnecessary-else": "superfluous-else-return",
    "simplify-boolean-comparison": "true-false-comparison",
}
"""The rules section 10 says `.sourcery.yaml` turns off, against the reason.

The reason is the ruff rule that turns each off, or another reason in
words. A rule ruff ships only in preview is no reason. A literal, for
the reason `STATED` above is one: the trees' copies agree with each
other while all of them are wrong.
"""

RULE_TYPES = ("comment", "refactoring", "suggestion")
"""Every `rule_types:` value, which the file leaves at its default.

Sourcery's own template lists the three. Section 10 has the key left
at its default; in Sourcery 1.46.0, `rule_types: [comment]` reports what
no `rule_types:` does.
"""


BARE_SKIP = "bare-sourcery-skip"
"""The local hook section 4 puts in every tree that calls `SOURCERY_CALLED`."""

BARE_SKIP_STANZA: dict[str, Any] = {
    "repo": "local",
    "id": BARE_SKIP,
    "name": "a sourcery skip names rules, and no tag",
    "language": "pygrep",
    "entry": (
        r"#\W*sourcery\W+skip(?!:)"
        r"|#\W*sourcery\W+skip:[^#]*"
        r"(?<![\w-])(?:default|refactoring|suggestion|comment)(?![\w-])"
    ),
    "types": ["python"],
}
r"""Section 4's `bare-sourcery-skip`, whole: a tree's has these keys alone.

What the entry refuses and why is section 4's bullet; `spelled()`'s
cases below are the forms measured. pygrep reads the file and the
pattern as bytes, where `\s` and `\w` are ASCII, so `\W` is what takes
in a non-breaking space.
"""

SKIP_WORDS = ("sourcery", "skip")
"""The two words of Sourcery's skip comment, kept apart for `spelled()`."""

TOP_LEVEL = ("files", "exclude", "default_stages", "default_language_version")
"""The top-level keys of a gate that change what every hook reads or runs.

`default_stages: [manual]` takes every hook out of CI's run,
`bare-sourcery-skip` with them.
"""

RELEASE_XY = re.compile(r"^(?P<major>[0-9]+)\.(?P<minor>[0-9]+)$")
"""The `X.Y` shape a `python_version` of `.sourcery.yaml` takes."""


def python_floor(pyproject: dict[str, Any]) -> tuple[int, int] | None:
    """Return the `X.Y` floor `requires-python` declares with `>=`.

    Another form reads as none, and the finding names the `>=` it looks for.

    :param pyproject: the parsed `pyproject.toml`.
    :returns: the floor, or `None` where no `>=` bound is found.
    """
    declared = str(pyproject.get("project", {}).get("requires-python", ""))
    found = FLOOR_BOUND.search(declared)
    if found is None:
        return None
    parts = [int(part) for part in found["version"].split(".")]
    return (parts[0], parts[1] if len(parts) > 1 else 0)


def ignored(patterns: list[Any], python: list[str]) -> list[str]:
    """Return the tracked Python files an `ignore:` entry covers.

    An entry is read as a path, a directory holding the file, or a glob,
    matched against the path from every depth, as Sourcery matches it:
    `conftest.py` covers `tests/conftest.py`. A leading `./` or `**/` is
    dropped. Where Sourcery reads one more narrowly, this over-reports,
    which a tree answers by naming no tracked Python file there at all.

    :param patterns: the `ignore:` list of `.sourcery.yaml`.
    :param python: the tracked Python files, relative to the root.
    :returns: the files covered, in the order given.
    """
    out: list[str] = []
    wanted = [
        str(raw).rstrip("/").removeprefix("./").removeprefix("**/") for raw in patterns
    ]
    for path in python:
        parts = path.split("/")
        tails = ["/".join(parts[depth:]) for depth in range(len(parts))]
        if any(
            tail == pattern
            or tail.startswith(pattern + "/")
            or fnmatch.fnmatch(tail, pattern)
            for tail in tails
            for pattern in wanted
        ):
            out.append(path)
    return out


def guard_departures(document: dict[str, Any]) -> list[str]:
    """Report where a parsed gate guards a Sourcery skip unlike section 4.

    :param document: the gate, as `gate()` returns it.
    :returns: one finding per departure, empty where there is none.
    """
    found = flattened(document)
    guards = [hook for hook in found if hook["id"] == BARE_SKIP]
    out = [] if guards else [f"no hook {BARE_SKIP} refuses a skip naming no rule"]
    for hook in guards:
        stanza = {key: value for key, value in hook.items() if key != "rev"}
        if stanza != BARE_SKIP_STANZA:
            out.append(f"{BARE_SKIP} is not section 4's: {stanza!r}")
    out.extend(
        f"the gate sets {key}: {document[key]!r}, which reaches every hook"
        for key in TOP_LEVEL
        if key in document
    )
    return out


FILTERED = ("**.py", SOURCERY_CONFIG)
"""What a caller's `pull_request` filter names besides its own file."""


def caller_departures(root: Path) -> list[str]:
    """Report where a tree calls `SOURCERY_CALLED` otherwise than section 10.

    A call is a job whose `uses:` names it, in this repository at any
    ref or as a local path, in a workflow triggered on `pull_request`
    whose `paths:` names the tree's Python, its `.sourcery.yaml` and
    the workflow's own file.

    :param root: the root of the checkout.
    :returns: one finding per departure, empty where there is none.
    """
    local = {
        f"{prefix}.github/workflows/{SOURCERY_CALLED}" for prefix in LOCAL_PREFIXES
    }
    calling = [
        workflow
        for workflow in workflows(root)
        for job in jobs(workflow).values()
        if str(job.get("uses", "")) in local
        or calls_here(str(job.get("uses", "")), SOURCERY_CALLED)
    ]
    if not calling:
        return [f"no workflow calls {SOURCERY_CALLED}"]
    out: list[str] = []
    for workflow in calling:
        if "pull_request" not in triggers(workflow):
            out.append(f"{workflow.name} calls {SOURCERY_CALLED} on no pull_request")
            continue
        trigger = triggers(workflow)["pull_request"] or {}
        named = set(trigger.get("paths") or [])
        wanted = {*FILTERED, f".github/workflows/{workflow.name}"}
        if not wanted <= named:
            out.append(f"{workflow.name}'s paths: name no {sorted(wanted - named)}")
    return out


def config_departures(
    config: dict[str, Any] | None,
    python: list[str],
    floor: tuple[int, int] | None,
) -> list[str]:
    """Report where a `.sourcery.yaml` departs from section 10.

    :param config: the parsed file, or `None` where the tree has none.
    :param python: the tracked Python files, relative to the root.
    :param floor: the `requires-python` floor, as `python_floor()` reads it.
    :returns: one finding per departure, empty where there is none.
    """
    if config is None:
        return [f"there is no {SOURCERY_CONFIG}"]
    out: list[str] = []
    settings = config.get("rule_settings") or {}
    disabled = {str(rule) for rule in settings.get("disable") or []}
    left_on = sorted(set(TURNED_OFF) - disabled)
    if left_on:
        out.append(f"{SOURCERY_CONFIG} leaves on {left_on}")
    also = sorted(disabled - set(TURNED_OFF))
    if also:
        out.append(f"{SOURCERY_CONFIG} also turns off {also}")
    if "enable" in settings and settings["enable"] != ["default"]:
        out.append(f"{SOURCERY_CONFIG} sets enable: {settings['enable']!r}")
    if "rule_types" in settings and sorted(settings["rule_types"] or []) != list(
        RULE_TYPES
    ):
        out.append(f"{SOURCERY_CONFIG} sets rule_types: {settings['rule_types']!r}")
    hidden = ignored(config.get("ignore") or [], python)
    if hidden:
        out.append(f"{SOURCERY_CONFIG} ignores {hidden}")
    declared = settings.get("python_version")
    release = RELEASE_XY.match(declared) if isinstance(declared, str) else None
    if release is None:
        out.append(f"{SOURCERY_CONFIG} python_version is {declared!r}, no X.Y")
    elif floor is None:
        out.append("pyproject.toml's requires-python names no >= floor to hold it to")
    elif (int(release["major"]), int(release["minor"])) > floor:
        out.append(
            f"{SOURCERY_CONFIG} python_version {declared} is above the"
            f" requires-python floor {floor[0]}.{floor[1]}"
        )
    return out


@pytest.mark.tier(Tier.PYTHON)
def test_a_python_tree_calls_sourcery_with_its_rules_off(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 10's `sourcery` job, its configuration, and section 4's guard.

    Asked only of a tree that tracks a Python file, which is what the
    job reads. `python_version` is held to at most the `requires-python`
    floor and not to it exactly: section 10 asks for the lowest
    interpreter the code runs on, which a script served to other trees
    can put lower.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: the parsed files.
    """
    root = trees[repository]
    python = tracked(root, "*.py")
    if not python:
        pytest.skip(f"{repository} tracks no Python file")
    path = root / SOURCERY_CONFIG
    config = (
        (yaml.safe_load(path.read_text(encoding="utf-8")) or {})
        if path.is_file()
        else None
    )
    found = (
        caller_departures(root)
        + guard_departures(gate(repository, trees))
        + config_departures(
            config, python, python_floor(parsed(repository, pyprojects))
        )
    )
    assert not found, f"{found}; " + by_hand(
        repository,
        f"grep -ln {SOURCERY_CALLED} .github/workflows/*.yml;"
        f" grep -n -A6 'id: {BARE_SKIP}' {CONFIG}; cat {SOURCERY_CONFIG};"
        " grep -n requires-python pyproject.toml",
    )


AGREEING_GATE: dict[str, Any] = {
    "repos": [
        {
            "repo": "local",
            "hooks": [
                {key: value for key, value in BARE_SKIP_STANZA.items() if key != "repo"}
            ],
        },
    ],
}
"""A gate section 4's `bare-sourcery-skip` reads as agreeing, for controls."""


def test_a_gate_off_section_4s_guard_would_be_reported() -> None:
    """`guard_departures` reports each way a gate can leave section 4.

    Each control changes one thing in `AGREEING_GATE` and asks for the
    finding naming it: a check that reads nothing stays green on these.
    """
    assert guard_departures(AGREEING_GATE) == []
    assert guard_departures({"repos": []}) == [
        f"no hook {BARE_SKIP} refuses a skip naming no rule"
    ]
    for key, value in (
        ("entry", "NEVERMATCH"),
        ("exclude", "^tests/"),
        ("stages", ["manual"]),
        ("language", "system"),
        ("name", "bare-sourcery-skip"),
        ("types", ["markdown"]),
    ):
        guard = copy.deepcopy(AGREEING_GATE)
        guard["repos"][0]["hooks"][0][key] = value
        assert any(
            line.startswith(f"{BARE_SKIP} is not section 4's")
            for line in guard_departures(guard)
        ), f"{BARE_SKIP} with {key}: {value!r} is read as agreeing"
    reaching: list[tuple[str, Any]] = [
        ("files", "^src/"),
        ("exclude", "^tests/"),
        ("default_stages", ["manual"]),
        ("default_language_version", {"python": "python3.11"}),
    ]
    for key, value in reaching:
        narrowed = {**copy.deepcopy(AGREEING_GATE), key: value}
        assert guard_departures(narrowed) == [
            f"the gate sets {key}: {value!r}, which reaches every hook"
        ]


def _workflow(root: Path, name: str, text: str) -> None:
    folder = root / ".github" / "workflows"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(text, encoding="utf-8")


def test_a_tree_off_section_10s_caller_would_be_reported(tmp_path: Path) -> None:
    """`caller_departures` reads a call, local or remote, on `pull_request`.

    :param tmp_path: where the trees are built.
    """
    remote = f"{ORG}/{SELF}/.github/workflows/{SOURCERY_CALLED}@v1"
    cases: list[tuple[str, str, list[str]]] = [
        ("pull_request", remote, []),
        ("pull_request", f"./.github/workflows/{SOURCERY_CALLED}", []),
        ("push", remote, [f"sourcery.yml calls {SOURCERY_CALLED} on no pull_request"]),
        (
            "pull_request",
            f"{ORG}/other/.github/workflows/{SOURCERY_CALLED}@v1",
            [f"no workflow calls {SOURCERY_CALLED}"],
        ),
        (
            "pull_request",
            f"{ORG}/{SELF}/.github/workflows/reusable-lint.yml@v1",
            [f"no workflow calls {SOURCERY_CALLED}"],
        ),
    ]
    paths = "".join(
        f"\n      - {path!r}" for path in (*FILTERED, ".github/workflows/sourcery.yml")
    )
    for index, (trigger, called, wanted) in enumerate(cases):
        root = tmp_path / str(index)
        _workflow(
            root,
            "sourcery.yml",
            f"on:\n  {trigger}:\n    paths:{paths}\n"
            f"jobs:\n  sourcery:\n    uses: {called}\n",
        )
        assert caller_departures(root) == wanted, f"{trigger}, {called}"
    for dropped in (*FILTERED, ".github/workflows/sourcery.yml", None):
        root = tmp_path / f"without-{dropped}"
        kept = [
            path
            for path in (*FILTERED, ".github/workflows/sourcery.yml")
            if dropped is not None and path != dropped
        ]
        block = "".join(f"\n      - {path!r}" for path in kept)
        filtered = f"\n    paths:{block}" if kept else ""
        _workflow(
            root,
            "sourcery.yml",
            f"on:\n  pull_request:{filtered}\njobs:\n  sourcery:\n    uses: {remote}\n",
        )
        missing = (
            [dropped]
            if dropped is not None
            else sorted((*FILTERED, ".github/workflows/sourcery.yml"))
        )
        assert caller_departures(root) == [
            f"sourcery.yml's paths: name no {sorted(missing)}"
        ], f"paths without {dropped}"
    assert caller_departures(tmp_path / "none") == [
        f"no workflow calls {SOURCERY_CALLED}"
    ]


def test_this_trees_bare_sourcery_skip_is_section_4s() -> None:
    """This tree's gate carries `BARE_SKIP_STANZA` as written."""
    found = [
        {key: value for key, value in hook.items() if key != "rev"}
        for hook in flattened(yaml.safe_load((ROOT / CONFIG).read_text("utf-8")))
        if hook["id"] == BARE_SKIP
    ]
    assert found == [BARE_SKIP_STANZA]


def spelled(
    after: str = "",
    between: str = " ",
    before: str = " ",
    words: tuple[str, str] = SKIP_WORDS,
) -> str:
    """Spell Sourcery's skip comment on a `def` line, from its parts.

    Built and not written out, so that `BARE_SKIP` reads no such comment
    in this file.

    :param after: what follows the second word.
    :param between: what separates the two words.
    :param before: what separates the hash from the first word.
    :param words: the two words.
    :returns: the line.
    """
    first, second = words
    return f"def f(d):  #{before}{first}{between}{second}{after}"


@pytest.mark.parametrize(
    ("line", "refused"),
    [
        pytest.param(spelled(), True, id="bare"),
        pytest.param(spelled(before=""), True, id="no-space"),
        pytest.param(spelled("  # reason"), True, id="hash-reason"),
        pytest.param(spelled(" - reason"), True, id="dash-reason"),
        pytest.param(spelled(" -"), True, id="dash"),
        pytest.param(spelled("  # noqa: ANN001"), True, id="noqa"),
        pytest.param(spelled(" : a"), True, id="space-colon"),
        pytest.param(spelled(": default"), True, id="default"),
        pytest.param(spelled(": refactoring"), True, id="refactor"),
        pytest.param(spelled(": suggestion"), True, id="suggestion"),
        pytest.param(spelled(": comment"), True, id="comment"),
        pytest.param(spelled(": switch, default"), True, id="in-list"),
        pytest.param(spelled(between="  "), True, id="two-spaces"),
        pytest.param(spelled(between="\t"), True, id="tab"),
        pytest.param(spelled(between="\u00a0"), True, id="nbsp"),
        pytest.param(spelled(between="\u2003"), True, id="em-space"),
        pytest.param(spelled(before="\t"), True, id="tab-after-hash"),
        pytest.param(spelled(before="\u00a0"), True, id="nbsp-after-hash"),
        pytest.param(spelled("\t: a"), True, id="tab-colon"),
        pytest.param(spelled("\u00a0: a"), True, id="nbsp-colon"),
        pytest.param(spelled("\u00a0"), True, id="nbsp-after"),
        pytest.param(spelled(":\tdefault"), True, id="tab-tag"),
        pytest.param(spelled(":\u00a0default"), True, id="nbsp-tag"),
        pytest.param(spelled(": switch,\tdefault"), True, id="tab-in-list"),
        pytest.param(spelled(": default", between="\t"), True, id="tab-word-tag"),
        pytest.param(spelled(between=":"), True, id="colon-between"),
        pytest.param(spelled(": switch"), False, id="named"),
        pytest.param(spelled(":\ta"), False, id="tab-named"),
        pytest.param(spelled(":\u00a0a"), False, id="nbsp-named"),
        pytest.param(spelled(": a", between="  "), False, id="spaces-named"),
        pytest.param(spelled(": a", between="\u00a0"), False, id="nbsp-words-named"),
        pytest.param(spelled(": DEFAULT"), False, id="tag-case"),
        pytest.param(spelled(words=("SOURCERY", "skip")), False, id="upper"),
        pytest.param(spelled(words=("sourcery", "Skip")), False, id="skip-case"),
        pytest.param(spelled(words=("Sourcery", "skip")), False, id="capital"),
        pytest.param(spelled(": a, b"), False, id="two-named"),
        pytest.param(spelled(":"), False, id="empty-list"),
        pytest.param(spelled(":\u00a0"), False, id="nbsp-empty"),
        pytest.param(spelled(": a  # a comment"), False, id="reason"),
        pytest.param(spelled(": no-comment"), False, id="suffix"),
    ],
)
def test_bare_sourcery_skip_refuses_a_skip_naming_no_rule(
    line: str,
    refused: bool,  # noqa: FBT001
) -> None:
    r"""`BARE_SKIP_STANZA`'s entry, compiled as pygrep compiles it.

    The pattern and the line as bytes, which is how pygrep reads both, so
    `\s` and `\w` read ASCII alone. `colon-between` is refused though
    Sourcery read it as no skip: `\W+` between the words is the shape
    that takes in every space it reads.

    :param line: a line of a Python file.
    :param refused: whether the hook reports it.
    """
    entry: str = BARE_SKIP_STANZA["entry"]
    found = re.search(entry.encode(), line.encode())
    assert bool(found) is refused, f"{entry!r} on {line!r}"


def test_a_sourcery_yaml_off_section_4_would_be_reported() -> None:
    """`config_departures` reports each way a `.sourcery.yaml` can leave it.

    The floor is 3.11 and the tree tracks one module at the root and three
    under `tests/`, one of them a level further down: an entry naming a
    file or a directory reaches it at any depth, as Sourcery's does.
    """
    python = [
        "example.py",
        "tests/conftest.py",
        "tests/helpers/one.py",
        "tests/one_test.py",
    ]
    under_tests = python[1:]
    floor = (3, 11)
    agreeing: dict[str, Any] = {
        "ignore": [".venv", "node_modules"],
        "rule_settings": {
            "enable": ["default"],
            "disable": list(TURNED_OFF),
            "rule_types": list(RULE_TYPES),
            "python_version": "3.11",
        },
    }
    assert config_departures(agreeing, python, floor) == []
    lower = copy.deepcopy(agreeing)
    lower["rule_settings"]["python_version"] = "3.10"
    assert config_departures(lower, python, floor) == [], "a lower version is refused"
    assert config_departures(None, python, floor) == [f"there is no {SOURCERY_CONFIG}"]
    left = copy.deepcopy(agreeing)
    left["rule_settings"]["disable"].remove("assign-if-exp")
    assert config_departures(left, python, floor) == [
        f"{SOURCERY_CONFIG} leaves on ['assign-if-exp']"
    ]
    for extra in ("default", "refactoring", "use-next", "switch"):
        more = copy.deepcopy(agreeing)
        more["rule_settings"]["disable"].append(extra)
        assert config_departures(more, python, floor) == [
            f"{SOURCERY_CONFIG} also turns off ['{extra}']"
        ]
    for enable in (["reintroduce-else"], [], ["default", "use-next"]):
        enabled = copy.deepcopy(agreeing)
        enabled["rule_settings"]["enable"] = enable
        assert config_departures(enabled, python, floor) == [
            f"{SOURCERY_CONFIG} sets enable: {enable!r}"
        ]
    for types in (["comment"], [], ["refactoring", "suggestion"]):
        typed = copy.deepcopy(agreeing)
        typed["rule_settings"]["rule_types"] = types
        assert config_departures(typed, python, floor) == [
            f"{SOURCERY_CONFIG} sets rule_types: {types!r}"
        ]
    defaults = copy.deepcopy(agreeing)
    del defaults["rule_settings"]["enable"], defaults["rule_settings"]["rule_types"]
    assert config_departures(defaults, python, floor) == [], "defaults are refused"
    for pattern, hidden in (
        ("**/*.py", python),
        ("tests", under_tests),
        ("tests/", under_tests),
        ("example.py", ["example.py"]),
        ("./tests", under_tests),
        ("helpers", ["tests/helpers/one.py"]),
        ("conftest.py", ["tests/conftest.py"]),
        ("helpers/one.py", ["tests/helpers/one.py"]),
        ("*/one.py", ["tests/helpers/one.py"]),
    ):
        ignoring = copy.deepcopy(agreeing)
        ignoring["ignore"].append(pattern)
        assert config_departures(ignoring, python, floor) == [
            f"{SOURCERY_CONFIG} ignores {hidden}"
        ], f"ignore: {pattern!r}"
    for version in ("3.15", "", "not-a-version", 3.11):
        wrong = copy.deepcopy(agreeing)
        wrong["rule_settings"]["python_version"] = version
        assert config_departures(wrong, python, floor), (
            f"python_version {version!r} is read as agreeing"
        )
    assert config_departures(agreeing, python, None) == [
        "pyproject.toml's requires-python names no >= floor to hold it to"
    ]
    assert python_floor({"project": {"requires-python": ">=3.11"}}) == (3, 11)
    assert python_floor({"project": {"requires-python": ">=3.12.1,<4"}}) == (3, 12)
    assert python_floor({"project": {"requires-python": ">=3"}}) == (3, 0)
    assert python_floor({}) is None


ACTIONLINT = "https://github.com/kjanat/actionlint"
"""The repository section 4 says the workflow linter is taken from."""

ACTIONLINT_ID = "actionlint-shellcheck"
"""The id of the hook section 4 takes from `ACTIONLINT`."""

ACTIONLINT_REFUSED = {
    "id": "actionlint",
    "repo": "https://github.com/Mateusz-Grzelinski/actionlint-py",
    "rev": "v1.7.12.25",
}
"""The stanza of a gate that takes the Python packaging.

A literal, for the reason `REFUSED` above is one: the check below is
green wherever the gates agree, and a reading that accepted this
stanza would stay green with nothing measured.
"""


def actionlint_departures(found: list[dict[str, Any]]) -> list[str]:
    """Report a gate without the fork, or with a fork hook off its id or pin.

    An actionlint hook taken from any other repository is reported too.

    :param found: the hook mappings, as `hooks()` reads them.
    :returns: one finding per departure listed, empty where there is none
        of them.
    """
    ours = [hook for hook in found if hook["repo"] == ACTIONLINT]
    others = [
        hook
        for hook in found
        if "actionlint" in str(hook["repo"]) and hook["repo"] != ACTIONLINT
    ]
    return (
        ([] if ours else [f"no hook is taken from {ACTIONLINT}"])
        + [f"{hook['id']} is taken from {hook['repo']}" for hook in others]
        + [
            f"{hook['id']} is pinned at {hook['rev']!r}, not a sha"
            for hook in ours
            if not PIN.match(str(hook["rev"]))
        ]
        + [
            f"{hook['id']} is the hook, not {ACTIONLINT_ID}"
            for hook in ours
            if hook["id"] != ACTIONLINT_ID
        ]
    )


def test_the_gate_lints_workflows_with_the_actionlint_fork(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 4's *workflows* bullet: the kjanat fork, pinned by a sha.

    README section 4 has why (btclib-org/.github#1698).

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    found = actionlint_departures(hooks(repository, trees))
    assert not found, (
        f"the gate departs from section 4's workflow linter: {found}; "
        + by_hand(repository, f"grep -n -B1 -A3 'repo: .*actionlint' {CONFIG}")
    )


def test_a_gate_off_the_fork_is_reported() -> None:
    """The check above reports what `actionlint_departures` lists.

    That is a gate without the fork, a fork hook off its id or pin, and an
    actionlint hook taken from any other repository.
    """
    other = f"actionlint is taken from {ACTIONLINT_REFUSED['repo']}"
    assert actionlint_departures([ACTIONLINT_REFUSED]) == [
        f"no hook is taken from {ACTIONLINT}",
        other,
    ]
    assert actionlint_departures(
        [{"id": "actionlint", "repo": ACTIONLINT, "rev": "v1.17.0"}]
    ) == [
        "actionlint is pinned at 'v1.17.0', not a sha",
        f"actionlint is the hook, not {ACTIONLINT_ID}",
    ]
    agreeing = {"id": ACTIONLINT_ID, "repo": ACTIONLINT, "rev": "0" * 40}
    assert actionlint_departures([agreeing]) == []
    assert actionlint_departures([agreeing, ACTIONLINT_REFUSED]) == [other], (
        "the Python packaging kept beside the fork is read as agreeing"
    )
    upstream = {
        "id": "actionlint-system",
        "repo": "https://github.com/rhysd/actionlint",
    }
    assert actionlint_departures([agreeing, upstream]) == [
        "actionlint-system is taken from https://github.com/rhysd/actionlint"
    ], "the upstream hook kept beside the fork is read as agreeing"
    mirror = {"id": "actionlint-docker", "repo": "https://example.org/actionlint"}
    assert actionlint_departures([agreeing, mirror]) == [
        "actionlint-docker is taken from https://example.org/actionlint"
    ], "a hook from a third actionlint repository is read as agreeing"


BASELINE = ".secrets.baseline"
"""The file section 4 says `detect-secrets` reads, at the root of a tree."""

HEX_PLUGIN = "HexHighEntropyString"
"""The `detect-secrets` plugin that reads a frozen `rev:` sha as a secret."""

REV_LINE_FILTER = {
    "path": "detect_secrets.filters.regex.should_exclude_line",
    "pattern": ['^\\s*rev: "?[0-9a-f]{40}"?(\\s|$)'],
}
"""The `filters_used` entry section 4's *secrets* bullet gives.

A literal, for the reason `REFUSED` above is one: a reading that
accepted any line filter would stay green with nothing measured.
"""


def rev_line_departures(baseline: dict[str, Any]) -> list[str]:
    """Report a baseline that enables the hex plugin without the filter.

    :param baseline: a parsed `.secrets.baseline`.
    :returns: the finding, empty where the plugin is off or the filter
        stands.
    """
    plugins = {plugin["name"] for plugin in baseline.get("plugins_used", [])}
    if HEX_PLUGIN not in plugins:
        return []
    filters = baseline.get("filters_used", [])
    if REV_LINE_FILTER in filters:
        return []
    return [f"{HEX_PLUGIN} is enabled and filters_used has no {REV_LINE_FILTER}"]


def test_a_baseline_with_the_hex_plugin_filters_frozen_rev_lines(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 4's *secrets* bullet: a line filter, not a pragma.

    The bullet has why (btclib-org/.github#1723).

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    path = trees[repository] / BASELINE
    if not path.is_file():
        pytest.skip(f"{repository} has no {BASELINE}")
    found = rev_line_departures(json.loads(path.read_text(encoding="utf-8")))
    assert not found, f"{found}; " + by_hand(
        repository, f"grep -n -A4 'should_exclude_line' {BASELINE}"
    )


def test_a_baseline_without_the_rev_line_filter_would_be_reported() -> None:
    """The check above reports what `rev_line_departures` lists."""
    on = {"plugins_used": [{"name": HEX_PLUGIN, "limit": 3.0}]}
    assert rev_line_departures(on) == [
        f"{HEX_PLUGIN} is enabled and filters_used has no {REV_LINE_FILTER}"
    ]
    file_filter = {
        "path": "detect_secrets.filters.regex.should_exclude_file",
        "pattern": ["^tests/"],
    }
    assert rev_line_departures({**on, "filters_used": [file_filter]}), (
        "a file exclusion is read as the line filter"
    )
    other_line = {**REV_LINE_FILTER, "pattern": ["^rev:"]}
    assert rev_line_departures({**on, "filters_used": [other_line]}), (
        "another line pattern is read as the filter"
    )
    assert rev_line_departures({**on, "filters_used": [REV_LINE_FILTER]}) == []
    assert rev_line_departures({"plugins_used": [{"name": "AWSKeyDetector"}]}) == []


PYROMA = "pyroma"
"""Section 4's packaging hook that reads a distribution's metadata."""

PYROMA_STATED = {
    "repo": "local",
    "entry": "uv run --locked --no-build --only-group check pyroma",
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
    found = (
        stated_departures(hook, STATED)
        if repository == SELF
        else served_departures(hook)
    )
    if UNFILTERED in hook:
        found.append(f"{UNFILTERED}: {hook[UNFILTERED]!r}, where section 4 has none")
    found.extend(counted_departures(hook))
    return found


def test_the_manifest_declares_what_section_4_says(trees: dict[str, Path]) -> None:
    """`MANIFEST`'s `check-changelog` carries the keys every taker relies on.

    A taker's stanza restates none of them, so this is the one place
    they are read for the trees that take the hook.

    :param trees: the checkouts.
    """
    path = trees[SELF] / MANIFEST
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    found = [hook for hook in parsed if hook.get("id") == CHANGELOG_HOOK]
    assert len(found) == 1, (
        f"{SELF}'s {MANIFEST} names {CHANGELOG_HOOK} {len(found)} times"
    )
    drifted = stated_departures(found[0], STATED)
    if UNFILTERED in found[0]:
        drifted.append(
            f"{UNFILTERED}: {found[0][UNFILTERED]!r}, where section 4 has none"
        )
    assert not drifted, f"{MANIFEST} says what section 4 does not: {drifted}"


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


def unfrozen(text: str) -> list[str]:
    """List the `rev:` lines of `SERVED` blocks not frozen at a tag.

    :param text: a gate, as its file holds it.
    :returns: each such block's line number with its `rev:` line, or
        with None where the block has none.
    """
    lines = text.splitlines()
    found: list[str] = []
    for number, line in enumerate(lines, start=1):
        opened = REPO_LINE.match(line)
        if opened is None or opened["repo"] != SERVED:
            continue
        rev = None
        for following in lines[number:]:
            if REPO_LINE.match(following):
                break
            if following.strip().startswith("rev:"):
                rev = following
                break
        if rev is None or FROZEN.match(rev) is None:
            found.append(f"{number}: {rev!r}")
    return found


def test_check_changelog_is_frozen_at_a_tag(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 4: a stanza taking `check-changelog` is frozen at a tag.

    The sha is the one `SELF`'s tag names, the annotated tag's own
    object, which `autoupdate --freeze` writes.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    if repository == SELF:
        pytest.skip(f"{SELF} keeps its own {CHANGELOG_HOOK} stanza local")
    path = trees[repository] / CONFIG
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if not any(
        (opened := REPO_LINE.match(line)) and opened["repo"] == SERVED
        for line in text.splitlines()
    ):
        pytest.skip(f"{repository}'s gate takes nothing from {SERVED}")
    hint = by_hand(repository, f"grep -n -A1 'repo: {SERVED}$' {CONFIG}")
    wrong = unfrozen(text)
    assert not wrong, f"rev: lines not frozen at a tag: {wrong}; {hint}"
    for line in text.splitlines():
        frozen = FROZEN.match(line)
        if frozen is None:
            continue
        ref = gh_json(f"repos/{ORG}/{SELF}/git/ref/tags/{frozen['tag']}")
        assert ref["object"]["sha"] == frozen["sha"], (
            f"{frozen['tag']} names {ref['object']['sha']}, not {frozen['sha']}; "
            + hint
        )


def test_an_unfrozen_stanza_would_be_reported() -> None:
    """A bare sha, a tag name or no `rev:` is reported, a frozen line not."""
    block = f"  - repo: {SERVED}\n    {{}}\n    hooks:\n      - id: x\n"
    sha = "0" * 40
    for rev in (
        f"rev: {sha}",
        "rev: v2026.10.25",
        "hooks: []",
        f"rev: {sha}  # frozen: v2026.10.25",
    ):
        assert unfrozen(block.format(rev)), f"{rev!r} read as frozen"
    for rev in (
        f"rev: {sha} # frozen: v2026.10.25",
        f"rev: {sha} # frozen: v2026.1.2",
    ):
        assert unfrozen(block.format(rev)) == [], f"{rev!r} read as unfrozen"
    other = "  - repo: https://example.com/x\n    rev: v1\n"
    assert unfrozen(other) == [], "a block of another repository is read"


def test_a_gate_that_had_drifted_would_be_reported() -> None:
    """The cell above is green on gates that agree, however it reads.

    Asked of the literal `REFUSED` names, once for each finding it
    carries: a key the hook states and section 4 gives it none of, a
    stanza declared where the hook is not served from, a `rev:` that is
    no commit, and an `args:` naming no count. `SELF` is asked
    separately: it is the one tree read for the manifest's keys and not
    for a pin.
    """
    refused = departures(REFUSED, "btclib")
    assert any("always_run" in line for line in departures(REFUSED, SELF)), (
        f"{REFUSED} read as carrying always_run in {SELF}: either a key"
        " section 4 states is no longer read there, or the literal wants"
        " another"
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
    taking = {
        "id": CHANGELOG_HOOK,
        "repo": SERVED,
        "rev": "0" * 40,
        "args": [COUNT, "7"],
    }
    assert departures(taking, "btclib") == [], (
        f"{taking} is read as drift from the keys it is built of"
    )
    serving = {
        "id": CHANGELOG_HOOK,
        "repo": "local",
        "rev": None,
        "args": [COUNT, "7"],
        **STATED,
    }
    assert departures(serving, SELF) == [], (
        f"{serving} is read as drift from the keys it is built of"
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
    on its own schedule while the floor waits for Dependabot to accept a
    newer uv, so a pin above the floor is the ordinary state and
    equality here would be red at each of those moves.

    :param rev: the pin of the block the hook was read out of.
    :param declared: the tree's `[tool.uv] required-version`.
    :returns: whether the floor admits that uv, or `None` where the
        floor is not the bare `>=` shape section 1 asks for, which is
        `test_the_uv_floor_is_not_above_what_dependabot_bundles`'s finding.
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
    `test_the_uv_floor_is_not_above_what_dependabot_bundles`'s question, and
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
