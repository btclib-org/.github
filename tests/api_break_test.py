# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for `reusable-api-break.yml`, the pull request's advisory label.

The label informs a review and gates nothing (btclib-org/.github#1674),
and a fork's pull request gets no write token, so what is asked here is
what keeps both true: the job fails no check, holds the one write it
needs, labels only a pull request of the calling repository, and uses
none of the triggers that would hand a fork's code a write token.
"""

from __future__ import annotations

from typing import Any

import yaml

from . import ROOT

_WORKFLOW = ROOT / ".github" / "workflows" / "reusable-api-break.yml"
_LABELS = ROOT / ".github" / "labels.yml"


def _parsed() -> dict[Any, Any]:
    """Return the workflow, parsed."""
    parsed: dict[Any, Any] = yaml.safe_load(_WORKFLOW.read_text(encoding="utf-8"))
    return parsed


def _job() -> dict[str, Any]:
    """Return the workflow's one job."""
    jobs: dict[str, Any] = _parsed()["jobs"]
    assert list(jobs) == ["api-break"]
    job: dict[str, Any] = jobs["api-break"]
    return job


def _step(name: str) -> dict[str, Any]:
    """Return the step of that name."""
    steps: list[dict[str, Any]] = _job()["steps"]
    return next(step for step in steps if step.get("name") == name)


def test_the_job_is_advisory() -> None:
    """The job concludes green whatever a step answers."""
    assert _job()["continue-on-error"] is True


def test_the_workflow_declares_no_trigger_but_the_call() -> None:
    """A fork's code never runs with a write token through a trigger here.

    `pull_request_target` and `workflow_run` are the two that would.
    """
    on = _parsed().get("on", _parsed().get(True))
    assert list(on) == ["workflow_call"]


def test_the_write_is_the_job_s_alone() -> None:
    """The workflow reads, and the job elevates `pull-requests` only."""
    assert _parsed()["permissions"] == {"contents": "read"}
    assert _job()["permissions"] == {"contents": "read", "pull-requests": "write"}


def test_the_label_is_set_only_on_a_pull_request_of_the_calling_repository() -> None:
    """A fork's token is read-only, so the step declines it by name."""
    condition = _step("Set the label")["if"]
    assert (
        "github.event.pull_request.head.repo.full_name == github.repository"
        in condition
    )
    assert "!= 'unknown'" in condition


def test_the_comparison_is_against_the_base_commit() -> None:
    """The base is the pull request's, handed through `env:` and not inlined."""
    step = _step("Compare the public API with the base")
    assert step["env"]["BASE_SHA"] == "${{ github.event.pull_request.base.sha }}"
    assert '-a "$BASE_SHA"' in step["run"]
    assert "${{" not in step["run"]


def test_a_failure_to_compare_leaves_the_label_as_it_is() -> None:
    """A griffe exit above 1 answers `unknown`, and nothing is set."""
    run = _step("Compare the public API with the base")["run"]
    assert '"$status" -gt 1' in run
    assert "broken=unknown" in run


def test_the_label_is_added_on_a_break_and_removed_otherwise() -> None:
    """Both calls are made, and neither is allowed to fail the step."""
    run = _step("Set the label")["run"]
    assert "POST" in run
    assert "labels[]=api-break" in run
    assert "DELETE" in run
    assert run.count("||") == 2


def test_the_findings_go_to_the_job_summary() -> None:
    """A fork's pull request is not labelled, so the summary is where it is read."""
    step = _step("Report the finding")
    assert "$GITHUB_STEP_SUMMARY" in step["run"]
    assert "github.event.pull_request.head" not in step.get("if", "")


def test_the_label_is_owed_by_the_publishing_trees_alone() -> None:
    """`labels.yml` names every tree that calls `reusable-public-api.yml`."""
    labels = yaml.safe_load(_LABELS.read_text(encoding="utf-8"))["labels"]
    label = next(entry for entry in labels if entry["name"] == "api-break")
    assert sorted(label["repositories"]) == [
        "bitcoin-core-rpc",
        "btclib",
        "btclib-ecc",
        "btclib-mnemonics",
        "btclib-node",
        "btclib-secp256k1",
        "btclib-wallet",
    ]
