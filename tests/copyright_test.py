"""The `notice-rgx` of every repository is its `COPYRIGHT`, transcribed.

Section 5 makes the copyright header a ruff rule: `CPY` checks every
source file against `notice-rgx`, and `notice-rgx` is `COPYRIGHT`'s text
escaped into a regex by hand. ruff reads the regex and never the file,
so the second link of that chain is checked in every repository that
selects the rule and the first is checked nowhere: a tree whose
`COPYRIGHT` and whose `notice-rgx` disagree passes its own gate. This is
the first link -- section 7's shape, a generated thing compared against
its source -- asked of every tree at once, because `COPYRIGHT` is a
section 14 file and the transcription is owed to be the same wherever
the file is.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

pytestmark = pytest.mark.integration

METACHARACTERS = frozenset(r"\.^$|?*+()[]{}")
"""What a transcription escapes: the characters a regex reads as syntax.

Not `re.escape`, which also escapes a space and a `#`, neither of which
means anything outside verbose mode and both of which open every line of
the file. The transcription is one spelling rather than any regex that
happens to match, so that the copies can be compared byte for byte and a
drifted one names its own difference.
"""


def transcribed(source: Path) -> str:
    r"""Derive the `notice-rgx` a `COPYRIGHT` file asks for.

    Each line with its metacharacters escaped, the lines joined by a
    literal `\n`, the whole anchored with `^`: the header is the file's
    text and it opens the source file, which is what the anchor says.

    :param source: the `COPYRIGHT` file to transcribe.
    :returns: the regex, as `pyproject.toml` holds it once parsed.
    """
    lines = source.read_text(encoding="utf-8").splitlines()
    escaped = (
        "".join(f"\\{char}" if char in METACHARACTERS else char for char in line)
        for line in lines
    )
    return "^" + r"\n".join(escaped)


def declared(parsed: dict[str, Any]) -> str | None:
    """Read the `notice-rgx` a parsed `pyproject.toml` declares.

    :param parsed: the file, parsed.
    :returns: the regex, or None where the table or the key is absent.
    """
    table = parsed.get("tool", {}).get("ruff", {}).get("lint", {})
    value = table.get("flake8-copyright", {}).get("notice-rgx")
    return value if isinstance(value, str) else None


EXPECTED_DRIFT = {
    "bitcoin-core-rpc": (
        "btclib-org/.github#119: bcr's header is the full MIT notice"
        " by a recorded departure"
    ),
}
"""A repository whose `notice-rgx` is known not to be its `COPYRIGHT` yet.

The value is the issue that decides it. An entry here is a strict
expected failure rather than a red row: the suite stays green on a
drift that is already filed, and the day the tree aligns the test passes
unexpectedly, which strict turns red -- the signal to delete the entry.
"""


def test_every_notice_rgx_is_its_copyright_transcribed(
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Where a repository declares the regex, it is its own file's text.

    A repository that declares none is not a finding here: whether it
    selects `CPY` at all is section 5's question of that tree, and a
    tree that selects the rule without the key fails its own gate on
    every file, ruff's default regex asking for a year the notice does
    not carry. A repository in `EXPECTED_DRIFT` is the test below's.

    :param trees: the checkouts.
    :param pyprojects: the parsed files.
    """
    drifted: dict[str, dict[str, str]] = {}
    checked: list[str] = []
    for repository, parsed in sorted(pyprojects.items()):
        regex = declared(parsed)
        if regex is None or repository in EXPECTED_DRIFT:
            continue
        checked.append(repository)
        expected = transcribed(trees[repository] / "COPYRIGHT")
        if regex != expected:
            drifted[repository] = {"declared": regex, "expected": expected}
    assert checked, "no repository declares a notice-rgx, so nothing was compared"
    assert not drifted, f"notice-rgx that is not COPYRIGHT transcribed: {drifted}"


@pytest.mark.parametrize(
    "repository",
    [
        pytest.param(
            repository,
            marks=pytest.mark.xfail(strict=True, raises=AssertionError, reason=reason),
        )
        for repository, reason in EXPECTED_DRIFT.items()
    ],
)
def test_a_recorded_drift_is_still_one(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """The entry in `EXPECTED_DRIFT` still describes the tree.

    Only an assertion counts as the expected failure: a repository the
    table names and the organization no longer has, or one that has
    dropped the key rather than aligned it, is a stale entry, and it
    errors rather than passing for the wrong reason.

    :param repository: the entry.
    :param trees: the checkouts.
    :param pyprojects: the parsed files.
    :raises LookupError: if the repository no longer declares the key.
    """
    regex = declared(pyprojects[repository])
    if regex is None:
        msg = f"EXPECTED_DRIFT names {repository}, which declares no notice-rgx"
        raise LookupError(msg)
    expected = transcribed(trees[repository] / "COPYRIGHT")
    assert regex == expected, f"{repository} still declares {regex!r}"
