# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the `CHANGELOG.md` open-section check of `.github/scripts`.

The script's own module docstring is the argument for what it checks and
why; this exercises both readings of it.
`test_this_trees_own_open_section_is_clean` runs it against this tree's
own file with the arguments this tree's own gate gives the hook, which
is the same question `pre-commit` asks on every commit -- and this
repository's own open section is its whole history, there being no
release to bound it, so a false positive here is not a corner case but
the first thing a coder would hit. The other tests build a small file of
their own instead, for the shapes a check must and must not answer to --
or, where a check reads a count or a placement rather than the section's
own text, drive that function directly on a fragment.

The arguments are read off `.pre-commit-config.yaml` rather than written
here: `--grandfathered` is a fact about this repository's history, and a
second copy of the number is the one that goes stale.

The script is loaded by path, `.github/scripts` being no package.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest
import yaml

from . import ROOT

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

_SCRIPT = ROOT / ".github" / "scripts" / "check_changelog.py"
_GATE = ROOT / ".pre-commit-config.yaml"
_HOOK = "check-changelog"
_CHANGELOG = ROOT / "CHANGELOG.md"

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


def arguments() -> list[str]:
    """Return the arguments this tree's own gate gives the hook.

    :returns: the `args:` of the `check-changelog` hook, in file order.
    """
    parsed = yaml.safe_load(_GATE.read_text(encoding="utf-8"))
    return [
        argument
        for entry in parsed["repos"]
        for hook in entry["hooks"]
        if hook["id"] == _HOOK
        for argument in hook.get("args", [])
    ]


def test_the_gate_names_the_count(script: ModuleType) -> None:
    """The gate passes `--grandfathered`, which the test below leans on.

    Without it the run below would measure the default instead, and pass
    for a reason that says nothing about this repository.
    """
    assert "--grandfathered" in arguments(), (
        f"{_GATE.name} gives {_HOOK} no --grandfathered"
    )
    assert script.problems(_CHANGELOG.read_text(encoding="utf-8")), (
        "this repository's open section passes at the default count, so"
        " the argument the gate passes decides nothing"
    )


def test_this_trees_own_open_section_is_clean(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """This repository's own `CHANGELOG.md`, read as the hook reads it.

    `_CHANGELOG` is the bare name the script resolves against the
    working directory `pre-commit` sets, so the file is named here
    rather than left to wherever pytest was started.
    """
    monkeypatch.setattr(script, "_CHANGELOG", _CHANGELOG)
    assert script.main(arguments()) == 0


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


def test_a_heading_less_entry_closing_the_same_issue_is_caught(
    script: ModuleType,
) -> None:
    """The second check reads the heading-less entry too, not only headed ones.

    `duplicate_closes` compares the heading-less entry's citations
    against a headed entry's, exactly as it compares two headed entries
    against each other, where the first and third checks read only the
    `### ` headings.
    """
    text = _CLEAN.replace(
        "### First entry\n\n- **first thing** (closes #1): one.\n\n",
        "- a heading-less entry (closes #1).\n\n",
    ).replace("(closes #2)", "(closes #1)")
    found = script.problems(text)
    assert len(found) == 1
    assert "closes #1, already closed by the heading-less entry" in found[0]


def test_a_heading_glued_to_the_line_above_is_caught(script: ModuleType) -> None:
    """A `### ` with no blank line above it is the third check."""
    text = _CLEAN.replace("\n\n### Second entry", "\n### Second entry")
    found = script.problems(text)
    assert len(found) == 1
    assert "no blank line above it" in found[0]


def test_the_same_entry_closing_twice_is_not_reported(script: ModuleType) -> None:
    """A list body citing the issue its heading answers again is normal.

    Section 9 of README.md has the body cite the issue in its own text,
    so a list body cites it in each bullet that claims something of it.
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


_LONG = "- one\n- two\n- three\n- four\n"


def test_a_long_body_after_the_rule_entry_is_caught(script: ModuleType) -> None:
    """The fourth check reads from the entry the rule entered with.

    The count passed is what the fixture holds above the rule heading,
    so the fifth check has nothing to say and the finding this asks
    about is the only one left.
    """
    rule = f"### {script.RULE_HEADING}\n\n- rule.\n"
    found = script.problems(f"{_CLEAN}\n{rule}\n### Long\n\n{_LONG}", 2)
    assert len(found) == 1
    assert "'Long'" in found[0]
    assert "4 lines" in found[0]


def test_a_long_body_before_the_rule_entry_is_not_reported(script: ModuleType) -> None:
    """An entry above the rule entry predates the rule and stays.

    The long entry is above the heading here, so the count passed is one
    higher than the test above's, for the same reason.
    """
    rule = f"### {script.RULE_HEADING}\n\n- rule.\n"
    assert script.problems(f"{_CLEAN}\n### Long\n\n{_LONG}\n{rule}", 3) == []


def test_misplaced_entries_is_clean_within_the_grandfathered_count(
    script: ModuleType,
) -> None:
    """A count at or below `grandfathered` is not a misplacement."""
    text = f"{_CLEAN}\n### {script.RULE_HEADING}\n\n- rule.\n"
    section, base = script.open_section(text)
    assert script.misplaced_entries(text, section, base, grandfathered=2) == []


def test_misplaced_entries_is_caught_past_the_grandfathered_count(
    script: ModuleType,
) -> None:
    """More entries above `RULE_HEADING` than `grandfathered` is refused.

    This is the blind spot btclib-org/.github#1204 named: an entry
    landed above `RULE_HEADING` by mistake reads, to `long_bodies()`, as
    older than the rule it postdates, and passes unmeasured. This check
    is what refuses it instead.
    """
    text = f"{_CLEAN}\n### {script.RULE_HEADING}\n\n- rule.\n"
    section, base = script.open_section(text)
    found = script.misplaced_entries(text, section, base, grandfathered=1)
    assert len(found) == 1
    assert "2 entries land above the rule heading" in found[0]
    assert "more than the 1 this repository grandfathers" in found[0]


def test_misplaced_entries_is_silent_where_the_rule_heading_is_absent(
    script: ModuleType,
) -> None:
    """A released section has no `RULE_HEADING` to count entries above."""
    section, base = script.open_section(_CLEAN)
    assert script.misplaced_entries(_CLEAN, section, base, grandfathered=0) == []


def test_a_misplaced_long_body_is_refused_once_grandfathered_is_exceeded(
    script: ModuleType,
) -> None:
    """The demonstrated shape: a misplaced, over-long entry is refused.

    `test_a_long_body_before_the_rule_entry_is_not_reported` above shows
    `long_bodies()` alone never measures this entry; `misplaced_entries()`
    wired into `problems()`, with the count already past what predates
    the rule, is what stops it landing silently.
    """
    rule = f"### {script.RULE_HEADING}\n\n- rule.\n"
    text = f"{_CLEAN}\n### Long\n\n{_LONG}\n{rule}"
    section, base = script.open_section(text)
    found = script.misplaced_entries(text, section, base, grandfathered=2)
    assert len(found) == 1
    assert "an entry has landed above it" in found[0]


def test_problems_carries_the_count_to_the_check_that_reads_it(
    script: ModuleType,
) -> None:
    """`problems()` hands `--grandfathered` on, and defaults to zero.

    `test_misplaced_entries_is_caught_past_the_grandfathered_count`
    above drives the check directly; this is the path from the command
    line, which is the one a run takes. The default is asked for too:
    it is what a caller naming no count gets, and a fixture with two
    entries above the rule heading is past it.
    """
    rule = f"### {script.RULE_HEADING}\n\n- rule.\n"
    text = f"{_CLEAN}\n{rule}"
    assert script.problems(text, 2) == []
    found = script.problems(text, 1)
    assert len(found) == 1
    assert "an entry has landed above it" in found[0]
    assert len(script.problems(text)) == 1


def test_link_definitions_are_not_lines_of_the_body(script: ModuleType) -> None:
    """btclib-benchmarks ends its file with a block of reference links."""
    links = "".join(f"[iss{n}]: https://example.invalid/{n}\n" for n in range(9))
    assert script.problems(f"{_CLEAN}\n### Short\n\n- one\n\n{links}") == []


def test_every_entry_is_measured_where_the_rule_entry_is_released(
    script: ModuleType,
) -> None:
    """With no rule entry in the open section, the bound reaches every entry."""
    found = script.problems(f"{_CLEAN}\n### Long\n\n{_LONG}")
    assert len(found) == 1
    assert "'Long'" in found[0]


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
    assert script.main([]) == 1
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
    assert script.main([]) == 0
    out = capsys.readouterr().out
    assert "repeats no heading" in out


def test_a_fenced_heading_is_not_read_as_a_repeat(script: ModuleType) -> None:
    """A `### ` line inside a fenced code block is a markdown example.

    btclib-org/.github#1372: the same title, fenced under the real entry
    that carries it, used to be read as a second heading repeating the
    first.
    """
    text = _CLEAN.replace(
        "- **first thing** (closes #1): one.",
        "```markdown\n### First entry\n```",
    )
    assert script.problems(text) == []


def test_a_fenced_release_heading_does_not_end_the_section_early(
    script: ModuleType,
) -> None:
    """A fenced `## ` line is not read as the next release's heading.

    btclib-org/.github#1372: placed under an entry, it used to make
    `open_section()` stop there, leaving every real entry below it
    unmeasured.
    """
    text = _CLEAN.replace(
        "- **first thing** (closes #1): one.",
        "- **first thing** (closes #1): one.\n\n```\n## 2020.1.1\n```",
    )
    section, _base = script.open_section(text)
    assert "### Second entry" in section


def test_a_longer_closing_fence_still_closes_the_block(script: ModuleType) -> None:
    """A closing fence with more backticks than the opening one still closes.

    CommonMark closes a fence on a line with *at least* as many backticks
    as it opened with, not exactly as many.
    """
    text = _CLEAN.replace(
        "- **first thing** (closes #1): one.",
        "- **first thing** (closes #1): one.\n\n```\n## 2020.1.1\n````",
    )
    section, _base = script.open_section(text)
    assert "### Second entry" in section


def test_a_shorter_candidate_does_not_close_a_longer_fence(script: ModuleType) -> None:
    """A line with fewer backticks than the opening one is not a close.

    Placed between a fence's real open and its real close, it is content
    rather than a boundary of its own, so a `## ` line past it stays
    blanked along with the rest of the still-open fence.
    """
    text = _CLEAN.replace(
        "- **first thing** (closes #1): one.",
        "- **first thing** (closes #1): one.\n\n````\n```\n## 2020.1.1\n````",
    )
    section, _base = script.open_section(text)
    assert "### Second entry" in section


def test_a_bare_keyword_outside_a_parenthetical_names_no_token(
    script: ModuleType,
) -> None:
    """`closes #N` in the sentence names no token; `(closes #N)` names it.

    Section 9 of README.md puts the keyword inside parentheses where an
    entry acts on the issue, and where an entry only names one the
    reference leaves the parentheses and the keyword is dropped, so the
    parentheses are what `closing_tokens()` reads: a keyword outside
    them is a shape the standard refuses, not one it reads differently.
    The empty set is measured beside the non-empty one from the same
    text: on its own it is also what a pattern matching nothing answers.
    """
    bare = "- **first thing** closes #1: one."
    parenthesised = bare.replace("closes #1", "(closes #1)")
    assert script.closing_tokens(bare) == set()
    assert script.closing_tokens(parenthesised) == {"#1"}


def test_a_bare_wrapped_citation_is_caught(script: ModuleType) -> None:
    """`#N` opening a line, unfixed, is the sixth check.

    btclib-org/.github#1398's own reproduction: a citation wraps at 80
    columns so its number opens the next line, which markdownlint-cli2's
    MD018 reads as a heading missing its space.
    """
    text = _CLEAN.replace(
        "- **second thing** (closes #2): two.",
        "- **second thing** ending before a citation (closes\n#2): two.",
    )
    found = script.problems(text)
    assert len(found) == 1
    assert "'#2'" in found[0]
    assert "opens the line" in found[0]


def test_an_already_fixed_wrapped_citation_is_still_caught(
    script: ModuleType,
) -> None:
    """`# N`, the shape MD018's own `--fix` has already produced, is caught too.

    A second `--fix` run does not repair this: there is no longer a bare
    `#N` for the fixer to notice, so the mangled shape has to be refused
    directly rather than relying on a later run undoing it.
    """
    text = _CLEAN.replace(
        "- **second thing** (closes #2): two.",
        "- **second thing** ending before a citation (closes\n# 2): two.",
    )
    found = script.problems(text)
    assert len(found) == 1
    assert "'# 2'" in found[0]


def test_a_real_heading_is_not_read_as_a_wrapped_citation(
    script: ModuleType,
) -> None:
    """A `### ` heading is two or three hashes, never this check's shape.

    A numeral in the title -- as a version or an issue count might use --
    stays two or three hashes ahead of the digits: the second character
    is itself a `#`, where the pattern wants a space, a tab or a digit.
    """
    text = _CLEAN.replace("### Second entry", "### 42 things changed")
    assert script.problems(text) == []


def test_a_wrapped_citation_inside_a_fenced_block_is_not_caught(
    script: ModuleType,
) -> None:
    """A fenced code block quoting the mangled shape is an example, not one."""
    text = _CLEAN.replace(
        "- **second thing** (closes #2): two.",
        "```\n#9).\n```",
    )
    assert script.problems(text) == []


def test_a_qualified_citation_opening_a_line_is_not_this_shape(
    script: ModuleType,
) -> None:
    """`owner/repo#N` opening a line does not open it with `#` at all.

    Measured against markdownlint-cli2 directly: MD018 does not read it
    as a heading, `owner/repo` sitting ahead of the `#`, so this does not
    refuse it either.
    """
    text = _CLEAN.replace(
        "- **second thing** (closes #2): two.",
        "- **second thing** ending before a citation (closes\n"
        "btclib-org/btclib#2): two.",
    )
    assert script.problems(text) == []


def test_an_indented_wrapped_citation_is_not_caught(script: ModuleType) -> None:
    """A wrap indented to stay part of the list item above it is not this shape.

    Measured against markdownlint-cli2 directly: a citation number
    indented by even one space is never read as a heading, which is the
    shape every list-item entry's own wrap takes, so this check -- keyed
    on column zero -- does not flag it.
    """
    text = _CLEAN.replace(
        "- **second thing** (closes #2): two.",
        "- **second thing** ending before a citation (closes\n  #2): two.",
    )
    assert script.problems(text) == []


def test_a_wrapped_citation_in_a_released_section_is_not_reported(
    script: ModuleType,
) -> None:
    """A wrapped citation under a second `## ` is outside the open section."""
    text = _CLEAN + "\n## v1.0\n\nprose before a citation (closes\n#9).\n"
    assert script.problems(text) == []


_RELEASED = _CLEAN + "\n## v2\n\n### Two\n\n- two.\n\n## v1\n\n### One\n\n- one.\n"
_LATE = "\n### Late\n\n- **late** (closes #3): three.\n"
_BASE = ("0123abcd", _RELEASED)
_REFUSED = "'Late' is under a release older than the newest"


def test_an_entry_appended_under_the_oldest_release_is_caught(
    script: ModuleType,
) -> None:
    """A new entry at the file's end, as btclib-org/.github#1614 measured."""
    found = script.problems(_RELEASED + _LATE, base=_BASE)
    assert len(found) == 1
    assert _REFUSED in found[0]
    assert "CHANGELOG.md at 0123abcd, the merge base with origin/main" in found[0]


def test_an_entry_appended_to_the_open_section_is_not_reported(
    script: ModuleType,
) -> None:
    """The same entry at the end of the open section passes."""
    text = _RELEASED.replace("\n## v2", _LATE + "\n## v2")
    assert script.problems(text, base=_BASE) == []


def test_an_entry_under_the_newest_release_is_not_reported(
    script: ModuleType,
) -> None:
    """The newest release is left out: a release branch adds to it."""
    text = _RELEASED.replace("\n## v1", _LATE + "\n## v1")
    assert script.problems(text, base=_BASE) == []


def test_a_release_cut_over_the_open_section_is_not_reported(
    script: ModuleType,
) -> None:
    """Cutting a release adds no heading to the releases before it."""
    text = _RELEASED.replace("## Unreleased", "## Unreleased\n\n## v3")
    assert script.problems(text, base=_BASE) == []


def test_a_fenced_heading_at_the_base_does_not_vouch_for_a_real_one(
    script: ModuleType,
) -> None:
    """A `### ` line in a fence at the base is an example, not the entry."""
    before = _RELEASED + "\n```text\n### Late\n```\n"
    found = script.problems(before + _LATE, base=("0123abcd", before))
    assert len(found) == 1
    assert _REFUSED in found[0]


def test_a_fenced_heading_under_an_older_release_is_not_reported(
    script: ModuleType,
) -> None:
    """A `### ` line in a fence on the branch is an example, not an entry."""
    text = _RELEASED + "\n```text\n### Fenced\n```\n"
    assert script.problems(text, base=_BASE) == []


def _git(root: Path, *args: str) -> str:
    """Run git in `root` as `Ann`, and return what it prints."""
    return subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "-c",
            "user.name=Ann",
            "-c",
            "user.email=ann@example.org",
            *args,
        ],
        capture_output=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()


def _commit(changelog: Path, text: str) -> str:
    """Commit `text` as the file, and return the commit."""
    changelog.write_text(text, encoding="utf-8")
    _git(changelog.parent, "add", changelog.name)
    _git(changelog.parent, "commit", "--quiet", "-m", text[-20:])
    return _git(changelog.parent, "rev-parse", "HEAD")


@pytest.fixture
def repo(
    script: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Path:
    """Return the file of a repository whose `origin/main` holds `_RELEASED`."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    changelog = tmp_path / "CHANGELOG.md"
    _git(tmp_path, "init", "--quiet")
    _git(
        tmp_path,
        "update-ref",
        "refs/remotes/origin/main",
        _commit(changelog, _RELEASED),
    )
    monkeypatch.setattr(script, "_CHANGELOG", changelog)
    return changelog


def test_main_refuses_an_entry_the_branch_committed(
    script: ModuleType,
    repo: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The base is the merge base, not `HEAD`, which holds the entry too."""
    base = _git(repo.parent, "rev-parse", "origin/main")
    _commit(repo, _RELEASED + _LATE)
    assert script.main([]) == 1
    out = capsys.readouterr().out
    assert _REFUSED in out
    assert f"at {base}, the merge base" in out


def test_main_passes_an_entry_in_the_open_section(
    script: ModuleType,
    repo: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The control: the same entry in the open section passes, compared."""
    _commit(repo, _RELEASED.replace("\n## v2", _LATE + "\n## v2"))
    assert script.main([]) == 0
    assert "no release older than the newest gains a heading" in capsys.readouterr().out


def test_a_stale_origin_main_refuses_until_fetched(
    script: ModuleType,
    repo: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An entry landed past a stale `origin/main` reads as the branch's own."""
    landed = _commit(repo, _RELEASED + _LATE)
    assert script.main([]) == 1
    assert _REFUSED in capsys.readouterr().out
    _git(repo.parent, "update-ref", "refs/remotes/origin/main", landed)
    assert script.main([]) == 0


def test_main_says_so_where_there_is_no_merge_base(
    script: ModuleType,
    repo: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """With no `origin/main`, the entry passes and the output says why."""
    _git(repo.parent, "update-ref", "-d", "refs/remotes/origin/main")
    _commit(repo, _RELEASED + _LATE)
    assert script.main([]) == 0
    assert "no released section compared" in capsys.readouterr().out
