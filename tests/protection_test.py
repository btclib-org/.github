"""The half of section 11's settings that classic protection carries.

Rulesets carry the integrity rules and the review requirement, and
`settings_test.py` reads them; the required checks with `strict`, the
dismissal of stale reviews, conversation resolution and `enforce_admins`
live in classic protection alone, which is the half that had drifted
while nothing read it -- btclib-org/.github#88 has the measurement.

The endpoint answers a token without push access with a 404, so the
whole module is one question a run needs a credential to ask, and skips
with the reason where it has none.
"""

from __future__ import annotations

import subprocess
from typing import Any

import pytest

from .organization import ORG, by_hand, gh_json

pytestmark = pytest.mark.integration

ENDPOINT = "branches/main/protection"


@pytest.fixture(scope="session")
def protections(repositories: list[str]) -> dict[str, dict[str, Any] | None]:
    """Fetch the classic protection document of every repository.

    :param repositories: the names to ask about.
    :returns: each name against its document, `None` where the token
        could not read it.
    """
    out: dict[str, dict[str, Any] | None] = {}
    for repository in repositories:
        try:
            out[repository] = gh_json(f"repos/{ORG}/{repository}/{ENDPOINT}")
        except subprocess.CalledProcessError:
            out[repository] = None
    return out


def test_main_requires_a_check_and_the_rest_of_classic_protection(
    repository: str,
    protections: dict[str, dict[str, Any] | None],
) -> None:
    """Section 11's classic list, field by field.

    Required checks with `strict`, one approving review with stale ones
    dismissed, linear history, no force pushes, no deletions,
    conversation resolution, and `enforce_admins` off -- the last being
    what lets the maintainer's review bypass work at all.

    :param repository: the repository asked about.
    :param protections: the classic protection of each repository.
    """
    document = protections[repository]
    if document is None:
        pytest.skip(f"this run's token cannot read {ENDPOINT} on {repository}")
    checks = document.get("required_status_checks") or {}
    reviews = document.get("required_pull_request_reviews") or {}
    wanted = {
        "a required check": bool(checks.get("checks")),
        "strict": checks.get("strict") is True,
        "one approving review": reviews.get("required_approving_review_count") == 1,
        "dismiss_stale_reviews": reviews.get("dismiss_stale_reviews") is True,
        "required_linear_history": document["required_linear_history"]["enabled"],
        "no force pushes": not document["allow_force_pushes"]["enabled"],
        "no deletions": not document["allow_deletions"]["enabled"],
        "required_conversation_resolution": document[
            "required_conversation_resolution"
        ]["enabled"],
        "enforce_admins off": not document["enforce_admins"]["enabled"],
    }
    off = sorted(field for field, held in wanted.items() if not held)
    assert not off, f"classic protection does not hold: {off}; " + by_hand(
        repository,
        f"gh api repos/{ORG}/{repository}/{ENDPOINT} --jq "
        "'{checks: [.required_status_checks.checks[]?.context],"
        " strict: .required_status_checks.strict,"
        " admins: .enforce_admins.enabled}'",
    )
