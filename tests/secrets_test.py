# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""A secret is an environment secret, bar what `REPOSITORY.md` records.

Section 11's *Tokens, publishing, scanning* keeps every secret in an
environment, where the owners review the job that reads it. What no
tree shows is the stores above the environment, so this reads them
through the API: the organization's, its Dependabot store, and each
repository's two. An entry there is accepted only where the repository
that spends it records it in its `REPOSITORY.md`.
"""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING

import pytest

from . import ORG, SELF, Refused, by_hand, gh_json

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

#: What `gh` prints for a server-side refusal.
TRANSIENT = re.compile(r"HTTP 5\d\d")

#: What `gh` prints for a refusal for want of a permission.
FORBIDDEN = re.compile(r"HTTP 403")

#: The one store the alignment token cannot read.
UNREADABLE = f"orgs/{ORG}/dependabot/secrets"

#: How often a store is asked before a refusal fails the test.
ATTEMPTS = 3

#: Read by `claude-review.yml`, which this repository's `REPOSITORY.md` records.
ORGANIZATION_EXCEPTIONS = frozenset({"CLAUDE_CODE_OAUTH_TOKEN"})

#: Read by `alignment.yml`, which this repository's `REPOSITORY.md` records.
REPOSITORY_EXCEPTIONS = {SELF: frozenset({"ALIGNMENT_APP_PRIVATE_KEY"})}


def held(endpoint: str) -> set[str]:
    """Name the secrets a store holds.

    The secrets service answers a passing 5xx now and then, so a read
    refused with one is asked again before it fails the test; any other
    refusal, a 403 for want of a permission included, raises at once.

    :param endpoint: the store's path after `gh api`.
    :returns: the names, never the values, which no endpoint returns.
    """
    endpoint = f"{endpoint}?per_page=100"
    for attempt in range(ATTEMPTS - 1):
        try:
            return {s["name"] for s in gh_json(endpoint)["secrets"]}
        except Refused as refused:
            if not TRANSIENT.search(refused.stderr):
                raise
            time.sleep(2**attempt)
    return {s["name"] for s in gh_json(endpoint)["secrets"]}


def unrecorded(found: set[str], allowed: frozenset[str], tree: Path) -> set[str]:
    """Name what a store holds that its spender does not record.

    :param found: what the store holds.
    :param allowed: the names this test admits there.
    :param tree: the spending repository's checkout.
    :returns: the names outside `allowed`, and those allowed but not
        written in the tree's `REPOSITORY.md`.
    """
    if not found:
        return set()
    record = (tree / "REPOSITORY.md").read_text(encoding="utf-8")
    return {n for n in found if n not in allowed or n not in record}


def skippable(endpoint: str, refused: Refused) -> bool:
    """Say whether a refusal excuses the read rather than failing it.

    Only the organization's Dependabot store, and only a 403: that store
    needs a permission the App token's action has no input to request,
    so any other refusal, or any other store's, is a finding.

    :param endpoint: the store's path after `gh api`.
    :param refused: what the read raised.
    :returns: whether to skip.
    """
    return endpoint == UNREADABLE and bool(FORBIDDEN.search(refused.stderr))


@pytest.mark.parametrize("store", ["actions", "dependabot"])
def test_the_organization_stores_hold_only_what_is_recorded(
    store: str,
    trees: dict[str, Path],
) -> None:
    """Neither organization store holds a secret its record omits.

    :param store: the organization store asked about.
    :param trees: the checkouts.
    """
    endpoint = f"orgs/{ORG}/{store}/secrets"
    try:
        found = held(endpoint)
    except Refused as refused:
        if not skippable(endpoint, refused):
            raise
        pytest.skip(
            "the organization's Dependabot store needs a permission the token "
            "action cannot request; the yearly secrets review, "
            f"{ORG}/{SELF}#1474, reads it by name, and a run with an admin "
            "token reads it here"
        )
    extra = unrecorded(found, ORGANIZATION_EXCEPTIONS, trees[SELF])
    assert not extra, f"{sorted(extra)} outside an environment; " + by_hand(
        SELF, f"gh api {endpoint} --jq '.secrets[].name'"
    )


@pytest.mark.parametrize(
    ("endpoint", "stderr", "expected"),
    [
        (UNREADABLE, "gh: Resource not accessible (HTTP 403)", True),
        (UNREADABLE, "gh: Server Error (HTTP 500)", False),
        (UNREADABLE, "gh: Not Found (HTTP 404)", False),
        (f"orgs/{ORG}/actions/secrets", "gh: Forbidden (HTTP 403)", False),
        (f"repos/{ORG}/x/dependabot/secrets", "gh: Forbidden (HTTP 403)", False),
    ],
)
def test_only_the_unreadable_store_answering_403_is_skipped(
    endpoint: str, stderr: str, *, expected: bool
) -> None:
    """The skip is that one store's 403, and nothing wider.

    :param endpoint: the store read.
    :param stderr: what `gh` said.
    :param expected: whether the read is excused.
    """
    refused = Refused(1, ["gh", "api", endpoint], stderr=stderr)
    assert skippable(endpoint, refused) is expected


def test_a_repository_holds_no_secret_outside_an_environment(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """A repository's own stores hold only what its `REPOSITORY.md` records.

    Its environments' secrets are not asked about: an environment is
    where a secret belongs.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    allowed = REPOSITORY_EXCEPTIONS.get(repository, frozenset())
    for store in ("actions", "dependabot"):
        endpoint = f"repos/{ORG}/{repository}/{store}/secrets"
        extra = unrecorded(held(endpoint), allowed, trees[repository])
        assert not extra, f"{sorted(extra)} outside an environment; " + by_hand(
            repository, f"gh api {endpoint} --jq '.secrets[].name'"
        )
