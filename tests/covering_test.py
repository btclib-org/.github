# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Which rulesets `settings_test.py` counts as covering a ref.

`settings_test.py` reaches GitHub and runs only with the switch set, so
the rule it reads coverage by is asked here, on rulesets written out,
where every run reaches it.
"""

from __future__ import annotations

from typing import Any

import pytest

from . import settings_test
from .settings_test import MAIN, TAGS, covering

# named without the `test_` prefix, so that this module does not collect them
refuses_a_rewrite = settings_test.test_main_refuses_a_rewritten_commit
needs_one_review = (
    settings_test.test_a_merge_needs_one_review_and_a_badge_tree_has_no_bypass
)

# a branch an exclusion spares, which is not main
SCRATCH = "refs/heads/scratch"


def ruleset(
    target: str,
    include: list[str],
    exclude: list[str],
    rules: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Write out a ruleset with the fields `settings_test.py` reads.

    :param target: `branch` or `tag`.
    :param include: the ref patterns it includes.
    :param exclude: the ref patterns it excludes.
    :param rules: the rules it carries, none by default.
    :returns: the ruleset, which nobody bypasses.
    """
    return {
        "target": target,
        "conditions": {"ref_name": {"include": include, "exclude": exclude}},
        "rules": rules or [],
        "bypass_actors": [],
    }


def review(approvals: int) -> dict[str, Any]:
    """Write out the review rule.

    :param approvals: the approvals it asks for.
    :returns: the rule.
    """
    return {
        "type": "pull_request",
        "parameters": {"required_approving_review_count": approvals},
    }


def main_as_designed() -> list[dict[str, Any]]:
    """Write out the rulesets over `main` a badge tree keeps.

    :returns: the integrity ruleset and the review one.
    """
    integrity = [
        {"type": rule}
        for rule in ("required_linear_history", "non_fast_forward", "deletion")
    ]
    return [
        ruleset("branch", [MAIN], [], integrity),
        ruleset("branch", [MAIN], [], [review(1)]),
    ]


def test_a_ruleset_with_no_exclusion_covers_its_ref() -> None:
    """A ruleset that excludes nothing is counted."""
    active = [ruleset("tag", [TAGS], []), ruleset("branch", [MAIN], [])]
    assert covering(active, "tag", TAGS) == [active[0]]
    assert covering(active, "branch", MAIN) == [active[1]]


@pytest.mark.parametrize(
    "exclude",
    [[TAGS], ["refs/tags/v1.0"], ["refs/heads/dev*"]],
    ids=["every-release-tag", "one-release-tag", "another-namespace"],
)
def test_an_exclusion_hides_a_ruleset_from_a_presence_check(
    exclude: list[str],
) -> None:
    """An exclusion is not read for what it spares: it disqualifies.

    :param exclude: the patterns the ruleset excludes.
    """
    active = [ruleset("tag", [TAGS], exclude)]
    assert not covering(active, "tag", TAGS)
    assert covering(active, "tag", TAGS, excluding=True) == active


def test_an_answer_without_exclude_covers_its_ref() -> None:
    """A ruleset whose answer has no `exclude` key still covers its ref."""
    active = [{"target": "tag", "conditions": {"ref_name": {"include": [TAGS]}}}]
    assert covering(active, "tag", TAGS) == active


def test_the_target_and_the_include_still_decide() -> None:
    """A tag ruleset does not cover a branch, nor one ref another's."""
    active = [ruleset("tag", [TAGS], [])]
    assert not covering(active, "branch", TAGS)
    assert not covering(active, "tag", MAIN)


def test_the_rulesets_written_out_here_keep_the_design() -> None:
    """The baseline the cases below add one ruleset to passes both tests."""
    refuses_a_rewrite({"tree": main_as_designed()})
    needs_one_review({"tree": main_as_designed()}, {"tree"})


@pytest.mark.parametrize("include", [MAIN, "~ALL"])
def test_an_excluding_ruleset_still_requiring_signatures_fails(include: str) -> None:
    """Sparing another branch leaves `required_signatures` on `main`.

    :param include: the pattern the signature ruleset includes.
    """
    signatures = ruleset(
        "branch", [include], [SCRATCH], [{"type": "required_signatures"}]
    )
    with pytest.raises(AssertionError, match="still require signatures"):
        refuses_a_rewrite({"tree": [*main_as_designed(), signatures]})


def test_an_excluding_second_review_ruleset_fails() -> None:
    """Sparing another branch leaves a second review rule on `main`."""
    second = ruleset("branch", [MAIN], [SCRATCH], [review(3)])
    with pytest.raises(AssertionError, match="several rulesets carry"):
        needs_one_review({"tree": [*main_as_designed(), second]}, {"tree"})
