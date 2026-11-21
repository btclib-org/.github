# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Assemble a release's changelog entries, and ask a pull request for one.

Section 9 of README.md gives the rule this script keeps: what an entry
under `changelog/next/` is named, what it holds, and when a pull request
adds one. What follows is what the code adds to it.

An entry's body holds no heading, no code fence and no html block, and
this script finds them so. A heading is a `#` run of one to six followed
by a space or the line's end, after any indent or block-quote marker, or
a line of `=` or of `-` alone, which is a setext underline after a text
line and a thematic break otherwise: either is refused. An html block is
one a blank line does not end, which could run on into the next entry:
a comment, `<script`, `<pre`, `<style`, `<textarea`, a processing
instruction (`<?`), a declaration (`<!` and a letter) and CDATA.

An entry is named `pr<N>.md`, or `pr<N>-iss<Y>.md` and on, `<N>` being
the pull request that adds it. The issues are the ones its text cites,
as `check_changelog.py`'s `cited_tokens()` reads a citation, in the
text's order and each once: `iss<Y>` for `#Y`, `<repo>-iss<Y>` for
`btclib-org/<repo>#Y`, the repository's name in lower case and without a
leading dot, and nothing for an issue of another owner. Both commands
refuse an entry whose `iss` parts are not those.

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
order of their pull requests' numbers that `order()` gives, above the
first `## ` heading outside a fence of each history file, and removes
the entries. The output depends on the
entries alone, so the same files give the same bytes, and a reviewer of
the release runs the command on the commit the release is cut from,
which holds every entry, and compares. It refuses a
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
`--labels` holds `LABEL`. Given `--pull-request`, it refuses an entry
the diff adds whose `pr<N>` is another number, and prints the name it
expects; without it, as in a local run, it reads the name's shape and
its `iss` parts alone. An entry the diff edits keeps its name, unless
the edit changes what it cites: then the name it prints carries the
pull request's number, or `<N>` without `--pull-request`. The
package is what a user installs: a path under `src/`, a gitlink, which
pins vendored code a wheel builds, and the `[project]` table of
`pyproject.toml` but its `version`, which a release's own pull request
sets. In a tree that does not publish, it
refuses any entry added or edited: nothing would ever assemble it. An
entry is edited where its text changes: one whose mode alone changes
says nothing new, and is no entry for the diff. A rename is none either:
an entry added with the blob of one the diff removes was written by the
pull request that added it first, so it asks the package for nothing
and `--pull-request` does not name it. Its name is read as any other's.

    uv run --no-project --python 3.15 changelog_entries.py assemble 2026.11.15
    uv run --no-project --python 3.15 changelog_entries.py check \
        HEAD^1 HEAD --labels "$LABELS" --pull-request "$NUMBER"

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

# an entry's name: its pull request's number, then an `iss` part for each
# issue its text cites, one of another btclib-org repository after that
# repository's name
_NAME = re.compile(
    r"pr(?P<number>[1-9][0-9]*)"
    r"(?P<cited>(?:-(?:[a-z0-9][a-z0-9._-]*-)?iss(?:0|[1-9][0-9]*))*)\.md",
)
# the owner whose repositories an entry's name holds the issues of
_ORGANIZATION = "btclib-org"
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


def order(name: str) -> tuple[int, str]:
    """Return where an entry stands in the release's section.

    The entries follow their pull requests' numbers, and two entries of
    one pull request follow their names.

    :param name: the file's name, which `name_problem()` admits.
    :returns: the key to sort by.
    """
    found = _NAME.fullmatch(name)
    if found is None:
        msg = f"{name} is not the name of an entry"
        raise ValueError(msg)
    return int(found["number"]), name


def expected_name(number: int | str, text: str) -> str:
    """Return the name of an entry of a pull request, from its text.

    Each issue the text cites gives an `iss` part, in the text's order and
    once: `iss<Y>` for `#Y`, `<repo>-iss<Y>` for `btclib-org/<repo>#Y`, the
    repository's name in lower case and without a leading dot. An issue of
    another owner gives none.

    :param number: the pull request's number, or `<N>` where it is not known.
    :param text: the entry's text.
    :returns: the file's name.
    """
    parts: list[str] = []
    for token in checker().cited_tokens(text):
        where, _, issue = token.partition("#")
        owner, _, repo = where.partition("/")
        if owner and owner.lower() != _ORGANIZATION:
            continue
        repo = repo.lower().removeprefix(".")
        part = f"{repo}-iss{int(issue)}" if repo else f"iss{int(issue)}"
        if part not in parts:
            parts.append(part)
    return "-".join([f"pr{number}", *parts]) + ".md"


def name_problem(name: str) -> str | None:
    """Say why a file name is not an entry's.

    :param name: the file's name, without its directory.
    :returns: the reason, or None where the name is an entry's.
    """
    if _NAME.fullmatch(name):
        return None
    return (
        f"{NEXT / name}: an entry is named pr<N>.md or pr<N>-iss<Y>.md, <N>"
        " being the pull request that adds it and each iss<Y> an issue its"
        " text cites (section 9)"
    )


def cited_problem(
    name: str,
    text: str,
    number: int | None = None,
    editor: int | str | None = None,
) -> str | None:
    """Say why an entry's name is not the one its text and number give.

    :param name: the file's name, which `name_problem()` admits.
    :param text: the file's text, which `text_problem()` admits.
    :param number: the pull request adding it, None to keep the name's.
    :param editor: the pull request editing it, or `<N>` where its number
        is not known: an edit that changes what the entry cites renames it
        under that number. None where nothing edits it.
    :returns: the reason, naming the file's expected name, or None.
    """
    own = order(name)[0] if number is None else number
    expected = expected_name(own, text)
    if name == expected:
        return None
    if number is None and editor is not None:
        return (
            f"{NEXT / name}: an edit that changes the issues an entry cites"
            " renames it, under the number of the pull request that edits it"
            f" (section 9): {NEXT / expected_name(editor, text)}"
        )
    what = "" if number is None else "its pull request and "
    return (
        f"{NEXT / name}: an entry is named for {what}the issues its text cites,"
        f" in the text's order (section 9): {NEXT / expected}"
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


def entry_problems(
    name: str,
    text: str,
    number: int | None = None,
    editor: int | str | None = None,
) -> list[str]:
    """Say why a file under `NEXT` is not an entry.

    :param name: the file's name.
    :param text: the file's text.
    :param number: the pull request that adds it, where it is to name it.
    :param editor: the pull request that edits it, as `cited_problem()`
        reads it.
    :returns: the reasons, none where it is an entry.
    """
    problem = (
        name_problem(name)
        or text_problem(name, text)
        or cited_problem(name, text, number, editor)
    )
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
            " not fold: remove the heading and move what its section holds into"
            f" {NEXT}/ as entries, in a pull request of its own before the"
            " release"
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


def tracked(root: Path) -> set[str]:
    """List the paths git tracks under `NEXT`, as it writes them.

    :param root: the tree's root, a git checkout `uncommitted()` read.
    :returns: each path from the tree's root.
    """
    done = subprocess.run(  # noqa: S603
        ["git", "-C", str(root), "ls-files", "-z", "--", str(NEXT)],  # noqa: S607
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    return set(filter(None, done.stdout.split("\0")))


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
    for depth in range(1, len(NEXT.parts) + 1):
        part = PurePosixPath(*NEXT.parts[:depth])
        if (root / part).is_symlink():
            msg = (
                f"{part} is a symlink: the entries are the tree's own files,"
                " which git can restore"
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
    known = tracked(root)
    problems += [
        f"{NEXT / path.name}: git tracks no file at this path, so it could not"
        " restore it"
        for path in data
        if (NEXT / path.name).as_posix() not in known
    ]
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
    """Run git on the repository `GIT_DIR` names, else the working directory's.

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


# an entry the diff writes: its mode at the head, its status letter,
# whether it is a rename, and its path
type Touched = tuple[str, str, bool, str]


def touched_entries(diff: list[Change]) -> list[Touched]:
    """List the entries the diff adds, edits or renames.

    :param diff: what `changed()` listed.
    :returns: each `.md` path under `NEXT` added, type-changed, or given a
        new blob, a rename being an addition of a blob the diff removes.
    """
    entries = [
        change
        for change in diff
        if PurePosixPath(change[5]).parent == NEXT and change[5].endswith(".md")
    ]
    # a rename reads as a removal and an addition of the same blob
    removed = {before for _, _, before, _, status, _ in entries if status == "D"}
    # an entry whose mode alone changed is not written: its text is the base's
    return [
        (new, status, after in removed and status == "A", path)
        for _, new, before, after, status, path in entries
        if status in {"A", "T"} or (status == "M" and before != after)
    ]


def read_problems(
    read: list[Touched],
    head: str,
    number: int | None,
    run: Git = git,
) -> list[str]:
    """Say why an entry the diff writes is not one, its name included.

    :param read: the regular files `touched_entries()` listed.
    :param head: the commit compared.
    :param number: the pull request's number, None where it is not known.
    :param run: what runs git.
    :returns: one message per reason.
    """
    problems = []
    for _, status, renamed, path in read:
        text = run("show", f"{head}:{path}").stdout
        # an entry the pull request adds is named for it, one it edits or
        # renames keeps the number it has, and one whose edit changes what
        # it cites is renamed under the pull request's
        added = status == "A" and not renamed
        named = number if added else None
        editor = None if added or renamed else ("<N>" if number is None else number)
        problems += entry_problems(PurePosixPath(path).name, text, named, editor)
    return problems


def releases(commit: str, run: Git = git) -> set[str]:
    """Read the release headings of `CHANGELOG.md` at a commit.

    :param commit: the commit to read.
    :param run: what runs git.
    :returns: each `## v<version>` line outside code, none where the
        commit holds no such file.
    """
    answer = run("show", f"{commit}:{FILES[0]}")
    if answer.returncode:
        return set()
    return {
        line
        for _, line in headings(answer.stdout)
        if _VERSION.fullmatch(line.removeprefix("## v"))
    }


def moved(
    base: str,
    head: str,
    removed: list[str],
    run: Git = git,
) -> tuple[int, str | None]:
    """Count the entries the diff moves into the newest release's section.

    An entry is moved where each history file at the head holds its text
    as an entry of its newest `## v<version>`, which is the newest of
    each file at the base too, no entry under `NEXT` at the head holds
    it, and `check_changelog.py`'s `tag_problem()` finds no reason in the
    tag.

    :param base: the commit compared against.
    :param head: the commit compared.
    :param removed: the entries the diff removes, by path.
    :param run: what runs git.
    :returns: how many it moves, and the tag's reason where it refuses
        the moves, None otherwise.
    """
    module = checker()
    found: set[str | None] = set()
    sections = []
    for name in FILES:
        release, entries = module.newest_release(run("show", f"{head}:{name}").stdout)
        before = module.newest_release(run("show", f"{base}:{name}").stdout)[0]
        found |= {release, before}
        sections.append(set(entries.values()))
    kept = {text.rstrip("\n") for text in pending(head, run).values()}
    texts = [run("show", f"{base}:{path}").stdout.rstrip("\n") for path in removed]
    count = sum(
        text not in kept and all(text in section for section in sections)
        for text in texts
    )
    if len(found) != 1 or None in found or not count:
        return 0, None
    tag: str | None = module.tag_problem(found.pop(), run)
    return (0, tag) if tag else (count, None)


def lost_entries(
    base: str,
    head: str,
    diff: list[Change],
    labels: list[str],
    run: Git = git,
) -> list[str]:
    """Say why the diff removes more entries than it adds.

    A rename, a retitle or a replacement removes one and adds one. A
    release's own pull request, whose `CHANGELOG.md` gains a
    `## v<version>` heading, removes them all, one labelled `LABEL`,
    such as the revert of an unreleased change, may remove its own, and
    an entry `moved()` counts is not lost. A move the tag refuses is
    refused whatever else the diff adds.

    :param base: the commit compared against.
    :param head: the commit compared.
    :param diff: what `changed()` listed.
    :param labels: the pull request's labels.
    :param run: what runs git.
    :returns: the reason, none where the diff passes.
    """
    entries = [
        (status, path)
        for *_, status, path in diff
        if PurePosixPath(path).parent == NEXT and path.endswith(".md")
    ]
    statuses = [status for status, _ in entries]
    gone, added = statuses.count("D"), statuses.count("A")
    if releases(head, run) - releases(base, run):
        return []
    removed = [path for status, path in entries if status == "D"]
    count, tag = moved(base, head, removed, run) if removed else (0, None)
    problems = []
    if gone - count > added and LABEL not in labels:
        problems.append(
            f"{NEXT}/: the diff removes {gone} entries and adds {added}, so the"
            " next release would lose what one says: only a release's assembly"
            " removes an entry, a pull request that moves it into the release's"
            f" section before the tag, or a pull request labelled {LABEL}"
            " (section 9)"
        )
    if tag:
        problems.append(
            f"{NEXT}/: the diff moves entries under the newest release, {tag}:"
            " an entry moves into a release's section only before its tag"
            " (section 9)"
        )
    return problems


def missing_entry(package: list[str], number: int | None) -> str:
    """Say that the diff changes the package and writes no entry.

    :param package: what `package_paths()` listed.
    :param number: the pull request's number, None where it is not known.
    :returns: the message, naming the first paths and the entry to add.
    """
    shown = ", ".join(package[:_SHOWN])
    if len(package) > _SHOWN:
        shown += ", ..."
    name = f"pr{'<N>' if number is None else number}-iss<Y>.md"
    return (
        f"{shown}: the diff changes what a user gets, and no file under"
        f" {NEXT}/ holds its entry: add {NEXT}/{name} (section 9 of"
        f" btclib-org/.github's README.md), or label the pull request"
        f" {LABEL} where it changes nothing a user gets"
    )


def check(
    base: str,
    head: str,
    labels: list[str],
    run: Git = git,
    number: int | None = None,
) -> list[str]:
    """Say why a diff is refused for its changelog entry.

    :param base: the commit compared against, a merge commit's first parent.
    :param head: the commit compared.
    :param labels: the pull request's labels.
    :param run: what runs git.
    :param number: the pull request's number, which names an entry it
        adds; None where it is not known, as in a local run.
    :returns: one message per reason, none where the diff passes.
    """
    diff = changed(base, head, run)
    touched = touched_entries(diff)
    publishes = run("cat-file", "-e", f"{head}:{RELEASE}").returncode == 0
    if not publishes:
        return [
            f"{path}: this tree does not publish, so it writes no entry (section 9)"
            for *_, path in touched
        ]
    problems = [
        f"{path}: an entry is a regular file, and this one's mode is {mode}"
        for mode, *_, path in touched
        if mode not in _REGULAR
    ]
    read = [change for change in touched if change[0] in _REGULAR]
    problems += read_problems(read, head, number, run)
    if read and not problems:
        problems += section_problems(
            pending(head, run),
            {PurePosixPath(path).name for *_, path in read},
        )
    problems += lost_entries(base, head, diff, labels, run)
    # a renamed entry was written by the pull request that added it
    written = [path for _, _, renamed, path in read if not renamed]
    package = package_paths(base, head, diff, run)
    if package and not written and LABEL not in labels:
        problems.append(missing_entry(package, number))
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


def pull_request_number(text: str) -> int:
    """Read the number `--pull-request` gives.

    :param text: the option's value.
    :returns: the number.
    :raises argparse.ArgumentTypeError: where it is not a positive number.
    """
    if not text.isascii() or not text.isdigit() or int(text) < 1:
        msg = f"a pull request's number is a positive integer, not {text!r}"
        raise argparse.ArgumentTypeError(msg)
    return int(text)


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
    checking.add_argument(
        "--pull-request",
        type=pull_request_number,
        help="the pull request's number, which names an entry it adds",
    )
    args = parser.parse_args(argv)
    try:
        if args.command == "assemble":
            for path in assemble(args.version, Path()):
                print(f"assembled and removed {path.as_posix()}")
            return 0
        problems = check(
            args.base,
            args.head,
            label_names(args.labels),
            number=args.pull_request,
        )
    except RefusedError as refused:
        problems = refused.problems
    for problem in problems:
        print(problem, file=sys.stderr)
    if not problems:
        print(f"{args.base}..{args.head}: the changelog entry is in order")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
