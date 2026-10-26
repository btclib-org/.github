# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Every entry under `ROADMAP.md`'s *Intended* cites an open issue.

The file says the issue an entry cites holds how far the work has gone,
and that the entry goes once that issue closes. A closed issue changes
nothing in the file, so the entry goes on stating, as intended, work
that is done or dropped. Whether an issue is open is the tracker's
answer, so these tests carry `integration`.

*Maintained* and *Not intended* are not read: an entry there cites the
issue that records a decision, and the decision stands once the issue
closes.
"""

from __future__ import annotations

import re

import pytest

from . import ROOT, bulleted, still_open
from .verbatim_test import PRECEDENT

pytestmark = pytest.mark.integration

ROADMAP = ROOT / "ROADMAP.md"

CITATION = re.compile(r"[\w.-]+/[\w.-]+#\d+")
"""An issue cited the way `still_open` reads one, `owner/repo#123`."""


def stale(entries: list[str]) -> list[str]:
    """Return the entries that cite no issue, or a closed one.

    :param entries: the bullets of a list, as `bulleted` returns them.
    :returns: those that fail, in the order given.
    """
    return [
        entry
        for entry in entries
        if not (cited := CITATION.findall(entry))
        or not all(still_open(issue) for issue in cited)
    ]


def test_every_intended_entry_cites_an_open_issue() -> None:
    """An entry goes once its issue closes, as `ROADMAP.md` says."""
    entries = bulleted(ROADMAP, "## Intended", "## Not intended")
    assert entries, "ROADMAP.md lists no entry under *Intended*"
    found = stale(entries)
    assert not found, (
        f"ROADMAP.md's *Intended* has entries citing no issue or a closed one: {found}."
        " An entry goes once its issue closes"
    )


def test_an_entry_citing_a_closed_issue_is_caught() -> None:
    """Without this, the check above could pass having read nothing.

    The same function is given an entry that cites a closed issue, and an
    entry that cites nothing.
    """
    closed = f"- **Done work** ({PRECEDENT})."
    uncited = "- **Work with no issue**."
    assert stale([closed, uncited]) == [closed, uncited], (
        f"{PRECEDENT} did not come back closed: either it was reopened, and"
        " the control needs an issue that is not, or a state is no longer"
        " being read"
    )
