# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The private channel `SECURITY.md` promises, and the file that promises it.

Two things a reporter depends on: the setting that opens the advisory
form, which is in no tree, and the mailbox the policy names beside it.
Section 2 of README.md says both are owed and why, section 15 gives
each as a command, and this asks them of every repository at once.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from . import ORG, Tier, by_hand, gh_json

pytestmark = pytest.mark.integration

ADDRESS = "security at btclib dot org"
"""Section 2's one mailbox, in the spelling no harvester lifts."""

MAILTO = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
"""A machine-readable address, which is the spelling the file avoids."""


def test_private_vulnerability_reporting_is_on(repository: str) -> None:
    """Section 2's advisory form is open, at every tier.

    The setting is in no tree, and a policy linking the form where it is
    off sends a reporter to a route they do not have.

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
    is, the address is the one section 2 names, and no `@` form beside
    it, that being the spelling a harvester reads.

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
