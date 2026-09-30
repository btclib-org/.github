# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the release audit of `.github/scripts`.

The audit runs in a release, so no pull request reaches it and a release
is the first run that would: what it passes to `uv audit` and what it
refuses is established here. The command is handed to a stand-in for uv,
except by the test running the script as a command, which puts a stub
`uv` of its own first on the `PATH`.

The script is loaded by path, `.github/scripts` being no package, as the
other scripts under it are tested.
"""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import ROOT

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

_SCRIPT = ROOT / ".github" / "scripts" / "check_audit.py"
_WORKFLOW = ROOT / ".github" / "workflows" / "reusable-audit.yml"
_UNREACHABLE = 2
_PYPROJECT = """\
[project]
name = "t"
version = "0"
dependencies = ["left-pad"]

[dependency-groups]
test = ["pytest"]
docs = ["sphinx"]
"""


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("check_audit", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "check_audit", module)
    spec.loader.exec_module(module)
    return module


def _tree(root: Path, pyproject: str = _PYPROJECT, vex: str | None = None) -> Path:
    """Write a tree's two files the script reads, the VEX list if given."""
    (root / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    if vex is not None:
        (root / ".github").mkdir()
        (root / ".github" / "vex.toml").write_text(vex, encoding="utf-8")
    return root


def _ran(
    script: ModuleType, root: Path, status: int = 0
) -> tuple[int, list[list[str]]]:
    """Run `main` with a stand-in for uv, returning its status and commands."""
    commands: list[list[str]] = []

    def run(command: list[str]) -> int:
        commands.append(command)
        return status

    return script.main([str(root)], run=run), commands


def test_every_group_is_left_out_and_the_locked_flag_is_passed(
    script: ModuleType, tmp_path: Path
) -> None:
    """What is audited is what the wheel declares, asserted by `--locked`."""
    code, commands = _ran(script, _tree(tmp_path))

    assert code == 0
    assert commands == [
        [
            "uv",
            "audit",
            "--preview-features",
            "audit-command",
            "--locked",
            "--no-group",
            "test",
            "--no-group",
            "docs",
        ]
    ]
    assert "--frozen" not in commands[0]


def test_a_tree_with_no_group_passes_no_group_flag(
    script: ModuleType, tmp_path: Path
) -> None:
    """A tree declaring no group has nothing to leave out."""
    pyproject = '[project]\nname = "t"\nversion = "0"\n'
    _, commands = _ran(script, _tree(tmp_path, pyproject))

    assert "--no-group" not in commands[0]


def test_the_vex_ids_are_the_only_ignores(script: ModuleType, tmp_path: Path) -> None:
    """Each `[[not_affected]]` id is one `--ignore`, once."""
    vex = (
        '[[not_affected]]\nid = "GHSA-aaaa"\nsource = "GitHub"\n\n'
        '[[not_affected]]\nid = "PYSEC-2026-1"\nsource = "OSV"\n\n'
        '[[not_affected]]\nid = "GHSA-aaaa"\nsource = "GitHub"\n'
    )
    _, commands = _ran(script, _tree(tmp_path, vex=vex))

    command = commands[0]
    ignores = [command[i + 1] for i, part in enumerate(command) if part == "--ignore"]
    assert ignores == ["GHSA-aaaa", "PYSEC-2026-1"]
    assert "--ignore-until-fixed" not in command


def test_an_ignore_is_said_in_the_log(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Uv says nothing of an ignored advisory, so the log says it."""
    vex = '[[not_affected]]\nid = "GHSA-aaaa"\n'
    _ran(script, _tree(tmp_path, vex=vex))

    assert "::notice::GHSA-aaaa is ignored" in capsys.readouterr().out


@pytest.mark.parametrize("status", [1, 2])
def test_the_status_of_uv_is_the_status_of_the_script(
    script: ModuleType, tmp_path: Path, status: int
) -> None:
    """Exit 1, an advisory, and exit 2, no service, both fail."""
    code, _ = _ran(script, _tree(tmp_path), status)

    assert code == status


def test_an_id_that_is_not_a_string_is_refused(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A list a typo made unreadable audits nothing rather than ignoring it."""
    code, commands = _ran(script, _tree(tmp_path, vex="[[not_affected]]\nid = 7\n"))

    assert code == 1
    assert commands == []
    assert "::error::" in capsys.readouterr().out


def test_an_entry_with_no_id_is_refused(script: ModuleType, tmp_path: Path) -> None:
    """A table without an `id` names nothing to ignore."""
    code, commands = _ran(
        script, _tree(tmp_path, vex='[[not_affected]]\nsource = "x"\n')
    )

    assert code == 1
    assert commands == []


def test_an_ignore_kept_in_pyproject_is_refused(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`[tool.uv.audit]` is an ignore the release's document lacks."""
    pyproject = _PYPROJECT + '\n[tool.uv.audit]\nignore = ["GHSA-aaaa"]\n'
    code, commands = _ran(script, _tree(tmp_path, pyproject))

    assert code == 1
    assert commands == []
    assert "[tool.uv.audit]" in capsys.readouterr().out


def test_an_ignore_kept_in_uv_toml_is_refused(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`[audit]` in `uv.toml` is the same list in the other file uv reads."""
    _tree(tmp_path)
    (tmp_path / "uv.toml").write_text(
        '[audit]\nignore = ["GHSA-aaaa"]\n', encoding="utf-8"
    )
    code, commands = _ran(script, tmp_path)

    assert code == 1
    assert commands == []
    assert "uv.toml" in capsys.readouterr().out


def test_a_uv_toml_without_an_audit_table_is_no_refusal(
    script: ModuleType, tmp_path: Path
) -> None:
    """Only the audit table is what the script refuses."""
    _tree(tmp_path)
    (tmp_path / "uv.toml").write_text(
        '[pip]\nindex-strategy = "first-index"\n', encoding="utf-8"
    )

    assert _ran(script, tmp_path)[0] == 0


def test_the_script_runs_as_a_command_and_returns_what_uv_returns(
    tmp_path: Path,
) -> None:
    """A stub `uv` first on the `PATH` receives the command and exits 2."""
    (tmp_path / "tree").mkdir()
    tree = _tree(tmp_path / "tree")
    stub = tmp_path / "bin"
    stub.mkdir()
    (stub / "uv").write_text(
        '#!/bin/sh\necho "$@" > "$STUBLOG"\nexit 2\n', encoding="utf-8"
    )
    (stub / "uv").chmod(0o755)
    log = tmp_path / "log"

    ran = subprocess.run(
        [sys.executable, str(_SCRIPT)],
        capture_output=True,
        cwd=tree,
        encoding="utf-8",
        check=False,
        env={
            **os.environ,
            "PATH": f"{stub}{os.pathsep}{os.environ['PATH']}",
            "STUBLOG": str(log),
        },
    )

    assert ran.returncode == _UNREACHABLE, ran.stdout + ran.stderr
    assert log.read_text(encoding="utf-8").split()[:4] == [
        "audit",
        "--preview-features",
        "audit-command",
        "--locked",
    ]


def _job() -> dict[str, Any]:
    """Return the workflow's one job."""
    parsed = yaml.safe_load(_WORKFLOW.read_text(encoding="utf-8"))
    job: dict[str, Any] = parsed["jobs"]["audit"]
    return job


def test_the_pin_is_at_or_above_every_trees_floor(
    repository: str, pyprojects: dict[str, dict[str, Any]]
) -> None:
    """A floor above the pin makes uv exit 2, which reads as no service."""
    setup = next(
        s
        for s in _job()["steps"]
        if s.get("uses", "").startswith("astral-sh/setup-uv@")
    )
    declared = pyprojects.get(repository, {}).get("tool", {}).get("uv", {})
    floor = str(declared.get("required-version", "")).removeprefix(">=")
    if not re.fullmatch(r"\d+(\.\d+)*", floor):
        pytest.skip(f"{repository} names no bare [tool.uv] required-version")

    def key(version: str) -> tuple[int, ...]:
        return tuple(int(part) for part in version.split("."))

    assert key(str(setup["with"]["version"])) >= key(floor), (
        f"{repository} requires uv {floor}, above the pin in {_WORKFLOW.name}"
    )


def test_the_workflow_runs_the_script_where_its_checkout_puts_it() -> None:
    """The path in the command is the checkout's `path:` and this file's."""
    steps = _job()["steps"]
    checkout = next(s for s in steps if s.get("with", {}).get("path") == "standard")
    run = next(s["run"] for s in steps if "check_audit.py" in s.get("run", ""))

    assert checkout["with"]["sparse-checkout"] == ".github/scripts"
    assert f"standard/{_SCRIPT.relative_to(ROOT).as_posix()}" in run
