# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the public API check of `.github/scripts`.

`reusable-public-api.yml` runs on a release, so no pull request reaches
it and the day a release breaks the surface is the first run that would.
What decides a finding covered is established here instead, against
lines `griffe check -f oneline` printed for btclib between two of its
releases, and a section of notes written the way btclib's are.

The script is loaded by path, `.github/scripts` being no package, as the
other scripts under it are tested.
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
    from pathlib import Path
    from types import ModuleType

_SCRIPT = ROOT / ".github" / "scripts" / "check_public_api.py"
_WORKFLOW = ROOT / ".github" / "workflows" / "reusable-public-api.yml"

# lines `griffe check -f oneline` printed for btclib between two releases
_FINDINGS = (
    "src/btclib/hwi.py:0: <module>: Public object was removed\n"
    "src/btclib/alias.py:0: MnemonicLang: Public object was removed\n"
    "src/btclib/alias.py:0: H160_Net: Public object was removed\n"
    "src/btclib/exceptions.py:518: "
    "ScriptError.__init__(index): Positional parameter was moved\n"
    "src/btclib/exceptions.py:518: "
    "ScriptError.__init__(code): Parameter was added as required\n"
    "src/btclib/bip32/__init__.py:0: <module>: Public object was removed\n"
    "src/btclib/script/engine/script_op_codes.py:207: "
    "read_push_data(element_size_limit): Parameter was removed\n"
    "src/btclib/script/engine/script.py:0: prepare_script: "
    "Public object was removed\n"
)

_NOTES = """\
# Release notes

Only what a user has to act on, and `not_a_finding` is not one.

## v2026.10 (work in progress, not released yet)

Nothing yet.

## v2026.9.29

### Breaking changes

- **`btclib.hwi` is gone**: use `btclib_wallet.hwi`.
- **`MnemonicLang` and `H160_Net` leave `btclib.alias`.**
- **`ScriptError(code, ...)` takes the code first**, and `index` moves.
- **`btclib.bip32` is a module of `btclib_wallet`** and the same for
  `btclib.script.engine.script.prepare_script`, which is now
  `prepare_script(script, flags,
  segwit)` in the wallet.
- **`read_push_data` drops its limit.**

```shell
git grep -n 'ScriptError' -- src
```

## v2026.9.24

- **`unrelated` is named only here.**
"""


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("check_public_api", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "check_public_api", module)
    spec.loader.exec_module(module)
    return module


def _run(
    script: ModuleType,
    tmp_path: Path,
    *,
    findings: str = _FINDINGS,
    notes: str = _NOTES,
    tag: str | None = "v2026.9.29",
) -> int:
    """Run `main` on files of the test's own, and return its exit code."""
    (tmp_path / "findings.txt").write_text(findings, encoding="utf-8")
    (tmp_path / "RELEASE_NOTES.md").write_text(notes, encoding="utf-8")
    argv = [
        "btclib",
        str(tmp_path / "findings.txt"),
        str(tmp_path / "RELEASE_NOTES.md"),
    ]
    if tag:
        argv += ["--tag", tag]
    code: int = script.main(argv)
    return code


def test_findings_the_section_names_are_all_covered(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A module by its dotted path, the rest by their name, all pass."""
    code = _run(script, tmp_path)

    printed = capsys.readouterr().out
    assert code == 0, printed
    assert printed.count("covered   ") == len(_FINDINGS.splitlines())
    assert "uncovered" not in printed
    assert "::error" not in printed


@pytest.mark.parametrize(
    ("entry", "named"),
    [
        ("- **`btclib.hwi` is gone**: use `btclib_wallet.hwi`.\n", "btclib.hwi"),
        ("- **`read_push_data` drops its limit.**\n", "read_push_data"),
        (
            "- **`ScriptError(code, ...)` takes the code first**, and `index` moves.\n",
            "ScriptError.__init__(index)",
        ),
    ],
)
def test_a_finding_the_section_does_not_name_is_refused_by_name(
    script: ModuleType,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    entry: str,
    named: str,
) -> None:
    """Remove the entry naming an object and the object is what is reported."""
    assert entry in _NOTES

    code = _run(script, tmp_path, notes=_NOTES.replace(entry, ""))

    printed = capsys.readouterr().out
    assert code == 1
    assert printed.splitlines()[-1].startswith("::error::")
    assert named in printed.splitlines()[-1]


def test_one_uncovered_finding_leaves_the_others_covered(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Every finding is printed, and only the missing one is marked so."""
    entry = "- **`read_push_data` drops its limit.**\n"

    _run(script, tmp_path, notes=_NOTES.replace(entry, ""))

    lines = capsys.readouterr().out.splitlines()
    uncovered = [line for line in lines if line.startswith("uncovered ")]
    assert len(uncovered) == 1
    assert "read_push_data(element_size_limit)" in uncovered[0]
    assert sum(line.startswith("covered   ") for line in lines) == (
        len(_FINDINGS.splitlines()) - 1
    )
    assert any(
        line.startswith("::error file=src/btclib/script/engine") for line in lines
    )


def test_a_module_is_not_named_by_its_package(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`btclib` in a span does not name `btclib.hwi`, nor does `hwi`."""
    notes = _NOTES.replace("`btclib.hwi` is gone", "`btclib` and `hwi` are gone")

    code = _run(script, tmp_path, notes=notes.replace("`btclib_wallet.hwi`", "x"))

    assert code == 1
    assert (
        capsys.readouterr().out.splitlines()[-1].endswith("does not name: btclib.hwi")
    )


def test_a_name_is_read_from_the_section_and_not_from_elsewhere(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A span above the section, in a fence or in another one names nothing."""
    notes = _NOTES.replace("`read_push_data` drops", "`read` drops")
    notes = notes.replace("# Release notes", "# Release notes\n\n`read_push_data`")
    notes = notes.replace("git grep -n", "`read_push_data`\ngit grep -n")
    notes = notes.replace("`unrelated`", "`read_push_data`")

    code = _run(script, tmp_path, notes=notes)

    assert code == 1
    assert (
        capsys.readouterr()
        .out.splitlines()[-1]
        .endswith("does not name: read_push_data(element_size_limit)")
    )


def test_a_rehearsal_reads_the_first_section_under_the_title(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """With no tag the open section is read, whatever its heading."""
    code = _run(script, tmp_path, tag=None)
    assert code == 1
    assert "does not name" in capsys.readouterr().out

    open_section = _NOTES.replace("Nothing yet.", "`btclib.hwi` ...")
    for heading in (
        "## v2026.10 (work in progress, not released yet)",
        "## Unreleased",
        "## v0.8.0.10 (work in progress, not released yet)",
    ):
        renamed = open_section.replace(
            "## v2026.10 (work in progress, not released yet)", heading
        )
        code = _run(
            script,
            tmp_path,
            notes=renamed,
            findings="src/btclib/hwi.py:0: <module>: Public object was removed\n",
            tag=None,
        )
        assert code == 0, heading


@pytest.mark.parametrize(
    ("heading", "found"),
    [
        ("## v2026.9.29", True),
        ("## v2026.9.29 (patched)", True),
        ("## v2026.9.290", False),
        ("### v2026.9.29", False),
        ("## v2026.9.2", False),
    ],
)
def test_a_tag_heading_is_the_tag_and_then_a_space_or_nothing(
    script: ModuleType, heading: str, *, found: bool
) -> None:
    """A longer last component, or a deeper heading, is not the tag's."""
    notes = f"# Release notes\n\n## v1\n\n{heading}\n\nbody `x`\n\n## v0\n"

    section = script.section(notes, "v2026.9.29")

    assert (section is not None) is found
    if found:
        assert section == "\nbody `x`\n"


def test_a_tag_with_no_section_is_refused_when_there_are_findings(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The notes were not written for this release, so nothing is covered."""
    code = _run(script, tmp_path, tag="v2027.1.1")

    assert code == 1
    assert "has no section for v2027.1.1" in capsys.readouterr().out


def test_no_findings_reads_no_notes(script: ModuleType, tmp_path: Path) -> None:
    """A release with no finding needs no notes file at all."""
    (tmp_path / "findings.txt").write_text("", encoding="utf-8")

    assert script.main(["btclib", str(tmp_path / "findings.txt"), "absent.md"]) == 0


def test_a_line_that_is_no_finding_is_refused(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A line griffe printed in another shape is never dropped as noise."""
    line = "Traceback (most recent call last):"

    code = _run(script, tmp_path, findings=line + "\n")

    assert code == 1
    assert capsys.readouterr().out.splitlines()[-1].endswith(f"does not name: {line}")


@pytest.mark.parametrize(
    ("path", "dotted"),
    [
        ("src/btclib/hwi.py", "btclib.hwi"),
        ("src/btclib/bip32/__init__.py", "btclib.bip32"),
        ("btclib/hwi.py", "btclib.hwi"),
        ("btclib/__init__.py", "btclib"),
        ("src/btclib_node/a/b.py", "src.btclib_node.a.b"),
    ],
)
def test_a_module_is_named_by_the_path_from_its_package(
    script: ModuleType, path: str, dotted: str
) -> None:
    """Whatever precedes the package on the path, a search path, is dropped."""
    (finding,) = script.findings(f"{path}:0: <module>: gone", "btclib")

    assert finding.name == dotted


def test_a_span_that_wraps_is_one_span(script: ModuleType) -> None:
    """A code span breaks across a line of the notes as any prose does."""
    assert "prepare_script" in script.named("`prepare_script(script,\nflags)`")


def test_the_script_runs_as_a_command(tmp_path: Path) -> None:
    """The exit code a step reads is the script's own."""
    (tmp_path / "findings.txt").write_text(_FINDINGS, encoding="utf-8")
    (tmp_path / "RELEASE_NOTES.md").write_text(_NOTES, encoding="utf-8")

    ran = subprocess.run(
        [sys.executable, str(_SCRIPT), "btclib", "findings.txt", "RELEASE_NOTES.md"],
        capture_output=True,
        cwd=tmp_path,
        encoding="utf-8",
        check=False,
    )

    assert ran.returncode == 1
    assert "does not name" in ran.stdout


def _steps() -> list[dict[str, Any]]:
    """Return the steps of the workflow's one job."""
    parsed = yaml.safe_load(_WORKFLOW.read_text(encoding="utf-8"))
    steps: list[dict[str, Any]] = parsed["jobs"]["public-api"]["steps"]
    return steps


def test_the_workflow_runs_the_script_where_its_checkout_puts_it() -> None:
    """The path in the command is the checkout's `path:` and this file's."""
    steps = _steps()
    checkout = next(s for s in steps if s.get("with", {}).get("path") == "standard")
    run = next(s["run"] for s in steps if "check_public_api.py" in s.get("run", ""))

    assert checkout["with"]["sparse-checkout"] == ".github/scripts"
    assert f"standard/{_SCRIPT.relative_to(ROOT).as_posix()}" in run


def test_the_workflow_hands_the_script_griffe_s_whole_output() -> None:
    """The findings are on standard error, so the redirect takes both.

    uv writes its own progress there too, which is what `--quiet` is for.
    """
    run = next(s["run"] for s in _steps() if "griffe" in s.get("run", ""))

    assert "-f oneline" in run
    assert "2>&1" in run
    assert "uvx --quiet" in run
