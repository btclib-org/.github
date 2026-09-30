# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Wait until the index serves the version a release just published.

Every cell of `pypi-install.yml` installs whatever the resolver picks,
and the index does not serve a new file the instant the upload returns: a
run that starts too early installs the version the release replaces and
reports a pass for it, which is worse than reporting nothing. So a run
with a release behind it waits for the version its tag names, and fails
rather than let the matrix measure the wrong thing.

What is asked is the simple index's page for the package, in the JSON
form of PEP 691, and the version is served once a file of that version is
listed on it. That page is what `pip` reads to choose a file, so the wait
ends on the document the install then depends on rather than on a
neighbouring one. It ends on what this runner is served: another runner
can still be served an older page by the edge it reaches.

The budget is a deadline and not a count of attempts. A wait stated as
attempts times an interval is a product to be multiplied out before it
can be compared with the job's own `timeout-minutes`, and a wait that
outlasts that is killed inside itself: the run then carries the runner's
message about a cancelled job where this was written to name the page to
go and read (btclib-org/btclib#1165). `DEFAULT_TIMEOUT` below states the
deadline once and the job header states its own timeout, so what decides
whether the wait fits inside the job is one number against one number.
Every request is bounded by what is left of the deadline as well as by
its own timeout, so the whole wait ends within `--timeout` of its first
request whatever the index does between answers. What is not bounded
here is a single answer arriving a byte at a time: `urlopen`'s timeout
is a socket timeout and applies per blocking read, so that case is the
job's `timeout-minutes` to end.

No trigger reaches the verdict this exists for. What is waited on is
somebody else's upload, so neither a release nor a rehearsal can arrange
for the index to be late, and a trigger added to reach the retry reaches
its first attempt instead. `tests/wait_for_pypi_release_test.py` is
therefore the only thing that drives the retry, the deadline and the
error path: it substitutes the transport and the clock, and advances the
clock past the deadline itself.

The tag is empty on every trigger but a release call, and an empty tag is
nothing to wait for rather than an error -- which is what makes this
runnable on a schedule and a dispatch, where a step only a release runs
is a step whose defect ships with a release.

    uv run --no-project --python 3.15 \
        .github/scripts/wait_for_pypi_release.py "$PACKAGE" "$TAG"
"""

from __future__ import annotations

import argparse
import json
import re
import time
from http import HTTPStatus
from http.client import HTTPException
from urllib.request import Request, urlopen

# the simple index, which answers one page per project and 404 for a
# project it has never had. The page lists files, so a version not yet
# served is a 200 without a file of it
INDEX = "https://pypi.org/simple"
# what pip sends (`pip/_internal/index/collector.py`, 26.2.1): the JSON form
# of PEP 691 first, the HTML forms as fallbacks. The index varies its answer
# on this header, so the string is pip's whole and not its first type. The
# answer is read as JSON, which is what the first type gets
ACCEPT = (
    "application/vnd.pypi.simple.v1+json, "
    "application/vnd.pypi.simple.v1+html; q=0.1, "
    "text/html; q=0.01"
)

# what a release has to arrive within, in seconds, and the one number the
# job's `timeout-minutes` is compared against. Chosen rather than
# measured: nothing here times how long the index takes to serve an
# upload, and what this bounds is the case where it never serves it at all
DEFAULT_TIMEOUT = 300.0
# between two questions to the index: long enough not to hammer it, short
# enough that the wait ends near the upload rather than near the deadline
DEFAULT_INTERVAL = 15.0
# one question's own bound, so that a connection that hangs spends part of
# the deadline rather than all of it
DEFAULT_REQUEST_TIMEOUT = 10.0


def normalize(package: str) -> str:
    """Return the name the simple index keys a project under (PEP 503)."""
    return re.sub(r"[-_.]+", "-", package).lower()


def version_of(filename: str) -> str | None:
    """Return the version a distribution's filename carries, if it has one.

    A wheel is `{name}-{version}-{tags}.whl` and an sdist
    `{name}-{version}.tar.gz`, the name having no hyphen in either
    because the build escapes it.
    """
    if filename.endswith(".whl"):
        parts = filename.split("-")
        return parts[1] if len(parts) > 1 else None
    stem = filename.removesuffix(".tar.gz").removesuffix(".zip")
    if stem == filename:
        return None
    return stem.rpartition("-")[2] or None


def lists(document: dict[str, object], version: str) -> bool:
    """Return whether the page lists a file of this version."""
    files = document.get("files")
    if not isinstance(files, list):
        return False
    return any(
        isinstance(entry, dict) and version_of(str(entry.get("filename"))) == version
        for entry in files
    )


def served(url: str, version: str, timeout: float) -> bool:
    """Return whether the index's page lists a file of this version."""
    request = Request(url, headers={"Accept": ACCEPT}, method="GET")  # noqa: S310
    try:
        with urlopen(request, timeout=timeout) as answer:  # noqa: S310
            if answer.status != HTTPStatus.OK:
                return False
            document = json.load(answer)
    # every way the index can fail to answer is one more reason to wait:
    # a 404 for a project the index does not have yet is an HTTPError, a
    # connection refused or timed out is an OSError, a truncated answer is
    # an HTTPException and a body that is not JSON is a ValueError. None
    # of them is this script's verdict, which the deadline alone decides.
    #
    # Separate clauses and not one parenthesised tuple, this file being
    # shared: `ruff-format` rewrites `except (OSError, HTTPException):`
    # into PEP 758's unparenthesised form wherever `requires-python` is
    # 3.14, and that form is a syntax error to mypy and to the
    # interpreter wherever it is 3.10 -- so the tuple cannot hold still
    # in all four trees at once and separate clauses can
    # (btclib-org/.github#1160)
    except OSError:
        return False
    except HTTPException:
        return False
    except ValueError:
        return False
    return isinstance(document, dict) and lists(document, version)


def wait(
    package: str,
    version: str,
    timeout: float,
    interval: float,
    request_timeout: float,
) -> int:
    """Poll the index for one version, and say what the deadline decided."""
    url = f"{INDEX}/{normalize(package)}/"
    started = time.monotonic()
    deadline = started + timeout
    while (left := deadline - time.monotonic()) > 0:
        if served(url, version, min(request_timeout, left)):
            waited = time.monotonic() - started
            print(f"the index serves {version} after {waited:.0f} s")
            return 0
        print(f"{version} is not served yet")
        time.sleep(min(interval, max(deadline - time.monotonic(), 0.0)))
    print(f"::error::{version} is not on the index {timeout:.0f} s later")
    return 1


def main(argv: list[str] | None = None) -> int:
    """Read the tag from the command line and wait for what it names."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", help="the name the index serves it under")
    parser.add_argument("tag", help="the release tag, empty on every other run")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--interval", type=float, default=DEFAULT_INTERVAL)
    parser.add_argument(
        "--request-timeout", type=float, default=DEFAULT_REQUEST_TIMEOUT
    )
    args = parser.parse_args(argv)

    version = args.tag.removeprefix("v")
    if not version:
        print("no release behind this run: nothing to wait for")
        return 0
    return wait(
        args.package, version, args.timeout, args.interval, args.request_timeout
    )


if __name__ == "__main__":
    raise SystemExit(main())
