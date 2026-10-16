# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Audit the lock, for what a release publishes or for the whole lock.

`uv audit` checks `uv.lock` against OSV and exits 1 on an advisory, 2 when
the service cannot be reached, and 0 otherwise; this script passes that
status on, so a release whose audit could not run fails as one whose audit
found something does. It runs `uv audit --locked`, never `--frozen`:
section 1 of the standard is what says why.

Two questions are the tree's and are answered from its own files.

What is audited is what the wheel declares. `uv audit` reads every
dependency group unless told otherwise, and no flag selects the default
groups alone, so every key of `[dependency-groups]` is passed as
`--no-group`. What is left is `[project] dependencies` and the extras,
which is what `Requires-Dist` carries. The development tools a release
does not publish are audited by the lint job (`--all-groups`, below).

What is ignored is what `.github/vex.toml` names: each `[[not_affected]]`
table's `id` is passed as `--ignore`, so the gate's only exemptions are
the ones the tree states there and, for a shipped component, in a release's
own signed document. A tree owes no such file where it has no entry. `uv
audit` would read an ignore from `[tool.uv.audit]` in `pyproject.toml` and
from `[audit]` in `uv.toml`, and neither is read here, the run refusing a
tree that has one: an ignore kept there is not in the release's document.
`--ignore` matches an advisory's id and its aliases in every package of the
set, where an entry names one component, so an entry for a component can
exempt the same advisory in another. `--ignore-until-fixed` is not used, a
finding that does not affect a release having nothing to do with whether a
fix exists.

`--all-groups` passes no `--no-group`, so the whole lock is audited: that is
what the lint job of `reusable-lint.yml` runs, a malicious package being as
harmful in a development tool as in the wheel. The refusals are the same. So
are the ignores, with one addition: an entry with a `group`, naming a
dependency group the release does not ship and giving its reason in `detail`,
is passed as `--ignore` here and in no release audit. A group the tree does
not declare, a missing `detail`, and a `component` the wheel ships are
refused: `--ignore` is global, so such an entry would exempt the release's own
copy of the package. What the wheel ships is read from `pyproject.toml` and
from `uv.lock`, the root package's runtime closure, so a package a dependency
brings in counts.

    uv run --no-project --python 3.15 .github/scripts/check_audit.py

run from the root of the tree whose lock it audits.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

# the spelling `uv audit`'s own warning gives for lifting the warning
PREVIEW = ("--preview-features", "audit-command")

VEX = Path(".github") / "vex.toml"

# the name a requirement starts with, before any extras, version or marker
REQUIREMENT = re.compile(r"\s*([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)")


def _load(path: Path) -> dict[str, Any]:
    """Return the parsed TOML file, empty where there is none."""
    if not path.is_file():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)


def refusals(root: Path) -> list[str]:
    """Return why the tree's configuration is refused, empty if it is not."""
    refused = []
    tool = _load(root / "pyproject.toml").get("tool", {})
    if "audit" in tool.get("uv", {}):
        refused.append(
            "pyproject.toml has [tool.uv.audit], an ignore list beside the VEX one"
        )
    if "audit" in _load(root / "uv.toml"):
        refused.append("uv.toml has [audit], an ignore list beside the VEX one")
    return refused


def groups(root: Path) -> list[str]:
    """Return the dependency groups the tree declares."""
    declared = _load(root / "pyproject.toml").get("dependency-groups", {})
    return list(declared)


def _normalized(name: str) -> str:
    """Return the PEP 503 form of a distribution name."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _edges(package: dict[str, Any], extra: str | None, *, is_root: bool) -> list[Any]:
    """Return the dependencies a package, or one of its extras, brings in."""
    if extra is not None:
        return list(package.get("optional-dependencies", {}).get(extra, []))
    edges = list(package.get("dependencies", []))
    if is_root:
        for each in package.get("optional-dependencies", {}).values():
            edges.extend(each)
    return edges


def _closure(lock: dict[str, Any]) -> set[str]:
    """Return the names reachable from the lock's root package.

    :param lock: the parsed `uv.lock`.
    """
    packages = {_normalized(each["name"]): each for each in lock.get("package", [])}
    roots = {
        name
        for name, package in packages.items()
        if "." in package.get("source", {}).values()
    }
    pending: list[tuple[str, str | None]] = [(name, None) for name in roots]
    seen: set[tuple[str, str | None]] = set()
    reached: set[str] = set()
    while pending:
        item = pending.pop()
        name, extra = item
        if item in seen or name not in packages:
            continue
        seen.add(item)
        for edge in _edges(packages[name], extra, is_root=name in roots):
            target = _normalized(edge["name"])
            reached.add(target)
            pending.append((target, None))
            pending.extend((target, requested) for requested in edge.get("extra", []))
    return reached


def shipped(root: Path) -> set[str]:
    """Return the PEP 503 names of everything the wheel requires.

    The names `[project]` gives, extras included, and the runtime closure of
    `uv.lock`: the root package's dependencies and optional dependencies,
    then those of every package reached, and of the extras each asks for. The
    lock covers a requirement `pyproject.toml` leaves to the backend, and a
    package a dependency brings in. The root's dependency groups are not
    followed.

    :param root: the tree whose files are read.
    :returns: the names, a set that is empty for a tree with neither file.
    """
    project = _load(root / "pyproject.toml").get("project", {})
    requirements = list(project.get("dependencies", []))
    for extra in project.get("optional-dependencies", {}).values():
        requirements.extend(extra)
    matches = (REQUIREMENT.match(requirement) for requirement in requirements)
    names = {_normalized(match[1]) for match in matches if match}

    return names | _closure(_load(root / "uv.lock"))


def _check_group(root: Path, table: dict[str, Any]) -> None:
    """Refuse a group entry that is unfit to ignore, and say why.

    :param root: the tree whose files say which groups it declares and requires.
    :param table: the `[[not_affected]]` table naming a group.
    :raises ValueError: where the entry is refused.
    """
    group = table["group"]
    detail = table.get("detail")
    if not isinstance(detail, str) or not detail:
        msg = f"{VEX}: {table['id']} names the group {group!r} and gives no `detail`"
        raise ValueError(msg)
    if group not in groups(root):
        msg = f"{VEX}: {table['id']} names the group {group!r}, which the tree lacks"
        raise ValueError(msg)
    component = table.get("component")
    if not isinstance(component, str) or not component:
        msg = f"{VEX}: {table['id']} names the group {group!r} and no `component`"
        raise ValueError(msg)
    if _normalized(component) in shipped(root):
        msg = (
            f"{VEX}: {table['id']} names {component!r}, which the wheel ships: "
            "`--ignore` is global, so the entry would exempt the release's copy"
        )
        raise ValueError(msg)


def ignored(root: Path, *, all_groups: bool = False) -> list[str]:
    """Return the ids `.github/vex.toml` judges not to affect the audited set.

    An entry with a `group` is about a development group the release does
    not ship, so only the audit of the whole lock ignores it.

    :param root: the tree whose list is read.
    :param all_groups: whether the development groups are audited too.
    :raises ValueError: where an id or a group entry is not valid.
    """
    tables = _load(root / VEX).get("not_affected", [])
    ids = [table.get("id") for table in tables]
    if not all(isinstance(each, str) and each for each in ids):
        msg = f"{VEX} has a [[not_affected]] table whose id is not a string"
        raise ValueError(msg)
    kept = []
    for table in tables:
        if "group" in table:
            if not isinstance(table["group"], str):
                msg = f"{VEX}: {table['id']} has a `group` that is not a string"
                raise ValueError(msg)
            _check_group(root, table)
            if not all_groups:
                continue
        kept.append(table["id"])
    return list(dict.fromkeys(kept))


def command(root: Path, *, all_groups: bool = False) -> list[str]:
    """Return the `uv audit` command line for the tree at the root.

    :param root: the tree whose lock is audited.
    :param all_groups: whether the dependency groups are audited too.
    """
    left_out = [] if all_groups else groups(root)
    flags = [
        *(part for group in left_out for part in ("--no-group", group)),
        *(
            part
            for vulnerability in ignored(root, all_groups=all_groups)
            for part in ("--ignore", vulnerability)
        ),
    ]
    return ["uv", "audit", *PREVIEW, "--locked", *flags]


def main(
    argv: Sequence[str] | None = None,
    run: Callable[[list[str]], int] | None = None,
) -> int:
    """Refuse a tree's own ignores, then run the audit and return its status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root", nargs="?", default=".", type=Path, help="the tree whose lock is audited"
    )
    parser.add_argument(
        "--all-groups",
        action="store_true",
        help="audit the dependency groups too, not only what the wheel declares",
    )
    args = parser.parse_args(argv)

    refused = refusals(args.root)
    if refused:
        for why in refused:
            print(f"::error::{why}")
        return 1
    try:
        audit = command(args.root, all_groups=args.all_groups)
    except ValueError as error:
        print(f"::error::{error}")
        return 1
    grouped = {
        table.get("id")
        for table in _load(args.root / VEX).get("not_affected", [])
        if "group" in table
    }
    for vulnerability in ignored(args.root, all_groups=args.all_groups):
        affects = "what is audited" if vulnerability in grouped else "the release"
        print(
            f"::notice::{vulnerability} is ignored, {VEX} judging it not to"
            f" affect {affects}",
            flush=True,
        )
    print(" ".join(audit), flush=True)
    if run is None:
        return subprocess.run(audit, check=False, cwd=args.root).returncode  # noqa: S603
    return run(audit)


if __name__ == "__main__":
    raise SystemExit(main())
