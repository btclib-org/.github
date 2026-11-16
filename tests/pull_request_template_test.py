# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 2's `PULL_REQUEST_TEMPLATE.md`, asked of every repository.

The section's directories bullet names it among what `.github/` holds
and the sentence under that bullet gives `.github/` to every tier;
section 16's checklist gives the file to a repository being set up. So
it is owed whatever a tree is written in, which is why the question here
carries no `tier` marker.

The path is the assertion and not only the file. GitHub reads a template
from more than one place in a tree, and the same section fixes `.github/`
with the alternative beside it, so a copy kept elsewhere is served to a
reader and is still a tree of a shape that section decides against.

Of what the file says, the comment it opens with is asked, and nothing
after it: section 2 gives that comment as an `html` block, which is
read where it stands and compared as a string. Below the comment, the
copy this repository carries names the commands of a tree whose gates
are its own, and says in itself that a repository whose commands differ
writes its own, so comparing the rest across the trees would be a
verbatim rule section 14 does not state.

The per-repository questions reach the network, and `conftest.py` marks
them `integration`. The question asked of this tree alone reaches
nothing, so the module carries no marker of its own.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import ORG, ROOT, by_hand, fenced, tracked

if TYPE_CHECKING:
    from pathlib import Path

TEMPLATE = ".github/PULL_REQUEST_TEMPLATE.md"

LISTING = f"git ls-files -- {TEMPLATE}"
"""How a reader asks a checkout whether the file is there."""

README = ROOT / "README.md"

RULE = "**`PULL_REQUEST_TEMPLATE.md` opens with the comment on sign-off"
"""How section 2's paragraph on the opening comment begins."""

OPEN = "<!--"

CLOSE = "-->"


def opening(text: str) -> str:
    """Return the comment a template opens with, through its first `-->`.

    :param text: the template.
    :returns: the comment, or the empty string where the file opens with
        none.
    """
    if not text.startswith(OPEN) or CLOSE not in text:
        return ""
    return text[: text.index(CLOSE) + len(CLOSE)]


def owed() -> str:
    """Return the comment section 2's block gives every tree.

    :returns: the block's text, without the line break `fenced` ends it
        with.
    :raises LookupError: where the section holds no such block, or one
        that is not a single comment.
    """
    block = fenced(README, RULE, "html").removesuffix("\n")
    if opening(block) != block:
        msg = f"{README.name}'s block under {RULE!r} is not one comment: {block!r}"
        raise LookupError(msg)
    return block


def test_a_repository_carries_a_pull_request_template(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """The file is tracked, at the path and under the name section 2 gives.

    `git ls-files` rather than the filesystem, so a copy left untracked
    in a checkout is not read as the repository's, and the pathspec is
    the whole path in the section's own spelling.

    What GitHub shows a reader does not answer it: a tree with no
    template of its own is shown this repository's, which is in no tree
    of the repository being asked about.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    assert tracked(trees[repository], TEMPLATE), (
        f"section 2 gives every tree {TEMPLATE} and this one does not track"
        " it; " + by_hand(repository, LISTING)
    )


def test_a_pull_request_template_opens_with_the_sign_off_comment(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """The template opens with section 2's comment, the same text.

    A tree tracking no template reads as one opening with nothing, the
    question above being where its absence is the finding.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    comment = owed()
    root = trees[repository]
    held = (
        (root / TEMPLATE).read_text(encoding="utf-8") if tracked(root, TEMPLATE) else ""
    )
    head = f"head -n {len(comment.splitlines())} {TEMPLATE}"
    assert opening(held) == comment, (
        f"{repository}: {TEMPLATE} does not open with the comment on sign-off"
        " section 2 of README.md gives, the same text; " + by_hand(repository, head)
    )


def test_this_template_opens_with_the_comment_section_2_gives() -> None:
    """This tree's template opens with section 2's comment, offline.

    The per-repository question asks the same of this tree, and only
    with `BTCLIB_INTEGRATION`; this one holds the rule and the template
    together on every run.
    """
    held = opening((ROOT / TEMPLATE).read_text(encoding="utf-8"))
    assert held == owed(), (
        f"{TEMPLATE} does not open with the comment section 2 of"
        f" {ORG}/.github's README.md gives, the same text"
    )
