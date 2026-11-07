# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The guard that `claude-review.yml`'s `issue_comment` decline rests on.

zizmor's dangerous-triggers is declined on that trigger because no job
of `reusable-claude-review.yml` answers a comment whose author the
mention job's `if:` does not name. zizmor reads the decline and not the
guard, so without these tests nothing turns red the day the guard goes
(btclib-org/.github#1813).

The review's `allowed_bots` is read here too, against the bot that
`reusable-claude-implement.yml` opens its pull requests as, and so is its
deny list.
"""

from __future__ import annotations

import re
import shlex

from . import ROOT
from .mention_bound_test import SESSION_TOOLS
from .workflows_test import jobs

# the reusable review, which holds both jobs
WORKFLOW = ROOT / ".github/workflows/reusable-claude-review.yml"

# the caller in this tree, which holds the trigger and its decline
CALLER = ROOT / ".github/workflows/claude-review.yml"

# the workflow whose pull requests a bot opens
IMPLEMENT = ROOT / ".github/workflows/reusable-claude-implement.yml"

# the tools the agent-mode jobs deny, for the reason the review step's
# comment gives
AGENT_DENIED = SESSION_TOOLS | {
    "CronCreate",
    "RemoteTrigger",
    "PushNotification",
    "ProposeGoal",
}

# the mention job's condition on the commenter, spaced as one line
GUARD = (
    """contains(fromJSON('["OWNER", "MEMBER", "COLLABORATOR"]'), """
    "github.event.comment.author_association)"
)


def condition(job: str) -> str:
    """Read a job's `if:` with its whitespace collapsed.

    :param job: the job's id.
    :returns: the condition on one line.
    """
    return " ".join(jobs(WORKFLOW)[job]["if"].split())


def test_the_mention_answers_only_the_repository_s_own_commenters() -> None:
    """The guard is a conjunct of the whole condition, not of one event's.

    It sits between the switch and the two event branches, so a comment
    of either event passes it or runs nothing.
    """
    assert condition("mention").startswith(
        f"${{{{ vars.CLAUDE_REVIEW_ENABLED == 'true' && {GUARD} && (("
    )


def test_the_review_answers_no_comment() -> None:
    """The review job runs on `pull_request` alone."""
    assert "&& github.event_name == 'pull_request' &&" in condition("review")


def test_the_decline_sits_on_the_trigger() -> None:
    """The caller declines the finding on `issue_comment` and nowhere else."""
    lines = CALLER.read_text(encoding="utf-8").splitlines()
    declined = [line for line in lines if "ignore[dangerous-triggers]" in line]
    assert declined == ["  issue_comment: # zizmor: ignore[dangerous-triggers]"]


def test_the_review_admits_the_agent_s_pull_requests() -> None:
    """`allowed_bots` names the bot the implement workflow commits as.

    `publish` opens the pull request with the App's token, so the bot its
    commit names is the actor of the review's `pull_request` run, which
    the action refuses unless the input names it. It is not `*`, for the
    reason the input's comment gives.
    """
    (step,) = [
        step
        for step in jobs(WORKFLOW)["review"]["steps"]
        if "allowed_bots" in step.get("with", {})
    ]
    named = step["with"]["allowed_bots"].split(",")
    (commit,) = [
        step["run"]
        for step in jobs(IMPLEMENT)["publish"]["steps"]
        if step.get("name") == "Commit the edit"
    ]
    bot = re.search(r"user\.name='([^']+)'", commit)

    assert bot is not None
    assert "*" not in named
    assert bot[1] in named


def test_the_review_denies_what_its_allow_list_does_not_keep_out() -> None:
    """The step's comment says why its allow list does not keep these out.

    The action takes every argument after `--disallowedTools` up to the
    next one starting `--`, and splits each on commas
    (btclib-org/.github#2115).
    """
    (step,) = [
        step for step in jobs(WORKFLOW)["review"]["steps"] if step.get("id") == "review"
    ]
    args = shlex.split(step["with"]["claude_args"])
    values: list[str] = []
    for arg in args[args.index("--disallowedTools") + 1 :]:
        if arg.startswith("--"):
            break
        values.append(arg)
    assert {tool for value in values for tool in value.split(",")} >= AGENT_DENIED
