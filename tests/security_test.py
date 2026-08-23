# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The private channel `SECURITY.md` promises, and the file that promises it.

Two things about reporting a vulnerability that drift apart in silence:
a repository setting no section names yet, and an address each file
writes for itself. btclib-org/.github#100 and btclib-org/.github#109
are where the sentence for each is being decided; what is asked here is
what both issues say closes them -- every repository answering the same
way.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from . import ORG, Tier, by_hand, gh_json

pytestmark = pytest.mark.integration

ADDRESS = "security at btclib dot org"
"""The one mailbox, in the spelling no harvester lifts."""

MAILTO = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
"""A machine-readable address, which is the spelling the file avoids."""


def test_private_vulnerability_reporting_is_on(repository: str) -> None:
    """The advisory form is the one channel that needs no mailbox read.

    `SECURITY.md` promises a private channel, and the form is the one
    that does not depend on somebody remembering to read an inbox; off,
    a file linking it sends a reporter to a route they do not have.

    :param repository: the repository asked about.
    """
    endpoint = f"repos/{ORG}/{repository}/private-vulnerability-reporting"
    enabled = gh_json(endpoint)["enabled"]
    assert enabled is True, (
        f"private vulnerability reporting is {enabled!r}; "
        + by_hand(repository, f"gh api {endpoint} --jq .enabled")
    )


def test_security_md_gives_the_one_address_spelled_out(
    repository: str,
    trees: dict[str, Path],
    tiers: dict[str, Tier],
) -> None:
    """Where a `SECURITY.md` is, it names the address and spells it out.

    Section 2 owes the file to a repository that publishes and lets the
    rest inherit this repository's, so a publisher without one is the
    finding and a non-publisher without one is aligned; where the file
    is, the address is the one every other copy gives, and no `@` form
    beside it, that being the spelling a harvester reads.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param tiers: the tier of each repository.
    """
    path = trees[repository] / "SECURITY.md"
    command = by_hand(
        repository,
        "grep -o -i -E 'security at btclib dot org|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+"
        "\\.[A-Za-z]{2,}' SECURITY.md | sort -u",
    )
    if not path.is_file():
        assert tiers[repository] != Tier.PUBLISHER, (
            "a publisher with no SECURITY.md, which section 2 owes it; " + command
        )
        return
    text = path.read_text(encoding="utf-8")
    assert ADDRESS in text, f"SECURITY.md does not give {ADDRESS!r}; " + command
    harvestable = sorted(set(MAILTO.findall(text)))
    assert not harvestable, f"SECURITY.md gives an address as {harvestable}; " + command
