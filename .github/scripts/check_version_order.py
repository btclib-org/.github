# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Refuse a release version that sorts at or below a release already tagged.

An installer resolving the newest version picks the one that sorts
highest, so a release sorting below the latest one already published is
never installed by anybody who does not ask for it by name, and an upload
cannot be taken back. A calendar version dated before the latest release
has that shape, and so does a day released again under a lower patch
component, `2026.9.24` after `2026.9.24.1` (btclib-org/.github#1318).

The comparison is with the repository's own `v*` tags, the job
releasing a version only under the tag `v` followed by it. The tag being
released is left out, being the version itself. A tag that is not
`v` followed by digits and dots is not compared: the job refuses to
release such a version, and PEP 440 reads a digits-and-dots version as a
sequence of integers, trailing zeros insignificant, which is the whole
of the ordering this script applies.

    uv run --no-project --python 3.14 \
        .github/scripts/check_version_order.py "$version"

run from the root of the checkout whose tags it reads.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

_FINAL = re.compile(r"\d+(?:\.\d+)*")


def _key(version: str) -> tuple[int, ...]:
    """Return the version as PEP 440 orders it, trailing zeros dropped."""
    parts = [int(part) for part in version.split(".")]
    while parts and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


def check(version: str, tags: Iterable[str]) -> str | None:
    """Return why the version is refused against these tags, or None."""
    if _FINAL.fullmatch(version) is None:
        return f"{version} is not a final version of digits and dots"
    released = [
        tag[1:]
        for tag in tags
        if tag.startswith("v") and tag != f"v{version}" and _FINAL.fullmatch(tag[1:])
    ]
    if not released:
        return None
    latest = max(released, key=_key)
    if _key(version) <= _key(latest):
        return (
            f"{version} does not sort above v{latest}, the latest release"
            " tagged, so an installer resolving the newest version never picks it"
        )
    return None


def tagged() -> list[str]:
    """Return the `v*` tags of the repository in the working directory."""
    listed = subprocess.run(
        ["git", "tag", "--list", "v*"],  # noqa: S607
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    return listed.stdout.split()


def main(argv: list[str] | None = None, tags: Iterable[str] | None = None) -> int:
    """Read the version from the command line and compare it with the tags."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="the declared version, without the v")
    args = parser.parse_args(argv)

    refused = check(args.version, tagged() if tags is None else tags)
    if refused:
        print(f"::error::{refused}")
        return 1
    print(f"{args.version} sorts above every release tagged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
