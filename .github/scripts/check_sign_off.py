# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Refuse each commit with no `Signed-off-by:` trailer naming its author.

What the trailer attests, and why a signature does not stand in for it,
is section 11's *Signatures* in the organization's standard.

A trailer counts where its address, the part in angle brackets, is the
commit's author address, compared without case. Two kinds of commit are
not read:

- a merge commit. The one GitHub's *Update branch* writes onto a pull
  request's branch is authored by whoever pressed it and carries no
  trailer. A conflict resolved by hand in a merge is not read either.
- a commit whose author address is one in `BOTS`. Dependabot signs off
  as `support@github.com`, not as its author, and pre-commit.ci does not
  sign off at all. claude[bot], which section 10's
  `reusable-claude-implement.yml` and `reusable-claude-release.yml`
  commit as, signs off nothing, for the reason `CONTRIBUTING.md`'s
  *Working with an LLM* gives. The rejected alternative is a trailer the
  workflow writes in its name, which certifies nothing.

  The exemption goes by the author address alone, not by who opened the
  pull request: a commit authored at one of these addresses passes in a
  person's pull request too.

    uv run --no-project --python 3.15 \
        .github/scripts/check_sign_off.py HEAD^1..HEAD^2

run from the root of a checkout of a pull request's merge commit, whose
two parents are the base and the head. Locally, `origin/main..HEAD`.

A failure prints each commit refused and how to add the trailer. Where
`GITHUB_STEP_SUMMARY` names a file, as it does in a step of a GitHub
Actions job, the failure also appends them to it as Markdown, which the
run shows on its summary page, naming the pull request's base,
`GITHUB_BASE_REF`. A pass appends nothing, and with the variable unset
no file is written.

The failure gives a command only where `refused_tail` finds the plain
case, and there it is `git rebase --signoff`, which signs off every
commit it replays as whoever runs it. In every other case it says how
each author signs off their own commits by hand. The rejected
alternative is a rebase whose `--exec` amends only the refused commits:
a shell test of which commits those are never read a commit as this
script does, the committer identity, merges and bots each making the
two disagree.

A subject and an address are the author's text, and a control character
in either could end the line that shows it and forge what follows, in
the log as in the summary. Each is printed with such characters escaped.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import re
import subprocess
import unicodedata

# the author addresses GitHub gives the bots' commits
BOTS = frozenset(
    {
        "49699333+dependabot[bot]@users.noreply.github.com",
        "66853113+pre-commit-ci[bot]@users.noreply.github.com",
        "209825114+claude[bot]@users.noreply.github.com",
    }
)

_ADDRESS = re.compile(r"<([^<>]+)>\s*$")
# an address a reader can type as it is shown: printable ASCII, not
# empty, with no space and no backslash, which `visible` writes escapes in
_PLAIN = re.compile(r"[!-\[\]-~]+")

FIX = (
    "Each commit above needs a Signed-off-by: trailer with the address"
    " shown, added by that commit's author."
)
MERGE = (
    "Only an administrator can merge the pull request until every commit above has one."
)


def _git(*args: str) -> str:
    r"""Return what git prints, run in the working directory.

    Decoded by hand, since text mode would turn a carriage return in a
    subject into a line break before `visible` could escape it. A byte
    that is not UTF-8 becomes a lone surrogate, which stays distinct from
    the `\xNN` escape `visible` prints for it.
    """
    ran = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        capture_output=True,
        check=True,
    )
    return ran.stdout.decode("utf-8", "surrogateescape")


def visible(text: str) -> str:
    r"""Return the text with each control character or line separator escaped.

    A byte that is not UTF-8 is shown as `\xNN`.
    """
    shown = []
    for char in text:
        if "\udc80" <= char <= "\udcff":
            shown.append(f"\\x{ord(char) - 0xDC00:02x}")
        elif unicodedata.category(char) in {"Cc", "Cf", "Cs", "Zl", "Zp"}:
            shown.append(char.encode("unicode_escape").decode("ascii"))
        else:
            shown.append(char)
    return "".join(shown)


def signs_off(author: str, trailers: str) -> bool:
    """Say whether a `Signed-off-by:` value names this author address."""
    for value in trailers.splitlines():
        found = _ADDRESS.search(value)
        if found and found[1].casefold() == author.casefold():
            return True
    return False


def _show(sha: str, field: str) -> str:
    """Return one field of a commit, as `git show --format` prints it."""
    return _git("show", "-s", f"--format={field}", sha)


def _trailers(sha: str) -> str:
    """Return the values of a commit's `Signed-off-by:` trailers."""
    return _show(sha, "%(trailers:key=Signed-off-by,valueonly)")


def refused_authors(revisions: str) -> list[tuple[str, str]]:
    """Return the sha and author address of each commit not signed off."""
    found = []
    for sha in _git("rev-list", "--no-merges", revisions).split():
        author = _show(sha, "%ae").strip()
        if author in BOTS:
            continue
        if not signs_off(author, _trailers(sha)):
            found.append((sha, author))
    return found


def line(sha: str, author: str) -> str:
    """Return the one line that names a refused commit."""
    subject = _show(sha, "%s").strip()
    return f"{sha[:12]} {visible(subject)}: no Signed-off-by: <{visible(author)}>"


def refused(revisions: str) -> list[str]:
    """Return a line per commit of the range that does not sign off."""
    return [line(sha, author) for sha, author in refused_authors(revisions)]


def _head(revisions: str) -> str | None:
    """Return the sha a range of the form `base..head` ends at, if one."""
    heads = [end for end in _git("rev-parse", revisions).split() if end[:1] != "^"]
    return heads[0] if len(heads) == 1 else None


def refused_tail(revisions: str, refused: list[str]) -> tuple[str, str] | None:
    """Return the address and start where `git rebase --signoff` is the fix.

    That is where the refused commits are the tail of the branch: walked
    back from the head, every commit is refused until the parent of the
    oldest of them, and no refused commit is elsewhere. The rebase starts
    at that parent and rewrites the refused commits alone, never a commit
    the check accepts, a merge or a bot's.

    The refused commits share one author address, compared exactly, so
    that `ann@…` and `ANN@…` are two, and it is `_PLAIN` and no bot's:
    whoever runs the rebase signs off as that address. Otherwise None.
    """
    if (sha := _head(revisions)) is None:
        return None
    tail = []
    while sha in refused:
        tail.append(sha)
        # a refused commit is no merge, so one with no parent is a root
        if not (parents := _show(sha, "%P").split()):
            return None
        (sha,) = parents
    if not tail or len(tail) != len(set(refused)):
        return None
    addresses = {_show(commit, "%ae").removesuffix("\n") for commit in tail}
    if len(addresses) != 1:
        return None
    (address,) = addresses
    bots = {bot.casefold() for bot in BOTS}
    if not _PLAIN.fullmatch(address) or address.casefold() in bots:
        return None
    return address, sha


def fork_point(revisions: str) -> str:
    """Return the sha where a range of the form `base..head` leaves its base.

    The commit is on the branch, so its author has it without fetching.
    Where the branch merged its base, it is the base commit last merged,
    so a rebase onto it replays the branch's own commits and none merged in.

    The rejected alternative is `origin/<base>`. In a clone of a fork,
    `origin` is the fork, as `gh repo fork` sets it, and the fork's copy
    of the base branch can be older than the commit the branch starts
    from: a rebase onto it replays the base's newer commits into the pull
    request, each with the contributor's trailer.
    """
    ends = _git("rev-parse", revisions).split()
    head = [end for end in ends if not end.startswith("^")]
    base = [end[1:] for end in ends if end.startswith("^")]
    return _git("merge-base", *head, *base).strip()


def commands(start: str) -> list[str]:
    """Return the commands that sign off the refused commits after `start`."""
    return [f"git rebase --signoff {start}", "git push --force-with-lease"]


def identity(address: str, start: str) -> str:
    """Return what the commands ask of the identity of whoever runs them."""
    return (
        "Run these from the branch. The trailer is written with your committer"
        " identity, so git config user.email, and GIT_COMMITTER_EMAIL where"
        f" you export it, must be {_span(address)}. The rebase starts at"
        f" {start}, the parent of the oldest commit refused, and rewrites the"
        " commits refused alone. The check runs again on the push."
    )


def by_hand(fork: str, authors: list[str], head: str | None) -> list[str]:
    """Return how each author signs off their own commits by hand.

    `--rebase-merges` keeps the branch's merges, which a plain `git rebase
    -i` drops with any change made in them alone. Recreated, a merge still
    loses such a change, as git's documentation of the option says, so the
    steps compare the result with `head`, the branch before the rebase,
    and bring back what differs. The restore's pathspec is `:/`, the top
    of the tree, which is what `git diff` reads from any directory.

    An empty address adds the step that corrects the author, since no
    trailer can name it. Another address that is not `_PLAIN` is named as
    getting no command, though its trailer, written as the address, is
    accepted.
    """
    steps = [
        (
            "Each author signs off their own commits and leaves the others as"
            f" they are: git rebase -i --rebase-merges {fork}, marking those"
            " commits edit, then at each stop git commit --amend --no-edit"
            " --signoff and git rebase --continue."
        ),
        (
            "The trailer is written with the committer identity, so at an"
            " author's stops git config user.email, and GIT_COMMITTER_EMAIL"
            " where exported, must be that author's address."
        ),
    ]
    if any(author and not _PLAIN.fullmatch(author) for author in authors):
        steps.append(
            "No command is printed for an address with a space, a backslash"
            " or a character outside printable ASCII."
        )
    if "" in authors:
        steps.append(
            "A commit with an empty author address cannot be signed off as it"
            " stands: at its stop, git commit --amend --no-edit --reset-author"
            " --signoff, with the author's own address as git config"
            " user.email."
        )
    if head:
        steps.append(
            f"Before git push --force-with-lease, git diff {head} HEAD prints"
            " nothing. Where it prints a change, a merge made it and the rebase"
            f" dropped it: git restore --source={head} --staged --worktree -- :/"
            " and git commit --signoff bring it back."
        )
    else:
        steps.append("Last, git push --force-with-lease.")
    return steps


def _ticks(text: str, least: int) -> str:
    """Return a backtick run longer than any in the text, and `least` long."""
    longest = max((len(run) for run in re.findall("`+", text)), default=0)
    return "`" * max(least, longest + 1)


def _fenced(language: str, lines: list[str]) -> list[str]:
    """Return the lines in a code block that no backtick run inside closes."""
    fence = _ticks("\n".join(lines), 3)
    return [f"{fence}{language}", *lines, fence]


def _span(text: str) -> str:
    """Return the text as a code span that no backtick run inside closes."""
    ticks = _ticks(text, 1)
    return f"{ticks} {text} {ticks}" if "`" in text else f"{ticks}{text}{ticks}"


def summary(
    lines: list[str], prose: list[str], fix: list[str], fork: str, base: str
) -> str:
    """Return the Markdown a failure adds to the run's summary.

    The lines go in a code block: a subject is the author's text, and an
    address in angle brackets would render as a link. `prose` is what the
    fix asks, and `fix` its commands, none where the fix is by hand.
    Outside a job of GitHub Actions, the link to `CONTRIBUTING.md` is this
    repository's.
    """
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repository = os.environ.get("GITHUB_REPOSITORY", "btclib-org/.github")
    named = _span(visible(base)) if base else "the base"
    return "\n".join(
        [
            "### Commits not signed off by their author",
            "",
            *_fenced("text", lines),
            "",
            FIX,
            "",
            *[text for s in prose for text in (s, "")],
            *([*_fenced("shell", fix), ""] if fix else []),
            (
                f"`{fork}` is the commit of {named} the branch starts from,"
                " or the last one it merged."
            ),
            MERGE,
            "",
            (
                "The trailer certifies the [Developer Certificate of Origin]"
                "(https://developercertificate.org/): that the author may"
                " contribute the commit under the project's license."
                f" [`CONTRIBUTING.md`]({server}/{repository}/blob/HEAD/"
                "CONTRIBUTING.md#pull-requests) has the rule."
            ),
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    """Read the range from the command line and check its commits."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("revisions", help="the range, as git rev-list reads it")
    args = parser.parse_args(argv)

    found = refused_authors(args.revisions)
    lines = [line(sha, author) for sha, author in found]
    for text in lines:
        print(f"::error::{text}")
    if lines:
        fork = fork_point(args.revisions)
        if plain := refused_tail(args.revisions, [sha for sha, _ in found]):
            address, start = plain
            prose, fix = [identity(address, start)], commands(start)
        else:
            authors = [author for _, author in found]
            prose, fix = by_hand(fork, authors, _head(args.revisions)), []
        for text in [FIX, *prose]:
            print(text)
        for command in fix:
            print(f"    {command}")
        print(MERGE)
        if path := os.environ.get("GITHUB_STEP_SUMMARY"):
            base = os.environ.get("GITHUB_BASE_REF", "")
            with pathlib.Path(path).open("a", encoding="utf-8") as out:
                out.write(summary(lines, prose, fix, fork, base))
        return 1
    print(f"every commit of {args.revisions} read is signed off by its author")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
