# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""A release tag is an object a signature can sit on.

The organization's rule is that a tag is signed, and `settings_test.py`
asks whether the ruleset enforces it; this asks whether the tag a
repository holds is one the rule can describe. A lightweight tag is a
ref to a commit with no object of its own, so there is nothing on it to
sign, and a ruleset requiring a signature on `refs/tags/v*` says nothing
about it. btclib-org/.github#105 is where what a release tag is, for a
repository that publishes nothing, is being decided.
"""

from __future__ import annotations

import pytest

from . import ORG, by_hand, gh_json

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
