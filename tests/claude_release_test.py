# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What keeps `reusable-claude-release.yml` within section 10's rule.

The workflow's header says how the file keeps the rule. These tests read
its configuration: the scopes each job and the agent's token are asked
for, the agent's allow list, the conditions each job starts on, and the
gates step, which is `reusable-claude-implement.yml`'s. The steps that
refuse a run, read the API and what is open, set the version, pack and
unpack the edit, check the body and commit are read out of the workflow
and run here, against stand-ins for `gh`, `uv` and `date`, so what is
asked is what the runner runs.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import pytest

from . import ROOT
from .check_sign_off_test import CLAUDE
from .claude_implement_test import DEFAULTS, conjuncts, hidden_calls, re_runnable
from .claude_review_test import AGENT_DENIED
from .workflows_test import document, jobs, triggers

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

# the reusable workflow, which holds the jobs
WORKFLOW = ROOT / ".github/workflows/reusable-claude-release.yml"

# the workflow whose gates step this one takes word for word
IMPLEMENT = ROOT / ".github/workflows/reusable-claude-implement.yml"

# the commit the fixture's release.yml pins reusable-public-api.yml to
PIN = "a" * 40

# the date the stand-in for `date` prints, and the version it makes
TODAY = "2026.11.10"


@pytest.fixture(autouse=True)
def no_git_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the machine's git configuration out of every git command here.

    :param monkeypatch: sets the environment for one test.
    """
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")


def step(job: str, name: str) -> dict[str, Any]:
    """Read one step of a job, by its name.

    :param job: the job's id.
    :param name: the step's name.
    :returns: the step.
    """
    (found,) = [s for s in jobs(WORKFLOW)[job]["steps"] if s.get("name") == name]
    return dict(found)


def action() -> dict[str, str]:
    """Read the `with:` of the agent's step.

    :returns: the step's inputs.
    """
    found: list[dict[str, str]] = [
        s["with"]
        for s in jobs(WORKFLOW)["write"]["steps"]
        if s.get("uses", "").startswith("anthropics/claude-code-action@")
    ]
    (inputs,) = found
    return inputs


def tools(flag: str) -> list[str]:
    """Read the rules after one flag of the agent's `claude_args`.

    :param flag: `--allowedTools` or `--disallowedTools`.
    :returns: the rules, up to the next flag.
    """
    args = shlex.split(action()["claude_args"])
    rules: list[str] = []
    for arg in args[args.index(flag) + 1 :]:
        if arg.startswith("--"):
            break
        rules.append(arg)
    return rules


def git(tree: Path, *args: str) -> str:
    """Run git in a fixture tree, as a committer of its own.

    :param tree: the tree.
    :param args: git's arguments.
    :returns: what git printed.
    """
    return subprocess.run(
        ["git", "-C", str(tree), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        capture_output=True,
        encoding="utf-8",
        check=True,
    ).stdout


def stand_in(bench: Path, name: str, body: str) -> None:
    """Write an executable stand-in on the bench.

    :param bench: the directory first on the path the steps run with.
    :param name: the command it stands in for.
    :param body: its script, after the `#!` line.
    """
    path = bench / name
    path.write_text("#!/bin/sh\n" + body)
    path.chmod(0o755)


def run_step(
    run: str, cwd: Path, bench: Path, env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    """Run a step's script as the runner does, `bash -e`, the bench first.

    :param run: the step's script.
    :param cwd: the checkout it runs in.
    :param bench: the directory of the stand-ins.
    :param env: the step's `env:`, and what the runner sets.
    :returns: the finished step.
    """
    return subprocess.run(
        ["bash", "-e", "-c", run],
        cwd=cwd,
        env={**os.environ, "PATH": f"{bench}:{os.environ['PATH']}", **env},
        capture_output=True,
        encoding="utf-8",
        check=False,
    )


def outputs(path: Path) -> dict[str, str]:
    """Read what a step wrote to `GITHUB_OUTPUT`.

    :param path: the file.
    :returns: each name and value.
    """
    if not path.exists():
        return {}
    return dict(line.split("=", 1) for line in path.read_text().splitlines())


# the jobs, in the order they run
JOBS = ["prepare", "write", "gates", "publish"]


def test_the_jobs_run_in_order() -> None:
    """Each job needs every job before it."""
    found = jobs(WORKFLOW)
    assert list(found) == JOBS
    for index, name in enumerate(JOBS[1:], start=1):
        needs = found[name]["needs"]
        assert set([needs] if isinstance(needs, str) else needs) == set(JOBS[:index])
        for needed in JOBS[:index]:
            assert f"needs.{needed}.result == 'success'" in conjuncts(
                found[name]["if"]
            ), (name, needed)


def test_no_job_runs_again_on_a_re_run() -> None:
    """Each job's condition holds `github.run_attempt == 1` as a conjunct."""
    assert re_runnable(WORKFLOW) == []


def test_a_release_starts_from_a_dispatch_on_the_default_branch() -> None:
    """The first job runs on `workflow_dispatch`, on the default branch."""
    found = conjuncts(jobs(WORKFLOW)["prepare"]["if"])
    assert "github.event_name == 'workflow_dispatch'" in found
    assert (
        "github.ref == format('refs/heads/{0}', github.event.repository.default_branch)"
        in found
    )
    assert list(triggers(WORKFLOW)) == ["workflow_call"]


def test_each_job_holds_what_its_comment_names() -> None:
    """No job writes the repository; `write` and `publish` take OIDC tokens."""
    found = {name: job["permissions"] for name, job in jobs(WORKFLOW).items()}
    assert found == {
        "prepare": {"contents": "read", "pull-requests": "read", "actions": "read"},
        "write": {"contents": "read", "id-token": "write"},
        "gates": {"contents": "read"},
        "publish": {"contents": "read", "id-token": "write"},
    }
    assert document(WORKFLOW)["permissions"] == {"contents": "read"}


def test_the_credential_reaches_the_agent_s_job_alone() -> None:
    """The OAuth token is named in `write` and in no other job."""
    for name, job in jobs(WORKFLOW).items():
        assert ("secrets." in str(job)) == (name == "write"), name


def test_the_agent_s_token_lists_every_default_and_writes_nothing() -> None:
    """Each default is named, read-only: the agent writes through no API."""
    listed: dict[str, str] = {}
    for line in action()["additional_permissions"].splitlines():
        if line.strip():
            key, value = line.split(":", 1)
            listed[key.strip()] = value.strip()
    assert set(listed) == DEFAULTS
    assert set(listed.values()) == {"read"}
    assert action()["allowed_non_write_users"] == "-none-"


def test_the_agent_edits_the_three_files_and_runs_nothing() -> None:
    """No Bash rule, and an `Edit` rule for each file the agent writes."""
    allowed = tools("--allowedTools")
    assert not [rule for rule in allowed if rule.startswith("Bash")]
    assert [rule for rule in allowed if rule.startswith("Edit")] == [
        "Edit(./CHANGELOG.md)",
        "Edit(./RELEASE_NOTES.md)",
        "Edit(/${{ runner.temp }}/claude-release-body/body.md)",
    ]
    denied = tools("--disallowedTools")
    assert "Edit(./.git/**)" in denied
    assert {tool for rule in denied for tool in rule.split(",")} >= AGENT_DENIED


def test_the_published_token_is_asked_for_no_workflows_scope() -> None:
    """`publish` asks for contents and pull requests, nothing more."""
    run = step("publish", "Push and open the pull request")["run"]
    assert '{"permissions": {"contents": "write", "pull_requests": "write"}}' in run


def test_the_gates_step_is_the_implement_workflow_s() -> None:
    """The step running the caller's gates is the same, word for word."""
    name = "Run the gates as a user of their own"
    (theirs,) = [s for s in jobs(IMPLEMENT)["gates"]["steps"] if s.get("name") == name]
    assert step("gates", name) == theirs


def test_no_step_hides_a_failed_gh_call() -> None:
    """Each `gh` or `curl` call is an assignment's whole or a direct call."""
    assert "defaults" not in document(WORKFLOW)
    for name, job in jobs(WORKFLOW).items():
        assert "defaults" not in job, name
        for each in job["steps"]:
            assert "shell" not in each, (name, each.get("name"))
            assert hidden_calls(each.get("run", "")) == [], (name, each.get("name"))


def test_a_run_an_administrator_did_not_start_is_refused(tmp_path: Path) -> None:
    """The permission of `github.actor` is read, and only `admin` passes.

    :param tmp_path: holds the stand-in for `gh`.
    """
    run = step("prepare", "Refuse a run an administrator did not start")["run"]
    env = {"REPO": "o/r", "ACTOR": "someone"}
    found = {}
    for permission in ("admin", "maintain", "write"):
        stand_in(tmp_path, "gh", f'echo "$@" > {tmp_path}/argv\necho {permission}\n')
        found[permission] = run_step(run, tmp_path, tmp_path, env).returncode
    assert found == {"admin": 0, "maintain": 1, "write": 1}
    argv = (tmp_path / "argv").read_text()
    assert argv.startswith("api repos/o/r/collaborators/someone/permission")


@pytest.fixture
def released(tmp_path: Path) -> tuple[Path, Path]:
    """Make a tree with a release tagged and a commit since, and a bench.

    The bench holds stand-ins: `date` prints `TODAY`, `gh` the count of
    branches named after the release, from a file, and `uv` reads the
    version from `pyproject.toml` and runs a script with this
    interpreter.

    :param tmp_path: a directory of this test's own.
    :returns: the tree and the bench.
    """
    tree = tmp_path / "tree"
    (tree / ".github/workflows").mkdir(parents=True)
    (tree / "pyproject.toml").write_text('[project]\nversion = "2026.12"\n')
    for name in ("CHANGELOG.md", "RELEASE_NOTES.md"):
        (tree / name).write_text(f"# {name}\n\n## v2026.11.7\n\nIt.\n")
    (tree / ".github/workflows/release.yml").write_text(
        "jobs:\n  public-api:\n    uses: btclib-org/.github/.github/workflows/"
        f"reusable-public-api.yml@{PIN} # v2026.11.5\n"
    )
    git(tree, "init", "-q", "-b", "main")
    git(tree, "add", "-A")
    git(tree, "commit", "-q", "-m", "First")
    git(tree, "tag", "v2026.11.7")
    (tree / "code.py").write_text("x = 1\n")
    git(tree, "add", "-A")
    git(tree, "commit", "-q", "-m", "Do a thing (closes #1) (#2)")
    (tree / "standard").symlink_to(ROOT)
    bench = tmp_path / "bench"
    bench.mkdir()
    stand_in(bench, "date", f"echo {TODAY}\n")
    (bench / "branches").write_text("0\n")
    stand_in(bench, "gh", f"cat {bench}/branches\n")
    stand_in(
        bench,
        "uv",
        'case "$1" in\n'
        "  version) sed -n 's/^version = \"\\(.*\\)\"$/\\1/p' pyproject.toml ;;\n"
        "  run) shift\n"
        '    while [ "$#" -gt 0 ]; do\n'
        '      case "$1" in\n'
        "        *.py) break ;;\n"
        "        --python|--with) shift 2 ;;\n"
        "        *) shift ;;\n"
        "      esac\n"
        "    done\n"
        f'    exec {sys.executable} "$@" ;;\n'
        "esac\n",
    )
    return tree, bench


def refusal(tree: Path, bench: Path) -> subprocess.CompletedProcess[str]:
    """Run the step that refuses a tree holding no release.

    :param tree: the checkout.
    :param bench: the stand-ins.
    :returns: the finished step.
    """
    env = {
        "REPO": "o/r",
        "WORKFLOW_SHA": PIN,
        "FACTS": str(tree.parent / "facts"),
        "GITHUB_OUTPUT": str(tree.parent / "output"),
    }
    run = step("prepare", "Refuse a tree that holds no release")["run"]
    return run_step(run, tree, bench, env)


def test_a_tree_holding_a_release_passes(released: tuple[Path, Path]) -> None:
    """The control: the version, the previous tag and the subjects.

    :param released: the tree and the bench.
    """
    tree, bench = released
    done = refusal(tree, bench)
    assert done.returncode == 0, done.stdout + done.stderr
    assert outputs(tree.parent / "output") == {
        "version": TODAY,
        "previous": "v2026.11.7",
        "placeholder": "2026.12",
    }
    subjects = (tree.parent / "facts/subjects.txt").read_text()
    assert subjects == "Do a thing (closes #1) (#2)\n"


def planted_version(tree: Path, bench: Path) -> None:
    """Declare a release's version where the placeholder stands."""
    del bench
    (tree / "pyproject.toml").write_text('[project]\nversion = "2026.11.7"\n')


def no_tag(tree: Path, bench: Path) -> None:
    """Delete the only tag."""
    del bench
    git(tree, "tag", "-d", "v2026.11.7")


def tag_elsewhere(tree: Path, bench: Path) -> None:
    """Tag a newer release on a commit HEAD does not reach."""
    del bench
    git(tree, "switch", "-q", "-c", "side", "HEAD~1")
    git(tree, "commit", "-q", "--allow-empty", "-m", "Side")
    git(tree, "tag", "v2026.11.8")
    git(tree, "switch", "-q", "main")


def nothing_since(tree: Path, bench: Path) -> None:
    """Move the tag to HEAD."""
    del bench
    git(tree, "tag", "-f", "v2026.11.7", "HEAD")


def heading_written(tree: Path, bench: Path) -> None:
    """Write the release's heading, with words after it, in the notes."""
    del bench
    notes = tree / "RELEASE_NOTES.md"
    notes.write_text(notes.read_text() + f"\n## v{TODAY} (draft)\n")


def notes_missing(tree: Path, bench: Path) -> None:
    """Remove the release notes."""
    del bench
    (tree / "RELEASE_NOTES.md").unlink()


def tagged_today(tree: Path, bench: Path) -> None:
    """Tag today's version as the previous release, with a commit since."""
    del bench
    git(tree, "tag", "-d", "v2026.11.7")
    git(tree, "tag", f"v{TODAY}", "HEAD~1")


def branch_exists(tree: Path, bench: Path) -> None:
    """Have the API answer that the release's branch exists."""
    del tree
    (bench / "branches").write_text("1\n")


def another_pin(tree: Path, bench: Path) -> None:
    """Pin reusable-public-api.yml to another commit."""
    del bench
    release = tree / ".github/workflows/release.yml"
    release.write_text(release.read_text().replace(PIN, "b" * 40))


def future_date(tree: Path, bench: Path) -> None:
    """Have the clock name a day that has begun nowhere."""
    del tree
    stand_in(bench, "date", "echo 2999.1.1\n")


def below_the_latest(tree: Path, bench: Path) -> None:
    """Tag the previous release after today's date."""
    del bench
    git(tree, "tag", "-d", "v2026.11.7")
    git(tree, "tag", "v2099.1.1", "HEAD~1")


@pytest.mark.parametrize(
    ("plant", "why"),
    [
        (planted_version, "not the placeholder YYYY.M"),
        (no_tag, "a first release is prepared by hand"),
        (tag_elsewhere, "the newest v* tag is v2026.11.8"),
        (nothing_since, "nothing has landed since v2026.11.7"),
        (heading_written, f'RELEASE_NOTES.md holds a "## v{TODAY}" heading'),
        (notes_missing, "the tree holds no RELEASE_NOTES.md"),
        (tagged_today, f"the tag v{TODAY} exists already"),
        (branch_exists, f"the branch claude/release-v{TODAY} exists already"),
        (another_pin, "release.yml calls reusable-public-api.yml at 'bbbb"),
        (future_date, "2999.1.1 is dated 2999-01-01"),
        (below_the_latest, "does not sort above v2099.1.1"),
    ],
    ids=lambda value: getattr(value, "__name__", ""),
)
def test_a_tree_holding_no_release_is_refused(
    released: tuple[Path, Path], plant: Callable[[Path, Path], None], why: str
) -> None:
    """Each refusal the header names fails the step, with its error.

    :param released: the tree and the bench.
    :param plant: what makes the tree hold no release.
    :param why: a part of the error.
    """
    tree, bench = released
    plant(tree, bench)
    done = refusal(tree, bench)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "::error::" in done.stdout
    assert why in done.stdout
    assert outputs(tree.parent / "output") == {}


def api(
    tmp_path: Path, griffe: tuple[str, int], gaps: tuple[str, int]
) -> tuple[subprocess.CompletedProcess[str], str]:
    """Run the public API step, with `uv run` standing in for both tools.

    :param tmp_path: a directory of this test's own.
    :param griffe: what griffe prints, and its exit status.
    :param gaps: what api_gaps.py prints, and its exit status.
    :returns: the finished step, and the findings file.
    """
    stand_in(
        tmp_path,
        "uv",
        f'case "$*" in\n'
        f"  *'griffe check'*) printf '{griffe[0]}'; exit {griffe[1]} ;;\n"
        f"  *api_gaps.py*) printf '{gaps[0]}'; exit {gaps[1]} ;;\n"
        "esac\nexit 9\n",
    )
    (tmp_path / "facts").mkdir()
    env = {
        "PACKAGE": "pkg",
        "PREVIOUS": "v2026.11.7",
        "FACTS": str(tmp_path / "facts"),
        "GRIFFE": "griffe==0",
    }
    run = step("prepare", "Read the public API against the previous release")["run"]
    done = run_step(run, tmp_path, tmp_path, env)
    return done, (tmp_path / "facts/findings.txt").read_text()


FINDING = "src/pkg/a.py:3: f(x): Parameter was removed\\n"


@pytest.mark.parametrize(
    ("griffe", "gaps", "expected"),
    [
        (("", 0), ("", 0), ""),
        ((FINDING, 1), ("", 0), FINDING.replace("\\n", "\n")),
        (("", 0), (FINDING, 1), FINDING.replace("\\n", "\n")),
    ],
)
def test_the_findings_of_both_tools_are_kept(
    tmp_path: Path, griffe: tuple[str, int], gaps: tuple[str, int], expected: str
) -> None:
    """An exit of 0 or 1 is an answer, and both answers go to the file.

    :param tmp_path: a directory of this test's own.
    :param griffe: what griffe prints, and its exit status.
    :param gaps: what api_gaps.py prints, and its exit status.
    :param expected: the findings file.
    """
    done, findings = api(tmp_path, griffe, gaps)
    assert done.returncode == 0, done.stdout + done.stderr
    assert findings == expected


@pytest.mark.parametrize(
    ("griffe", "gaps"),
    [
        (("Traceback (most recent call last):\\n", 1), ("", 0)),
        (("", 2), ("", 0)),
        (("", 0), ("", 2)),
    ],
    ids=["griffe-traceback", "griffe-2", "api-gaps-2"],
)
def test_a_tool_that_fails_stops_the_job(
    tmp_path: Path, griffe: tuple[str, int], gaps: tuple[str, int]
) -> None:
    """A traceback, or an exit above 1, answers nothing.

    :param tmp_path: a directory of this test's own.
    :param griffe: what griffe prints, and its exit status.
    :param gaps: what api_gaps.py prints, and its exit status.
    """
    done, _ = api(tmp_path, griffe, gaps)
    assert done.returncode == 1
    assert "::error::" in done.stdout


def what_is_open(tmp_path: Path, *, deps_latest: bool) -> dict[str, str]:
    """Run the step reading what is open, against a stand-in `gh`.

    The release path holds `release.yml`, `.github/scripts/` and the
    workflow `release.yml` calls, `test.yml`.

    :param tmp_path: a directory of this test's own.
    :param deps_latest: whether the tree has a `deps-latest.yml`.
    :returns: each file the step wrote, by name.
    """
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/release.yml").write_text(
        "jobs:\n  test:\n    uses: ./.github/workflows/test.yml\n"
    )
    if deps_latest:
        (tmp_path / ".github/workflows/deps-latest.yml").write_text("")
    prs = [
        {"number": 4, "files": [{"path": "README.md"}]},
        {"number": 5, "files": [{"path": ".github/workflows/test.yml"}]},
        {"number": 6, "files": [{"path": ".github/scripts/x.py"}]},
        {"number": 7, "files": [{"path": ".github/workflows/lint.yml"}]},
        {"number": 8, "files": [{"path": ".github/workflows/release.yml"}]},
        {"number": 9, "files": [{"path": f"docs/{i}.md"} for i in range(100)]},
        {"number": 10, "files": [{"path": f"docs/{i}.md"} for i in range(99)]},
    ]
    runs = [
        {"conclusion": "failure", "status": "completed", "createdAt": "T", "url": "U"}
    ]
    (tmp_path / "prs.json").write_text(json.dumps(prs))
    (tmp_path / "runs.json").write_text(json.dumps(runs))
    stand_in(
        tmp_path,
        "gh",
        f'case "$1 $2" in\n  "pr list") cat {tmp_path}/prs.json ;;\n'
        f'  "run list") cat {tmp_path}/runs.json ;;\n  *) exit 9 ;;\nesac\n',
    )
    facts = tmp_path / "facts"
    facts.mkdir()
    env = {"REPO": "o/r", "BASE": "main", "FACTS": str(facts)}
    done = run_step(
        step("prepare", "Read what is open")["run"], tmp_path, tmp_path, env
    )
    assert done.returncode == 0, done.stdout + done.stderr
    return {path.name: path.read_text() for path in facts.iterdir()}


def test_the_release_path_is_read_off_the_files_each_pull_request_changes(
    tmp_path: Path,
) -> None:
    """`release.yml`, a workflow it calls and a script are on the path.

    So is a pull request showing 100 files, the most `gh pr list` reads,
    and one showing 99 is not.

    :param tmp_path: a directory of this test's own.
    """
    found = what_is_open(tmp_path, deps_latest=True)
    assert found == {
        "open.txt": "#4, #5, #6, #7, #8, #9, #10\n",
        "release-path.txt": "#5, #6, #8, #9\n",
        "deps-latest.txt": "failure, started T, U\n",
    }


def test_a_tree_with_no_deps_latest_reads_no_run(tmp_path: Path) -> None:
    """The step asks for no run of a workflow the tree does not hold.

    :param tmp_path: a directory of this test's own.
    """
    assert "deps-latest.txt" not in what_is_open(tmp_path, deps_latest=False)


def lock_tree(tmp_path: Path) -> Path:
    """Make a checkout holding `pyproject.toml` and `uv.lock`.

    :param tmp_path: a directory of this test's own.
    :returns: the checkout.
    """
    tree = tmp_path / "tree"
    tree.mkdir()
    (tree / "pyproject.toml").write_text('[project]\nversion = "2026.12"\n')
    (tree / "uv.lock").write_text('version = "2026.12"\n')
    (tree / "README.md").write_text("x\n")
    git(tree, "init", "-q")
    git(tree, "add", "-A")
    git(tree, "commit", "-q", "-m", "x")
    return tree


@pytest.mark.parametrize(
    ("extra", "expected"),
    [("", 0), ("README.md", 1), ("uv.lock", 1), ("pyproject.toml", 1)],
)
def test_setting_the_version_changes_one_line_of_two_files(
    tmp_path: Path, extra: str, expected: int
) -> None:
    """A stand-in `uv lock` that writes anything more fails the step.

    A line it adds to `uv.lock` or to `pyproject.toml` stands for a pin
    moved; a third file, for any other change.

    :param tmp_path: a directory of this test's own.
    :param extra: a file the stand-in adds a line to besides the version.
    :param expected: the step's exit status.
    """
    tree = lock_tree(tmp_path)
    touch = f"echo 'y = 1' >> {extra}\n" if extra else ""
    stand_in(
        tmp_path,
        "uv",
        'case "$1" in\n'
        '  version) [ "$2" = --frozen ] || exit 9\n'
        '    sed -i.bak "s/2026.12/$3/" pyproject.toml && rm pyproject.toml.bak ;;\n'
        f'  lock) sed -i.bak "s/2026.12/{TODAY}/" uv.lock && rm uv.lock.bak\n'
        f"    {touch} ;;\n"
        "esac\n",
    )
    (facts := tmp_path / "facts/tree").mkdir(parents=True)
    env = {"VERSION": TODAY, "PLACEHOLDER": "2026.12", "FACTS": str(facts.parent)}
    done = run_step(step("prepare", "Set the version")["run"], tree, tmp_path, env)
    assert done.returncode == expected, done.stdout + done.stderr
    if not expected:
        assert TODAY in (facts / "pyproject.toml").read_text()
        assert TODAY in (facts / "uv.lock").read_text()


@pytest.mark.parametrize(("tamper", "expected"), [(False, 0), (True, 1)])
def test_the_facts_travel_only_under_their_digest(
    tmp_path: Path,
    tamper: bool,  # noqa: FBT001
    expected: int,
) -> None:
    """The pack's digest is checked where the facts are unpacked.

    :param tmp_path: a directory of this test's own.
    :param tamper: whether the pack changes after its digest is taken.
    :param expected: the unpacking step's exit status.
    """
    facts = tmp_path / "facts"
    facts.mkdir()
    (facts / "subjects.txt").write_text("A subject\n")
    out = tmp_path / "out"
    env = {"FACTS": str(facts), "OUT": str(out), "GITHUB_OUTPUT": str(tmp_path / "o")}
    done = run_step(step("prepare", "Pack the facts")["run"], tmp_path, tmp_path, env)
    assert done.returncode == 0, done.stderr
    if tamper:
        with (out / "facts.tar").open("ab") as stream:
            stream.write(b"\0")
    env = {
        "IN": str(out),
        "FACTS": str(tmp_path / "unpacked"),
        "EXPECTED": outputs(tmp_path / "o")["digest"],
    }
    run = step("write", "Unpack the facts")["run"]
    done = run_step(run, tmp_path, tmp_path, env)
    assert done.returncode == expected, done.stdout + done.stderr
    if not expected:
        assert (tmp_path / "unpacked/subjects.txt").read_text() == "A subject\n"


def edited(tmp_path: Path, *, notes: bool = True) -> tuple[Path, dict[str, str]]:
    """Pack an edit as `write` does, and lay it over a fresh checkout.

    :param tmp_path: a directory of this test's own.
    :param notes: whether the edit changes `RELEASE_NOTES.md`.
    :returns: the checkout, and the outputs of the unpacking step.
    """
    tree = lock_tree(tmp_path)
    for name in ("CHANGELOG.md", "RELEASE_NOTES.md"):
        (tree / name).write_text("## v2026.11.7\n\nIt.\n")
    git(tree, "add", "-A")
    git(tree, "commit", "-q", "-m", "y")
    work = tmp_path / "work"
    git(tree, "worktree", "add", "-q", str(work))
    (work / "CHANGELOG.md").write_text(f"## v{TODAY}\n\nNew.\n\n## v2026.11.7\n\nIt.\n")
    if notes:
        (work / "RELEASE_NOTES.md").write_text(f"## v{TODAY}\n\nAct.\n")
    (body := tmp_path / "body").mkdir()
    (body / "body.md").write_text("The release.\n")
    (work / "stray.txt").write_text("left by the step\n")
    out = tmp_path / "out"
    env = {"BODY": str(body), "OUT": str(out), "GITHUB_OUTPUT": str(tmp_path / "w")}
    run = step("write", "Pack the release's sections")["run"]
    done = run_step(run, work, tmp_path, env)
    assert done.returncode == 0, done.stdout + done.stderr
    (facts := tmp_path / "facts/tree").mkdir(parents=True)
    for name in ("pyproject.toml", "uv.lock"):
        (facts / name).write_text((tree / name).read_text().replace("2026.12", TODAY))
    env = {
        "IN": str(out),
        "FACTS": str(facts.parent),
        "EXPECTED": outputs(tmp_path / "w")["digest"],
        "GITHUB_OUTPUT": str(tmp_path / "g"),
    }
    done = run_step(
        step("gates", "Unpack the edit over the checkout")["run"], tree, tmp_path, env
    )
    assert done.returncode == (0 if notes else 1), done.stdout + done.stderr
    return tree, outputs(tmp_path / "g")


def test_the_edit_lays_the_four_files_over_the_checkout(tmp_path: Path) -> None:
    """Nothing else the editing step left travels.

    :param tmp_path: a directory of this test's own.
    """
    tree, found = edited(tmp_path)
    staged = git(tree, "diff", "--cached", "--name-only").split()
    assert staged == ["CHANGELOG.md", "RELEASE_NOTES.md", "pyproject.toml", "uv.lock"]
    assert found["tree"] == git(tree, "write-tree").strip()


def test_an_edit_that_leaves_a_file_unchanged_is_refused(tmp_path: Path) -> None:
    """A release changes the four files, the notes among them.

    :param tmp_path: a directory of this test's own.
    """
    _, found = edited(tmp_path, notes=False)
    assert found == {}


def test_publish_lays_the_edit_as_the_gates_did() -> None:
    """Both jobs run one unpacking script, and publish commits its tree."""
    name = "Unpack the edit over the checkout"
    assert step("publish", name)["run"] == step("gates", name)["run"]
    commit = step("publish", "Commit the release")
    assert commit["env"]["GATED"] == "${{ needs.gates.outputs.tree }}"
    assert '"$(git write-tree)" != "$GATED"' in commit["run"]


@pytest.mark.parametrize(("right", "expected"), [(True, 0), (False, 1)])
def test_the_release_is_committed_by_claude_with_no_trailer(
    tmp_path: Path,
    right: bool,  # noqa: FBT001
    expected: int,
) -> None:
    """The commit holds the gated tree, under claude[bot] and no `-by:` line.

    `check_sign_off.py` passes that address with no trailer, as its
    tests show for the implement workflow's commit.

    :param tmp_path: a directory of this test's own.
    :param right: whether the tree the gates recorded is the staged one.
    :param expected: the step's exit status.
    """
    tree, found = edited(tmp_path)
    env = {
        "VERSION": TODAY,
        "PREVIOUS": "v2026.11.7",
        "BRANCH": f"claude/release-v{TODAY}",
        "GATED": found["tree"] if right else "0" * 40,
        "RUNNER_TEMP": str(tmp_path),
    }
    done = run_step(step("publish", "Commit the release")["run"], tree, tmp_path, env)
    assert done.returncode == expected, done.stdout + done.stderr
    if expected:
        return
    shown = git(tree, "show", "-s", "--format=%an <%ae>%n%s%n%(trailers)", "HEAD")
    assert shown == f"{CLAUDE}\nv{TODAY}\n\n"


@pytest.mark.parametrize(("tip", "expected"), [("s", 0), ("t", 1)])
def test_a_default_branch_that_moved_is_refused(
    tmp_path: Path, tip: str, expected: int
) -> None:
    """The sections are written from the run's commit, which has to be the tip.

    :param tmp_path: a directory of this test's own.
    :param tip: the sha the API answers.
    :param expected: the step's exit status.
    """
    stand_in(tmp_path, "gh", f"echo {tip}\n")
    env = {"REPO": "o/r", "BASE": "main", "SHA": "s"}
    run = step("publish", "Refuse a default branch that has moved")["run"]
    assert run_step(run, tmp_path, tmp_path, env).returncode == expected


def body(tmp_path: Path, findings: str, lists: dict[str, str]) -> str:
    """Run the step writing the pull request's body.

    :param tmp_path: a directory of this test's own.
    :param findings: the findings file.
    :param lists: the facts files of what is open, and of deps-latest.
    :returns: the body.
    """
    (edit := tmp_path / "in/edit").mkdir(parents=True)
    (edit / "body.md").write_text("The release.\n")
    (facts := tmp_path / "facts").mkdir()
    (facts / "findings.txt").write_text(findings)
    for name, text in lists.items():
        (facts / name).write_text(text)
    env = {
        "IN": str(edit.parent),
        "FACTS": str(facts),
        "PREVIOUS": "v2026.11.7",
        "GATES": "uv run pytest",
        "RUN": "https://run",
        "FENCE": "```",
        "GRIFFE": "griffe==0",
        "RUNNER_TEMP": str(tmp_path),
    }
    run = step("publish", "Write the pull request's body")["run"]
    done = run_step(run, tmp_path, tmp_path, env)
    assert done.returncode == 0, done.stdout + done.stderr
    return (tmp_path / "body.md").read_text()


def test_the_body_says_none_where_nothing_is_open(tmp_path: Path) -> None:
    """Empty lists read `none`, and no finding reads as no break.

    :param tmp_path: a directory of this test's own.
    """
    text = body(tmp_path, "", {"open.txt": "\n", "release-path.txt": "\n"})
    assert text.startswith("The release.\n")
    assert "griffe==0 and api_gaps.py find no break" in text
    assert "On the release path: none." in text
    assert "Open, so not in this release: none." in text
    assert "This tree has no `deps-latest` run to read." in text
    assert "```shell\nuv run pytest\n```" in text


def test_the_body_carries_the_findings_and_what_is_open(tmp_path: Path) -> None:
    """The findings in a block of their own, and the numbers of what is open.

    :param tmp_path: a directory of this test's own.
    """
    lists = {
        "open.txt": "#4, #5\n",
        "release-path.txt": "#5\n",
        "deps-latest.txt": "success, started T, U\n",
    }
    text = body(tmp_path, "a.py:1: f: gone\n", lists)
    assert "```text\na.py:1: f: gone\n```" in text
    assert "On the release path: #5." in text
    assert "Open, so not in this release: #4, #5." in text
    assert "Its newest run on the default branch: success, started T, U." in text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("The release.\n\nOn the release path: #5.\n", 0),
        ("The release closes #5.\n", 1),
        ("It fixes\nbtclib-org/btclib#5.\n", 1),
        ("Thanks to @someone.\n", 1),
        ("Signed-off-by: A <a@b>\n", 1),
        ("It fixes https://github.com/o/r/issues/5.\n", 1),
        ("**Closes** #5\n", 1),
        ("Closes [#5](https://github.com/o/r/issues/5)\n", 1),
        ("Closes&nbsp;#5\n", 1),
        ("Closes\u00a0#5\n", 1),
        ("<b>Resolves</b> #5\n", 1),
        ("Closes<br>#5\n", 1),
        ("The fixed `## v2026.11.7` heading.\n", 0),
    ],
)
def test_a_body_that_closes_or_mentions_anything_is_refused(
    tmp_path: Path, text: str, expected: int
) -> None:
    """A closing reference, across a line break, markup or a link too.

    A mention and a trailer are refused as well, and a keyword followed
    by no reference passes.

    :param tmp_path: a directory of this test's own.
    :param text: the body.
    :param expected: the step's exit status.
    """
    (tmp_path / "body.md").write_text(text)
    run = step("publish", "Refuse a body that closes or mentions anything")["run"]
    done = run_step(run, tmp_path, tmp_path, {"RUNNER_TEMP": str(tmp_path)})
    assert done.returncode == expected, done.stdout + done.stderr
