# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Save the bestpractices.dev answers, or list stale or differing ones.

A tree is registered where its README carries a bestpractices.dev badge,
which is where the project id is read from. For each one this writes
`bestpractices/<tree>.json`: every criterion's status and justification,
keys sorted, so that a review shows as a diff and a run with nothing
changed leaves none. The file of a tree no longer registered is removed.

    uv run --no-project --python 3.15 .github/scripts/bestpractices.py

`--stale` fetches nothing from bestpractices.dev. It reads the saved files
and lists each answer whose justification names a `v`-prefixed version
older than the tree's latest GitHub release, an ISO date before that
release, or the words "draft" or "next release", which carry no date and
are always listed. It misses a version written without its `v`, a date in
another format, and an answer gone stale without naming anything, such as
an asset name or an advisory state. It also lists a version or a date an
answer cites on purpose, as history.

`--differ` reads the saved files too, and lists each criterion whose status
is not the same in every tree, for a review to check each difference has a
reason. A tree with no answer shows `-`.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.request import Request, urlopen

if TYPE_CHECKING:
    from collections.abc import Sequence

ORG = "btclib-org"
SAVED = Path(__file__).parents[2] / "bestpractices"
PROJECT = "https://www.bestpractices.dev/projects/{id}.json"
BADGE = re.compile(r"bestpractices\.dev/projects/(\d+)")
STATUS = "_status"
JUSTIFICATION = "_justification"
VERSION = re.compile(r"\bv(\d+(?:\.\d+)+)\b")
DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
UNDATED = re.compile(r"\b(?:draft|next release)\b", re.IGNORECASE)

Answers = dict[str, dict[str, Any]]


def gh(*args: str) -> str:
    """Return what `gh api` prints for the arguments."""
    return subprocess.run(  # noqa: S603
        ["gh", "api", *args],  # noqa: S607
        check=True,
        capture_output=True,
        encoding="utf-8",
    ).stdout


def fetch(number: int) -> dict[str, Any]:
    """Return the project's whole entry at bestpractices.dev."""
    request = Request(PROJECT.format(id=number))  # noqa: S310
    with urlopen(request, timeout=30) as answer:  # noqa: S310
        project: dict[str, Any] = json.load(answer)
    return project


def project_id(readme: str) -> int | None:
    """Return the project id the README's badge names, `None` without one."""
    found = set(BADGE.findall(readme))
    if len(found) > 1:
        msg = f"the README names several bestpractices.dev projects: {found}"
        raise ValueError(msg)
    return int(found.pop()) if found else None


def registered() -> dict[str, int]:
    """Return each public tree of the organization with its project id."""
    names = gh(
        "--paginate",
        f"orgs/{ORG}/repos?type=public&per_page=100",
        "--jq",
        ".[] | select((.archived or .fork) | not) | .name",
    ).split()
    out = {}
    for name in sorted(names):
        readme = gh(
            "-H", "Accept: application/vnd.github.raw", f"repos/{ORG}/{name}/readme"
        )
        number = project_id(readme)
        if number is not None:
            out[name] = number
    return out


def answers(project: dict[str, Any]) -> Answers:
    """Return each criterion's status and justification, nothing else."""
    return {
        key.removesuffix(STATUS): {
            "status": status,
            "justification": project.get(key.removesuffix(STATUS) + JUSTIFICATION),
        }
        for key, status in project.items()
        if key.endswith(STATUS)
    }


def render(saved: Answers) -> str:
    """Return the answers as the file holds them."""
    return json.dumps(saved, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _version(text: str) -> tuple[int, ...]:
    """Return a version as numbers: `v2026.10.1` follows `v2026.9.30`."""
    return tuple(int(part) for part in text.removeprefix("v").split("."))


def stale(saved: Answers, tag: str, published: str) -> list[str]:
    """Return each answer naming something older than the release, with what."""
    latest = _version(tag)
    day = published[:10]
    out = []
    for criterion, answer in sorted(saved.items()):
        text = answer["justification"] or ""
        versions = [
            f"v{each}" for each in VERSION.findall(text) if _version(each) < latest
        ]
        dates = [each for each in DATE.findall(text) if each < day]
        words = [each.lower() for each in UNDATED.findall(text)]
        named = dict.fromkeys([*versions, *dates, *words])
        if named:
            out.append(f"{criterion}: {', '.join(named)}")
    return out


def differ(saved: dict[str, Answers]) -> list[str]:
    """Return each criterion whose status differs by tree, with every status."""
    criteria = sorted({criterion for each in saved.values() for criterion in each})
    out = []
    for criterion in criteria:
        statuses = {
            tree: str(given.get(criterion, {}).get("status", "-"))
            for tree, given in sorted(saved.items())
        }
        if len(set(statuses.values())) > 1:
            trees = ", ".join(f"{tree} {status}" for tree, status in statuses.items())
            out.append(f"{criterion}: {trees}")
    return out


def main(argv: Sequence[str] | None = None) -> int:
    """Save the answers, or list the stale ones or the differing ones."""
    parser = argparse.ArgumentParser(description=__doc__)
    listing = parser.add_mutually_exclusive_group()
    listing.add_argument(
        "--stale", action="store_true", help="list stale answers, write nothing"
    )
    listing.add_argument(
        "--differ",
        action="store_true",
        help="list criteria whose status differs by tree, write nothing",
    )
    parser.add_argument(
        "--saved", type=Path, default=SAVED, help="the directory of the saved answers"
    )
    args = parser.parse_args(argv)

    if args.stale:
        for path in sorted(args.saved.glob("*.json")):
            release = json.loads(gh(f"repos/{ORG}/{path.stem}/releases/latest"))
            saved = json.loads(path.read_text(encoding="utf-8"))
            for line in stale(saved, release["tag_name"], release["published_at"]):
                print(f"{path.stem} {release['tag_name']}: {line}")
        return 0

    if args.differ:
        saved = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in args.saved.glob("*.json")
        }
        for line in differ(saved):
            print(line)
        return 0

    args.saved.mkdir(exist_ok=True)
    trees = registered()
    for path in args.saved.glob("*.json"):
        if path.stem not in trees:
            path.unlink()
    for tree, number in trees.items():
        path = args.saved / f"{tree}.json"
        path.write_text(render(answers(fetch(number))), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
