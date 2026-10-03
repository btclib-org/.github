# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Every tree section 10's `scorecard` entry names keeps a good first issue.

The rule is section 10's, beside the registration at bestpractices.dev
that the same entry owes: its gold criterion `small_tasks` asks for small
tasks identified for new contributors. An issue's labels and its state
are the forge's and in no checkout, so the count is the API's.
"""

from __future__ import annotations

from urllib.parse import quote

import pytest

from . import ORG, by_hand, gh
from .grid_test import record

# the label CONTRIBUTING.md sets aside for a first contribution
LABEL = "good first issue"

pytestmark = pytest.mark.integration


def test_a_scorecard_tree_keeps_a_good_first_issue_open(repository: str) -> None:
    """At least one open issue carries the label.

    The issues endpoint answers pull requests too, and those are left
    out: a pull request is a contribution already made, not a task
    waiting for one.

    :param repository: the repository asked about.
    """
    if repository not in record()["scorecard"]:
        pytest.skip(f"section 10's scorecard entry does not name {repository}")
    found = gh(
        f"repos/{ORG}/{repository}/issues?state=open&labels={quote(LABEL)}"
        "&per_page=100",
        ".[] | select(.pull_request == null) | .number",
    )
    assert found, f"{repository} has no open issue labelled {LABEL!r}; " + by_hand(
        repository, f"gh issue list --state open --label '{LABEL}'"
    )
