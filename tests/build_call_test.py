# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 12's rule that a publisher's release calls `reusable-build.yml`.

`build_provenance_test.py` reads the callee, which holds the signature.
This reads the callers: a `release.yml` that builds and signs for itself
is a release whose signer its own steps can alter, and nothing else
would say so.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import Tier, by_hand
from .release_test import released
from .workflows_test import document

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

# the build, called at section 10's `@main`
CALL = "btclib-org/.github/.github/workflows/reusable-build.yml@main"


@pytest.mark.tier(Tier.PUBLISHER)
def test_the_release_calls_the_signing_build(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 12: the release's files are built and signed by the callee.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    jobs = document(released(trees[repository])).get("jobs") or {}
    calling = [job_id for job_id, job in jobs.items() if job.get("uses") == CALL]
    assert calling, "no job of release.yml calls reusable-build.yml; " + by_hand(
        repository, "grep -n reusable-build.yml@main .github/workflows/release.yml"
    )
