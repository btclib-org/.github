# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Which rulesets `settings_test.py` counts as covering a ref.

`settings_test.py` reaches GitHub and runs only with the switch set, so
the rule it reads coverage by is asked here, on rulesets written out,
where every run reaches it.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

import pytest

from . import settings_test
from .settings_test import MAIN, TAGS, covering

if TYPE_CHECKING:
    from collections.abc import Iterator

# named without the `test_` prefix, so that this module does not collect them
refuses_a_rewrite = settings_test.test_main_refuses_a_rewritten_commit
needs_one_review = (
    settings_test.test_a_merge_needs_one_review_and_a_badge_tree_has_no_bypass
)
refuses_an_unsigned_tag = (
    settings_test.test_a_repository_with_tags_refuses_an_unsigned_one
)
admin_moves_a_tag = settings_test.test_only_an_administrator_moves_a_release_tag

# a branch an exclusion spares, which is not main
SCRATCH = "refs/heads/scratch"
# the repository role `admin`, excused always
ADMIN = {
    "actor_type": "RepositoryRole",
    "actor_id": settings_test.ADMIN_ROLE,
    "bypass_mode": "always",
}


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


def tags_as_designed() -> list[dict[str, Any]]:
    """Write out the rulesets over `refs/tags/v*` every tree keeps.

    :returns: the signature ruleset and the restricting one.
    """
    moves = [{"type": rule} for rule in ("creation", "update", "deletion")]
    return [
        ruleset("tag", [TAGS], [], [{"type": "required_signatures"}]),
        {**ruleset("tag", [TAGS], [], moves), "bypass_actors": [ADMIN]},
    ]


@pytest.fixture
def tagged(monkeypatch: pytest.MonkeyPatch) -> None:
    """Answer that every repository has a tag, without asking GitHub.

    :param monkeypatch: what replaces the call.
    """
    monkeypatch.setattr(settings_test, "gh_json", lambda _: [{"name": "v1"}])


@pytest.mark.usefixtures("tagged")
def test_the_tag_rulesets_written_out_here_keep_the_design() -> None:
    """The baseline the cases below change passes both tag tests."""
    refuses_an_unsigned_tag(["tree"], {"tree": tags_as_designed()})
    admin_moves_a_tag(["tree"], {"tree": tags_as_designed()})


@pytest.mark.usefixtures("tagged")
def test_an_excluding_restriction_nobody_bypasses_fails() -> None:
    """Sparing one tag still keeps an administrator from every other."""
    spare = ruleset("tag", [TAGS], ["refs/tags/v99"], [{"type": "creation"}])
    with pytest.raises(AssertionError, match="admin role bypass is not always"):
        admin_moves_a_tag(["tree"], {"tree": [*tags_as_designed(), spare]})


@pytest.mark.usefixtures("tagged")
def test_a_bypassed_signature_rule_fails() -> None:
    """The admin role's bypass does not reach the signature rule."""
    signed, moves = tags_as_designed()
    combined = {**moves, "rules": [*signed["rules"], *moves["rules"]]}
    with pytest.raises(AssertionError, match="tag signatures are bypassed"):
        refuses_an_unsigned_tag(["tree"], {"tree": [combined]})


# an actor other than the admin role, excused always
SOMEBODY = {"actor_type": "User", "actor_id": 1, "bypass_mode": "always"}


@contextmanager
def fails(match: str) -> Iterator[None]:
    """Expect an assertion naming `match`, and fail where the test skips.

    A skip is what an unread bypass list asks for, so a case whose
    violation is in plain sight has to tell it from the failure.

    :param match: what the assertion says.
    :yields: to the block under test.
    """
    try:
        with pytest.raises(AssertionError, match=match):
            yield
    except pytest.skip.Exception as skipped:
        pytest.fail(f"skipped beside a visible violation: {skipped}")


def unread(rules: dict[str, Any]) -> dict[str, Any]:
    """Return a ruleset as a token without write access to it reads it.

    :param rules: the ruleset.
    :returns: the ruleset without its `bypass_actors`.
    """
    return {key: value for key, value in rules.items() if key != "bypass_actors"}


def test_a_bypass_beside_an_unread_main_ruleset_fails() -> None:
    """One integrity ruleset unread does not hide another one's bypass."""
    integrity, reviewed = main_as_designed()
    first, *rest = integrity["rules"]
    hidden = unread({**integrity, "rules": [first]})
    bypassed = {**integrity, "rules": rest, "bypass_actors": [SOMEBODY]}
    with fails("integrity rules somebody may bypass"):
        refuses_a_rewrite({"tree": [hidden, bypassed, reviewed]})


@pytest.mark.usefixtures("tagged")
def test_a_bypassed_signature_beside_an_unread_one_fails() -> None:
    """One signature ruleset unread does not hide another one's bypass."""
    signed, moves = tags_as_designed()
    bypassed = {**signed, "bypass_actors": [ADMIN]}
    with fails("tag signatures are bypassed"):
        refuses_an_unsigned_tag(["tree"], {"tree": [unread(signed), bypassed, moves]})


@pytest.mark.usefixtures("tagged")
def test_an_unread_signature_ruleset_alone_skips() -> None:
    """Where nothing read is wrong, an unread list is a skip, not a pass."""
    signed, moves = tags_as_designed()
    with pytest.raises(pytest.skip.Exception, match="cannot see"):
        refuses_an_unsigned_tag(["tree"], {"tree": [unread(signed), moves]})


@pytest.mark.parametrize(
    ("actors", "match"),
    [([SOMEBODY], "another actor may push"), ([], "admin role bypass is not always")],
    ids=["another-actor", "nobody"],
)
@pytest.mark.usefixtures("tagged")
def test_a_wrong_restriction_beside_an_unread_one_fails(
    actors: list[dict[str, Any]], match: str
) -> None:
    """One restricting ruleset unread does not hide another one's bypass.

    :param actors: who the read ruleset excuses.
    :param match: the failure that names it.
    """
    signed, moves = tags_as_designed()
    wrong = {**moves, "bypass_actors": actors}
    with fails(match):
        admin_moves_a_tag(["tree"], {"tree": [signed, unread(moves), wrong]})
