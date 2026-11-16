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
after it: section 2 gives every tree this repository's comment. Below
it, the copy this repository carries names the commands of a tree whose
gates are its own, and says in itself that a repository whose commands
differ writes its own, so comparing the rest across the trees would be a
verbatim rule section 14 does not state.

The per-repository questions reach the network, and `conftest.py` marks
them `integration`. The questions asked of this tree alone reach
nothing, so the module carries no marker of its own.
"""

from __future__ import annotations

import itertools
import re
from typing import TYPE_CHECKING

import pytest

from . import ORG, ROOT, SELF, by_hand, sole, tracked

if TYPE_CHECKING:
    from pathlib import Path

TEMPLATE = ".github/PULL_REQUEST_TEMPLATE.md"

LISTING = f"git ls-files -- {TEMPLATE}"
"""How a reader asks a checkout whether the file is there."""

README = ROOT / "README.md"

RULE = "**`PULL_REQUEST_TEMPLATE.md` opens with the comment on sign-off"
"""How section 2's paragraph on the opening comment begins."""

NAMED = ("git commit -s", "CONTRIBUTING.md's *Pull requests*")
"""What that paragraph says the comment gives the author: the command,
and the document and section it points to, both without backticks."""

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


PART = "A-Za-z0-9._/-"
"""What can stand inside a path or a word, and so cannot border a name."""


def unnamed(text: str) -> list[str]:
    """List what of `NAMED` a text does not name.

    The text is read without its backticks, so that README.md's
    `` `CONTRIBUTING.md`'s `` and the comment's plain spelling read
    alike; with a line break after a hyphen dropped, since a word is not
    wrapped at its own hyphen; and with every other line break as a
    space, so a phrase it wraps is found. A name counts whole only: no
    character of `PART` before it, and none after it but a full stop,
    so `NOT-CONTRIBUTING.md` and `OTHER/CONTRIBUTING.md` do not name
    `CONTRIBUTING.md`, and a sentence may end on a name.

    :param text: the text.
    :returns: the entries of `NAMED` it lacks.
    """
    joined = re.sub(r"-[ \t]*\n\s*", "-", text.replace("`", ""))
    words = " ".join(joined.split())
    after = PART.replace(".", "")
    return [
        name
        for name in NAMED
        if not re.search(rf"(?<![{PART}]){re.escape(name)}(?![{after}])", words)
    ]


def paragraph() -> str:
    """Return section 2's paragraph on the opening comment.

    :returns: the lines from the one `RULE` opens to the next blank line,
        joined by line breaks.
    """
    lines = README.read_text(encoding="utf-8").splitlines()
    return "\n".join(itertools.takewhile(bool, lines[sole(README, lines, RULE) :]))


def owed() -> str:
    """Return this repository's opening comment, the one every tree owes.

    A comment lacking any of `NAMED` is not the comment on sign-off: a
    template that opened with markdownlint's comment would otherwise be
    what every tree is compared with. `LookupError` and not an
    assertion, so that the backlog's expected failures do not excuse
    it.

    :returns: the comment.
    :raises LookupError: where the comment lacks one of them.
    """
    comment = opening((ROOT / TEMPLATE).read_text(encoding="utf-8"))
    if missing := unnamed(comment):
        msg = f"{TEMPLATE} opens with no comment naming {missing}: {comment!r}"
        raise LookupError(msg)
    return comment


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
    """The template opens with this repository's comment, the same text.

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
        f" {ORG}/{SELF}'s opens with, the same text through its {CLOSE}; "
        + by_hand(repository, head)
    )


def test_this_template_opens_with_the_comment_section_2_describes() -> None:
    """This tree's template opens with a comment naming what section 2 says.

    Each of `NAMED` is in the paragraph `paragraph()` reads and in the
    comment. Read offline, so that the rule and the comment every tree is
    compared with cannot part on a run without `BTCLIB_INTEGRATION`.
    """
    comment = opening((ROOT / TEMPLATE).read_text(encoding="utf-8"))
    unstated = unnamed(paragraph())
    missing = unnamed(comment)
    assert not unstated, f"section 2's paragraph on {TEMPLATE} does not name {unstated}"
    assert not missing, f"{TEMPLATE} opens with no comment naming {missing}"


ELSEWHERE = [
    pytest.param("OTHER.md", id="another document"),
    pytest.param("NOT-CONTRIBUTING.md", id="a longer name"),
    pytest.param("OTHER/CONTRIBUTING.md", id="another directory"),
    pytest.param("NOT-\nCONTRIBUTING.md", id="a longer name wrapped at its hyphen"),
    pytest.param("NOT-`CONTRIBUTING.md`", id="a longer name around backticks"),
]
"""What `CONTRIBUTING.md` is rewritten to, each naming another document."""


@pytest.mark.parametrize("rewritten", ELSEWHERE)
@pytest.mark.parametrize("source", ["comment", "paragraph"])
def test_a_text_pointing_elsewhere_does_not_name_the_section(
    rewritten: str,
    source: str,
) -> None:
    """`unnamed()` reads the rule and the comment alike, and whole names.

    :param rewritten: what the document's name becomes.
    :param source: which of the two texts is rewritten.
    """
    text = (
        opening((ROOT / TEMPLATE).read_text(encoding="utf-8"))
        if source == "comment"
        else paragraph()
    )
    assert not unnamed(text)
    assert unnamed(text.replace("CONTRIBUTING.md", rewritten, 1)) == [NAMED[1]]


@pytest.mark.parametrize(
    ("written", "rewritten", "lacked"),
    [
        *(
            pytest.param("CONTRIBUTING.md", *case.values, NAMED[1], id=case.id)
            for case in ELSEWHERE
        ),
        pytest.param("git commit -s", "git commit", NAMED[0], id="no sign-off flag"),
    ],
)
def test_a_comment_pointing_elsewhere_is_not_the_one_owed(
    written: str,
    rewritten: str,
    lacked: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`owed()` refuses this tree's comment with one of `NAMED` changed.

    Run on a copy of the template under a stand-in root, so that a
    comment pointing to another document is refused rather than made
    what every tree is compared with.

    :param written: the words of this template's comment that change.
    :param rewritten: what they become.
    :param lacked: the entry of `NAMED` the change takes away.
    :param tmp_path: the stand-in root.
    :param monkeypatch: what puts the stand-in in place of `ROOT`.
    """
    text = (ROOT / TEMPLATE).read_text(encoding="utf-8")
    comment = opening(text)
    assert written in comment
    copy = tmp_path / TEMPLATE
    copy.parent.mkdir(parents=True)
    copy.write_text(text.replace(written, rewritten, 1), encoding="utf-8")
    monkeypatch.setattr(f"{__name__}.ROOT", tmp_path)
    with pytest.raises(LookupError) as refused:
        owed()
    assert repr(lacked) in str(refused.value)
