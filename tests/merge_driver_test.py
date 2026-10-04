# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 9: neither history file has a merge driver, in any tree.

`git check-attr` reads the attribute as git applies it, so a pattern such
as `*.md merge=union` counts, not only a line naming the file.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import by_hand, output

if TYPE_CHECKING:
    from pathlib import Path

# the files section 9 gives no merge driver
HISTORY = ("CHANGELOG.md", "RELEASE_NOTES.md")


def drivers(root: Path) -> dict[str, str]:
    """Read the merge attribute a tree gives each history file.

    The user's own attributes file is switched off, so that a setting
    in it is not read as the tree's.

    :param root: the root of the checkout.
    :returns: each history file whose merge attribute is set, against
        its value.
    """
    out = output(
        "git",
        "-C",
        str(root),
        "-c",
        "core.attributesFile=/dev/null",
        "check-attr",
        "merge",
        "--",
        *HISTORY,
    )
    found = {}
    for line in out.splitlines():
        path, _, value = line.split(": ", 2)
        if value != "unspecified":
            found[path] = value
    return found


def test_neither_history_file_has_a_merge_driver(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 9: a rebase stops on these files, and the file is rebuilt.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    found = drivers(trees[repository])
    assert not found, f"history files with a merge attribute: {found}; " + by_hand(
        repository,
        "git -c core.attributesFile=/dev/null check-attr merge"
        " -- CHANGELOG.md RELEASE_NOTES.md",
    )


def test_a_planted_driver_is_read(tmp_path: Path) -> None:
    """The reading finds a driver a tree sets, and none where it sets none.

    :param tmp_path: where the tree is built.
    """
    output("git", "-C", str(tmp_path), "init", "--quiet")
    assert drivers(tmp_path) == {}
    (tmp_path / ".gitattributes").write_text(
        "CHANGELOG.md merge=union\n", encoding="utf-8"
    )
    assert drivers(tmp_path) == {"CHANGELOG.md": "union"}
