# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Each published security advisory carries what section 12's order sets.

The order is section 12's *A security advisory is worked in this order*.
An advisory is the forge's and in no checkout, so the answer is the
API's. A draft is out of reach, for the reason that section gives.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from . import ORG, by_hand, gh

# section 12's week after publication
WINDOW = timedelta(days=7)


def unset(advisory: dict[str, Any]) -> list[str]:
    """Name what triage and publication left out of an advisory.

    :param advisory: the advisory, as the repository's endpoint answers it.
    :returns: the missing fields, empty where none is.
    """
    vectors = [
        score["vector_string"]
        for score in (advisory.get("cvss_severities") or {}).values()
        if score and score.get("vector_string")
    ]
    missing = [] if vectors else ["CVSS vector"]
    if not advisory.get("cwe_ids"):
        missing.append("CWE")
    vulnerabilities = advisory["vulnerabilities"]
    if not vulnerabilities or not all(
        v.get("patched_versions") for v in vulnerabilities
    ):
        missing.append("patched version")
    return missing


def due(published_at: str, now: datetime, window: timedelta = WINDOW) -> bool:
    """Say whether an advisory was published longer ago than the window.

    :param published_at: the ISO 8601 time the advisory was published.
    :param now: the time of the check.
    :param window: how long GitHub is given for the CVE and the database.
    :returns: True once the CVE and the database entry are owed.
    """
    return now - datetime.fromisoformat(published_at) > window


def test_the_checks_can_fail() -> None:
    """Each field is refused when absent, and the week is a bound."""
    whole = {
        "cvss_severities": {
            "cvss_v3": {"vector_string": None},
            "cvss_v4": {"vector_string": "CVSS:4.0/AV:N"},
        },
        "cwe_ids": ["CWE-20"],
        "vulnerabilities": [{"patched_versions": "2026.10.4"}],
    }
    assert unset(whole) == []
    bare = {
        "cvss_severities": {"cvss_v3": {"vector_string": None}, "cvss_v4": None},
        "cwe_ids": [],
        "vulnerabilities": [{"patched_versions": None}],
    }
    assert unset(bare) == ["CVSS vector", "CWE", "patched version"]
    assert unset({**whole, "vulnerabilities": []}) == ["patched version"]
    now = datetime(2026, 10, 11, 12, tzinfo=UTC)
    assert due("2026-10-04T11:00:00Z", now)
    assert not due("2026-10-04T13:00:00Z", now)


@pytest.fixture(scope="session")
def published(repositories: list[str]) -> dict[str, list[dict[str, Any]]]:
    """Ask for every repository's published advisories.

    :param repositories: the names to ask about.
    :returns: each name against its advisories, as the endpoint answers them.
    """
    return {
        repository: [
            json.loads(line)
            for line in gh(
                f"repos/{ORG}/{repository}/security-advisories"
                "?state=published&per_page=100",
                ".[] | @json",
            )
        ]
        for repository in repositories
    }


@pytest.mark.integration
def test_the_published_advisories_are_read(
    published: dict[str, list[dict[str, Any]]],
) -> None:
    """The organization has published advisories, so reading none is a fault.

    An empty answer is what a token that cannot see them gets too, and the
    per-repository tests would pass on it.

    :param published: each repository against its published advisories.
    """
    assert any(published.values()), (
        "no published advisory read in the organization; by hand: "
        f"gh api 'repos/{ORG}/<repo>/security-advisories?state=published' "
        "--jq length"
    )


@pytest.mark.integration
def test_a_published_advisory_states_its_vector_weakness_and_fix(
    repository: str,
    published: dict[str, list[dict[str, Any]]],
) -> None:
    """Step 1's vector and CWE and step 3's patched version are set.

    :param repository: the repository asked about.
    :param published: each repository against its published advisories.
    """
    gaps = {
        advisory["ghsa_id"]: missing
        for advisory in published[repository]
        if (missing := unset(advisory))
    }
    assert not gaps, f"published advisories lack {gaps}; " + by_hand(
        repository,
        "gh api 'repos/{owner}/{repo}/security-advisories?state=published' "
        "--jq '.[] | {ghsa_id, cvss_severities, cwe_ids, vulnerabilities}'",
    )


@pytest.mark.integration
def test_a_published_advisory_has_its_cve_and_its_database_entry(
    repository: str,
    published: dict[str, list[dict[str, Any]]],
) -> None:
    """Past the week, step 4's CVE is assigned and the database has the entry.

    The database is asked for its reviewed advisories, the default type:
    those are what Dependabot alerts on and what OSV imports.

    :param repository: the repository asked about.
    :param published: each repository against its published advisories.
    """
    now = datetime.now(UTC)
    gaps: dict[str, list[str]] = {}
    for advisory in published[repository]:
        if not due(advisory["published_at"], now):
            continue
        ghsa = advisory["ghsa_id"]
        missing = [] if advisory.get("cve_id") else ["CVE"]
        if not gh(f"advisories?ghsa_id={ghsa}", ".[].ghsa_id"):
            missing.append("Advisory Database entry")
        if missing:
            gaps[ghsa] = missing
    assert not gaps, (
        f"advisories published over {WINDOW.days} days ago lack {gaps}; "
        + by_hand(
            repository,
            "gh api 'repos/{owner}/{repo}/security-advisories?state=published' "
            "--jq '.[] | [.ghsa_id, .published_at, .cve_id] | @tsv', then "
            "gh api 'advisories?ghsa_id=<ghsa>' --jq length",
        )
    )
