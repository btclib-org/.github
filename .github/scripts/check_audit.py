# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Audit the lock for what a release publishes, before it publishes.

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
does not publish are left to Dependabot's alerts, which read the whole lock.

What is ignored is what `.github/vex.toml` names: each `[[not_affected]]`
table's `id` is passed as `--ignore`, so the gate's only exemptions are
the ones the release states in its own signed document. A tree owes no
such file where it has no entry. `uv audit` would read an ignore from
`[tool.uv.audit]` in `pyproject.toml` and from `[audit]` in `uv.toml`, and
neither is read here, the run refusing a tree that has one: an ignore kept
there is not in the release's document. `--ignore` matches an advisory's
id and its aliases in every package of the set, where an entry names one
component, so an entry for a component can exempt the same advisory in
another. `--ignore-until-fixed` is not used, a finding that does not
affect a release having nothing to do with whether a fix exists.

    uv run --no-project --python 3.15 .github/scripts/check_audit.py

run from the root of the tree whose lock it audits.
"""

from __future__ import annotations

import argparse
import subprocess
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

# the spelling `uv audit`'s own warning gives for lifting the warning
PREVIEW = ("--preview-features", "audit-command")

VEX = Path(".github") / "vex.toml"


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


def ignored(root: Path) -> list[str]:
    """Return the ids `.github/vex.toml` judges not to affect the release."""
    tables = _load(root / VEX).get("not_affected", [])
    ids = [table.get("id") for table in tables]
    if not all(isinstance(each, str) and each for each in ids):
        msg = f"{VEX} has a [[not_affected]] table whose id is not a string"
        raise ValueError(msg)
    return list(dict.fromkeys(ids))


def command(root: Path) -> list[str]:
    """Return the `uv audit` command line for the tree at the root."""
    flags = [
        *(part for group in groups(root) for part in ("--no-group", group)),
        *(
            part
            for vulnerability in ignored(root)
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
    args = parser.parse_args(argv)

    refused = refusals(args.root)
    if refused:
        for why in refused:
            print(f"::error::{why}")
        return 1
    try:
        audit = command(args.root)
    except ValueError as error:
        print(f"::error::{error}")
        return 1
    for vulnerability in ignored(args.root):
        print(
            f"::notice::{vulnerability} is ignored, {VEX} judging it not to"
            " affect the release",
            flush=True,
        )
    print(" ".join(audit), flush=True)
    if run is None:
        return subprocess.run(audit, check=False, cwd=args.root).returncode  # noqa: S603
    return run(audit)


if __name__ == "__main__":
    raise SystemExit(main())
