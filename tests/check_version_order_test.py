# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the release version order check of `.github/scripts`.

The check runs only on a tag push, so no rehearsal reaches it and a
release is the first run that would: what it refuses is established here
or on the day it matters. The tags are passed in rather than read off a
repository, except by the test running the script as a command, which
builds a repository of its own to read them from.

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
import yaml

from . import ROOT

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

_SCRIPT = ROOT / ".github" / "scripts" / "check_version_order.py"
_WORKFLOW = ROOT / ".github" / "workflows" / "reusable-version-check.yml"
_TAGS = ["v2026.9.3", "v2026.9.24", "v2026.9.13", "v2022.2.9-patch1"]


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("check_version_order", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "check_version_order", module)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("version", ["2026.9.20", "2026.9.13", "2026.9.24.0"])
def test_a_version_not_above_the_latest_release_is_refused(
    script: ModuleType, version: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """The versions btclib-org/.github#1318 was filed for do not pass.

    The latest release is found by version and not by where it is listed,
    a version tagged already still sorts below it with its own tag left
    out, and a version equal to it under PEP 440 does not sort above it.
    """
    assert script.main([version], tags=_TAGS) == 1

    reported = capsys.readouterr().out
    assert reported.startswith(f"::error::{version} does not sort above v2026.9.24")


def test_a_day_released_again_under_a_lower_patch_is_refused(
    script: ModuleType,
) -> None:
    """A patch component counts, a missing one reading as zero."""
    assert script.check("2026.9.24", ["v2026.9.24.1"])
    assert script.check("2026.9.24.1", ["v2026.9.24.2"])


@pytest.mark.parametrize("version", ["2026.9.25", "2026.9.24.1", "2026.10.1"])
def test_a_version_above_the_latest_release_passes(
    script: ModuleType, version: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """A release sorting above every one tagged is no defect."""
    assert script.main([version], tags=_TAGS) == 0

    assert capsys.readouterr().out == f"{version} sorts above every release tagged\n"


def test_the_tag_being_released_is_not_compared(script: ModuleType) -> None:
    """The tag pushed for the version is in the checkout, and is the version."""
    assert script.check("2026.9.25", [*_TAGS, "v2026.9.25"]) is None


def test_the_components_are_compared_as_integers(script: ModuleType) -> None:
    """0.8.0.10 sorts above 0.8.0.9, which a string comparison denies."""
    assert script.check("0.8.0.10", ["v0.8.0.9", "v0.8.0"]) is None
    assert script.check("0.8.0.9", ["v0.8.0.10"])


def test_a_tag_of_another_shape_is_not_compared(script: ModuleType) -> None:
    """Neither a tag without the `v` nor one past digits and dots orders."""
    tags = ["2027.1.1", "v2027.1.1rc1", "history/dev-2027.1.1", "vendor"]

    assert script.check("2026.9.25", tags) is None


def test_the_first_release_passes(script: ModuleType) -> None:
    """With no release tagged there is nothing to sort below."""
    assert script.check("2026.9.24", []) is None


def test_a_version_past_digits_and_dots_is_refused(script: ModuleType) -> None:
    """A version the check cannot order is refused, never passed."""
    assert script.check("2026.9.25rc1", _TAGS)


def _git(where: Path, *args: str) -> None:
    """Run git in a repository of the test's own, reading no config file."""
    quiet = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(
        ["git", "-C", str(where), "-c", "user.name=t", "-c", "user.email=t@t", *args],
        capture_output=True,
        check=True,
        env={**os.environ, **quiet},
    )


@pytest.mark.parametrize(("version", "code"), [("2026.9.20", 1), ("2026.9.25", 0)])
def test_the_script_reads_the_tags_of_the_working_directory(
    tmp_path: Path, version: str, code: int
) -> None:
    """Run as a command, with no tags passed in."""
    _git(tmp_path, "init", "--quiet")
    _git(tmp_path, "commit", "--quiet", "--allow-empty", "-m", "a release")
    _git(tmp_path, "tag", "v2026.9.24")

    ran = subprocess.run(
        [sys.executable, str(_SCRIPT), version],
        capture_output=True,
        cwd=tmp_path,
        encoding="utf-8",
        check=False,
    )

    assert ran.returncode == code, ran.stdout


def _steps() -> list[dict[str, Any]]:
    """Return the steps of the workflow's one job."""
    parsed = yaml.safe_load(_WORKFLOW.read_text(encoding="utf-8"))
    steps: list[dict[str, Any]] = parsed["jobs"]["version-check"]["steps"]
    return steps


def test_the_workflow_runs_the_script_on_every_release() -> None:
    """A tree passing tag-requires-day: false is ordered as well.

    btclib-secp256k1's 0.8.0.7 is digits and dots, so nothing keeps that
    tree out of the check, and the scripts checkout has to reach it too.
    """
    steps = _steps()
    run = next(s for s in steps if "check_version_order.py" in s.get("run", ""))
    checkout = next(s for s in steps if s.get("with", {}).get("path") == "standard")

    assert run["if"] == "github.event_name == 'push'"
    assert checkout["if"] == "github.event_name == 'push'"


def test_the_workflow_runs_the_script_where_its_checkout_puts_it() -> None:
    """The path in the command is the checkout's `path:` and this file's."""
    steps = _steps()
    checkout = next(s for s in steps if s.get("with", {}).get("path") == "standard")
    run = next(s["run"] for s in steps if "check_version_order.py" in s.get("run", ""))

    assert checkout["with"]["sparse-checkout"] == ".github/scripts"
    assert f"standard/{_SCRIPT.relative_to(ROOT).as_posix()}" in run


def test_the_workflow_fetches_the_tags_it_compares_with() -> None:
    """The caller's checkout takes the whole history, its tags with it."""
    checkout = _steps()[0]

    assert checkout["uses"].startswith("actions/checkout@")
    assert checkout["with"]["fetch-depth"] == 0
