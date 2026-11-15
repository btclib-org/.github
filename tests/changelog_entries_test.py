# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for `.github/scripts/changelog_entries.py` and its workflow.

The script's docstring says what it assembles and what it asks of a
diff. `assemble` is driven on a tree written in `tmp_path`, and `check`
on a git repository there, with the global and the system configuration
of git left out, so that a `commit.gpgsign` set there signs no fixture.
"""

from __future__ import annotations

import errno
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import ROOT

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import ModuleType

_SCRIPT = ROOT / ".github" / "scripts" / "changelog_entries.py"
_WORKFLOW = ROOT / ".github" / "workflows" / "reusable-changelog-entry.yml"
_LABELS = ROOT / ".github" / "labels.yml"

# the checkout's depth: the merge commit and its parents
DEPTH = 2


def _script() -> ModuleType:
    """Load the script by path, `.github/scripts` being no package."""
    spec = importlib.util.spec_from_file_location("changelog_entries", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["changelog_entries"] = module
    spec.loader.exec_module(module)
    return module


script = _script()


def _release_check() -> ModuleType:
    """Load `check_release_sections.py`, which the release's gates run."""
    path = ROOT / ".github" / "scripts" / "check_release_sections.py"
    spec = importlib.util.spec_from_file_location("check_release_sections", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release_check = _release_check()

CHANGELOG = """\
# Changelog

The preamble.

## v2026.11.14

### An older entry

Its body (closes #1).
"""

NOTES = """\
# Release notes

```markdown
## v2026.1.1 in a fence is no heading
```

## v2026.11.14

### An older note

Its body (closes #1).
"""

ENTRIES = {
    "github-2287.md": (
        "### Another repository's\n\nIts body (issue btclib-org/.github#2287).\n"
    ),
    "12.md": "### Twelve\n\nTwelve's body\nruns on (closes #12).\n",
    "3.md": "### Three\n\nThree's body (closes #3).\n",
    "bip39-slip39-7.md": (
        "### Seven there\n\nIts body (closes btclib-org/bip39-slip39#7).\n"
    ),
}

SECTION = """\
## v2026.11.15

### Three

Three's body (closes #3).

### Twelve

Twelve's body
runs on (closes #12).

### Seven there

Its body (closes btclib-org/bip39-slip39#7).

### Another repository's

Its body (issue btclib-org/.github#2287).
"""


@pytest.fixture(autouse=True)
def _git_of_its_own(monkeypatch: pytest.MonkeyPatch) -> None:
    """Read no git configuration of the user's or the system's."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")


# git run as the committer `Ann`
_AS_ANN = ("git", "-c", "user.name=Ann", "-c", "user.email=ann@example.org")


def _commit_at(root: Path) -> None:
    """Make `root` a git checkout, and commit everything in it.

    :param root: the tree's root.
    """
    for args in (
        ["init", "--quiet", "--initial-branch=main"],
        ["add", "--all"],
        ["commit", "--quiet", "--allow-empty", "-m", "tree"],
    ):
        subprocess.run(
            [*_AS_ANN, "-C", str(root), *args],
            capture_output=True,
            check=True,
        )


def _tree(root: Path, entries: dict[str, str], *, commit: bool = True) -> Path:
    """Write the history files and the entries under `root`, and commit them.

    :param root: the tree's root.
    :param entries: each entry's file name against its text.
    :param commit: whether to commit them, the assembly running on a commit.
    :returns: the directory the entries are in.
    """
    (root / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
    (root / "RELEASE_NOTES.md").write_text(NOTES, encoding="utf-8")
    directory = root / "changelog" / "next"
    directory.mkdir(parents=True)
    (directory / ".markdownlint.jsonc").write_text("{}\n", encoding="utf-8")
    for name, text in entries.items():
        (directory / name).write_text(text, encoding="utf-8")
    if commit:
        _commit_at(root)
    return directory


def test_the_entries_go_above_the_last_release_in_both_files(tmp_path: Path) -> None:
    """One section, in the fixed order, in each history file, then no entry."""
    directory = _tree(tmp_path, ENTRIES)

    removed = script.assemble("2026.11.15", tmp_path)

    assert sorted(path.name for path in removed) == sorted(ENTRIES)
    assert [path.name for path in directory.iterdir()] == [".markdownlint.jsonc"]
    changelog = (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8")
    preamble, _, rest = CHANGELOG.partition("## v2026.11.14")
    assert changelog == preamble + SECTION + "\n## v2026.11.14" + rest
    notes = (tmp_path / "RELEASE_NOTES.md").read_text(encoding="utf-8")
    above, _, below = NOTES.partition("## v2026.11.14\n")
    assert notes == above + SECTION + "\n## v2026.11.14\n" + below
    assert release_check.problems("2026.11.15", changelog, CHANGELOG) == []
    assert release_check.problems("2026.11.15", notes, NOTES) == []


def test_the_same_entries_give_the_same_bytes(tmp_path: Path) -> None:
    """Whatever order the files were written in, the files come out alike."""
    digests = set()
    for index, entries in enumerate([ENTRIES, dict(reversed(ENTRIES.items()))]):
        root = tmp_path / str(index)
        root.mkdir()
        _tree(root, entries)
        script.assemble("2026.11.15", root)
        both = b"".join((root / name).read_bytes() for name in script.FILES)
        digests.add(hashlib.sha256(both).hexdigest())
    assert len(digests) == 1


@pytest.mark.parametrize("base", ["# Changelog\n", "# Changelog\n\nIts preamble.\n\n"])
def test_a_file_with_no_release_takes_the_section_at_its_end(base: str) -> None:
    """The first release of a tree has no `## ` heading to go above.

    The release's gates take the file for the base and the section alone.

    :param base: the file before its first release.
    """
    new = script.section("1", {"3.md": ENTRIES["3.md"]})
    text = script.inserted("CHANGELOG.md", base, "1", new)

    assert text == base.rstrip("\n") + "\n\n" + new
    assert release_check.problems("1", text, base) == []


@pytest.mark.parametrize("entries", [{}, None])
def test_no_entry_is_no_release(tmp_path: Path, entries: dict[str, str] | None) -> None:
    """An empty directory and a missing one both refuse, and nothing is written.

    :param entries: the entries, None for no directory at all.
    """
    if entries is None:
        (tmp_path / "CHANGELOG.md").write_text(CHANGELOG, encoding="utf-8")
        (tmp_path / "RELEASE_NOTES.md").write_text(NOTES, encoding="utf-8")
        _commit_at(tmp_path)
    else:
        _tree(tmp_path, entries)

    with pytest.raises(script.RefusedError) as refused:
        script.assemble("2026.11.15", tmp_path)

    assert refused.value.problems == [
        (
            "changelog/next holds no entry: nothing changed for a user, so there"
            " is nothing to release"
        ),
    ]
    assert (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8") == CHANGELOG


@pytest.mark.parametrize(
    ("name", "text", "reason"),
    [
        ("notes.md", "### T\n\nB.\n", "an entry is named <n>.md or <repo>-<n>.md"),
        ("0.md", "### T\n\nB.\n", "an entry is named"),
        ("Github-1.md", "### T\n\nB.\n", "an entry is named"),
        ("1.md", "### T\n\nB.", "an entry ends with one newline"),
        ("1.md", "### T\n\nB.\n\n", "an entry ends with one newline"),
        ("1.md", "## T\n\nB.\n", "an entry opens with a `### ` title"),
        ("1.md", "- **T** (closes #1).\n", "an entry opens with a `### ` title"),
        ("1.md", "### T\nB.\n", "followed by a blank line and the body"),
        ("1.md", "### T\n", "followed by a blank line and the body"),
        ("1.md", "### T\n\none\ntwo\nthree\nfour\n", "runs past 3 lines"),
        ("1.md", "### T\n\none\n\ntwo\n", "holds no blank line and no heading"),
        ("1.md", "### T\n\none\n### U\n", "holds no blank line and no heading"),
        ("1.md", "### T\n\none\n  ## U\n", "holds no blank line and no heading"),
        ("1.md", "### T \n\nB.\n", "the title ends with no space"),
        ("1.md", "### T\r\n\r\nB.\r\n", "end with a line feed alone"),
        ("1.md", "### T\n\nB.\n```text\n", "holds no code fence"),
        ("1.md", "### T\n\nB.\n  ~~~\n", "holds no code fence"),
        ("1.md", "### T\n\nB.\n<!-- note\n", "no html block"),
        ("1.md", "### T\n\nText (closes #2).\n---\n", "no heading"),
        ("1.md", "### T\n\nText (closes #2).\n===\n", "no heading"),
        ("1.md", "### T\n\nText (closes #2).\n   =  \n", "no heading"),
        ("1.md", "### T\n\n---\nText (closes #2).\n", "no heading"),
        ("1.md", "### T\n\nB.\n> # U\n", "no heading"),
        ("1.md", "### T\n\nB.\n#\n", "no heading"),
        ("1.md", "### T\n\nB.\n<script>\n", "no html block"),
        ("1.md", "### T\n\nB.\n<STYLE type=x>\n", "no html block"),
        ("1.md", "### T\n\nB.\n  <pre\n", "no html block"),
        ("1.md", "### T\n\nB.\n<textarea>\n", "no html block"),
        ("1.md", "### T\n\nB.\n<?php\n", "no html block"),
        ("1.md", "### T\n\nB.\n<!DOCTYPE html>\n", "no html block"),
        ("1.md", "### T\n\nB.\n<![CDATA[\n", "no html block"),
    ],
)
def test_a_file_that_is_no_entry_is_refused(
    tmp_path: Path,
    name: str,
    text: str,
    reason: str,
) -> None:
    """The name and the text are an entry's, or nothing is assembled.

    :param name: the file's name.
    :param text: the file's text.
    :param reason: what the refusal says.
    """
    _tree(tmp_path, {"5.md": "### Five\n\nFive (closes #5).\n", name: text})

    with pytest.raises(script.RefusedError) as refused:
        script.assemble("2026.11.15", tmp_path)

    (problem,) = refused.value.problems
    assert problem.startswith(f"changelog/next/{name}: ")
    assert reason in problem
    assert (tmp_path / "changelog" / "next" / "5.md").is_file()
    assert (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8") == CHANGELOG


@pytest.mark.parametrize(
    "body",
    [
        "```foo``` runs inline (closes #2).",
        "#tag is a word (closes #2).",
        "Text (closes #2).\n- - - is a list",
        "<scripts> is a word (closes #2).",
        "<b>bold</b> (closes #2).",
    ],
)
def test_a_line_that_opens_nothing_is_a_body_line(tmp_path: Path, body: str) -> None:
    """No fence, heading or html block: the rules the assembly reads by.

    :param body: the entry's body.
    """
    _tree(tmp_path, {"2.md": f"### Two\n\n{body}\n"})

    script.assemble("2026.11.15", tmp_path)

    assert f"### Two\n\n{body}\n" in (tmp_path / "CHANGELOG.md").read_text(
        encoding="utf-8"
    )


def test_two_entries_with_one_title_are_refused(tmp_path: Path) -> None:
    """Each is an entry, and the release's section would repeat a heading."""
    same = "### Fix validation\n\nIt validates (closes #{}).\n"
    _tree(tmp_path, {"10.md": same.format(10), "11.md": same.format(11)})

    with pytest.raises(script.RefusedError) as refused:
        script.assemble("2026.11.15", tmp_path)

    assert refused.value.problems == [
        (
            f"changelog/next/{name}: {other} holds the title '### Fix validation'"
            " too, and a release's section repeats no heading"
        )
        for name, other in (("10.md", "11.md"), ("11.md", "10.md"))
    ]
    assert (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8") == CHANGELOG


def test_an_entry_of_three_lines_is_admitted() -> None:
    """The bound is section 9's, three lines of body."""
    assert script.entry_problems("1.md", "### T\n\none\ntwo\nthree\n") == []


def test_a_version_already_assembled_is_refused(tmp_path: Path) -> None:
    """A second run would write the release's heading twice."""
    _tree(tmp_path, ENTRIES)

    with pytest.raises(script.RefusedError) as refused:
        script.assemble("2026.11.14", tmp_path)

    assert refused.value.problems == [
        "CHANGELOG.md already holds ## v2026.11.14: a release that holds it is done"
    ]
    assert len(list((tmp_path / "changelog" / "next").glob("*.md"))) == len(ENTRIES)


# the command that takes the history files and the entries back to HEAD
RESTORE = (
    "git restore --source=HEAD --staged --worktree --"
    " CHANGELOG.md RELEASE_NOTES.md changelog/next"
)


def test_a_directory_left_by_a_killed_run_is_refused(tmp_path: Path) -> None:
    """The directories and the command that restores the commit are named."""
    _tree(tmp_path, ENTRIES)
    (tmp_path / ".changelog-assembly-abc").mkdir()
    (tmp_path / ".changelog-assembly-def").mkdir()
    before = _snapshot(tmp_path)

    with pytest.raises(script.RefusedError) as refused:
        script.assemble("2026.11.15", tmp_path)

    left, restore = refused.value.problems
    assert left.startswith(
        ".changelog-assembly-abc, .changelog-assembly-def: left by an assembly"
    )
    assert restore.endswith(
        f": {RESTORE} && rm -rf -- .changelog-assembly-abc .changelog-assembly-def"
    )
    assert _snapshot(tmp_path) == before


def test_a_file_named_as_the_directory_is_not_left_by_a_run(tmp_path: Path) -> None:
    """A file or a symlink of that name is the user's, and the run goes on."""
    _tree(tmp_path, ENTRIES)
    (tmp_path / ".changelog-assembly-notes.txt").write_text("x\n", encoding="utf-8")
    (tmp_path / ".changelog-assembly-link").symlink_to(tmp_path / "changelog")

    script.assemble("2026.11.15", tmp_path)

    assert (tmp_path / ".changelog-assembly-notes.txt").read_text() == "x\n"
    assert (tmp_path / ".changelog-assembly-link").is_symlink()


def _staged_entry(root: Path) -> None:
    """Add an entry to the index, and commit nothing."""
    (root / "changelog/next/20.md").write_text("### T\n\nB (closes #20).\n")
    subprocess.run(["git", "-C", str(root), "add", "--all"], check=True)


def _untracked_entry(root: Path) -> None:
    """Write an entry git does not know."""
    (root / "changelog/next/20.md").write_text("### T\n\nB (closes #20).\n")


def _edited_entry(root: Path) -> None:
    """Edit an entry the commit holds."""
    (root / "changelog/next/3.md").write_text("### Three\n\nEdited (closes #3).\n")


def _edited_history(root: Path) -> None:
    """Edit a history file the commit holds."""
    with (root / "RELEASE_NOTES.md").open("a", encoding="utf-8") as stream:
        stream.write("\nA line.\n")


def _ignored_entry(root: Path) -> None:
    """Write an entry an ignore rule hides from `git status` by default."""
    with (root / ".git/info/exclude").open("a", encoding="utf-8") as stream:
        stream.write("changelog/next/21.md\n")
    (root / "changelog/next/21.md").write_text("### U\n\nB (closes #21).\n")


def test_an_ignored_file_the_assembly_does_not_read_is_no_change(
    tmp_path: Path,
) -> None:
    """An editor's file under `changelog/next/` stops nothing."""
    _tree(tmp_path, ENTRIES)
    with (tmp_path / ".git/info/exclude").open("a", encoding="utf-8") as stream:
        stream.write(".DS_Store\n")
    (tmp_path / "changelog/next/.DS_Store").write_bytes(b"x")

    script.assemble("2026.11.15", tmp_path)

    assert (tmp_path / "changelog/next/.DS_Store").read_bytes() == b"x"


@pytest.mark.parametrize(
    ("change", "path"),
    [
        (_staged_entry, "changelog/next/20.md"),
        (_untracked_entry, "changelog/next/20.md"),
        (_edited_entry, "changelog/next/3.md"),
        (_edited_history, "RELEASE_NOTES.md"),
        (_ignored_entry, "changelog/next/21.md"),
    ],
    ids=["staged", "untracked", "edited-entry", "edited-history", "ignored"],
)
@pytest.mark.parametrize("killed", [False, True])
def test_what_the_commit_does_not_hold_is_refused_before_anything_changes(
    tmp_path: Path,
    change: Callable[[Path], None],
    path: str,
    killed: bool,  # noqa: FBT001
) -> None:
    """Going back to the commit would lose it, so the run does not start.

    :param change: what makes the tree differ from its commit.
    :param path: the path it changes.
    :param killed: whether the run is one that would be killed at its
        first change.
    """
    root = tmp_path / "root"
    root.mkdir()
    _tree(root, ENTRIES)
    change(root)
    before = _snapshot(root)

    if killed:
        (harness := tmp_path / "killed.py").write_text(KILLED, encoding="utf-8")
        ran = subprocess.run(
            [sys.executable, "-I", str(harness), str(_SCRIPT), "0", str(_STATUS)],
            cwd=root,
            capture_output=True,
            encoding="utf-8",
            check=False,
        )
        assert ran.returncode == 1, ran.stderr
        problems = ran.stderr.splitlines()
    else:
        with pytest.raises(script.RefusedError) as refused:
            script.assemble("2026.11.15", root)
        problems = refused.value.problems

    assert problems == [
        f"{path}: commit them first, so that git can undo a run that does not finish"
    ]
    assert _snapshot(root) == before
    assert not list(root.glob(".changelog-assembly-*"))


def test_a_tree_that_is_no_git_checkout_is_refused(tmp_path: Path) -> None:
    """No commit holds the files, so nothing could undo a killed run."""
    _tree(tmp_path, ENTRIES, commit=False)
    before = _snapshot(tmp_path)

    with pytest.raises(script.RefusedError) as refused:
        script.assemble("2026.11.15", tmp_path)

    (problem,) = refused.value.problems
    assert problem.endswith(
        "is not a git checkout, or git is missing: the assembly runs on a"
        " commit, so that git can undo a run that does not finish"
    )
    assert _snapshot(tmp_path) == before


def test_without_git_nothing_is_assembled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A git the path does not hold refuses as a tree with no commit does."""
    _tree(tmp_path, ENTRIES)
    monkeypatch.setenv("PATH", str(tmp_path / "nowhere"))

    with pytest.raises(script.RefusedError) as refused:
        script.assemble("2026.11.15", tmp_path)

    (problem,) = refused.value.problems
    assert "is not a git checkout, or git is missing" in problem


def test_a_version_that_is_not_digits_and_dots_and_a_missing_file_are_refused(
    tmp_path: Path,
) -> None:
    """Section 12's version, and the history files, or nothing is written."""
    _tree(tmp_path, ENTRIES)
    (tmp_path / "RELEASE_NOTES.md").unlink()
    _commit_at(tmp_path)

    with pytest.raises(script.RefusedError) as refused:
        script.assemble("2026.11.15rc1", tmp_path)

    assert refused.value.problems == [
        "'2026.11.15rc1' is not a version: digits and dots",
        "RELEASE_NOTES.md is missing",
    ]


def test_entries_whose_section_check_changelog_refuses_are_refused(
    tmp_path: Path,
) -> None:
    """`check_changelog.py` judges the section: two closes of one issue."""
    _tree(
        tmp_path,
        {
            "4.md": "### Four\n\nIt (closes #9).\n",
            "5.md": "### Five\n\nIt (closes #9).\n",
        },
    )

    with pytest.raises(script.RefusedError) as refused:
        script.assemble("2026.11.15", tmp_path)

    (problem,) = refused.value.problems
    assert problem.startswith("the section the entries make, line ")
    assert "closes #9, already closed by heading 'Four'" in problem


def test_without_check_changelog_beside_it_nothing_is_assembled(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The checks that judge a section are not skipped without the script."""
    _tree(tmp_path, ENTRIES)
    monkeypatch.setattr(script, "CHECKER", tmp_path / "check_changelog.py")

    with pytest.raises(script.RefusedError) as refused:
        script.assemble("2026.11.15", tmp_path)

    assert refused.value.problems[0].endswith(
        "check_changelog.py is missing: it judges the section, beside this script"
    )


FENCED = """\
# Changelog

````markdown
```
## v99
```
````

~~~
## v98
~~~

<!--
## v97
-->

## v2026.11.14

### An older entry

Its body (closes #1).
"""


def test_a_heading_in_a_fence_or_a_comment_is_not_the_last_release(
    tmp_path: Path,
) -> None:
    """A longer fence holds shorter ones; tilde fences and comments count."""
    _tree(tmp_path, {"3.md": ENTRIES["3.md"]})
    for name in script.FILES:
        (tmp_path / name).write_text(FENCED, encoding="utf-8")
    _commit_at(tmp_path)

    script.assemble("2026.11.15", tmp_path)

    above, _, below = FENCED.partition("## v2026.11.14\n")
    section = "## v2026.11.15\n\n" + ENTRIES["3.md"]
    for name in script.FILES:
        text = (tmp_path / name).read_text(encoding="utf-8")
        assert text == above + section + "\n## v2026.11.14\n" + below
        assert release_check.problems("2026.11.15", text, FENCED) == []


@pytest.mark.parametrize("name", ["CHANGELOG.md", "RELEASE_NOTES.md"])
def test_a_work_in_progress_heading_is_refused(tmp_path: Path, name: str) -> None:
    """The assembly folds no such section, and the release's gates refuse it.

    :param name: the history file holding the heading.
    """
    _tree(tmp_path, {"3.md": ENTRIES["3.md"]})
    path = tmp_path / name
    wip = "## v2026.12 (work in progress, not released yet)\n\n### It\n\nIt.\n\n"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("## v2026.11.14", f"{wip}## v2026.11.14", 1))
    _commit_at(tmp_path)
    before = _snapshot(tmp_path)

    with pytest.raises(script.RefusedError) as refused:
        script.assemble("2026.11.15", tmp_path)

    assert refused.value.problems == [
        (
            f"{name} holds a (work in progress, not released yet) heading, which"
            " a release does not fold: remove the heading, move what its section"
            " holds into changelog/next/ as entries, and commit both before the"
            " run"
        )
    ]
    assert _snapshot(tmp_path) == before


def test_a_work_in_progress_heading_in_a_fence_is_an_example(tmp_path: Path) -> None:
    """Only a heading outside code is one."""
    _tree(tmp_path, {"3.md": ENTRIES["3.md"]})
    path = tmp_path / "CHANGELOG.md"
    example = "```\n## v1 (work in progress, not released yet)\n```\n\n"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("## v2026.11.14", f"{example}## v2026.11.14", 1))
    _commit_at(tmp_path)

    script.assemble("2026.11.15", tmp_path)


@pytest.mark.parametrize(
    "opened",
    ["```text\n## v1\n", "````\n```\n## v1\n", "~~~\n## v1\n```\n", "<!--\n## v1\n"],
)
def test_a_file_ending_inside_a_fence_is_refused(tmp_path: Path, opened: str) -> None:
    """The section would land inside the example, and nothing is written.

    :param opened: what the file opens and never closes.
    """
    _tree(tmp_path, {"3.md": ENTRIES["3.md"]})
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n" + opened, encoding="utf-8")
    _commit_at(tmp_path)

    with pytest.raises(script.RefusedError) as refused:
        script.assemble("2026.11.15", tmp_path)

    assert refused.value.problems == [
        "CHANGELOG.md ends inside a code fence or an html comment",
    ]
    assert (tmp_path / "changelog" / "next" / "3.md").is_file()


def test_a_backtick_run_with_a_backtick_after_it_opens_no_fence() -> None:
    """A fence's info string holds no backtick, so the line is inline code."""
    text = "# Changelog\n\n```a``` b\n\n## v1\n"
    assert script.headings(text) == [(text.index("## v1"), "## v1")]


def test_a_symlink_is_no_entry(tmp_path: Path) -> None:
    """Assembly reads regular files alone, and writes nothing otherwise."""
    directory = _tree(tmp_path, {"3.md": ENTRIES["3.md"]})
    (directory / "4.md").symlink_to(directory / "3.md")
    _commit_at(tmp_path)

    with pytest.raises(script.RefusedError) as refused:
        script.assemble("2026.11.15", tmp_path)

    assert refused.value.problems == ["changelog/next/4.md: an entry is a regular file"]
    assert (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8") == CHANGELOG


def _snapshot(root: Path) -> dict[str, tuple[bytes, int]]:
    """Read every file under `root` but `.git`, hidden ones too, with modes."""
    return {
        path.relative_to(root).as_posix(): (
            path.read_bytes(),
            path.stat().st_mode & 0o777,
        )
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".git" not in path.relative_to(root).parts[:1]
    }


# a mode no file is written with, which an assembly keeps
_KEPT = 0o640


def _modes_tree(root: Path) -> None:
    """Write the entries and the history files, with modes a rewrite would lose.

    :param root: the tree's root.
    """
    root.mkdir()
    directory = _tree(root, ENTRIES, commit=False)
    (directory / "12.md").chmod(0o755)
    (root / "CHANGELOG.md").chmod(_KEPT)
    _commit_at(root)


def _once(original: Any, fails: Any) -> Any:  # noqa: ANN401 - wraps any callable
    """Wrap a callable so that its first call `fails` matches raises.

    :param original: the callable.
    :param fails: what says, from the call's arguments, it is the one.
    :returns: the wrapper.
    """
    state = {"failed": False}

    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        if not state["failed"] and fails(*args, **kwargs):
            state["failed"] = True
            msg = "injected failure"
            raise OSError(msg)
        return original(*args, **kwargs)

    return wrapper


def _fail(step: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Make one step of the assembly fail once.

    :param step: `stage`, `write`, `link`, `rename` or `remove`.
    """
    match step:
        case "stage":
            monkeypatch.setattr(
                script.tempfile,
                "mkdtemp",
                _once(script.tempfile.mkdtemp, lambda **kw: kw["dir"].name == "root"),
            )
        case "write":
            monkeypatch.setattr(
                Path,
                "write_bytes",
                _once(Path.write_bytes, lambda path, _: path.name == "new-1"),
            )
        case "link":
            monkeypatch.setattr(
                Path,
                "hardlink_to",
                _once(Path.hardlink_to, lambda _, target: target.name == "3.md"),
            )
        case "rename":
            monkeypatch.setattr(
                Path,
                "replace",
                _once(
                    Path.replace, lambda _, target: target.name == "RELEASE_NOTES.md"
                ),
            )
        case _:
            monkeypatch.setattr(
                Path,
                "unlink",
                _once(Path.unlink, lambda path, *_, **__: path.name == "3.md"),
            )


def _assembled(tmp_path: Path) -> dict[str, tuple[bytes, int]]:
    """Assemble a tree no failure touches.

    :param tmp_path: a directory of this test's own.
    :returns: the tree's files after the assembly.
    """
    expected = tmp_path / "expected"
    _modes_tree(expected)
    script.assemble("2026.11.15", expected)
    assert (expected / "CHANGELOG.md").stat().st_mode & 0o777 == _KEPT
    return _snapshot(expected)


@pytest.mark.parametrize("step", ["stage", "write", "link", "rename", "remove"])
def test_a_failing_step_leaves_the_tree_as_it_was(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    step: str,
) -> None:
    """Every step undone, each mode kept, nothing left over, a retry completes.

    :param step: the step that fails.
    """
    root = tmp_path / "root"
    _modes_tree(root)
    before = _snapshot(root)

    with monkeypatch.context() as patched:
        _fail(step, patched)
        with pytest.raises(OSError, match="injected failure"):
            script.assemble("2026.11.15", root)

    assert _snapshot(root) == before
    assert not list(root.glob(".changelog-assembly-*"))
    script.assemble("2026.11.15", root)
    assert _snapshot(root) == _assembled(tmp_path)


# the changes an assembly of `ENTRIES` makes: each history file, then each entry
_CHANGES = len(script.FILES) + len(ENTRIES)


@pytest.mark.parametrize("fails_at", range(1, _CHANGES))
def test_a_full_disk_after_the_first_change_leaves_the_tree_as_it_was(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fails_at: int,
) -> None:
    """Once a file has changed, nothing can be written, and the tree comes back.

    Every way to allocate fails from the first change on, and the change
    numbered `fails_at`, counted from 0, fails as a full disk does.

    :param fails_at: the change that fails.
    """
    root = tmp_path / "root"
    _modes_tree(root)
    before = _snapshot(root)
    state = {"changes": 0}

    def full() -> OSError:
        return OSError(errno.ENOSPC, "No space left on device")

    def allocating(original: Any) -> Any:  # noqa: ANN401 - wraps any callable
        def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            if state["changes"]:
                raise full()
            return original(*args, **kwargs)

        return wrapper

    def changing(original: Any, counts: Any) -> Any:  # noqa: ANN401
        def wrapper(path: Path, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
            if counts(path):
                if state["changes"] == fails_at:
                    raise full()
                state["changes"] += 1
            return original(path, *args, **kwargs)

        return wrapper

    with monkeypatch.context() as patched:
        for owner, name in [
            (script.tempfile, "mkdtemp"),
            (script.tempfile, "mkstemp"),
            (os, "link"),
            (os, "mkdir"),
            (Path, "write_bytes"),
            (Path, "write_text"),
            (Path, "hardlink_to"),
            (Path, "touch"),
            (Path, "mkdir"),
            (Path, "open"),
        ]:
            patched.setattr(owner, name, allocating(getattr(owner, name)))
        patched.setattr("builtins.open", allocating(open))
        patched.setattr(
            Path, "replace", changing(Path.replace, lambda p: p.name.startswith("new-"))
        )
        patched.setattr(
            Path, "unlink", changing(Path.unlink, lambda p: p.parent.name == "next")
        )
        with pytest.raises(OSError, match="No space left on device"):
            script.assemble("2026.11.15", root)

    assert state["changes"] == fails_at
    assert _snapshot(root) == before
    assert not list(root.glob(".changelog-assembly-*"))
    script.assemble("2026.11.15", root)
    assert _snapshot(root) == _assembled(tmp_path)


# a run killed before the change numbered `kill_at`, counted from 0, with
# the status `status`: -1 kills it while it stages, and the number of the
# changes once they are all made, before it removes its directory
KILLED = """\
import importlib.util, os, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("entries", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
kill_at, status, done = int(sys.argv[2]), int(sys.argv[3]), [0]


def killing(original, counts):
    def wrapper(path, *args, **kwargs):
        if counts(path):
            if done[0] == kill_at:
                os._exit(status)
            done[0] += 1
        return original(path, *args, **kwargs)

    return wrapper


def staging(*args, **kwargs):
    os._exit(status)


def removing(*args, **kwargs):
    if done[0] == kill_at:
        os._exit(status)
    return rmtree(*args, **kwargs)


if kill_at < 0:
    Path.hardlink_to = staging
Path.replace = killing(Path.replace, lambda path: path.name.startswith("new-"))
Path.unlink = killing(Path.unlink, lambda path: path.parent.name == "next")
rmtree, module.shutil.rmtree = module.shutil.rmtree, removing
sys.exit(module.main(["assemble", "2026.11.15"]))
"""
_STATUS = 9


@pytest.mark.parametrize("shell", ["bash", "zsh"])
@pytest.mark.parametrize("kill_at", range(-1, _CHANGES + 1))
def test_the_recovery_a_killed_run_prints_brings_the_commit_back(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    shell: str,
    kill_at: int,
) -> None:
    """Killed at each step, the next run refuses; its command, run, restores.

    :param shell: the shell the printed command is run in.
    :param kill_at: the change before which the run is killed.
    """
    if shutil.which(shell) is None:
        pytest.skip(f"{shell} is not installed")
    root = tmp_path / "root"
    root.mkdir()
    monkeypatch.chdir(root)
    _tree(root, ENTRIES)
    before = _snapshot(root)
    (harness := tmp_path / "killed.py").write_text(KILLED, encoding="utf-8")

    killed = subprocess.run(
        [sys.executable, "-I", str(harness), str(_SCRIPT), str(kill_at), str(_STATUS)],
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    assert killed.returncode == _STATUS, killed.stderr
    assert list(root.glob(".changelog-assembly-*"))

    assert script.main(["assemble", "2026.11.15"]) == 1
    printed = capsys.readouterr().err
    (command,) = [
        line.split("from the tree's root: ", 1)[1]
        for line in printed.splitlines()
        if "from the tree's root: " in line
    ]
    assert command.startswith(f"{RESTORE} && rm -rf -- .changelog-assembly-")
    subprocess.run([shell, "-c", command], check=True)

    assert _snapshot(root) == before
    assert _git("status", "--porcelain") == ""
    assert script.main(["assemble", "2026.11.15"]) == 0
    expected = tmp_path / "expected"
    expected.mkdir()
    _tree(expected, ENTRIES)
    script.assemble("2026.11.15", expected)
    assert _snapshot(root) == _snapshot(expected)


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Make a publishing tree with one base commit the working directory.

    :returns: the tree's root.
    """
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    monkeypatch.chdir(tmp_path)
    _git("init", "--quiet", "--initial-branch=main")
    _write(".github/workflows/release.yml", "name: release\n")
    _write("src/pkg/__init__.py", '"""A package."""\n')
    _write("docs/index.md", "# Docs\n")
    _write(
        "pyproject.toml",
        '[project]\nname = "pkg"\nversion = "2026.12"\ndependencies = []\n'
        "\n[tool.ruff]\n",
    )
    _commit()
    return tmp_path


def _git(*args: str) -> str:
    """Run git in the working directory as the committer `Ann`."""
    ran = subprocess.run(
        ["git", "-c", "user.name=Ann", "-c", "user.email=ann@example.org", *args],
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    return ran.stdout


def _write(path: str, text: str) -> None:
    """Write a file of the working tree, its directories made."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text, encoding="utf-8")


def _commit() -> None:
    """Commit everything in the working tree."""
    _git("add", "--all")
    _git("commit", "--quiet", "--allow-empty", "-m", "commit")


ENTRY = "### Pkg does a thing\n\nIt does it (closes #4).\n"


def _refusal(problems: list[str]) -> str:
    """Return the one refusal of a missing entry, or fail."""
    (problem,) = problems
    assert problem.endswith(
        ": the diff changes what a user gets, and no file under changelog/next/"
        " holds its entry: add changelog/next/<n>.md (section 9 of"
        " btclib-org/.github's README.md), or label the pull request"
        " no-user-change where it changes nothing a user gets",
    )
    return problem


@pytest.mark.usefixtures("repo")
def test_a_change_to_the_package_without_an_entry_is_refused() -> None:
    """A path under `src/` is the package."""
    _write("src/pkg/__init__.py", '"""A package that does more."""\n')
    _commit()

    assert _refusal(script.check("HEAD^1", "HEAD", [])).startswith(
        "src/pkg/__init__.py: "
    )


@pytest.mark.usefixtures("repo")
def test_the_label_exempts_a_change_to_the_package() -> None:
    """The reviewer's word that the change reaches no user."""
    _write("src/pkg/__init__.py", '"""A package, reworded."""\n')
    _commit()

    assert script.check("HEAD^1", "HEAD", ["api-break", "no-user-change"]) == []
    assert script.LABEL == "no-user-change"


@pytest.mark.usefixtures("repo")
@pytest.mark.parametrize("path", ["changelog/next/4.md", "changelog/next/github-9.md"])
def test_an_entry_added_or_edited_passes(path: str) -> None:
    """The second pull request for an issue edits the file that is there.

    :param path: the entry's path.
    """
    _write("src/pkg/__init__.py", '"""A package that does more."""\n')
    _write(path, ENTRY)
    _commit()
    assert script.check("HEAD^1", "HEAD", []) == []

    _write("src/pkg/__init__.py", '"""A package that does more still."""\n')
    _write(path, ENTRY.replace("does it", "does it twice"))
    _commit()
    assert script.check("HEAD^1", "HEAD", []) == []


@pytest.mark.usefixtures("repo")
def test_an_entry_whose_mode_alone_changed_is_not_written() -> None:
    """Its text is the base's, so it says nothing of the package's change."""
    _write("changelog/next/4.md", ENTRY)
    _commit()
    Path("changelog/next/4.md").chmod(0o755)
    _write("src/pkg/__init__.py", '"""A package that does more."""\n')
    _commit()

    assert _refusal(script.check("HEAD^1", "HEAD", [])).startswith(
        "src/pkg/__init__.py: "
    )


@pytest.mark.usefixtures("repo")
def test_an_entry_that_is_no_entry_is_refused_whatever_the_diff() -> None:
    """The text is read on every pull request that writes one."""
    _write("docs/index.md", "# Docs, reworded\n")
    _write("changelog/next/4.md", "- **Pkg** does a thing (closes #4).\n")
    _commit()

    assert script.check("HEAD^1", "HEAD", []) == [
        "changelog/next/4.md: an entry opens with a `### ` title",
    ]


@pytest.mark.usefixtures("repo")
def test_an_entry_whose_title_another_holds_is_refused() -> None:
    """The entry already on the base is compared, and not reported."""
    _write("changelog/next/4.md", ENTRY)
    _commit()
    _write("changelog/next/5.md", ENTRY.replace("#4", "#5"))
    _commit()

    assert script.check("HEAD^1", "HEAD", []) == [
        (
            "changelog/next/5.md: 4.md holds the title '### Pkg does a thing'"
            " too, and a release's section repeats no heading"
        ),
    ]


@pytest.mark.usefixtures("repo")
def test_a_symlink_entry_is_refused_however_it_arrives() -> None:
    """An entry added as a link, or a regular one turned into a link."""
    _write("src/pkg/__init__.py", '"""A package that does more."""\n')
    _write("changelog/next/4.md", ENTRY)
    _commit()
    Path("changelog/next/4.md").unlink()
    Path("changelog/next/4.md").symlink_to("../../docs/index.md")
    _commit()
    assert script.check("HEAD^1", "HEAD", []) == [
        (
            "changelog/next/4.md: an entry is a regular file, and this one's mode"
            " is 120000"
        ),
    ]

    Path("changelog/next/5.md").symlink_to("4.md")
    _write("src/pkg/__init__.py", '"""A package that does more still."""\n')
    _commit()
    problems = script.check("HEAD^1", "HEAD", [])
    assert problems[0] == (
        "changelog/next/5.md: an entry is a regular file, and this one's mode is 120000"
    )
    assert _refusal(problems[1:]).startswith("src/pkg/__init__.py: ")


@pytest.mark.usefixtures("repo")
def test_an_entry_closing_what_another_closes_is_refused() -> None:
    """The section the head's entries make is judged by `check_changelog.py`."""
    _write("changelog/next/4.md", ENTRY)
    _commit()
    _write("changelog/next/5.md", ENTRY.replace("thing", "second thing"))
    _commit()

    (problem,) = script.check("HEAD^1", "HEAD", [])
    assert problem.startswith("the section the entries make, line ")
    assert "closes #4, already closed by heading 'Pkg does a thing'" in problem


@pytest.mark.usefixtures("repo")
def test_a_change_outside_the_package_asks_for_nothing() -> None:
    """Documents, tests and `[tool]` tables are not what a user installs."""
    _write("docs/index.md", "# Docs, reworded\n")
    _write("tests/pkg_test.py", '"""A test."""\n')
    _write(
        "pyproject.toml",
        '[project]\nname = "pkg"\nversion = "2026.12"\ndependencies = []\n'
        "\n[tool.ruff]\nline-length = 88\n",
    )
    _commit()

    assert script.check("HEAD^1", "HEAD", []) == []


@pytest.mark.usefixtures("repo")
def test_the_version_is_the_release_s_and_asks_for_nothing() -> None:
    """A release's pull request sets the version and removes the entries."""
    _write("changelog/next/4.md", ENTRY)
    _commit()
    _write(
        "pyproject.toml",
        Path("pyproject.toml")
        .read_text(encoding="utf-8")
        .replace("2026.12", "2026.12.1"),
    )
    Path("changelog/next/4.md").unlink()
    _commit()

    assert script.check("HEAD^1", "HEAD", []) == []


@pytest.mark.usefixtures("repo")
def test_a_change_to_the_project_table_is_the_package() -> None:
    """A dependency's floor changes what a user installs."""
    _write(
        "pyproject.toml",
        Path("pyproject.toml")
        .read_text(encoding="utf-8")
        .replace("[]", '["base58-bech32>=2026.11.12"]'),
    )
    _commit()

    assert _refusal(script.check("HEAD^1", "HEAD", [])).startswith("pyproject.toml: ")


@pytest.mark.usefixtures("repo")
def test_a_gitlink_is_the_package() -> None:
    """A submodule's pin moves the vendored code a wheel builds."""
    sha = _git("rev-parse", "HEAD").strip()
    _git("update-index", "--add", "--cacheinfo", f"160000,{sha},vendored")
    _git("commit", "--quiet", "-m", "vendor")

    assert _refusal(script.check("HEAD^1", "HEAD", [])).startswith("vendored: ")


@pytest.mark.usefixtures("repo")
def test_a_refusal_names_three_paths_at_most() -> None:
    """The rest of a long diff is the pull request's own listing."""
    for index in range(5):
        _write(f"src/pkg/m{index}.py", '"""A module."""\n')
    _commit()

    assert _refusal(script.check("HEAD^1", "HEAD", [])).startswith(
        "src/pkg/m0.py, src/pkg/m1.py, src/pkg/m2.py, ...: "
    )


@pytest.mark.usefixtures("repo")
def test_a_tree_that_does_not_publish_writes_no_entry() -> None:
    """Nothing would assemble it, and the package asks for none there."""
    Path(".github/workflows/release.yml").unlink()
    _commit()
    _write("src/pkg/__init__.py", '"""A package that does more."""\n')
    _commit()
    assert script.check("HEAD^1", "HEAD", []) == []

    _write("changelog/next/4.md", ENTRY)
    _commit()
    assert script.check("HEAD^1", "HEAD", []) == [
        (
            "changelog/next/4.md: this tree does not publish, so it writes no"
            " entry (section 9)"
        ),
    ]


@pytest.mark.usefixtures("repo")
def test_a_diff_git_cannot_read_is_refused() -> None:
    """A base the checkout lacks is a refusal, never a pass."""
    with pytest.raises(script.RefusedError) as refused:
        script.check("no-such-commit", "HEAD", [])

    assert refused.value.problems[0].startswith(
        "git cannot read the diff no-such-commit..HEAD: "
    )


def _by_path(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the script as the workflow does, as a program."""
    return subprocess.run(
        [sys.executable, str(_SCRIPT), *args],
        capture_output=True,
        check=False,
        encoding="utf-8",
    )


@pytest.mark.usefixtures("repo")
def test_run_as_a_program_check_reads_the_labels_as_json() -> None:
    """`toJSON()` of the event's label names is what the step passes."""
    _write("src/pkg/__init__.py", '"""A package that does more."""\n')
    _commit()

    refused = _by_path("check", "HEAD^1", "HEAD", "--labels", '["api-break"]')
    passed = _by_path("check", "HEAD^1", "HEAD", "--labels", json.dumps([script.LABEL]))

    assert refused.returncode == 1
    assert "no-user-change" in refused.stderr
    assert passed.returncode == 0
    assert passed.stdout == "HEAD^1..HEAD: the changelog entry is in order\n"


@pytest.mark.usefixtures("repo")
@pytest.mark.parametrize(
    "labels", ['{"no-user-change": false}', "null", '["no-user-change", 1]', "not json"]
)
def test_labels_that_are_not_a_list_of_strings_are_refused(labels: str) -> None:
    """A mapping's keys exempt nothing, and nothing ends in a traceback.

    :param labels: the option's value.
    """
    _write("src/pkg/__init__.py", '"""A package that does more."""\n')
    _commit()

    ran = _by_path("check", "HEAD^1", "HEAD", "--labels", labels)

    assert ran.returncode == 1
    assert ran.stderr == f"--labels takes a JSON list of strings, not {labels!r}\n"


def test_run_as_a_program_assemble_prints_what_it_removed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The tree is the working directory, and a refusal exits 1."""
    _tree(tmp_path, {"3.md": ENTRIES["3.md"]})
    monkeypatch.chdir(tmp_path)

    ran = _by_path("assemble", "2026.11.15")
    _commit_at(tmp_path)
    again = _by_path("assemble", "2026.11.16")

    assert ran.returncode == 0
    assert ran.stdout == "assembled and removed changelog/next/3.md\n"
    assert again.returncode == 1
    assert again.stderr.startswith("changelog/next holds no entry")


def test_this_tree_holds_no_entry() -> None:
    """This tree publishes nothing, so `check` would refuse any entry here."""
    assert not (ROOT / ".github" / "workflows" / "release.yml").exists()
    assert not (ROOT / "changelog").exists()


def _parsed() -> dict[Any, Any]:
    """Read the workflow, whose `on` key YAML may read as True."""
    parsed: dict[Any, Any] = yaml.safe_load(_WORKFLOW.read_text(encoding="utf-8"))
    return parsed


def _job() -> dict[str, Any]:
    """Read the workflow's one job."""
    (job,) = _parsed()["jobs"].values()
    return dict(job)


def _step(name: str) -> dict[str, Any]:
    """Return the step of that name."""
    steps: list[dict[str, Any]] = _job()["steps"]
    return next(step for step in steps if step.get("name") == name)


def test_the_workflow_declares_no_trigger_but_the_call_and_writes_nothing() -> None:
    """The caller holds the trigger; the token reads."""
    parsed = _parsed()
    on: dict[str, Any] = parsed.get("on", parsed.get(True)) or {}
    assert list(on) == ["workflow_call"]
    assert parsed["permissions"] == {"contents": "read"}
    assert _job()["permissions"] == {"contents": "read"}


def test_the_job_reads_an_open_pull_request_alone() -> None:
    """Only a pull request's merge commit has the diff the check reads."""
    assert " ".join(_job()["if"].split()) == (
        "${{ github.event_name == 'pull_request' && "
        "github.event.action != 'closed' && "
        "!github.event.pull_request.draft }}"
    )
    assert _job()["name"] == "Changelog entry"


def test_the_step_reads_the_merge_against_its_first_parent_with_the_labels() -> None:
    """Depth 2 holds the first parent, and the labels are the event's."""
    assert _step("Checkout code")["with"]["fetch-depth"] == DEPTH
    checkout = _step("Check out the script")
    assert checkout["with"]["path"] == "standard"
    assert checkout["with"]["sparse-checkout"] == ".github/scripts"
    step = _step("Check that a change for the user carries its entry")
    assert step["env"] == {
        "LABELS": "${{ toJSON(github.event.pull_request.labels.*.name) }}",
    }
    assert " ".join(step["run"].replace("\\\n", " ").split()) == (
        "uv run --no-project --python 3.15"
        f" standard/{_SCRIPT.relative_to(ROOT).as_posix()}"
        ' check HEAD^1 HEAD --labels "$LABELS"'
    )


def test_the_label_is_owed_where_api_break_is() -> None:
    """The publishing trees, the only ones a release assembles in."""
    labels = yaml.safe_load(_LABELS.read_text(encoding="utf-8"))["labels"]
    by_name = {entry["name"]: entry for entry in labels}
    assert by_name[script.LABEL]["repositories"] == by_name["api-break"]["repositories"]
