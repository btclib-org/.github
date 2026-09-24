# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Refuse a calendar release version dated after the day it is published.

A calendar version `YYYY.M.D`, optionally `YYYY.M.D.N` for a patch, names
the day it was cut, and it sorts by that day: a version dated a month
ahead sorts above every real release cut before that date, so an
installer picks it over newer code, and an upload cannot be taken back.
Between releases a tree declares a month-only placeholder, `YYYY.M`, and
a day filled into a placeholder naming the next month is how such a
version gets written (btclib-org/.github#1310).

What the day is compared with is the run's own clock, and not the tagged
commit's date: the release pull request fixes the version before it
lands, and the tag can follow a day later, so the commit is not the
moment the version is published and the run is. Only a day after that
moment is refused. A version dated earlier passes, since a tag pushed
the day after its release pull request landed, or a failed release run
re-run later, is dated in the past and is no defect.

The comparison is with the date at UTC+14 rather than in UTC, which is a
day of slack in the one direction that needs it: whoever cuts a release
names it after the date on their own calendar, and that date is up to a
day ahead of UTC's east of Greenwich -- a release cut shortly after
local midnight in Rome is still the previous day in UTC. UTC+14,
`Pacific/Kiritimati`, is the furthest ahead any time zone runs, so the
date there is the latest date anybody can be looking at; a day after it
has begun nowhere.

    uv run --no-project --python 3.14 \
        .github/scripts/check_calendar_version.py "$version"
"""

from __future__ import annotations

import argparse
import re
from datetime import UTC, date, datetime, timedelta

# the furthest ahead of UTC any time zone runs: `Pacific/Kiritimati`
LATEST_OFFSET = timedelta(hours=14)

_CALENDAR = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:\.\d+)?")


def check(version: str, now: datetime) -> str | None:
    """Return why the version is refused at this instant, or None."""
    match = _CALENDAR.fullmatch(version)
    if match is None:
        return f"{version} is not YYYY.M.D, optionally YYYY.M.D.N for a patch"
    year, month, day = (int(part) for part in match.groups())
    try:
        dated = date(year, month, day)
    except ValueError:
        return f"{version} names no calendar date"
    latest = (now.astimezone(UTC) + LATEST_OFFSET).date()
    if dated > latest:
        return (
            f"{version} is dated {dated.isoformat()}, a day that has not"
            f" begun in any time zone at {now.astimezone(UTC):%Y-%m-%d %H:%M} UTC"
        )
    return None


def main(argv: list[str] | None = None, now: datetime | None = None) -> int:
    """Read the version from the command line and check its date."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="the declared version, without the v")
    args = parser.parse_args(argv)

    refused = check(args.version, now or datetime.now(UTC))
    if refused:
        print(f"::error::{refused}")
        return 1
    print(f"{args.version} is not dated in the future")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
