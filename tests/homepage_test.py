# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""A tree's homepage is its btclib.org page, its documentation Read the Docs.

Section 3 sends the two surfaces that carry the name -- `[project.urls]
homepage`, which an index serves with the package, and the repository's
`.homepage`, the *About* link on its page -- to the repository's page on
btclib.org. It has `documentation` name the Read the Docs site exactly
where Read the Docs serves the tree. No gate in the tree the rule binds
compares them: a release ships whatever `pyproject.toml` says, and the
setting is changed in a dashboard. This is the same shape of pair
`topics_test.py` compares, one side a line of `pyproject.toml` and the
other a setting no file in the tree holds, and the section's commands
are what a failure here points at.

Both tests ask a tree that declares `[project.urls]`, whatever its tier,
and skip one that declares none: the rule is about that table's fields.
"""

from __future__ import annotations

import functools
import json
import re
from typing import Any
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from . import ORG, TIMEOUT, Tier, by_hand

pytestmark = pytest.mark.integration

HOME = "https://btclib.org/{repository}/"
"""Section 3's `homepage`, on both surfaces."""

SITE = re.compile(r"https://(?P<slug>[a-z0-9-]+)\.readthedocs\.io/")
"""Section 3's `documentation`, matched whole."""

PROJECT = "https://app.readthedocs.org/api/v3/projects/{slug}/"
"""Section 11's *Pages and Read the Docs* project endpoint, public."""

URLS = "sed -n '/^\\[project.urls\\]/,/^\\[/p' pyproject.toml"
"""The command that prints the table, in a checkout."""

ASK = f"curl -s {PROJECT.format(slug='<slug>')} | jq .repository.url"
"""The command that names the repository a project builds from."""


def declared(repository: str, pyprojects: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return a tree's `[project.urls]`, or skip a tree that declares none.

    The keys are read the way
    `test_the_project_urls_are_section_3s_names` reads them,
    case folded and a space read as an underscore, so a key spelled
    another way for the same link is found rather than reported missing.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    :returns: the table, its keys spelled as section 3 names them.
    """
    urls = pyprojects[repository].get("project", {}).get("urls")
    if not urls:
        pytest.skip(f"{repository} declares no [project.urls]")
    return {key.lower().replace(" ", "_"): value for key, value in urls.items()}


@functools.cache
def serves(slug: str, repository: str) -> bool:
    """Ask Read the Docs whether a project builds from a repository.

    The slug is not the repository's name, and a slug of that name may
    be somebody else's project: `ecc` is, the tree being served as
    `btclib-ecc`. So the project's `repository.url` is what decides, read
    with any `.git` suffix removed. A slug no project holds answers 404.
    Any other refusal raises rather than asserts, so that no backlog row
    excuses it.

    :param slug: the project's slug.
    :param repository: the repository asked about.
    :returns: whether the project exists and builds from that repository.
    """
    try:
        with urlopen(PROJECT.format(slug=slug), timeout=TIMEOUT) as answer:  # noqa: S310
            project: dict[str, Any] = json.load(answer)
    except HTTPError as error:
        with error:
            if error.code == 404:  # noqa: PLR2004
                return False
            raise
    url: str = project["repository"]["url"]
    return url.removesuffix(".git") == f"https://github.com/{ORG}/{repository}"


@pytest.mark.tier(Tier.PYTHON)
def test_the_homepage_is_the_page_on_btclib_org(
    repository: str,
    settings: dict[str, dict[str, Any]],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 3: `.homepage` and `homepage` are both the btclib.org page.

    Compared as written, with no normalization of a trailing slash or of
    case: section 3 spells the URL, and a surface that drops its slash
    is the difference the rule sends to be corrected.

    :param repository: the repository asked about.
    :param settings: the repository documents.
    :param pyprojects: the parsed files.
    """
    urls = declared(repository, pyprojects)
    expected = HOME.format(repository=repository)
    read = {
        ".homepage": settings[repository].get("homepage"),
        "[project.urls] homepage": urls.get("homepage"),
    }
    wrong = {surface: url for surface, url in read.items() if url != expected}
    assert not wrong, f"{wrong}, expected {expected}; " + by_hand(
        repository, f"gh api repos/{ORG}/{repository} --jq .homepage; {URLS}"
    )


@pytest.mark.tier(Tier.PYTHON)
def test_the_documentation_is_the_read_the_docs_site_serving_the_tree(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 3: `documentation` is the Read the Docs site, where there is one.

    Read the Docs serving the tree is a setting outside it, so it is read
    off the service. The slugs asked are the one `documentation` names,
    the repository's name and the distribution's name; the last two are
    how a tree served there and declaring nothing is found. A tree served
    under another slug that it declares nowhere passes unseen.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    documentation = declared(repository, pyprojects).get("documentation")
    slugs = {repository, pyprojects[repository]["project"].get("name", repository)}
    if isinstance(documentation, str) and (site := SITE.fullmatch(documentation)):
        slugs.add(site["slug"])
    sites = [
        f"https://{slug}.readthedocs.io/"
        for slug in sorted(slugs)
        if serves(slug, repository)
    ]
    command = by_hand(repository, f"{URLS}; {ASK}")
    if not sites:
        assert documentation is None, (
            f"documentation is {documentation!r}, and Read the Docs serves"
            f" {repository} under none of {sorted(slugs)}; " + command
        )
        return
    assert documentation in sites, (
        f"documentation is {documentation!r}, and Read the Docs serves"
        f" {repository} at {sites}; " + command
    )
