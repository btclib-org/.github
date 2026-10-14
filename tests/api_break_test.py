# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for `reusable-api-break.yml` and `.github/scripts/api_break.py`.

The label informs a review and gates nothing (btclib-org/.github#1674),
and a fork's pull request gets no write token, so what is asked here is
what keeps both true: that a break is told from griffe's other exit-1
answers, that the right call sets the label, and that the workflow
holds the one write it needs and no trigger that would hand a fork's
code a write token.

The outputs below are what griffe 2.2.0 printed, `-f oneline -X`, for a
two-commit repository holding `src/pkg/__init__.py`: a parameter added
and a function removed, a package that is not there, and a base that is
no commit. The paths of the installation are replaced and nothing else.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import ROOT

if TYPE_CHECKING:
    from collections.abc import Sequence
    from types import ModuleType

_WORKFLOW = ROOT / ".github" / "workflows" / "reusable-api-break.yml"
_SCRIPT = ROOT / ".github" / "scripts" / "api_break.py"
_LABELS = ROOT / ".github" / "labels.yml"

BREAK = 'src/pkg/__init__.py:1: f(b): Parameter was added as required\nsrc/pkg/__init__.py:0: g: Public object was removed\n'
ABSENT = 'Traceback (most recent call last):\n  File "/runner/uv/archive-v0/x/bin/griffe", line 12, in <module>\n    sys.exit(main())\n             ~~~~^^\n  File "/runner/uv/archive-v0/x/lib/python3.15/site-packages/griffecli/_internal/cli.py", line 643, in main\n    return commands[subcommand](**opts_dict)\n           ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^\n  File "/runner/uv/archive-v0/x/lib/python3.15/site-packages/griffecli/_internal/cli.py", line 547, in check\n    old_package = load_git(\n        against_path,\n    ...<8 lines>...\n        resolve_external=None,\n    )\n  File "/runner/uv/archive-v0/x/lib/python3.15/site-packages/griffe/_internal/loader.py", line 934, in load_git\n    return load(\n        objspec,\n    ...<13 lines>...\n        resolve_implicit=resolve_implicit,\n    )\n  File "/runner/uv/archive-v0/x/lib/python3.15/site-packages/griffe/_internal/loader.py", line 857, in load\n    result = loader.load(\n        objspec,\n    ...<2 lines>...\n        find_stubs_package=find_stubs_package,\n    )\n  File "/runner/uv/archive-v0/x/lib/python3.15/site-packages/griffe/_internal/loader.py", line 165, in load\n    obj_path, package = self.finder.find_spec(\n                        ~~~~~~~~~~~~~~~~~~~~~^\n        objspec,  # ty:ignore[invalid-argument-type]\n        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n        try_relative_path=try_relative_path,\n        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n        find_stubs_package=find_stubs_package,\n        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n    )\n    ^\n  File "/runner/uv/archive-v0/x/lib/python3.15/site-packages/griffe/_internal/finder.py", line 220, in find_spec\n    return module_name, self.find_package(top_module_name)\n                        ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^\n  File "/runner/uv/archive-v0/x/lib/python3.15/site-packages/griffe/_internal/finder.py", line 292, in find_package\n    raise ModuleNotFoundError(module_name)\nModuleNotFoundError: nopkg\n'
BAD_REF = 'Traceback (most recent call last):\n  File "/runner/uv/archive-v0/x/lib/python3.15/site-packages/griffe/_internal/git.py", line 141, in _tmp_worktree\n    _git("-C", str(repo), "worktree", "add", "-b", tmp_branch, location, ref)\n    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File "/runner/uv/archive-v0/x/lib/python3.15/site-packages/griffe/_internal/git.py", line 62, in _git\n    raise GitError(process.stdout.strip())\ngriffe._internal.exceptions.GitError: fatal: invalid reference: deadbeef\n\nThe above exception was the direct cause of the following exception:\n\nTraceback (most recent call last):\n  File "/runner/uv/archive-v0/x/bin/griffe", line 12, in <module>\n    sys.exit(main())\n             ~~~~^^\n  File "/runner/uv/archive-v0/x/lib/python3.15/site-packages/griffecli/_internal/cli.py", line 643, in main\n    return commands[subcommand](**opts_dict)\n           ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^\n  File "/runner/uv/archive-v0/x/lib/python3.15/site-packages/griffecli/_internal/cli.py", line 547, in check\n    old_package = load_git(\n        against_path,\n    ...<8 lines>...\n        resolve_external=None,\n    )\n  File "/runner/uv/archive-v0/x/lib/python3.15/site-packages/griffe/_internal/loader.py", line 929, in load_git\n    with _tmp_worktree(repo, ref) as worktree:\n         ~~~~~~~~~~~~~^^^^^^^^^^^\n  File "/runner/uv/python/lib/python3.15/contextlib.py", line 203, in __enter__\n    return next(self.gen)\n  File "/runner/uv/archive-v0/x/lib/python3.15/site-packages/griffe/_internal/git.py", line 143, in _tmp_worktree\n    raise RuntimeError(f"Could not create git worktree: {error}") from error\nRuntimeError: Could not create git worktree: fatal: invalid reference: deadbeef\n'


def _script() -> ModuleType:
    """Load the script by path, `.github/scripts` being no package."""
    spec = importlib.util.spec_from_file_location("api_break", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["api_break"] = module
    spec.loader.exec_module(module)
    return module


script = _script()


def test_findings_with_exit_1_are_a_break() -> None:
    """Every line a finding, and the exit code 1."""
    assert script.classify(1, BREAK) == "true"


@pytest.mark.parametrize("output", [ABSENT, BAD_REF, ""])
def test_an_exception_with_exit_1_is_not_a_break(output: str) -> None:
    """A traceback exits 1 too, and nothing is then said of the label."""
    assert script.classify(1, output) == "unknown"


def test_a_finding_among_a_traceback_is_not_a_break() -> None:
    """One line that is not a finding is enough."""
    assert script.classify(1, BREAK + ABSENT) == "unknown"


def test_no_findings_is_no_break() -> None:
    """Exit 0 is a clean comparison, whatever it printed."""
    assert script.classify(0, "") == "false"


@pytest.mark.parametrize("status", [2, 127])
def test_any_other_exit_is_not_a_break(status: int) -> None:
    """Findings printed beside another exit code are not trusted."""
    assert script.classify(status, BREAK) == "unknown"


def test_a_break_adds_the_label_and_no_break_removes_it() -> None:
    """Each answer asks the one call, on the pull request's own labels."""
    add = script.calls("true", "o/r", "7")
    remove = script.calls("false", "o/r", "7")

    assert add == [
        [
            "gh", "api", "--method", "POST", "repos/o/r/issues/7/labels",
            "-f", "labels[]=api-break",
        ]
    ]  # fmt: skip
    assert remove == [
        ["gh", "api", "--method", "DELETE", "repos/o/r/issues/7/labels/api-break"]
    ]


def test_an_unknown_answer_asks_nothing() -> None:
    """The label stays as it is."""
    assert script.calls("unknown", "o/r", "7") == []


def _done(code: int, stderr: str = "") -> subprocess.CompletedProcess[str]:
    """Return a finished command."""
    return subprocess.CompletedProcess([], code, "", stderr)


def test_removing_a_label_that_is_not_there_is_no_warning() -> None:
    """A 404 on the DELETE is the state asked for."""

    def run(_: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return _done(1, "gh: Label does not exist (HTTP 404)")

    assert script.label("false", "o/r", "7", run) == []


def test_any_other_failure_is_a_warning() -> None:
    """A 403 on either call is told, and not hidden as a 404."""

    def run(_: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return _done(1, "gh: Resource not accessible (HTTP 403)")

    assert len(script.label("false", "o/r", "7", run)) == 1
    assert len(script.label("true", "o/r", "7", run)) == 1


def test_a_404_on_adding_is_a_warning() -> None:
    """Only the DELETE tolerates it."""

    def run(_: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return _done(1, "gh: Not Found (HTTP 404)")

    assert len(script.label("true", "o/r", "7", run)) == 1


def test_the_command_prints_the_answer_for_the_output_file(
    tmp_path: Any, capsys: pytest.CaptureFixture[str]
) -> None:
    """`broken=<answer>` is the line `GITHUB_OUTPUT` takes."""
    findings = tmp_path / "findings.txt"
    findings.write_text(BREAK, encoding="utf-8")

    assert script.main(["classify", "1", str(findings)]) == 0
    assert capsys.readouterr().out == "broken=true\n"


def _parsed() -> dict[Any, Any]:
    """Return the workflow, parsed."""
    parsed: dict[Any, Any] = yaml.safe_load(_WORKFLOW.read_text(encoding="utf-8"))
    return parsed


def _job() -> dict[str, Any]:
    """Return the workflow's one job."""
    jobs: dict[str, Any] = _parsed()["jobs"]
    assert list(jobs) == ["api-break"]
    job: dict[str, Any] = jobs["api-break"]
    return job


def _step(name: str) -> dict[str, Any]:
    """Return the step of that name."""
    steps: list[dict[str, Any]] = _job()["steps"]
    return next(step for step in steps if step.get("name") == name)


def test_the_workflow_declares_no_trigger_but_the_call() -> None:
    """A fork's code never runs with a write token through a trigger here.

    `pull_request_target` and `workflow_run` are the two that would.
    """
    parsed = _parsed()
    on: dict[str, Any] = parsed.get("on", parsed.get(True)) or {}
    assert list(on) == ["workflow_call"]


def test_the_write_is_the_job_s_alone() -> None:
    """The workflow reads, and the job elevates `pull-requests` only."""
    assert _parsed()["permissions"] == {"contents": "read"}
    assert _job()["permissions"] == {"contents": "read", "pull-requests": "write"}
    assert _job()["continue-on-error"] is True


def test_the_label_is_set_only_on_a_pull_request_of_the_calling_repository() -> None:
    """A fork's token is read-only, so the step declines it by name."""
    condition = _step("Set the label")["if"]
    assert (
        "github.event.pull_request.head.repo.full_name == github.repository"
        in condition
    )
    assert "!= 'unknown'" in condition


def test_the_comparison_is_against_the_base_without_importing() -> None:
    """The base is the pull request's, through `env:`; `-X` imports nothing."""
    step = _step("Compare the public API with the base")
    assert step["env"]["BASE_SHA"] == "${{ github.event.pull_request.base.sha }}"
    assert '-a "$BASE_SHA"' in step["run"]
    assert " -X " in step["run"]
    assert "${{" not in step["run"]


def test_the_workflow_runs_the_script_where_its_checkout_puts_it() -> None:
    """Both steps take the script from the checkout's `path:` and this file's."""
    checkout = _step("Check out the script")
    assert checkout["with"]["path"] == "standard"
    assert checkout["with"]["sparse-checkout"] == ".github/scripts"
    path = f"standard/{_SCRIPT.relative_to(ROOT).as_posix()}"
    assert path in _step("Compare the public API with the base")["run"]
    assert path in _step("Set the label")["run"]


def test_the_findings_go_to_the_job_summary() -> None:
    """A fork's pull request is not labelled, so its finding is read here."""
    step = _step("Report the finding")
    assert "$GITHUB_STEP_SUMMARY" in step["run"]
    assert "head.repo" not in step.get("if", "")


def test_the_label_is_owed_by_the_publishing_trees_alone() -> None:
    """`labels.yml` names every tree that calls `reusable-public-api.yml`."""
    labels = yaml.safe_load(_LABELS.read_text(encoding="utf-8"))["labels"]
    label = next(entry for entry in labels if entry["name"] == "api-break")
    assert sorted(label["repositories"]) == [
        "bitcoin-core-rpc",
        "btclib",
        "btclib-ecc",
        "btclib-mnemonics",
        "btclib-node",
        "btclib-secp256k1",
        "btclib-wallet",
    ]
