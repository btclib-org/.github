# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for `workflows_test.py`'s re-read reader, on scripts built here.

That module asks it of every listing aggregate of the organization, and
a run over trees that all read once, or all read again, cannot show that
the reader tells the two apart. These build both, and the scripts a
line-based reading would get wrong: a loop and a listing that do not
hold each other, a `done` that is text, a loop that is a comment.

Nothing here reaches the network, so no `integration` marker, for the
reason `pins_test.py` gives.
"""

from __future__ import annotations

import pytest

from .workflows_test import looped, rereads

LIST = (
    "jobs=$(gh api --paginate \\\n"
    '  "repos/${GITHUB_REPOSITORY}/actions/runs/'
    '${GITHUB_RUN_ID}/jobs?per_page=100" \\\n'
    "  --jq '.jobs[] | .name')\n"
)
"""The listing's call as section 10's aggregates write it, the path quoted."""

AGAIN = (
    "reads=0\n"
    "while :; do\n"
    f"{LIST}"
    '  lagging=$(printf "%s\\n" "${jobs}" | awk \'$1 == "unfinished"\')\n'
    '  if [ -z "${lagging}" ] || [ "${reads}" -eq 3 ]; then\n'
    "    break\n"
    "  fi\n"
    "  reads=$((reads + 1))\n"
    "  sleep 10\n"
    "done\n"
)
"""A listing read again in a loop, which is the positive control."""


def test_a_listing_read_in_a_loop_that_sleeps_is_a_re_read() -> None:
    """Section 10's shape, which every refusal below differs from."""
    assert looped(AGAIN)


def test_a_listing_read_once_is_refused() -> None:
    """The step as it reads before the re-read, the listing asked once."""
    assert not looped(f"set -euo pipefail\n{LIST}printf '%s\\n' \"${{jobs}}\"\n")


def test_a_for_loop_reads_again_as_a_while_loop_does() -> None:
    """The keyword opening the loop is not what is read, `do` is."""
    script = f"for attempt in 1 2 3 4\ndo\n{LIST}  sleep 10\ndone\n"
    assert looped(script)


def test_a_sleep_outside_the_loop_is_refused() -> None:
    """A loop around the listing that never waits reads it back to back."""
    assert not looped(f"for attempt in 1 2 3 4; do\n{LIST}done\nsleep 10\n")


def test_a_loop_that_waits_before_the_listing_is_refused() -> None:
    """A wait ahead of one read is a delay, not a re-read."""
    assert not looped(f"for attempt in 1 2 3; do sleep 10; done\n{LIST}")


def test_a_quoted_done_does_not_close_the_loop() -> None:
    """An `echo` saying done, ahead of the listing it shares a loop with.

    Read as a keyword, the word would close the loop there and leave the
    listing and the `sleep` outside it.
    """
    script = f'while :; do\n  echo "read done"\n{LIST}  sleep 10\ndone\n'
    assert looped(script)


def test_an_unquoted_done_that_is_an_argument_does_not_close_the_loop() -> None:
    """`done` after a command word is that command's argument."""
    script = f"while :; do\n  echo done\n{LIST}  sleep 10\ndone\n"
    assert looped(script)


def test_a_sleep_that_is_an_argument_is_no_wait() -> None:
    """`sleep` after a command word is that command's argument."""
    assert not looped(f"while :; do\n{LIST}  echo sleep\ndone\n")


def test_a_loop_that_is_a_comment_is_refused() -> None:
    """A comment line describing the loop is not one."""
    script = f"# while :; do gh api actions/runs; sleep 10; done\n{LIST}"
    assert not looped(script)


def test_a_nested_loop_counts_toward_the_one_around_it() -> None:
    """The listing inside an inner loop and the wait in the outer one."""
    script = f"while :; do\n  for page in 1; do\n{LIST}  done\n  sleep 10\ndone\n"
    assert looped(script)


@pytest.mark.parametrize(
    ("steps", "wanted"),
    [
        pytest.param([{"run": AGAIN}], True, id="the-step-loops"),
        pytest.param(
            [{"run": f"{LIST}"}, {"run": "while :; do sleep 10; done"}],
            False,
            id="listing-and-loop-in-two-steps",
        ),
    ],
)
def test_a_loop_is_one_script(steps: list[dict[str, str]], wanted: bool) -> None:  # noqa: FBT001
    """Asked per string of the job, a loop not reaching into another step.

    :param steps: the job's steps.
    :param wanted: what `rereads` should answer.
    """
    assert rereads({"needs": ["analyze"], "steps": steps}) is wanted
