# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the run's-jobs check of `.github/scripts`.

What a run of `codeql.yml` shows is the check that does not wait: the
jobs listing usually agrees with the run by the time the aggregate reads
it. What no run can show is a listing that lags for as long as the
deadline, a row that concludes between two reads, or any of the verdicts
that turn a red run into a red check -- the run cannot be made to lag,
and a failing job is what the check is there to catch -- so the wait, the
deadline and the annotations are reached here or nowhere.

Both of the wait's inputs are substituted for that. `_Listing` is the
jobs listing: a scripted sequence of reads that also counts them. `_Clock`
is the clock, and it moves only when the script sleeps on it, which makes
the deadline arrive in no time at all and the reads before it exact
rather than approximate. `list_jobs` alone is exercised against a
substituted `gh`, since what it promises is the command it runs and how it
reads the pages the command prints.

The script is loaded by path, `.github/scripts` being no package, as the
other scripts under it are tested.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

_SCRIPT = Path(__file__).parents[1] / ".github" / "scripts" / "check_run_jobs.py"
_REPOSITORY = "btclib-org/btclib"
_RUN_ID = "42"
_USAGE = 2
_GH_FAILED = 4
# a 30 s deadline at the shipped interval: a read before each sleep, and
# the read at the deadline
_READS_IN_30_S = 4
_READS_TO_SETTLE = 3
_CHECK = ("unfinished", "in_progress", "codeql: every job passed")
_ANALYZE_PY = ("success", "completed", "analyze / Analyze (python)")
_ANALYZE_ACTIONS = ("success", "completed", "analyze / Analyze (actions)")
_LAGGING_PY = ("unfinished", "in_progress", "analyze / Analyze (python)")
_LAGGING_ACTIONS = ("unfinished", "queued", "analyze / Analyze (actions)")
_FAILED_PY = ("failure", "completed", "analyze / Analyze (python)")


class _Clock:
    """A monotonic clock that stands still until the script sleeps on it."""

    def __init__(self) -> None:
        self.now = 0.0
        self.slept: list[float] = []

    def monotonic(self) -> float:
        """Return the reading, which only `sleep` below moves."""
        return self.now

    def sleep(self, seconds: float) -> None:
        """Spend the seconds a wait on a real clock would have spent.

        A sleep of nothing is refused: it moves no clock, so a wait that
        asks for one never reaches its deadline.
        """
        assert seconds > 0
        self.slept.append(seconds)
        self.now += seconds


class _Listing:
    """The reads the listing answers, in order, the last one repeating."""

    def __init__(
        self, module: ModuleType, reads: list[list[tuple[str, str, str]]]
    ) -> None:
        self.module = module
        self.reads = reads
        self.count = 0
        self.asked: list[tuple[str, str]] = []

    def __call__(self, run: tuple[str, str]) -> list[object]:
        """Answer the next read, and record what was asked."""
        self.asked.append(run)
        rows = self.reads[min(self.count, len(self.reads) - 1)]
        self.count += 1
        return [self.module.Row(*row) for row in rows]


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("check_run_jobs", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "check_run_jobs", module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def clock(script: ModuleType, monkeypatch: pytest.MonkeyPatch) -> _Clock:
    """Put a clock this test moves where the script reads a real one."""
    fake = _Clock()
    monkeypatch.setattr(script, "time", fake)
    return fake


def _listing(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    *reads: list[tuple[str, str, str]],
) -> _Listing:
    """Put a scripted sequence of reads where the listing would be."""
    listing = _Listing(script, list(reads))
    monkeypatch.setattr(script, "list_jobs", listing)
    return listing


def _run(script: ModuleType, result: str = "success", *options: str) -> int:
    """Run the script the way the job does, for `analyze`'s `result`."""
    verdict = script.main(
        [
            "analyze",
            result,
            "--repository",
            _REPOSITORY,
            "--run-id",
            _RUN_ID,
            *options,
        ]
    )
    assert isinstance(verdict, int)
    return verdict


def test_a_listing_that_agrees_with_the_run_is_read_once_and_passes(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No row lags, so nothing is waited for, and the rows are printed."""
    listing = _listing(script, monkeypatch, [_ANALYZE_PY, _ANALYZE_ACTIONS, _CHECK])

    assert _run(script) == 0

    assert listing.count == 1
    assert listing.asked == [(_REPOSITORY, _RUN_ID)]
    assert clock.slept == []
    assert capsys.readouterr().out == (
        "success\tcompleted\tanalyze / Analyze (python)\n"
        "success\tcompleted\tanalyze / Analyze (actions)\n"
        "unfinished\tin_progress\tcodeql: every job passed\n"
    )


def test_a_row_that_concludes_between_reads_is_judged_on_its_conclusion(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A lagging row is read again, and what it turns out to be decides."""
    listing = _listing(
        script,
        monkeypatch,
        [_LAGGING_PY, _ANALYZE_ACTIONS, _CHECK],
        [_LAGGING_PY, _ANALYZE_ACTIONS, _CHECK],
        [_ANALYZE_PY, _ANALYZE_ACTIONS, _CHECK],
    )

    assert _run(script) == 0

    assert listing.count == _READS_TO_SETTLE
    assert clock.slept == [10.0, 10.0]
    shown = capsys.readouterr().out
    assert "listed unfinished, read again in 10 s:" in shown
    assert "unfinished\tin_progress\tanalyze / Analyze (python)" in shown
    assert "accepted" not in shown


def test_a_lagging_row_that_turns_out_to_have_failed_fails_the_check(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Waiting is not forgiving: the conclusion it ends on is judged."""
    _listing(
        script,
        monkeypatch,
        [_LAGGING_PY, _CHECK],
        [_FAILED_PY, _CHECK],
    )

    assert _run(script) == 1

    assert clock.slept == [10.0]
    assert (
        "::error::these jobs of the run did not succeed:"
        "%0Afailure completed analyze / Analyze (python)\n"
    ) in capsys.readouterr().out


def test_rows_lagging_at_the_deadline_are_accepted_as_the_needs_jobs(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The deadline ends the wait, and the rows still lagging are accepted.

    A listing that never catches up is the one this exists for: it is read
    at the deadline too, and a result of `success` is then what stands.
    """
    listing = _listing(script, monkeypatch, [_LAGGING_PY, _LAGGING_ACTIONS, _CHECK])

    assert _run(script) == 0

    assert clock.now == pytest.approx(30.0)
    assert listing.count == _READS_IN_30_S
    assert clock.slept == [10.0, 10.0, 10.0]
    shown = capsys.readouterr().out
    assert (
        "still listed unfinished, accepted as analyze's (success):\n"
        "unfinished\tin_progress\tanalyze / Analyze (python)\n"
        "unfinished\tqueued\tanalyze / Analyze (actions)\n"
    ) in shown
    assert "::error::" not in shown


def test_a_skipped_result_accepts_lagging_rows_too(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`skipped` is the second result that leaves the listing to lag."""
    listing = _listing(script, monkeypatch, [_LAGGING_PY, _CHECK])

    assert _run(script, "skipped") == 0

    assert listing.count == _READS_IN_30_S
    assert clock.now == pytest.approx(30.0)


def test_the_last_pause_is_cut_to_what_is_left_of_the_deadline(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A deadline that is no multiple of the interval is still the deadline."""
    _listing(script, monkeypatch, [_LAGGING_PY, _CHECK])

    assert _run(script, "success", "--timeout", "25", "--interval", "10") == 0

    assert clock.slept == [10.0, 10.0, 5.0]
    assert clock.now == pytest.approx(25.0)


def test_a_pause_cut_short_is_shown_as_it_is(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A pause of a third of a second is not announced as none."""
    _listing(script, monkeypatch, [_LAGGING_PY, _CHECK])

    assert _run(script, "success", "--timeout", "10.3", "--interval", "10") == 0

    assert clock.slept == [10.0, pytest.approx(0.3)]
    assert "read again in 0.3 s:" in capsys.readouterr().out


def test_a_read_outlasting_the_deadline_is_the_last_one(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """What is left can be negative, and it ends the wait without a sleep.

    `gh` is bounded only by the job, so the clock can be past the deadline
    when a read returns, and `time.sleep` raises on a negative number.
    """

    def slow(_run: tuple[str, str]) -> list[object]:
        """Answer a lagging listing, having spent longer than the budget."""
        clock.now += 90.0
        return [script.Row(*_LAGGING_PY), script.Row(*_CHECK)]

    monkeypatch.setattr(script, "list_jobs", slow)

    assert _run(script) == 0

    assert clock.slept == []


def test_the_defaults_are_the_budget_a_run_actually_gets(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The workflow passes no budget, so the shipped one is what bounds it."""
    _listing(script, monkeypatch, [_LAGGING_PY, _CHECK])

    assert _run(script) == 0

    assert clock.slept == [script.DEFAULT_INTERVAL] * 3
    assert clock.now == pytest.approx(script.DEFAULT_TIMEOUT)


@pytest.mark.parametrize("result", ["failure", "cancelled", ""])
def test_a_result_that_is_not_a_pass_accepts_no_row_and_waits_for_none(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    result: str,
) -> None:
    """The listing is read once, and its unfinished rows count against it."""
    listing = _listing(script, monkeypatch, [_LAGGING_PY, _CHECK])

    assert _run(script, result) == 1

    assert listing.count == 1
    assert clock.slept == []
    shown = capsys.readouterr().out
    assert f"::error::analyze's own result is '{result}'\n" in shown
    # the row a pass would have accepted is counted against the check
    assert (
        "::error::this check should be the run's one unfinished job; 2 are"
        "%0Aunfinished in_progress analyze / Analyze (python)"
        "%0Aunfinished in_progress codeql: every job passed\n"
    ) in shown
    assert "accepted" not in shown


def test_a_result_that_is_not_a_pass_fails_a_listing_that_shows_none(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A failure `needs` reports with no row failed is still a failure."""
    _listing(script, monkeypatch, [_ANALYZE_PY, _CHECK])

    assert _run(script, "failure") == 1

    assert capsys.readouterr().out.count("::error::") == 1
    assert clock.slept == []


def test_a_row_that_did_not_succeed_is_named_by_the_annotation(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Every such row is in one annotation, its tabs turned to spaces."""
    _listing(
        script,
        monkeypatch,
        [
            _FAILED_PY,
            ("cancelled", "completed", "analyze / Analyze (actions)"),
            ("timed_out", "completed", "other"),
            _CHECK,
        ],
    )

    assert _run(script) == 1

    assert (
        "::error::these jobs of the run did not succeed:"
        "%0Afailure completed analyze / Analyze (python)"
        "%0Acancelled completed analyze / Analyze (actions)"
        "%0Atimed_out completed other\n"
    ) in capsys.readouterr().out
    assert clock.slept == []


def test_the_listing_is_printed_before_any_verdict_is(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A failing check says what it saw first."""
    _listing(script, monkeypatch, [_FAILED_PY, _CHECK])

    assert _run(script) == 1

    shown = capsys.readouterr().out
    assert shown.index("failure\tcompleted") < shown.index("::error::")
    assert clock.slept == []


def test_a_listing_with_no_unfinished_job_is_refused(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """This job is running, so a listing without it is not this run's.

    The annotation carries no list, there being no row to name.
    """
    _listing(script, monkeypatch, [_ANALYZE_PY, ("success", "completed", "x")])

    assert _run(script) == 1

    assert (
        "::error::this check should be the run's one unfinished job; 0 are\n"
        in capsys.readouterr().out
    )
    assert clock.slept == []


def test_a_second_unfinished_job_is_refused_and_named(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A job of another workflow still running is not this job's to accept."""
    other = ("unfinished", "queued", "lint")
    _listing(script, monkeypatch, [_ANALYZE_PY, other, _CHECK])

    assert _run(script) == 1

    assert (
        "::error::this check should be the run's one unfinished job; 2 are"
        "%0Aunfinished queued lint"
        "%0Aunfinished in_progress codeql: every job passed\n"
    ) in capsys.readouterr().out
    assert clock.slept == []


@pytest.mark.parametrize(
    "name",
    [
        "analyze",
        "analyze /",
        "analyzer / Analyze (python)",
        "Analyze / analyze / Analyze (python)",
        "analyze/ Analyze (python)",
    ],
)
def test_only_a_row_under_the_needs_jobs_prefix_lags(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    """A name that merely resembles the prefix is nobody's to accept."""
    listing = _listing(script, monkeypatch, [("unfinished", "queued", name), _CHECK])

    assert _run(script) == 1

    assert listing.count == 1
    assert clock.slept == []


def test_a_gh_that_fails_fails_the_check_and_is_not_read_again(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A read that failed is no lagging row: the check says so and ends."""

    def failing(_run: tuple[str, str]) -> list[object]:
        """Fail the way `subprocess.run(check=True)` does."""
        raise subprocess.CalledProcessError(_GH_FAILED, ["gh"])

    monkeypatch.setattr(script, "list_jobs", failing)

    assert _run(script) == 1

    assert "::error::`gh api` exited 4 reading the run's jobs" in (
        capsys.readouterr().out
    )
    assert clock.slept == []


def test_the_listing_is_read_through_gh_and_every_page_of_it(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`--paginate` prints one object per row, page after page.

    A row with no conclusion yet is `unfinished`, and a blank line, which
    is what a page holding no row prints, is no row.
    """
    seen: list[list[str]] = []
    pages = (
        '{"conclusion":"success","status":"completed","name":"a / b"}\n'
        '{"conclusion":null,"status":"queued","name":"c"}\n'
        "\n"
        '{"conclusion":"failure","status":"completed","name":"d"}\n'
    )

    def gh(command: list[str], **options: object) -> subprocess.CompletedProcess[str]:
        """Answer as `gh api --paginate` does, recording the command."""
        seen.append(command)
        assert options["check"] is True
        return subprocess.CompletedProcess(command, 0, stdout=pages)

    monkeypatch.setattr(script.subprocess, "run", gh)

    rows = script.list_jobs(script.Run(_REPOSITORY, _RUN_ID))

    assert rows == [
        script.Row("success", "completed", "a / b"),
        script.Row("unfinished", "queued", "c"),
        script.Row("failure", "completed", "d"),
    ]
    assert seen == [
        [
            "gh",
            "api",
            "--paginate",
            f"repos/{_REPOSITORY}/actions/runs/{_RUN_ID}/jobs?per_page=100",
            "--jq",
            ".jobs[] | {conclusion, status, name}",
        ]
    ]


def test_the_run_is_read_from_the_environment_the_runner_sets(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The job passes the needs job and its result, and nothing else."""
    listing = _listing(script, monkeypatch, [_ANALYZE_PY, _CHECK])
    monkeypatch.setenv("GITHUB_REPOSITORY", "btclib-org/other")
    monkeypatch.setenv("GITHUB_RUN_ID", "7")
    monkeypatch.setattr(sys, "argv", ["prog", "analyze", "success"])

    assert script.main() == 0

    assert listing.asked == [("btclib-org/other", "7")]
    assert clock.slept == []


@pytest.mark.parametrize("unset", ["GITHUB_REPOSITORY", "GITHUB_RUN_ID"])
def test_a_run_that_is_not_named_is_a_usage_error(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, unset: str
) -> None:
    """Outside a runner there is no run to read, and nothing is read."""
    monkeypatch.setenv("GITHUB_REPOSITORY", "btclib-org/other")
    monkeypatch.setenv("GITHUB_RUN_ID", "7")
    monkeypatch.delenv(unset)
    listing = _listing(script, monkeypatch, [_CHECK])

    with pytest.raises(SystemExit) as raised:
        script.main(["analyze", "success"])

    assert raised.value.code == _USAGE
    assert listing.count == 0
