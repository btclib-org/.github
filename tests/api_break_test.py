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

The files in `griffe_output/` are what griffe 2.2.0 printed with
`-f oneline -X` over a two-commit repository holding
`src/pkg/__init__.py`: a parameter added and a function removed, a
package that is not there, and a base that is no commit. The paths of
the installation are replaced and nothing else.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path
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

_OUTPUTS = Path(__file__).parent / "griffe_output"
BREAK = (_OUTPUTS / "break.txt").read_text(encoding="utf-8")
ABSENT = (_OUTPUTS / "absent.txt").read_text(encoding="utf-8")
BAD_REF = (_OUTPUTS / "bad_ref.txt").read_text(encoding="utf-8")


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


@pytest.mark.parametrize("answer", ["", "unknown", "True", "break"])
def test_an_answer_that_is_not_true_or_false_is_a_warning(answer: str) -> None:
    """A wiring fault reads as an empty answer, and is told, not silent."""
    ran: list[Sequence[str]] = []

    def run(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
        ran.append(argv)
        return _done(0)

    assert len(script.label(answer, "o/r", "7", run)) == 1
    assert not ran


def test_a_call_that_succeeds_is_no_warning() -> None:
    """Both answers, with the command exiting 0."""

    def run(_: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return _done(0)

    assert script.label("true", "o/r", "7", run) == []
    assert script.label("false", "o/r", "7", run) == []


def test_the_label_command_prints_each_warning(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A warning is a workflow command line, and none prints nothing."""
    monkeypatch.setattr(script, "label", lambda *_: ["boom"])
    assert script.main(["label", "true", "o/r", "7"]) == 0
    assert capsys.readouterr().out == "::warning::boom\n"

    monkeypatch.setattr(script, "label", lambda *_: [])
    assert script.main(["label", "true", "o/r", "7"]) == 0
    assert capsys.readouterr().out == ""


def test_the_default_runner_keeps_the_output_of_a_failing_command() -> None:
    """A non-zero exit is returned, not raised, with both streams kept."""
    code = "import sys; print('out'); sys.stderr.write('err'); sys.exit(3)"

    done = script._run([sys.executable, "-c", code])  # noqa: SLF001

    assert (done.returncode, done.stdout.strip(), done.stderr) == (3, "out", "err")


def test_a_404_on_adding_is_a_warning() -> None:
    """Only the DELETE tolerates it."""

    def run(_: Sequence[str]) -> subprocess.CompletedProcess[str]:
        return _done(1, "gh: Not Found (HTTP 404)")

    assert len(script.label("true", "o/r", "7", run)) == 1


def test_the_command_prints_the_answer_for_the_output_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
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
    condition = " ".join(_step("Set the label")["if"].split())
    assert condition == (
        "steps.compare.outputs.broken != 'unknown' && "
        "github.event.pull_request.head.repo.full_name == github.repository"
    )


def test_the_job_declines_a_closed_or_draft_pull_request() -> None:
    """Only a pull request that is open and ready is walked."""
    condition = " ".join(_job()["if"].split())
    assert condition == (
        "${{ github.event_name == 'pull_request' && "
        "github.event.action != 'closed' && "
        "!github.event.pull_request.draft }}"
    )


def test_the_history_is_fetched_and_a_failed_griffe_is_caught() -> None:
    """The base has to be reachable, and the status is read, not fatal."""
    checkout = next(
        step for step in _job()["steps"] if step.get("name") == "Checkout code"
    )
    assert checkout["with"]["fetch-depth"] == 0
    assert "|| status=$?" in _step("Compare the public API with the base")["run"]


def test_the_comparison_is_against_the_base_without_importing() -> None:
    """The base is the pull request's, through `env:`; `-X` imports nothing."""
    step = _step("Compare the public API with the base")
    assert step["env"]["BASE_SHA"] == "${{ github.event.pull_request.base.sha }}"
    assert '-a "$BASE_SHA"' in step["run"]
    assert " -X " in step["run"]
    assert "${{" not in step["run"]


def test_the_answer_reaches_the_label_step() -> None:
    """The classify line writes to the step output, and the label reads it."""
    run = _step("Compare the public API with the base")["run"]
    assert run.rstrip().endswith('>> "$GITHUB_OUTPUT"')
    assert "2>&1" in run
    assert _step("Compare the public API with the base")["id"] == "compare"
    assert (
        _step("Set the label")["env"]["BROKEN"]
        == "${{ steps.compare.outputs.broken }}"
    )


def test_the_finding_pattern_is_the_one_the_release_check_reads() -> None:
    """One format of griffe's output, held equal where it is read twice."""
    spec = importlib.util.spec_from_file_location(
        "check_public_api", ROOT / ".github" / "scripts" / "check_public_api.py"
    )
    assert spec is not None
    assert spec.loader is not None
    other = importlib.util.module_from_spec(spec)
    sys.modules["check_public_api"] = other
    spec.loader.exec_module(other)
    for line in BREAK.splitlines() + ABSENT.splitlines() + BAD_REF.splitlines():
        assert bool(script._FINDING.fullmatch(line)) == bool(  # noqa: SLF001
            other._FINDING.fullmatch(line)  # noqa: SLF001
        )


def test_both_workflows_pin_the_same_griffe() -> None:
    """The comment says the version is the same there, so it is asked."""
    pins = {
        tuple(re.findall(r"griffe==[\d.]+", path.read_text(encoding="utf-8")))
        for path in (_WORKFLOW, _WORKFLOW.with_name("reusable-public-api.yml"))
    }
    assert len(pins) == 1
    assert pins != {()}


def test_the_workflow_runs_the_script_where_its_checkout_puts_it() -> None:
    """Both steps take the script from the checkout's `path:`."""
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
    """The trees `labels.yml` owes the label to, as listed there."""
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
