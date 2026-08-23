"""Which repositories the standard applies to, how far, and what is owed.

Three things about the organization kept in one module, so that a
change to any of them is made in one place:

- **which repositories there are** -- asked of the API rather than
  listed, for the reason `names` gives;
- **how far the standard reaches each one** -- section 2's tier,
  measured off the tree by the two files that section names. The
  section's own table of repositories is a claim the suite checks
  against this measurement, in `tiers_test.py`;
- **which findings are already filed** -- the backlog, one row per
  issue, so that a failure the tracker knows about is reported as
  expected and a repository that catches up is reported as a row to
  delete. `xfail_strict` in `pyproject.toml` is what turns the second
  into a failure.
"""

from __future__ import annotations

import enum
import functools
from pathlib import Path

from .organization import ORG, gh


class Tier(enum.IntEnum):
    """Section 2's three tiers, numbered as that section numbers them.

    Tier 1 owes the whole file and tier 3 the least, so the number goes
    up as what is owed goes down. A test names the tier it applies down
    to, and a repository of a higher number is skipped with the reason
    rather than failed: a checklist about a wheel is not a finding
    against a tree that builds none.
    """

    PUBLISHER = 1
    """A Python package that publishes, which is the standard entire."""

    PYTHON = 2
    """A Python project that publishes nothing."""

    ANY = 3
    """Any repository, whatever it is written in."""

    def binds(self, repository_tier: Tier) -> bool:
        """Say whether a rule of this tier reaches a repository of that one.

        :param repository_tier: the repository's tier.
        :returns: whether the repository owes what this tier owes.
        """
        return repository_tier <= self


def tier(root: Path) -> Tier:
    """Measure a repository's tier off its tree, as section 2 does.

    A repository is Python where it holds a `pyproject.toml`, and
    publishes where it holds `release.yml`; the section's loop asks the
    API for the same two files.

    :param root: the root of the checkout.
    :returns: the tier the tree answers to.
    """
    if not (root / "pyproject.toml").is_file():
        return Tier.ANY
    if (root / ".github" / "workflows" / "release.yml").is_file():
        return Tier.PUBLISHER
    return Tier.PYTHON


@functools.cache
def names() -> list[str]:
    """Ask the API for every repository, rather than listing them here.

    A list written down here would be one more place to remember a new
    repository, and the one place nobody would think to look: a tree that
    joins the organization is in scope for this suite the moment it
    exists. Archived repositories are out -- what they agree with is the
    standard of the day they were archived.

    Forks are not, though they were: the reason given was that a fork's
    conventions are upstream's, and that is false for a fork the
    organization has taken over. `bbt` is one -- its upstream has not
    been pushed since 2022, every commit since is the organization's, and
    the forks downstream are of this copy rather than of that one.
    Excluding it meant the one repository furthest from the standard was
    the one nothing measured.

    The filter is right in general and was wrong for one repository, so
    it comes back the day that repository is detached from its upstream:
    btclib-org/bbt#13 carries the request GitHub's support grants, and
    the last box on it is this line.

    Cached, because the list is read once at collection to parametrize
    the per-repository tests and once more by the `repositories` fixture,
    and the two have to be the same list.

    :returns: the repository names, `.github` among them.
    """
    return gh(
        f"orgs/{ORG}/repos?per_page=100",
        ".[] | select(.archived == false) | .name",
    )


BACKLOG: tuple[tuple[int, str, tuple[str, ...]], ...] = (
    # the issue, the test it is the subject of, and the repositories
    # whose failure that issue already records. A row here is a finding
    # somebody has read and filed, not one excused: the test still runs,
    # and a repository that stops failing -- by passing, or by the run
    # skipping it, the file it read gone or its tier moved -- is
    # reported until its name is taken out, which is what closes the
    # checkbox on the issue. conftest.py is what makes the skip a report
    (
        105,
        "test_the_newest_tag_is_an_object_a_signature_can_sit_on",
        (
            "btclib-node",
            "portanode",
        ),
    ),
    (
        107,
        "test_dependabot_watches_only_the_ecosystems_section_11_names",
        (
            ".github",
            "bbt",
        ),
    ),
    (
        110,
        "test_lychee_accepts_every_success_code",
        (
            "bitcoin-core-rpc",
            "btclib",
            "btclib-benchmarks",
            "btclib-node",
            "btclib-secp256k1",
        ),
    ),
    (
        111,
        "test_a_lychee_cache_is_kept_between_runs",
        (
            ".github",
            "bitcoin-core-rpc",
            "btclib",
            "btclib-benchmarks",
            "btclib-node",
            "btclib-secp256k1",
            "portanode",
        ),
    ),
    (112, "test_mypy_is_strict", ("btclib-node",)),
    (112, "test_the_gate_runs_mypy", ("bbt",)),
    (119, "test_cpy_is_selected_with_a_notice_rgx", (".github",)),
    (119, "test_every_notice_rgx_is_its_copyright_transcribed", ("bitcoin-core-rpc",)),
    (128, "test_no_step_passes_frozen", ("btclib-secp256k1",)),
    (
        129,
        "test_every_dependency_group_is_a_row_of_section_1",
        (
            "bitcoin-core-rpc",
            "btclib",
            "btclib-secp256k1",
        ),
    ),
    (
        130,
        "test_the_syntax_hooks_run",
        (
            "bbt",
            "bitcoin-core-rpc",
            "btclib-benchmarks",
            "btclib-secp256k1",
            "portanode",
        ),
    ),
    (
        131,
        "test_name_tests_test_runs_at_its_default",
        (
            ".github",
            "btclib-node",
            "btclib-secp256k1",
        ),
    ),
    (
        131,
        "test_every_test_file_is_named_so_pytest_collects_it",
        (
            ".github",
            "btclib-node",
            "btclib-secp256k1",
        ),
    ),
    (
        132,
        "test_dependabot_watches_only_the_ecosystems_section_11_names",
        ("btclib-secp256k1",),
    ),
    (133, "test_the_project_urls_are_the_seven_section_3_names", ("bitcoin-core-rpc",)),
    (
        134,
        "test_the_local_hooks_run",
        (
            "bbt",
            "bitcoin-core-rpc",
            "btclib-secp256k1",
        ),
    ),
    (153, "test_the_syntax_hooks_run", ("portanode",)),
)
"""What the tracker already knows, read by `conftest.py` at collection."""


def filed(test: str, repository: str) -> list[int]:
    """Return the issues recording that a test fails on a repository.

    :param test: the test function's name.
    :param repository: the repository's name.
    :returns: the issue numbers, empty where none is filed.
    """
    return [
        issue
        for issue, subject, repositories in BACKLOG
        if subject == test and repository in repositories
    ]
