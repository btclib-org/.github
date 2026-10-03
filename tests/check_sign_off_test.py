# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 11's `Signed-off-by:` check, its script and the jobs running it.

The script reads a repository built by each test, so what is asked is
git's own trailer parsing and not a reading of it. The jobs are read from
both workflows that carry one, and every tree's `lint.yml` is asked
whether it runs one.

The script is loaded by path, `.github/scripts` being no package, as the
other scripts under it are tested.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import pytest

from . import ORG, ROOT, SELF, by_hand
from .workflows_test import jobs

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

SCRIPT = ROOT / ".github" / "scripts" / "check_sign_off.py"
WORKFLOWS = ROOT / ".github" / "workflows"
# a pull request's commits, read off the merge commit a pull_request run
# checks out
RANGE = "HEAD^1..HEAD^2"

AUTHOR = "Ann <ann@example.org>"
DEPENDABOT = "dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>"
PRE_COMMIT_CI = (
    "pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>"
)


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("check_sign_off", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "check_sign_off", module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Make a repository with one base commit the working directory."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.chdir(tmp_path)
    _git("init", "--quiet", "--initial-branch=main")
    _commit("base")


def _git(*args: str) -> str:
    """Run git in the working directory as the committer `Ann`."""
    ran = subprocess.run(
        ["git", "-c", "user.name=Ann", "-c", "user.email=ann@example.org", *args],
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    return ran.stdout


def _commit(message: str, author: str = AUTHOR, *, signoff: bool = False) -> None:
    """Commit nothing under this message and author."""
    extra = ["--signoff"] if signoff else []
    _git(
        "commit",
        "--quiet",
        "--allow-empty",
        f"--author={author}",
        "-m",
        message,
        *extra,
    )


@pytest.mark.usefixtures("repo")
def test_a_commit_signed_off_by_its_author_passes(script: ModuleType) -> None:
    """`git commit -s` writes the trailer the check reads."""
    _commit("one", signoff=True)
    _commit("two", "ANN <Ann@Example.org>", signoff=True)

    assert script.refused("main~2..main") == []


@pytest.mark.usefixtures("repo")
def test_a_commit_with_no_trailer_is_refused(script: ModuleType) -> None:
    """The line names the commit and the address the trailer has to carry."""
    _commit("unsigned")

    (line,) = script.refused("main~1..main")

    assert line.endswith(" unsigned: no Signed-off-by: <ann@example.org>")


def _run_the_fix(script: ModuleType, revisions: str, out: str) -> None:
    """Run the command the failure printed, as `Ann`."""
    (command,) = (s for s in map(str.strip, out.splitlines()) if s.startswith("git "))
    _git(*command.split()[1:])
    assert script.refused(revisions) == []


@pytest.mark.usefixtures("repo")
def test_the_command_the_failure_prints_signs_the_branch_off(
    script: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    """Run as printed, the command adds the trailer to every commit refused."""
    _git("checkout", "--quiet", "-b", "topic")
    _commit("one", signoff=True)
    _commit("two")

    assert script.main(["main..topic"]) == 1
    out = capsys.readouterr().out
    assert "cannot merge" in out
    _run_the_fix(script, "main..topic", out)


@pytest.mark.usefixtures("repo")
def test_the_command_leaves_a_merged_in_base_alone(
    script: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    """A branch that merged its base is rebased onto the base commit it merged.

    The base's commit is `Bob`'s and not signed off, so a command that
    replayed it would carry `Ann`'s trailer on it into the range.
    """
    _git("checkout", "--quiet", "-b", "topic")
    _commit("work")
    _git("checkout", "--quiet", "main")
    _commit("landed meanwhile", "Bob <bob@example.org>")
    _git("checkout", "--quiet", "topic")
    _git("merge", "--quiet", "--no-edit", "main")
    _commit("more work")

    assert script.main(["main..topic"]) == 1
    _run_the_fix(script, "main..topic", capsys.readouterr().out)
    _git("merge-base", "--is-ancestor", "main", "topic")


@pytest.mark.usefixtures("repo")
def test_a_trailer_naming_somebody_else_is_refused(script: ModuleType) -> None:
    """The author's own sign-off is asked for, not anybody's."""
    _commit("forwarded", "Bob <bob@example.org>", signoff=True)

    assert script.refused("main~1..main")


@pytest.mark.usefixtures("repo")
def test_a_trailer_outside_the_last_paragraph_is_refused(script: ModuleType) -> None:
    """Git reads trailers off the message's last paragraph alone."""
    _commit("subject\n\nSigned-off-by: Ann <ann@example.org>\n\nA closing line.")

    assert script.refused("main~1..main")


@pytest.mark.usefixtures("repo")
@pytest.mark.parametrize("bot", [DEPENDABOT, PRE_COMMIT_CI])
def test_a_bot_commit_is_not_read(script: ModuleType, bot: str) -> None:
    """Dependabot's and pre-commit.ci's commits pass with no trailer."""
    _commit("Bump a dependency", bot)

    assert script.refused("main~1..main") == []


@pytest.mark.usefixtures("repo")
def test_a_merge_commit_is_not_read(script: ModuleType) -> None:
    """The merge *Update branch* writes carries no trailer and is skipped.

    The commit merged in from the base is outside the range, being the
    base's; the branch's own commit is still read.
    """
    _git("checkout", "--quiet", "-b", "topic")
    _commit("work", signoff=True)
    _git("checkout", "--quiet", "main")
    _commit("landed meanwhile")
    _git("checkout", "--quiet", "topic")
    _git("merge", "--quiet", "--no-edit", "main")

    assert script.refused("main..topic") == []


@pytest.mark.parametrize(("signoff", "code"), [(True, 0), (False, 1)])
@pytest.mark.usefixtures("repo")
def test_the_script_reads_a_pull_requests_merge_commit(
    *, signoff: bool, code: int
) -> None:
    """Run as a command on the range the jobs pass, with the merge checked out.

    The merge's first parent is the base and its second the head, as on
    the ref GitHub builds for a pull request.
    """
    _git("checkout", "--quiet", "-b", "topic")
    _commit("work", signoff=signoff)
    _git("checkout", "--quiet", "--detach", "main")
    _git("merge", "--quiet", "--no-ff", "--no-edit", "topic")

    ran = subprocess.run(
        [sys.executable, str(SCRIPT), RANGE],
        capture_output=True,
        encoding="utf-8",
        check=False,
    )

    assert ran.returncode == code, ran.stdout


def _run(job: dict[str, Any]) -> str:
    """Return the command of the job's step that runs the script."""
    run: str = next(s["run"] for s in job["steps"] if SCRIPT.name in s.get("run", ""))
    return run


@pytest.mark.parametrize(
    ("workflow", "path"),
    [
        ("reusable-lint.yml", f"standard/{SCRIPT.relative_to(ROOT).as_posix()}"),
        ("lint.yml", SCRIPT.relative_to(ROOT).as_posix()),
    ],
)
def test_the_job_reads_the_whole_branch(workflow: str, path: str) -> None:
    """Each job runs the script on the range, over a checkout of all history.

    The reusable job runs this repository's copy, checked out at `main`
    beside the caller's tree; this repository's own job runs the branch's.
    """
    job = jobs(WORKFLOWS / workflow)["sign-off"]
    checkout = job["steps"][0]

    assert job["name"] == "Sign-off"
    assert job["permissions"] == {"contents": "read"}
    assert "github.event_name == 'pull_request'" in job["if"]
    assert checkout["uses"].startswith("actions/checkout@")
    assert checkout["with"]["fetch-depth"] == 0
    assert f"{path} {RANGE}" in _run(job)


def test_the_lint_gate_checks_the_sign_off(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """The tree's `lint.yml` calls the reusable workflow or runs the script.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    path = trees[repository] / ".github" / "workflows" / "lint.yml"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    called = f"{ORG}/{SELF}/.github/workflows/reusable-lint.yml@main" in text
    assert called or SCRIPT.name in text, (
        f"lint.yml neither calls reusable-lint.yml nor runs {SCRIPT.name}; "
        + by_hand(repository, f"grep -c {SCRIPT.name} .github/workflows/lint.yml")
    )
