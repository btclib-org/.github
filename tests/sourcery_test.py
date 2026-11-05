# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 10's `sourcery` job, read off `reusable-sourcery.yml` and its caller.

`hooks_test.py` asks every Python tree for a caller and a `.sourcery.yaml`.
This reads the callee and this tree's caller: what the job may touch,
what it pins, how the base branch reaches its script, and which files
its script hands Sourcery. That last is asked by running the script in a
repository built by the test, with `uvx` stubbed to write down what it
was asked, so what is read is the script's own choice and not a reading
of its text. It also holds `hooks_test.py`'s reading of an `ignore:` entry
to what Sourcery skipped, and its reading of the pins that let one hide a
vendored file.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import pytest

from . import ROOT
from .hooks_test import (
    PIN_WORKFLOW,
    Asks,
    caller_departures,
    git_blob,
    ignored,
    pinned,
    pins,
)
from .workflows_test import document, steps

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

WORKFLOWS = ROOT / ".github" / "workflows"
CALLEE = WORKFLOWS / "reusable-sourcery.yml"
CALLER = WORKFLOWS / "sourcery.yml"
LINT = WORKFLOWS / "lint.yml"

READ_ONLY = {"contents": "read"}
"""The one permission section 10 gives the job: it reads the tree."""

VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
"""A release of Sourcery, which the job env names once."""

REVIEW = "Review what the pull request changes"
"""The callee's step that chooses what Sourcery reads, by name."""


def _review() -> dict[str, Any]:
    found = [step for step in steps(CALLEE) if step.get("name") == REVIEW]
    assert len(found) == 1, f"{CALLEE.name} has {len(found)} steps named {REVIEW!r}"
    return found[0]


def test_the_job_reads_the_tree_and_writes_nothing() -> None:
    """Both files ask `contents: read` and no job widens it."""
    for workflow in (CALLEE, CALLER):
        parsed = document(workflow)
        assert parsed.get("permissions") == READ_ONLY, workflow.name
        widened = [
            name
            for name, job in (parsed.get("jobs") or {}).items()
            if "permissions" in job
        ]
        assert not widened, f"{workflow.name}: {widened} set their own permissions"


def test_the_actions_are_the_ones_lint_yml_pins() -> None:
    """Each action the callee uses is pinned to the commit `lint.yml` uses."""
    pinned = {step["uses"] for step in steps(LINT) if "uses" in step}
    used = [step["uses"] for step in steps(CALLEE) if "uses" in step]
    assert used, f"{CALLEE.name} uses no action"
    assert set(used) <= pinned, sorted(set(used) - pinned)


def test_the_checkout_reads_history_and_keeps_no_credential() -> None:
    """`fetch-depth: 0` for the merge base, and no token left in the clone."""
    checkouts = [
        step.get("with") or {}
        for step in steps(CALLEE)
        if str(step.get("uses", "")).startswith("actions/checkout@")
    ]
    assert checkouts == [{"fetch-depth": 0, "persist-credentials": False}]


def test_no_expression_is_pasted_into_a_script() -> None:
    """A value reaches a `run:` through `env:`, never as `${{ }}` in it."""
    pasted = [
        f"{workflow.name}: {step.get('name')}"
        for workflow in (CALLEE, CALLER)
        for step in steps(workflow)
        if "${{" in str(step.get("run", ""))
    ]
    assert not pasted, pasted


def test_the_version_is_set_once_and_nothing_fixes() -> None:
    """One `SOURCERY_VERSION`, one `sourcery==` reading it, and no `--fix`."""
    text = CALLEE.read_text(encoding="utf-8")
    (job,) = (document(CALLEE).get("jobs") or {}).values()
    assert VERSION.match(str((job.get("env") or {}).get("SOURCERY_VERSION", "")))
    assert text.count("SOURCERY_VERSION:") == 1
    assert re.findall(r"sourcery==\S*", text) == ['sourcery==$SOURCERY_VERSION"']
    assert "--fix" not in str(_review()["run"])
    lines_only = re.search(r"--diff(?![\w-])", str(_review()["run"]))
    assert lines_only is None, "--diff reads lines, not files"


def test_this_trees_caller_is_section_10s() -> None:
    """This tree's `sourcery.yml` calls the job as `hooks_test.py` asks."""
    assert caller_departures(ROOT) == []


QUIET = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
"""No configuration of the machine reaches the repository a test builds."""


def _git(tree: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(tree), *args],
        capture_output=True,
        encoding="utf-8",
        check=True,
        env={**os.environ, **QUIET},
    )


BASE = ("base.py", ".sourcery.yaml", ".github/workflows/sourcery.yml")
"""What the base branch of the repository a test builds holds."""

ASKED = ["--python", "3.15", "--from", "sourcery==1.46.0", "sourcery", "review"]
"""What the script asks `uvx` before the files: the stub records it."""

RUN = "\x1e"
"""What the stub writes before each run's arguments."""


def _reviewed(
    tmp_path: Path,
    added: tuple[str, ...] = (),
    moved: tuple[tuple[str, str], ...] = (),
    removed: tuple[str, ...] = (),
    base: str = "main",
) -> tuple[int, list[list[str]]]:
    """Run the callee's script over a pull request built from the arguments.

    :param tmp_path: where the repository and the stub go.
    :param added: the paths the pull request adds or rewrites.
    :param moved: the renames it makes, each a source and a destination.
    :param removed: the paths it deletes.
    :param base: what `BASE_REF` carries.
    :returns: the script's exit code, and the arguments `uvx` was given
        at each run.
    """
    tree = tmp_path / "tree"
    tree.mkdir()
    _git(tree, "init", "--quiet", "--initial-branch=main")
    _git(tree, "config", "user.email", "probe@example.invalid")
    _git(tree, "config", "user.name", "probe")
    for name in BASE:
        (tree / name).parent.mkdir(parents=True, exist_ok=True)
        (tree / name).write_text("x = 1\n", encoding="utf-8")
    _git(tree, "add", ".")
    _git(tree, "commit", "--quiet", "-m", "base")
    _git(tree, "update-ref", "refs/remotes/origin/main", "HEAD")
    _git(tree, "switch", "--quiet", "-c", "change")
    for name in added:
        (tree / name).parent.mkdir(parents=True, exist_ok=True)
        (tree / name).write_text("y = 2\n", encoding="utf-8")
        _git(tree, "add", "--", name)
    for source, destination in moved:
        _git(tree, "mv", "--", source, destination)
    for name in removed:
        _git(tree, "rm", "--quiet", "--", name)
    _git(tree, "commit", "--quiet", "--allow-empty", "-m", "change")
    stub = tmp_path / "stub"
    stub.mkdir()
    log = tmp_path / "log"
    (stub / "uvx").write_text(
        "#!/bin/sh\nprintf '\\036\\0' >> \"$STUBLOG\"\n"
        'printf \'%s\\0\' "$@" >> "$STUBLOG"\n',
        encoding="utf-8",
    )
    (stub / "uvx").chmod(0o755)
    runner_temp = tmp_path / "runner_temp"
    runner_temp.mkdir()
    script = tmp_path / "review.sh"
    script.write_text(str(_review()["run"]), encoding="utf-8")
    ran = subprocess.run(
        ["bash", "--noprofile", "--norc", "-eo", "pipefail", str(script)],
        capture_output=True,
        cwd=tree,
        encoding="utf-8",
        check=False,
        env={
            **os.environ,
            **QUIET,
            "PATH": f"{stub}{os.pathsep}{os.environ['PATH']}",
            "STUBLOG": str(log),
            "RUNNER_TEMP": str(runner_temp),
            "BASE_REF": base,
            "SOURCERY_VERSION": "1.46.0",
        },
    )
    runs: list[list[str]] = []
    if log.is_file():
        for argument in log.read_text(encoding="utf-8").split("\0")[:-1]:
            if argument == RUN:
                runs.append([])
            else:
                runs[-1].append(argument)
    return ran.returncode, runs


WHOLE = [[*ASKED, "--check", "."]]
"""What `uvx` is asked for the whole tree."""


def _files(*names: str) -> list[list[str]]:
    """Spell what `uvx` is asked for the files named.

    :param names: the files, in the order git prints them.
    :returns: the one run reading them.
    """
    return [[*ASKED, "--check", "--", *names]]


@pytest.mark.parametrize(
    ("added", "moved", "removed", "wanted"),
    [
        pytest.param(("src/one.py",), (), (), _files("src/one.py"), id="python"),
        pytest.param(
            ("src/b.py", "docs/a.md", "src/a.py"),
            (),
            (),
            _files("src/a.py", "src/b.py"),
            id="python-among-prose",
        ),
        pytest.param(
            ("--diff=touch PWNED #.py",),
            (),
            (),
            _files("--diff=touch PWNED #.py"),
            id="option-named",
        ),
        pytest.param(("café.py",), (), (), _files("café.py"), id="non-ascii"),
        pytest.param(
            ("a b.py", "n\nl.py"), (), (), _files("a b.py", "n\nl.py"), id="blank"
        ),
        pytest.param((), (), ("base.py",), [], id="deleted-python"),
        pytest.param(("docs/sourcery.md",), (), (), [], id="prose"),
        pytest.param(("tests/.sourcery.yaml",), (), (), [], id="nested-config"),
        pytest.param((".sourcery.yaml",), (), (), WHOLE, id="config"),
        pytest.param(
            (".sourcery.yaml", "src/one.py"), (), (), WHOLE, id="config-and-python"
        ),
        pytest.param(
            (".github/workflows/reusable-sourcery.yml",), (), (), WHOLE, id="callee"
        ),
        pytest.param((".github/workflows/sourcery.yml",), (), (), WHOLE, id="caller"),
        pytest.param(
            (), ((".sourcery.yaml", "x.sourcery.yaml"),), (), WHOLE, id="config-renamed"
        ),
        pytest.param(
            (),
            ((".github/workflows/sourcery.yml", ".github/workflows/ci.yml"),),
            (),
            WHOLE,
            id="caller-renamed",
        ),
        pytest.param(
            (),
            (("base.py", "moved.py"),),
            (),
            _files("moved.py"),
            id="python-renamed",
        ),
    ],
)
def test_the_review_reads_the_changed_python_files_or_the_whole_tree(
    tmp_path: Path,
    added: tuple[str, ...],
    moved: tuple[tuple[str, str], ...],
    removed: tuple[str, ...],
    wanted: list[list[str]],
) -> None:
    """The changed Python files, whole; nothing; or all, where rules moved.

    Files and not `--diff`, which reads the changed lines of them alone.
    A rename is read as the deletion and the addition it is, so a
    `.sourcery.yaml` renamed away reads as the file changing. A name
    reaches Sourcery as it is, a space, a newline or a non-ASCII letter
    in it, and after `--`, so a name like an option is a file. The whole
    tree is read once, and no file after it.

    :param tmp_path: where the repository is built.
    :param added: the paths the pull request adds or rewrites.
    :param moved: the renames it makes.
    :param removed: the paths it deletes.
    :param wanted: the arguments `uvx` is to be given at each run, no
        run where it is not to run.
    """
    code, asked = _reviewed(tmp_path, added, moved, removed)
    assert code == 0
    assert asked == wanted


def test_the_review_refuses_an_event_with_no_base(tmp_path: Path) -> None:
    """No base branch is a failure naming it, and Sourcery is not run.

    :param tmp_path: where the repository is built.
    """
    code, asked = _reviewed(tmp_path, ("src/one.py",), base="")
    assert code == 1
    assert not asked


def test_the_review_stops_where_git_cannot_read_the_base(tmp_path: Path) -> None:
    """A base branch git cannot resolve fails the step, and Sourcery is not run.

    :param tmp_path: where the repository is built.
    """
    code, asked = _reviewed(tmp_path, ("src/one.py",), base="nosuch")
    assert code != 0
    assert not asked


LAYOUT = (
    "a.py",
    "pkg/conftest.py",
    "pkg/helpers/one.py",
    "tests/_data/z.py",
    "tests/a_test.py",
    "tests/unit/_data/sub/y.py",
    "tests/unit/_data/x.py",
)
"""The tree Sourcery was asked about, each file holding one finding."""

DATA = ["tests/_data/z.py", "tests/unit/_data/sub/y.py", "tests/unit/_data/x.py"]
DEEPER = DATA[1:]
TESTS = [path for path in LAYOUT if path.startswith("tests/")]


@pytest.mark.parametrize(
    ("entry", "skipped"),
    [
        pytest.param("tests/**/_data", DEEPER, id="double-star-directory"),
        pytest.param("tests/*/_data", DEEPER, id="star-directory"),
        pytest.param("tests/**/_data/", DEEPER, id="directory-glob-slash"),
        pytest.param("tests/_data/", DATA[:1], id="directory-slash"),
        pytest.param("unit/_data", DEEPER, id="directory-mid-path"),
        pytest.param("_data", DATA, id="directory-name"),
        pytest.param("**/_data/**", DATA, id="double-star-around"),
        pytest.param("tests/**", TESTS, id="double-star-under"),
        pytest.param("./tests", TESTS, id="dot-slash"),
        pytest.param("**/*.py", list(LAYOUT[1:]), id="double-star-file"),
        pytest.param("pkg/*.py", ["pkg/conftest.py"], id="star-file"),
        pytest.param("*/one.py", ["pkg/helpers/one.py"], id="star-parent"),
        pytest.param("*.py", list(LAYOUT), id="star-any-file"),
        pytest.param("conftest.py/", ["pkg/conftest.py"], id="file-slash"),
        pytest.param("pkg/**/conftest.py", [], id="double-star-not-empty"),
        pytest.param(".", list(LAYOUT), id="root"),
        pytest.param("./", list(LAYOUT), id="root-slash"),
        pytest.param("tests/./_data", DATA[:1], id="dot-segment"),
        pytest.param("pkg//helpers", ["pkg/helpers/one.py"], id="doubled-slash"),
        pytest.param("/tests", [], id="absolute"),
        pytest.param("TESTS", [], id="case"),
        pytest.param("tests/../tests", [], id="dot-dot"),
    ],
)
def test_ignored_reads_an_entry_as_sourcery_does(
    entry: str, skipped: list[str]
) -> None:
    """`ignored()` covers what Sourcery 1.46.0 skipped for the same entry.

    Each case was measured in a scratch repository holding `LAYOUT` and
    an `origin` on github.com, with `ignore: [<entry>]` in its
    `.sourcery.yaml` and the files Sourcery reported read off
    `uvx --python 3.15 --from sourcery==1.46.0 sourcery review --check .`.

    :param entry: the `ignore:` entry.
    :param skipped: the files Sourcery reported no finding in.
    """
    assert ignored([entry], list(LAYOUT)) == skipped


def test_a_git_blob_is_git_s_own(tmp_path: Path) -> None:
    """`git_blob()` answers what `git hash-object` answers.

    :param tmp_path: where the file is written.
    """
    data = b"print('hello')\n"
    (tmp_path / "x.py").write_bytes(data)
    answered = subprocess.run(
        ["git", "hash-object", str(tmp_path / "x.py")],
        capture_output=True,
        encoding="utf-8",
        check=True,
        env={**os.environ, **QUIET},
    ).stdout.strip()
    assert git_blob(data) == answered


PINNED = "tests/unit/_data/test_framework/v2_p2p.py"
"""The vendored module of the tree a test builds, at btclib-node's path."""

VENDORED = b"# Bitcoin Core's own code\n"
"""Its bytes, as upstream holds them."""

MINE = b"# mine, not upstream\n"
"""Bytes no upstream holds, the tree's own code."""

TREE = "btclib-node"
"""The name the tree a test builds goes by in the organization."""

UPSTREAM = ("bitcoin/bitcoin", "test/functional/test_framework/v2_p2p.py")
"""The repository and path the pin of the tree a test builds names."""

COMMIT = "6a129983c9bf8efa1081f9a8b462c3635d1cfb39"
"""The commit that pin names."""


def _steps(*lines: str) -> str:
    return "jobs:\n  pins:\n    steps:\n" + "".join(
        f"      - {line}\n" for line in lines
    )


RUNS = _steps("run: python3 check.py tests/_data/README.md")
"""A workflow whose step passes the pin file to its command."""


def _calling(owner: str, ledger: str) -> str:
    return (
        "jobs:\n  pins:\n"
        f"    uses: {owner}/.github/workflows/reusable-vendored-vectors.yml@{COMMIT}\n"
        "    with:\n      ledgers: >-\n"
        f'        [{{"ledger": "{ledger}", "title": "Drift"}}]\n'
    )


CALLS = _calling("btclib-org/.github", "tests/_data/README.md")
"""A workflow handing the pin file to the organization's reusable check."""


def _pin_file(
    blob: str,
    *,
    heading: str = f"## `{PINNED}`",
    fields: str = f"repo    {UPSTREAM[0]}\npath    {UPSTREAM[1]}\ncommit  {COMMIT}",
) -> str:
    return (
        "# Vendored test vectors\n\n"
        f"{heading}\n\n"
        "```text\n"
        f"{fields}  2026-06-04\n"
        f"blob    {blob}\n"
        "pulled  2026-10-27\n"
        "```\n"
    )


def _upstream(
    held: dict[tuple[str, str, str], bytes],
) -> Callable[[str, str, str], str | None]:
    def answer(repo: str, commit: str, path: str) -> str | None:
        data = held.get((repo, commit, path))
        return None if data is None else git_blob(data)

    return answer


HELD = {(UPSTREAM[0], COMMIT, UPSTREAM[1]): VENDORED}
"""What upstream holds, as the stub of `upstream_blob()` answers it."""


@dataclass(frozen=True)
class GitHub:
    """What the stubs of `pinned()`'s half that asks GitHub answer."""

    held: dict[tuple[str, str, str], bytes] = field(default_factory=lambda: HELD)
    """The bytes each repository holds at a commit and path."""

    own: frozenset[str] = frozenset()
    """The commits on the tree's own default branch."""

    unmerged: frozenset[str] = frozenset()
    """The commits upstream serves that are not on its default branch."""

    roots: dict[str, str] = field(default_factory=dict)
    """The root of each fork's network; any other repository is its own."""

    def asks(self) -> Asks:
        """Answer as these stubs say, never reaching GitHub.

        :returns: the questions `pinned()` puts, stubbed.
        """
        return Asks(
            own=lambda _tree, commit: commit in self.own,
            blob=_upstream(self.held),
            root=lambda repo: self.roots.get(repo, repo),
            merged=lambda _repo, commit: commit not in self.unmerged,
        )


UPSTREAM_ONLY = GitHub()
"""Upstream merged the vendored bytes; the tree holds none of its commits."""


def _pinning(
    tree: Path,
    *,
    document: str | None = None,
    workflow: str | None = RUNS,
    data: bytes = VENDORED,
    github: GitHub = UPSTREAM_ONLY,
) -> list[str]:
    files = {
        PINNED: data,
        "tests/_data/README.md": (document or _pin_file(git_blob(VENDORED))).encode(),
    }
    if workflow is not None:
        files[PIN_WORKFLOW] = workflow.encode()
    for name, content in files.items():
        path = tree / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    _git(tree, "init", "--quiet")
    _git(tree, "add", "--all")
    return pinned(tree, TREE, [PINNED], github.asks())


def test_a_file_pinned_by_its_blob_and_re_checked_is_kept(tmp_path: Path) -> None:
    """A pin whose blob is the file's and upstream's, handed over, keeps it.

    The questions of `Asks` are stubbed: this is the local half of
    `pinned()`, which reads the checkout alone.
    `hooks_test.py` runs the half that asks GitHub, under the
    `integration` marker.

    :param tmp_path: where the repository is built.
    """
    assert _pinning(tmp_path) == [PINNED]


def test_a_pin_file_handed_to_the_reusable_check_is_kept(tmp_path: Path) -> None:
    """A `ledger` of the organization's callee is handed over as a `run:` is.

    :param tmp_path: where the repository is built.
    """
    assert _pinning(tmp_path, workflow=CALLS) == [PINNED]


def test_words_after_a_pin_s_field_are_not_read(tmp_path: Path) -> None:
    r"""A field is its first word, as btclib-node's own checker reads it.

    Its `check_vendored_pin.py` reads `(\S+)` after the field's name, so
    `pins()` does too, and a `blob` line with more after it keeps the file
    it pins.

    :param tmp_path: where the repository is built.
    """
    document = _pin_file(f"{git_blob(VENDORED)}  re-pulled")
    assert _pinning(tmp_path, document=document) == [PINNED]


def test_a_file_git_does_not_track_is_not_kept(tmp_path: Path) -> None:
    """A pinned file on disk that git does not track is not kept.

    :param tmp_path: where the repository is built.
    """
    assert _pinning(tmp_path) == [PINNED]
    _git(tmp_path, "rm", "--cached", "--quiet", PINNED)
    assert pinned(tmp_path, TREE, [PINNED], UPSTREAM_ONLY.asks()) == []


def test_a_file_not_asked_about_is_not_kept(tmp_path: Path) -> None:
    """Only the files `among` names reach the half that asks GitHub.

    :param tmp_path: where the repository is built.
    """
    _pinning(tmp_path)
    asked: list[tuple[str, str, str]] = []

    def answer(repo: str, commit: str, path: str) -> str | None:
        asked.append((repo, commit, path))
        return git_blob(VENDORED)

    stubbed = Asks(
        own=lambda *_: False,
        blob=answer,
        root=lambda repo: repo,
        merged=lambda *_: True,
    )
    assert pinned(tmp_path, TREE, [], stubbed) == []
    assert not asked


MINE_BLOB = git_blob(MINE)
INVENTED = f"repo    nobody/nothing\npath    x\ncommit  {'0' * 40}"

NODE = "09be07c3b0ecabe0ed77cfbea85a095128b9f52c"
"""A commit of btclib-node's own `main`, which its forks serve too."""

FORK = "jaynarayan-yadav/btclib-node"
"""A fork of btclib-node, whose owner sets its default branch."""

FORK_ONLY = "54eecec21303f18f6379228692d812b080b5e1fa"
"""A commit on a branch of `FORK` changing btclib-node's own test."""

HOME = f"btclib-org/{TREE}"
"""The tree's own repository, the root of its fork network."""

DOTTED = "../../../btclib-org/btclib-node/contents/README.md"
"""A `path` GitHub resolves out of the repository the pin names."""


def _own_code(
    repo: str,
    path: str,
    commit: str = NODE,
    *,
    own: bool = False,
    roots: dict[str, str] | None = None,
) -> dict[str, Any]:
    return {
        "data": MINE,
        "document": _pin_file(
            MINE_BLOB, fields=f"repo    {repo}\npath    {path}\ncommit  {commit}"
        ),
        "github": GitHub(
            {(repo, commit, path): MINE},
            frozenset({commit}) if own else frozenset(),
            roots=roots or {},
        ),
    }


@pytest.mark.parametrize(
    ("changes", "why"),
    [
        pytest.param({"data": VENDORED + b"\n"}, "changed here", id="bytes"),
        pytest.param({"workflow": None}, "no workflow", id="no-workflow"),
        pytest.param(
            {"workflow": _steps("run: check tests/README.md")},
            "another pin file",
            id="workflow-names-another",
        ),
        pytest.param(
            {"workflow": _steps("run: check tests/_data/README.md.bak")},
            "a longer path",
            id="workflow-names-longer",
        ),
        pytest.param(
            {"workflow": _calling("someone/.github", "tests/_data/README.md")},
            "another owner's callee",
            id="callee-elsewhere",
        ),
        pytest.param(
            {"workflow": _calling("btclib-org/.github", "tests/README.md")},
            "the callee handed another pin file",
            id="callee-names-another",
        ),
        pytest.param(
            {
                "document": _pin_file(MINE_BLOB),
                "github": GitHub({(UPSTREAM[0], COMMIT, UPSTREAM[1]): MINE}),
            },
            "the pin and upstream hold another blob",
            id="blob",
        ),
        pytest.param(
            {"document": _pin_file(git_blob(VENDORED)).replace("commit  ", "pulled  ")},
            "no commit",
            id="no-commit",
        ),
        pytest.param(
            {"document": _pin_file(git_blob(VENDORED), heading="## Bitcoin Core")},
            "no path in the heading",
            id="heading",
        ),
        pytest.param(
            {"workflow": "# see tests/_data/README.md\n"},
            "the pin file only in a comment",
            id="comment-only",
        ),
        pytest.param(
            {
                "workflow": "on:\n  push:\n    paths: [tests/_data/README.md]\n"
                + _steps("run: echo hello")
            },
            "the pin file only under on.push.paths",
            id="paths-only",
        ),
        pytest.param(
            {"data": MINE, "document": _pin_file(MINE_BLOB, fields=INVENTED)},
            "invented fields under a real run: line",
            id="invented-fields",
        ),
        pytest.param(
            _own_code("someone/copy-of-btclib-node", PINNED, own=True),
            "the tree's own commit, in a repository outside its network",
            id="own-commit-elsewhere",
        ),
        pytest.param(
            _own_code(HOME, PINNED, FORK_ONLY),
            "the tree's own repository, at a commit its main lacks",
            id="self-repo",
        ),
        pytest.param(
            _own_code(
                FORK, "tests/unit/orphanage_test.py", FORK_ONLY, roots={FORK: HOME}
            ),
            "the tree's own code, at a commit only a fork of the tree holds",
            id="fork-of-tree-own-commit",
        ),
        pytest.param(
            _own_code(FORK, "README.md", FORK_ONLY, roots={FORK: HOME.upper()}),
            "a fork of the tree, its root in another case",
            id="fork-of-tree-case",
        ),
        pytest.param(
            _own_code(
                "someone/node",
                PINNED,
                COMMIT,
                roots={HOME: "upstream/node", "someone/node": "upstream/node"},
            ),
            "the tree a fork, and the pin to another fork of its upstream",
            id="tree-is-a-fork",
        ),
        pytest.param(
            _own_code("bitcoin/bitcoin", DOTTED),
            "a path that leaves the repository",
            id="dot-segments",
        ),
        pytest.param(
            _own_code("bitcoin/..", "btclib-org/btclib-node/contents/README.md"),
            "a repo with a dot segment",
            id="repo-dot-segment",
        ),
        pytest.param(
            _own_code("bitcoin/bitcoin", "x//y"),
            "an empty path segment",
            id="empty-segment",
        ),
        pytest.param(
            _own_code("bitcoin/bitcoin", "README.md", "master"),
            "a branch, not a commit",
            id="commit-branch",
        ),
        pytest.param(
            {"github": GitHub({(UPSTREAM[0], COMMIT, UPSTREAM[1]): MINE})},
            "upstream holds other bytes",
            id="wrong-upstream-blob",
        ),
        pytest.param(
            {"github": GitHub(unmerged=frozenset({COMMIT}))},
            "a commit only a fork of upstream or a pull request holds",
            id="fork-of-upstream",
        ),
        pytest.param(
            {"github": GitHub({})}, "upstream holds nothing there", id="no-upstream"
        ),
    ],
)
def test_a_file_not_pinned_byte_for_byte_is_not_kept(
    tmp_path: Path, changes: dict[str, Any], why: str
) -> None:
    """Each condition `pinned()` reads, broken alone, leaves the file unkept.

    Each case breaks one condition and holds every other. The cases
    holding `MINE` pin the tree's own code.

    :param tmp_path: where the repository is built.
    :param changes: what differs from the kept case.
    :param why: what the case breaks.
    """
    assert _pinning(tmp_path, **changes) == [], why


def test_a_pin_is_read_under_any_heading_level() -> None:
    """A pin is read under `###`, as in btclib, and `##`, as in btclib-node.

    A heading naming no path ends the pin above it.
    """
    document = _pin_file("a" * 40, heading=f"### `{PINNED}`")
    assert pins(document)[PINNED]["blob"] == "a" * 40
    grouped = document.replace(
        f"### `{PINNED}`", f"### `{PINNED}`\n\n## bitcoin/bitcoin"
    )
    assert pins(grouped) == {}
