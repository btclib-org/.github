# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Assemble a release's changelog entries, and ask a pull request for one.

Section 9 of README.md: a pull request that changes what a user gets
adds its entry as a file of its own under `changelog/next/`, and a
release assembles those files into `CHANGELOG.md` and `RELEASE_NOTES.md`.
Pull requests citing different issues write different files, so neither
conflicts with the other, and the entry is reviewed with the change it
describes.

A file is named `<n>.md`, `<n>` being the number of the issue it cites,
or of the pull request where it cites none: GitHub numbers both in one
sequence. An issue of another btclib-org repository gives
`<repo>-<n>.md`, the repository's name without a leading dot, so
btclib-org/.github#2287 gives `github-2287.md`. A second pull request for
the same issue edits the file that is there. The file is a regular file
holding the entry as it lands: a `### ` title, a blank line, and at most
three lines of body, with no heading, no code fence and no html block
among them. A heading is a `#` run of one to six followed by a space or
the line's end, after any indent or block-quote marker, or a line of
`=` or of `-` alone, which is a setext underline after a text line and a
thematic break otherwise: either is refused. An html block is one a
blank line does not end, which could run on into the next entry: a
comment, `<script`, `<pre`, `<style`, `<textarea`, a processing
instruction (`<?`), a declaration (`<!` and a letter) and CDATA.

The entries together are the release's section, and `check_changelog.py`
beside this script is what judges a section: this script loads it from
its own directory and runs its checks on the section the entries make,
so a section it assembles is one that check passes. This script finds a
history file's fences by a rule of its own: a line opening a fence is
one of three or more backticks or tildes after any indent or block-quote
marker, a backtick fence's info string holds no backtick, a fence closes
on a line of its own marker at least as long with nothing but spaces
after it, and an unclosed fence runs to the end of the file, where
`assemble` refuses it. An html comment block is read like a fence.

`assemble <version>` writes `## v<version>` and every entry, in the
order `order()` gives, above the first `## ` heading outside a fence of
each history file, and removes the entries. The output depends on the entries
alone, so the same files give the same bytes, and a reviewer of the
release runs the command on the base and compares. It refuses a
directory holding no `.md` file, which is the exact form of "nothing
changed for a user"; an `.md` file that is not an entry; and entries
whose section `check_changelog.py` refuses. It refuses where a history
file already holds the version's heading, or a `## ` heading marked
`(work in progress, not released yet)`, which it does not fold. Before
it changes anything it writes each file's new text into a directory of
its own at the tree's root, and gives each history file and each entry
a second name there, a hard link, which takes no new data. Then it
renames the new texts over the history files and removes the entries,
which takes no space either; where a step fails it renames the second
names back, so a failure, a full disk included, leaves the tree as it
was, each file with its mode.
It removes no other file: `changelog/next/.markdownlint.jsonc` stays.
It runs on a commit: it refuses a tree that is not a git checkout, and
one where `git status` shows a history file or anything under
`changelog/next/` changed, staged or untracked, or an entry or a history
file ignored, so that the commit holds every byte a run can change. A
run killed before it finishes leaves its directory, and maybe a history
file or an entry changed: it does not resume. The next run refuses
while the directory is there, and prints the `git restore` that takes
the history files and the entries back to the commit, which loses
nothing the run did not write.

`check <base> <head>` reads the diff between two commits, as
`reusable-changelog-entry.yml` runs it on a pull request's merge commit.
In a tree that publishes, which holds `.github/workflows/release.yml`
(section 2), it refuses an entry added or edited that is not one, or
whose section with the other entries the head holds is refused, and a
diff that changes the package and adds or edits no entry, unless
`--labels` holds `LABEL`. The package is what a user installs: a path
under `src/`, a gitlink, which pins vendored code a wheel builds, and the
`[project]` table of `pyproject.toml` but its `version`, which a
release's own pull request sets. In a tree that does not publish, it
refuses any entry added or edited: nothing would ever assemble it. An
entry is edited where its text changes: one whose mode alone changes
says nothing new, and is no entry for the diff.

    uv run --no-project --python 3.15 changelog_entries.py assemble 2026.11.15
    uv run --no-project --python 3.15 changelog_entries.py check \
        HEAD^1 HEAD --labels "$LABELS"

`--labels` is a JSON list of strings, as `toJSON()` writes one, and
anything else is refused.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

# the label saying a pull request changes nothing a user gets
LABEL = "no-user-change"
# where the entries wait for the release, from the tree's root
NEXT = PurePosixPath("changelog/next")
# the files a release's section is assembled into
FILES = ("CHANGELOG.md", "RELEASE_NOTES.md")
# the file whose presence says a tree publishes (section 2)
RELEASE = ".github/workflows/release.yml"
# the script whose checks judge a section, beside this one
CHECKER = Path(__file__).with_name("check_changelog.py")

_NAME = re.compile(r"(?:(?P<repo>[a-z0-9][a-z0-9.-]*)-)?(?P<number>[1-9][0-9]*)\.md")
_TITLE = re.compile(r"### \S(?:.*\S)?")
_VERSION = re.compile(r"[0-9]+(?:\.[0-9]+)*")
# a line opening or closing a fence: an indent or block-quote marker, the
# marker, and what follows it
_FENCE = re.compile(r"[ \t>]*(`{3,}|~{3,})(.*)")
# the first line of an html comment that is a block of its own
_COMMENT = re.compile(r" {0,3}<!--")
# a line opening an html block that a blank line does not end: a comment,
# `<script`, `<pre`, `<style`, `<textarea`, a processing instruction, a
# declaration, CDATA
_HTML = re.compile(
    r" {0,3}(?:<(?:script|pre|style|textarea)(?:[ \t>]|$)"
    r"|<\?|<![A-Za-z]|<!\[CDATA\[|<!--)",
    re.IGNORECASE,
)
# an ATX heading, after any indent or block-quote marker
_ATX = re.compile(r"[ \t>]*#{1,6}(?:[ \t]|$)")
# a setext underline, or a thematic break where no text line is above it
_UNDERLINE = re.compile(r" {0,3}(?:=+|-+)[ \t]*")
_MAX_BODY_LINES = 3
# the words of a work-in-progress heading, which `check_release_sections.py`
# refuses in a release
_WORK_IN_PROGRESS = "(work in progress, not released yet)"
# the name an assembly's own directory opens with, at the tree's root
_STAGING = ".changelog-assembly-"
_GITLINK = "160000"
# the modes git gives a regular file
_REGULAR = frozenset({"100644", "100755"})
# how many of the package's paths a refusal names
_SHOWN = 3


class RefusedError(Exception):
    """What the command refuses, one message per reason."""

    def __init__(self, problems: list[str]) -> None:
        """Keep the reasons.

        :param problems: one message per reason.
        """
        super().__init__("\n".join(problems))
        self.problems = problems


def order(name: str) -> tuple[str, int]:
    """Return where an entry stands in the release's section.

    This tree's own numbers come first, in their order, then each other
    repository's, by its name and then by number.

    :param name: the file's name, which `name_problem()` admits.
    :returns: the key to sort by.
    """
    found = _NAME.fullmatch(name)
    if found is None:
        msg = f"{name} is not the name of an entry"
        raise ValueError(msg)
    return found["repo"] or "", int(found["number"])


def name_problem(name: str) -> str | None:
    """Say why a file name is not an entry's.

    :param name: the file's name, without its directory.
    :returns: the reason, or None where the name is an entry's.
    """
    if _NAME.fullmatch(name):
        return None
    return (
        f"{NEXT / name}: an entry is named <n>.md or <repo>-<n>.md, <n> being"
        " the issue it cites"
    )


def body_problem(body: list[str]) -> str | None:
    """Say why the lines under an entry's title are not its body.

    :param body: the lines after the title's blank line.
    :returns: the reason, or None where they are one to three lines with
        no blank line, no heading, no code fence and no html block.
    """
    if not body:
        return "the title is followed by a blank line and the body"
    if len(body) > _MAX_BODY_LINES:
        return f"the body runs past {_MAX_BODY_LINES} lines (section 9)"
    if any(
        not line.strip() or _ATX.match(line) or _UNDERLINE.fullmatch(line)
        for line in body
    ):
        return "the body holds no blank line and no heading"
    if any(opens_fence(line) or _HTML.match(line) for line in body):
        return "the body holds no code fence and no html block"
    return None


def text_problem(name: str, text: str) -> str | None:
    """Say why a file's text is not an entry.

    :param name: the file's name, for the message.
    :param text: the file's text.
    :returns: the reason, or None where the text is a `### ` title, a
        blank line and the body `body_problem()` admits, ending in one
        newline.
    """
    title, *rest = text.removesuffix("\n").split("\n")
    problem: str | None
    if "\r" in text:
        problem = "an entry's lines end with a line feed alone"
    elif not text.endswith("\n") or text.endswith("\n\n"):
        problem = "an entry ends with one newline"
    elif not _TITLE.fullmatch(title.rstrip()):
        problem = "an entry opens with a `### ` title"
    elif title != title.rstrip():
        problem = "the title ends with no space"
    elif rest[:1] != [""]:
        problem = "the title is followed by a blank line and the body"
    else:
        problem = body_problem(rest[1:])
    return f"{NEXT / name}: {problem}" if problem else None


def entry_problems(name: str, text: str) -> list[str]:
    """Say why a file under `NEXT` is not an entry.

    :param name: the file's name.
    :param text: the file's text.
    :returns: the reasons, none where it is an entry.
    """
    problem = name_problem(name) or text_problem(name, text)
    return [problem] if problem else []


def section(version: str, entries: dict[str, str]) -> str:
    """Write a release's section from its entries.

    :param version: the release's version, without the `v`.
    :param entries: each entry's file name against its text.
    :returns: the heading, then each entry in `order()`, a blank line
        between two.
    """
    texts = [entries[name] for name in sorted(entries, key=order)]
    return f"## v{version}\n\n" + "\n".join(texts)


def checker() -> Any:  # noqa: ANN401 - a module loaded by path
    """Load `check_changelog.py` from this script's directory.

    :returns: the module.
    :raises RefusedError: where the directory does not hold it.
    """
    spec = importlib.util.spec_from_file_location("_check_changelog", CHECKER)
    if spec is None or spec.loader is None or not CHECKER.is_file():
        msg = f"{CHECKER} is missing: it judges the section, beside this script"
        raise RefusedError([msg])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def section_problems(entries: dict[str, str], written: set[str]) -> list[str]:
    """Say why the entries' section is refused.

    Two entries with one title are named first, by file; any other
    refusal is `check_changelog.py`'s, run on the section the entries
    make.

    :param entries: each entry's file name against its text, every one
        an entry.
    :param written: the names asked about: a title another entry shares
        is reported for these alone.
    :returns: one message per reason, none where the section passes.
    """
    titles: dict[str, list[str]] = {}
    for name in sorted(entries):
        titles.setdefault(entries[name].split("\n", 1)[0], []).append(name)
    problems = [
        f"{NEXT / name}: {', '.join(o for o in names if o != name)} holds the"
        f" title {title!r} too, and a release's section repeats no heading"
        for title, names in titles.items()
        if len(names) > 1
        for name in names
        if name in written
    ]
    if problems or not entries:
        return problems
    text = section("0", entries)
    found: list[str] = checker().problems(text)
    return [f"the section the entries make, {problem}" for problem in found]


def opens_fence(line: str) -> str:
    """Return the marker of the fence a line opens.

    :param line: a line outside any fence.
    :returns: the backticks or tildes, or "" where it opens none: a
        backtick fence's info string holds no backtick.
    """
    found = _FENCE.fullmatch(line)
    if found is None or (found[1][0] == "`" and "`" in found[2]):
        return ""
    return found[1]


def code_lines(text: str) -> tuple[list[bool], bool]:
    """Say which lines of a file are code: fenced, or an html comment.

    The module docstring gives the fence rule.

    :param text: a whole file.
    :returns: for each line `splitlines()` gives, whether it is code;
        and whether a fence or a comment is still open at the end.
    """
    out = []
    fence = ""
    comment = False
    for line in text.splitlines():
        code = bool(fence) or comment
        found = _FENCE.fullmatch(line)
        opened = "" if fence or comment else opens_fence(line)
        if fence:
            if (
                found
                and found[1][0] == fence[0]
                and len(found[1]) >= len(fence)
                and not found[2].strip(" \t")
            ):
                fence = ""
        elif comment:
            comment = "-->" not in line
        elif opened:
            fence, code = opened, True
        elif _COMMENT.match(line):
            comment, code = "-->" not in line[line.index("<!--") + 4 :], True
        out.append(code)
    return out, bool(fence) or comment


def headings(text: str) -> list[tuple[int, str]]:
    """Return the offset and the line of each `## ` heading outside code.

    :param text: a whole file.
    :returns: each heading's offset into `text` and its line.
    """
    found = []
    offset = 0
    lines = text.splitlines(keepends=True)
    for line, code in zip(lines, code_lines(text)[0], strict=True):
        if not code and line.startswith("## "):
            found.append((offset, line.rstrip("\r\n")))
        offset += len(line)
    return found


def inserted(name: str, text: str, version: str, new: str) -> str:
    """Put a release's section above the file's first `## ` heading.

    :param name: the file's name, for the message.
    :param text: the file.
    :param version: the release's version, without the `v`.
    :param new: the section `section()` wrote.
    :returns: the file with the section in it, or at its end where it
        holds no `## ` heading.
    :raises RefusedError: where the file already holds the heading, holds
        a work-in-progress one, or ends inside a code fence or an html
        comment.
    """
    found = headings(text)
    if any(line == f"## v{version}" for _, line in found):
        msg = f"{name} already holds ## v{version}: a release that holds it is done"
        raise RefusedError([msg])
    if any(_WORK_IN_PROGRESS in line for _, line in found):
        msg = (
            f"{name} holds a {_WORK_IN_PROGRESS} heading, which a release does"
            " not fold: remove the heading, move what its section holds into"
            f" {NEXT}/ as entries, and commit both before the run"
        )
        raise RefusedError([msg])
    if code_lines(text)[1]:
        msg = f"{name} ends inside a code fence or an html comment"
        raise RefusedError([msg])
    if found:
        start = found[0][0]
        return text[:start] + new + "\n" + text[start:]
    return text.rstrip("\n") + "\n\n" + new


def uncommitted(root: Path) -> list[str]:
    """List the history files and entries the commit does not hold as they are.

    An ignored file counts where the assembly would read it, a history
    file or an `.md` file in `NEXT`, so that going back to the commit
    loses nothing it read; another ignored file, as an editor's, does not.

    :param root: the tree's root.
    :returns: each path `git status` shows changed, staged, untracked or
        ignored where the assembly reads it.
    :raises RefusedError: where the tree is not a git checkout, or git is
        missing.
    """
    try:
        done = subprocess.run(  # noqa: S603
            [  # noqa: S607
                "git",
                "-C",
                str(root),
                "status",
                "--porcelain",
                "--untracked-files=all",
                "--ignored",
                "--",
                *FILES,
                str(NEXT),
            ],
            capture_output=True,
            encoding="utf-8",
            check=False,
        )
    except OSError:
        done = None
    if done is None or done.returncode:
        msg = (
            f"{root.resolve()} is not a git checkout, or git is missing: the"
            " assembly runs on a commit, so that git can undo a run that does"
            " not finish"
        )
        raise RefusedError([msg])
    return [
        line[3:]
        for line in done.stdout.splitlines()
        if not line.startswith("!! ") or read_by_assembly(line[3:])
    ]


def read_by_assembly(path: str) -> bool:
    """Say whether the assembly reads a path of the tree.

    :param path: the path, from the tree's root, as git writes it.
    :returns: whether it is a history file or an `.md` file in `NEXT`.
    """
    found = PurePosixPath(path)
    return path in FILES or (found.parent == NEXT and found.suffix == ".md")


def recovery(left: list[Path]) -> str:
    """Say how to take the tree back to its commit after a killed run.

    :param left: the directories a killed run left at the tree's root.
    :returns: the command, run from the tree's root, and what it does.
    """
    command = shlex.join(
        [
            "git",
            "restore",
            "--source=HEAD",
            "--staged",
            "--worktree",
            "--",
            *FILES,
            str(NEXT),
        ]
    )
    if left:
        command += " && " + shlex.join(["rm", "-rf", "--", *(p.name for p in left)])
    return (
        "to take the history files and the entries back to the commit, run"
        f" from the tree's root: {command}"
    )


def stage(
    root: Path, files: dict[Path, bytes], removed: list[Path]
) -> tuple[Path, dict[Path, Path], dict[Path, Path]]:
    """Write what the assembly needs before it changes anything.

    Every byte the assembly and its undoing need is written here, so a
    full disk stops the assembly here, before any file has changed.

    :param root: the tree's root, where the directory goes.
    :param files: each history file against its new bytes.
    :param removed: the entries to remove.
    :returns: the directory; each history file against its new text;
        each history file and entry against its second name.
    """
    staged = Path(tempfile.mkdtemp(dir=root, prefix=_STAGING))
    try:
        new: dict[Path, Path] = {}
        kept: dict[Path, Path] = {}
        for index, (path, data) in enumerate(files.items()):
            new[path] = staged / f"new-{index}"
            new[path].write_bytes(data)
            new[path].chmod(stat.S_IMODE(path.stat().st_mode))
        for index, path in enumerate([*files, *removed]):
            kept[path] = staged / f"kept-{index}"
            kept[path].hardlink_to(path)
    except BaseException:
        shutil.rmtree(staged)
        raise
    return staged, new, kept


def apply(root: Path, files: dict[Path, bytes], removed: list[Path]) -> None:
    """Replace the files, then remove the entries, undoing it all on a failure.

    Once `stage()` has run, each step renames or removes a name, and so
    does each step that undoes one: a hard link keeps each file's bytes
    and mode under a second name until the assembly is done.

    :param root: the tree's root.
    :param files: each history file against its new bytes.
    :param removed: the entries to remove.
    """
    staged, new, kept = stage(root, files, removed)
    changed: list[Path] = []
    try:
        for path in files:
            new[path].replace(path)
            changed.append(path)
        for path in removed:
            path.unlink()
            changed.append(path)
    except BaseException:
        for path in reversed(changed):
            kept[path].replace(path)
        shutil.rmtree(staged)
        raise
    shutil.rmtree(staged)


def assemble(version: str, root: Path) -> list[Path]:
    """Assemble the entries under `NEXT` into each history file; remove them.

    Nothing is written unless everything is admitted, and a failure
    while writing puts back what was written.

    :param version: the release's version, without the `v`.
    :param root: the tree's root.
    :returns: the entries removed.
    :raises RefusedError: where the version, an entry or a file is
        refused, or where there is no entry.
    """
    if left := [
        path
        for path in sorted(root.glob(f"{_STAGING}*"))
        if path.is_dir() and not path.is_symlink()
    ]:
        names = ", ".join(path.name for path in left)
        msg = (
            f"{names}: left by an assembly that did not finish, so a history"
            " file or an entry may be changed"
        )
        raise RefusedError([msg, recovery(left)])
    if changes := uncommitted(root):
        msg = (
            f"{', '.join(changes)}: commit them first, so that git can undo a"
            " run that does not finish"
        )
        raise RefusedError([msg])
    problems = []
    if not _VERSION.fullmatch(version):
        problems.append(f"{version!r} is not a version: digits and dots")
    directory = root / NEXT
    paths = sorted(directory.glob("*.md")) if directory.is_dir() else []
    if not paths:
        problems.append(
            f"{NEXT} holds no entry: nothing changed for a user, so there"
            " is nothing to release"
        )
    irregular = [path for path in paths if path.is_symlink() or not path.is_file()]
    problems += [
        f"{NEXT / path.name}: an entry is a regular file" for path in irregular
    ]
    data = {path: path.read_bytes() for path in paths if path not in irregular}
    entries = {path.name: raw.decode("utf-8") for path, raw in data.items()}
    for name, text in entries.items():
        problems += entry_problems(name, text)
    if not problems:
        problems += section_problems(entries, set(entries))
    targets = [root / name for name in FILES]
    problems += [f"{path.name} is missing" for path in targets if not path.is_file()]
    if problems:
        raise RefusedError(problems)
    new = section(version, entries)
    files = {
        path: inserted(
            path.name, path.read_bytes().decode("utf-8"), version, new
        ).encode("utf-8")
        for path in targets
    }
    apply(root, files, list(data))
    return paths


# what runs git: `git()` below, or a test's stand-in
type Git = Callable[..., subprocess.CompletedProcess[str]]


def git(*args: str) -> subprocess.CompletedProcess[str]:
    """Run git in the working directory, the tree's checkout.

    :param args: git's arguments.
    :returns: what git answered, its output decoded.
    """
    return subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        capture_output=True,
        encoding="utf-8",
        check=False,
    )


# a path the diff changes: its mode at the base and at the head, its blob
# at the base and at the head, its status letter and its path
type Change = tuple[str, str, str, str, str, str]


def changed(base: str, head: str, run: Git = git) -> list[Change]:
    """List what the diff changes, renames read as a removal and an addition.

    :param base: the commit compared against.
    :param head: the commit compared.
    :param run: what runs git.
    :returns: each path the diff changes, as `Change` gives it.
    :raises RefusedError: where git cannot read the diff.
    """
    answer = run("diff", "--raw", "--no-abbrev", "--no-renames", "-z", base, head)
    if answer.returncode:
        msg = f"git cannot read the diff {base}..{head}: {answer.stderr.strip()}"
        raise RefusedError([msg])
    fields = answer.stdout.split("\0")
    out = []
    for index in range(0, len(fields) - 1, 2):
        old, new, before, after, status = fields[index].lstrip(":").split(" ")
        out.append((old, new, before, after, status, fields[index + 1]))
    return out


def project(commit: str, run: Git = git) -> dict[str, Any]:
    """Read `pyproject.toml`'s `[project]` table at a commit, `version` aside.

    :param commit: the commit to read.
    :param run: what runs git.
    :returns: the table, empty where the commit holds no such file.
    """
    answer = run("show", f"{commit}:pyproject.toml")
    if answer.returncode:
        return {}
    table: dict[str, Any] = tomllib.loads(answer.stdout).get("project", {})
    return {key: value for key, value in table.items() if key != "version"}


def package_paths(
    base: str,
    head: str,
    diff: list[Change],
    run: Git = git,
) -> list[str]:
    """List what the diff changes of what a user installs.

    :param base: the commit compared against.
    :param head: the commit compared.
    :param diff: what `changed()` listed.
    :param run: what runs git.
    :returns: each path under `src/`, each gitlink, and `pyproject.toml`
        where its `[project]` table but `version` changed.
    """
    found = [
        path
        for old, new, *_, path in diff
        if path.startswith("src/") or _GITLINK in {old, new}
    ]
    paths = {path for *_, path in diff}
    if "pyproject.toml" in paths and project(base, run) != project(head, run):
        found.append("pyproject.toml")
    return found


def pending(commit: str, run: Git = git) -> dict[str, str]:
    """Read every entry a commit holds under `NEXT`, regular files alone.

    :param commit: the commit to read.
    :param run: what runs git.
    :returns: each entry's file name against its text.
    """
    listed = run("ls-tree", "-z", commit, "--", f"{NEXT}/").stdout.split("\0")
    out = {}
    for line in filter(None, listed):
        meta, _, path = line.partition("\t")
        name = PurePosixPath(path).name
        if meta.split(" ")[0] in _REGULAR and name.endswith(".md"):
            out[name] = run("show", f"{commit}:{path}").stdout
    return out


def check(base: str, head: str, labels: list[str], run: Git = git) -> list[str]:
    """Say why a diff is refused for its changelog entry.

    :param base: the commit compared against, a merge commit's first parent.
    :param head: the commit compared.
    :param labels: the pull request's labels.
    :param run: what runs git.
    :returns: one message per reason, none where the diff passes.
    """
    diff = changed(base, head, run)
    # an entry whose mode alone changed is not written: its text is the base's
    touched = [
        (new, path)
        for _, new, before, after, status, path in diff
        if (status in {"A", "T"} or (status == "M" and before != after))
        and PurePosixPath(path).parent == NEXT
        and path.endswith(".md")
    ]
    publishes = run("cat-file", "-e", f"{head}:{RELEASE}").returncode == 0
    if not publishes:
        return [
            f"{path}: this tree does not publish, so it writes no entry (section 9)"
            for _, path in touched
        ]
    problems = [
        f"{path}: an entry is a regular file, and this one's mode is {mode}"
        for mode, path in touched
        if mode not in _REGULAR
    ]
    written = [path for mode, path in touched if mode in _REGULAR]
    for path in written:
        text = run("show", f"{head}:{path}").stdout
        problems += entry_problems(PurePosixPath(path).name, text)
    if written and not problems:
        problems += section_problems(
            pending(head, run),
            {PurePosixPath(path).name for path in written},
        )
    package = package_paths(base, head, diff, run)
    if package and not written and LABEL not in labels:
        shown = ", ".join(package[:_SHOWN])
        if len(package) > _SHOWN:
            shown += ", ..."
        problems.append(
            f"{shown}: the diff changes what a user gets, and no file under"
            f" {NEXT}/ holds its entry: add {NEXT}/<n>.md (section 9 of"
            f" btclib-org/.github's README.md), or label the pull request"
            f" {LABEL} where it changes nothing a user gets",
        )
    return problems


def label_names(text: str) -> list[str]:
    """Read the labels `--labels` gives.

    :param text: the option's value.
    :returns: the names.
    :raises RefusedError: where the value is not a JSON list of strings.
    """
    try:
        found = json.loads(text)
    except json.JSONDecodeError:
        found = None
    if not isinstance(found, list) or not all(isinstance(x, str) for x in found):
        msg = f"--labels takes a JSON list of strings, not {text!r}"
        raise RefusedError([msg])
    return found


def main(argv: Sequence[str] | None = None) -> int:
    """Run the requested command.

    :param argv: the arguments, `sys.argv[1:]` where none are given.
    :returns: 0 where the command passed, 1 where it refused.
    """
    parser = argparse.ArgumentParser(
        description="Assemble a release's changelog entries, or ask a diff for one.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    assembling = sub.add_parser("assemble", help="assemble the entries into a release")
    assembling.add_argument("version", help="the release's version, without the v")
    checking = sub.add_parser("check", help="ask a diff for its entry")
    checking.add_argument("base")
    checking.add_argument("head")
    checking.add_argument("--labels", default="[]", help="a JSON list of label names")
    args = parser.parse_args(argv)
    try:
        if args.command == "assemble":
            for path in assemble(args.version, Path()):
                print(f"assembled and removed {path.as_posix()}")
            return 0
        problems = check(args.base, args.head, label_names(args.labels))
    except RefusedError as refused:
        problems = refused.problems
    for problem in problems:
        print(problem, file=sys.stderr)
    if not problems:
        print(f"{args.base}..{args.head}: the changelog entry is in order")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
