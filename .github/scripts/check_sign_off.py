# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Refuse each commit with no `Signed-off-by:` trailer naming its author.

What the trailer attests, and why a signature does not stand in for it,
is section 11's *Signatures* in btclib-org/.github's `README.md`.

A trailer counts where its address, the part in angle brackets, is the
commit's author address, compared without case. Two kinds of commit are
not read:

- a merge commit. The one GitHub's *Update branch* writes onto a pull
  request's branch is authored by whoever pressed it and carries no
  trailer. A conflict resolved by hand in a merge is not read either.
- a commit whose author address is one in `BOTS`. Dependabot signs off
  as `support@github.com`, not as its author, and pre-commit.ci does not
  sign off at all.

    uv run --no-project --python 3.15 \
        .github/scripts/check_sign_off.py HEAD^1..HEAD^2

run from the root of a checkout of a pull request's merge commit, whose
two parents are the base and the head. Locally, `origin/main..HEAD`.
"""

from __future__ import annotations

import argparse
import re
import subprocess

# the author addresses GitHub gives Dependabot's and pre-commit.ci's commits
BOTS = frozenset(
    {
        "49699333+dependabot[bot]@users.noreply.github.com",
        "66853113+pre-commit-ci[bot]@users.noreply.github.com",
    }
)

_ADDRESS = re.compile(r"<([^<>]+)>\s*$")


def _git(*args: str) -> str:
    """Return what git prints, run in the working directory."""
    ran = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    return ran.stdout


def signs_off(author: str, trailers: str) -> bool:
    """Say whether a `Signed-off-by:` value names this author address."""
    for value in trailers.splitlines():
        found = _ADDRESS.search(value)
        if found and found[1].casefold() == author.casefold():
            return True
    return False


def refused(revisions: str) -> list[str]:
    """Return a line per commit of the range that does not sign off."""
    lines = []
    for sha in _git("rev-list", "--no-merges", revisions).split():
        author = _git("show", "-s", "--format=%ae", sha).strip()
        if author in BOTS:
            continue
        trailers = _git(
            "show", "-s", "--format=%(trailers:key=Signed-off-by,valueonly)", sha
        )
        if not signs_off(author, trailers):
            subject = _git("show", "-s", "--format=%s", sha).strip()
            lines.append(f"{sha[:12]} {subject}: no Signed-off-by: <{author}>")
    return lines


def fork_point(revisions: str) -> str:
    """Return the sha where a range of the form `base..head` leaves its base.

    The commit is on the branch, so its author has it without fetching.
    Where the branch merged its base, it is the base commit last merged,
    so a rebase onto it replays the branch's own commits and none merged in.
    """
    ends = _git("rev-parse", revisions).split()
    head = [end for end in ends if not end.startswith("^")]
    base = [end[1:] for end in ends if end.startswith("^")]
    return _git("merge-base", *head, *base).strip()


def main(argv: list[str] | None = None) -> int:
    """Read the range from the command line and check its commits."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("revisions", help="the range, as git rev-list reads it")
    args = parser.parse_args(argv)

    lines = refused(args.revisions)
    for line in lines:
        print(f"::error::{line}")
    if lines:
        print(
            "Each commit above needs a Signed-off-by: trailer with the address"
            " shown, added by that commit's author. Where they are all yours, run"
            " this with that address as your git user.email, then force-push the"
            " branch:\n"
            f"    git rebase --signoff {fork_point(args.revisions)}\n"
            "The pull request cannot merge until every commit above has one."
        )
        return 1
    print(f"every commit of {args.revisions} read is signed off by its author")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
