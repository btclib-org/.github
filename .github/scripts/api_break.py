# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Decide whether `griffe check` found a break, and set the label from it.

`griffe check -f oneline` prints one finding per line, which
`check_public_api.py` reads, and exits 1 with findings. An uncaught
exception exits 1 too, with a traceback in place of findings: a package
absent at the base and a base that is no commit both do. So the exit
code alone cannot say there is a break. `classify` calls it one only
where every line of the output is a finding, and anything else is
`unknown`, which leaves the label as it is. `reusable-api-break.yml`
adds the findings of `api_gaps.py` to the output, in the same format.

    uv run --no-project --python 3.15 .github/scripts/api_break.py \
        classify "$status" "$findings" >> "$GITHUB_OUTPUT"
    uv run --no-project --python 3.15 .github/scripts/api_break.py \
        label "$broken" "$GITHUB_REPOSITORY" "$pull_request"

`label` never exits non-zero: the label is advisory, and a call that
failed, or an answer that is neither `true` nor `false`, is a warning
for the log.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

LABEL = "api-break"
_FINDING = re.compile(r"(.+?):(\d+): (\S+): (.*)")
_NOT_FOUND = "HTTP 404"


def classify(status: int, output: str) -> str:
    """Say whether the output of the comparison is a break.

    :param status: the higher of griffe's and `api_gaps.py`'s exit codes.
    :param output: what both printed, griffe's standard output and error
        and the script's standard output.
    :returns: `true` for a break, `false` for none, `unknown` otherwise.
    """
    if status == 0:
        return "false"
    lines = [line for line in output.splitlines() if line.strip()]
    if status == 1 and lines and all(_FINDING.fullmatch(line) for line in lines):
        return "true"
    return "unknown"


def calls(broken: str, repository: str, pull_request: str) -> list[list[str]]:
    """List the `gh` commands that set the label for an answer.

    :param broken: `true` or `false`; anything else asks nothing.
    :param repository: `owner/name`.
    :param pull_request: the pull request's number.
    :returns: the commands, none where the label stays as it is.
    """
    issue = f"repos/{repository}/issues/{pull_request}"
    if broken == "true":
        return [
            [
                "gh",
                "api",
                "--method",
                "POST",
                f"{issue}/labels",
                "-f",
                f"labels[]={LABEL}",
            ]
        ]
    if broken == "false":
        return [["gh", "api", "--method", "DELETE", f"{issue}/labels/{LABEL}"]]
    return []


def _run(argv: Sequence[str]) -> subprocess.CompletedProcess[str]:
    """Run a command, keeping what it printed and whatever it exited with."""
    return subprocess.run(  # noqa: S603
        argv, capture_output=True, check=False, encoding="utf-8"
    )


def label(
    broken: str,
    repository: str,
    pull_request: str,
    run: Callable[[Sequence[str]], subprocess.CompletedProcess[str]] | None = None,
) -> list[str]:
    """Set the label, and report what could not be done.

    A 404 on removing the label means it was not there, which is the
    state asked for. Any other failure is a warning.

    :param broken: `true` or `false`; anything else is warned of.
    :param repository: `owner/name`.
    :param pull_request: the pull request's number.
    :param run: runs a command; `subprocess.run` where none is given.
    :returns: the warnings, empty where all went as asked.
    """
    execute = run or _run
    if broken not in {"true", "false"}:
        return [f"no answer to set the label from: {broken!r}"]
    warnings = []
    for argv in calls(broken, repository, pull_request):
        done = execute(argv)
        removing = argv[3] == "DELETE"
        if done.returncode and not (removing and _NOT_FOUND in done.stderr):
            why = " ".join(done.stderr.split())
            warnings.append(f"{' '.join(argv)} failed: {why}")
    return warnings


def main(argv: Sequence[str] | None = None) -> int:
    """Run one of the two commands.

    :param argv: the arguments, `sys.argv[1:]` where none are given.
    :returns: 0 always: the label is advisory.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("classify")
    one.add_argument("status", type=int)
    one.add_argument("findings", type=Path)
    two = sub.add_parser("label")
    two.add_argument("broken")
    two.add_argument("repository")
    two.add_argument("pull_request")
    args = parser.parse_args(argv)
    if args.command == "classify":
        text = args.findings.read_text(encoding="utf-8", errors="replace")
        print(f"broken={classify(args.status, text)}")
    else:
        for warning in label(args.broken, args.repository, args.pull_request):
            print(f"::warning::{warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
