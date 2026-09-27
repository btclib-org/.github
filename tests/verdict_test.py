# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for `workflows_test.py`'s `verdict`, on workflows built here.

That function runs a listing aggregate's step against stubs, and a run
over the organization cannot show what the stubs hand the step: these
build steps that print it, and a step that judges the result against one
that does not.

Nothing here reaches the network, so no `integration` marker, for the
reason `pins_test.py` gives. What it needs is `bash` and `jq` on `PATH`,
which the runner has as the step's own runner does.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yaml

from .workflows_test import aggregates, refusals, verdict

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

LIST = (
    'gh api --paginate "repos/${GITHUB_REPOSITORY}/actions/runs/'
    '${GITHUB_RUN_ID}/jobs?per_page=100" '
    '--jq \'.jobs[] | "\\(.conclusion // "unfinished")\\t\\(.name)"\'\n'
)
"""The listing's call, printing each row as the aggregates' steps read it."""

JUDGED = (
    'for result in "${A_RESULT}" "${B_RESULT}"; do\n'
    '  case "${result}" in success | skipped) ;; *) exit 1 ;; esac\n'
    "done\n"
)
"""A step judging every result, which is section 10's shape."""


def aggregate(
    root: Path, run: str, ids: tuple[str, ...] = ("a", "b")
) -> tuple[Path, dict[str, Any]]:
    """Write a workflow of called jobs and their aggregate, and return both.

    Each id's result reaches the step as `<ID>_RESULT`, the way the
    organization's aggregates name it.

    :param root: the directory to write into.
    :param run: the aggregate's listing step's `run:`.
    :param ids: the jobs the aggregate `needs`.
    :returns: the file, and the aggregate job's own mapping.
    """
    env = {"GH_TOKEN": "${{ github.token }}"} | {
        f"{i.upper()}_RESULT": f"${{{{ needs.{i}.result }}}}" for i in ids
    }
    document = {
        "on": "push",
        "jobs": {i: {"name": f"Job {i}", "runs-on": "ubuntu-latest"} for i in ids}
        | {
            "passed": {
                "name": "codeql: every job passed",
                "needs": list(ids),
                "runs-on": "ubuntu-latest",
                "steps": [{"env": env, "run": run}],
            }
        },
    }
    path = root / "fragment.yml"
    path.write_text(yaml.safe_dump(document), encoding="utf-8")
    return path, aggregates(path)["passed"]


def test_the_listing_holds_the_needs_rows_passed_and_the_own_row_unfinished(
    tmp_path: Path,
) -> None:
    """What the step sees, which is what makes its verdict about the results.

    :param tmp_path: the directory the workflow and the stubs go in.
    """
    path, job = aggregate(tmp_path, LIST)
    (tmp_path / "run").mkdir()
    ran = verdict(path, job, {"a": "failure", "b": "success"}, tmp_path / "run")
    assert (ran.status, ran.stubbed) == (0, False), ran.output
    assert ran.output.splitlines() == [
        "success\tJob a",
        "success\tJob b",
        "unfinished\tcodeql: every job passed",
    ]


def test_each_result_reads_its_own_id_and_another_expression_empty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`${{ github.token }}` is not a result, and this process's is not it.

    :param tmp_path: the directory the workflow and the stubs go in.
    :param monkeypatch: what gives this process a token the step must not see.
    """
    monkeypatch.setenv("GH_TOKEN", "this process's")
    run = (
        '[ "${A_RESULT}" = cancelled ] && [ "${B_RESULT}" = success ]'
        ' && [ -z "${GH_TOKEN}" ]\n'
    )
    path, job = aggregate(tmp_path, f"{LIST}{run}")
    (tmp_path / "run").mkdir()
    results = {"a": "cancelled", "b": "success"}
    assert verdict(path, job, results, tmp_path / "run").status == 0


def test_a_step_judging_every_result_is_refused_nothing(tmp_path: Path) -> None:
    """The shape section 10 asks for, which is the positive control.

    :param tmp_path: the directory the workflow and the stubs go in.
    """
    path, job = aggregate(tmp_path, f"{LIST}{JUDGED}")
    assert refusals(path, job, tmp_path) == []


def test_a_step_judging_the_rows_alone_passes_every_probe(tmp_path: Path) -> None:
    """Every row passing, a step not reading the results has nothing to fail on.

    :param tmp_path: the directory the workflow and the stubs go in.
    """
    path, job = aggregate(tmp_path, LIST)
    assert refusals(path, job, tmp_path) == [
        "a=failure: passes",
        "a=cancelled: passes",
        "b=failure: passes",
        "b=cancelled: passes",
    ]


def test_a_step_refusing_failure_alone_passes_cancelled(tmp_path: Path) -> None:
    """A step naming the one bad result it expects, and missing the other.

    :param tmp_path: the directory the workflow and the stubs go in.
    """
    run = '[ "${A_RESULT}" != failure ] && [ "${B_RESULT}" != failure ]\n'
    path, job = aggregate(tmp_path, f"{LIST}{run}")
    assert refusals(path, job, tmp_path) == [
        "a=cancelled: passes",
        "b=cancelled: passes",
    ]


def test_a_step_judging_one_needs_job_passes_the_other(tmp_path: Path) -> None:
    """Every result set bad at once would hide this: `b` failing alone.

    :param tmp_path: the directory the workflow and the stubs go in.
    """
    run = 'case "${A_RESULT}" in success | skipped) ;; *) exit 1 ;; esac\n'
    path, job = aggregate(tmp_path, f"{LIST}{run}")
    assert refusals(path, job, tmp_path) == ["b=failure: passes", "b=cancelled: passes"]


def test_a_call_the_stub_refuses_is_not_the_steps_refusal(tmp_path: Path) -> None:
    """A second `gh` call on the failure path, whose status is the stub's.

    :param tmp_path: the directory the workflow and the stubs go in.
    """
    run = (
        'case "${A_RESULT}${B_RESULT}" in successsuccess) ;;'
        " *) gh run view; exit 0 ;; esac\n"
    )
    path, job = aggregate(tmp_path, f"{LIST}{run}")
    wrong = refusals(path, job, tmp_path)
    assert wrong
    assert all(line.endswith("which the stub refuses") for line in wrong), wrong


def test_a_relative_write_lands_in_the_scratch_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The step's working directory is the run's own, not this process's.

    :param tmp_path: the directory the workflow and the stubs go in.
    :param monkeypatch: what moves this process into a directory of its own.
    """
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    path, job = aggregate(tmp_path, f"{LIST}touch written\n")
    (tmp_path / "run").mkdir()
    verdict(path, job, {"a": "success", "b": "success"}, tmp_path / "run")
    assert list(elsewhere.iterdir()) == []
    assert (tmp_path / "run" / "cwd" / "written").exists()
