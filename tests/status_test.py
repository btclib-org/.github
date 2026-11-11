# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 2's `## Status` section, asked of every `README.md`.

Section 2 puts the badges of its third group, the gates and the
sentinels, in a `## Status` section, the last `## ` section and above
the supported-by line, and every other badge at the head. A badge is
told apart by its image, the address section 2 gives each one, and not
by its alt text. A comment directly above the head's first badge, or
above the first badge of `## Status`, is one line. A `README.md` is read
with its fenced blocks dropped, so that an example in one does not
answer for the file. Which badges a tree owes, their order inside a
group, and whether a comment restates section 2 are section 15's audit
and a reader's, and not asked here.
"""

from __future__ import annotations

import itertools
import re
from typing import TYPE_CHECKING

import pytest

from . import by_hand
from .contributing_test import SUPPORTED
from .links_test import FENCE

if TYPE_CHECKING:
    from pathlib import Path

BADGE = re.compile(r"\[!\[[^\]]*\]\(([^)\s]+)[^)]*\)\]\(")
"""A badge: an image inside a link, its image's address captured."""

STATUS = re.compile(
    r"/actions/workflows/[^/]+/badge\.svg"
    r"|results\.pre-commit\.ci/badge/"
    r"|readthedocs\.org/projects/[^/]+/badge"
    r"|api\.scorecard\.dev/projects/"
)
"""The images of section 2's third group, as that section gives them.

pre-commit.ci's, a workflow-run badge for each workflow, Read the
Docs', and the Scorecard's score, which is `scorecard`'s badge in place
of a workflow-run one.
"""

HEADING = "## Status"

SECTION = re.compile(r"^## .*$", re.MULTILINE)

ASKED = r"grep -n -E '^## |\[!\[|actively supported' README.md"
"""How a reader looks at the headings and the badges in a checkout."""


def comment(lines: list[str], row: int) -> int:
    """Count the lines of the HTML comment directly above a line.

    :param lines: the file's lines.
    :param row: the index of the line.
    :returns: the comment's lines, `0` where the line above ends none.
    """
    if row == 0 or not lines[row - 1].rstrip().endswith("-->"):
        return 0
    first = row - 1
    while first > 0 and "<!--" not in lines[first]:
        first -= 1
    return row - first


def long_comments(text: str, start: int | None) -> list[str]:
    """Name each row whose comment runs over more than one line.

    :param text: the file's text, its fenced blocks dropped.
    :param start: where `## Status` begins, `None` without one.
    :returns: the rows, `the head` or `## Status`, and their comments' lines.
    """
    lines = text.splitlines()
    offsets = list(itertools.accumulate((len(line) + 1 for line in lines), initial=0))
    places: dict[str, int] = {}
    for row, line in enumerate(lines):
        if not BADGE.search(line):
            continue
        place = HEADING if start is not None and offsets[row] > start else "the head"
        places.setdefault(place, row)
    return [
        f"the comment above the badges of {place} runs over {length} lines"
        for place, row in places.items()
        if (length := comment(lines, row)) > 1
    ]


def unmet(readme: str) -> list[str]:
    """Say how a `README.md` falls short of the rule, if it does.

    :param readme: the file's text.
    :returns: what is wrong, empty where nothing is.
    """
    text = FENCE.sub("", readme)
    badges = [(found.start(), found.group(1)) for found in BADGE.finditer(text)]
    status = [(at, image) for at, image in badges if STATUS.search(image)]
    headings = [(found.start(), found.group(0)) for found in SECTION.finditer(text)]
    last = headings[-1] if headings else None
    start = last[0] if last is not None and last[1] == HEADING else None
    problems = long_comments(text, start)
    if not status:
        return problems
    if start is None:
        return [f"no `{HEADING}` section is the last `## ` section", *problems]
    if above := [image for at, image in status if at < start]:
        problems.append(f"badges of section 2's third group above it: {above}")
    if below := [
        image for at, image in badges if at > start and not STATUS.search(image)
    ]:
        problems.append(f"badges of the head under it: {below}")
    if (supported := SUPPORTED.search(text)) is not None and supported.start() < start:
        problems.append("it is below the supported-by line")
    return problems


def test_a_readme_keeps_its_gates_and_sentinels_in_its_status_section(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """The repository's `README.md` puts its badges where section 2 says.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    readme = (trees[repository] / "README.md").read_text(encoding="utf-8")
    problems = unmet(readme)
    assert not problems, f"{problems}; {by_hand(repository, ASKED)}"


HEAD = "[![PyPI version](https://img.shields.io/pypi/v/x.svg)](https://pypi.org/x)"
GATE = (
    "[![lint workflow status]"
    "(https://github.com/o/x/actions/workflows/lint.yml/badge.svg?branch=main)]"
    "(https://github.com/o/x/actions/workflows/lint.yml?query=branch%3Amain)"
)
SUPPORT = "The btclib organization is actively supported by its sponsors."


@pytest.mark.parametrize(
    ("shape", "expected"),
    [
        pytest.param(
            "# x\n\n{head}\n\n## Use\n\n## Status\n\n{gate}\n\n---\n\n{support}\n",
            None,
            id="kept",
        ),
        pytest.param("# x\n\n{head}\n\n## Use\n", None, id="no-gate"),
        pytest.param(
            "# x\n\n{gate}\n\n## Status\n\n{gate}\n", "third group above", id="head"
        ),
        pytest.param(
            "# x\n\n## Status\n\n{gate}\n\n## Use\n", "last `## `", id="not-last"
        ),
        pytest.param("# x\n\n{gate}\n", "last `## `", id="absent"),
        pytest.param(
            "# x\n\n## Status\n\n{gate}\n{head}\n", "of the head under", id="head-below"
        ),
        pytest.param(
            "# x\n\n{support}\n\n## Status\n\n{gate}\n", "supported-by", id="supported"
        ),
        pytest.param(
            "# x\n\n```markdown\n{gate}\n```\n\n## Status\n\n{gate}\n",
            None,
            id="fenced",
        ),
        pytest.param(
            "# x\n\n<!-- one -->\n{head}\n\n## Status\n\n<!-- one -->\n{gate}\n",
            None,
            id="one-line-comments",
        ),
        pytest.param(
            "# x\n\n<!-- one\ntwo -->\n{head}\n\n## Status\n\n{gate}\n",
            "head runs over 2 lines",
            id="long-comment",
        ),
    ],
)
def test_the_reader_tells_the_shapes_apart(shape: str, expected: str | None) -> None:
    """`unmet` accepts the rule's shapes and names each one it refuses.

    :param shape: a `README.md`, its badges and supported-by line as
        placeholders.
    :param expected: words of the answer, `None` where it accepts.
    """
    problems = unmet(shape.format(head=HEAD, gate=GATE, support=SUPPORT))
    if expected is None:
        assert not problems
    else:
        assert problems
        assert expected in " ".join(problems)
