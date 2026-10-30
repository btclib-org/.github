# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What `SECURITY.md`'s *Security review* section names, in every tree.

Section 2 of README.md, in its *Root files*, says what the section
holds and what a section written before any review says instead. This
reads the section of every tree that carries one for those items.

`missing` asks for each item by its shape -- a date, a link, a sha --
and takes section 2's one sentence for a section before any review; the
tests that reach nothing run it on the shapes the trees hold.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from . import ORG, by_hand

if TYPE_CHECKING:
    from pathlib import Path

# the line that opens the section, as every tree carrying it writes it
HEADING = "## Security review"

# how a section written before any review says so, in section 2's words
NONE = "No security review has been done"

DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
PROFILE = re.compile(r"\]\(https://github\.com/[A-Za-z0-9-]+\)")
COMMIT = re.compile(r"`([0-9a-f]{7,40})`")


def section(text: str) -> str | None:
    """Return the *Security review* section of a `SECURITY.md`.

    :param text: the whole file.
    :returns: the lines from the heading to the next heading of any
        level, or `None` where the file has no such heading.
    """
    lines = text.splitlines()
    if HEADING not in lines:
        return None
    start = lines.index(HEADING) + 1
    end = next(
        (i for i in range(start, len(lines)) if lines[i].startswith("#")),
        len(lines),
    )
    return "\n".join(lines[start:end])


def missing(body: str, repository: str) -> list[str]:
    """Say which of section 2's items a *Security review* section lacks.

    The compare link is read for the commit it starts from, and that
    sha and the commit the section names have to abbreviate each other:
    a link from any other commit compares the wrong tree with `main`.
    The review issue may be in any repository of the organization.
    Section 2's words for a section before any review are matched across
    line breaks, so that a refilled paragraph still reads as one.

    :param body: the section, its heading excluded.
    :param repository: the tree it is in, which its links name.
    :returns: the items not found, empty where every one is.
    """
    if NONE in " ".join(body.split()):
        return []
    org = rf"https://github\.com/{ORG}"
    base = rf"{org}/{re.escape(repository)}"
    links = re.findall(rf"{base}/compare/([0-9a-f]{{7,40}})\.\.\.main\b", body)
    named = COMMIT.findall(body)
    out = [
        item
        for item, found in (
            ("the date", DATE.search(body)),
            ("the reviewer's GitHub profile", PROFILE.search(body)),
            ("the review issue", re.search(rf"{org}/[\w.-]+/issues/\d+\b", body)),
            ("the reviewed commit", named),
            ("a compare link from that commit to main", links),
        )
        if not found
    ]
    if (
        links
        and named
        and not any(
            link.startswith(sha) or sha.startswith(link)
            for link in links
            for sha in named
        )
    ):
        out.append(f"a compare link from {named} rather than from {links}")
    return out


def test_a_security_review_section_names_the_review(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 2's items are in the section, where a tree carries one.

    A tree without the section, or without a `SECURITY.md`, is skipped
    with the reason: section 2 says what the section holds, and
    `security_test.py` is what asks a publisher for the file.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    path = trees[repository] / "SECURITY.md"
    if not path.is_file():
        pytest.skip(f"{repository} has no SECURITY.md")
    body = section(path.read_text(encoding="utf-8"))
    if body is None:
        pytest.skip(f"{repository}'s SECURITY.md has no {HEADING!r}")
    lacking = missing(body, repository)
    assert not lacking, (
        f"SECURITY.md's *Security review* section lacks {lacking}; "
        + by_hand(repository, "sed -n '/^## Security review$/,/^#/p' SECURITY.md")
    )


# btclib's section as PR btclib-org/btclib#2867 writes it, every item in
REVIEWED = """
The latest security review is dated 2026-09-30.
[pmazzocchi](https://github.com/pmazzocchi) did it against the
[assurance case](./ASSURANCE_CASE.md), and
[issue 2450](https://github.com/btclib-org/btclib/issues/2450) records it.

The review's scope is the tree at commit `341b06139cd1`.
[What changed since](https://github.com/btclib-org/btclib/compare/341b06139cd1af4df9fb1a7e0d3eb7c7fe5d7028...main)
is that commit's comparison with `main`.
"""


def test_the_reading_finds_every_item_in_a_reviewed_section() -> None:
    """A section in the shape the trees converge on lacks nothing."""
    text = f"# Security policy\n\n{HEADING}\n{REVIEWED}\n## Next\n\nmore\n"
    body = section(text)
    assert body is not None
    assert "## Next" not in body
    assert missing(body, "btclib") == []


def test_the_reading_names_each_item_a_section_lacks() -> None:
    """Each item taken out is reported, so no item is read as found unseen.

    The shape without the last paragraph is the one the trees hold
    before their compare link lands.
    """
    before_the_link = REVIEWED.split("\n\nThe review's scope", maxsplit=1)[0]
    assert missing(before_the_link, "btclib") == [
        "the reviewed commit",
        "a compare link from that commit to main",
    ]
    for item, removed in (
        ("the date", "2026-09-30"),
        ("the reviewer's GitHub profile", "(https://github.com/pmazzocchi)"),
        ("the review issue", "https://github.com/btclib-org/btclib/issues/2450"),
    ):
        assert missing(REVIEWED.replace(removed, ""), "btclib") == [item]
    assert missing(REVIEWED, "ecc") == ["a compare link from that commit to main"]
    outside = REVIEWED.replace(
        "github.com/btclib-org/btclib/issues", "github.com/x/y/issues"
    )
    assert missing(outside, "btclib") == ["the review issue"]
    other = REVIEWED.replace("`341b06139cd1`", "`0123456789ab`")
    wrong = (
        "a compare link from ['0123456789ab'] rather than from"
        " ['341b06139cd1af4df9fb1a7e0d3eb7c7fe5d7028']"
    )
    assert missing(other, "btclib") == [wrong]
    short = REVIEWED.replace(
        "341b06139cd1af4df9fb1a7e0d3eb7c7fe5d7028...", "341b061..."
    )
    assert missing(short, "btclib") == []
    six = REVIEWED.replace("341b06139cd1af4df9fb1a7e0d3eb7c7fe5d7028...", "341b06...")
    assert missing(six, "btclib") == ["a compare link from that commit to main"]


def test_the_review_issue_may_be_in_another_repository() -> None:
    """An issue of the organization recording a review of several trees."""
    elsewhere = REVIEWED.replace(
        "github.com/btclib-org/btclib/issues/2450",
        "github.com/btclib-org/.github/issues/1362",
    )
    assert missing(elsewhere, "btclib") == []


def test_a_section_before_any_review_owes_nothing() -> None:
    """base58-bech32's section, written before any review, is read as such."""
    body = (
        "\nNo security review has been done yet. The\n"
        "[assurance case](./ASSURANCE_CASE.md) is what one is done against.\n"
    )
    assert missing(body, "base58-bech32") == []
    refilled = "\nNo security\nreview has  been done yet.\n"
    assert missing(refilled, "base58-bech32") == []
    assert section("# Security policy\n\n## Reporting\n") is None
