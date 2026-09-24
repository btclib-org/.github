# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the calendar version date check of `.github/scripts`.

The check runs only on a tag push, and only on a calendar-versioned
tree, so no rehearsal reaches it and a release is the first run that
would: what it refuses is established here or on the day it matters.
The instant the version is checked at is passed in rather than read off
the clock, which is what makes the boundary at UTC+14 exact. A test runs
the script as a command, on the real clock, with dates so far on either
side of it that the answer cannot depend on when it runs.

The tests reading `reusable-version-check.yml` itself are there because
what keeps a tree that is not calendar-versioned out of this check is
the workflow's `if:` and not the script, which refuses such a version.

The script is loaded by path, `.github/scripts` being no package, as the
other scripts under it are tested.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import ROOT

if TYPE_CHECKING:
    from types import ModuleType

_SCRIPT = ROOT / ".github" / "scripts" / "check_calendar_version.py"
_WORKFLOW = ROOT / ".github" / "workflows" / "reusable-version-check.yml"
# a fixed instant, so that no verdict below depends on when the suite runs
_THAT_DAY = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("check_calendar_version", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "check_calendar_version", module)
    spec.loader.exec_module(module)
    return module


def test_a_version_dated_next_month_is_refused(
    script: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    """The version btclib-org/.github#1310 was filed for does not pass."""
    assert script.main(["2026.10.24"], now=_THAT_DAY) == 1

    reported = capsys.readouterr().out
    assert reported.startswith("::error::2026.10.24 is dated 2026-10-24")


@pytest.mark.parametrize(
    "version", ["2026.9.24", "2026.9.24.1", "2026.9.1", "2025.12.31"]
)
def test_a_version_dated_today_or_earlier_passes(
    script: ModuleType, version: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """A release dated the day it runs, or before, is no defect."""
    assert script.main([version], now=_THAT_DAY) == 0

    assert capsys.readouterr().out == f"{version} is not dated in the future\n"


def test_the_day_after_in_utc_passes_once_it_has_begun_at_utc_plus_14(
    script: ModuleType,
) -> None:
    """The slack is the furthest-ahead time zone's date, to the minute."""
    assert script.check("2026.9.25", datetime(2026, 9, 24, 9, 59, tzinfo=UTC))
    assert script.check("2026.9.25", datetime(2026, 9, 24, 10, 0, tzinfo=UTC)) is None


def test_two_days_after_in_utc_is_refused_at_the_last_minute_of_it(
    script: ModuleType,
) -> None:
    """The slack is one day and not more."""
    assert script.check("2026.9.26", datetime(2026, 9, 24, 23, 59, tzinfo=UTC))


def test_an_instant_in_another_zone_is_read_as_the_same_instant(
    script: ModuleType,
) -> None:
    """The comparison is with an instant, not with a wall clock's date."""
    rome = datetime.fromisoformat("2026-09-25T00:30+02:00")

    assert script.check("2026.9.25", rome) is None
    assert script.check("2026.9.26", rome)


@pytest.mark.parametrize("version", ["2026.2.30", "2026.13.1", "0.8.0.7", "2026.9"])
def test_a_version_naming_no_date_is_refused(script: ModuleType, version: str) -> None:
    """A version the check cannot date is refused, never passed."""
    assert script.check(version, _THAT_DAY)


@pytest.mark.parametrize(("version", "code"), [("9999.12.31", 1), ("2000.1.1", 0)])
def test_the_script_reads_the_real_clock_when_run(version: str, code: int) -> None:
    """Run as a command, with no instant passed in."""
    ran = subprocess.run(
        [sys.executable, str(_SCRIPT), version],
        capture_output=True,
        encoding="utf-8",
        check=False,
    )

    assert ran.returncode == code, ran.stdout


def _steps() -> list[dict[str, Any]]:
    """Return the steps of the workflow's one job."""
    parsed = yaml.safe_load(_WORKFLOW.read_text(encoding="utf-8"))
    steps: list[dict[str, Any]] = parsed["jobs"]["version-check"]["steps"]
    return steps


def test_the_workflow_runs_the_script_only_on_a_calendar_release() -> None:
    """A tree passing tag-requires-day: false never reaches the script.

    btclib-secp256k1's 0.8.0.7 is refused by the script, as
    `test_a_version_naming_no_date_is_refused` says, so the condition is
    what keeps that tree's release open.
    """
    run = next(s for s in _steps() if "check_calendar_version.py" in s.get("run", ""))

    assert run["if"] == "github.event_name == 'push' && inputs.tag-requires-day"


def test_the_workflow_runs_the_script_where_its_checkout_puts_it() -> None:
    """The path in the command is the checkout's `path:` and this file's."""
    steps = _steps()
    checkout = next(s for s in steps if s.get("with", {}).get("path") == "standard")
    run = next(
        s["run"] for s in steps if "check_calendar_version.py" in s.get("run", "")
    )

    assert checkout["with"]["sparse-checkout"] == ".github/scripts"
    assert f"standard/{_SCRIPT.relative_to(ROOT).as_posix()}" in run
