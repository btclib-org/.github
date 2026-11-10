# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the release sections check of `.github/scripts`.

The script is loaded by path, `.github/scripts` being no package, as the
other scripts under it are tested. Its heading verdict is compared with
the awk program `reusable-version-check.yml` runs on a tag, read out of
that workflow and run here on the same files.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from . import ROOT
from .workflows_test import jobs

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

_SCRIPT = ROOT / ".github" / "scripts" / "check_release_sections.py"
_VERSION_CHECK = ROOT / ".github" / "workflows" / "reusable-version-check.yml"

_PREAMBLE = "# Changelog\n\nThe record.\n\n"
_PREVIOUS = "## v2026.11.7\n\n### An entry\n\nIts body (closes #1).\n"
_WIP = "## v2026.12 (work in progress, not released yet)\n\n### Folded\n\nIt.\n\n"
_RELEASE = "## v2026.12.3\n\n### Folded\n\nIt.\n\n"


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("check_release_sections", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "check_release_sections", module)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("text", "base"),
    [
        pytest.param(
            _PREAMBLE + _RELEASE + _PREVIOUS, _PREAMBLE + _PREVIOUS, id="added"
        ),
        pytest.param(
            _PREAMBLE + _RELEASE + _PREVIOUS,
            _PREAMBLE + _WIP + _PREVIOUS,
            id="folded",
        ),
        pytest.param(
            _PREAMBLE + "```text\n## v1\n```\n\n" + _RELEASE + _PREVIOUS,
            _PREAMBLE + "```text\n## v1\n```\n\n" + _PREVIOUS,
            id="a-fenced-heading",
        ),
    ],
)
def test_a_release_section_added_above_the_previous_passes(
    script: ModuleType, text: str, base: str
) -> None:
    """The release's section first, the rest of the file the base's."""
    assert script.problems("2026.12.3", text, base) == []


@pytest.mark.parametrize(
    ("text", "base", "why"),
    [
        pytest.param(
            _PREAMBLE + "## v2026.12.3 (draft)\n\nIt.\n\n" + _PREVIOUS,
            _PREAMBLE + _PREVIOUS,
            'not "## v2026.12.3" alone',
            id="words-after-the-heading",
        ),
        pytest.param(
            _PREAMBLE + _PREVIOUS + "\n" + _RELEASE,
            _PREAMBLE + _PREVIOUS,
            "the first \"## \" heading is '## v2026.11.7'",
            id="below-the-previous",
        ),
        pytest.param(
            _PREAMBLE + "## v2026.12.3\n\n\n" + _PREVIOUS,
            _PREAMBLE + _PREVIOUS,
            "is empty",
            id="empty",
        ),
        pytest.param(
            _PREAMBLE + _RELEASE + _WIP + _PREVIOUS,
            _PREAMBLE + _WIP + _PREVIOUS,
            "still heads a work-in-progress section",
            id="work-in-progress-kept",
        ),
        pytest.param(
            _PREAMBLE + _RELEASE + _PREVIOUS.replace("closes #1", "closes #2"),
            _PREAMBLE + _PREVIOUS,
            "differs from the base",
            id="a-released-entry-changed",
        ),
        pytest.param(
            "# Changelog\n\n" + _RELEASE + _PREVIOUS,
            _PREAMBLE + _PREVIOUS,
            "differs from the base",
            id="the-preamble-changed",
        ),
        pytest.param(
            _PREAMBLE + "```text\n## v2026.12.3\n```\n\n" + _PREVIOUS,
            _PREAMBLE + _PREVIOUS,
            "the first \"## \" heading is '## v2026.11.7'",
            id="a-fenced-release-heading",
        ),
    ],
)
def test_a_section_that_is_not_the_release_s_alone_is_refused(
    script: ModuleType, text: str, base: str, why: str
) -> None:
    """Each shape the docstring refuses is refused, saying why."""
    found = script.problems("2026.12.3", text, base)
    assert found
    assert any(why in problem for problem in found), found


def test_run_as_a_program_it_names_the_file(tmp_path: Path) -> None:
    """A refusal is an `::error` annotation on the file, and exits 1."""
    (tmp_path / "base.md").write_text(_PREAMBLE + _PREVIOUS)
    edited = tmp_path / "CHANGELOG.md"
    for text, expected in ((_PREAMBLE + _RELEASE + _PREVIOUS, 0), (_PREVIOUS, 1)):
        edited.write_text(text)
        done = subprocess.run(
            [sys.executable, str(_SCRIPT), "2026.12.3", str(edited), "base.md"],
            cwd=tmp_path,
            capture_output=True,
            encoding="utf-8",
            check=False,
        )
        assert done.returncode == expected, done.stdout + done.stderr
        assert (f"::error file={edited}::" in done.stdout) == bool(expected)


def _awk(tmp_path: Path, text: str) -> int:
    """Run version-check's release-notes step on both files holding `text`.

    :param tmp_path: holds the files and a stand-in `uv`.
    :param text: what both files hold.
    :returns: the step's exit status.
    """
    name = "Check that the release notes are written for the tag (release only)"
    (run,) = [
        step["run"]
        for step in jobs(_VERSION_CHECK)["version-check"]["steps"]
        if step.get("name") == name
    ]
    for file in ("RELEASE_NOTES.md", "CHANGELOG.md"):
        (tmp_path / file).write_text(text)
    uv = tmp_path / "uv"
    uv.write_text("#!/bin/sh\necho 2026.12.3\n")
    uv.chmod(0o755)
    return subprocess.run(
        ["bash", "-e", "-c", run],
        cwd=tmp_path,
        env={**os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}"},
        capture_output=True,
        check=False,
    ).returncode


@pytest.mark.parametrize(
    "section",
    [
        pytest.param(_RELEASE, id="alone"),
        pytest.param("## v2026.12.3 (draft)\n\nIt.\n\n", id="words-after"),
        pytest.param("## v2026.12.3\n\n\n", id="empty"),
        pytest.param("", id="missing"),
    ],
)
def test_the_heading_verdict_is_version_check_s(
    script: ModuleType, tmp_path: Path, section: str
) -> None:
    """Where the release's section stands first, both pass or both refuse.

    The script also refuses a section that is not first, which the awk
    program does not ask.
    """
    text = _PREAMBLE + section + _PREVIOUS
    refused = bool(script.problems("2026.12.3", text, _PREAMBLE + _PREVIOUS))
    assert refused == bool(_awk(tmp_path, text))
