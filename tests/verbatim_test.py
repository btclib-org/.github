"""The files section 14 calls verbatim agree where it says they do.

The list is prose with a reason under each entry, which is what a person
reading it needs; the subject of each bullet is a path, which is what
this needs. Nothing else in the organization compares those copies, and
the failure they hide is silent by construction: a hook config that
drifts still lints, it just stops asking the same question everywhere.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from .organization import ROOT
from .tables import subjects

pytestmark = pytest.mark.integration


MARKER = b"\n## This repository in particular\n"
"""The heading a shared file puts its own tree's half under.

A file that carries it is compared up to it and not past it, which is
what lets `CONTRIBUTING.md` and `REVIEWING.md` be one file everywhere and
still answer for the tree they are in. The marker lives in the file
rather than in a list here: a second list is one more thing to keep in
step with the first, and the file is the thing being compared anyway.
"""

EXPECTED_DRIFT = {
    ".gitattributes": (
        "btclib-org/.github#102: seven distinct copies; per-repo sweeps align them"
    ),
}
"""A path section 14 names whose copies are known not to agree yet.

The value is the issue that decides it. An entry here is a strict
expected failure rather than a red row: the suite stays green on a
drift that is already filed, and the day the copies agree the test
passes unexpectedly, which strict turns red -- the signal to delete the
entry.
"""


def verbatim() -> list[str]:
    """Read both halves of section 14 that name a whole path.

    :returns: the paths, relative to a repository root.
    """
    return subjects(
        ROOT / "README.md",
        "**The same file in every repository**",
        "**Decided per repository**",
    )


def shared(path: Path) -> bytes:
    """Read the half of a copy that every repository is meant to share.

    :param path: the file to read.
    :returns: everything before the marker, or the whole file without one.
    """
    body = path.read_bytes()
    cut = body.find(MARKER)
    return body if cut < 0 else body[:cut]


def test_section_14_names_files(trees: dict[str, Path]) -> None:
    """A path in the list that no repository carries is a stale entry.

    :param trees: the checkouts.
    """
    unknown = [
        path
        for path in verbatim()
        if not any((root / path).is_file() for root in trees.values())
    ]
    assert not unknown, f"section 14 names paths no repository has: {unknown}"


def copies(trees: dict[str, Path], path: str) -> dict[bytes, list[str]]:
    """Group the repositories carrying a file by the shared half they carry.

    :param trees: the checkouts.
    :param path: the file, relative to a repository root.
    :returns: each distinct content against the repositories holding it.
    """
    out: dict[bytes, list[str]] = {}
    for repository, root in sorted(trees.items()):
        here = root / path
        if here.is_file():
            out.setdefault(shared(here), []).append(repository)
    return out


def test_every_copy_of_a_verbatim_file_is_the_same_copy(
    trees: dict[str, Path],
) -> None:
    """Where two repositories carry one of these files, it is one file.

    A repository that carries none of a given file is not a finding:
    section 14 is about what the copies agree on, and which repositories
    need a copy at all is that file's own bullet to say. A path in
    `EXPECTED_DRIFT` is the test below's.

    :param trees: the checkouts.
    """
    drifted: dict[str, list[str]] = {}
    for path in verbatim():
        if path in EXPECTED_DRIFT:
            continue
        found = copies(trees, path)
        if len(found) > 1:
            drifted[path] = [", ".join(holders) for holders in found.values()]
    assert not drifted, f"verbatim files that differ between trees: {drifted}"


@pytest.mark.parametrize(
    "path",
    [
        pytest.param(
            path,
            marks=pytest.mark.xfail(strict=True, raises=AssertionError, reason=reason),
        )
        for path, reason in EXPECTED_DRIFT.items()
    ],
)
def test_a_recorded_drift_is_still_one(trees: dict[str, Path], path: str) -> None:
    """The entry in `EXPECTED_DRIFT` still describes the copies.

    Only an assertion counts as the expected failure: a path the table
    names and section 14 no longer does is a stale entry, and it errors
    rather than passing for the wrong reason.

    :param trees: the checkouts.
    :param path: the entry.
    :raises LookupError: if section 14 no longer names the path.
    """
    if path not in verbatim():
        msg = f"EXPECTED_DRIFT names {path!r}, which section 14 does not"
        raise LookupError(msg)
    found = copies(trees, path)
    assert len(found) == 1, f"{path} is {len(found)} distinct files"
