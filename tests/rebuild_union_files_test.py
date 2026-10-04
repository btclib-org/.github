# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The script that rebuilds the union files after a rebase or a merge.

Each test builds a repository: a base, a branch `topic` that adds a block to
a union file, and a `main` that moved meanwhile. The rebase is run for real,
with the `merge=union` driver where the test says so, so the damage the
script repairs is git's own and not a model of it. A control asserts the
rebase left the file different from what the script then writes.

The script is loaded by path, `.github/scripts` being no package, as the
other scripts under it are tested.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from . import ROOT

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

SCRIPT = ROOT / ".github" / "scripts" / "rebuild_union_files.py"
NAME = "CHANGELOG.md"
REFUSED = 2
OPEN = "## Unreleased\n\n### Old\n\n- old\n"
RELEASED = "\n## v1\n\n- v1\n"
BASE = OPEN + RELEASED


def entry(heading: str, *lines: str) -> str:
    """Return an entry, with the blank line above it the files keep."""
    return f"\n### {heading}\n\n" + "".join(f"{line}\n" for line in lines)


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("rebuild_union_files", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "rebuild_union_files", module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Make an empty repository the working directory."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.chdir(tmp_path)
    git("init", "--quiet", "--initial-branch=main")
    return tmp_path


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run git in the working directory as `Ann`."""
    return subprocess.run(
        ["git", "-c", "user.name=Ann", "-c", "user.email=ann@example.org", *args],
        capture_output=True,
        encoding="utf-8",
        check=check,
    )


def commit(root: Path, text: str, name: str = NAME) -> str:
    """Commit the file with this text, and return the commit."""
    (root / name).write_text(text, encoding="utf-8")
    git("add", name)
    git("commit", "--quiet", "-m", text[:20] or "empty")
    return git("rev-parse", "HEAD").stdout.strip()


def rebase(
    root: Path, texts: tuple[str, str, str], *, union: bool, name: str = NAME
) -> tuple[str, str, subprocess.CompletedProcess[str]]:
    """Rebase a topic over a landing; return the old base, old tip and the run.

    `texts` are the file at the base, on the topic and on `main`.
    """
    base, topic, landed = texts
    if union:
        (root / ".gitattributes").write_text(f"{name} merge=union\n", encoding="utf-8")
        git("add", ".gitattributes")
        git("commit", "--quiet", "-m", "attributes")
    old_base = commit(root, base, name)
    git("checkout", "--quiet", "-b", "topic")
    old_tip = commit(root, topic, name)
    git("checkout", "--quiet", "main")
    commit(root, landed, name)
    git("checkout", "--quiet", "topic")
    return old_base, old_tip, git("rebase", "main", check=False)


def run(script: ModuleType, old_base: str, old_tip: str, *extra: str) -> int:
    """Run the script as a session does, naming the new base `main`."""
    return int(script.main([old_base, old_tip, "--base", "main", *extra]))


def test_the_eaten_blank_line_is_put_back(
    script: ModuleType, repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`merge=union` writes the blank line both entries start with once."""
    landed = BASE.replace(RELEASED, entry("B", "- b") + RELEASED)
    topic = BASE.replace(RELEASED, entry("A", "- a") + RELEASED)
    old_base, old_tip, ran = rebase(repo, (BASE, topic, landed), union=True)
    expected = landed.replace(RELEASED, entry("A", "- a") + RELEASED)

    assert ran.returncode == 0
    assert (repo / NAME).read_text(encoding="utf-8") != expected

    assert run(script, old_base, old_tip) == 1
    assert (repo / NAME).read_text(encoding="utf-8") == expected
    assert capsys.readouterr().out.startswith(f"{NAME}: written")
    assert run(script, old_base, old_tip) == 0
    assert capsys.readouterr().out.startswith(f"{NAME}: agrees")


def test_a_shared_last_line_is_put_back(script: ModuleType, repo: Path) -> None:
    """A citation line both entries end with is kept once by the driver."""
    landed = OPEN + entry("B", "- b", "  (issue #5)")
    topic = OPEN + entry("A", "- a", "  (issue #5)")
    old_base, old_tip, ran = rebase(repo, (OPEN, topic, landed), union=True)
    expected = landed + entry("A", "- a", "  (issue #5)")

    assert ran.returncode == 0
    assert (repo / NAME).read_text(encoding="utf-8") != expected

    assert run(script, old_base, old_tip) == 1
    assert (repo / NAME).read_text(encoding="utf-8") == expected


def test_a_shared_heading_is_put_back(script: ModuleType, repo: Path) -> None:
    """A heading both entries open with is kept once by the driver."""
    base = OPEN
    landed = base + entry("Fixed", "- b")
    topic = base + entry("Fixed", "- a")
    old_base, old_tip, ran = rebase(repo, (base, topic, landed), union=True)
    expected = landed + entry("Fixed", "- a")

    assert ran.returncode == 0
    assert (repo / NAME).read_text(encoding="utf-8") != expected

    assert run(script, old_base, old_tip) == 1
    assert (repo / NAME).read_text(encoding="utf-8") == expected


def test_a_stopped_rebase_is_resolved(script: ModuleType, repo: Path) -> None:
    """Without the driver the rebase stops, with markers in the file."""
    landed = BASE.replace(RELEASED, entry("B", "- b") + RELEASED)
    topic = BASE.replace(RELEASED, entry("A", "- a") + RELEASED)
    old_base, old_tip, ran = rebase(repo, (BASE, topic, landed), union=False)
    expected = landed.replace(RELEASED, entry("A", "- a") + RELEASED)

    assert ran.returncode != 0
    assert "<<<<<<<" in (repo / NAME).read_text(encoding="utf-8")

    assert run(script, old_base, old_tip) == 1
    assert (repo / NAME).read_text(encoding="utf-8") == expected
    assert run(script, old_base, old_tip) == 0


def test_a_stopped_merge_takes_the_branch_merged_in(
    script: ModuleType, repo: Path
) -> None:
    """During a merge `HEAD`'s merge base with `main` is the old base."""
    landed = BASE.replace(RELEASED, entry("B", "- b") + RELEASED)
    topic = BASE.replace(RELEASED, entry("A", "- a") + RELEASED)
    old_base, old_tip, _ = rebase(repo, (BASE, topic, landed), union=False)
    git("rebase", "--abort", check=False)
    git("merge", "main", check=False)
    expected = landed.replace(RELEASED, entry("A", "- a") + RELEASED)

    assert git("merge-base", "HEAD", "main").stdout.strip() == old_base
    assert script.default_base() == git("rev-parse", "main").stdout.strip()
    assert script.main([old_base, old_tip]) == 1
    assert (repo / NAME).read_text(encoding="utf-8") == expected


def test_a_release_on_the_new_base_moves_the_block(
    script: ModuleType, repo: Path
) -> None:
    """The block goes to the section that is open now, not the one it was in."""
    topic = BASE.replace(RELEASED, entry("A", "- a") + RELEASED)
    landed = "## Unreleased\n\n## v2\n\n### Old\n\n- old\n" + RELEASED
    old_base, old_tip, ran = rebase(repo, (BASE, topic, landed), union=True)
    expected = "## Unreleased\n" + entry("A", "- a") + landed[len("## Unreleased\n") :]

    assert ran.returncode == 0
    assert (repo / NAME).read_text(encoding="utf-8") != expected

    assert run(script, old_base, old_tip) == 1
    assert (repo / NAME).read_text(encoding="utf-8") == expected


def test_tight_release_notes_bullets_get_no_blank_line(
    script: ModuleType, repo: Path
) -> None:
    """A block is put where it stood, with the blank lines it had."""
    base = "## v2 (WIP)\n\n- old\n\n## v1\n"
    topic = base.replace("- old\n", "- old\n- a\n")
    landed = base.replace("- old\n", "- old\n- b\n")
    name = "RELEASE_NOTES.md"
    old_base, old_tip, _ = rebase(repo, (base, topic, landed), union=False, name=name)

    assert run(script, old_base, old_tip) == 1
    expected = base.replace("- old\n", "- old\n- b\n- a\n")
    assert (repo / name).read_text(encoding="utf-8") == expected


def test_a_block_that_is_not_one_addition_is_refused(
    script: ModuleType, repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Two separate additions, or an edit, are not a block."""
    topic = BASE.replace("- old\n", "- old\n- a\n").replace("- v1\n", "- v1\n- c\n")
    landed = BASE + entry("B", "- b")
    old_base, old_tip, _ = rebase(repo, (BASE, topic, landed), union=True)
    before = (repo / NAME).read_text(encoding="utf-8")

    assert run(script, old_base, old_tip) == REFUSED
    assert "not one contiguous addition" in capsys.readouterr().out
    assert (repo / NAME).read_text(encoding="utf-8") == before


def test_a_place_that_is_not_found_is_refused(
    script: ModuleType, repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The lines after the block are not at the end of the new open section."""
    topic = BASE.replace("- old\n", "- a\n- old\n")
    landed = BASE.replace("- old\n", "- other\n")
    old_base, old_tip, _ = rebase(repo, (BASE, topic, landed), union=False)
    before = (repo / NAME).read_text(encoding="utf-8")

    assert run(script, old_base, old_tip) == REFUSED
    assert "not at the end of the open section" in capsys.readouterr().out
    assert (repo / NAME).read_text(encoding="utf-8") == before


def test_a_block_outside_the_open_section_is_refused(
    script: ModuleType, repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An addition in a released section is not an entry."""
    topic = BASE + "- late\n"
    old_base, old_tip, _ = rebase(repo, (BASE, topic, BASE + "- x\n"), union=True)

    assert run(script, old_base, old_tip) == REFUSED
    assert "does not lie in the open section" in capsys.readouterr().out


def test_a_file_the_branch_did_not_touch_is_left_alone(
    script: ModuleType, repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Only the file the branch changed is read and written."""
    name = "RELEASE_NOTES.md"
    commit(repo, "- same\n", name)
    topic = BASE.replace(RELEASED, entry("A", "- a") + RELEASED)
    landed = BASE.replace("- old\n", "- old\n- b\n")
    old_base, old_tip, _ = rebase(repo, (BASE, topic, landed), union=True)
    (repo / name).write_text("kept\n", encoding="utf-8")

    assert run(script, old_base, old_tip) == 0
    assert (repo / name).read_text(encoding="utf-8") == "kept\n"
    assert f"{name}: the branch did not change it" in capsys.readouterr().out
