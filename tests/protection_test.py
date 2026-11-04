# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The half of section 11's settings that classic protection carries.

Rulesets carry the integrity rules and the review requirement, and
`settings_test.py` reads them; the required checks with `strict` off, the
dismissal of stale reviews, conversation resolution and `enforce_admins`
live in classic protection alone, which is the half that had drifted
while nothing read it -- btclib-org/.github#88 has the measurement. That
issue closed without deciding classic's own `required_signatures`;
btclib-org/.github#1381 settled it off, and this test reads that field
back too. No ruleset over `main` carries the rule either
(btclib-org/.github#1738), which `settings_test.py` reads.

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

from . import ORG, ROOT, by_hand, filed, gh_json, still_open
from .check_sign_off_test import SCRIPT
from .dependency_review_test import ACTION, REUSABLE, TREE_READ_AS
from .hooks_test import SOURCERY_CALLED, sourcery_calls
from .workflows_test import calls_here, jobs

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

EXPECTED_DEPARTURE: dict[tuple[str, str], str] = {}
"""A field of the classic list known not to hold, against the issue deciding it.

The key is the repository and the field's name in the test below.

Empty is where this returns rather than where it always is: the table
stands for the next departure the maintainer accepts.
"""

CALLED = "reusable-lint.yml"
"""The workflow of this repository holding the review job a tree calls."""


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

    Required checks with `strict` off, one approving review with stale ones
    dismissed, linear history, no force pushes, no deletions,
    conversation resolution, and `enforce_admins` off -- the last being
    what lets the maintainer's review bypass work in a tree that keeps
    one. A `main` with
    no classic protection is the same question with every field off,
    and is reported as that rather than as a case of its own: the list
    is what section 11 states, and a branch holding none of it fails
    the list, through the one assertion the backlog knows to excuse.
    A field `EXPECTED_DEPARTURE` lists for the repository is excused,
    and checked not to hold.

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
        "strict off": checks.get("strict") is False,
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
    problems: list[str] = []
    if off := sorted(
        field for field, held in wanted.items() if not held and field not in excused
    ):
        problems.append(f"classic protection does not hold: {off}")
    if back:
        problems.append(
            f"excused but holding again, delete the EXPECTED_DEPARTURE entry: {back}"
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


SOURCERY_ROW = "test_a_python_tree_calls_sourcery_with_its_rules_off"
"""The test whose `BACKLOG` row lists the trees not yet requiring Sourcery."""


def sourcery_context(root: Path) -> str | None:
    """Name the check context a tree's call of `SOURCERY_CALLED` reports.

    The calling job's name, or its id where it has none, then the called
    job's name, as a job calling a reusable workflow reports.

    :param root: the root of the checkout.
    :returns: the context, or `None` where no job calls the workflow.
    """
    calls = sourcery_calls(root)
    if not calls:
        return None
    workflow, job_id = calls[0]
    name = jobs(workflow)[job_id].get("name", job_id)
    (called,) = jobs(ROOT / ".github" / "workflows" / SOURCERY_CALLED).values()
    return f"{name} / {called['name']}"


def sourcery_departures(
    document: dict[str, Any], context: str | None, *, waiting: bool
) -> list[str]:
    """Report where a classic protection departs from section 10 on Sourcery.

    A tree whose call reports `context`, and that is not `waiting` in the
    row, requires that context from the Actions app and no other naming
    Sourcery. Any other tree requires no context naming Sourcery.

    :param document: the classic protection, possibly empty.
    :param context: what `sourcery_context` names, `None` where no job calls
        the workflow.
    :param waiting: whether the tree is in the `BACKLOG` row of `SOURCERY_ROW`.
    :returns: one finding, or none.
    """
    checks = (document.get("required_status_checks") or {}).get("checks") or []
    named = [
        (str(check.get("context", "")), check.get("app_id"))
        for check in checks
        if "sourcery" in str(check.get("context", "")).lower()
    ]
    wanted = [] if context is None or waiting else [(context, ACTIONS_APP)]
    if named == wanted:
        return []
    return [f"requires {named}, where section 10 wants {wanted}"]


def test_a_sourcery_departure_would_be_reported(tmp_path: Path) -> None:
    """`sourcery_departures` and `sourcery_context` each way they can answer.

    :param tmp_path: where the trees are built.
    """
    context = "sourcery / Sourcery"
    assert sourcery_context(ROOT) == context

    def document(*checks: tuple[str, int]) -> dict[str, Any]:
        return {
            "required_status_checks": {
                "checks": [{"context": c, "app_id": a} for c, a in checks]
            }
        }

    others = [("Lint", ACTIONS_APP), ("Sign-off", ACTIONS_APP)]
    required = document(*others, (context, ACTIONS_APP))
    assert sourcery_departures(required, context, waiting=False) == []
    assert sourcery_departures(document(*others), None, waiting=False) == []
    assert sourcery_departures(document(*others), context, waiting=True) == []
    assert sourcery_departures({}, None, waiting=True) == []
    wrong = [
        (document(*others), context, False),
        (required, context, True),
        (required, None, False),
        (document((context, 1)), context, False),
        (document(("sourcery", ACTIONS_APP)), context, False),
        (document(("sourcery", ACTIONS_APP), (context, ACTIONS_APP)), context, False),
        ({}, context, False),
    ]
    for doc, called, waiting in wrong:
        assert sourcery_departures(doc, called, waiting=waiting), (doc, called, waiting)
    root = tmp_path / "named"
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / ".github" / "workflows" / "python.yml").write_text(
        "on:\n  pull_request:\njobs:\n  check:\n    name: Python\n"
        f"    uses: ./.github/workflows/{SOURCERY_CALLED}\n",
        encoding="utf-8",
    )
    assert sourcery_context(root) == "Python / Sourcery"
    assert sourcery_context(tmp_path / "none") is None


def test_main_requires_sourcery_once_out_of_its_row(
    repository: str,
    trees: dict[str, Path],
    protections: dict[str, dict[str, Any] | str | None],
) -> None:
    """Section 10: `sourcery` is required once a tree is out of its row.

    The trees whose clean-up has not landed, or whose caller,
    `.sourcery.yaml` or guard is not section 10's and section 4's, are
    the `BACKLOG` row of `SOURCERY_ROW`. A tree out of that row whose
    caller is in place requires the context the caller reports; a tree
    in the row, or with no caller, requires none naming Sourcery.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param protections: the classic protection of each repository.
    """
    document = protections[repository]
    if not isinstance(document, dict):
        pytest.skip(f"no classic protection of {repository} to read")
    found = sourcery_departures(
        document,
        sourcery_context(trees[repository]),
        waiting=bool(filed(SOURCERY_ROW, repository)),
    )
    assert not found, f"{found}; " + by_hand(
        repository,
        f"gh api repos/{ORG}/{repository}/{ENDPOINT} --jq "
        "'[.required_status_checks.checks[]? | [.context, .app_id]]'",
    )


@pytest.mark.parametrize(
    "entry",
    list(EXPECTED_DEPARTURE),
    ids=[f"{r}-{f}" for r, f in EXPECTED_DEPARTURE],
)
def test_a_recorded_departure_is_still_one(entry: tuple[str, str]) -> None:
    """Each `EXPECTED_DEPARTURE` entry cites an open issue.

    :param entry: the entry's repository and field.
    """
    repository, field = entry
    reference = EXPECTED_DEPARTURE[entry]
    assert still_open(reference), f"{repository} {field} cites {reference}, closed"


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
        if calls_here(str(job.get("uses", "")), CALLED):
            return f"{name} / {jobs(REUSABLE)[called]['name']}"
        if any(carries(step) for step in job.get("steps") or []):
            return str(name)
    return None


def reviews(step: dict[str, Any]) -> bool:
    """Say whether a step runs the dependency review on the shared config."""
    return bool(
        ACTION.search(step.get("uses", ""))
        and step.get("with", {}).get("config-file") == TREE_READ_AS
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
