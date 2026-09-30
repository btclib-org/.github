# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Install the version a release just published, retrying while it is unserved.

`wait_for_pypi_release.py` asks the index from one runner, and every cell
of `pypi-install.yml` then reads it through the edge that cell reaches: an
edge can still hold the page from before the upload after the wait has
passed. The cell's installer then fails to resolve the pinned requirement
and the run reports a failure that a later attempt would not have had. So
each cell installs through this script, which runs the installer it is
given and, while the installer says the pinned requirement is not
resolvable, runs it again after a pause.

What is retried is that one message and nothing else. `pip` prints
`No matching distribution found for <requirement>` and `uv` prints `no
version of <requirement>`, and the requirement is the package, its extras
if it has any, and `==` the version. Every other failure ends the script
at once with the installer's own status: an sdist that does not build is
the cell's verdict and waiting changes nothing about it.

The message does not say why. `pip` prints it both where the index does
not serve the version yet and where it serves the version with no file
this cell can install (a wheel for another platform, an interpreter the
files exclude). So the deadline's `::error::` names both causes, and
what it cannot do is tell them apart: the installer's own output, shown
above it, is where a reader looks.

The installer's output is shown as it arrives, not when the attempt
ends: an sdist build takes minutes, and a log that is silent for that
long reads as a hang.

The budget is a deadline and not a count of attempts, for the reason
`wait_for_pypi_release.py`'s docstring gives. `DEFAULT_TIMEOUT` is chosen
rather than measured, since nothing times how long an edge keeps a stale
page, and it is the one number to be read against the calling job's
`timeout-minutes`. It bounds the retrying, and an attempt that has begun
is the installer's to finish: the job's timeout is what ends an attempt
that never returns.

The installer command is the caller's, given after `--`, and the script
appends the requirement to it. Two things about it are the caller's to
get right, because the script cannot see them:

- Its cache is off. The index sends `Cache-Control: max-age` on the
  page, and neither `pip` nor `uv` asks again for a page it holds for
  that long, so a retry with the cache on reads back the page it failed
  on. That is `--no-cache-dir` for `pip` and `--no-cache` for `uv`.
- It installs into the cell's own environment, which is the whole point
  of the cell. The script starts the installer as a child and passes
  the environment through, so the target is whatever the installer
  finds there: `python -m pip` of the `setup-python` interpreter, or
  `uv pip` into the `.venv` the step made.

An empty tag is a run with no release behind it, and the script then
installs the unpinned requirement once, with no retry: nothing is
waited for and the newest version is the one wanted.

Standard library only, and no syntax or name newer than the oldest
interpreter a cell runs, since the script runs on the cell's own
interpreter and not on one it fetches: `python` in a `setup-python`
cell, `uv run --no-project python` in a cell whose environment `uv`
made. A pinned `uv run --no-project --python 3.15`, which
`reusable-wait-for-index.yml` uses, would need `uv` set up in a cell
that has no other use for it and would run the script on an interpreter
that is not the cell's, while what the cell measures is the cell's own.
The scripts sit in a second checkout under a `path:`, sparse on
`.github/scripts` as `reusable-wait-for-index.yml`'s is. That checkout
is admissible in a job that has none of the calling tree's own source
for the reason given there, and the `path:` keeps that repository's root
files, `pyproject.toml` among them, out of the directory the cell runs
in.

No trigger reaches the deadline. What is waited on is an edge that is
stale for as long as it is, which no run can arrange, so
`tests/install_published_release_test.py` is what drives the retry, the
deadline and the error: it substitutes the installer and the clock.

    python btclib-org-github/.github/scripts/install_published_release.py \
        "$PACKAGE" "$TAG" -- \
        python -m pip install --no-cache-dir --only-binary "$PACKAGE"
"""

from __future__ import annotations

import argparse
import io
import re
import subprocess
import sys
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

# what a runner has to be served the pinned version within, in seconds:
# chosen rather than measured, and read against the calling job's own
# `timeout-minutes`
DEFAULT_TIMEOUT = 600.0
# between two attempts: long enough not to hammer the index, short enough
# that the install ends near the moment the edge catches up
DEFAULT_INTERVAL = 15.0


def unresolvable(output: str, requirement: str, version: str) -> bool:
    """Return whether the installer says it cannot resolve this pin.

    The name matches however the installer spells it (`pip` echoes the
    requirement as typed, `uv` normalizes it), the extras are any, and
    the version is followed by nothing that would make it another one.
    """
    name = re.escape(requirement.partition("[")[0])
    name = re.sub(r"(\\?[-_.])+", "[-_.]+", name)
    pattern = (
        rf"(No matching distribution found for|no version of) "
        rf"{name}(\[[^\]]*\])?=={re.escape(version)}(?!\w|\.\w)"
    )
    return re.search(pattern, output, re.IGNORECASE) is not None


def run_installer(command: list[str], emit: Callable[[str], None]) -> tuple[int, str]:
    """Run the installer, handing each line to `emit` as it arrives.

    Standard error is merged into standard output so that the order the
    installer wrote in is the order it is shown and searched in.
    """
    lines: list[str] = []
    with subprocess.Popen(  # noqa: S603
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        # the installer's words are read for ASCII and the rest is only
        # shown, so a byte that is not UTF-8 is a replacement character
        # and not a crash. Showing it is `main`'s to keep from crashing
        # too, this script's own stdout being no UTF-8 stream on Windows
        encoding="utf-8",
        errors="replace",
    ) as process:
        for line in process.stdout or ():
            emit(line)
            lines.append(line)
    return process.returncode, "".join(lines)


def show(line: str) -> None:
    """Print one line of the installer's output now, not at exit."""
    print(line, end="", flush=True)


def install(
    installer: list[str],
    requirement: str,
    version: str,
    timeout: float,
    interval: float,
) -> int:
    """Install the pinned requirement, and say what the deadline decided."""
    pinned = f"{requirement}=={version}"
    started = time.monotonic()
    deadline = started + timeout
    while True:
        status, output = run_installer([*installer, pinned], show)
        if status == 0:
            return 0
        if not unresolvable(output, requirement, version):
            return status
        left = deadline - time.monotonic()
        if left <= 0:
            print(
                f"::error::{pinned} did not resolve within {timeout:.0f} s: "
                "either the index has not served it to this runner yet, or it "
                "serves it with no file this cell can install, and the "
                "installer prints the same message for both"
            )
            return 1
        pause = min(interval, left)
        print(
            f"{pinned} is not resolvable yet, trying again in {pause:.0f} s",
            flush=True,
        )
        time.sleep(pause)


def main(argv: list[str] | None = None) -> int:
    """Read the requirement, the tag and the installer, and install."""
    # a stream in the locale's encoding (cp1252 on a Windows cell) cannot
    # write every character the installer's output can carry, and a failed
    # write would turn a successful install into a failed step
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(errors="replace")
    arguments = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(
        description=__doc__, usage="%(prog)s [options] requirement tag -- installer..."
    )
    parser.add_argument(
        "requirement", help="the package, with its extras if it has any: `pkg[extra]`"
    )
    parser.add_argument("tag", help="the release tag, empty on every other run")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)
    if "--" not in arguments:
        parser.error("the installer command follows `--`")
    split = arguments.index("--")
    args = parser.parse_args(arguments[:split])
    installer = arguments[split + 1 :]
    if not installer:
        parser.error("the installer command after `--` is empty")

    version = args.tag.removeprefix("v")
    if not version:
        return run_installer([*installer, args.requirement], show)[0]
    return install(installer, args.requirement, version, args.timeout, args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
