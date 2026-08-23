# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 11's Dependabot ecosystems, read off each `dependabot.yml`.

The section names two the tree carries whatever it holds, `github-actions`
and `uv`, and two more a tree earns by holding what they watch; pre-commit
hook revisions have no ecosystem at all, pre-commit.ci updating them.
Section 2 lists the file among what `.github/` holds. A tree without the
file, and a tree declaring an ecosystem the section does not name, are the
two ways a tree can disagree with the section, and what this module asks.
Which of the four a tree is owed is the half the section makes conditional
and this module does not measure -- btclib-org/.github#171.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from . import by_hand

pytestmark = pytest.mark.integration

NAMED = {"github-actions", "uv", "bundler", "gitsubmodule"}
"""Section 11's ecosystems, the last two conditional on the tree."""


def test_dependabot_watches_only_the_ecosystems_section_11_names(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Every declared `package-ecosystem` is one the section names.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    path = trees[repository] / ".github" / "dependabot.yml"
    command = by_hand(
        repository,
        "sed -n 's/^ *- *package-ecosystem: *//p' .github/dependabot.yml",
    )
    assert path.is_file(), (
        "no .github/dependabot.yml, which section 2 lists; " + command
    )
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    declared = {entry["package-ecosystem"] for entry in parsed.get("updates", [])}
    unknown = sorted(declared - NAMED)
    assert not unknown, f"ecosystems section 11 does not name: {unknown}; " + command
