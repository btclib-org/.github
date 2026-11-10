# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Refuse a release section that adds more than the release, or too little.

`reusable-claude-release.yml` has the agent write a release's section of
`CHANGELOG.md` and of `RELEASE_NOTES.md`, and this is what its gates job
asks of each file before the tree's own gates run. The edited file is
compared with the file at the base, the commit the release is cut from:

- its first `## ` heading is `## v<version>`, alone on its line, and its
  section holds a line that is not blank. `release.yml` asks the same of
  the tag's section before anything is built, through the awk program of
  `reusable-version-check.yml`, and asks it of the section wherever it
  stands;
- no `## ` heading holds `(work in progress, not released yet)`: the
  release pull request folds such a section into its own, as
  `shared/RELEASING.md`'s *Release to PyPI* says;
- the file without the release's section is the base without its first
  section where that is a work-in-progress one, and the base whole
  otherwise. So the agent changes no line outside its section, a
  released entry included. Section 9 lets a release's pull request
  correct which issues a released entry cites; that edit is a person's.

A `## ` line inside a fenced code block is an example, not a heading.

    uv run --no-project --python 3.15 \
        .github/scripts/check_release_sections.py \
        "$version" CHANGELOG.md base.md

where `base.md` is the file at the base, `git show HEAD:CHANGELOG.md`.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

# the words a work-in-progress heading carries after its version
_WORK_IN_PROGRESS = "(work in progress, not released yet)"

_FENCE = re.compile(r"^(```|~~~)")


def headings(lines: list[str]) -> list[int]:
    """Return the index of each `## ` heading, fenced blocks left out."""
    found = []
    fenced = False
    for index, line in enumerate(lines):
        if _FENCE.match(line):
            fenced = not fenced
        elif not fenced and line.startswith("## "):
            found.append(index)
    return found


def first_section(lines: list[str]) -> tuple[int, int] | None:
    """Return where the first `## ` section starts and ends, or None."""
    found = headings(lines)
    if not found:
        return None
    end = found[1] if len(found) > 1 else len(lines)
    return found[0], end


def problems(version: str, text: str, base: str) -> list[str]:
    """Return why the edited file is refused, nothing where it passes.

    :param version: the release's version, without the `v`.
    :param text: the edited file.
    :param base: the file at the base.
    :returns: one message per refusal.
    """
    heading = f"## v{version}"
    lines = text.splitlines()
    section = first_section(lines)
    if section is None or lines[section[0]] != heading:
        first = "none" if section is None else repr(lines[section[0]])
        return [f'the first "## " heading is {first}, not "{heading}" alone']
    start, end = section
    found: list[str] = []
    if not any(line.strip() for line in lines[start + 1 : end]):
        found.append(f'the section "{heading}" is empty')
    found.extend(
        f"line {index + 1} still heads a work-in-progress section"
        for index in headings(lines)
        if _WORK_IN_PROGRESS in lines[index]
    )
    before = base.splitlines()
    folded = first_section(before)
    if folded is not None and _WORK_IN_PROGRESS in before[folded[0]]:
        before = before[: folded[0]] + before[folded[1] :]
    if lines[:start] + lines[end:] != before:
        found.append(
            f'the file outside "{heading}" differs from the base, a folded'
            " work-in-progress section left out"
        )
    return found


def main(argv: list[str] | None = None) -> int:
    """Read the version and the two files, and report each refusal."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="the release's version, without the v")
    parser.add_argument("file", help="the edited file")
    parser.add_argument("base", help="the file at the base")
    args = parser.parse_args(argv)

    text = Path(args.file).read_text(encoding="utf-8")
    base = Path(args.base).read_text(encoding="utf-8")
    found = problems(args.version, text, base)
    for problem in found:
        print(f"::error file={args.file}::{problem}")
    if found:
        return 1
    print(f'{args.file} adds "## v{args.version}" and changes nothing else')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
