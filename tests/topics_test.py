# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""A repository's topics and its package's keywords name the same things.

Both are what somebody searching finds the project by, and they live in
two places that cannot see each other: one is a repository setting, the
other a line of `pyproject.toml`. Section 3 is the rule and section 15
the command a person runs; this is the run nobody has to remember.

They are compared as sets. The API answers alphabetically whatever was
set, so the order it gives is nobody's, where the order in
`pyproject.toml` is by relevance and is maintained -- which is also what
makes the cap meaningful: GitHub takes twenty topics, so past twenty the
topics are the first twenty keywords rather than an arbitrary subset.
"""

from __future__ import annotations

from typing import Any

import pytest

from .organization import ORG, by_hand

CAP = 20
"""How many topics GitHub keeps. Not a choice of the organization's."""

pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def topics(settings: dict[str, dict[str, Any]]) -> dict[str, set[str]]:
    """Take the topics out of the repository document of every repository.

    :param settings: the repository documents.
    :returns: each name against its topics.
    """
    return {
        repository: set(document["topics"]) for repository, document in settings.items()
    }


def keyworded(pyprojects: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    """Return the keywords of every package, whether it declares any or not.

    A package with no `keywords` line answers `[]` here rather than
    dropping out, because the two ways of having none are the same fact
    and neither excuses the repository from having no topic either.
    Dropping out is what a package would do to be exempt from the
    comparison below, and deleting a line is not how a rule is opted out
    of.

    Which trees are packages is what `[build-system]` says: a
    `pyproject.toml` that builds nothing describes a suite or a tool, has
    nothing on an index for anybody to search, and section 3's rule about
    keywords is not about it.

    :param pyprojects: the parsed files.
    :returns: each package against its keywords, in file order.
    """
    return {
        repository: parsed.get("project", {}).get("keywords", [])
        for repository, parsed in pyprojects.items()
        if "build-system" in parsed
    }


def test_the_topics_are_the_keywords(
    pyprojects: dict[str, dict[str, Any]],
    topics: dict[str, set[str]],
) -> None:
    """Every package's topics are its keywords, capped and as a set.

    Both directions at once: a keyword no topic answers to is the index
    knowing what GitHub does not, and a topic no keyword answers to is
    the other way round. A package with neither is aligned, and a package
    with one and not the other is the finding whichever side is empty.

    :param pyprojects: the parsed files.
    :param topics: the topics of each repository.
    """
    apart: dict[str, dict[str, list[str]]] = {}
    for repository, keywords in sorted(keyworded(pyprojects).items()):
        want = set(keywords[:CAP])
        here = topics[repository]
        if here != want:
            apart[repository] = {
                "topics only": sorted(here - want),
                "keywords only": sorted(want - here),
            }
    assert not apart, f"topics and keywords that disagree: {apart}"


def test_a_repository_has_topics(repository: str, topics: dict[str, set[str]]) -> None:
    """A reader arriving from a search arrives at every repository.

    The rule above derives the topics from `keywords` and so reaches a
    package alone; a repository with no `keywords` to derive them from
    is the one with none set, and btclib-org/.github#105 is where what
    such a repository owes is being decided. What is asked meanwhile is
    the floor either answer shares: that there is at least one.

    :param repository: the repository asked about.
    :param topics: the topics of each repository.
    """
    assert topics[repository], "no topics at all; " + by_hand(
        repository, f"gh api repos/{ORG}/{repository}/topics --jq .names"
    )
