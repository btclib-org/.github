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

from . import ORG, ROOT, SELF, by_hand

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
    script: ModuleType, root: Path, status: int = 0, *flags: str
) -> tuple[int, list[list[str]]]:
    """Run `main` with a stand-in for uv, returning its status and commands."""
    commands: list[list[str]] = []

    def run(command: list[str]) -> int:
        commands.append(command)
        return status

    return script.main([str(root), *flags], run=run), commands


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


def test_all_groups_leaves_none_out_and_keeps_the_rest(
    script: ModuleType, tmp_path: Path
) -> None:
    """The lint job's audit reads the whole lock, with the same ignores."""
    vex = '[[not_affected]]\nid = "GHSA-aaaa"\n'
    code, commands = _ran(script, _tree(tmp_path, vex=vex), 0, "--all-groups")

    assert code == 0
    assert commands == [
        [
            "uv",
            "audit",
            "--preview-features",
            "audit-command",
            "--locked",
            "--ignore",
            "GHSA-aaaa",
        ]
    ]


def test_all_groups_still_refuses_a_tree_ignore(
    script: ModuleType, tmp_path: Path
) -> None:
    """The refusal of a second ignore list does not depend on the groups."""
    pyproject = _PYPROJECT + '\n[tool.uv.audit]\nignore = ["GHSA-aaaa"]\n'
    code, commands = _ran(script, _tree(tmp_path, pyproject), 0, "--all-groups")

    assert code == 1
    assert commands == []


_GROUPED = (
    '[[not_affected]]\nid = "GHSA-aaaa"\nsource = "GitHub"\ncomponent = "ecdsa"\n'
    'group = "test"\ndetail = "A test tool the release does not ship."\n\n'
    '[[not_affected]]\nid = "GHSA-bbbb"\nsource = "GitHub"\n'
)


def _ignores(command: list[str]) -> list[str]:
    """Return the ids a command passes as `--ignore`."""
    return [command[i + 1] for i, part in enumerate(command) if part == "--ignore"]


def test_a_group_entry_is_ignored_by_the_whole_lock_audit_only(
    script: ModuleType, tmp_path: Path
) -> None:
    """The release ships the wheel, so a development group's id is not its."""
    tree = _tree(tmp_path, vex=_GROUPED)

    _, release = _ran(script, tree)
    _, whole = _ran(script, tree, 0, "--all-groups")

    assert _ignores(release[0]) == ["GHSA-bbbb"]
    assert _ignores(whole[0]) == ["GHSA-aaaa", "GHSA-bbbb"]


@pytest.mark.parametrize(
    ("entry", "message"),
    [
        ('group = "nope"\ndetail = "r"\ncomponent = "x"\n', "which the tree lacks"),
        ('group = "test"\ncomponent = "x"\n', "gives no `detail`"),
        ('group = "test"\ndetail = ""\ncomponent = "x"\n', "gives no `detail`"),
        ('group = 7\ndetail = "r"\ncomponent = "x"\n', "not a string"),
        ('group = "test"\ndetail = "r"\n', "no `component`"),
        # the rehearsal: a package both required and in a group, whose
        # advisory `--ignore`, being global, would exempt in the wheel too
        ('group = "test"\ndetail = "r"\ncomponent = "Left_Pad"\n', "wheel ships"),
        ('group = "test"\ndetail = "r"\ncomponent = "sphinx"\n', "wheel ships"),
    ],
    ids=[
        "unknown group",
        "no reason",
        "empty reason",
        "not a string",
        "no component",
        "required",
        "extra",
    ],
)
def test_a_bad_group_entry_is_refused(
    script: ModuleType,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    entry: str,
    message: str,
) -> None:
    """An unfit group entry stops both audits."""
    pyproject = _PYPROJECT + '\n[project.optional-dependencies]\ndocs = ["sphinx"]\n'
    vex = f'[[not_affected]]\nid = "GHSA-aaaa"\n{entry}'
    tree = _tree(tmp_path, pyproject, vex)

    for flags in ((), ("--all-groups",)):
        code, commands = _ran(script, tree, 0, *flags)

        assert code == 1
        assert commands == []
        assert message in capsys.readouterr().out


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


def _setup(steps: list[dict[str, Any]]) -> dict[str, Any]:
    """Return the last `setup-uv` step of these, the one the next runs on."""
    step: dict[str, Any] = [
        s for s in steps if s.get("uses", "").startswith("astral-sh/setup-uv@")
    ][-1]
    return step


# `!cancelled()` runs the step after a failed one.
_ALWAYS = "${{ !cancelled() }}"


def _audit_step(job: dict[str, Any]) -> str:
    """Return the job's audit command, once it ends the job on the pin.

    :param job: a `lint` job that writes the audit out.
    :returns: the `run` of the step that calls the script.
    """
    steps = job["steps"]
    last = steps[-1]
    run: str = last.get("run", "")
    assert "check_audit.py" in run, "the audit is not the last step"
    assert "--all-groups" in run, "the audit passes no --all-groups"
    assert last.get("if", _ALWAYS) == _ALWAYS, "the audit step is conditional"
    setup = _setup(steps[:-1])
    pinned = _setup(_job()["steps"])["with"]["version"]
    assert setup.get("with", {}).get("version") == pinned, f"not the pin, {pinned}"
    assert setup.get("if") == last.get("if"), "the uv step's condition differs"
    return run


@pytest.mark.parametrize(
    ("name", "script"),
    [
        ("reusable-lint.yml", "standard/.github/scripts/check_audit.py"),
        ("lint.yml", ".github/scripts/check_audit.py"),
    ],
)
def test_the_lint_job_audits_on_the_uv_the_release_audit_pins(
    name: str, script: str
) -> None:
    """The pin is written once per workflow file, and the copies are equal.

    :param name: the workflow holding a copy of the pin.
    :param script: where its step finds the script.
    """
    path = ROOT / ".github" / "workflows" / name
    job = yaml.safe_load(path.read_text(encoding="utf-8"))["jobs"]["lint"]

    run = _audit_step(job)

    assert re.search(rf"(?<![\w/]){re.escape(script)}(?!\w)", run)


def test_the_lint_gate_audits_the_whole_lock(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """The tree's `lint.yml` calls the reusable workflow or carries the step.

    A call is enough: the job it runs is the one the test above reads. A
    tree that writes its `lint` job out owes the audit as the job's last
    step, on the uv `reusable-audit.yml` pins. A tree with no `uv.lock`
    has nothing for `uv audit --locked` to read, and owes none.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    if not (trees[repository] / "uv.lock").is_file():
        pytest.skip(f"{repository} has no uv.lock")
    path = trees[repository] / ".github" / "workflows" / "lint.yml"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if f"{ORG}/{SELF}/.github/workflows/reusable-lint.yml@main" in text:
        return
    hint = by_hand(repository, "grep -c check_audit .github/workflows/lint.yml")
    jobs = yaml.safe_load(text).get("jobs", {}) if text else {}
    assert "lint" in jobs, (
        f"lint.yml neither calls reusable-lint.yml nor has a lint job; {hint}"
    )
    try:
        _audit_step(jobs["lint"])
    except (AssertionError, IndexError) as lacking:
        msg = (
            "lint.yml's lint job does not end with the audit on the uv "
            f"{_WORKFLOW.name} pins ({lacking!r}); {hint}"
        )
        raise AssertionError(msg) from lacking


def test_a_group_entry_notice_does_not_say_the_release(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A group's id does not affect what is audited, not the release."""
    _ran(script, _tree(tmp_path, vex=_GROUPED), 0, "--all-groups")

    out = capsys.readouterr().out
    assert "GHSA-aaaa is ignored" in out
    assert "GHSA-aaaa is ignored, .github/vex.toml judging it not to affect what" in out
    assert "GHSA-bbbb is ignored, .github/vex.toml judging it not to affect the" in out


_LOCK = """\
version = 1

[[package]]
name = "t"
version = "0"
source = { virtual = "." }
dependencies = [{ name = "carrier" }]

[package.dev-dependencies]
dev = [{ name = "py-wormgpt" }, { name = "dev-only" }]

[[package]]
name = "carrier"
version = "1.0.0"
source = { registry = "https://invalid.invalid/simple" }
dependencies = [
    { name = "t" },
    { name = "py-wormgpt", extra = ["fast"] },
]

[[package]]
name = "py-wormgpt"
version = "1.0.0"
source = { registry = "https://invalid.invalid/simple" }
dependencies = [{ name = "carrier" }]

[package.optional-dependencies]
fast = [{ name = "Speed_Up" }]

[[package]]
name = "speed-up"
version = "1"
source = { registry = "https://invalid.invalid/simple" }

[[package]]
name = "dev-only"
version = "1"
source = { registry = "https://invalid.invalid/simple" }
"""


def test_the_lock_closure_reaches_what_a_dependency_brings_in(
    script: ModuleType, tmp_path: Path
) -> None:
    """Carrier needs py-wormgpt, and the cycles back to it end the walk."""
    tree = _tree(tmp_path)
    (tree / "uv.lock").write_text(_LOCK, encoding="utf-8")

    names = script.shipped(tree)

    assert {"left-pad", "carrier", "py-wormgpt", "speed-up", "t"} <= names
    assert "dev-only" not in names


def test_a_group_entry_for_a_package_a_dependency_ships_is_refused(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The rehearsal: the group holds py-wormgpt and so does the wheel."""
    vex = (
        '[[not_affected]]\nid = "MAL-2026-17886"\nsource = "OSV"\n'
        'component = "py-wormgpt"\ngroup = "test"\ndetail = "r"\n'
    )
    tree = _tree(tmp_path, vex=vex)
    (tree / "uv.lock").write_text(_LOCK, encoding="utf-8")

    code, commands = _ran(script, tree, 0, "--all-groups")

    assert code == 1
    assert commands == []
    assert "which the wheel ships" in capsys.readouterr().out


def test_a_group_only_package_is_not_shipped_by_the_lock(
    script: ModuleType, tmp_path: Path
) -> None:
    """A group entry for a package only a group holds is still passed."""
    vex = (
        '[[not_affected]]\nid = "GHSA-aaaa"\nsource = "OSV"\n'
        'component = "dev-only"\ngroup = "test"\ndetail = "r"\n'
    )
    tree = _tree(tmp_path, vex=vex)
    (tree / "uv.lock").write_text(_LOCK, encoding="utf-8")

    _, commands = _ran(script, tree, 0, "--all-groups")

    assert _ignores(commands[0]) == ["GHSA-aaaa"]
