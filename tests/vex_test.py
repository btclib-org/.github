# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 12's not-affected list, read off each tree's `.github/vex.toml`.

The file is optional: a tree with nothing to say has none, and the test
of its shape skips it. What it reads is the file where there is one -- that it
parses, that every entry holds exactly the keys the section names, and
that each `justification` is one of CycloneDX 1.6's own -- because
`generate_sbom.py` refuses a malformed list at release time, and a tree
finds that out on the day it cuts a tag. A file with no entry is refused
too: the section says a tree with none has no file, since an empty one
would read as a list that had been looked at.

Whether an entry's `component` is one the release's document carries is
not read here. The document is built from a wheel, and only the script
that builds it can answer that.

What is read against the API is the Dependabot clause: an alert
dismissed as `not_used` or `inaccurate`, on a distribution the tree's
`[project]` declares, owes an entry naming that distribution and one of
the alert's advisory identifiers. The declared distributions are read
off `pyproject.toml` rather than a wheel, `dependencies` and every
`optional-dependencies` table, which is what a wheel's `Requires-Dist`
is built from.
"""

from __future__ import annotations

import json
import tomllib
from typing import TYPE_CHECKING, Any

import pytest

from . import ORG, Tier, by_hand, gh
from .dependencies_test import REQUIREMENT, normalized

if TYPE_CHECKING:
    from pathlib import Path

# where a tree keeps its list, relative to its root
LIST = ".github/vex.toml"

# the keys of one `[[not_affected]]` table, all of them required
KEYS = frozenset({"id", "source", "component", "justification", "detail"})

# the dismissal reasons that say the release is not affected; the API's
# others, `tolerable_risk`, `no_bandwidth` and `fix_started`, say it is
NOT_AFFECTING = frozenset({"not_used", "inaccurate"})

# CycloneDX 1.6's `impactAnalysisJustification`, the whole enumeration
JUSTIFICATIONS = frozenset(
    {
        "code_not_present",
        "code_not_reachable",
        "requires_configuration",
        "requires_dependency",
        "requires_environment",
        "protected_by_compiler",
        "protected_at_runtime",
        "protected_at_perimeter",
        "protected_by_mitigating_control",
    }
)


def problems(text: str) -> list[str]:
    """Return what is wrong with a list, one sentence each.

    :param text: the content of a `vex.toml`.
    :returns: the problems found, empty where the list is well formed.
    """
    try:
        document: dict[str, Any] = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        return [f"does not parse: {error}"]
    entries = document.get("not_affected", [])
    if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
        return ["`not_affected` is not a list of tables"]
    if not entries:
        return ["has no `[[not_affected]]` entry"]
    found = []
    for position, entry in enumerate(entries, 1):
        if set(entry) != KEYS:
            found.append(f"entry {position} holds {sorted(entry)}, not {sorted(KEYS)}")
        elif not all(isinstance(value, str) and value for value in entry.values()):
            found.append(f"entry {position} has a value that is not a non-empty string")
        elif entry["justification"] not in JUSTIFICATIONS:
            found.append(
                f"entry {position} has the justification {entry['justification']!r}"
            )
    return found


def declared(project: dict[str, Any]) -> set[str]:
    """Return the distributions a `[project]` table has the wheel require.

    A table that leaves its requirements to the backend has none to read
    here, and an empty set would pass every dismissal, so it is refused.

    :param project: the parsed `[project]` table.
    :returns: the names, normalized.
    :raises ValueError: where `dynamic` names either requirement key.
    """
    dynamic = {"dependencies", "optional-dependencies"} & set(
        project.get("dynamic", [])
    )
    if dynamic:
        msg = f"[project] declares {sorted(dynamic)} dynamic: not in pyproject.toml"
        raise ValueError(msg)
    requirements = list(project.get("dependencies", []))
    for extra in project.get("optional-dependencies", {}).values():
        requirements.extend(extra)
    return {
        normalized(match[1])
        for requirement in requirements
        if (match := REQUIREMENT.match(requirement))
    }


def unanswered(
    alerts: list[dict[str, Any]],
    entries: list[dict[str, str]],
    names: set[str],
) -> list[str]:
    """Return the dismissals that owe an entry and have none, one each.

    :param alerts: the tree's dismissed alerts, as the API answers them.
    :param entries: the tree's `[[not_affected]]` tables.
    :param names: the distributions the wheel declares, normalized.
    :returns: one sentence per alert left unanswered.
    """
    found = []
    for alert in alerts:
        package = alert["dependency"]["package"]
        name = normalized(package["name"])
        if (
            alert["dismissed_reason"] not in NOT_AFFECTING
            or package["ecosystem"] != "pip"
            or name not in names
        ):
            continue
        advisory = alert["security_advisory"]
        ids = {identifier["value"] for identifier in advisory["identifiers"]}
        if not any(
            normalized(entry["component"]) == name and entry["id"] in ids
            for entry in entries
        ):
            found.append(
                f"alert {alert['number']} ({advisory['ghsa_id']} on "
                f"{package['name']}) dismissed as {alert['dismissed_reason']}"
            )
    return found


@pytest.mark.integration
def test_a_not_affected_list_is_well_formed(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 12: a tree's list, where it has one, is what the script reads.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    path = trees[repository] / LIST
    if not path.is_file():
        pytest.skip(f"{repository} keeps no {LIST}")
    found = problems(path.read_text(encoding="utf-8"))
    assert not found, (
        f"{LIST} " + "; ".join(found) + "; " + by_hand(repository, f"cat {LIST}")
    )


@pytest.mark.integration
@pytest.mark.tier(Tier.PUBLISHER)
def test_a_dismissal_that_says_not_affected_is_listed(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 12: a `not_used` or `inaccurate` dismissal has its entry.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: the parsed `pyproject.toml` files.
    """
    alerts = [
        json.loads(line)
        for line in gh(
            f"repos/{ORG}/{repository}/dependabot/alerts?state=dismissed&per_page=100",
            ".[] | tojson",
        )
    ]
    path = trees[repository] / LIST
    entries = (
        tomllib.loads(path.read_text(encoding="utf-8")).get("not_affected", [])
        if path.is_file()
        else []
    )
    names = declared(pyprojects[repository].get("project", {}))
    found = unanswered(alerts, entries, names)
    assert not found, (
        f"{LIST} has no entry for " + "; ".join(found) + "; "
        f"by hand: gh api 'repos/{ORG}/{repository}/dependabot/alerts"
        "?state=dismissed' --jq '.[] | [.number, .dismissed_reason, "
        ".dependency.package.name, .security_advisory.ghsa_id] | @tsv'"
    )


def alert(reason: str, package: str, ecosystem: str = "pip") -> dict[str, Any]:
    """Build one dismissed alert, shaped as the API answers it.

    :param reason: the dismissal reason.
    :param package: the package the alert is on.
    :param ecosystem: the package's ecosystem.
    :returns: the alert.
    """
    return {
        "number": 7,
        "dismissed_reason": reason,
        "dependency": {"package": {"ecosystem": ecosystem, "name": package}},
        "security_advisory": {
            "ghsa_id": "GHSA-aaaa-bbbb-cccc",
            "identifiers": [
                {"type": "GHSA", "value": "GHSA-aaaa-bbbb-cccc"},
                {"type": "CVE", "value": "CVE-2026-0001"},
            ],
        },
    }


def entry(component: str, identifier: str) -> dict[str, str]:
    """Build one `[[not_affected]]` table.

    :param component: the component it names.
    :param identifier: its `id`.
    :returns: the table.
    """
    return {
        "id": identifier,
        "source": "GitHub",
        "component": component,
        "justification": "code_not_reachable",
        "detail": "d",
    }


@pytest.mark.parametrize(
    ("alerts", "entries", "owed"),
    [
        ([alert("not_used", "ecdsa")], [], True),
        ([alert("inaccurate", "ecdsa")], [], True),
        ([alert("inaccurate", "ecdsa")], [entry("ecdsa", "CVE-2026-0001")], False),
        (
            [alert("inaccurate", "ecdsa")],
            [entry("Ecdsa", "GHSA-aaaa-bbbb-cccc")],
            False,
        ),
        ([alert("inaccurate", "ecdsa")], [entry("ecdsa", "CVE-2026-9999")], True),
        ([alert("inaccurate", "ecdsa")], [entry("coincurve", "CVE-2026-0001")], True),
        ([alert("inaccurate", "extra-dep")], [], True),
        ([alert("tolerable_risk", "ecdsa")], [], False),
        ([alert("no_bandwidth", "ecdsa")], [], False),
        ([alert("fix_started", "ecdsa")], [], False),
        ([alert("inaccurate", "pytest")], [], False),
        ([alert("inaccurate", "ecdsa", "npm")], [], False),
    ],
    ids=[
        "not_used unlisted",
        "inaccurate unlisted",
        "listed by CVE",
        "listed by GHSA in another spelling",
        "listed under another id",
        "listed under another component",
        "an extra's dependency",
        "tolerable_risk",
        "no_bandwidth",
        "fix_started",
        "undeclared",
        "another ecosystem",
    ],
)
def test_a_dismissal_is_owed_an_entry_only_where_the_clause_says(
    alerts: list[dict[str, Any]],
    entries: list[dict[str, str]],
    owed: bool,  # noqa: FBT001
) -> None:
    """The reader can fail, and fails only on what the clause reaches.

    :param alerts: the dismissed alerts.
    :param entries: the list's tables.
    :param owed: whether an entry is owed and missing.
    """
    names = declared(
        {
            "dependencies": ["ecdsa>=0.19", "btclib[secp256k1] ; python_version>'3'"],
            "optional-dependencies": {"x": ["Extra_Dep"]},
        }
    )
    assert bool(unanswered(alerts, entries, names)) is owed


@pytest.mark.parametrize("key", ["dependencies", "optional-dependencies"])
def test_a_dynamic_requirement_table_is_refused(key: str) -> None:
    """The reader does not read an empty set where the backend decides.

    :param key: the requirement key declared dynamic.
    """
    with pytest.raises(ValueError, match="dynamic"):
        declared({"dynamic": [key]})


@pytest.mark.parametrize(
    ("text", "fragment"),
    [
        ("not_affected = [", "does not parse"),
        ("", "no `[[not_affected]]`"),
        (
            '[[not_affected]]\nid = "a"\n',
            "entry 1 holds",
        ),
        (
            (
                "[[not_affected]]\nid = 'a'\nsource = 's'\ncomponent = 'c'\n"
                "justification = 'unknown'\ndetail = 'd'\n"
            ),
            "justification 'unknown'",
        ),
        (
            (
                "[[not_affected]]\nid = 1\nsource = 's'\ncomponent = 'c'\n"
                "justification = ['code_not_present']\ndetail = 'd'\n"
            ),
            "not a non-empty string",
        ),
        ("not_affected = 'x'\n", "not a list of tables"),
    ],
    ids=[
        "unparsable",
        "empty",
        "missing keys",
        "unknown justification",
        "not a string",
        "not a list of tables",
    ],
)
def test_a_malformed_list_is_named(text: str, fragment: str) -> None:
    """The reader can fail: each way a list is wrong is found.

    :param text: a list wrong in one way.
    :param fragment: what the problem says.
    """
    assert fragment in "; ".join(problems(text))


def test_a_well_formed_list_has_no_problem() -> None:
    """The control for the cases above: a list of one good entry is clean."""
    text = (
        '[[not_affected]]\nid = "a"\nsource = "s"\ncomponent = "c"\n'
        'justification = "code_not_present"\ndetail = "d"\n'
    )
    assert problems(text) == []
