# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 11's review of the dependencies a pull request adds.

Three questions of this tree and two of every tree. Of this tree: that the
organization's file holds only keys the action reads and states the policy
the section gives, and that `reusable-lint.yml`'s job reads that file at
`main`, with the action pinned and the token no wider than read access.
Of every tree: that the forge's dependency graph is on, which is what the
action reads, and that the lint gate runs the job, either by calling
`reusable-lint.yml` or by carrying the action in its own `lint.yml`.

What is not read is the action's behaviour. A config file the action
refuses, or a licence it would fail on, is found by running the action's
own parser, which is not something this suite can do without a node
toolchain; the file's comments say what each entry was measured against.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
import yaml

from . import ORG, ROOT, SELF, Refused, by_hand, gh_json
from .workflows_test import jobs

if TYPE_CHECKING:
    from pathlib import Path

CONFIG = ROOT / ".github" / "dependency-review.yml"
"""The organization's one file, which section 11 says every tree reads."""

REUSABLE = ROOT / ".github" / "workflows" / "reusable-lint.yml"
"""The workflow whose `dependency-review` job reads it."""

READ_AS = f"{ORG}/{SELF}/.github/dependency-review.yml@main"
"""How a workflow names the file: at `main`, as a reusable call does."""

KEYS = frozenset(
    {
        "allow-dependencies-licenses",
        "allow-ghsas",
        "allow-licenses",
        "base-ref",
        "comment-summary-in-pr",
        "deny-groups",
        "deny-licenses",
        "deny-packages",
        "fail-on-scopes",
        "fail-on-severity",
        "head-ref",
        "license-check",
        "retry-on-snapshot-warnings",
        "retry-on-snapshot-warnings-timeout",
        "show-openssf-scorecard",
        "show-patched-versions",
        "vulnerability-check",
        "warn-on-openssf-scorecard-level",
        "warn-only",
    }
)
"""What the action's config file accepts, read off its `action.yml`.

The action drops a key it does not know without a word, so a misspelt
`fail-on-severty` is a threshold silently not set."""

ACTION = re.compile(r"actions/dependency-review-action@[0-9a-f]{40}\b")
"""The action at a commit, which section 10 says every action is."""

PURL = re.compile(r"pkg:[a-z]+/[a-z0-9]+(?:[-_.][a-z0-9]+)*")
"""An ecosystem and a name, no version: the action matches by name."""


def test_the_organization_file_states_the_policy() -> None:
    """The file holds the threshold and the licence lists section 11 gives.

    `allow-ghsas` is absent because section 11 sends an allowed advisory
    to `.github/vex.toml`, and `deny-licenses` because the action refuses
    it beside `allow-licenses`.
    """
    parsed = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert set(parsed) <= KEYS, f"unknown keys {sorted(set(parsed) - KEYS)}"
    assert parsed["fail-on-severity"] == "moderate"
    assert "allow-ghsas" not in parsed
    assert "deny-licenses" not in parsed
    allowed = parsed["allow-licenses"]
    assert allowed == sorted(set(allowed)), "allow-licenses is not sorted and unique"
    # the action drops an entry holding an expression, so one would
    # read as a licence allowed while allowing nothing
    assert not [item for item in allowed if re.search(r"\s", item)], allowed
    excepted = parsed["allow-dependencies-licenses"]
    assert all(PURL.fullmatch(item) for item in excepted), excepted
    assert len(set(excepted)) == len(excepted)


def test_the_reusable_job_reads_the_organization_file() -> None:
    """The job pins the action, reads the file at `main`, and reads contents."""
    job = jobs(REUSABLE)["dependency-review"]
    assert job["name"] == "Dependency review"
    assert job["permissions"] == {"contents": "read"}
    assert "github.event_name == 'pull_request'" in job["if"]
    (step,) = job["steps"]
    assert ACTION.fullmatch(step["uses"]), step["uses"]
    assert step["with"]["config-file"] == READ_AS
    assert CONFIG.is_file()


def test_the_dependency_graph_is_on(repository: str) -> None:
    """The action has a graph to compare, which is a setting and not a file.

    The call is the action's own, the compare endpoint, which answers 403
    where the graph is off. Not the SBOM endpoint, which generates a
    document on each call and can time out with a 500 that says nothing
    about the setting.

    :param repository: the repository asked about.
    """
    endpoint = f"repos/{ORG}/{repository}/dependency-graph/compare/HEAD...HEAD"
    try:
        gh_json(endpoint)
    except Refused as refused:
        said = refused.stderr.strip()
        pytest.fail(f"{said}; " + by_hand(repository, f"gh api {endpoint}"))


def test_the_lint_gate_reviews_added_dependencies(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """The tree's `lint.yml` calls the reusable workflow or carries the action.

    A call is enough: the job it runs is the one the test above reads. A
    tree with its own `lint.yml` owes the action and the file's name.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    path = trees[repository] / ".github" / "workflows" / "lint.yml"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    called = f"{ORG}/{SELF}/.github/workflows/reusable-lint.yml@main" in text
    carried = bool(ACTION.search(text)) and READ_AS in text
    assert called or carried, (
        "lint.yml neither calls reusable-lint.yml nor runs the action on "
        f"{READ_AS}; "
        + by_hand(repository, "grep -c dependency-review .github/workflows/lint.yml")
    )
