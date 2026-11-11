# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Refuse a built page that links at `BLOB` a file a docs page includes.

Section 2 of the standard, *The documentation*, is the rule. This reads
the built html for a link `RootFileLinks` left at `BLOB`.

Run from the root of the tree, with the directory the build wrote:

    uv run --no-project --python 3.15 \
        standard/.github/scripts/check_included_links.py docs/build/html

`BLOB` is `[project.urls] repository` of `pyproject.toml` followed by
`/blob/main/`, `conf.py` reading the same key. The included files are
the ones the `docs/source/*.md` pages include, each page holding at most
one include fence whose path is relative to the page. A fence shown in a
code block is text, not an include. Each link found is printed as
`page:line: url`; `main` says what the exit code is.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

# where the pages sit, relative to the root of the tree
SOURCE = Path("docs/source")

# a line opening or closing a fence: its marker, and the info string after it
FENCE = re.compile(r"^(`{3,}|~{3,})\s*(.*?)\s*$")

# the info string of an include fence; its argument runs to the end of the line
INCLUDE = re.compile(r"^\{include\}\s+(.+)$")

# the name of the directive an info string opens
DIRECTIVE = re.compile(r"^\{([^}]+)\}")

# the directives whose body this check reads as markup, among them the
# admonitions, containers and version notes of docutils and sphinx. Every
# directive not named here is read as code, so an include inside it is
# not checked: {code-block}, {eval-rst} and {toctree}, and also some that
# do parse their body, as {figure}, {list-table} and {glossary}. The list
# names only directives MyST renders by parsing their body, and grows
# when a page needs an include inside another one
PARSED = (
    "admonition",
    "attention",
    "caution",
    "danger",
    "error",
    "hint",
    "important",
    "note",
    "tip",
    "warning",
    "seealso",
    "topic",
    "sidebar",
    "epigraph",
    "highlights",
    "pull-quote",
    "compound",
    "container",
    "only",
    "hlist",
    "acks",
    "deprecated",
    "versionadded",
    "versionchanged",
    "versionremoved",
    "version-deprecated",
    "version-added",
    "version-changed",
    "version-removed",
)


def includes(text: str) -> list[str]:
    """Return the paths of the include fences of a page, in page order.

    A fence opening a directive of `PARSED` holds markdown, which myst
    parses, so a fence inside it is read. Any other fence is code, and
    what it holds is shown, not parsed. A fence closes at a bare marker
    of its own character, at least as long as the one that opened it.

    :param text: the page.
    :returns: the paths, as the fences write them.
    """
    paths: list[str] = []
    # the open fences, innermost last: marker, and whether it is code
    open_fences: list[tuple[str, bool]] = []
    for line in text.splitlines():
        fence = FENCE.match(line)
        if fence is None:
            continue
        marker, info = fence.groups()
        if open_fences:
            top, _ = open_fences[-1]
            if not info and marker[0] == top[0] and len(marker) >= len(top):
                open_fences.pop()
                continue
            if open_fences[-1][1]:
                continue
        if include := INCLUDE.match(info):
            paths.append(include[1])
        directive = DIRECTIVE.match(info)
        open_fences.append((marker, directive is None or directive[1] not in PARSED))
    return paths


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
    """Return the paths, relative to the root, that a page includes.

    :param root: the root of the tree.
    :returns: the paths, `/`-separated.
    :raises ValueError: where a page holds more than one include fence.
    """
    paths: set[str] = set()
    for page in sorted((root / SOURCE).glob("*.md")):
        found = includes(page.read_text(encoding="utf-8"))
        if len(found) > 1:
            msg = f"{page}: {len(found)} include fences, expected at most one"
            raise ValueError(msg)
        for path in found:
            target = (page.parent / path).resolve().relative_to(root.resolve())
            paths.add(target.as_posix())
    return paths


def links(html: Path, prefix: str, paths: set[str]) -> list[str]:
    """List each link of the built pages to an included file at `BLOB`.

    :param html: the directory the build wrote.
    :param prefix: what `blob` returns.
    :param paths: what `included` returns.
    :returns: one `page:line: url` per link, in page order.
    """
    # the path ends at a query, as `?plain=1`, or at a fragment
    href = re.compile(rf'href="({re.escape(prefix)}([^"#?]*)[^"]*)"')
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
            "::error::the links above reach at BLOB a file these pages render, "
            "where they are to reach that page (section 2's The documentation)"
        )
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
