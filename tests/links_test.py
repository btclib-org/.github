# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The `links` workflow asks lychee a question its flags let it answer.

`links.yml` gates nothing, so its whole value is that a red run means a
destination has moved: a flag that makes a live host read as dead, or
that promises a cache no step keeps, costs an investigation and buys
nothing, and a question the arguments never ask leaves a move
unreported. The flags are read from the action's `args:` rather than
grepped, the arguments being one folded string the grep would have to
reassemble.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest

from . import ORG, SELF, by_hand, tracked
from .workflows_test import steps

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

ACTION = "lycheeverse/lychee-action"

SUCCESS = set(range(100, 104)) | set(range(200, 300))
"""lychee's own default for `--accept`: `100..=103,200..=299`.

Read back with `lychee --help | sed -n '/--accept/,/default/p' | tail -1`.
The flag replaces the range rather than adding to it, so a list that
names fewer turns every other success into an error.
"""

RANGE = re.compile(r"^(\d+)(?:\.\.=(\d+))?$")
"""One entry of an `--accept` list: a code, or an inclusive range."""


def lychee(repository: str, trees: dict[str, Path]) -> tuple[dict[str, Any], Path]:
    """Find the lychee step of a repository's `links.yml`, with the file.

    Skipped where there is no `links.yml`: section 10's record gives the
    workflow to every repository, so a tree without one is a gap in that
    tree, reported by `grid_test.py` against the record rather than asked
    here. An error where the file exists and no step calls the action,
    since the file is then not what its name says.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the step mapping and the workflow file.
    :raises LookupError: where `links.yml` calls the action no times or
        more than once.
    """
    workflow = trees[repository] / ".github" / "workflows" / "links.yml"
    if not workflow.is_file():
        pytest.skip(f"{repository} has no links.yml")
    found = [
        step for step in steps(workflow) if step.get("uses", "").startswith(ACTION)
    ]
    if len(found) != 1:
        msg = f"{repository}/links.yml calls {ACTION} {len(found)} times"
        raise LookupError(msg)
    return found[0], workflow


def arguments(step: dict[str, Any]) -> list[str]:
    """Split the action's `args:` input into words.

    :param step: the lychee step.
    :returns: the words, empty where the input is not given.
    """
    return str(step.get("with", {}).get("args", "")).split()


def accepted(words: list[str]) -> set[int]:
    """Read the status codes an argument list makes lychee accept.

    Both spellings clap takes, `--accept <list>` and `--accept=<list>`:
    a list the second way is one word, and reading only the first would
    take it for the default and pass a list that drops half of it.

    :param words: the action's arguments.
    :returns: the codes, lychee's default where `--accept` is not passed.
    :raises ValueError: where an entry is neither a code nor a range.
    """
    given = None
    for index, word in enumerate(words):
        if word == "--accept":
            given = words[index + 1]
        elif word.startswith("--accept="):
            given = word.removeprefix("--accept=")
    if given is None:
        return set(SUCCESS)
    out: set[int] = set()
    for entry in given.split(","):
        found = RANGE.match(entry)
        if not found:
            msg = f"--accept entry {entry!r} is neither a code nor a range"
            raise ValueError(msg)
        low = int(found.group(1))
        high = int(found.group(2) or low)
        out.update(range(low, high + 1))
    return out


def ranges(codes: list[int]) -> list[str]:
    """Write a sorted list of codes the way `--accept` spells them.

    :param codes: the codes, sorted.
    :returns: each run of consecutive codes as `low..=high`, or alone.
    """
    out: list[str] = []
    start = previous = None
    for code in [*codes, None]:
        if start is not None and previous is not None and code != previous + 1:
            out.append(str(start) if start == previous else f"{start}..={previous}")
            start = None
        if start is None:
            start = code
        previous = code
    return out


def test_lychee_accepts_every_success_code(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """An `--accept` list covers what lychee would accept unasked.

    A list may add to the default -- `429` is the one worth adding, a
    rate limit being an answer from a host that is alive -- and may not
    take from it: a host that starts answering `204` to a HEAD turns a
    live link into a reported dead one, without anybody touching the
    tree.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    step, _ = lychee(repository, trees)
    lost = sorted(SUCCESS - accepted(arguments(step)))
    assert not lost, (
        f"success codes --accept turns into errors: {ranges(lost)}; "
        + by_hand(repository, "grep -o -- '--accept [^ ]*' .github/workflows/links.yml")
    )


def test_lychee_checks_a_link_into_a_heading(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """`--include-fragments` is passed, so an anchor is a link too.

    A fragment is checked only when asked for, and the forge serves the
    page whether or not the fragment names a heading on it -- so a
    heading renamed in one tree breaks the links into it with nothing
    red in that tree. The run that would notice is the one over the
    file holding the link, which is why every tree passes the flag and
    not only the tree whose headings are cited most.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    step, _ = lychee(repository, trees)
    assert "--include-fragments" in arguments(step), (
        "lychee checks a fragment only when asked, and a link into "
        "another tree's heading is checked by this tree's run alone; "
        + by_hand(
            repository,
            "grep -c include-fragments .github/workflows/links.yml",
        )
    )


def test_a_lychee_cache_is_kept_between_runs(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """`--cache` is passed only where a step keeps `.lycheecache`.

    A workflow run starts from a fresh workspace, so a cache lychee
    writes at the end of one run is read by the next only if a step
    restores it; without one the flag decides nothing, and a comment
    crediting it with absorbing a throttling host describes a mechanism
    that is not there.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    step, workflow = lychee(repository, trees)
    if "--cache" not in arguments(step):
        return
    kept = any(
        other.get("uses", "").startswith("actions/cache") for other in steps(workflow)
    )
    assert kept, (
        "--cache is passed and no step restores or saves .lycheecache; "
        + by_hand(
            repository,
            "grep -c 'actions/cache\\|lycheecache' .github/workflows/links.yml",
        )
    )


FENCE = re.compile(r"^```.*?^```\n?", re.DOTALL | re.MULTILINE)
"""A fenced code block, so its own `#` comments are not read as headings.

README.md's own `# 38` (a shell comment inside a `gh api` example) and
two more comment lines are exactly this shape: not stripped, they read
as headings GitHub never renders, and `anchors()` would answer three
ids too many.
"""

HEADING = re.compile(r"^#{1,6} (.+)$", re.MULTILINE)
"""One heading of a markdown file, its own text after the `#`s."""

ROOT_LINK = re.compile(rf"github\.com/{re.escape(ORG)}/{re.escape(SELF)}#([\w-]+)")
"""A link into this repository by anchor, the root shape lychee cannot
check once its step holds a token (btclib-org/.github#630): the API
answers that the repository exists, and lychee takes that for the
anchor. This asks the same question offline, against this file's own
headings.
"""


def slug(heading: str) -> str:
    """Render a heading's text the way GitHub's own anchor does.

    Lowercase, spaces to hyphens, everything but a word character, a
    space or a hyphen already in the heading dropped -- which is what
    strips a heading's backticks along with its punctuation, GitHub
    slugging the rendered text rather than the markdown that produced
    it.

    :param heading: the heading's text, markdown and all.
    :returns: the anchor GitHub renders for it.
    """
    return re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "", heading.lower()).strip())


def anchors(markdown: str) -> set[str]:
    """Read every heading of a file as the anchors GitHub gives them.

    A repeated slug is suffixed `-1`, `-2` and so on, in heading order,
    which is GitHub's own rule for a duplicate; README.md repeats none
    today, but a link resolving is a claim about GitHub's rendering and
    not only about this file's headings being distinct.

    :param markdown: the file's text.
    :returns: every anchor the file answers to.
    """
    seen: dict[str, int] = {}
    out: set[str] = set()
    for heading in HEADING.findall(FENCE.sub("", markdown)):
        base = slug(heading)
        count = seen.get(base, 0)
        seen[base] = count + 1
        out.add(base if count == 0 else f"{base}-{count}")
    return out


def test_slug_matches_three_headings_already_linked_by_anchor() -> None:
    """GitHub's own rendering, read off three anchors already in the tree.

    `tests/__init__.py`'s own docstring mentions `./README.md#8-coverage-at-100`
    as an example anchor rather than a link, `SECURITY.md` links
    `#2-the-tree` and `CODE_OF_CONDUCT.md` links
    `#14-copied-verbatim-and-decided-per-repository` -- three anchors
    already resolving on GitHub, against the headings they name.
    """
    known = {
        "8. Coverage at 100%": "8-coverage-at-100",
        "2. The tree": "2-the-tree",
        "14. Copied verbatim, and decided per repository": (
            "14-copied-verbatim-and-decided-per-repository"
        ),
    }
    wrong = {
        heading: slug(heading)
        for heading, want in known.items()
        if slug(heading) != want
    }
    assert not wrong, f"slug disagrees with a known anchor {known}: {wrong}"


def test_a_root_link_into_this_files_heading_resolves(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """A `github.com/<org>/.github#<fragment>` link names a real heading.

    This is the shape *A `github.com/<owner>/<repo>#heading` link is
    unchecked by this flag* in section 10 names as the one lychee cannot
    check once its step holds a token, so the check is made here,
    offline, against this file's own headings rather than against the
    forge.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    targets = anchors((trees[SELF] / "README.md").read_text(encoding="utf-8"))
    root = trees[repository]
    broken = sorted(
        f"{path}: #{fragment}"
        for path in tracked(root, "*.md")
        for fragment in ROOT_LINK.findall((root / path).read_text(encoding="utf-8"))
        if fragment not in targets
    )
    assert not broken, (
        f"links no heading of README.md answers to: {broken}; "
        + by_hand(repository, f"grep -rn 'github.com/{ORG}/{SELF}#' -- '*.md'")
    )
