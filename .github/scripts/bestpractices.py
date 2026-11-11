# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Read the trees' bestpractices.dev answers, and say where the site lags.

A tree is registered where its README carries a bestpractices.dev badge,
which is where the project id is read from. Its answers of record are its
`.bestpractices.json`, at the top level of its default branch: flat keys
`<criterion>_status` and `<criterion>_justification`, keys sorted, two
spaces of indent, a newline at the end. A key is named as the site
reads it from that file, which matches names exactly: as the site's entry
gives it, except an OSPS id, which the entry gives as `OSPS-AC-01.01` and
the file as `osps_ac_01_01`.

    uv run --no-project --python 3.15 .github/scripts/bestpractices.py --drift

`--seed <dir>` writes `<dir>/<tree>/.bestpractices.json` from the answers
the site gives, for a tree's first file to copy. It leaves out a null
justification, a status of `?` and a status that is not a string, such
as an integer: the site skips a `?` it reads in the file, and drops a
status that is not a string. It writes nothing in this repository.

`--drift` fetches each tree's answers from the site and lists each
criterion the file holds whose status or justification there differs.
Then it prints URLs of the site's edit form, each for one section of
the form, because the form ignores a field of another section. Each URL
carries the file's values for its criteria and forces them over the
answers given, for whoever may edit the project to review and save. A
section's criteria go over several URLs where one would be longer than
the site accepts. A criterion too long for a URL of its own is named on
a line of its own, to type into the form by hand. The section of a
criterion is the first level that lists it in the criteria files of
ossf/best-practices-badge at `CRITERIA_REF`. A criterion no level lists
there gets no URL, and is named on a line of its own. A tree whose file
and site agree prints nothing.

`--stale` fetches nothing from bestpractices.dev. It reads the files and
lists each answer whose justification names a `v`-prefixed version older
than the tree's latest GitHub release, an ISO date before that release,
or the words "draft" or "next release", which carry no date and are
always listed. It misses a version written without its `v`, a date in
another format, and an answer gone stale without naming anything, such as
an asset name or an advisory state. It also lists a version or a date an
answer cites on purpose, as history.

`--differ` reads the files too, and lists each criterion whose status is
not the same in every tree that has a file, for a review to check each
difference has a reason. A tree with no answer shows `-`.

`--drift`, `--stale` and `--differ` list a tree with no file as
`<tree>: no .bestpractices.json`. `--files <dir>` makes them read
`<dir>/<tree>/.bestpractices.json`, the layout `--seed` writes, in place
of the trees' default branches.
"""

from __future__ import annotations

import argparse
import functools
import json
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

if TYPE_CHECKING:
    from collections.abc import Sequence

ORG = "btclib-org"
FILE = ".bestpractices.json"
SITE = "https://www.bestpractices.dev"
PROJECT = SITE + "/projects/{id}.json"
EDIT = SITE + "/projects/{id}/{section}/edit?{query}"
# the longest path and query the site answers: one byte more gets a 414
TARGET = 8192
# the site redirects a path without a locale to one with it, so a URL
# leaves room for the longest locale its pages link, as `zh-CN`
LOCALE = len("/zh-CN")
UPSTREAM = "ossf/best-practices-badge"
# the commit of UPSTREAM whose criteria files say where a criterion is,
# moved by hand: a criterion added upstream after it is named by --drift
# as in no section until the pin moves
CRITERIA_REF = "9a7839f4e85a9c51cde24efa5cf386f97c2f2921"
METAL = "criteria/criteria.yml"
METAL_LEVEL = re.compile(r"^- '(\d+)':")
METAL_CRITERION = re.compile(r"^      - ([A-Za-z0-9_]+):[ ]*(?:#.*)?$")
# the form's section for each level, as upstream's REDIRECTS names it
METAL_SECTION = {"0": "passing", "1": "silver", "2": "gold"}
BASELINE = "criteria/baseline_criteria.yml"
BASELINE_LEVEL = re.compile(r"^([^\s:]+):")
BASELINE_CRITERION = re.compile(r"^      ([a-z0-9_]+):[ ]*(?:#.*)?$")
OSPS = "OSPS-"
UNKNOWN = "?"
BADGE = re.compile(r"bestpractices\.dev/projects/(\d+)")
STATUS = "_status"
JUSTIFICATION = "_justification"
VERSION = re.compile(r"\bv(\d+(?:\.\d+)+)\b")
DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
UNDATED = re.compile(r"\b(?:draft|next release)\b", re.IGNORECASE)

Answers = dict[str, Any]


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


def tree_file(tree: str) -> str | None:
    """Return the tree's file on its default branch, `None` without one."""
    run = subprocess.run(  # noqa: S603
        [  # noqa: S607
            "gh",
            "api",
            "-H",
            "Accept: application/vnd.github.raw",
            f"repos/{ORG}/{tree}/contents/{FILE}",
        ],
        check=False,
        capture_output=True,
        encoding="utf-8",
    )
    if run.returncode == 0:
        return run.stdout
    if "(HTTP 404)" in run.stderr:
        return None
    raise subprocess.CalledProcessError(
        run.returncode, run.args, run.stdout, run.stderr
    )


def read(tree: str, files: Path | None) -> Answers | None:
    """Return the tree's answers of record, `None` where it has no file."""
    if files is None:
        text = tree_file(tree)
    else:
        path = files / tree / FILE
        text = path.read_text(encoding="utf-8") if path.is_file() else None
    if text is None:
        return None
    try:
        given = json.loads(text)
    except json.JSONDecodeError as error:
        msg = f"{tree}: {FILE} is not JSON: {error}"
        raise ValueError(msg) from error
    if not isinstance(given, dict):
        msg = f"{tree}: {FILE} holds no JSON object"
        raise TypeError(msg)
    return given


def field(key: str) -> str:
    """Return a key of the site's entry as the file and the form name it."""
    if not key.startswith(OSPS):
        return key
    return key.lower().replace("-", "_").replace(".", "_")


def answers(project: dict[str, Any]) -> Answers:
    """Return each criterion's status and justification as the file has them."""
    out: Answers = {}
    for key, status in project.items():
        if key.endswith(STATUS):
            criterion = key.removesuffix(STATUS)
            if isinstance(status, str) and status != UNKNOWN:
                out[field(key)] = status
            justification = project.get(criterion + JUSTIFICATION)
            if justification is not None:
                out[field(criterion) + JUSTIFICATION] = justification
    return out


def _baseline(key: str) -> str | None:
    """Return the section a top-level key of the baseline file names."""
    return key if key.startswith("baseline-") else None


def where(metal: str, baseline: str) -> dict[str, str]:
    """Return the first section of the form that holds each criterion.

    The criteria files are read a line at a time, at the indent each
    gives a criterion, since this script runs on the standard library.
    """
    out: dict[str, str] = {}
    for text, level, criterion, section_of in (
        (metal, METAL_LEVEL, METAL_CRITERION, METAL_SECTION.get),
        (baseline, BASELINE_LEVEL, BASELINE_CRITERION, _baseline),
    ):
        section = None
        for line in text.splitlines():
            if found := level.match(line):
                section = section_of(found[1])
            elif section and (found := criterion.match(line)):
                out.setdefault(found[1], section)
    return out


@functools.cache
def form() -> dict[str, str]:
    """Return `where` for the criteria files at `CRITERIA_REF`."""
    metal, baseline = (
        gh(
            "-H",
            "Accept: application/vnd.github.raw",
            f"repos/{UPSTREAM}/contents/{path}?ref={CRITERIA_REF}",
        )
        for path in (METAL, BASELINE)
    )
    return where(metal, baseline)


def render(given: Answers) -> str:
    """Return the answers as the file holds them."""
    return json.dumps(given, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def criteria(given: Answers) -> list[str]:
    """Return the criteria the answers name, sorted."""
    return sorted(
        {
            key.removesuffix(suffix)
            for key in given
            for suffix in (STATUS, JUSTIFICATION)
            if key.endswith(suffix)
        }
    )


def _version(text: str) -> tuple[int, ...]:
    """Return a version as numbers: `v2026.10.1` follows `v2026.9.30`."""
    return tuple(int(part) for part in text.removeprefix("v").split("."))


def stale(given: Answers, tag: str, published: str) -> list[str]:
    """Return each answer naming something older than the release, with what."""
    latest = _version(tag)
    day = published[:10]
    out = []
    for criterion in criteria(given):
        text = given.get(criterion + JUSTIFICATION) or ""
        versions = [
            f"v{each}" for each in VERSION.findall(text) if _version(each) < latest
        ]
        dates = [each for each in DATE.findall(text) if each < day]
        words = [each.lower() for each in UNDATED.findall(text)]
        if named := dict.fromkeys([*versions, *dates, *words]):
            out.append(f"{criterion}: {', '.join(named)}")
    return out


def differ(given: dict[str, Answers]) -> list[str]:
    """Return each criterion whose status differs by tree, with every status."""
    every = sorted({each for held in given.values() for each in criteria(held)})
    out = []
    for criterion in every:
        statuses = {
            tree: str(held.get(criterion + STATUS, "-"))
            for tree, held in sorted(given.items())
        }
        if len(set(statuses.values())) > 1:
            trees = ", ".join(f"{tree} {status}" for tree, status in statuses.items())
            out.append(f"{criterion}: {trees}")
    return out


def drift(given: Answers, live: Answers) -> dict[str, list[str]]:
    """Return each criterion of the file the site answers otherwise."""
    out = {}
    for criterion in criteria(given):
        if fields := [
            suffix.removeprefix("_")
            for suffix in (STATUS, JUSTIFICATION)
            if given.get(criterion + suffix) != live.get(criterion + suffix)
        ]:
            out[criterion] = fields
    return out


def proposal(
    number: int, section: str, given: Answers, differing: Sequence[str]
) -> str:
    """Return the edit form's URL carrying the file's values, forced.

    A status the file does not hold is not sent, the form rejecting a
    blank one. A justification it does not hold is sent blank.
    """
    pairs = []
    for criterion in differing:
        if (status := given.get(criterion + STATUS)) is not None:
            pairs.append((criterion + STATUS, str(status)))
        pairs.append(
            (criterion + JUSTIFICATION, given.get(criterion + JUSTIFICATION) or "")
        )
    pairs.append(("overrides", ",".join(key for key, _ in pairs)))
    return EDIT.format(id=number, section=section, query=urlencode(pairs))


def fits(url: str) -> bool:
    """Say whether the site accepts the URL once its redirect adds a locale.

    `urlencode` writes ASCII, so a character of the URL is a byte.
    """
    return len(url.removeprefix(SITE)) + LOCALE <= TARGET


def proposals(
    number: int, section: str, given: Answers, differing: Sequence[str]
) -> tuple[list[str], list[str]]:
    """Return the `proposal` URLs for the criteria, and those too long for one.

    The criteria fill each URL in order, a new one starting where the next
    criterion would make it longer than the site accepts.
    """
    urls: list[str] = []
    alone: list[str] = []
    held: list[str] = []
    for criterion in differing:
        if not fits(proposal(number, section, given, [criterion])):
            alone.append(criterion)
            continue
        if held and not fits(proposal(number, section, given, [*held, criterion])):
            urls.append(proposal(number, section, given, held))
            held = []
        held.append(criterion)
    if held:
        urls.append(proposal(number, section, given, held))
    return urls, alone


def seed(root: Path, trees: dict[str, int]) -> None:
    """Write each tree's file under `root` from the site's answers."""
    for tree, number in trees.items():
        path = root / tree / FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(answers(fetch(number))), encoding="utf-8")


def drifted(found: dict[str, Answers], trees: dict[str, int]) -> list[str]:
    """Return what `--drift` prints for the trees that have a file."""
    out = []
    for tree, given in found.items():
        differing = drift(given, answers(fetch(trees[tree])))
        out += [
            f"{tree}: {criterion}: {', '.join(fields)}"
            for criterion, fields in differing.items()
        ]
        if not differing:
            continue
        sections: dict[str | None, list[str]] = {}
        for criterion in differing:
            sections.setdefault(form().get(criterion), []).append(criterion)
        for section, held in sections.items():
            if section is None:
                out.append(f"{tree}: in no section of the form: {', '.join(held)}")
                continue
            urls, alone = proposals(trees[tree], section, given, held)
            out += [f"{tree}: {url}" for url in urls]
            if alone:
                out.append(
                    f"{tree}: too long for a URL, to type into the {section}"
                    f" form by hand: {', '.join(alone)}"
                )
    return out


def staled(found: dict[str, Answers]) -> list[str]:
    """Return what `--stale` prints for the trees that have a file."""
    out = []
    for tree, given in found.items():
        release = json.loads(gh(f"repos/{ORG}/{tree}/releases/latest"))
        tag = release["tag_name"]
        out += [
            f"{tree} {tag}: {line}"
            for line in stale(given, tag, release["published_at"])
        ]
    return out


def main(argv: Sequence[str] | None = None) -> int:
    """Seed the files, or list drift, stale answers or differing ones."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--seed",
        type=Path,
        metavar="DIR",
        help="write DIR/<tree>/.bestpractices.json from the site's answers",
    )
    mode.add_argument(
        "--drift",
        action="store_true",
        help="list what the site answers otherwise than the files, with a URL",
    )
    mode.add_argument(
        "--stale", action="store_true", help="list stale answers, write nothing"
    )
    mode.add_argument(
        "--differ",
        action="store_true",
        help="list criteria whose status differs by tree, write nothing",
    )
    parser.add_argument(
        "--files",
        type=Path,
        metavar="DIR",
        help="read DIR/<tree>/.bestpractices.json, not the trees' default branches",
    )
    args = parser.parse_args(argv)
    if args.seed is not None and args.files is not None:
        parser.error("--files reads the files, and --seed writes them")
    trees = registered()

    if args.seed is not None:
        seed(args.seed, trees)
        return 0

    found = {}
    for tree in trees:
        given = read(tree, args.files)
        if given is None:
            print(f"{tree}: no {FILE}")
        else:
            found[tree] = given

    if args.drift:
        lines = drifted(found, trees)
    elif args.stale:
        lines = staled(found)
    else:
        lines = differ(found)
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
