# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Refuse a built page that links at `BLOB` a file the docs render.

Section 2 of the standard, *The documentation*, is the rule. This reads
the built html for a link `RootFileLinks` left at `BLOB`.

Run from the root of the tree, with the directory the build wrote:

    uv run --no-project --python 3.15 \
        standard/.github/scripts/check_included_links.py docs/build/html

`BLOB` is `[project.urls] repository` of `pyproject.toml` followed by
`/blob/main/`, `conf.py` reading the same key. The rendered files are
the ones the `docs/source/*_link.md` shims include, each shim holding
one include fence whose path is relative to the shim. Each link found
is printed as `page:line: url`; `main` says what the exit code is.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

# where the shims sit, relative to the root of the tree
SOURCE = Path("docs/source")

# the include fence of a shim; its argument runs to the end of the line
INCLUDE = re.compile(r"^```\{include\}\s+(.+?)\s*$", re.MULTILINE)


def blob(root: Path) -> str:
    """Return the url prefix of a file of the tree on its default branch.

    The `[project.urls]` key is read as tests/pyproject_test.py compares
    section 3's keys, case folded and a space read as an underscore, so
    `Repository` is the same link as `repository`.

    :param root: the root of the tree.
    :returns: `<repository>/blob/main/`.
    """
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    urls = {
        key.lower().replace(" ", "_"): url
        for key, url in project["project"]["urls"].items()
    }
    return f"{urls['repository'].rstrip('/')}/blob/main/"


def included(root: Path) -> set[str]:
    """Return the paths, relative to the root, that a shim includes.

    :param root: the root of the tree.
    :returns: the paths, `/`-separated.
    :raises ValueError: where a shim holds other than one include fence.
    """
    paths: set[str] = set()
    for shim in sorted((root / SOURCE).glob("*_link.md")):
        found = INCLUDE.findall(shim.read_text(encoding="utf-8"))
        if len(found) != 1:
            msg = f"{shim}: {len(found)} include fences, expected one"
            raise ValueError(msg)
        target = (shim.parent / found[0]).resolve().relative_to(root.resolve())
        paths.add(target.as_posix())
    return paths


def links(html: Path, prefix: str, paths: set[str]) -> list[str]:
    """List each link of the built pages to an included file at `BLOB`.

    :param html: the directory the build wrote.
    :param prefix: what `blob` returns.
    :param paths: what `included` returns.
    :returns: one `page:line: url` per link, in page order.
    """
    href = re.compile(rf'href="({re.escape(prefix)}([^"#]*)[^"]*)"')
    found: list[str] = []
    for page in sorted(html.rglob("*.html")):
        lines = page.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, 1):
            found.extend(
                f"{page}:{number}: {match[1]}"
                for match in href.finditer(line)
                if match[2] in paths
            )
    return found


def main(argv: list[str]) -> int:
    """Check the directory named on the command line.

    :param argv: the arguments, the directory the build wrote alone.
    :returns: 0 where no page links an included file at `BLOB`, 1 where
        one does, 2 on a wrong argument count or a directory holding no
        page, where a 0 would answer for pages nobody read.
    """
    if len(argv) != 1:
        print("usage: check_included_links.py <built html directory>")
        return 2
    if not any(Path(argv[0]).rglob("*.html")):
        print(f"::error::{argv[0]} holds no built page to read")
        return 2
    root = Path.cwd()
    found = links(Path(argv[0]), blob(root), included(root))
    for line in found:
        print(line)
    if found:
        print(
            "::error::the links above reach at BLOB a file these pages render; "
            "RootFileLinks in docs/source/conf.py is to turn them into that page "
            "(section 2's The documentation)"
        )
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
