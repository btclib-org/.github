# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 11's Dependabot ecosystems, read off each `dependabot.yml`.

The section names two the tree carries whatever it holds, `github-actions`
and `uv`, and two more a tree earns by holding what they watch; pre-commit
hook revisions have no ecosystem at all, pre-commit.ci updating them.
Section 2 lists the file among what `.github/` holds. The section gives
the first two without a condition, so where a tree declines one the
finding is either the tree's or the section's, and the issue the backlog
names is where that is decided.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from . import by_hand, tracked

pytestmark = pytest.mark.integration

CONFIG = ".github/dependabot.yml"

DECLARED = f"sed -n 's/^ *- *package-ecosystem: *//p' {CONFIG}"
"""How a reader takes the ecosystems out of the file in a checkout."""

EVERY_TREE = {"github-actions", "uv"}
"""Section 11's ecosystems every tree declares, whatever it holds."""

WATCHED = {
    "bundler": ("Gemfile", "*/Gemfile"),
    "gitsubmodule": (".gitmodules",),
}
"""Section 11's conditional ecosystems, each against what it watches.

The pathspecs are `git ls-files`'s, so a site Gemfile is found wherever
the site keeps it and a submodule by the file git writes at the root.
"""

PATHSPECS = " ".join(
    f"'{pattern}'" for patterns in WATCHED.values() for pattern in patterns
)
"""The pathspecs above, as a reader passes them to `git ls-files`."""

NAMED = EVERY_TREE | set(WATCHED)
"""Every ecosystem section 11 names, conditional or not."""


def ecosystems(repository: str, trees: dict[str, Path]) -> set[str]:
    """Return every `package-ecosystem` a repository's file declares.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the ecosystems declared, whatever they are.
    :raises FileNotFoundError: where the tree has no `dependabot.yml`,
        section 2 listing it among what `.github/` holds.
    """
    path = trees[repository] / CONFIG
    if not path.is_file():
        msg = f"{repository} has no {CONFIG}; " + by_hand(repository, DECLARED)
        raise FileNotFoundError(msg)
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {entry["package-ecosystem"] for entry in parsed.get("updates", [])}


def test_dependabot_watches_only_the_ecosystems_section_11_names(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Every declared `package-ecosystem` is one the section names.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    unknown = sorted(ecosystems(repository, trees) - NAMED)
    assert not unknown, f"ecosystems section 11 does not name: {unknown}; " + by_hand(
        repository, DECLARED
    )


def test_dependabot_watches_what_section_11_gives_every_tree(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """`github-actions` and `uv`, which the section makes no tree earn.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    missing = sorted(EVERY_TREE - ecosystems(repository, trees))
    assert not missing, (
        f"ecosystems section 11 gives every tree and this one omits: {missing}; "
        + by_hand(repository, DECLARED)
    )


def test_dependabot_watches_a_conditional_ecosystem_where_its_subject_is_there(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """`bundler` where the tree has a Gemfile, `gitsubmodule` where a submodule.

    Both directions, since an ecosystem watching what the tree does not
    have and a subject nothing watches are the same disagreement with
    the section read from either end.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    declared = ecosystems(repository, trees) & set(WATCHED)
    owed = {name for name, patterns in WATCHED.items() if tracked(root, *patterns)}
    assert declared == owed, (
        f"conditional ecosystems declared {sorted(declared)}, and the tree holds"
        f" what {sorted(owed)} watch; "
        + by_hand(repository, f"{DECLARED}; git ls-files {PATHSPECS}")
    )
