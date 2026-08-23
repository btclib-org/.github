# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The `links` workflow asks lychee a question its flags let it answer.

`links.yml` gates nothing, so its whole value is that a red run means a
destination has moved: a flag that makes a live host read as dead, or
that promises a cache no step keeps, costs an investigation and buys
nothing. Both are read from the action's `args:` rather than grepped,
the arguments being one folded string the grep would have to reassemble.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from . import by_hand
from .workflows_test import steps

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

    Skipped where there is no `links.yml`, that being
    btclib-org/.github#107's question rather than this module's; an
    error where the file exists and no step calls the action, since the
    file is then not what its name says.

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
