# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Fail the regtest job on a skip its own caller has not declared exempt.

`pytest` exits 0 for a module that skipped itself, so a job whose fixture
stopped finding the node would stay green while asking Core nothing --
the failure mode of an unattended run that looks like good news. This
reads the run's own JUnit report and fails it unless every testcase
either ran or was exempted by name.

Two exemptions, read from the report the same way and answered
differently:

`--exclude-classname` removes a matching testcase from judgment
altogether -- it is not counted among the cases considered, whether it
ran, failed or skipped. It exempts one family by module name; a second
family has no classname of its own to be given (btclib-org/.github#1377).

`--skip-reason-prefix` exempts a single *skip*, and only where its own
JUnit message starts with the caller's declared prefix -- a testcase
that runs, or that fails, is unaffected by it either way, and a skip
whose reason does not carry the prefix still fails the job. A caller
with several legitimately-skipping families gives them one shared reason
prefix rather than naming each family's module.

A `pytest` collection-level skip -- a whole module skipped before any of
its tests run -- carries the fixed message `"collection skipped"`, which
no caller-chosen prefix can be written to match; such a skip always
fails the job.

    uv run --no-project --python 3.15 \
        .github/scripts/check_node_ran.py integration.xml \
        --exclude-classname "$EXCLUDE_CLASSNAME" \
        --skip-reason-prefix "$SKIP_REASON_PREFIX"
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def considered(report: ET.Element, exclude_classname: str) -> list[ET.Element]:
    """Return the testcases exclude-classname does not remove from judgment."""
    return [
        case
        for case in report.iter("testcase")
        if not exclude_classname or exclude_classname not in case.get("classname", "")
    ]


def skip_reason(case: ET.Element) -> str | None:
    """Return the case's own skip message, or None where it was not skipped."""
    skipped = case.find("skipped")
    return None if skipped is None else skipped.get("message", "")


def is_exempt_skip(case: ET.Element, skip_reason_prefix: str) -> bool:
    """Return whether a skipped case's reason carries the declared prefix."""
    reason = skip_reason(case)
    if reason is None or not skip_reason_prefix:
        return False
    return reason.startswith(skip_reason_prefix)


def check(report_path: Path, exclude_classname: str, skip_reason_prefix: str) -> int:
    """Print every skip, failing on one the caller has not declared exempt."""
    # the run's own JUnit output, this job's previous step having just
    # written it -- not data an adversary could have shaped
    report = ET.parse(report_path).getroot()  # noqa: S314
    ran = considered(report, exclude_classname)
    skipped = [case for case in ran if skip_reason(case) is not None]
    failing = [case for case in skipped if not is_exempt_skip(case, skip_reason_prefix)]

    for case in skipped:
        name, reason = case.get("name"), skip_reason(case)
        if case in failing:
            print(f"::error::{name} skipped: {reason}")
        else:
            print(f"{name} skipped and exempt: {reason}")

    if not ran or failing:
        print(
            f"::error::{len(ran)} test(s) ran, "
            f"{len(failing)} of {len(skipped)} skip(s) unexempted"
        )
        return 1
    print(f"{len(ran)} test(s) ran against the node")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Read the report and the two exemptions from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="the run's own JUnit xml")
    parser.add_argument("--exclude-classname", default="")
    parser.add_argument("--skip-reason-prefix", default="")
    args = parser.parse_args(argv)
    return check(args.report, args.exclude_classname, args.skip_reason_prefix)


if __name__ == "__main__":
    raise SystemExit(main())
