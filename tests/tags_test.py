# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""A release tag is an object a signature can sit on.

The organization's rule is that a tag is signed, and `settings_test.py`
asks whether the ruleset enforces it; this asks whether the tag a
repository holds is one the rule can describe. A lightweight tag is a
ref to a commit with no object of its own, so there is nothing on it to
sign, and a ruleset requiring a signature on `refs/tags/v*` says nothing
about it. What a release tag is does not turn on whether the repository
publishes: btclib-org/.github#105 is where that was settled. The ruleset
reads no tag's own signature, so `test_the_newest_release_tag_is_verified`
asks each tree's newest `v*` tag what GitHub says of it.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from fnmatch import fnmatch

import pytest

from . import ORG, SELF, by_hand, gh, gh_json

pytestmark = pytest.mark.integration


def test_the_newest_tag_is_an_object_a_signature_can_sit_on(repository: str) -> None:
    """The tag the API lists first is an annotated one.

    Asked only of repositories that have a tag, as the ruleset test is.

    :param repository: the repository asked about.
    """
    listed = gh_json(f"repos/{ORG}/{repository}/tags?per_page=1")
    if not listed:
        pytest.skip(f"{repository} has no tags")
    tag = listed[0]["name"]
    endpoint = f"repos/{ORG}/{repository}/git/ref/tags/{tag}"
    kind = gh_json(endpoint)["object"]["type"]
    assert kind == "tag", f"{tag} points at a {kind}, not a tag object; " + by_hand(
        repository, f"gh api {endpoint} --jq .object.type"
    )


def test_the_newest_release_tag_is_verified(repository: str) -> None:
    """GitHub verifies the signature on the newest `v*` tag.

    The `tag-integrity` ruleset refuses an unsigned commit and does not
    read the tag's own signature, and `release.yml` publishes on the
    push. This reads the signature back as the release steps do.

    :param repository: the repository asked about.
    """
    listed = gh_json(f"repos/{ORG}/{repository}/tags?per_page=100")
    tags = [t["name"] for t in listed if t["name"].startswith("v")]
    if not tags:
        pytest.skip(f"{repository} has no v* tag")
    tag = tags[0]
    ref = f"repos/{ORG}/{repository}/git/ref/tags/{tag}"
    target = gh_json(ref)["object"]
    endpoint = f"repos/{ORG}/{repository}/git/tags/{target['sha']}"
    command = by_hand(repository, f"gh api {endpoint} --jq .verification")
    kind = target["type"]
    assert kind == "tag", f"{tag} is a {kind}, which carries no signature; {command}"
    verification = gh_json(endpoint)["verification"]
    assert verification["verified"] is True, (
        f"{tag} is not verified: {verification['reason']}; {command}"
    )


CALENDAR = re.compile(r"^v(\d{4})\.(\d{1,2})\.(\d{1,2})$")
"""Section 12's tag of this repository, `vYYYY.M.D` and nothing after."""

CALLED = ".github/workflows/reusable-*.yml"
"""The files a tree's pin into this repository runs."""


def test_this_repository_tags_what_it_changes_for_the_trees() -> None:
    """Section 12: a tag on `main` within a day of a reusable workflow changing.

    Skipped until the first tag, which is where the rule starts to be
    kept. The landing is dated by the commit on `main` that changed a
    `CALLED` file since the newest tag, the oldest such commit counting.
    """
    lines = gh(
        f"repos/{ORG}/{SELF}/tags?per_page=100", '.[] | "\\(.name) \\(.commit.sha)"'
    )
    tags = dict(line.split(" ", 1) for line in lines)
    calendar = {name: CALENDAR.match(name) for name in tags}
    dated = {name: found for name, found in calendar.items() if found}
    if not dated:
        pytest.skip(f"{SELF} has no vYYYY.M.D tag")
    newest = max(dated, key=lambda name: tuple(map(int, dated[name].groups())))
    endpoint = f"repos/{ORG}/{SELF}/compare/{tags[newest]}...main"
    compare = gh_json(endpoint)
    command = by_hand(SELF, f"gh api {endpoint} --jq .status")
    assert compare["status"] in {"ahead", "identical"}, (
        f"{newest} names no commit of main; {command}"
    )
    after = {commit["sha"] for commit in compare["commits"]}
    changed = [
        f["filename"] for f in compare["files"] if fnmatch(f["filename"], CALLED)
    ]
    landed = [
        datetime.fromisoformat(line.split(" ", 1)[1])
        for name in changed
        for line in gh(
            f"repos/{ORG}/{SELF}/commits?sha=main&path={name}&per_page=100",
            '.[] | "\\(.sha) \\(.commit.committer.date)"',
        )
        if line.split(" ", 1)[0] in after
    ]
    waiting = datetime.now(UTC) - min(landed, default=datetime.now(UTC))
    assert waiting <= timedelta(days=1), (
        f"{sorted(changed)} changed on main {waiting} ago and {newest} predates it;"
        f" {by_hand(SELF, f'git log --format=%cI {newest}..origin/main -- {CALLED}')}"
    )
