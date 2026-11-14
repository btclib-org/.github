# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The reactions `reusable-claude-review.yml` posts on a pull request.

The shell of the `start` and `outcome` jobs, and the verdict check that
chooses the outcome, are read out of the workflow and run here against a
stand-in `gh`, so what is asked is the shell the runner runs and not a
copy of it. `jq` is the real one, as on the runner. What the API does
with the calls is not asked: no test reaches GitHub
(btclib-org/.github#2267).

The jobs' permissions are read as the workflow's header gives them: the
reaction jobs hold `pull-requests: write` alone, which the caller grants
for the review already, so a caller needs no new scope.
"""

from __future__ import annotations

import json
import os
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from . import ROOT
from .workflows_test import jobs

if TYPE_CHECKING:
    from pathlib import Path

# the reusable review, which holds the jobs
WORKFLOW = ROOT / ".github/workflows/reusable-claude-review.yml"

# the caller in this tree, whose calling job grants the scopes
CALLER = ROOT / ".github/workflows/claude-review.yml"

# the warning the shell ends on, with status 0, where it leaves the
# reactions as they were
WARNING = "::warning::the reactions were left as they were: "

# the identity the job's GITHUB_TOKEN posts as
ACTIONS = "github-actions[bot]"

# the reactions the jobs post
REACTIONS = ("eyes", "+1", "-1", "confused")

# what both reaction steps take from the job and the event
SHARED = {
    "GH_TOKEN": "${{ secrets.GITHUB_TOKEN }}",
    "REPO": "${{ github.repository }}",
    "NUMBER": "${{ github.event.pull_request.number }}",
}

# the pull request the stand-in is asked about
REPO = "o/r"
NUMBER = "5"
URL = f"repos/{REPO}/issues/{NUMBER}/reactions"

HEAD = "0123456789abcdef0123456789abcdef01234567"
OTHER = "fedcba9876543210fedcba9876543210fedcba98"

# a stand-in `gh` that records each call, one per line, its arguments
# separated by the unit separator. It answers a GET of the reactions or
# the reviews with the file the test wrote for it, and a POST or a DELETE
# by editing the reactions file, as the API does, a POST of a reaction
# already there adding nothing; or by failing where FAIL_LIST, FAIL_POST
# or FAIL_DELETE is set
STAND_IN = """#!/bin/sh
for arg in "$@"; do printf '%s\\037' "$arg"; done >> "$CALLS"
printf '\\n' >> "$CALLS"
edit() { jq "$@" "$REACTIONS" > "$REACTIONS.new" && mv "$REACTIONS.new" "$REACTIONS"; }
case "$*" in
  *"--method POST "*)
    [ -z "$FAIL_POST" ] || exit 1
    edit --arg c "${6#content=}" --arg me github-actions[bot] '
      if any(.[][]; .content == $c and .user.login == $me) then .
      else .[-1] += [{"id": 99, "content": $c, "user": {"login": $me}}] end'
    ;;
  *"--method DELETE "*)
    [ -z "$FAIL_DELETE" ] || exit 1
    edit --argjson id "${4##*/}" 'map(map(select(.id != $id)))'
    ;;
  *"/reactions --paginate --slurp") [ -z "$FAIL_LIST" ] || exit 1; cat "$REACTIONS" ;;
  *"/reviews --paginate --slurp") cat "$REVIEWS" ;;
  *) exit 9 ;;
esac
"""

VERDICT = "Refuse to report anything but an ack of this head"


def only_step(job: str) -> dict[str, Any]:
    """Read the one step of a reaction job.

    :param job: the job's id.
    :returns: the step mapping.
    """
    (step,) = jobs(WORKFLOW)[job]["steps"]
    found: dict[str, Any] = step
    return found


def verdict_step() -> dict[str, Any]:
    """Find the review job's verdict check.

    :returns: the step mapping.
    """
    (step,) = [
        each
        for each in jobs(WORKFLOW)["review"]["steps"]
        if each.get("name") == VERDICT
    ]
    found: dict[str, Any] = step
    return found


class Stand:
    """A directory holding the stand-in `gh`, its answers and its record."""

    def __init__(self, root: Path) -> None:
        """Write the stand-in and empty answers.

        :param root: a directory of the test's own.
        """
        self.root = root
        self.bin = root / "bin"
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text(STAND_IN)
        gh.chmod(0o755)
        self.calls = root / "calls"
        self.reactions = root / "reactions.json"
        self.reviews = root / "reviews.json"
        self.answer(reactions=[], reviews=[])

    def answer(
        self,
        reactions: list[dict[str, Any]] | None = None,
        reviews: list[dict[str, Any]] | None = None,
    ) -> None:
        """Set what a GET answers, as one page under `--slurp`.

        :param reactions: the reactions on the pull request.
        :param reviews: the reviews on the pull request.
        """
        if reactions is not None:
            self.reactions.write_text(json.dumps([reactions]))
        if reviews is not None:
            self.reviews.write_text(json.dumps([reviews]))

    def run(self, shell: str, **extra: str) -> subprocess.CompletedProcess[str]:
        """Run a step's shell as the runner does, the stand-in first on PATH.

        :param shell: the step's `run:` text.
        :param extra: the step's own variables.
        :returns: the finished process.
        """
        script = self.root / "step"
        script.write_text(shell)
        env = {
            **os.environ,
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "CALLS": str(self.calls),
            "REACTIONS": str(self.reactions),
            "REVIEWS": str(self.reviews),
            "GH_TOKEN": "stand-in",
            "REPO": REPO,
            "NUMBER": NUMBER,
            **extra,
        }
        return subprocess.run(
            ["bash", "-e", str(script)],
            capture_output=True,
            encoding="utf-8",
            check=False,
            env=env,
        )

    def left(self) -> list[tuple[str, str]]:
        """Read the reactions the pull request carries after the calls.

        :returns: each reaction's author and content, in order.
        """
        pages = json.loads(self.reactions.read_text())
        return [
            (each["user"]["login"], each["content"]) for page in pages for each in page
        ]

    def recorded(self) -> list[list[str]]:
        """Read back the calls the stand-in received.

        :returns: each call's arguments, in order.
        """
        if not self.calls.exists():
            return []
        lines = self.calls.read_text().splitlines()
        return [line.split("\x1f")[:-1] for line in lines]


@pytest.fixture
def stand(tmp_path: Path) -> Stand:
    """Give a test the stand-in `gh`.

    :param tmp_path: a directory of this test's own.
    :returns: the stand-in's directory.
    """
    return Stand(tmp_path)


def reaction(login: str, content: str, number: int) -> dict[str, Any]:
    """Build a reaction as the API lists it.

    :param login: who posted it.
    :param content: what it is.
    :param number: its id.
    :returns: the reaction.
    """
    return {"id": number, "content": content, "user": {"login": login}}


POST = ["api", "--method", "POST", URL, "-f"]
GET = ["api", URL, "--paginate", "--slurp"]


def delete(number: int) -> list[str]:
    """Build the call that removes a reaction.

    :param number: the reaction's id.
    :returns: the call's arguments.
    """
    return ["api", "--method", "DELETE", f"{URL}/{number}", "--silent"]


def test_the_reaction_jobs_run_the_same_shell() -> None:
    """`start` and `outcome` differ in REACTION alone."""
    assert only_step("start")["run"] == only_step("outcome")["run"]


@pytest.mark.parametrize("content", REACTIONS)
def test_it_removes_the_job_s_others_then_adds_its_reaction(
    stand: Stand, content: str
) -> None:
    """Only the jobs' own reactions go, and not the one kept.

    :param stand: the stand-in.
    :param content: the reaction asked for.
    """
    mine = dict(zip(REACTIONS, range(1, 5), strict=True))
    stand.answer(
        reactions=[
            *(reaction(ACTIONS, kind, number) for kind, number in mine.items()),
            reaction(ACTIONS, "heart", 5),
            reaction("someone", "eyes", 6),
            reaction("claude[bot]", "+1", 7),
        ]
    )
    done = stand.run(only_step("start")["run"], REACTION=content)
    assert done.returncode == 0, done.stderr
    assert stand.recorded() == [
        GET,
        *(delete(number) for kind, number in mine.items() if kind != content),
        [*POST, f"content={content}", "--silent"],
    ]
    assert stand.left() == [
        (ACTIONS, content),
        (ACTIONS, "heart"),
        ("someone", "eyes"),
        ("claude[bot]", "+1"),
    ]


def test_an_empty_reaction_clears_and_posts_nothing(stand: Stand) -> None:
    """What `start` does where the review job does not run.

    :param stand: the stand-in.
    """
    stand.answer(reactions=[reaction(ACTIONS, "+1", 1), reaction("someone", "+1", 2)])
    done = stand.run(only_step("start")["run"], REACTION="")
    assert done.returncode == 0, done.stderr
    assert stand.recorded() == [GET, delete(1)]
    assert stand.left() == [("someone", "+1")]


def test_a_failed_post_leaves_no_earlier_verdict(stand: Stand) -> None:
    """The run that fails to post, then is cancelled, leaves no stale `+1`.

    Nothing runs after a cancellation, so what the shell left is what
    the pull request keeps.

    :param stand: the stand-in.
    """
    stand.answer(reactions=[reaction(ACTIONS, "+1", 1), reaction(ACTIONS, "eyes", 2)])
    done = stand.run(only_step("start")["run"], REACTION="eyes", FAIL_POST="1")
    assert done.returncode == 0, done.stderr
    assert done.stdout == f"{WARNING}posting eyes failed.\n"
    assert stand.recorded()[-1][:4] == POST[:4]
    assert stand.left() == [(ACTIONS, "eyes")]


def test_a_failed_removal_ends_the_shell(stand: Stand) -> None:
    """The limit the header states: a stale reaction stays, nothing is posted.

    :param stand: the stand-in.
    """
    stand.answer(reactions=[reaction(ACTIONS, "+1", 1)])
    done = stand.run(only_step("outcome")["run"], REACTION="-1", FAIL_DELETE="1")
    assert done.returncode == 0, done.stderr
    assert done.stdout == f"{WARNING}removing reaction 1 failed.\n"
    assert stand.recorded() == [GET, delete(1)]
    assert stand.left() == [(ACTIONS, "+1")]


@pytest.mark.parametrize("job", ["start", "outcome"])
def test_a_refused_list_is_a_warning_and_not_a_red_job(stand: Stand, job: str) -> None:
    """What run 43598529478 met: the API refused the list, with HTTP 403.

    The shell ends 0 so that the job is green, leaving the verdict check
    the only thing that decides the colour.

    :param stand: the stand-in.
    :param job: the reaction job.
    """
    stand.answer(reactions=[reaction(ACTIONS, "+1", 1)])
    done = stand.run(only_step(job)["run"], REACTION="confused", FAIL_LIST="1")
    assert done.returncode == 0, done.stderr
    assert done.stdout == f"{WARNING}listing them failed.\n"
    assert stand.recorded() == [GET]
    assert stand.left() == [(ACTIONS, "+1")]


def test_it_reads_every_page(stand: Stand) -> None:
    """A reaction on a later page goes too.

    :param stand: the stand-in.
    """
    stand.reactions.write_text(
        json.dumps([[reaction("someone", "eyes", 1)], [reaction(ACTIONS, "eyes", 2)]])
    )
    done = stand.run(only_step("start")["run"], REACTION="+1")
    assert done.returncode == 0, done.stderr
    assert delete(2) in stand.recorded()


@pytest.mark.parametrize(
    "content",
    [
        pytest.param("heart", id="another reaction"),
        pytest.param("EYES", id="upper case"),
        pytest.param("eyes ", id="trailing space"),
        pytest.param("+1 -f x=y", id="flags inside"),
    ],
)
def test_it_refuses_anything_else_and_does_not_call_gh(
    stand: Stand, content: str
) -> None:
    """Anything but one of the jobs' reactions is a warning, `gh` unrun.

    :param stand: the stand-in.
    :param content: the reaction asked for.
    """
    done = stand.run(only_step("start")["run"], REACTION=content)
    assert done.returncode == 0, done.stderr
    assert done.stdout.startswith(WARNING)
    assert not stand.recorded()


def review(login: str, body: str) -> dict[str, Any]:
    """Build a review as the API lists it.

    :param login: who posted it.
    :param body: its summary.
    :returns: the review.
    """
    return {"user": {"login": login}, "body": body}


CLAUDE = "claude[bot]"


@pytest.mark.parametrize(
    ("reviews", "expected", "status"),
    [
        pytest.param([review(CLAUDE, f"ACK {HEAD}\n")], "+1", 0, id="ack"),
        pytest.param(
            [review(CLAUDE, f"ACK {HEAD[:7]}\n\n- a point")], "+1", 0, id="short ack"
        ),
        pytest.param([review(CLAUDE, f"ACK {OTHER}")], "confused", 1, id="stale ack"),
        pytest.param(
            [review(CLAUDE, f"CHANGES REQUESTED {HEAD}")], "-1", 1, id="changes"
        ),
        pytest.param([review(CLAUDE, f"NACK {HEAD[:12]}")], "-1", 1, id="nack"),
        pytest.param(
            [review(CLAUDE, f"CHANGES REQUESTED {OTHER}")],
            "confused",
            1,
            id="stale changes",
        ),
        pytest.param([review(CLAUDE, f"NACK {OTHER}")], "confused", 1, id="stale nack"),
        pytest.param(
            [review(CLAUDE, f"NO VERDICT {HEAD}: the diff did not load")],
            "confused",
            1,
            id="no verdict",
        ),
        pytest.param([], "confused", 1, id="no review"),
        pytest.param(
            [review(CLAUDE, f"ACK {HEAD}"), review(CLAUDE, "a reading")],
            "confused",
            1,
            id="a reading after an ack",
        ),
        pytest.param(
            [review("someone", f"ACK {HEAD}")], "confused", 1, id="another's ack"
        ),
    ],
)
def test_the_verdict_check_writes_the_reaction_whatever_it_reports(
    stand: Stand,
    tmp_path: Path,
    reviews: list[dict[str, Any]],
    expected: str,
    status: int,
) -> None:
    """The outcome names the head, or it is `confused`; the colour is kept.

    :param stand: the stand-in.
    :param tmp_path: holds the step's output file.
    :param reviews: the reviews on the pull request.
    :param expected: the reaction the step writes.
    :param status: the step's exit status, 0 for an ack of the head alone.
    """
    stand.answer(reviews=reviews)
    output = tmp_path / "output"
    output.touch()
    done = stand.run(verdict_step()["run"], HEAD_SHA=HEAD, GITHUB_OUTPUT=str(output))
    assert (done.returncode, output.read_text()) == (status, f"reaction={expected}\n")


def test_the_outcome_reads_the_verdict_and_falls_back_to_confused() -> None:
    """The review job passes the check's reaction out, by the step's id."""
    review_job = jobs(WORKFLOW)["review"]
    assert verdict_step()["id"] == "verdict"
    assert review_job["outputs"] == {
        "reaction": "${{ steps.verdict.outputs.reaction }}"
    }
    assert only_step("start")["env"] == {**SHARED, "REACTION": EYES_WHERE}
    assert only_step("outcome")["env"] == {
        **SHARED,
        "REACTION": "${{ needs.review.outputs.reaction || 'confused' }}",
    }


# the eyes where the review job runs, nothing elsewhere
EYES_WHERE = (
    "${{ vars.CLAUDE_REVIEW_ENABLED == 'true'\n"
    "    && !github.event.pull_request.draft && 'eyes' || '' }}"
)


def conjuncts(condition: str) -> set[str]:
    """Cut a condition with no top-level `||` at its `&&`, spaces collapsed.

    :param condition: an expression inside `${{ }}`.
    :returns: the conjuncts.
    """
    text = " ".join(condition.split()).removeprefix("${{").removesuffix("}}")
    return {part.strip() for part in text.split("&&")}


def test_start_runs_on_every_head_and_puts_the_eyes_where_the_review_runs() -> None:
    """A draft push, or one with the switch off, still clears the reactions.

    `start`'s condition and the one choosing the eyes are the review
    job's, split: the switch and the draft check decide the eyes alone.
    So a `+1` on head A is gone once head B is pushed as a draft, which
    the shell's empty reaction then does (btclib-org/.github#2267).
    """
    start, review_job = jobs(WORKFLOW)["start"], jobs(WORKFLOW)["review"]
    eyes_where = only_step("start")["env"]["REACTION"]
    chosen = conjuncts(eyes_where.removesuffix(" && 'eyes' || '' }}") + " }}")
    assert eyes_where.endswith(" && 'eyes' || '' }}")
    assert conjuncts(start["if"]) | chosen == conjuncts(review_job["if"])
    assert chosen == {
        "vars.CLAUDE_REVIEW_ENABLED == 'true'",
        "!github.event.pull_request.draft",
    }
    assert not conjuncts(start["if"]) & chosen
    assert "needs" not in start
    assert "needs" not in review_job


def test_a_draft_push_clears_an_earlier_ack(stand: Stand) -> None:
    """Head A acked, head B pushed as a draft: A's `+1` goes, nothing comes.

    The empty reaction is what `EYES_WHERE` gives on a draft.

    :param stand: the stand-in.
    """
    stand.answer(reactions=[reaction(ACTIONS, "+1", 1)])
    done = stand.run(only_step("start")["run"], REACTION="")
    assert done.returncode == 0, done.stderr
    assert stand.left() == []


def test_the_outcome_follows_both_whatever_the_review_s_result() -> None:
    """It runs unless the run is cancelled, and not where the review skipped."""
    outcome = jobs(WORKFLOW)["outcome"]
    assert outcome["needs"] == ["start", "review"]
    assert outcome["if"] == ("${{ !cancelled() && needs.review.result != 'skipped' }}")


@pytest.mark.parametrize("job", ["start", "outcome"])
def test_a_reaction_job_holds_pull_requests_write_and_runs_nothing_of_the_head(
    job: str,
) -> None:
    """No checkout, no action, and no scope but `pull-requests: write`.

    :param job: the job's id.
    """
    assert jobs(WORKFLOW)[job]["permissions"] == {"pull-requests": "write"}
    assert all("uses" not in step for step in jobs(WORKFLOW)[job]["steps"])


def calling_grant() -> dict[str, str]:
    """Read the scopes this tree's calling job grants the callee.

    :returns: each scope against its level.
    """
    (calling,) = [
        job
        for job in jobs(CALLER).values()
        if "reusable-claude-review.yml" in job.get("uses", "")
    ]
    granted: dict[str, str] = calling["permissions"]
    return granted


def test_the_caller_grants_every_scope_the_callee_declares() -> None:
    """A scope the calling job leaves off ends the run as `startup_failure`.

    The header of `reusable-claude-review.yml` says why.
    """
    granted = calling_grant()
    for job in jobs(WORKFLOW).values():
        for scope, level in job["permissions"].items():
            assert granted.get(scope) in {level, "write"}, scope


def test_the_caller_grants_what_it_granted_before_the_reactions() -> None:
    """No tree's calling job needs a new scope for the reactions.

    Every caller of the organization grants these three for the review,
    so the reactions arrive with a tree's pin and nothing else.
    """
    assert calling_grant() == {
        "contents": "read",
        "pull-requests": "write",
        "id-token": "write",
    }
