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


def test_the_caller_runs_on_a_pull_request_and_is_not_required() -> None:
    """The caller's trigger, and no required context named for it.

    Section 11 is where the required checks are listed, and it names no
    context of this job.
    """
    assert "pull_request" in triggers(CALLER)
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    eleven = text[text.index("\n## 11. ") : text.index("\n## 12. ")]
    assert "sourcery" not in eleven.lower()


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


def _reviewed(tmp_path: Path, changed: str, base: str = "main") -> tuple[int, str]:
    """Run the callee's script over a pull request changing one file.

    :param tmp_path: where the repository and the stub go.
    :param changed: the path the pull request adds.
    :param base: what `BASE_REF` carries.
    :returns: the script's exit code, and the arguments `uvx` was given.
    """
    tree = tmp_path / "tree"
    tree.mkdir()
    _git(tree, "init", "--quiet", "--initial-branch=main")
    _git(tree, "config", "user.email", "probe@example.invalid")
    _git(tree, "config", "user.name", "probe")
    (tree / "base.py").write_text("x = 1\n", encoding="utf-8")
    _git(tree, "add", "base.py")
    _git(tree, "commit", "--quiet", "-m", "base")
    _git(tree, "update-ref", "refs/remotes/origin/main", "HEAD")
    _git(tree, "switch", "--quiet", "-c", "change")
    path = tree / changed
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("y = 2\n", encoding="utf-8")
    _git(tree, "add", changed)
    _git(tree, "commit", "--quiet", "-m", "change")
    stub = tmp_path / "stub"
    stub.mkdir()
    log = tmp_path / "log"
    (stub / "uvx").write_text(
        '#!/bin/sh\nprintf "%s\\n" "$@" > "$STUBLOG"\n', encoding="utf-8"
    )
    (stub / "uvx").chmod(0o755)
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
            "BASE_REF": base,
            "SOURCERY_VERSION": "1.46.0",
        },
    )
    asked = log.read_text(encoding="utf-8") if log.is_file() else ""
    return ran.returncode, asked


@pytest.mark.parametrize(
    ("changed", "whole"),
    [
        pytest.param("src/one.py", False, id="python"),
        pytest.param(".sourcery.yaml", True, id="config"),
        pytest.param(".github/workflows/sourcery.yml", True, id="caller"),
        pytest.param(".github/workflows/reusable-sourcery.yml", True, id="callee"),
        pytest.param("tests/.sourcery.yaml", False, id="nested-config"),
        pytest.param("docs/sourcery.md", False, id="prose"),
    ],
)
def test_the_review_reads_the_diff_or_the_whole_tree(
    tmp_path: Path,
    changed: str,
    whole: bool,  # noqa: FBT001
) -> None:
    """The diff against the merge base, or every file where the rules moved.

    :param tmp_path: where the repository is built.
    :param changed: the file the pull request changes.
    :param whole: whether Sourcery is to read the whole tree.
    """
    code, asked = _reviewed(tmp_path, changed)
    assert code == 0
    arguments = asked.splitlines()
    assert arguments[:5] == [
        "--from",
        "sourcery==1.46.0",
        "sourcery",
        "review",
        "--check",
    ]
    if whole:
        assert arguments[5:] == ["."]
    else:
        assert arguments[5:] == ["--diff", "git diff origin/main...", "."]


def test_the_review_refuses_an_event_with_no_base(tmp_path: Path) -> None:
    """No base branch is a failure naming it, and Sourcery is not run.

    :param tmp_path: where the repository is built.
    """
    code, asked = _reviewed(tmp_path, "src/one.py", base="")
    assert code == 1
    assert not asked
