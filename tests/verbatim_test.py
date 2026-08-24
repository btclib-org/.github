# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The files section 14 calls verbatim are carried where it says, and agree.

The list is prose with a reason under each entry, which is what a person
reading it needs; each bullet opens with a path and with who owes a copy,
which is what this needs. Nothing else in the organization compares those
copies, and the failure they hide is silent by construction: a hook config
that drifts still lints, it just stops asking the same question everywhere.
A tree with no copy at all hides the same way -- a comparison of what is
there has nothing to say about it, and the clause is what separates the
tree that owes one from the tree the file does not apply to.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from . import ROOT, subjects
from .grid_test import triggers

pytestmark = pytest.mark.integration


ALIGNMENT = ROOT / ".github" / "workflows" / "alignment.yml"
"""The workflow whose `pull_request` trigger is compared against section 14.

Read rather than named a second time as a list of paths: what a pull
request has to touch to be checked is the workflow's own `paths:`, and
this asks that block the same question `test_section_14_names_files`
asks of the checkouts.
"""

MARKER = b"\n## This repository in particular\n"
"""The heading a shared file puts its own tree's half under.

A file that carries it is compared up to it and not past it, which is
what lets `CONTRIBUTING.md` and `REVIEWING.md` be one file everywhere and
still answer for the tree they are in. The marker lives in the file
rather than in a list here: a second list is one more thing to keep in
step with the first, and the file is the thing being compared anyway.
"""

EVERYWHERE = "owed by every repository"
"""How a bullet of section 14 says a copy is owed of every tree.

The other spelling is `owed where` and a condition, which is prose this
does not read: a tree the condition does not reach carries no copy and
is short of nothing. Reading the clause off the bullet is what keeps the
answer where the standard states it, rather than in a list here that
would have to be kept in step with that one.
"""

CONDITIONAL = "owed where "
"""How a bullet of section 14 opens where a copy is owed on a condition."""

EXPECTED_DRIFT: dict[str, str] = {"CONTRIBUTING.md": "btclib-org/.github#281"}
"""A path section 14 names whose copies are known not to agree yet.

The value is the issue that decides it. An entry here is a strict
expected failure rather than a red row: the suite stays green on a
drift that is already filed, and the day the copies agree the test
passes unexpectedly, which strict turns red -- the signal to delete the
entry.
"""


def verbatim() -> dict[str, str]:
    """Read both halves of section 14 that name a whole path.

    :returns: each path, relative to a repository root, against the
        clause its bullet opens with.
    """
    return subjects(
        ROOT / "README.md",
        "**The same file in every repository**",
        "**Decided per repository**",
    )


def shared(path: Path) -> bytes:
    """Read the half of a copy that every repository is meant to share.

    Both halves end at one newline, so a copy that leaves a blank line
    before the marker and one that does not say the same thing here. The
    marker opens with a newline of its own, so the two spellings
    otherwise differ by the last byte of the half -- a difference a diff
    renders as nothing, in a report naming two groups of copies that look
    identical.

    :param path: the file to read.
    :returns: everything before the marker, or the whole file without
        one, ending at a single newline.
    """
    body = path.read_bytes()
    cut = body.find(MARKER)
    if cut >= 0:
        body = body[:cut]
    return body.rstrip(b"\n") + b"\n"


def owed(path: str, clause: str) -> bool:
    """Say whether section 14 owes a file of every repository.

    :param path: the file the bullet is about, for the message.
    :param clause: what the bullet says after its subject.
    :returns: whether every repository is meant to carry a copy.
    :raises LookupError: where the bullet opens with neither spelling.
    """
    if clause.startswith(CONDITIONAL):
        return False
    if clause.startswith(EVERYWHERE):
        return True
    msg = (
        f"section 14's bullet for {path} opens with neither {EVERYWHERE!r}"
        f" nor {CONDITIONAL!r}: {clause!r}"
    )
    raise LookupError(msg)


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


def test_alignment_triggers_on_every_verbatim_file() -> None:
    """A pull request editing one of these files gets checked on that commit.

    `alignment.yml`'s own `paths:` admits the section of `README.md` that
    lists these files, which is not the same trigger as the files
    themselves -- a pull request editing one waits for the Thursday cron
    otherwise.

    :raises AssertionError: where a path section 14 names is missing from
        the trigger.
    """
    admitted = triggers(ALIGNMENT)["pull_request"]["paths"]
    missing = sorted(set(verbatim()) - set(admitted))
    assert not missing, f"alignment.yml's paths trigger admits none of: {missing}"


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

    A repository that carries none of a given file is not this test's
    finding: this one is about what the copies agree on, and whether a
    tree owes a copy at all is what the test below asks of that file's
    bullet. A path in `EXPECTED_DRIFT` is the last test's.

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


def test_a_repository_carries_the_verbatim_files_owed_of_it(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """A file section 14 owes of every repository is missing from none.

    Every other question about these files is asked of the copies that
    exist, so a tree with none reads as one the standard passes over.
    `EXPECTED_DRIFT` is not consulted: an entry there records copies that
    disagree, which is a different finding from a copy that is not there.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    missing = [
        path
        for path, clause in verbatim().items()
        if owed(path, clause) and not (root / path).is_file()
    ]
    assert not missing, f"section 14 files this tree does not carry: {missing}"


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
