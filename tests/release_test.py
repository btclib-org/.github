# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 12's bill of materials, read off the workflow that publishes it.

The bullet is one claim about every publisher's release: the document is
published beside the distribution files, and the attestation signs it
with them. Both halves are properties of `release.yml`, so that is what
these read -- parsed, and with the directory taken off the step that
downloads the artifact rather than written down here, because a tree is
free to put the document in `dist/` with the distribution files instead
of in a directory of its own, and a pattern for either spelling passes
vacuously on the other.

btclib-org/.github#1121 named two other shapes, and this is why neither
is here. A read over each tree's `.github/scripts/generate_sbom.py`
answers what the document contains, where the bullet is about the
document reaching the release and the statement; and the content that
section argues over -- a vendored library at the commit its submodule
pins -- is a question only a tree with a submodule has an answer to, so
asked of every publisher it decides nothing about the trees that carry
none. Declining a reader altogether was the third, on the ground that
what a release publishes is the release's own business: what that leaves
unheld is a tree that stops writing the document, whose release then
finishes green with one fewer file attached, and it leaves the
preamble's rule -- a rule enters the file together with what reads it --
to be amended rather than met.

`SBOM` is the organization's name for the artifact and not the
standard's, section 12 fixing the document and not its spelling: a tree
that renames it renames it here.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any

import pytest

from . import ORG, ROOT, SELF, Tier, by_hand
from .workflows_test import COMMENT, REMOTE_CALL, document, workflows

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

SBOM = "sbom"
"""What the organization's publishers name the artifact carrying it."""

RELEASE = "release.yml"
"""The workflow a tag runs, and the file section 2 reads a tier off."""

DOWNLOAD = "actions/download-artifact@"
"""The action a release job takes a built artifact back from."""

UPLOAD = "actions/upload-artifact@"
"""The action the job that writes the document hands it on with."""

ATTEST = "actions/attest@"
"""The action that signs the release assets, section 12's attestation."""

CREATE = "gh release create"
"""The command that attaches files to the GitHub release."""

SOURCE = "__source__"
"""The key `jobs` stashes on a resolved job, naming where its steps live.

No workflow key is spelled this way, so it cannot collide with anything
YAML gave the job; `source` reads it back off a job `attesting` or
`creating` found, to build a `by_hand` command that names the file the
steps actually came from rather than the caller's own `release.yml`.
"""


def released(root: Path) -> Path:
    """Return a publisher's release workflow.

    Built rather than searched for: this is the file section 2 measures
    tier 1 by, so a test carrying the tier marker is asked only of a
    tree that has it.

    :param root: the root of the checkout.
    :returns: the path to the workflow.
    """
    return root / ".github" / "workflows" / RELEASE


def jobs(workflow: Path) -> dict[str, dict[str, Any]]:
    """Read every job of a workflow, by id, following a delegating one.

    Section 12's caller is free to convert `attest` or `github-release`
    into a call on one of this repository's own reusable workflows
    (btclib-org/.github#35), and a job that delegates carries `uses:`
    and no `steps:` of its own. Such a job is resolved: the callee is
    read out of `ROOT` -- this working tree, which is what a `uses:`
    pinned at `@main` (section 10) actually runs -- and its own steps
    are put in the delegating job's place, `SOURCE` naming the file
    they came from. A `uses:` naming a repository other than this one's
    own, or naming this one at a ref other than `main`, is refused
    rather than guessed at: the object such a call would run is not the
    file `ROOT` holds.

    A job with a local `./`-call (`test`, `lint`, `docs` and the like in
    a caller's own `release.yml`) is left as it is, with no steps: it is
    never the job `attesting` or `creating` looks for, and following it
    would need the calling tree's own checkout, which this suite does
    not hold in `jobs`' signature.

    Per job and not `workflows_test.steps`' flat list, because what is
    asked here is where a file lands within one job: a download in the
    job that signs says nothing about the job that attaches.

    :param workflow: the file to read.
    :returns: each job id against its own mapping.
    :raises LookupError: where a job delegates to a `uses:` naming a ref
        other than `main`, or a repository other than this one's own.
    """
    found = document(workflow).get("jobs") or {}
    out: dict[str, dict[str, Any]] = {}
    for job_id, job in found.items():
        if not isinstance(job, dict):
            continue
        if job.get("steps") or "uses" not in job:
            out[job_id] = job
            continue
        value = str(job["uses"])
        matched = REMOTE_CALL.match(value)
        if matched is None:
            # a local `./`-call, or some other shape: not this bug's
            # concern, and never the job `attesting` or `creating` wants
            out[job_id] = job
            continue
        if matched["owner"] != ORG or matched["repo"] != SELF:
            msg = (
                f"{job_id} delegates to {value!r}, naming a repository "
                "this suite does not read"
            )
            raise LookupError(msg)
        ref = value[matched.end() :]
        if ref != "main":
            msg = (
                f"{job_id} delegates to {value!r} at {ref!r}, not main, "
                "so this tree does not hold the object it runs"
            )
            raise LookupError(msg)
        callee = ROOT / ".github" / "workflows" / matched["file"]
        steps = [
            step
            for callee_job in (document(callee).get("jobs") or {}).values()
            for step in (callee_job.get("steps") or [])
        ]
        out[job_id] = {**job, "steps": steps, SOURCE: (SELF, matched["file"])}
    return out


def source(job: dict[str, Any], repository: str) -> tuple[str, str]:
    """Say which repository and file a job's steps actually came from.

    :param job: a job's own mapping, as `jobs` returns it.
    :param repository: the repository whose `release.yml` was asked.
    :returns: the repository and the workflow file name to run a
        by-hand command against.
    """
    found_repository, found_file = job.get(SOURCE, (repository, RELEASE))
    return str(found_repository), str(found_file)


def artifacts(job: dict[str, Any], action: str) -> dict[str, str]:
    """Read the artifacts a job moves with one of the two actions.

    :param job: the job's own mapping.
    :param action: `DOWNLOAD` or `UPLOAD`.
    :returns: each artifact name against the directory the step gives
        it, the workspace root where the step names none.
    """
    out: dict[str, str] = {}
    for step in job.get("steps") or []:
        if not str(step.get("uses", "")).startswith(action):
            continue
        given = step.get("with") or {}
        if "name" in given:
            out[str(given["name"])] = str(given.get("path") or ".")
    return out


def covers(pattern: str, directory: str) -> bool:
    """Say whether a path a workflow passes reaches that directory.

    `dist/*` reaches a document downloaded into `dist/` exactly as
    `sbom/*` reaches one downloaded into `sbom`, which is why the
    directory is read off the download rather than fixed here. A pattern
    naming no directory at all reaches nothing: the document is
    published beside the distribution files, and the workspace root is
    where the checkout is.

    :param pattern: a glob or a path a workflow passes.
    :param directory: the directory a download step names.
    :returns: whether the pattern's own directory is that one.
    """
    return "/" in pattern and PurePosixPath(pattern).parent == PurePosixPath(directory)


def attesting(workflow: Path) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Return the job that signs the release assets, with its own step.

    :param workflow: the file to read.
    :returns: the job's id, the job, and the `actions/attest` step.
    :raises LookupError: where the workflow holds other than one such
        step, which is a release this cannot answer for rather than a
        release with nothing signed.
    """
    found = [
        (job_id, job, step)
        for job_id, job in jobs(workflow).items()
        for step in (job.get("steps") or [])
        if str(step.get("uses", "")).startswith(ATTEST)
    ]
    if len(found) != 1:
        msg = f"{workflow.name} holds {len(found)} steps using {ATTEST}"
        raise LookupError(msg)
    return found[0]


def arguments(run: str) -> list[str]:
    """Read the words each `gh release create` in a shell is passed.

    A whole-line comment is dropped first, for the reason
    `workflows_test.COMMENT` gives, and a line ending in a backslash is
    joined to the one below it: the command is passed one logical line
    however the file wraps it.

    :param run: the step's shell.
    :returns: the words after each occurrence of the command, in order.
    """
    joined = COMMENT.sub("", run).replace("\\\n", " ")
    return [
        word
        for part in joined.split(CREATE)[1:]
        for word in part.split("\n", 1)[0].split()
    ]


def creating(workflow: Path) -> tuple[str, dict[str, Any], list[str]]:
    """Return the job that cuts the GitHub release, with what it attaches.

    :param workflow: the file to read.
    :returns: the job's id, the job, and the words its step passes.
    :raises LookupError: where the workflow holds other than one step
        running the command.
    """
    found = [
        (job_id, job, arguments(str(step["run"])))
        for job_id, job in jobs(workflow).items()
        for step in (job.get("steps") or [])
        if CREATE in str(step.get("run", ""))
    ]
    if len(found) != 1:
        msg = f"{workflow.name} holds {len(found)} steps running {CREATE!r}"
        raise LookupError(msg)
    return found[0]


@pytest.mark.tier(Tier.PUBLISHER)
def test_a_publisher_writes_a_bill_of_materials(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 12: every publisher publishes one.

    Asked of the tree's workflows rather than of `release.yml` alone:
    the document is written where the distribution files are built, and
    the release takes back what that job uploaded.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    writing = [
        workflow.name
        for workflow in workflows(trees[repository])
        if any(SBOM in artifacts(job, UPLOAD) for job in jobs(workflow).values())
    ]
    assert writing, f"no job uploads a {SBOM} artifact; " + by_hand(
        repository, f"grep -rn 'name: {SBOM}$' .github/workflows/"
    )


@pytest.mark.tier(Tier.PUBLISHER)
def test_the_attestation_signs_the_bill_of_materials(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 12: the attestation signs the document with the files.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    job_id, job, step = attesting(released(trees[repository]))
    found_repository, found_file = source(job, repository)
    command = by_hand(
        found_repository, f"grep -n -A6 '{ATTEST}' .github/workflows/{found_file}"
    )
    landed = artifacts(job, DOWNLOAD).get(SBOM)
    assert landed, f"{job_id} takes back no {SBOM} artifact; " + command
    signed = str((step.get("with") or {}).get("subject-path", "")).split()
    assert any(covers(pattern, landed) for pattern in signed), (
        f"{job_id} signs {signed} and the {SBOM} artifact lands in {landed!r}; "
        + command
    )


@pytest.mark.tier(Tier.PUBLISHER)
def test_the_release_attaches_the_bill_of_materials(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 12: the document is published beside the distribution files.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    job_id, job, attached = creating(released(trees[repository]))
    found_repository, found_file = source(job, repository)
    command = by_hand(
        found_repository, f"grep -n '{CREATE}' .github/workflows/{found_file}"
    )
    landed = artifacts(job, DOWNLOAD).get(SBOM)
    assert landed, f"{job_id} takes back no {SBOM} artifact; " + command
    assert any(covers(word, landed) for word in attached), (
        f"{job_id} attaches {attached} and the {SBOM} artifact lands in "
        f"{landed!r}; " + command
    )
