# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the `CHANGELOG.md` open-section check of `.github/scripts`.

The script's own module docstring is the argument for what it checks and
why; this exercises both readings of it.
`test_this_trees_own_open_section_is_clean` runs it unmodified, against
this tree's own file, which is the same question the `pre-commit` hook
asks on every commit -- and this repository's own open section is its
whole history, there being no release to bound it, so a false positive
here is not a corner case but the first thing a coder would hit. Every
other test builds a small file of its own instead, one for each of the
three checks and the shapes each must not answer to.

The script is loaded by path, `.github/scripts` being no package.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import TYPE_CHECKING

import pytest

from . import ROOT

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

_SCRIPT = ROOT / ".github" / "scripts" / "check_changelog.py"

_CLEAN = """\
# Changelog

## Unreleased

### First entry

- **first thing** (closes #1): one.

### Second entry

- **second thing** (closes #2): two.
"""


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("check_changelog", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "check_changelog", module)
    spec.loader.exec_module(module)
    return module


def test_this_trees_own_open_section_is_clean(script: ModuleType) -> None:
    """This repository's own `CHANGELOG.md`, read unmodified, passes."""
    assert script.main() == 0


def test_a_clean_fixture_is_a_positive_control(script: ModuleType) -> None:
    """The fixture text itself passes, which is what its problems() answer."""
    assert script.problems(_CLEAN) == []


def test_a_repeated_heading_is_caught(script: ModuleType) -> None:
    """Two `### ` headings with the same text is the first check."""
    text = _CLEAN.replace("Second entry", "First entry")
    found = script.problems(text)
    assert len(found) == 1
    assert "repeats the heading" in found[0]


def test_two_entries_closing_one_issue_is_caught(script: ModuleType) -> None:
    """Two entries each `(closes #N)` the same number is the second check."""
    text = _CLEAN.replace("(closes #2)", "(closes #1)")
    found = script.problems(text)
    assert len(found) == 1
    assert "closes #1, already closed by" in found[0]


def test_a_heading_glued_to_the_line_above_is_caught(script: ModuleType) -> None:
    """A `### ` with no blank line above it is the third check."""
    text = _CLEAN.replace("\n\n### Second entry", "\n### Second entry")
    found = script.problems(text)
    assert len(found) == 1
    assert "no blank line above it" in found[0]


def test_the_same_entry_closing_twice_is_not_reported(script: ModuleType) -> None:
    """A list body citing the issue its heading answers again is normal.

    Section 9 of README.md lets an entry make several related claims
    about the one issue it answers, each bullet citing it again.
    """
    text = _CLEAN.replace(
        "- **first thing** (closes #1): one.\n",
        "- **first thing** (closes #1): one.\n\n- **again** (closes #1): still one.\n",
    )
    assert script.problems(text) == []


def test_an_issue_advanced_by_two_entries_is_not_reported(script: ModuleType) -> None:
    """`(issue #N)` recurring across entries is this tree's own convention.

    A tree that never releases, this repository among them, keeps one
    open section for its whole history, so a long-lived issue is
    answered across several entries over as many weeks -- normal, by
    section 9's *A live claim* rule, and not what the second check asks
    about.
    """
    text = _CLEAN.replace("(closes #2)", "(issue #1)")
    assert script.problems(text) == []


def test_one_entry_advancing_and_another_closing_is_not_reported(
    script: ModuleType,
) -> None:
    """`(issue #N)` followed later by `(closes #N)` is the ordinary case."""
    text = _CLEAN.replace("(closes #1)", "(issue #1)")
    assert script.problems(text.replace("(closes #2)", "(closes #1)")) == []


def test_a_mixed_group_closes_only_the_keyword_it_names(script: ModuleType) -> None:
    """`(closes #593, issue #571)` closes the first number, not the second."""
    text = _CLEAN.replace("(closes #1)", "(closes #593, issue #571)").replace(
        "(closes #2)",
        "(closes #571)",
    )
    assert script.problems(text) == []


def test_two_entries_closing_the_same_number_under_mixed_groups_is_caught(
    script: ModuleType,
) -> None:
    """The keyword nearest a token decides it, in both entries at once."""
    text = _CLEAN.replace("(closes #1)", "(issue #9, closes #1)").replace(
        "(closes #2)",
        "(closes #1)",
    )
    found = script.problems(text)
    assert len(found) == 1
    assert "closes #1, already closed by" in found[0]


def test_a_cross_repository_citation_compares_as_written(script: ModuleType) -> None:
    """A bare `#N` and a qualified `owner/repo#N` are different tokens."""
    text = _CLEAN.replace("(closes #2)", "(closes btclib-org/btclib-node#1)")
    assert script.problems(text) == []


def test_two_qualified_citations_of_one_issue_are_caught(script: ModuleType) -> None:
    """Two entries closing the same `owner/repo#N` collide as written."""
    text = _CLEAN.replace("(closes #1)", "(closes btclib-org/btclib-node#1)").replace(
        "(closes #2)",
        "(closes btclib-org/btclib-node#1)",
    )
    found = script.problems(text)
    assert len(found) == 1
    assert "btclib-org/btclib-node#1, already closed by" in found[0]


def test_a_released_section_is_outside_the_open_one(script: ModuleType) -> None:
    """A duplicate under a second `## ` is a release, not the open section."""
    text = _CLEAN + "\n## v1.0\n\n### First entry\n\n- **again** (closes #1): one.\n"
    assert script.problems(text) == []


def test_a_quoted_example_is_not_read_as_a_citation(script: ModuleType) -> None:
    """A backtick-quoted `(closes #N)` is prose, not a citation of its own."""
    text = _CLEAN.replace(
        "- **second thing** (closes #2): two.",
        "- **second thing** (closes #2): the first entry's body reads"
        " `(closes #1)` verbatim.",
    )
    assert script.problems(text) == []


def test_main_reports_a_problem_and_returns_1(
    script: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`main()` prints the finding and exits 1, the shape the hook reads."""
    broken = tmp_path / "CHANGELOG.md"
    broken.write_text(_CLEAN.replace("Second entry", "First entry"), encoding="utf-8")
    monkeypatch.setattr(script, "_CHANGELOG", broken)
    assert script.main() == 1
    out = capsys.readouterr().out
    assert "repeats the heading" in out


def test_main_reports_nothing_wrong_and_returns_0(
    script: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A clean file prints one summary line and exits 0."""
    clean = tmp_path / "CHANGELOG.md"
    clean.write_text(_CLEAN, encoding="utf-8")
    monkeypatch.setattr(script, "_CHANGELOG", clean)
    assert script.main() == 0
    out = capsys.readouterr().out
    assert "repeats no heading" in out
