"""Section 2's table of repositories and tiers is what the trees measure.

The section says the table is a claim and its loop is what checks it,
in either direction; this is that loop, run against every tree at once
and against the working tree for this repository, so that a row the
tree contradicts and a repository the table leaves out are each a
failure rather than something noticed in a diff.
"""

from __future__ import annotations

import pytest

from .organization import ORG, ROOT, by_hand
from .repositories import Tier
from .tables import name, rows

pytestmark = pytest.mark.integration


def declared() -> dict[str, Tier]:
    """Read the repository table of section 2.

    :returns: each repository name against the tier the table gives it.
    """
    return {
        name(row["repository"]): Tier(int(row["tier"]))
        for row in rows(ROOT / "README.md", "repository", "tier")
    }


def test_section_2_gives_every_repository_a_row(tiers: dict[str, Tier]) -> None:
    """Every repository has a row, and every row a repository.

    :param tiers: the tier of each repository, measured.
    """
    unlisted = sorted(set(tiers) - set(declared()))
    unknown = sorted(set(declared()) - set(tiers))
    assert not unlisted, f"repositories with no row in section 2: {unlisted}"
    assert not unknown, f"rows of section 2 for no repository: {unknown}"


def test_the_tier_section_2_gives_a_repository_is_the_one_measured(
    repository: str,
    tiers: dict[str, Tier],
) -> None:
    """A row's tier is what the two files in the tree measure.

    :param repository: the repository asked about.
    :param tiers: the tier of each repository, measured.
    """
    claimed = declared().get(repository)
    measured = tiers[repository]
    assert claimed == measured, (
        f"section 2 says tier {claimed}, the tree measures tier {measured}; "
        + by_hand(
            repository,
            f"gh api repos/{ORG}/{repository}/contents/pyproject.toml --silent;"
            f" gh api repos/{ORG}/{repository}/contents/.github/workflows/release.yml"
            " --silent",
        )
    )
