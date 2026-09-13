# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The files section 14 calls verbatim are carried where it says, and agree.

The list is prose with a reason under each entry, which is what a person
reading it needs; each bullet opens with a path and with who owes a copy,
which is what this needs, and so does each paragraph naming a file the
list leaves out by its subject. Nothing else in the organization compares those
copies, and the failure they hide is silent by construction: a hook config
that drifts still lints, it just stops asking the same question everywhere.
A tree with no copy at all hides the same way -- a comparison of what is
there has nothing to say about it, and the clause is what separates the
tree that owes one from the tree the file does not apply to.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest

from . import ORG, ROOT, still_open, subjects
from .per_subject_test import declared, per_subject
from .workflows_test import triggers

if TYPE_CHECKING:
    from collections.abc import Collection
    from pathlib import Path

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
"""How section 14 says a copy is owed of every tree.

The other spelling is `owed where` and a condition, which is prose this
does not read: a tree the condition does not reach carries no copy and
is short of nothing. Reading the clause off the standard is what keeps
the answer where it states it, rather than in a list here that would
have to be kept in step with that one. A bullet of the compared list
opens with it, and so does a paragraph naming a file that list leaves
out by its subject, that file being uncompared and owed all the same.
"""

CONDITIONAL = "owed where "
"""How section 14 opens where a copy is owed on a condition."""

SECTION = re.compile(r"from `(#{1,6} [^`]+)`")
"""How a bullet names the heading that opens the section it compares.

Only a bullet naming a section this way is read for one; a bullet with
no such clause is a whole-file bullet, by `MARKER` or by neither. The
heading's own text lives in the bullet, in `README.md`, rather than in a
second constant here that a rename of the section would leave stale.
"""

COMMIT = re.compile(r"(?P<repository>[A-Za-z0-9._-]+)@[0-9a-f]{7,40}")
"""The form of the field behind an `EXPECTED_DRIFT` value's comma.

The repository half is resolved against the names the organization
answers with. The sha is read for its shape alone: `conftest.py`
clones each tree `--depth=1`, so its object store holds the tip commit
and answers no to an arbitrary historical sha, for the clone's reason
rather than the entry's.
"""

EXPECTED_DRIFT: dict[str, str] = {}
"""A path section 14 names whose copies are known not to agree yet.

The value is the issue that decides it, and the commit the drift came
from where one commit made it -- a reference, then a comma, then
`<repo>@<sha>` where one exists. `drift_reference` reads the first
field, and `names_a_commit` holds the second to that form. An entry
here is a strict expected failure rather than a red row: the
suite stays green on a drift that is already filed, and the day the
copies agree the test passes unexpectedly, which strict turns red -- the
signal to delete the entry. That red says the copies agree and not how
they came to, so the commit is what tells whoever deletes the entry
which way the drift was resolved.

Empty is where this returns rather than where it always is: the table
stands for the next drift a branch cannot converge on its own.
"""


def drift_reference(value: str) -> str:
    """Read the issue reference out of an `EXPECTED_DRIFT` value.

    A value may carry more than the reference -- the commit a drift
    came from, comma-separated behind it -- so this reads the field
    before the first comma, never the value whole.

    :param value: an `EXPECTED_DRIFT` entry's value.
    :returns: the reference alone, qualified the way `still_open` reads it.
    """
    return value.split(",", maxsplit=1)[0]


def drift_commit(value: str) -> str:
    """Read the commit field out of an `EXPECTED_DRIFT` value.

    :param value: an `EXPECTED_DRIFT` entry's value.
    :returns: the field behind the first comma, or the empty string
        where the value is a reference and nothing else.
    """
    return value.partition(",")[2].strip()


def names_a_commit(value: str, repositories: Collection[str]) -> bool:
    """Say whether a value's commit field is `<repo>@<sha>` of this tree's.

    A value that is a reference and nothing else has no field to hold
    to the form, and answers true.

    :param value: an `EXPECTED_DRIFT` entry's value.
    :param repositories: the organization's repository names.
    :returns: whether the field behind the first comma is absent, or
        is `<repo>@<sha>` naming one of those repositories.
    """
    commit = drift_commit(value)
    if not commit:
        return True
    found = COMMIT.fullmatch(commit)
    return found is not None and found["repository"] in repositories


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


def section_heading(clause: str) -> str | None:
    """Read the heading a bullet names its section by, where it names one.

    :param clause: what the bullet says after its subject.
    :returns: the heading line, `#` and all, or ``None`` where the
        clause names no section.
    """
    found = SECTION.search(clause)
    return found.group(1) if found else None


def section(body: bytes, heading: str) -> bytes:
    """Read one named section of a file, its own heading to the next.

    A section's own heading opens what is compared and the next heading
    at the same level closes it, so two copies whose surrounding
    sections differ still compare equal here as long as the section
    itself does not.

    :param body: the file's bytes.
    :param heading: the heading line that opens the section, `#` and
        all.
    :returns: from that heading to the line before the next one at the
        same level, or to the end of the file where there is none,
        ending at a single newline like every other shape `shared`
        reads.
    :raises LookupError: where the file holds no line matching
        `heading`.
    """
    opening = heading.encode() + b"\n"
    at = body.find(b"\n" + opening)
    if at < 0:
        if not body.startswith(opening):
            msg = f"no {heading!r} heading in this copy"
            raise LookupError(msg)
        at = -1
    start = at + 1
    level = heading.split(" ", 1)[0].encode()
    boundary = re.compile(b"\n" + re.escape(level) + b" ")
    found = boundary.search(body, start + len(opening))
    end = found.start() + 1 if found else len(body)
    return body[start:end].rstrip(b"\n") + b"\n"


def shared(path: Path, clause: str = "") -> bytes:
    """Read the half of a copy that every repository is meant to share.

    Both halves end at one newline, so a copy that leaves a blank line
    before the marker and one that does not say the same thing here. The
    marker opens with a newline of its own, so the two spellings
    otherwise differ by the last byte of the half -- a difference a diff
    renders as nothing, in a report naming two groups of copies that look
    identical. A clause naming a section reads that section alone,
    ending the same way every other shape does.

    :param path: the file to read.
    :param clause: the bullet's own clause, read for a section it names.
    :returns: the named section where the clause names one, everything
        before the marker where the file carries one, or the whole file
        otherwise -- each ending at a single newline.
    """
    body = path.read_bytes()
    heading = section_heading(clause)
    if heading is not None:
        return section(body, heading)
    cut = body.find(MARKER)
    if cut >= 0:
        body = body[:cut]
    return body.rstrip(b"\n") + b"\n"


def owed(path: str, clause: str) -> bool:
    """Say whether section 14 owes a file of every repository.

    :param path: the file the clause is about, for the message.
    :param clause: what section 14 says after that subject.
    :returns: whether every repository is meant to carry a copy.
    :raises LookupError: where the clause opens with neither spelling.
    """
    if clause.startswith(CONDITIONAL):
        return False
    if clause.startswith(EVERYWHERE):
        return True
    msg = (
        f"section 14's clause for {path} opens with neither {EVERYWHERE!r}"
        f" nor {CONDITIONAL!r}: {clause!r}"
    )
    raise LookupError(msg)


def unowed(root: Path, paragraphs: dict[str, str]) -> list[str]:
    """List the per-subject files a tree owes and carries no copy of.

    A paragraph is answered by any path it gives a copy of its subject:
    the one it opens with, or one it sends a tree to. That is what keeps
    a departure in the prose a reader reads rather than in a second copy
    of it here, and it is why a departure worded away is a red row and
    not a question nobody asks.

    :param root: the root of the checkout.
    :param paragraphs: each subject against its clause.
    :returns: the subjects this tree owes a copy of and holds none of.
    :raises LookupError: where a clause opens with neither spelling.
    """
    return [
        subject
        for subject, clause in paragraphs.items()
        if owed(subject, clause)
        and not any((root / path).is_file() for path in declared(subject, clause))
    ]


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
    themselves -- a pull request editing one waits for the Saturday cron
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
    clause = verbatim()[path]
    out: dict[bytes, list[str]] = {}
    for repository, root in sorted(trees.items()):
        here = root / path
        if here.is_file():
            out.setdefault(shared(here, clause), []).append(repository)
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

    Asked of the compared list and of the per-subject paragraphs alike:
    a file outside the comparison by its subject is inside the obligation
    all the same, and section 14 says who owes one of it in the same two
    spellings. Every other question about these files is asked of the
    copies that exist, so a tree with none reads as one the standard
    passes over. `EXPECTED_DRIFT` is not consulted: an entry there
    records copies that disagree, which is a different finding from a
    copy that is not there.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    missing = [
        path
        for path, clause in verbatim().items()
        if owed(path, clause) and not (root / path).is_file()
    ]
    missing += unowed(root, per_subject())
    assert not missing, f"section 14 files this tree does not carry: {missing}"


PLANTED = "here/probe.py"
"""The subject of a paragraph written for the check below, not read from one.

Both per-subject paragraphs name a condition, so `owed` answers false
for each and neither asks any tree for a copy. A check parametrized over
them alone is green however it behaves, which is what
`test_the_field_behind_the_comma_names_a_repository_and_a_commit` is
asked of literals for; these are that, for the reading that decides a
missing copy.
"""

BY_ANOTHER_NAME = "under/probe_by_another_name.py"
"""Where the planted paragraph says one tree keeps its copy.

A departure by name rather than by directory, which is `btclib-node`'s
for `.github/scripts/check_vendored_vectors.py` and the one a check
keyed on the path alone reads as a tree short of a copy.
"""


def test_a_departure_answers_a_paragraph_and_dropping_it_reddens_the_tree(
    tmp_path: Path,
) -> None:
    """A tree at a stated departure owes nothing; unstate it and it owes one.

    The planted tree carries the departure and not the subject, so the
    first answer is one only a reader of the departure gives. The second
    is the same tree against the same clause with that sentence gone,
    which is what says the check cannot pass by finding nothing to read.
    A condition in place of the spelling asks nothing of the tree at all,
    which is the state both live paragraphs are in.

    :param tmp_path: where the tree is built.
    """
    root = tmp_path / "tree"
    (root / BY_ANOTHER_NAME).parent.mkdir(parents=True)
    (root / BY_ANOTHER_NAME).write_text("", encoding="utf-8")
    stated = f"{EVERYWHERE}. `btclib-node` keeps its copy at `{BY_ANOTHER_NAME}`."
    assert not unowed(root, {PLANTED: stated})
    silent = f"{EVERYWHERE}, and no tree is sent anywhere else."
    assert unowed(root, {PLANTED: silent}) == [PLANTED], (
        "a paragraph naming one path and a tree carrying another read as"
        " a copy that is there: the departure is not what is being read"
    )
    assert not unowed(root, {PLANTED: f"{CONDITIONAL}the tree has one."})


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


WELL_FORMED = "btclib-org/.github#830, portanode@309a098"
"""An `EXPECTED_DRIFT` value of the shape the checks below ask for."""

MALFORMED = "btclib-org/.github#830, not yet ported to the other trees"
"""A value whose commit field is prose, read as a control on that shape.

The table is empty between drifts, so a check reading it alone is green
however its reader behaves. These literals are what the check is asked
of on a day the table names nothing.
"""

STRANGER = "btclib-org/.github#830, not-a-repository@309a098"
"""A value of that shape naming a repository the organization has not."""


def test_drift_reference_reads_only_the_field_before_the_first_comma() -> None:
    """A value naming a commit besides the issue still yields it alone."""
    assert drift_reference(WELL_FORMED) == "btclib-org/.github#830"


def test_the_field_behind_the_comma_names_a_repository_and_a_commit(
    repositories: list[str],
) -> None:
    """An `EXPECTED_DRIFT` value's commit field is `<repo>@<sha>`.

    Asked of the literals above as well as of the table, which is
    empty between drifts: a check reading the table alone passes with
    its reader deleted.

    :param repositories: the organization's repository names.
    """
    assert names_a_commit(WELL_FORMED, repositories)
    assert names_a_commit(drift_reference(WELL_FORMED), repositories)
    assert not names_a_commit(MALFORMED, repositories), (
        f"{MALFORMED!r} read as naming a commit: the field behind the"
        " comma is not being held to `<repo>@<sha>`"
    )
    assert not names_a_commit(STRANGER, repositories), (
        f"{STRANGER!r} read as naming a commit: either the organization"
        " has taken a repository by that name, and this control wants"
        " another, or the repository half is no longer read"
    )
    faulty = {
        path: drift_commit(value)
        for path, value in EXPECTED_DRIFT.items()
        if not names_a_commit(value, repositories)
    }
    assert not faulty, (
        "EXPECTED_DRIFT values whose field behind the comma is not"
        f" `<repo>@<sha>` of {ORG}: {faulty}"
    )


PRECEDENT = "btclib-org/.github#367"
"""A closed issue of this tracker, read as the control on the check below.

`backlog_test.py`'s own `PRECEDENT` is the same issue for the same
reason: a reader that told no state from another -- open for a 404, or
for a renamed field -- would pass an all-open check on nothing measured,
and 367 is what tells that reader from a working one.
"""


def test_every_expected_drift_entry_cites_an_open_issue() -> None:
    """An entry goes when its issue closes, the way a `BACKLOG` row does.

    `test_a_recorded_drift_is_still_one` re-derives that the copies still
    differ; it never asks whether the issue in the value is still open,
    which is what leaves a stale citation excusing a live drift with a
    green run and nothing pointing at it. `backlog_test.py` asks the
    equivalent question of `BACKLOG`, and btclib-org/.github#844 is the
    issue that named the gap between the two tables.
    """
    stale = [
        path
        for path, value in EXPECTED_DRIFT.items()
        if not still_open(drift_reference(value))
    ]
    assert not stale, (
        f"EXPECTED_DRIFT cites issues that have closed: {stale}. An entry"
        " goes once the copies converge; where they still differ, it"
        " cites the issue recording it now"
    )


def test_a_reader_that_answered_open_for_every_drift_would_be_caught() -> None:
    """The check above passes on an empty answer, however it came to be one.

    It is green where every entry cites an open issue and green where no
    state was read at all. Asking the same function for an issue that is
    closed is what tells the two apart.
    """
    assert not still_open(PRECEDENT), (
        f"{PRECEDENT} did not come back closed: either it was reopened, and"
        " the control needs an issue that is not, or a state is no longer"
        " being read"
    )
