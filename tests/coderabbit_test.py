# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""CodeRabbit never approves, as section 11's *Review* says.

The rule and its reason are there. Section 14 owes every tree this file,
so this tree's copy is the one read here.
"""

from __future__ import annotations

from typing import Any

import yaml

from . import ROOT

CONFIG = ROOT / ".coderabbit.yaml"


def reviews() -> dict[str, Any]:
    """Read the `reviews` table of this tree's `.coderabbit.yaml`.

    :returns: the table, as PyYAML parses it.
    """
    parsed: dict[str, dict[str, Any]] = yaml.safe_load(
        CONFIG.read_text(encoding="utf-8")
    )
    return parsed["reviews"]


def test_coderabbit_approves_nothing_on_its_own() -> None:
    """The automatic approval is off, written out rather than defaulted."""
    assert reviews()["auto_approvals"]["enabled"] is False


def test_an_author_cannot_ask_coderabbit_for_an_approval() -> None:
    """The author's `@coderabbitai approve` is refused."""
    assert reviews()["auto_approvals"]["allow_author_approval"] is False


def test_no_legacy_alias_stands_beside_the_keys() -> None:
    """The schema's older names for the same two keys are absent.

    `request_changes_workflow` and `allow_author_approval` directly under
    `reviews` alias the keys above. Where `request_changes_workflow` and
    `enabled` disagree, CodeRabbit turns the approvals off and reports a
    configuration error, its *Automatic Approvals* page says: an alias is
    a second place for the same fact, so neither is written.
    """
    assert not {"request_changes_workflow", "allow_author_approval"} & set(reviews())
