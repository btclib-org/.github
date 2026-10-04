# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 11's labels and issue types, asked of every repository.

`.github/labels.yml` gives each tree its labels, with a colour and a
description each. A tree's labels are the forge's and in no checkout, so
they are read from the API. An issue's kind is its issue type, so each
issue form a tree keeps sets `type:` and applies no kind label.
"""

from __future__ import annotations

import json
from collections import Counter
from typing import TYPE_CHECKING, Any

import yaml

from . import ORG, ROOT, by_hand, gh, tracked

if TYPE_CHECKING:
    from pathlib import Path

# the organization's one set
SET = ROOT / ".github" / "labels.yml"

# where a tree keeps its issue forms; config.yml there is not a form
FORMS = ".github/ISSUE_TEMPLATE"

# the organization's issue types: `gh api orgs/btclib-org/issue-types`
TYPES = {"Bug", "Feature", "Task"}

# GitHub's default kind labels, which no tree carries: an issue's kind is
# its type. The set refuses them as extras; a form applying one is the
# way one comes back.
KINDS = {"bug", "documentation", "enhancement", "question"}


def document() -> dict[str, Any]:
    """Read the set.

    :returns: the file, parsed.
    """
    parsed: dict[str, Any] = yaml.safe_load(SET.read_text(encoding="utf-8"))
    return parsed


def test_the_set_names_each_label_once() -> None:
    """No name is listed twice, whatever the key it is listed under.

    The tests below key the set by name, so a second entry would replace
    the first without a word.
    """
    file = document()
    names = [label["name"] for label in file["labels"]]
    names += file["dependabot"]
    twice = sorted(name for name, count in Counter(names).items() if count > 1)
    assert not twice, f"{SET.name} lists these more than once: {twice}"


def test_a_repository_carries_the_label_set(repository: str) -> None:
    """The tree's labels are the ones the file owes it, as the file has them.

    A colour is compared without case: GitHub keeps the case it was
    given, and both spellings name one colour.

    :param repository: the repository asked about.
    """
    file = document()
    passed_over = set(file["dependabot"])
    owed = {
        label["name"]: (label["color"].lower(), label["description"])
        for label in file["labels"]
        if repository in label.get("repositories", [repository])
    }
    held = {
        label["name"]: (label["color"].lower(), label["description"] or "")
        for label in map(
            json.loads,
            gh(f"repos/{ORG}/{repository}/labels?per_page=100", ".[] | tojson"),
        )
        if label["name"] not in passed_over
    }
    missing = sorted(owed.keys() - held.keys())
    extra = sorted(held.keys() - owed.keys())
    both = owed.keys() & held.keys()
    differ = sorted(name for name in both if owed[name] != held[name])
    assert held == owed, (
        f"{repository} against {SET.name}: missing {missing}, not in it {extra},"
        f" colour or description differing {differ}; "
        + by_hand(repository, "gh label list --limit 100 --json name,color,description")
    )


def test_an_issue_form_sets_a_type_and_no_kind_label(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Every form sets an issue type, and its `labels:` names no kind label.

    GitHub reads `labels:` as a list or as a comma-delimited string, so
    both are split.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    wrong = []
    for path in tracked(root, f"{FORMS}/*.yml", f"{FORMS}/*.yaml"):
        if path.rsplit("/", 1)[-1] in {"config.yml", "config.yaml"}:
            continue
        form = yaml.safe_load((root / path).read_text(encoding="utf-8"))
        labels = form.get("labels") or []
        if isinstance(labels, str):
            labels = labels.split(",")
        if form.get("type") not in TYPES or KINDS & {label.strip() for label in labels}:
            wrong.append(path)
    assert not wrong, (
        f"{repository}: these forms set no issue type, or apply a kind label: {wrong}; "
        + by_hand(repository, f"grep -nE '^(type|labels):' {FORMS}/*.y*ml")
    )
