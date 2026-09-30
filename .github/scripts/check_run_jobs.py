# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Fail an aggregate job unless every other job of its run succeeded.

The job is the one a branch rule can name where no cell of a called
workflow's matrix can be, and it asks the run's own jobs listing what
happened rather than trusting `needs.<id>.result`: `needs` cannot tell a
matrix cell that died in *Set up job* from one that ran and passed
(btclib-org/btclib#1001). The listing is read whole, printed before it is
judged, and judged on each row's conclusion:

- a conclusion that is not `success` or `skipped` fails the job, and so
  does a row still unfinished, unless the next paragraph accepts it or
  it is the one row the last bullet allows;
- the `needs` job's own result is judged beside the listing, and a result
  that is neither `success` nor `skipped` fails the job whatever the
  listing shows (btclib-org/.github#1424). That turns a pass into a fail
  and never the reverse;
- exactly one row of the run may be unfinished besides the accepted ones,
  and it is this job's. It is counted and not excluded by name, a name
  being what goes stale when the job is renamed, and none unfinished at
  all is refused too: a listing with no job running is not a listing of
  the run this script is running in.

An unfinished row is accepted where it is a row of the `needs` job, whose
name starts with the job's id and ` / `, the prefix a called workflow's
jobs are listed under, and where the `needs` job's own result is
`success` or `skipped`. `needs` does not let this job start before that
job concludes, so such a row is the listing lagging and not the run
(btclib-org/.github#1395). With any other result nothing is accepted this
way.

Such a row is read again before it is accepted, because the result is not
the listing's equal, and a row that concludes between two reads is judged
on its conclusion. Only a row that would be accepted is waited for: a
listing with none is read once (btclib-org/.github#1416). What is waited
for is GitHub's jobs listing catching up with the run's own jobs, which no
run can arrange.

The wait counts against a deadline and not against a number of reads.
`DEFAULT_TIMEOUT` is chosen rather than measured, since nothing times how
long the listing lags, and it is the one number to be read against the
calling job's `timeout-minutes`. The last read is taken at the deadline,
and a read that is still lagging then is accepted. What is not bounded
here is one `gh` call: the job's `timeout-minutes` ends that. A `gh` that
fails is the job's failure and is not read again, a failed read being no
lagging row.

The verdict is in this script and not in the workflow for the reason
section 10 of `README.md` gives for a wait: what the job exists for is
the verdict it reaches when the wait runs out, and no trigger reaches it.
`tests/check_run_jobs_test.py` reaches it: it substitutes the listing and
the clock.

Standard library only, on the runner's own `python3`: the job installs
nothing and has none of the calling tree's source, so the script sits in
a second checkout under a `path:`, sparse on `.github/scripts` as
`reusable-wait-for-index.yml`'s is. The runner supplies `gh`, and
`GITHUB_REPOSITORY` and `GITHUB_RUN_ID` name what it reads. The token
reaches `gh` through `GH_TOKEN`, and the job needs `actions: read` for
it.

    python3 btclib-org-github/.github/scripts/check_run_jobs.py \
        analyze "$ANALYZE_RESULT"
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from typing import NamedTuple

# what the listing has to settle within, in seconds: chosen rather than
# measured, and read against the calling job's own `timeout-minutes`
DEFAULT_TIMEOUT = 30.0
# between two reads of the listing
DEFAULT_INTERVAL = 10.0
# the conclusion of a row that has none yet
UNFINISHED = "unfinished"
# the two conclusions that are not a failure
PASSED = ("success", "skipped")


class Run(NamedTuple):
    """The run whose jobs are read: the repository and the run's own id."""

    repository: str
    run_id: str


class Row(NamedTuple):
    """One job of the run, as the listing shows it."""

    conclusion: str
    status: str
    name: str

    def line(self) -> str:
        """Return the row as the log shows it, its columns tab-separated."""
        return f"{self.conclusion}\t{self.status}\t{self.name}"


def list_jobs(run: Run) -> list[Row]:
    """Read every row of the run's jobs listing, every page of it.

    `.status` is kept beside the conclusion so that an unfinished job says
    which kind it is: queued and running are one word to `.conclusion` and
    two facts to a reader of the log. A job with no conclusion yet is
    `UNFINISHED`.
    """
    answer = subprocess.run(  # noqa: S603
        [  # noqa: S607
            "gh",
            "api",
            "--paginate",
            f"repos/{run.repository}/actions/runs/{run.run_id}/jobs?per_page=100",
            "--jq",
            ".jobs[] | {conclusion, status, name}",
        ],
        check=True,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )
    rows = []
    for line in answer.stdout.splitlines():
        if line.strip():
            job = json.loads(line)
            rows.append(
                Row(job["conclusion"] or UNFINISHED, job["status"], job["name"])
            )
    return rows


def prefix_of(needs: str, result: str) -> str:
    """Return the prefix of the rows this job accepts unfinished, or none."""
    return f"{needs} / " if result in PASSED else ""


def accepted(row: Row, prefix: str) -> bool:
    """Return whether the row is unfinished and one the `needs` job owns."""
    return row.conclusion == UNFINISHED and prefix != "" and row.name.startswith(prefix)


def read(run: Run, prefix: str, timeout: float, interval: float) -> list[Row]:
    """Read the listing until no row it would accept is unfinished.

    The listing returned is the last one read, which holds the rows that
    were still lagging at the deadline.
    """
    deadline = time.monotonic() + timeout
    while True:
        rows = list_jobs(run)
        lagging = [row for row in rows if accepted(row, prefix)]
        left = deadline - time.monotonic()
        if not lagging or left <= 0:
            return rows
        pause = min(interval, left)
        print(f"listed unfinished, read again in {pause:g} s:")
        print("\n".join(row.line() for row in lagging))
        time.sleep(pause)


def annotate(message: str, rows: list[Row]) -> None:
    """Print an error annotation that names the rows it is about.

    An annotation is what the checks page shows without the log being
    opened. `%0A` is a newline to one, and the tab goes with it: the
    columns line up in a log and not in this.
    """
    lines = "".join(f"%0A{row.line().replace(chr(9), ' ')}" for row in rows)
    print(f"::error::{message}{lines}")


def judge(rows: list[Row], needs: str, result: str) -> int:
    """Print what the listing shows and say whether the run passed."""
    prefix = prefix_of(needs, result)
    lagging = [row for row in rows if accepted(row, prefix)]
    counted = [
        row
        for row in rows
        if row.conclusion == UNFINISHED and not accepted(row, prefix)
    ]
    bad = [row for row in rows if row.conclusion not in (*PASSED, UNFINISHED)]
    # printed before it is judged: the job whose purpose is to be trusted
    # is the one that has to be able to say what it saw
    print("\n".join(row.line() for row in rows))
    if lagging:
        print(f"still listed unfinished, accepted as {needs}'s ({result}):")
        print("\n".join(row.line() for row in lagging))
    verdict = 0
    if result not in PASSED:
        annotate(f"{needs}'s own result is '{result}'", [])
        verdict = 1
    if bad:
        annotate("these jobs of the run did not succeed:", bad)
        verdict = 1
    if len(counted) != 1:
        # no colon on this one, and rows after it only if there are any:
        # nothing unfinished is the case that says nothing, and a colon
        # would promise a list
        annotate(
            f"this check should be the run's one unfinished job; {len(counted)} are",
            counted,
        )
        verdict = 1
    return verdict


def check(run: Run, needs: str, result: str, timeout: float, interval: float) -> int:
    """Read the run's listing, waiting for the rows it lags on, and judge it."""
    prefix = prefix_of(needs, result)
    try:
        rows = read(run, prefix, timeout, interval)
    except subprocess.CalledProcessError as error:
        print(f"::error::`gh api` exited {error.returncode} reading the run's jobs")
        return 1
    return judge(rows, needs, result)


def main(argv: list[str] | None = None) -> int:
    """Read the `needs` job and its result, and judge the run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("needs", help="the id of the job this one needs")
    parser.add_argument("result", help="that job's `needs.<id>.result`")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID", ""))
    args = parser.parse_args(argv)
    if not (args.repository and args.run_id):
        parser.error("the run is named by GITHUB_REPOSITORY and GITHUB_RUN_ID")
    return check(
        Run(args.repository, args.run_id),
        args.needs,
        args.result,
        args.timeout,
        args.interval,
    )


if __name__ == "__main__":
    raise SystemExit(main())
