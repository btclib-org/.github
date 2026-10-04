# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Each scorecard tree has had a good first issue open in the last 12 months.

The rule is section 10's, beside the registration at bestpractices.dev
that the same entry owes: its gold criterion `small_tasks` asks for small
tasks identified for new contributors. An issue's labels and dates are
the forge's and in no checkout, so the answer is the API's.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from urllib.parse import quote

import pytest

from . import ORG, by_hand, gh
from .grid_test import record

# the label CONTRIBUTING.md sets aside for a first contribution
LABEL = "good first issue"

# section 10's window, a year plus a day for a leap year
WINDOW = timedelta(days=366)

# what `closed_at` reads as for an issue still open
OPEN = "open"


def recent(ends: list[str], now: datetime, window: timedelta = WINDOW) -> bool:
    """Say whether any issue was open at some time within the window.

    :param ends: per issue, `OPEN` or the ISO 8601 time it was closed.
    :param now: the end of the window.
    :param window: how far back it reaches.
    :returns: True when one is still open or was closed within the window.
    """
    return any(
        end == OPEN or now - datetime.fromisoformat(end) <= window for end in ends
    )


def test_an_issue_closed_before_the_window_does_not_count() -> None:
    """The check can fail: only an old closed issue, or none, is refused."""
    now = datetime(2026, 10, 4, tzinfo=UTC)
    assert recent([OPEN], now)
    assert recent(["2025-10-03T00:00:00Z"], now)
    assert not recent(["2025-10-02T00:00:00Z"], now)
    assert not recent([], now)


@pytest.mark.integration
def test_a_scorecard_tree_has_a_recent_good_first_issue(repository: str) -> None:
    """At least one issue with the label was open at some time in the window.

    The issues endpoint answers pull requests too, and those are left
    out: a pull request is a contribution already made, not a task
    waiting for one.

    :param repository: the repository asked about.
    """
    if repository not in record()["scorecard"]:
        pytest.skip(f"section 10's scorecard entry does not name {repository}")
    ends = gh(
        f"repos/{ORG}/{repository}/issues?state=all&labels={quote(LABEL)}&per_page=100",
        f'.[] | select(.pull_request == null) | .closed_at // "{OPEN}"',
    )
    assert recent(ends, datetime.now(UTC)), (
        f"{repository} has no issue labelled {LABEL!r} open in "
        f"the last {WINDOW.days} days; "
        + by_hand(repository, f"gh issue list --state all --label '{LABEL}'")
    )
