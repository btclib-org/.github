# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The half of section 11's settings that classic protection carries.

Rulesets carry the integrity rules and the review requirement, and
`settings_test.py` reads them; the required checks with `strict`, the
dismissal of stale reviews, conversation resolution and `enforce_admins`
live in classic protection alone, which is the half that had drifted
while nothing read it -- btclib-org/.github#88 has the measurement.

The endpoint answers 404 twice over, and the two are not one case. A
branch with no classic protection at all is `Branch not protected`,
which is the drift btclib-org/.github#88 exists to catch and where a
repository moved to rulesets alone would end up: that one is every
field of the list off, and the test says so. A repository the token
cannot see is `Not Found`, and that one is skipped with the reason, the
run having nothing to say about a document it could not read. The two
are told apart on what `gh` wrote to stderr; anything else the endpoint
answers is raised, a throttled or failing API being neither.
"""

from __future__ import annotations

import subprocess
from typing import Any

import pytest

from .organization import ORG, by_hand, gh_json

pytestmark = pytest.mark.integration

ENDPOINT = "branches/main/protection"

UNPROTECTED = "Branch not protected"
"""What `gh api` reports for a `main` with no classic protection."""

UNREADABLE = "Not Found"
"""What `gh api` reports for a repository, or a document, the token cannot see."""


@pytest.fixture(scope="session")
def protections(repositories: list[str]) -> dict[str, dict[str, Any] | None]:
    """Fetch the classic protection document of every repository.

    :param repositories: the names to ask about.
    :returns: each name against its document -- empty where `main` has
        no classic protection -- or `None` where the token could not
        read it.
    :raises subprocess.CalledProcessError: where the endpoint answered
        something other than a document or one of the two 404s.
    """
    out: dict[str, dict[str, Any] | None] = {}
    for repository in repositories:
        try:
            out[repository] = gh_json(f"repos/{ORG}/{repository}/{ENDPOINT}")
        except subprocess.CalledProcessError as error:
            if UNPROTECTED in error.stderr:
                out[repository] = {}
            elif UNREADABLE in error.stderr:
                out[repository] = None
            else:
                raise
    return out


def holds(document: dict[str, Any], field: str, *, off: bool = False) -> bool:
    """Say whether one of the `{"enabled": bool}` fields is as section 11 wants.

    A field the document lacks holds nothing either way: a `main` with
    no classic protection forbids no force push, and a default read for
    `allow_force_pushes` would have said it does.

    :param document: the classic protection, possibly empty.
    :param field: the field's name.
    :param off: whether the section wants the field off rather than on.
    :returns: whether the field is there and in the wanted state.
    """
    return field in document and bool(document[field]["enabled"]) is not off


def test_main_requires_a_check_and_the_rest_of_classic_protection(
    repository: str,
    protections: dict[str, dict[str, Any] | None],
) -> None:
    """Section 11's classic list, field by field.

    Required checks with `strict`, one approving review with stale ones
    dismissed, linear history, no force pushes, no deletions,
    conversation resolution, and `enforce_admins` off -- the last being
    what lets the maintainer's review bypass work at all. A `main` with
    no classic protection is the same question with every field off,
    and is reported as that rather than as a case of its own: the list
    is what section 11 states, and a branch holding none of it fails
    the list, through the one assertion the backlog knows to excuse.

    :param repository: the repository asked about.
    :param protections: the classic protection of each repository.
    """
    document = protections[repository]
    if document is None:
        pytest.skip(
            f"this run's token cannot read {ENDPOINT} on {repository}: "
            f"gh api repos/{ORG}/{repository}/{ENDPOINT} answered {UNREADABLE}"
        )
    checks = document.get("required_status_checks") or {}
    reviews = document.get("required_pull_request_reviews") or {}
    wanted = {
        "a required check": bool(checks.get("checks")),
        "strict": checks.get("strict") is True,
        "one approving review": reviews.get("required_approving_review_count") == 1,
        "dismiss_stale_reviews": reviews.get("dismiss_stale_reviews") is True,
        "required_linear_history": holds(document, "required_linear_history"),
        "no force pushes": holds(document, "allow_force_pushes", off=True),
        "no deletions": holds(document, "allow_deletions", off=True),
        "required_conversation_resolution": holds(
            document, "required_conversation_resolution"
        ),
        "enforce_admins off": holds(document, "enforce_admins", off=True),
    }
    off = sorted(field for field, held in wanted.items() if not held)
    assert not off, f"classic protection does not hold: {off}; " + by_hand(
        repository,
        f"gh api repos/{ORG}/{repository}/{ENDPOINT} --jq "
        "'{checks: [.required_status_checks.checks[]?.context],"
        " strict: .required_status_checks.strict,"
        " admins: .enforce_admins.enabled}'",
    )
