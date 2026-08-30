# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""A releasing tree's homepage is its documentation, on both surfaces.

Section 3 sends the two surfaces that carry the name -- `[project.urls]
homepage`, which an index serves with the package, and the repository's
`.homepage`, the *About* link on its page -- to the documentation the
tree provides, and has `documentation` name that same URL. No gate in
the tree the rule binds compares them: a release ships whatever
`pyproject.toml` says, and the setting is changed in a dashboard. This
is the same shape of pair `topics_test.py` compares, one side a line of
`pyproject.toml` and the other a setting no file in the tree holds, and
the section's two commands are what a failure here points at.
"""

from __future__ import annotations

from typing import Any

import pytest

from . import ORG, Tier, by_hand

pytestmark = pytest.mark.integration

SURFACES = (".homepage", "[project.urls] homepage", "[project.urls] documentation")
"""Where the URL is read from, in the order a failure names them."""


@pytest.mark.tier(Tier.PUBLISHER)
def test_the_homepage_is_the_documentation_on_both_surfaces(
    repository: str,
    settings: dict[str, dict[str, Any]],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 3: `.homepage`, `homepage` and `documentation` are one string.

    Compared as written, with no normalization of a trailing slash or of
    case: the rule is that the surfaces agree, so a slash one of them
    carries and another lacks is the disagreement the rule sends to be
    corrected rather than a difference to read past. Whether the string
    ends in a slash is the tree's own spelling, and this asks each tree
    only about itself.

    Whether that one URL is the tree's own site rather than a sibling's
    is not asked: section 3 names no host and no shape for the site, so
    a test reading the answer off the URL would carry a host the
    standard does not.

    The keys of `[project.urls]` are read the way
    `test_the_project_urls_are_the_seven_section_3_names` reads them,
    case folded and a space read as an underscore, so a key spelled
    another way for the same link is found rather than reported missing
    twice.

    :param repository: the repository asked about.
    :param settings: the repository documents.
    :param pyprojects: the parsed files.
    """
    urls = pyprojects[repository].get("project", {}).get("urls", {})
    spelled = {key.lower().replace(" ", "_"): value for key, value in urls.items()}
    read = dict(
        zip(
            SURFACES,
            (
                settings[repository].get("homepage"),
                spelled.get("homepage"),
                spelled.get("documentation"),
            ),
            strict=True,
        )
    )
    command = by_hand(
        repository,
        f"gh api repos/{ORG}/{repository} --jq .homepage;"
        " sed -n '/^\\[project.urls\\]/,/^\\[/p' pyproject.toml",
    )
    unset = [surface for surface in SURFACES if not read[surface]]
    assert not unset, f"no URL on {unset}; " + command
    assert len(set(read.values())) == 1, f"the surfaces disagree: {read}; " + command
