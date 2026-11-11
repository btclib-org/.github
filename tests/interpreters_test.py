# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 1's interpreter window, and the version a workflow here names.

A library covers every interpreter still in support and an application
takes the newest its dependencies allow, which is section 1's rule and
the reason the two halves are asked differently here.

Each tree that publishes holds a module of this name reading its own
declarations against one another -- `requires-python` against the
classifiers, the classifiers against the platform sweeps -- which is
what section 15 means by a repository answering for itself. It is a
published tree's, which section 3 states where it states the convention
and section 15 gives the reason for.

Left here is the question no tree can ask: the libraries name one
window, so a tree that disagrees with the others is out of step with
them. And what a tree holding no module of its own leaves unasked: the
ends of that window, declared in `pyproject.toml` and in
`.python-version` whatever the tree is, and read here against one
another; the pin against the interpreters a tree's `test.yml` names; and
the floor against the patches the jobs running a tree's suite name.
Which tree is a library is `library` below, section 1 giving the rule
and the reason.

The calendar itself is asked of nothing here. What decides it is
python.org's, a date in it is a date this suite would have to be told,
and what the trees can be held to without one is that they agree.

Two cells ask about this tree instead, and about section 10 rather
than section 1: a reusable workflow whose job installs nothing of the
caller runs on a version written in the file, since no `requires-python`
reaches a script that imports nothing. That is a literal in a shared
workflow, which is the thing a calling tree's own module of this name
can no longer see, so the tree hosting the file is where it is read. The
cell after them, on the patch a floor names, is section 1's again.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
from itertools import product
from typing import TYPE_CHECKING, Any

import pytest

from . import ORG, SELF, Tier, by_hand, tracked
from .workflows_test import jobs, steps, workflows

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


def release(version: str) -> str:
    """Return the `X.Y` a version belongs to.

    A classifier names a minor version and the floor names a patch of
    one, section 1 saying why, so the two are compared at `X.Y`.

    :param version: a version as it is written, `3.11.9` and the like.
    :returns: its first two parts.
    """
    return ".".join(version.split(".")[:2])


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
    """Section 1: the libraries name one window between them.

    A floor or a classifier list only one of them declares is that tree
    out of step with the others, and which of them is wrong is section
    1's answer rather than this suite's. A floor counts at its `X.Y`,
    its patch being the one each tree's own jobs run. A tree that
    publishes a program rather than a library is out of the comparison
    instead of wrong in it, its own window being its dependencies'.

    :param pyprojects: the parsed files.
    :param tiers: each repository's tier.
    """
    declared: dict[str, list[str]] = {}
    for repository, parsed in sorted(pyprojects.items()):
        if not library(parsed, tiers[repository]):
            continue
        floor, classified = versions(parsed)
        listed = ",".join(sorted(classified, key=ordered))
        window = f">={release(floor)}, classifiers {listed or 'none'}"
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
    the floor's `X.Y`. Section 15 is where a tree holding no module
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
    assert release(floor) == lowest, (
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


SUITE = ".github/workflows/test.yml"
"""The workflow holding the coverage job, which section 1 runs on the pin."""


@pytest.mark.tier(Tier.PYTHON)
def test_the_suite_workflow_names_only_the_interpreter_the_tree_pins(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 1: a local run measures what the coverage job measures.

    That holds while `test.yml` names no interpreter but the one
    `.python-version` pins. A literal there is a second copy of the pin,
    and it stays behind when the pin moves. A `t` suffix is dropped, as
    `pinned` drops it, and the two are compared at `X.Y`, so that a job
    there can name the floor's patch, section 1 saying where. Section 15
    says why the other workflows are left to a reading.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    workflow = root / SUITE
    if not workflow.is_file():
        pytest.skip(f"{repository} has no {SUITE}")
    pin = pinned(root)
    other = sorted(
        {
            version.removesuffix("t")
            for step in steps(workflow)
            for version in named(step)
            if release(version.removesuffix("t")) != release(pin)
        }
    )
    assert not other, (
        f"{SUITE} names {', '.join(other)} and .python-version pins {pin!r}; "
        + by_hand(repository, f"grep -n -- '--python \\|python-version:' {SUITE}")
    )


def test_a_suite_workflow_naming_another_interpreter_is_reported(
    tmp_path: Path,
) -> None:
    """The cell above fails on a planted `test.yml` that names another version.

    Over trees that agree, the cell is green whatever its reading does.
    The free-threaded build of the pin and a patch of it are planted
    too, and agree; a patch of another version does not.

    :param tmp_path: where the trees are planted.
    """
    cases: list[tuple[str, str, str]] = [
        ("3.15t", "3.15", ""),
        ("3.14", "3.15", "3.14"),
        ("3.15", "3.13", "3.13"),
        ("3.15", '"3.13"', "3.13"),
        ("3.15.2", "3.15", ""),
        ("3.15", "3.14.3", "3.14.3"),
    ]
    for index, (setup, run, wanted) in enumerate(cases):
        root = tmp_path / str(index)
        folder = root / ".github" / "workflows"
        folder.mkdir(parents=True)
        (root / ".python-version").write_text("3.15\n", encoding="utf-8")
        (folder / "test.yml").write_text(
            "on: push\njobs:\n  coverage:\n    runs-on: ubuntu-latest\n"
            "    steps:\n      - uses: astral-sh/setup-uv@v1\n"
            f'        with:\n          python-version: "{setup}"\n'
            f"      - run: uv run --python {run} pytest\n",
            encoding="utf-8",
        )
        trees = {"x": root}
        if not wanted:
            test_the_suite_workflow_names_only_the_interpreter_the_tree_pins("x", trees)
            continue
        with pytest.raises(AssertionError, match=rf"names {re.escape(wanted)} and"):
            test_the_suite_workflow_names_only_the_interpreter_the_tree_pins("x", trees)


NAMED = re.compile(r"--python[= ][\"']?(\d+(?:\.\d+)+t?)")
"""An interpreter version a step names on a `uv run` line, quoted or not.

Whatever uv is asked for, patch level and free-threaded suffix included,
so that each cell reading it chooses how much of it to compare: section
10's cells below compare all of it with the pin, and the `test.yml` cell
above compares its `X.Y`, section 1 saying why.
"""

TAKEN = re.compile(r"^\d+(?:\.\d+)+t?$")
"""A `python-version:` given a version rather than a caller's expression."""

NAMES_ONE = (
    ".github/workflows/reusable-api-break.yml",
    ".github/workflows/reusable-audit.yml",
    ".github/workflows/reusable-claude-release.yml",
    ".github/workflows/reusable-docs.yml",
    ".github/workflows/reusable-documented.yml",
    ".github/workflows/reusable-integration-bitcoind.yml",
    ".github/workflows/reusable-lint.yml",
    ".github/workflows/reusable-public-api.yml",
    ".github/workflows/reusable-sourcery.yml",
    ".github/workflows/reusable-version-check.yml",
    ".github/workflows/reusable-wait-for-index.yml",
)
"""The workflows of this repository naming an interpreter literally.

Named rather than counted: a pattern that stopped matching one of them
would leave the rest agreeing with each other and this module green.
Section 10 is what puts a file here -- a job reading neither the
caller's lock nor its project carries its own version -- so an entry is
a decision taken there before it is a line here.
"""


def named(step: dict[str, Any]) -> set[str]:
    """Read the interpreter versions one step names literally.

    From the parsed step rather than from the file's text: a comment
    above a step is gone by the time the parser returns, so a version
    argued about there is not a version named. A `python-version:`
    handed `${{ inputs.python-version }}` names none either -- that
    version is the caller's, which is the other half of section 10's
    rule.

    :param step: the step's own mapping.
    :returns: the versions it names, empty where it names none.
    """
    found = set(NAMED.findall(str(step.get("run", ""))))
    taken = str((step.get("with") or {}).get("python-version", ""))
    if TAKEN.match(taken):
        found.add(taken)
    return found


def naming(root: Path) -> dict[str, set[str]]:
    """Read every workflow of a tree that names an interpreter.

    :param root: the root of the checkout.
    :returns: each such file, named from the root, against the versions
        it carries; a workflow naming none is left out.
    """
    carried = {
        workflow.relative_to(root).as_posix(): {
            version for step in steps(workflow) for version in named(step)
        }
        for workflow in workflows(root)
    }
    return {path: versions for path, versions in carried.items() if versions}


def test_the_workflows_naming_an_interpreter_are_the_ones_recorded(
    trees: dict[str, Path],
) -> None:
    """Section 10: a job names a version only where no calling tree claims it.

    A rename, a rewrapped line and a deleted literal all land here
    rather than in the cell below, which reads the versions of whatever
    this one found: asserting that a literal is the right one says
    nothing the day nothing matches at all.

    :param trees: the checkouts, this one among them.
    """
    found = tuple(sorted(naming(trees[SELF])))
    assert found == NAMES_ONE, (
        f"an interpreter is named in {', '.join(found) or 'no workflow'}, and"
        f" the workflows that carry one are {', '.join(NAMES_ONE)}; "
        + by_hand(SELF, "grep -rn -- '--python \\|python-version:' .github/workflows/")
    )


def test_a_workflow_naming_an_interpreter_names_the_one_this_tree_pins(
    trees: dict[str, Path],
) -> None:
    """Section 10: such a version is the one the tree hosting the file pins.

    The version is not the calling tree's to declare -- the script runs
    `--no-project` over the standard library, so no `requires-python`
    bears on it -- and this is the other end of that sentence: what it
    is instead. A tree pins one interpreter, and a shared workflow
    naming a second would be a version nothing here declares.

    :param trees: the checkouts, this one among them.
    """
    root = trees[SELF]
    pin = pinned(root)
    assert pin, ".python-version names no interpreter"
    elsewhere = {
        path: sorted(versions)
        for path, versions in naming(root).items()
        if versions != {pin}
    }
    assert not elsewhere, (
        f"workflows naming an interpreter other than {pin}: {elsewhere}; "
        + by_hand(SELF, "cat .python-version")
    )


PATCH = re.compile(r"^\d+\.\d+\.\d+$")
"""A version written down to its patch release, `3.11.9` and the like."""

MATRIX = re.compile(r"^\$\{\{\s*matrix\.([\w-]+)\s*\}\}$")
"""A value taken from one key of the job's matrix."""

INPUT = re.compile(r"^\$\{\{\s*inputs\.([\w-]+)\s*\}\}$")
"""A value a called workflow takes from one of its inputs."""

LISTED_INPUT = re.compile(r"^\$\{\{\s*fromJSON\(\s*inputs\.([\w-]+)\s*\)\s*\}\}$")
"""A matrix row a called workflow takes from a JSON list among its inputs."""

EXPRESSION = re.compile(r"\$\{\{\s*(.*?)\s*\}\}")
"""An expression in a `run:` script, closed up so that it splits as one word."""

ENDS = frozenset({"&&", "||", ";", "|", "&"})
"""The words that end one shell command and start the next."""

VALUED = frozenset(
    {
        "--allow-insecure-host",
        "--cache-dir",
        "--color",
        "--config-file",
        "--config-setting",
        "--config-settings-package",
        "--default-index",
        "--directory",
        "--env-file",
        "--exclude-newer",
        "--exclude-newer-package",
        "--extra",
        "--extra-index-url",
        "--find-links",
        "--fork-strategy",
        "--group",
        "--index",
        "--index-strategy",
        "--index-url",
        "--keyring-provider",
        "--link-mode",
        "--no-binary-package",
        "--no-build-isolation-package",
        "--no-build-package",
        "--no-editable-package",
        "--no-extra",
        "--no-group",
        "--no-sources-package",
        "--only-group",
        "--package",
        "--prerelease",
        "--prerelease-package",
        "--project",
        "--python",
        "--python-platform",
        "--refresh-package",
        "--reinstall-package",
        "--resolution",
        "--upgrade-group",
        "--upgrade-package",
        "--with",
        "--with-editable",
        "--with-requirements",
        "-C",
        "-P",
        "-f",
        "-i",
        "-p",
        "-w",
    }
)
"""The `uv run` options whose value is the next word, not the command.

What `uv run --help` lists with a value, which the cell after the
control compares this with: an option missing here would make its value
read as the command, and a pytest run after it uncounted.
"""

HELP_VALUED = re.compile(r"^\s+(?:(-\w), )?(--[\w-]+) <", re.MULTILINE)
"""An option `uv run --help` lists with a value, short form and long."""

SETUP_PYTHON = "actions/setup-python@"
"""The action whose `python-version` is the `python` of the steps after it."""

SETUP_UV = "astral-sh/setup-uv@"
"""The action whose `python-version` sets `UV_PYTHON` for the steps after it."""


def uncommented(line: str) -> str:
    """Drop a shell comment from one line, as the shell reads one.

    A `#` opens a comment where it opens a word outside quotes; inside a
    word or a quote it is a character.

    :param line: one line of a script.
    :returns: the line up to its comment.
    """
    quote = ""
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
        elif char == "\\" and quote != "'":
            escaped = True
        elif quote:
            quote = "" if char == quote else quote
        elif char in "'\"":
            quote = char
        elif char == "#" and (index == 0 or line[index - 1].isspace()):
            return line[:index]
    return line


def commands(run: str) -> list[list[str]]:
    """Split a `run:` script into the words of each of its commands.

    A backslash ending a line continues it, a comment is dropped as
    `uncommented` drops it, and `&&`, `||`, `;`, `|` and `&` end a
    command. A line with an unclosed quote gives no command.

    :param run: the script.
    :returns: each command's words, in order.
    """
    found: list[list[str]] = []
    joined = EXPRESSION.sub(
        lambda match: "${{" + match[1].replace(" ", "") + "}}",
        run.replace("\\\n", " "),
    )
    for line in joined.splitlines():
        lexer = shlex.shlex(uncommented(line), posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.commenters = ""
        try:
            words = list(lexer)
        except ValueError:
            continue
        command: list[str] = []
        for word in [*words, ";"]:
            if word not in ENDS:
                command.append(word)
            elif command:
                found.append(command)
                command = []
    return found


def invocation(words: list[str]) -> tuple[bool, bool, str | None]:
    """Read whether one command runs pytest, and what it asks to run it on.

    pytest is run as `pytest`, as `python -m pytest` or `python3 -m
    pytest`, or after `uv run` and its options as either of those or as
    `-m pytest`; variable assignments may come first. An option of
    `VALUED` takes the next word, and every other option none. An
    interpreter is asked for by `uv run`'s `--python` or `-p`, spaced or
    joined by `=`, or else by a `UV_PYTHON=` assignment among the words
    directly before `uv run`; `env UV_PYTHON=<version>` and an earlier `export`
    are not read.

    :param words: the command's words.
    :returns: whether it runs pytest, whether through `uv run`, and the
        interpreter `uv run` asks for, `None` where it asks for none.
    """
    rest = list(words)
    asked: str | None = None
    while rest and re.match(r"^\w+=", rest[0]):
        name, _, value = rest[0].partition("=")
        asked = value if name == "UV_PYTHON" else asked
        rest = rest[1:]
    through_uv = rest[:2] == ["uv", "run"]
    if not through_uv:
        asked = None
    if through_uv:
        rest = rest[2:]
        while rest and rest[0].startswith("-") and rest[0] not in {"-m", "--module"}:
            option, _, joined = rest[0].partition("=")
            taken = not joined and option in VALUED
            if option in {"--python", "-p"}:
                asked = joined or (rest[1] if len(rest) > 1 else None)
            rest = rest[2:] if taken else rest[1:]
        rest = rest[1:] if rest[:1] in (["-m"], ["--module"]) else rest
    if rest[:1] in (["python"], ["python3"]):
        rest = rest[2:] if rest[1:2] == ["-m"] else []
    return rest[:1] == ["pytest"], through_uv, asked


def callee(called: str, root: Path, shared: Path) -> Path | None:
    """Find the file a job calls, where a checkout here holds it.

    A call into the tree itself starts `./` or `$/`. A call into this
    repository is read in its checkout at the tip, not at the revision
    the call pins.

    :param called: the job's `uses:`.
    :param root: the root of the calling tree.
    :param shared: the root of this repository's checkout.
    :returns: the workflow file, or `None` for a call into anywhere else.
    """
    path = called.split("@", maxsplit=1)[0]
    if path.startswith(("./", "$/")):
        return root / path[2:]
    prefix = f"{ORG}/{SELF}/"
    if path.startswith(prefix):
        return shared / path.removeprefix(prefix)
    return None


def resolved(
    value: object, job: dict[str, Any], inputs: dict[str, set[str]]
) -> set[str]:
    """Read the interpreter versions one value stands for in a job.

    A version stands for itself, and `${{ inputs.<name> }}` for what the
    caller handed as that input. `${{ matrix.<key> }}` stands for the
    key's values in the combinations `combinations` expands. Any other
    expression stands for nothing here.

    :param value: the value as YAML or the script gave it.
    :param job: the job's own mapping, for its matrix.
    :param inputs: what a caller handed, by input; empty for a job no
        workflow calls.
    :returns: the versions, free-threaded suffix included.
    """
    text = str(value)
    if TAKEN.match(text):
        return {text}
    if named_input := INPUT.match(text):
        return set(inputs.get(named_input[1], set()))
    if not (key := MATRIX.match(text)):
        return set()
    return {
        version
        for combination in combinations(job, inputs)
        if key[1] in combination
        for version in resolved(combination[key[1]], {}, inputs)
    }


def combinations(
    job: dict[str, Any], inputs: dict[str, set[str]]
) -> list[dict[str, str]]:
    """Expand a job's matrix into the combinations GitHub runs.

    Each key's row is a list, or `${{ fromJSON(inputs.<name>) }}` for
    the versions a caller handed as that input; any other expression,
    and an input that carries no version, is one value that no
    `exclude` row matches. An `exclude` row drops each combination it
    matches in every key it names. Only then is each `include` row added
    to every remaining combination of the keys' rows whose values it
    does not change, or run as a combination of its own where it fits
    none, which no later row extends, as GitHub's workflow syntax says.

    :param job: the job's own mapping.
    :param inputs: what a caller handed, by input.
    :returns: the combinations, each value as YAML gave it, in text.
    """
    matrix = (job.get("strategy") or {}).get("matrix")
    if not isinstance(matrix, dict):
        return []
    rows = {
        str(name): values(row, inputs)
        for name, row in matrix.items()
        if name not in {"include", "exclude"}
    }
    original = (
        [dict(zip(rows, row, strict=True)) for row in product(*rows.values())]
        if rows
        else []
    )
    for dropped in rules(matrix, "exclude"):
        original = [
            combination
            for combination in original
            if any(combination.get(k) != v for k, v in dropped.items())
        ]
    alone: list[dict[str, str]] = []
    for added in rules(matrix, "include"):
        fits = [
            combination
            for combination in original
            if all(combination[k] == v for k, v in added.items() if k in rows)
        ]
        for combination in fits:
            combination.update(added)
        if not fits:
            alone.append(added)
    return original + alone


def values(row: object, inputs: dict[str, set[str]]) -> list[str]:
    """Read one key's row of a matrix, as `combinations` reads it.

    :param row: the row as YAML gave it.
    :param inputs: what a caller handed, by input.
    :returns: its values, in text.
    """
    if isinstance(row, list):
        return [str(item) for item in row]
    if (listed := LISTED_INPUT.match(str(row))) and listed[1] in inputs:
        return sorted(inputs[listed[1]])
    return [str(row)]


def rules(matrix: dict[str, Any], kind: str) -> list[dict[str, str]]:
    """Read a matrix's `include` or `exclude` rows, in text.

    :param matrix: the matrix's own mapping.
    :param kind: `include` or `exclude`.
    :returns: each row that is a mapping, its keys and values as text.
    """
    return [
        {str(key): str(value) for key, value in row.items()}
        for row in matrix.get(kind) or []
        if isinstance(row, dict)
    ]


def ran(job: dict[str, Any], inputs: dict[str, set[str]]) -> set[str]:
    """Read the interpreters a job's own steps run pytest on.

    A `uv run` asking for one runs on it. A `uv run` asking for none
    runs on the `python-version` of the last `setup-uv` step before it,
    and a bare `pytest` or `python -m pytest` on that of the last
    `setup-python` step; with no such step, each runs on what nothing
    here reads, `.python-version` or the runner's own. Each value is
    read as `resolved` reads it. A step whose `if:` is the literal
    `false` is left out, and an `env:` setting `UV_PYTHON` is not read.

    :param job: the job's own mapping.
    :param inputs: what a caller handed, by input, as `resolved` takes it.
    :returns: the versions, free-threaded suffix included.
    """
    found: set[str] = set()
    uv: set[str] = set()
    python: set[str] = set()
    for step in job.get("steps") or []:
        if skipped(step):
            continue
        uses = str(step.get("uses", ""))
        given = (step.get("with") or {}).get("python-version", "")
        if uses.startswith(SETUP_UV):
            uv = resolved(given, job, inputs)
        elif uses.startswith(SETUP_PYTHON):
            python = resolved(given, job, inputs)
        for words in commands(str(step.get("run", ""))):
            runs, through_uv, asked = invocation(words)
            if not runs:
                continue
            if asked is not None:
                found |= resolved(asked, job, inputs)
            else:
                found |= uv if through_uv else python
    return found


def handed(job: dict[str, Any]) -> dict[str, set[str]]:
    """Read the interpreters a call hands the workflow it calls, by input.

    Each `with:` value, or each entry of one that is a JSON list, read
    as `resolved` reads a value of the calling job.

    :param job: the calling job's own mapping.
    :returns: the versions each input carries, empty sets dropped.
    """
    found: dict[str, set[str]] = {}
    for name, value in (job.get("with") or {}).items():
        try:
            listed = json.loads(str(value))
        except json.JSONDecodeError:
            listed = None
        items = listed if isinstance(listed, list) else [value]
        if carried := {
            version for item in items for version in resolved(item, job, {})
        }:
            found[str(name)] = carried
    return found


def skipped(job: dict[str, Any]) -> bool:
    """Say whether a job's or a step's `if:` is the literal `false`.

    :param job: the job's or the step's own mapping.
    :returns: whether it is skipped whatever the event.
    """
    condition = job.get("if", True)
    return condition is False or EXPRESSION.sub(r"\1", str(condition)) == "false"


def lanes(root: Path, shared: Path) -> set[str]:
    """Read every interpreter a tree's jobs run pytest on, as named.

    A job's own steps count as `ran` reads them. A call counts where the
    workflow it calls is in this tree or in this repository's checkout:
    its jobs' steps count as `ran` reads them, given what `handed` reads
    in the call, so a version handed on counts only where it reaches a
    pytest command there. A call made from that workflow in turn is not
    followed, and a job whose `if:` is the literal `false` is left out.

    :param root: the root of the checkout.
    :param shared: the root of this repository's checkout.
    :returns: the versions, free-threaded suffix included.
    """
    found: set[str] = set()
    for workflow in workflows(root):
        for job in jobs(workflow).values():
            if skipped(job):
                continue
            if "uses" not in job:
                found |= ran(job, {})
                continue
            path = callee(str(job["uses"]), root, shared)
            if path is None or not path.is_file():
                continue
            inputs = handed(job)
            for called in jobs(path).values():
                if "uses" not in called and not skipped(called):
                    found |= ran(called, inputs)
    return found


@pytest.mark.tier(Tier.PYTHON)
def test_a_job_running_the_suite_names_the_patch_the_floor_names(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 1: the floor is the oldest patch a CI job runs, named there.

    A job asking for `X.Y` alone runs the patch its runner supplies, so
    a floor is a patch the suite runs on only where a job names it as
    the interpreter pytest runs on, which `lanes` says how it reads. A
    free-threaded build of the floor's patch is that release, so its `t`
    is dropped. Whether no job runs an older one is left to a reading: a
    workflow may name a second tree's or a dependency's interpreter, as
    section 15 says.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: the parsed files.
    """
    floor, _ = versions(pyprojects[repository])
    command = by_hand(
        repository,
        "grep -n requires-python pyproject.toml;"
        " grep -rn -- '--python \\|python-version' .github/workflows/",
    )
    assert PATCH.match(floor), (
        f"requires-python is >={floor}, which names no patch; " + command
    )
    named = lanes(trees[repository], trees[SELF])
    assert floor in {version.removesuffix("t") for version in named}, (
        f"requires-python is >={floor} and no job running the suite names"
        f" {floor}; " + command
    )


def test_a_floor_no_suite_job_names_is_reported(tmp_path: Path) -> None:
    """The cell above fails on planted trees whose floor pytest never runs on.

    Each form the docstrings of `invocation`, `ran`, `combinations` and
    `lanes` name is planted once naming the floor, and agrees,
    btclib-secp256k1's `uv run` among them. Each near miss is planted
    too, and fails: a floor without its patch, the minor version alone,
    a version pytest does not run on, in the job or in the workflow it
    calls, pytest only mentioned, installed or echoed, an excluded
    matrix combination, a job or a step that never runs, and calls to a
    workflow that runs no pytest or that no checkout here holds.

    :param tmp_path: where the trees are planted.
    """
    suite = (
        "on: workflow_call\njobs:\n  one:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - uses: astral-sh/setup-uv@v1\n        with:\n"
        "          python-version: ${{ inputs.python-version }}\n"
        "      - run: uv run --group test pytest --no-cov\n"
        "  many:\n    runs-on: ubuntu-latest\n    strategy:\n      matrix:\n"
        "        os: ${{ fromJSON(inputs.runners) }}\n"
        "        python: ${{ fromJSON(inputs.python-versions) }}\n"
        "    steps:\n      - run: uv run -p ${{ matrix.python }} -m pytest\n"
        "      - run: uv run --python ${{ inputs.linted }} ruff check .\n"
    )
    other = (
        "on: workflow_call\njobs:\n  check:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: |\n          # pytest is the next job's\n"
        "          python check.py\n"
    )
    call = "    uses: ./.github/workflows/reusable-suite.yml\n    with:\n"
    shared = f"    uses: {ORG}/{SELF}/.github/workflows/reusable-shared.yml@0\n"
    elsewhere = "    uses: someone/else/.github/workflows/reusable-suite.yml@0\n"
    checker = "    uses: ./.github/workflows/reusable-other.yml\n    with:\n"
    steps_ = "    runs-on: ubuntu-latest\n"
    matrix = (
        f'{steps_}    strategy:\n      matrix:\n        python: ["3.11.9", "3.15"]\n'
    )
    on_matrix = "    steps:\n      - run: uv run --python ${{ matrix.python }} pytest\n"
    setup_uv = (
        "    steps:\n      - uses: astral-sh/setup-uv@v1\n"
        '        with:\n          python-version: "3.11.9"\n'
    )
    setup_python = (
        "    steps:\n      - uses: actions/setup-python@v1\n"
        '        with:\n          python-version: "3.11.9"\n'
    )

    included = (
        f"{steps_}    strategy:\n      matrix:\n        include:\n"
        f'          - python: "3.11.9"\n{on_matrix}'
    )
    excluded = (
        matrix.replace(steps_, "")
        + f'        exclude:\n          - python: "3.11.9"\n{steps_}{on_matrix}'
    )
    restored = excluded.replace(
        steps_, f'        include:\n          - python: "3.11.9"\n{steps_}'
    )
    on_os = (
        f"{steps_}    strategy:\n      matrix:\n        os: [OS]\n"
        '        python: ["3.11.9", "3.15"]\n        exclude:\n'
        '          - os: a\n            python: "3.11.9"\n'
        f"{on_matrix}"
    )
    sweep = (
        """      runners: '["macos-latest"]'\n"""
        """      python-versions: '["3.11.9", "3.15"]'\n"""
    )
    alone = (
        f"{steps_}    strategy:\n      matrix:\n        include:\n"
        '          - python: "3.11.9"\n          - python: "3.15"\n'
        f"{on_matrix}"
    )
    apart = (
        f"{steps_}    strategy:\n      matrix:\n        os: [ubuntu-latest]\n"
        "        include:\n"
        '          - os: macos-latest\n            python: "3.11.9"\n'
        '          - os: macos-latest\n            python: "3.12.3"\n'
        f"{on_matrix}"
    )
    added = (
        f"{steps_}    strategy:\n      matrix:\n        os: [a]\n"
        f'        include:\n          - python: "3.11.9"\n{on_matrix}'
    )
    local = (
        "    uses: $/.github/workflows/reusable-suite.yml\n    with:\n"
        '      python-version: "3.11.9"\n'
    )
    skipped_setup = (
        "      - uses: astral-sh/setup-uv@v1\n        if: false\n"
        '        with:\n          python-version: "3.15"\n'
    )

    secp256k1 = (
        "uv run --python 3.11.9 --locked --no-default-groups --group test"
        " --reinstall-package btclib-secp256k1 --no-cache pytest --no-cov"
    )

    def run(script: str) -> str:
        return f"{steps_}    steps:\n      - run: {script}\n"

    missing = "no job running the suite names 3.11.9"
    cases: list[tuple[str, str, str]] = [
        ("3.11.9", f'{call}      python-version: "3.11.9"\n', ""),
        ("3.11.9", call + """      python-versions: '["3.11.9", "3.15"]'\n""", ""),
        ("3.11.9", call + sweep, ""),
        ("3.11.9", alone, ""),
        ("3.11.9", apart, ""),
        ("3.11.9", f'{shared}    with:\n      python-version: "3.11.9"\n', ""),
        (
            "3.11.9",
            matrix.replace(steps_, "")
            + f"{call}      python-version: ${{{{ matrix.python }}}}\n",
            "",
        ),
        ("3.11.9", run("uv run --python 3.11.9 --group test pytest"), ""),
        ("3.11.9", run("uv run --python=3.11.9 python -m pytest"), ""),
        ("3.11.9", run("X=1 uv run -p 3.11.9 pytest -x && echo done"), ""),
        ("3.11.9", run("uv run --python 3.11.9t pytest"), ""),
        ("3.11.9", f"{steps_}{setup_uv}      - run: uv run pytest\n", ""),
        ("3.11.9", f"{steps_}{setup_python}      - run: python -m pytest\n", ""),
        ("3.11.9", matrix + on_matrix, ""),
        ("3.11.9", included, ""),
        ("3.11.9", run(secp256k1), ""),
        ("3.11.9", run("X=a#b uv run --python 3.11.9 -- pytest"), ""),
        ("3.11.9", run("""'uv run -p 3.11.9 pytest --junitxml "report #1.xml"'"""), ""),
        ("3.11", f'{call}      python-version: "3.11"\n', "which names no patch"),
        ("3.11.9", f'{call}      python-version: "3.11"\n', missing),
        ("3.11.9", call + "      python-versions: ${{ inputs.v }}\n", missing),
        ("3.11.9", f'{checker}      python-version: "3.11.9"\n', missing),
        ("3.11.9", f'{elsewhere}    with:\n      python-version: "3.11.9"\n', missing),
        ("3.11.9", run("'uv run --python 3.11.9 python -V  # pytest'"), missing),
        ("3.11.9", run("'true  # ; uv run --python 3.11.9 pytest'"), missing),
        ("3.11.9", run("echo uv run --python 3.11.9 pytest"), missing),
        ("3.11.9", f"{steps_}{setup_python}      - run: pip install pytest\n", missing),
        ("3.11.9", f"{steps_}{setup_python}      - run: uv run pytest\n", missing),
        ("3.11.9", f"{steps_}{setup_uv}      - run: python -m pytest\n", missing),
        (
            "3.11.9",
            run("uv run --python 3.11.9 ruff check .")
            + "      - run: uv run --python 3.15 pytest\n",
            missing,
        ),
        (
            "3.11.9",
            f"{matrix}    steps:\n      - run: uv run --python 3.15 pytest\n",
            missing,
        ),
        ("3.11.9", excluded, missing),
        ("3.11.9", restored, ""),
        ("3.11.9", on_os.replace("OS", "a"), missing),
        ("3.11.9", on_os.replace("OS", "a, b"), ""),
        ("3.11.9", added, ""),
        ("3.11.9", run("UV_PYTHON=3.11.9 pytest"), missing),
        ("3.11.9", f"{steps_}{setup_python}      - run: pytest\n", ""),
        ("3.11.9", run("uv run --python 3.11.9 python3 -m pytest"), ""),
        ("3.11.9", run("uv run --python 3.11.9 --module pytest"), ""),
        ("3.11.9", local, ""),
        ("3.11.9", run("UV_PYTHON=3.11.9 uv run pytest"), ""),
        ("3.11.9", run("UV_PYTHON=3.12.3 uv run -p 3.11.9 pytest"), ""),
        (
            "3.11.9",
            f"{steps_}{setup_uv}      - run: UV_PYTHON=3.12.3 uv run pytest\n",
            missing,
        ),
        (
            "3.11.9",
            f"{steps_}{setup_uv}{skipped_setup}      - run: uv run pytest\n",
            "",
        ),
        (
            "3.11.9",
            run("uv run --python 3.11.9 pytest") + "        if: false\n",
            missing,
        ),
        ("3.11.9", f'{call}      linted: "3.11.9"\n', missing),
        ("3.11.9", "    if: false\n" + run("uv run --python 3.11.9 pytest"), missing),
        (
            "3.11.9",
            run("uv run --index-strategy x --python 3.11.9 ruff check pytest"),
            missing,
        ),
    ]
    hosted = tmp_path / "shared" / ".github" / "workflows"
    hosted.mkdir(parents=True)
    (hosted / "reusable-shared.yml").write_text(suite, encoding="utf-8")
    for index, (floor, job, wanted) in enumerate(cases):
        root = tmp_path / str(index)
        folder = root / ".github" / "workflows"
        folder.mkdir(parents=True)
        (folder / "lane.yml").write_text(
            f"on: push\njobs:\n  lane:\n{job}", encoding="utf-8"
        )
        (folder / "reusable-suite.yml").write_text(suite, encoding="utf-8")
        (folder / "reusable-other.yml").write_text(other, encoding="utf-8")
        trees = {"x": root, SELF: tmp_path / "shared"}
        parsed = {"x": {"project": {"requires-python": f">={floor}"}}}
        if not wanted:
            test_a_job_running_the_suite_names_the_patch_the_floor_names(
                "x", trees, parsed
            )
            continue
        with pytest.raises(AssertionError, match=wanted):
            test_a_job_running_the_suite_names_the_patch_the_floor_names(
                "x", trees, parsed
            )


def test_valued_is_what_uv_run_help_lists() -> None:
    """`VALUED` names the options `uv run --help` lists with a value.

    The uv this runs is the one running the suite, which `UV` names. An
    option uv adds lands here as a difference rather than as a pytest
    run nobody counted.
    """
    uv = os.environ.get("UV") or shutil.which("uv")
    assert uv, "no uv to ask: UV is unset and none is on PATH"
    listed = subprocess.run(
        [uv, "run", "--help"], capture_output=True, check=True, encoding="utf-8"
    ).stdout
    found = {
        option for pair in HELP_VALUED.findall(listed) for option in pair if option
    }
    assert "--python" in found, f"uv run --help read as {sorted(found)}"
    assert found == VALUED, (
        f"uv run --help lists {sorted(found - VALUED)} beyond VALUED, and"
        f" VALUED holds {sorted(VALUED - found)} it does not list"
    )


def test_combinations_read_the_workflow_syntax_example() -> None:
    """`combinations` gives the jobs GitHub's own matrix example lists.

    The example of *Running variations of jobs in a workflow*, where an
    `include` row that fits no original combination runs on its own and
    a later row does not extend it.
    """
    matrix = {
        "fruit": ["apple", "pear"],
        "animal": ["cat", "dog"],
        "include": [
            {"color": "green"},
            {"color": "pink", "animal": "cat"},
            {"fruit": "apple", "shape": "circle"},
            {"fruit": "banana"},
            {"fruit": "banana", "animal": "cat"},
        ],
    }
    expected = [
        {"fruit": "apple", "animal": "cat", "color": "pink", "shape": "circle"},
        {"fruit": "apple", "animal": "dog", "color": "green", "shape": "circle"},
        {"fruit": "pear", "animal": "cat", "color": "pink"},
        {"fruit": "pear", "animal": "dog", "color": "green"},
        {"fruit": "banana"},
        {"fruit": "banana", "animal": "cat"},
    ]
    assert combinations({"strategy": {"matrix": matrix}}, {}) == expected
