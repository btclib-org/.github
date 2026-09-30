# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 12's not-affected list, read off each tree's `.github/vex.toml`.

The file is optional: a tree with nothing to say has none, and the test
passes for it. What it reads is the file where there is one -- that it
parses, that every entry holds exactly the keys the section names, and
that each `justification` is one of CycloneDX 1.6's own -- because
`generate_sbom.py` refuses a malformed list at release time, and a tree
finds that out on the day it cuts a tag. A file with no entry is refused
too: the section says a tree with none has no file, since an empty one
would read as a list that had been looked at.

Whether an entry's `component` is one the release's document carries is
not read here. The document is built from a wheel, and only the script
that builds it can answer that.
"""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING, Any

import pytest

from . import by_hand

if TYPE_CHECKING:
    from pathlib import Path

# where a tree keeps its list, relative to its root
LIST = ".github/vex.toml"

# the keys of one `[[not_affected]]` table, all of them required
KEYS = frozenset({"id", "source", "component", "justification", "detail"})

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
