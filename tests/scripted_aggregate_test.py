# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for how `workflows_test.py` reads a call of `check_run_jobs.py`.

`workflows_test.py` asks every tree, and needs the network to clone them:
what it accepts as a call has to be proved on jobs written here, so that
a shape it wrongly passes is red without a tree carrying it. The shape
that matters is the one btclib-org/.github#1424 was: a result that is
named in the step and not given to the script, which the step's text
holds all the same in a comment or an `echo`.
"""

from __future__ import annotations

from typing import Any

import pytest

from .workflows_test import checkout_faults, command_faults, scripted

_SCRIPT = "btclib-org-github/.github/scripts/check_run_jobs.py"
_RESULT = "${{ needs.%s.result }}"


def _job(
    run: str,
    needs: tuple[str, ...] = ("analyze",),
    env: dict[str, str] | None = None,
    path: str = "btclib-org-github",
) -> dict[str, Any]:
    """Build an aggregate job whose step runs `run`, as a tree writes it."""
    holders = {f"{name.upper()}_RESULT": _RESULT % name for name in needs}
    return {
        "needs": list(needs),
        "permissions": {"contents": "read", "actions": "read"},
        "steps": [
            {
                "uses": "actions/checkout@" + "0" * 40,
                "with": {
                    "repository": "btclib-org/.github",
                    "ref": "main",
                    "path": path,
                    "persist-credentials": False,
                    "sparse-checkout": ".github/scripts",
                },
            },
            {
                "env": {"GH_TOKEN": "${{ github.token }}", **holders, **(env or {})},
                "run": run,
            },
        ],
    }


_ONE = f'python3 {_SCRIPT} analyze "${{ANALYZE_RESULT}}"'
_TWO = (
    f'python3 {_SCRIPT} changes "${{CHANGES_RESULT}}" coverage "${{COVERAGE_RESULT}}"'
)
_LINES = {
    "RESULTS": "changes " + _RESULT % "changes" + "\ncoverage " + _RESULT % "coverage"
}
_JOBS = ("changes", "coverage")


@pytest.mark.parametrize(
    ("run", "needs", "env"),
    [
        (_ONE, ("analyze",), None),
        (_ONE.replace("python3 ", ""), ("analyze",), None),
        (f"{_ONE} \\\n --row analyze=x", ("analyze",), None),
        (_TWO, _JOBS, None),
        (f"python3 {_SCRIPT} --results-env RESULTS", _JOBS, _LINES),
        (f"# analyze $X\n{_ONE}\necho done", ("analyze",), None),
    ],
)
def test_a_call_giving_each_result_to_the_script_is_accepted(
    run: str, needs: tuple[str, ...], env: dict[str, str] | None
) -> None:
    """The pair, or the variable, in the script's own arguments."""
    job = _job(run, needs, env)

    assert scripted(job)
    assert command_faults(job) == []
    assert checkout_faults(job) == []


@pytest.mark.parametrize(
    ("run", "needs", "env"),
    [
        # the pair only in a comment, the script called without it
        (f'python3 {_SCRIPT}\n# analyze "${{ANALYZE_RESULT}}"', ("analyze",), None),
        # the pair only in an echo
        (f'echo analyze "${{ANALYZE_RESULT}}"\npython3 {_SCRIPT}', ("analyze",), None),
        (f'python3 {_SCRIPT} ; echo analyze "${{ANALYZE_RESULT}}"', ("analyze",), None),
        # a second job's pair only in a comment
        (
            (
                f'python3 {_SCRIPT} changes "${{CHANGES_RESULT}}"\n'
                '# coverage "${COVERAGE_RESULT}"'
            ),
            _JOBS,
            None,
        ),
        # --results-env only in an echo, or given in the `=` form
        (f"echo --results-env RESULTS\npython3 {_SCRIPT}", _JOBS, _LINES),
        (f"python3 {_SCRIPT} --results-env=RESULTS", _JOBS, _LINES),
        # a pair for another job, or another variable, or unbraced
        (f'python3 {_SCRIPT} other "${{ANALYZE_RESULT}}"', ("analyze",), None),
        (f'python3 {_SCRIPT} analyze "${{CHANGES_RESULT}}"', ("analyze",), None),
        (f'python3 {_SCRIPT} analyze "$ANALYZE_RESULT"', ("analyze",), None),
        # a results variable with a line short
        (
            f"python3 {_SCRIPT} --results-env RESULTS",
            _JOBS,
            {"RESULTS": "changes " + _RESULT % "changes"},
        ),
    ],
)
def test_a_result_named_in_the_step_and_not_given_to_the_script_is_refused(
    run: str, needs: tuple[str, ...], env: dict[str, str] | None
) -> None:
    """A comment, an `echo` and a near miss are none of them the call."""
    job = _job(run, needs, env)

    assert scripted(job)
    assert command_faults(job) != []


@pytest.mark.parametrize(
    "run",
    [
        f"echo python3 {_SCRIPT} analyze $X",
        f"# python3 {_SCRIPT}",
        "true",
    ],
)
def test_a_step_that_does_not_run_the_script_is_not_a_scripted_step(run: str) -> None:
    """The script named in a comment or printed is no call, so no shape."""
    assert not scripted(_job(run))


def test_the_script_is_run_from_the_path_its_checkout_names() -> None:
    """A path in a comment, or another directory, is refused."""
    elsewhere = _job(_ONE, path="elsewhere")
    commented = _job(f"# {_SCRIPT}\npython3 other/.github/scripts/check_run_jobs.py")

    assert checkout_faults(elsewhere) != []
    assert checkout_faults(commented) != []


def test_a_step_that_cannot_be_read_is_not_taken_for_one_that_never_calls() -> None:
    """A quoted string over several lines beside a real call is a fault.

    It does not lex a line at a time. Read as no call at all, the job
    would be no scripted aggregate and no test would ask it anything.
    """
    run = (
        f"python3 {_SCRIPT} analyze \"${{ANALYZE_RESULT}}\"\nawk 'BEGIN {{\n  x = 1 }}'"
    )
    job = _job(run)

    assert scripted(job)
    assert command_faults(job) != []
