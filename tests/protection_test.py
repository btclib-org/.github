# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The half of section 11's settings that classic protection carries.

Rulesets carry the integrity rules and the review requirement, and
`settings_test.py` reads them; the required checks with `strict`, the
dismissal of stale reviews, conversation resolution and `enforce_admins`
live in classic protection alone, which is the half that had drifted
while nothing read it -- btclib-org/.github#88 has the measurement. That
issue closed without deciding classic's own `required_signatures`;
btclib-org/.github#1381 settled it off, `main-integrity` already
carrying the rule, and this test reads that field back too.

The review of added dependencies and the `Signed-off-by:` check are
required checks too, and each context depends on how the tree's
`lint.yml` produces the job: that file is what the test reads to know
which one to look for.

The endpoint answers 404 three times over, and none of the three is one
case. A branch with no classic protection at all is `Branch not
protected`, which is the drift btclib-org/.github#88 exists to catch and
where a repository moved to rulesets alone would end up: that one is
every field of the list off, and the test says so. A repository the
token cannot see is `Not Found`, and that one is skipped with the
reason, the run having nothing to say about a document it could not
read. A repository with no `main` branch at all -- GitHub defaults a new
repository to whatever branch it pushes first, and section 16 sets
`main` explicitly only as a later checklist step -- is `Branch not
found`, and that one fails, naming the repository and the missing
branch: no other test in this suite asks whether `main` exists, so a
skip here would leave the question unanswered rather than merely
deferred. The three are told apart on what `gh` wrote to stderr; anything
else the endpoint answers is raised, a throttled or failing API being
none of them.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from . import ORG, SELF, by_hand, gh_json, still_open
from .check_sign_off_test import SCRIPT
from .dependency_review_test import ACTION, READ_AS, REUSABLE
from .workflows_test import jobs

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

pytestmark = pytest.mark.integration

ENDPOINT = "branches/main/protection"

UNPROTECTED = "Branch not protected"
"""What `gh api` reports for a `main` with no classic protection."""

UNREADABLE = "Not Found"
"""What `gh api` reports for a repository or document the token cannot see."""

NO_MAIN = "Branch not found"
"""What `gh api` reports for a repository with no `main` branch yet."""

ACTIONS_APP = 15368
"""The Actions app, which section 11 binds every required check to."""

EXPECTED_DEPARTURE: dict[tuple[str, str], str] = {
    ("claude-process", "strict"): "btclib-org/.github#1619",
}
"""A field of the classic list known to be off, against the issue deciding it.

The key is the repository and the field's name in the test below.
"""

STAND_IN = {"strict": "merge_queue"}
"""The rule that has to be on `main` where a classic field is excused.

The merge queue tests each pull request merged onto the current `main`
before it lands, which is what `strict` guarantees.
"""

CALL = f"{ORG}/{SELF}/.github/workflows/reusable-lint.yml@main"
"""How a tree's `lint.yml` calls the workflow that holds the review job."""


@pytest.fixture(scope="session")
def protections(repositories: list[str]) -> dict[str, dict[str, Any] | str | None]:
    """Fetch the classic protection document of every repository.

    :param repositories: the names to ask about.
    :returns: each name against its document -- empty where `main` has
        no classic protection -- `None` where the token could not read
        it, or a failure reason where there is no `main` to hold one.
    :raises subprocess.CalledProcessError: where the endpoint answered
        something other than a document or one of the three 404s.
    """
    out: dict[str, dict[str, Any] | str | None] = {}
    for repository in repositories:
        try:
            out[repository] = gh_json(f"repos/{ORG}/{repository}/{ENDPOINT}")
        except subprocess.CalledProcessError as error:
            if UNPROTECTED in error.stderr:
                out[repository] = {}
            elif UNREADABLE in error.stderr:
                out[repository] = None
            elif NO_MAIN in error.stderr:
                out[repository] = (
                    f"{repository} has no main branch to protect: "
                    f"gh api repos/{ORG}/{repository}/{ENDPOINT} answered {NO_MAIN}"
                )
            else:
                raise
    return out


def holds(document: dict[str, Any], field: str, *, off: bool = False) -> bool:
    """Say whether one of the `{"enabled": bool}` fields is as section 11 wants.

    A field the document lacks holds nothing either way: a `main` with
    no classic protection forbids no force push, and a default read for
    `allow_force_pushes` would have said it does.

    :param document: the classic protection, possibly empty.
    :param field: the field's name.
    :param off: whether the section wants the field off rather than on.
    :returns: whether the field is there and in the wanted state.
    """
    return field in document and bool(document[field]["enabled"]) is not off


def test_main_requires_a_check_and_the_rest_of_classic_protection(
    repository: str,
    protections: dict[str, dict[str, Any] | str | None],
) -> None:
    """Section 11's classic list, field by field.

    Required checks with `strict`, one approving review with stale ones
    dismissed, linear history, no force pushes, no deletions,
    conversation resolution, and `enforce_admins` off -- the last being
    what lets the maintainer's review bypass work at all. A `main` with
    no classic protection is the same question with every field off,
    and is reported as that rather than as a case of its own: the list
    is what section 11 states, and a branch holding none of it fails
    the list, through the one assertion the backlog knows to excuse.
    A field `EXPECTED_DEPARTURE` lists for the repository is excused,
    and checked to be off.

    :param repository: the repository asked about.
    :param protections: the classic protection of each repository.
    """
    document = protections[repository]
    if document is None:
        pytest.skip(
            f"this run's token cannot read {ENDPOINT} on {repository}: "
            f"gh api repos/{ORG}/{repository}/{ENDPOINT} answered {UNREADABLE}"
        )
    if isinstance(document, str):
        pytest.fail(document)
    checks = document.get("required_status_checks") or {}
    reviews = document.get("required_pull_request_reviews") or {}
    wanted = {
        "a required check": bool(checks.get("checks")),
        "strict": checks.get("strict") is True,
        "one approving review": reviews.get("required_approving_review_count") == 1,
        "dismiss_stale_reviews": reviews.get("dismiss_stale_reviews") is True,
        "required_linear_history": holds(document, "required_linear_history"),
        "no force pushes": holds(document, "allow_force_pushes", off=True),
        "no deletions": holds(document, "allow_deletions", off=True),
        "required_conversation_resolution": holds(
            document, "required_conversation_resolution"
        ),
        "enforce_admins off": holds(document, "enforce_admins", off=True),
        "required_signatures off": holds(document, "required_signatures", off=True),
    }
    excused = {field for name, field in EXPECTED_DEPARTURE if name == repository}
    back = sorted(field for field in excused if wanted[field])
    off = sorted(
        field for field, held in wanted.items() if not held and field not in excused
    )
    problems: list[str] = []
    if off:
        problems.append(f"classic protection does not hold: {off}")
    if back:
        problems.append(
            f"excused but on again, delete the EXPECTED_DEPARTURE entry: {back}"
        )
    assert not problems, (
        "; ".join(problems)
        + "; "
        + by_hand(
            repository,
            f"gh api repos/{ORG}/{repository}/{ENDPOINT} --jq "
            "'{checks: [.required_status_checks.checks[]?.context],"
            " strict: .required_status_checks.strict,"
            " admins: .enforce_admins.enabled}'",
        )
    )


@pytest.mark.parametrize(
    "entry",
    list(EXPECTED_DEPARTURE),
    ids=[f"{r}-{f}" for r, f in EXPECTED_DEPARTURE],
)
def test_a_recorded_departure_is_still_one(entry: tuple[str, str]) -> None:
    """Each `EXPECTED_DEPARTURE` entry cites an open issue and has its rule.

    :param entry: the entry's repository and field.
    """
    repository, field = entry
    reference = EXPECTED_DEPARTURE[entry]
    assert still_open(reference), f"{repository} {field} cites {reference}, closed"
    rules = gh_json(f"repos/{ORG}/{repository}/rules/branches/main")
    assert any(rule["type"] == STAND_IN[field] for rule in rules), (
        f"{repository} has no active {STAND_IN[field]} rule on main: its {field}"
        " departure no longer has the rule it rests on"
    )


def lint_context(
    lint: Path, called: str, carries: Callable[[dict[str, Any]], bool]
) -> str | None:
    """Name the check context a job of the tree's `lint.yml` reports.

    A job calling `reusable-lint.yml` reports the called job's name after
    its own, and a job with a step carrying the check reports its own name.

    :param lint: the tree's `lint.yml`.
    :param called: the job's id in `reusable-lint.yml`.
    :param carries: whether a step of the tree's own job carries the check.
    :returns: the context, or `None` where the file holds neither job.
    """
    if not lint.is_file():
        return None
    for job_id, job in jobs(lint).items():
        name = job.get("name", job_id)
        if job.get("uses") == CALL:
            return f"{name} / {jobs(REUSABLE)[called]['name']}"
        if any(carries(step) for step in job.get("steps") or []):
            return str(name)
    return None


def reviews(step: dict[str, Any]) -> bool:
    """Say whether a step runs the dependency review on the shared config."""
    return bool(
        ACTION.search(step.get("uses", ""))
        and step.get("with", {}).get("config-file") == READ_AS
    )


def signs_off(step: dict[str, Any]) -> bool:
    """Say whether a step runs the `Signed-off-by:` script."""
    return SCRIPT.name in step.get("run", "")


@pytest.mark.parametrize(
    ("called", "carries"),
    [("dependency-review", reviews), ("sign-off", signs_off)],
)
def test_main_requires_the_lint_check(
    repository: str,
    trees: dict[str, Path],
    protections: dict[str, dict[str, Any] | str | None],
    called: str,
    carries: Callable[[dict[str, Any]], bool],
) -> None:
    """Section 11's `Dependency review` and `Sign-off`, required from Actions.

    Each context is the called job's name after the calling job's own in
    a tree calling `reusable-lint.yml`, and the job's name in a tree with
    its own `lint.yml`: the tree's own file says which, and the rule has to name
    what that file produces, since a context nothing reports blocks every
    merge and one the rule lacks gates nothing.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param protections: the classic protection of each repository.
    :param called: the job's id in `reusable-lint.yml`.
    :param carries: whether a step of the tree's own job carries the check.
    """
    document = protections[repository]
    if document is None:
        pytest.skip(
            f"this run's token cannot read {ENDPOINT} on {repository}: "
            f"gh api repos/{ORG}/{repository}/{ENDPOINT} answered {UNREADABLE}"
        )
    if isinstance(document, str):
        pytest.fail(document)
    lint = trees[repository] / ".github" / "workflows" / "lint.yml"
    context = lint_context(lint, called, carries)
    assert context, f"lint.yml neither calls reusable-lint.yml nor runs {called}"
    required = {
        (check["context"], check["app_id"])
        for check in (document.get("required_status_checks") or {}).get("checks", [])
    }
    assert (context, ACTIONS_APP) in required, (
        f"main does not require {context!r} from the Actions app; "
        + by_hand(
            repository,
            f"gh api repos/{ORG}/{repository}/{ENDPOINT}/required_status_checks "
            "--jq '[.checks[] | [.context, .app_id]]'",
        )
    )
