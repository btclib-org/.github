# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The rulesets, the merge method and the token section 11 describes.

These are the rules that live in no tree: a repository setting is
invisible to every gate, every hook and every reviewer, and the only
thing that would notice one quietly turned off is somebody opening the
settings page of a repository nobody is currently working on. Three of
section 15's settings commands are asked here; the classic
`branches/main/protection` is `protection_test.py`'s.

Rulesets are read by what they enforce rather than by what they are
called: a rule is what holds the door, and a name is how a person finds
it in a list.
"""

from __future__ import annotations

from typing import Any

import pytest

from .organization import ORG, by_hand, gh_json

MAIN = "refs/heads/main"
TAGS = "refs/tags/v*"

pytestmark = pytest.mark.integration


@pytest.fixture(scope="session")
def rulesets(repositories: list[str]) -> dict[str, list[dict[str, Any]]]:
    """Every active ruleset of every repository, fetched whole.

    The listing endpoint answers with names and enforcement and no rules
    at all, so each one is fetched again by its id: what this suite asks
    about a ruleset is the rules in it.

    :param repositories: the names to ask about.
    :returns: each name against its active rulesets.
    """
    out: dict[str, list[dict[str, Any]]] = {}
    for repository in repositories:
        listed = gh_json(f"repos/{ORG}/{repository}/rulesets")
        out[repository] = [
            gh_json(f"repos/{ORG}/{repository}/rulesets/{entry['id']}")
            for entry in listed
            if entry["enforcement"] == "active"
        ]
    return out


def covering(
    active: list[dict[str, Any]],
    target: str,
    ref: str,
) -> list[dict[str, Any]]:
    """Return the active rulesets that apply to one ref pattern.

    :param active: the repository's rulesets.
    :param target: `branch` or `tag`.
    :param ref: the pattern the ruleset must include.
    :returns: those that match, in the order the API gave them.
    """
    return [
        ruleset
        for ruleset in active
        if ruleset["target"] == target
        and ref in (ruleset["conditions"]["ref_name"]["include"])
    ]


def enforcing(rulesets_of_ref: list[dict[str, Any]], rule: str) -> list[dict[str, Any]]:
    """Return that rule as every ruleset covering the ref carries it.

    Every carrier and not the first: rules are cumulative, so a second
    ruleset naming the same rule with a bypass list of its own excuses
    somebody from it, and a caller reading the first would report the
    door as held while it is not.

    `bypass_actors` comes back attached to the rule rather than to the
    ruleset holding it, because who is excused is a property of the rule
    to every caller here. It is `None` where the endpoint omitted the
    field, which is not the same answer as `[]`: see
    `test_squash_is_the_only_button` for the other field a token without
    push access cannot see, and the same distinction being drawn there.

    :param rulesets_of_ref: the rulesets covering a ref.
    :param rule: the rule type to look for.
    :returns: the rule once per ruleset enforcing it, empty where none
        does.
    """
    return [
        {**entry, "bypass_actors": ruleset.get("bypass_actors")}
        for ruleset in rulesets_of_ref
        for entry in ruleset["rules"]
        if entry["type"] == rule
    ]


def test_main_refuses_an_unsigned_or_rewritten_commit(
    rulesets: dict[str, list[dict[str, Any]]],
) -> None:
    """The four rules that make `main` an append-only, signed branch.

    No bypass on any of them: the review rule is what one person is
    excused from, and this is what nobody is.

    Which rules hold the door is public; who is excused from one is not,
    the endpoint omitting `bypass_actors` for a token without push
    access. The first question is asked of every repository either way,
    and the run reports itself skipped when the second could not be
    asked anywhere it looked.

    :param rulesets: the active rulesets of each repository.
    """
    wanted = (
        "required_signatures",
        "required_linear_history",
        "non_fast_forward",
        "deletion",
    )
    missing: dict[str, list[str]] = {}
    excused: dict[str, list[str]] = {}
    unseen: list[str] = []
    for repository, active in sorted(rulesets.items()):
        covers = covering(active, "branch", MAIN)
        found = {rule: enforcing(covers, rule) for rule in wanted}
        absent = sorted(rule for rule, carried in found.items() if not carried)
        if absent:
            missing[repository] = absent
        present = [entry for carried in found.values() for entry in carried]
        if any(entry["bypass_actors"] is None for entry in present):
            unseen.append(repository)
            continue
        bypassed = sorted(
            rule
            for rule, carried in found.items()
            if any(entry["bypass_actors"] for entry in carried)
        )
        if bypassed:
            excused[repository] = bypassed
    assert not missing, f"main is not protected by: {missing}"
    assert not excused, f"integrity rules somebody may bypass: {excused}"
    if unseen:
        pytest.skip(
            "this run's token cannot see who bypasses a rule on"
            f" {', '.join(unseen)}: bypass_actors needs push access to read"
        )


def test_a_merge_needs_one_review_and_one_person_may_merge_anyway(
    rulesets: dict[str, list[dict[str, Any]]],
) -> None:
    """Review is the gate, and the bypass excuses it while merging only.

    `pull_request` as a bypass mode excuses its holder from the review
    rule while merging a pull request and at no other time. `always`
    would permit a direct push, which is the thing the integrity rules
    above are for.

    One ruleset carries it, because two would each name their own
    approval count and their own bypass list and the branch would enforce
    whichever is stricter -- an answer nobody can read off either page.

    That the rule exists and how many approvals it asks for is public;
    the mode is not, for the reason the test above gives.

    :param rulesets: the active rulesets of each repository.
    """
    wrong: dict[str, str] = {}
    unseen: list[str] = []
    for repository, active in sorted(rulesets.items()):
        carried = enforcing(covering(active, "branch", MAIN), "pull_request")
        if not carried:
            wrong[repository] = "no pull_request rule on main"
            continue
        if len(carried) > 1:
            wrong[repository] = "several rulesets carry the review rule on main"
            continue
        rule = carried[0]
        approvals = rule["parameters"]["required_approving_review_count"]
        if approvals != 1:
            wrong[repository] = f"{approvals} approvals asked for, not 1"
            continue
        actors = rule["bypass_actors"]
        if actors is None:
            unseen.append(repository)
            continue
        modes = sorted(actor["bypass_mode"] for actor in actors)
        if modes != ["pull_request"]:
            wrong[repository] = f"bypass actors are {modes}, not one merging one"
    assert not wrong, f"repositories whose review rule is not the design: {wrong}"
    if unseen:
        pytest.skip(
            "this run's token cannot see who bypasses review on"
            f" {', '.join(unseen)}: bypass_actors needs push access to read"
        )


def test_a_repository_with_tags_refuses_an_unsigned_one(
    repositories: list[str],
    rulesets: dict[str, list[dict[str, Any]]],
) -> None:
    """A release is a signed tag, and the ruleset is what makes it one.

    Asked only of repositories that have a tag: one that has never cut a
    release has nothing to protect yet, and a rule about a shape of tag
    it does not use would be enforcing nothing.

    :param repositories: the names to ask about.
    :param rulesets: the active rulesets of each repository.
    """
    unprotected = [
        repository
        for repository in sorted(repositories)
        if gh_json(f"repos/{ORG}/{repository}/tags?per_page=1")
        and not enforcing(
            covering(rulesets[repository], "tag", TAGS), "required_signatures"
        )
    ]
    assert not unprotected, f"repositories whose tags need no signature: {unprotected}"


def test_squash_is_the_only_button(settings: dict[str, dict[str, Any]]) -> None:
    """One change is one commit on `main`, and the dialog offers one way.

    A merge commit is refused by linear history already; rebase is the
    one deliberately removed, since it replays a branch's review steps
    onto `main`.

    Unlike everything else here, these four fields are not public: the
    repository endpoint omits them for a token without push access, so
    this is the one question a run needs a credential to ask. Skipped
    rather than passed where it cannot be asked -- a token that answers
    for one repository and not the rest would otherwise report the
    organization as aligned on the strength of one row. The skip comes
    after the loop and not inside it, so what was seen before the first
    invisible repository is reported rather than thrown away.

    :param settings: the repository documents.
    """
    wanted = {
        "allow_squash_merge": True,
        "allow_merge_commit": False,
        "allow_rebase_merge": False,
        "delete_branch_on_merge": True,
    }
    wrong: dict[str, dict[str, bool]] = {}
    unseen: dict[str, list[str]] = {}
    for repository, document in sorted(settings.items()):
        absent = [key for key in wanted if key not in document]
        if absent:
            unseen[repository] = absent
            continue
        off = {
            key: document[key] for key, want in wanted.items() if document[key] != want
        }
        if off:
            wrong[repository] = off
    assert not wrong, f"repositories whose merge button is not the design: {wrong}"
    if unseen:
        pytest.skip(
            f"this run's token cannot see the merge method on {unseen}:"
            " those four fields need push access to read"
        )


def test_the_workflow_token_is_read(repository: str) -> None:
    """Section 15: a token that is `read`, and a job elevates what it needs.

    The default grant is the one every workflow runs with that declares
    nothing more, so a `write` here is a write every step of every
    workflow holds.

    :param repository: the repository asked about.
    """
    endpoint = f"repos/{ORG}/{repository}/actions/permissions/workflow"
    granted = gh_json(endpoint)["default_workflow_permissions"]
    assert granted == "read", f"the default workflow token is {granted!r}; " + by_hand(
        repository, f"gh api {endpoint}"
    )
