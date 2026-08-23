# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 11's Dependabot ecosystems, read off each `dependabot.yml`.

The section closes the count -- three ecosystems, and pre-commit
revisions the fourth with none -- and section 2 lists the file among
what `.github/` holds. A tree without the file and a tree declaring an
ecosystem the section does not name are the two ways the trees can
disagree with it, and the backlog names the issue for each.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from .organization import by_hand

pytestmark = pytest.mark.integration

NAMED = {"github-actions", "uv", "bundler"}
"""Section 11's three, `bundler` where a site Gemfile exists."""


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
