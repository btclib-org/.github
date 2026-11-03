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
of its text.
"""

from __future__ import annotations

import os
import re
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from . import ROOT
from .hooks_test import caller_departures
from .workflows_test import document, steps, triggers

if TYPE_CHECKING:
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


def test_the_caller_runs_on_a_pull_request_and_is_not_required() -> None:
    """The caller's trigger, and no required context named for it.

    Section 11 is where the required checks are listed, and it names no
    context of this job.
    """
    assert "pull_request" in triggers(CALLER)
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    eleven = text[text.index("\n## 11. ") : text.index("\n## 12. ")]
    assert "sourcery" not in eleven.lower()


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
