# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 2's `## Contributing` paragraph, asked of every `README.md`.

The paragraph is read out of the section, for the reason `fenced` gives:
a transcription is the copy that goes stale. A `README.md` is read with
its fenced blocks dropped, so that the standard's own example of the
paragraph does not answer for the section the standard owes. The
heading is matched as a line, and the paragraph under it with its line
breaks ignored, since markdown renders a paragraph the same however it
wraps.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from . import ORG, ROOT, SELF, by_hand, fenced
from .links_test import FENCE

if TYPE_CHECKING:
    from pathlib import Path

OPENING = "has a `## Contributing` section opening"
"""The line of section 2 that opens the rule and precedes the block."""

LINK = "./CONTRIBUTING.md"
"""The paragraph's link, relative to the root of the tree."""

ABSOLUTE = f"https://github.com/{ORG}/{SELF}/blob/main/CONTRIBUTING.md"
"""The same target from `profile/README.md`.

The organization's page resolves a relative link against `profile/`,
where no `CONTRIBUTING.md` is.
"""

SUPPORTED = re.compile(r"actively\s+supported\s+by")
"""Words of section 2's supported-by line, which the paragraph is above."""

PAGE = ROOT / "profile" / "README.md"

ASKED = "grep -n -A 6 '^## Contributing' README.md"
"""How a reader looks at the section in a checkout."""


def paragraph() -> str:
    """Read the block section 2 gives, its heading included.

    :returns: the block's text.
    """
    return fenced(ROOT / "README.md", OPENING, "markdown")


def flat(text: str) -> str:
    """Join a text's words with single spaces.

    :param text: the markdown.
    :returns: its words, one space apart.
    """
    return " ".join(text.split())


def unmet(readme: str, block: str) -> str | None:
    """Say how a `README.md` falls short of the rule, if it does.

    :param readme: the file's text.
    :param block: the paragraph, its heading on the first line.
    :returns: what is wrong, or `None` where nothing is.
    """
    heading, _, body = block.partition("\n")
    text = FENCE.sub("", readme)
    found = None
    offset = 0
    for line in text.splitlines(keepends=True):
        offset += len(line)
        if line.rstrip("\n") == heading and flat(text[offset:]).startswith(flat(body)):
            found = offset
            break
    if found is None:
        return "no `## Contributing` section opens with section 2's paragraph"
    supported = SUPPORTED.search(text)
    if supported is not None and supported.start() < found:
        return "the paragraph is below the supported-by line"
    return None


def test_a_readme_opens_its_contributing_section_with_the_paragraph(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """The repository's `README.md` carries section 2's paragraph.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    readme = (trees[repository] / "README.md").read_text(encoding="utf-8")
    problem = unmet(readme, paragraph())
    assert problem is None, f"{problem}; " + by_hand(repository, ASKED)


def test_the_organization_page_carries_the_paragraph() -> None:
    """`profile/README.md` carries it, its link made absolute."""
    block = paragraph()
    assert LINK in block, f"section 2's paragraph no longer links {LINK}"
    problem = unmet(PAGE.read_text(encoding="utf-8"), block.replace(LINK, ABSOLUTE))
    assert problem is None, f"profile/README.md: {problem}"


@pytest.mark.parametrize(
    ("shape", "expected"),
    [
        pytest.param("{block}\n\n---\n\n{supported}\n", None, id="above"),
        pytest.param("{rewrapped}\n", None, id="rewrapped"),
        pytest.param("{supported}\n\n{block}\n", "below", id="below"),
        pytest.param("```markdown\n{block}```\n", "no ", id="fenced"),
        pytest.param("#{block}\n", "no ", id="lower-heading"),
        pytest.param("{split}\n", "no ", id="split-heading"),
        pytest.param("# Title\n", "no ", id="absent"),
    ],
)
def test_the_reader_tells_the_shapes_apart(shape: str, expected: str | None) -> None:
    """`unmet` accepts the rule's shapes and names each one it refuses.

    :param shape: a `README.md`, the block and the supported-by line as
        placeholders.
    :param expected: words of the answer, `None` where it accepts.
    """
    block = paragraph()
    heading, _, body = block.partition("\n")
    readme = shape.format(
        block=block,
        rewrapped=heading + "\n" + body.replace(" ", "\n"),
        split=block.replace(" ", "\n", 1),
        supported="The organization is actively supported by its sponsors.",
    )
    problem = unmet(readme, block)
    if expected is None:
        assert problem is None
    else:
        assert problem is not None
        assert expected in problem
