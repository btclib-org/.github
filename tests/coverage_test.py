# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 8's clauses on what a floor measures.

The first is the one on a statement only some invocations execute. Such
a statement is covered on the invocations that execute it and
reads as a miss on the others, so under a floor with no slack the
runner's flags decide whether the gate passes. The section answers with
a test of the statement rather than a pragma over it, and this asks the
trees for that test.

What a suite holds of that class is a hook pytest calls under one set of
flags and not another. `pytest_report_header` is one: pytest calls it to
write the header block, and a run under `-q` or under `--no-header`
writes no such block and makes no such call. A hook pytest calls
whatever the flags -- `pytest_configure`, `pytest_generate_tests` -- is
outside the class, and a check keyed on a conftest hook no test module
names would report those too, in trees where nothing is wrong.

The second is the one on the scripts under `.github/scripts`: a tree
holding Python scripts there names the directory in
`[tool.coverage.run]`'s `source`, and coverage reports each of them
unrun, so its floor reaches them. A script the tree lists in `omit` is
not asked about, as coverage does not report it. Whether it carries its
reason is a comment of `pyproject.toml`, and prose is left to a reader.

Asked of a tree that declares a coverage floor rather than of a tier:
section 8 reads which gate applies off what the tree installs, and where
no total is gated on, no flag turns a hook into a red build.
"""

from __future__ import annotations

import ast
import re
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any

import pytest

from . import ROOT, by_hand, output, tracked

if TYPE_CHECKING:
    from pathlib import Path

TESTS = "tests"
"""Section 2's directory for a tree's suite."""

CONFTEST = "conftest.py"
"""pytest's own file, which section 7 puts under `tests/`."""

BY_FLAG = ("pytest_report_header",)
"""The hooks whose invocation the runner's flags decide.

A name belongs here where pytest's call to the hook is behind a flag
rather than in the protocol every run follows. The class is the property
section 8 names, so a hook pytest gives that shape next enters by being
written here.
"""

BY_HAND = f"git grep -nE '{'|'.join(BY_FLAG)}' -- '{TESTS}'"
"""How the same question is decided in a checkout.

The conftest's definition and every test module naming it come back
together, so a single line naming the conftest is the finding.
"""

HOOK = BY_FLAG[0]
"""A hook of the class, for the plantings below."""

WHATEVER_THE_FLAGS = "pytest_configure"
"""A hook pytest calls on every invocation, which the class leaves out."""

SILENT = "from . import nothing"
"""A planted test module that names no hook."""

SCRIPTS = ".github/scripts"
"""Section 8's directory of a tree's workflow scripts, as `source` names it."""

PYTHON_SCRIPTS = f"{SCRIPTS}/*.py"
"""The pathspec of the scripts the clause is about."""

MODULE_NAME = re.compile(r"[^.#~!$@%^&*()+=,]+\.pyw?")
"""The file names `find_python_files` yields, which coverage reports unrun."""

NAMESPACES = {"include_namespace_packages": True}
"""The `[tool.coverage.report]` setting that reports a subdirectory with no
`__init__.py`."""

GLOB: list[tuple[re.Pattern[str], str | None]] = [
    (re.compile(token), regex)
    for token, regex in [
        (r"\*\*\*+", None),
        (r"[^/]+\*\*+", None),
        (r"\*\*+[^/]+", None),
        (r"\*\*/\*\*", None),
        (r"^\*+/", r"(.*[/\\\\])?"),
        (r"/\*+$", r"[/\\\\].*"),
        (r"\*\*/", r"(.*[/\\\\])?"),
        (r"/", r"[/\\\\]"),
        (r"\*", r"[^/\\\\]*"),
        (r"\?", r"[^/\\\\]"),
        (r"\[.*?\]", r"\g<0>"),
        (r"[a-zA-Z0-9_-]+", r"\g<0>"),
        (r"[\[\]]", None),
        (r"[\s\S]", r"\\\g<0>"),
    ]
]
"""How coverage turns an `omit` pattern into a regex, token by token.

`G2RX_TOKENS` in `coverage/files.py`, in its order: the first token that
matches is taken, and one whose regex is None is refused.
"""


def defined(conftest: Path) -> set[str]:
    """Return the names of the functions a file defines.

    The source is parsed rather than the module imported: nothing
    installs the trees this suite clones, so a conftest importing the
    package it configures could not be imported to be asked.

    :param conftest: the file to read.
    :returns: every function name it defines, nested ones included.
    """
    tree = ast.parse(conftest.read_text(encoding="utf-8"), filename=str(conftest))
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    }


def stranded(root: Path) -> list[str]:
    """Return the hooks of the class a tree leaves to the runner's flags.

    Every `conftest.py` under `tests/` is read, a per-directory one being
    as much pytest's file as the suite's own, and a hook is exercised
    where a test module names it -- which is what a test of the statement
    does, whether it calls the hook or reads a run's output for it.

    :param root: the root of the checkout.
    :returns: the hooks it defines and no test module names, in the order
        `BY_FLAG` gives them.
    """
    tests = root / TESTS
    hooks = {name for path in sorted(tests.rglob(CONFTEST)) for name in defined(path)}
    modules = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(tests.rglob("*_test.py"))
    )
    return [hook for hook in BY_FLAG if hook in hooks and hook not in modules]


def floor(config: dict[str, Any]) -> float | None:
    """Return the coverage floor a parsed `pyproject.toml` declares.

    :param config: the parsed file, empty where the tree keeps none.
    :returns: what `fail_under` is set to, or None where nothing is.
    """
    report = config.get("tool", {}).get("coverage", {}).get("report", {})
    total: float | None = report.get("fail_under")
    return total


@pytest.mark.integration
def test_a_hook_the_flags_can_strand_carries_a_test_of_its_own(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 8: the statement is exercised where a floor makes it red.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: each tree's parsed `pyproject.toml`.
    """
    total = floor(pyprojects.get(repository, {}))
    if total is None:
        pytest.skip(f"{repository} declares no coverage floor")
    left = stranded(trees[repository])
    assert not left, (
        f"{TESTS}/{CONFTEST} defines {left}, which pytest calls on some"
        f" invocations and not others, and no test module names it: under"
        f" fail_under = {total} the flags decide whether the gate passes; "
        + by_hand(repository, BY_HAND)
    )


def plant(root: Path, hook: str, module: str) -> None:
    """Build a tree whose suite defines a hook and holds one test module.

    :param root: where to build it.
    :param hook: the hook the conftest defines.
    :param module: the test module's source.
    """
    tests = root / TESTS
    tests.mkdir(parents=True)
    body = f"def {hook}() -> str:\n    return ''\n"
    (tests / CONFTEST).write_text(body, encoding="utf-8")
    (tests / "planted_test.py").write_text(f"{module}\n", encoding="utf-8")


@pytest.mark.parametrize(
    ("hook", "module", "expected"),
    [
        pytest.param(HOOK, SILENT, [HOOK], id="stranded"),
        pytest.param(HOOK, f"from .conftest import {HOOK}", [], id="tested"),
        pytest.param(WHATEVER_THE_FLAGS, SILENT, [], id="unconditional"),
    ],
)
def test_a_planted_tree_reddens_only_where_the_flags_can_strand_a_hook(
    tmp_path: Path,
    hook: str,
    module: str,
    expected: list[str],
) -> None:
    """Each state a tree can be in against the clause, and the finding.

    A hook of the class no test module names is the finding; the same
    hook named by one is what says the reading cannot report every tree
    that defines a hook; and a hook pytest calls whatever the flags is
    outside the class, which is what keeps this off the trees the
    section has nothing to say about.

    :param tmp_path: where the tree is built.
    :param hook: the hook the planted conftest defines.
    :param module: the planted test module's source.
    :param expected: what `stranded` owes for that tree.
    """
    plant(tmp_path, hook, module)
    assert stranded(tmp_path) == expected


def unmeasured(root: Path, config: dict[str, Any]) -> list[str]:
    """Return the Python scripts under `.github/scripts` a floor leaves out.

    `source` is compared as a path, so `./.github/scripts` and
    `.github/scripts/` name the directory as coverage reads them. A script
    is still left out where coverage would not report it unrun, as section
    8 says of a subdirectory and `discovered` of a name. A script `omit`
    matches is not returned, whatever `source` names: section 8 lets a
    tree list it there.

    :param root: the root of the checkout.
    :param config: its parsed `pyproject.toml`, empty where it keeps none.
    :returns: the tracked scripts `omit` does not match, where `source`
        does not name the directory; where it does, those of them
        coverage would not report.
    """
    coverage = config.get("tool", {}).get("coverage", {})
    run = coverage.get("run", {})
    omit = omission(root, run.get("omit", []))
    paths = [PurePosixPath(script) for script in tracked(root, PYTHON_SCRIPTS)]
    packages = {path.parent for path in paths if path.name == "__init__.py"}
    kept = [path for path in paths if not omit.match(str((root / path).resolve()))]
    directory = (root / SCRIPTS).resolve()
    if all((root / entry).resolve() != directory for entry in run.get("source", [])):
        return [str(path) for path in kept]
    namespaces = bool(coverage.get("report", {}).get("include_namespace_packages"))
    return [
        str(path)
        for path in kept
        if not discovered(path, packages, namespaces=namespaces)
    ]


def omission(root: Path, omit: list[str]) -> re.Pattern[str]:
    """Compile `[tool.coverage.run]`'s `omit` as coverage matches it.

    coverage matches each pattern against a file's absolute, resolved
    path, and the whole path. A pattern that opens with neither `*` nor
    `?` is also tried resolved against the directory coverage runs in,
    taken here as the root (`prep_patterns`). A pattern with no `/`
    matches a file name in any directory (`_glob_to_regex`). `GLOB` says
    what each token becomes. A `$VAR` in a pattern is left as written,
    where coverage substitutes it from the environment.

    An `__init__.py` that `omit` matches still makes its directory a
    package, since coverage applies `omit` to the files it finds and not
    to the walk.

    :param root: the root of the checkout, where coverage runs.
    :param omit: the patterns, as `pyproject.toml` writes them.
    :returns: a regex whose `match` says whether a resolved path is
        omitted, which matches no path where `omit` is empty.
    :raises ValueError: where coverage refuses a pattern.
    """
    patterns = [
        variant
        for pattern in omit
        for variant in (
            [pattern]
            if pattern.startswith(("*", "?"))
            else [pattern, str((root / pattern).resolve())]
        )
    ]
    regexes: list[str] = []
    for pattern in patterns:
        glob = pattern.replace("\\", "/")
        if "/" not in glob:
            glob = f"**/{glob}"
        parts: list[str] = []
        position = 0
        while position < len(glob):
            found, regex = next(
                (match, regex)
                for token, regex in GLOB
                if (match := token.match(glob, position))
            )
            if regex is None:
                msg = f"coverage refuses the omit pattern {pattern!r}: {found[0]!r}"
                raise ValueError(msg)
            parts.append(found.expand(regex))
            position = found.end()
        regexes.append(f"(?:{''.join(parts)})")
    return re.compile(rf"(?:{'|'.join(regexes)})\Z" if regexes else r"(?!)")


def discovered(
    path: PurePosixPath, packages: set[PurePosixPath], *, namespaces: bool
) -> bool:
    """Say whether coverage reports a script under `.github/scripts` unrun.

    The name test is coverage's own, in `coverage.files.find_python_files`,
    and `include_namespace_packages` does not lift it.

    :param path: the script, relative to the root of the checkout.
    :param packages: the directories that hold an `__init__.py`.
    :param namespaces: whether `[tool.coverage.report]` sets
        `include_namespace_packages`.
    :returns: whether coverage's name test takes the name, and each
        directory between `.github/scripts` and the script holds an
        `__init__.py` or `namespaces` is set.
    """
    if not MODULE_NAME.fullmatch(path.name):
        return False
    top = PurePosixPath(SCRIPTS)
    return namespaces or all(
        directory in packages for directory in path.parents if top in directory.parents
    )


@pytest.mark.integration
def test_a_floor_measures_the_scripts_under_github_scripts(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 8: a floor reaches the Python scripts a tree holds.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: each tree's parsed `pyproject.toml`.
    """
    config = pyprojects.get(repository, {})
    total = floor(config)
    if total is None:
        pytest.skip(f"{repository} declares no coverage floor")
    left = unmeasured(trees[repository], config)
    assert not left, (
        f"fail_under = {total} says nothing of {left}: [tool.coverage.run]"
        f" source does not name {SCRIPTS}, or coverage would not report them"
        " unrun, for a directory with no __init__.py or a name it skips; "
        + by_hand(
            repository,
            f"git ls-files '{PYTHON_SCRIPTS}'; grep -n '^source' pyproject.toml",
        )
    )


@pytest.mark.parametrize(
    ("scripts", "source", "report", "expected"),
    [
        pytest.param(["s.py"], ["pkg", "tests"], {}, [f"{SCRIPTS}/s.py"], id="omitted"),
        pytest.param(["s.py"], ["pkg", "tests", SCRIPTS], {}, [], id="named"),
        pytest.param(
            ["s.py"], ["pkg", "tests", f"./{SCRIPTS}"], {}, [], id="dot-slash"
        ),
        pytest.param(
            ["s.py"], ["pkg", "tests", f"{SCRIPTS}/"], {}, [], id="trailing-slash"
        ),
        pytest.param([], ["pkg", "tests"], {}, [], id="none"),
        pytest.param(
            ["s.py", "tools/t.py"],
            ["pkg", "tests", SCRIPTS],
            {},
            [f"{SCRIPTS}/tools/t.py"],
            id="subdirectory",
        ),
        pytest.param(
            ["tools/__init__.py", "tools/t.py"],
            ["pkg", "tests", SCRIPTS],
            {},
            [],
            id="subpackage",
        ),
        pytest.param(
            ["tools/deep/t.py", "tools/deep/__init__.py"],
            ["pkg", "tests", SCRIPTS],
            {},
            [f"{SCRIPTS}/tools/deep/__init__.py", f"{SCRIPTS}/tools/deep/t.py"],
            id="package-below-a-plain-directory",
        ),
        pytest.param(
            ["tools/t.py"],
            ["pkg", "tests", SCRIPTS],
            NAMESPACES,
            [],
            id="namespace-packages",
        ),
        pytest.param(
            ["s.py", "a.b.py"],
            ["pkg", "tests", SCRIPTS],
            {},
            [f"{SCRIPTS}/a.b.py"],
            id="unimportable-name",
        ),
        pytest.param(
            ["tools/a.b.py", "tools/t.py"],
            ["pkg", "tests", SCRIPTS],
            NAMESPACES,
            [f"{SCRIPTS}/tools/a.b.py"],
            id="unimportable-name-in-a-namespace-package",
        ),
        pytest.param(
            ["café.py", 'a"b.py'],
            ["pkg", "tests", SCRIPTS],
            {},
            [],
            id="a-name-git-quotes",
        ),
    ],
)
def test_a_planted_tree_reddens_only_where_source_leaves_a_script_out(
    tmp_path: Path,
    scripts: list[str],
    source: list[str],
    report: dict[str, bool],
    expected: list[str],
) -> None:
    """Each state a tree can be in against the clause, and the finding.

    :param tmp_path: where the tree is built.
    :param scripts: the Python scripts the planted tree holds.
    :param source: what its `source` names.
    :param report: its `[tool.coverage.report]`, beside the floor.
    :param expected: what `unmeasured` owes for that tree.
    """
    stage(tmp_path, scripts)
    config = {"tool": {"coverage": {"run": {"source": source}, "report": report}}}
    assert unmeasured(tmp_path, config) == expected


@pytest.mark.parametrize(
    ("scripts", "omit", "expected"),
    [
        pytest.param(
            ["tools/gen.py"], [f"{SCRIPTS}/tools/gen.py"], [], id="the-script"
        ),
        pytest.param(
            ["tools/gen.py"], [f"./{SCRIPTS}/tools/gen.py"], [], id="dot-slash"
        ),
        pytest.param(["tools/gen.py"], [f"{SCRIPTS}/*"], [], id="its-tree"),
        pytest.param(["tools/gen.py"], ["gen.py"], [], id="its-name"),
        pytest.param(["tools/gen.py"], ["*/tools/*"], [], id="a-leading-star"),
        pytest.param(
            ["tools/gen.py"], [f"{SCRIPTS}/**/gen.py"], [], id="a-double-star"
        ),
        pytest.param(
            ["tools/gen.py"],
            [f"{SCRIPTS}/*.py"],
            [f"{SCRIPTS}/tools/gen.py"],
            id="a-star-stays-in-its-directory",
        ),
        pytest.param(
            ["tools/gen.py"],
            ["*/site-packages/*", "tests/integration/*"],
            [f"{SCRIPTS}/tools/gen.py"],
            id="section-8s-example",
        ),
        pytest.param(
            ["tools/__init__.py", "tools/gen.py"],
            [f"{SCRIPTS}/tools/__init__.py"],
            [],
            id="an-omitted-init-still-makes-a-package",
        ),
    ],
)
def test_a_script_omit_matches_is_not_reported(
    tmp_path: Path,
    scripts: list[str],
    omit: list[str],
    expected: list[str],
) -> None:
    """Section 8 lets a tree list in `omit` a script coverage would not report.

    :param tmp_path: where the tree is built.
    :param scripts: the Python scripts the planted tree holds.
    :param omit: what its `[tool.coverage.run]` omits.
    :param expected: what `unmeasured` owes for that tree.
    """
    stage(tmp_path, scripts)
    config = {"tool": {"coverage": {"run": {"source": [SCRIPTS], "omit": omit}}}}
    assert unmeasured(tmp_path, config) == expected


def test_a_script_omit_matches_is_not_reported_where_source_misses_it(
    tmp_path: Path,
) -> None:
    """Where `source` misses the directory, an omitted script is no finding.

    :param tmp_path: where the tree is built.
    """
    stage(tmp_path, ["s.py", "t.py"])
    run = {"source": ["pkg"], "omit": [f"{SCRIPTS}/s.py"]}
    assert unmeasured(tmp_path, {"tool": {"coverage": {"run": run}}}) == [
        f"{SCRIPTS}/t.py"
    ]


@pytest.mark.parametrize("pattern", ["***", f"{SCRIPTS}/x**", "**/**", "a[b"])
def test_an_omit_pattern_coverage_refuses_is_refused(pattern: str) -> None:
    """A pattern coverage refuses is refused here too, not read some other way.

    :param pattern: the `omit` entry.
    """
    with pytest.raises(ValueError, match="coverage refuses"):
        omission(ROOT, [pattern])


def stage(root: Path, scripts: list[str]) -> None:
    """Build a tree that tracks some scripts under `.github/scripts`.

    The scripts are added to the index of a repository of their own,
    since what the reading lists is what git tracks, and a file beside
    them in another language is the control on the pathspec.

    :param root: where to build it.
    :param scripts: the Python scripts, relative to `.github/scripts`.
    """
    directory = root / SCRIPTS
    for script in [*scripts, "render.mjs"]:
        (directory / script).parent.mkdir(parents=True, exist_ok=True)
        (directory / script).write_text("", encoding="utf-8")
    output("git", "-C", str(root), "init", "--quiet")
    output("git", "-C", str(root), "add", "--all")
