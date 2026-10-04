# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Rebuild `CHANGELOG.md` and `RELEASE_NOTES.md` after a rebase or merge.

A rebase stopped on a conflict in these files leaves markers around two blocks
that share lines, and at git's default conflict style deleting the markers
writes those lines once, such as the blank line between entries. A tree that
still sets `merge=union` gets the same damage with no conflict. This script
rebuilds them.

For each file the branch changed between its old base and its old tip, the
script takes the block the branch added and splices it into the new base's
copy. The open section of each file is its first `## ` heading, and the block
goes at the same distance from that section's end as it had in the old tip:
the lines that followed it there must be the last lines of the new base's
open section. The block goes into the new base's open section, not into a
section a release closed meanwhile.

The script refuses, and leaves the file alone, where

- the branch's change is not one contiguous addition,
- the block holds a `## ` heading, or does not lie in the open section,
- the branch adds or deletes the file, or the new base has no such file,
- the file has no open section in the new base, or the lines that followed
  the block are not found at the end of it,
- a file does not end in a newline.

A refused file is rebuilt by hand.

The block is read rightmost, so a line it shares with the text above it is
counted as that text's. A place is found by its position in the section, so
it is found exactly once or not at all.

Exit status: 0 where every file already agrees, 1 where one was written, 2
where one was refused. Run in the worktree, with the rebase or merge stopped
or finished:

    uv run --no-project --python 3.15 \
        .github/scripts/rebuild_union_files.py <old base> <old tip>

Where it was stopped, `git add` the files, then `git rebase --continue` or
`git merge --continue`; where it finished, commit them. On a branch of
several commits the whole block is written at the first stop, so a later
commit that only touched the file turns empty and the rebase drops it.

The new base is `MERGE_HEAD` during a merge, else
`git merge-base HEAD origin/main`; `--base` names another. During a merge
`HEAD` is still the old tip, so its merge base would be the old base.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

FILES = ("CHANGELOG.md", "RELEASE_NOTES.md")
HEADING = "## "


class Refused(Exception):  # noqa: N818
    """A file the script will not rebuild, with the reason."""


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    """Run git in the working directory."""
    return subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        capture_output=True,
        check=check,
    )


def _lines(revision: str, name: str) -> list[str] | None:
    """Return the lines of a file at a revision, or None where it has none."""
    ran = _git("show", f"{revision}:{name}", check=False)
    if ran.returncode:
        return None
    return _split(ran.stdout)


def _split(data: bytes) -> list[str]:
    """Split text into lines that keep their endings."""
    text = data.decode("utf-8")
    if text and not text.endswith("\n"):
        msg = "does not end in a newline"
        raise Refused(msg)
    return text.splitlines(keepends=True)


def _open_section(lines: list[str]) -> tuple[int, int] | None:
    """Return the first line after the first heading, and the section's end."""
    headings = [i for i, line in enumerate(lines) if line.startswith(HEADING)]
    if not headings:
        return None
    end = headings[1] if len(headings) > 1 else len(lines)
    return headings[0] + 1, end


def added_block(
    before: list[str], after: list[str]
) -> tuple[list[str], list[str]] | None:
    """Return the block added and the lines after it in the open section.

    None where the file did not change. The block is read rightmost.
    """
    if before == after:
        return None
    size = len(after) - len(before)
    cut = 0
    while cut < min(len(before), len(after)) and before[cut] == after[cut]:
        cut += 1
    if size <= 0 or before[cut:] != after[cut + size :]:
        msg = "the branch's change is not one contiguous addition"
        raise Refused(msg)
    block = after[cut : cut + size]
    if any(line.startswith(HEADING) for line in block):
        msg = f"the block holds a `{HEADING}` heading"
        raise Refused(msg)
    section = _open_section(after)
    if section is None or not section[0] <= cut < cut + size <= section[1]:
        msg = "the block does not lie in the open section"
        raise Refused(msg)
    return block, after[cut + size : section[1]]


def rebuilt(base: list[str], block: list[str], tail: list[str]) -> list[str]:
    """Return the new base with the block put before the tail of its section."""
    section = _open_section(base)
    if section is None:
        msg = "the new base has no open section"
        raise Refused(msg)
    end = section[1]
    start = end - len(tail)
    if start < section[0] or base[start:end] != tail:
        msg = "the lines that followed the block are not at the end of the open section"
        raise Refused(msg)
    return [*base[:start], *block, *base[start:]]


def rebuild(name: str, old_base: str, old_tip: str, new_base: str) -> int:
    """Rebuild one file; return 0 where it agrees and 1 where it was written."""
    before = _lines(old_base, name)
    after = _lines(old_tip, name)
    if before is None and after is None:
        print(f"{name}: in neither revision, left alone")
        return 0
    if before is None or after is None:
        msg = "the branch adds or deletes the file"
        raise Refused(msg)
    found = added_block(before, after)
    if found is None:
        print(f"{name}: the branch did not change it, left alone")
        return 0
    base = _lines(new_base, name)
    if base is None:
        msg = "the new base has no such file"
        raise Refused(msg)
    expected = "".join(rebuilt(base, *found)).encode("utf-8")
    path = Path(_git("rev-parse", "--show-toplevel").stdout.decode().strip()) / name
    if path.is_file() and path.read_bytes() == expected:
        print(f"{name}: agrees")
        return 0
    path.write_bytes(expected)
    print(f"{name}: written, {len(found[0])} lines of the branch's block")
    return 1


def default_base() -> str:
    """Return `MERGE_HEAD` during a merge, else the merge base with main."""
    merging = _git("rev-parse", "-q", "--verify", "MERGE_HEAD", check=False)
    if merging.returncode == 0:
        return merging.stdout.decode().strip()
    return _git("merge-base", "HEAD", "origin/main").stdout.decode().strip()


def main(argv: list[str] | None = None) -> int:
    """Read the revisions from the command line and rebuild each file."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("old_base", help="the branch's base before the rebase")
    parser.add_argument("old_tip", help="the branch's tip before the rebase")
    parser.add_argument(
        "--base",
        help="the new base; the default is in the docstring",
    )
    args = parser.parse_args(argv)

    new_base = args.base or default_base()
    status = 0
    for name in FILES:
        try:
            changed = rebuild(name, args.old_base, args.old_tip, new_base)
        except Refused as why:
            print(f"::error::{name}: refused, {why}")
            status = 2
        else:
            if status == 0:
                status = changed
    return status


if __name__ == "__main__":
    raise SystemExit(main())
