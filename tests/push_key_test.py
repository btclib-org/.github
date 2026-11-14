# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 10's push key, read off every workflow a push to main runs.

The key is read off the standard and asked of each tree's workflows. The
tests below the first run offline and hold the reader to the shapes it
has to tell apart: each way `on:` reaches `main`, the release call's
suffix, and the per-ref key a publishing workflow keeps.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import ROOT, branch_listed, by_hand, listed
from .workflows_test import document, gated, jobs, triggers

if TYPE_CHECKING:
    from pathlib import Path

FENCE = re.compile(r"^( *)```yaml\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
"""A fenced YAML block of the standard, at any indent, with its indent.

Section 10 gives the push key in a block inside a bullet, so the fence is
indented, and the block is dedented by the fence's own indent before it
is parsed.
"""

MAIN = "main"
"""The branch whose pushes section 10 keys on their commit."""

PUSH_TERM = "github.event_name == 'push' && github.sha || "
"""The term section 10's key opens with, and a publishing workflow drops."""

SUFFIX = "${{ inputs.concurrency-suffix }}"
"""What a gate the release workflow calls appends to its group (section 10)."""

ALONE = "${{ github.sha }}"
"""The key section 10 admits for every run of a workflow with no PR trigger."""

REF_ALONE = "${{ github.ref }}"
"""The per-ref key a publishing workflow with no PR trigger may also take."""

WRITE_ALL = "write-all"
"""The `permissions:` value that grants every scope, `id-token` among them."""


def keyed(standard: Path = ROOT / "README.md") -> str:
    """Read the key section 10 gives a workflow with a push trigger on main.

    Off the standard rather than transcribed here, for the reason
    `workflows_test.conditional` gives. The key is the group from its
    first `${{` on: the name before it is each workflow's own.

    :param standard: the file to read, this tree's own `README.md`.
    :returns: the key, folded as YAML folds it.
    :raises LookupError: where the file does not give exactly one block
        whose `concurrency:` names a group, or where that key does not
        open with `PUSH_TERM`.
    """
    found: list[str] = []
    for indent, body in FENCE.findall(standard.read_text(encoding="utf-8")):
        block = "".join(
            line.removeprefix(indent) for line in body.splitlines(keepends=True)
        )
        parsed = yaml.safe_load(block)
        concurrency = parsed.get("concurrency") if isinstance(parsed, dict) else None
        group = concurrency.get("group") if isinstance(concurrency, dict) else None
        if isinstance(group, str) and "${{" in group:
            found.append(group[group.index("${{") :])
    if len(found) != 1:
        msg = f"{standard.name} gives {len(found)} concurrency groups in YAML blocks"
        raise LookupError(msg)
    if not found[0].startswith("${{ " + PUSH_TERM):
        msg = f"{standard.name}'s key does not open with {PUSH_TERM!r}"
        raise LookupError(msg)
    return found[0]


def events(workflow: Path) -> dict[str, Any]:
    """Read a workflow's events, whichever of its three forms `on:` takes.

    `triggers` reads the mapping alone. A string or a list names events
    with no filter, each of which reaches every branch.

    :param workflow: the file to read.
    :returns: each event against its filter, None where it has none.
    """
    parsed = document(workflow)
    on = parsed.get("on", parsed.get(True, {}))
    if isinstance(on, str):
        return {on: None}
    if isinstance(on, list):
        return {str(event): None for event in on}
    return on if isinstance(on, dict) else {}


def pushed_to_main(workflow: Path) -> bool:
    """Say whether a push to `main` starts a run of a workflow.

    Its branch filter decides as GitHub reads one, through
    `branch_listed`: `branches` takes the branch, `branches-ignore`
    leaves out what it takes. A push with neither reaches every branch,
    unless it filters on tags, which then confines it to tags.

    :param workflow: the file to read.
    :returns: whether its `push` trigger reaches `main`.
    """
    on = events(workflow)
    if "push" not in on:
        return False
    push = on["push"]
    if not isinstance(push, dict):
        return True
    if "branches" in push:
        return branch_listed(listed(push["branches"]), MAIN)
    if "branches-ignore" in push:
        return not branch_listed(listed(push["branches-ignore"]), MAIN)
    return "tags" not in push and "tags-ignore" not in push


def publishes(workflow: Path) -> bool:
    """Say whether a workflow holds the token that publishes outside the run.

    `id-token: write` is what a Pages deployment and a published
    Scorecard result each hold, at the workflow's level or a job's.
    `write-all` grants it with every other scope.

    :param workflow: the file to read.
    :returns: whether any of its `permissions:` blocks grants it.
    """
    blocks = [
        document(workflow).get("permissions"),
        *(job.get("permissions") for job in jobs(workflow).values()),
    ]
    return any(
        block == WRITE_ALL
        or (isinstance(block, dict) and block.get("id-token") == "write")
        for block in blocks
    )


def group(workflow: Path) -> str:
    """Read a workflow's concurrency group.

    :param workflow: the file to read.
    :returns: the group, given as a mapping's `group` or as a bare name,
        empty where the workflow declares none.
    """
    found = document(workflow).get("concurrency")
    found = found.get("group") if isinstance(found, dict) else found
    return found if isinstance(found, str) else ""


def suffixed(workflow: Path) -> bool:
    """Say whether a workflow takes the suffix a release call passes.

    :param workflow: the file to read.
    :returns: whether its `workflow_call` declares `concurrency-suffix`.
    """
    call = triggers(workflow).get("workflow_call")
    inputs = call.get("inputs") if isinstance(call, dict) else None
    return isinstance(inputs, dict) and "concurrency-suffix" in inputs


def keyed_as_asked(workflow: Path, wanted: str) -> bool:
    """Say whether a workflow a push to main runs keys its group as asked.

    Every accepted key ends with `SUFFIX` exactly where the workflow
    declares it: without it, a tag push's release call would share the
    group of main's push run on that commit, and cancel it.

    :param workflow: the file to read.
    :param wanted: the key section 10 gives, as `keyed` reads it.
    :returns: for a workflow that publishes, whether its key is `wanted`
        without `PUSH_TERM`, or also `REF_ALONE` where it has no
        `pull_request` trigger; for any other, whether its key is
        `wanted`, or also `ALONE` where it has no `pull_request` trigger.
    """
    found = group(workflow)
    key = found[found.index("${{") :] if "${{" in found else found
    reviewed = "pull_request" in events(workflow)
    if publishes(workflow):
        allowed = [wanted.replace(PUSH_TERM, "", 1)]
        extra = REF_ALONE
    else:
        allowed = [wanted]
        extra = ALONE
    if not reviewed:
        allowed.append(extra)
    tail = SUFFIX if suffixed(workflow) else ""
    return key in {each + tail for each in allowed}


@pytest.mark.integration
def test_a_push_run_on_main_is_keyed_on_its_commit(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 10's push key, asked of every workflow a push to main runs.

    Compared as a string after YAML has folded it, as the conditional at
    `cancel-in-progress` is, the name before the key being the
    workflow's own.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    wanted = keyed()
    wrong = [
        f"{workflow.name}: {group(workflow)!r}"
        for workflow in gated(repository, trees)
        if pushed_to_main(workflow) and not keyed_as_asked(workflow, wanted)
    ]
    assert not wrong, f"a push run is not keyed as section 10 says: {wrong}; " + (
        by_hand(repository, "grep -n -A4 '^concurrency:' .github/workflows/*.yml")
    )


@pytest.mark.parametrize(
    ("on", "wanted"),
    [
        ("on: push\n", True),
        ("on: [push, pull_request]\n", True),
        ("on:\n  push:\n", True),
        ("on:\n  push:\n    branches: [main]\n", True),
        ("on:\n  push:\n    branches: main\n", True),
        ("on:\n  push:\n    branches: ['**']\n", True),
        ("on:\n  push:\n    branches: ['**', '!main']\n", False),
        ("on:\n  push:\n    branches: [release]\n", False),
        ("on:\n  push:\n    branches-ignore: [main]\n", False),
        ("on:\n  push:\n    branches-ignore: [release]\n", True),
        ("on:\n  push:\n    paths: [src/**]\n", True),
        ("on:\n  push:\n    tags: ['v*']\n", False),
        ("on:\n  push:\n    tags-ignore: ['v*']\n", False),
        ("on:\n  pull_request:\n", False),
        ("on: pull_request\n", False),
    ],
    ids=[
        "a bare string",
        "a list",
        "a mapping with no filter",
        "main listed",
        "main as one string",
        "every branch",
        "every branch but main",
        "another branch",
        "main ignored",
        "another branch ignored",
        "paths alone",
        "tags alone",
        "tags ignored alone",
        "no push",
        "no push, a string",
    ],
)
def test_a_push_to_main_is_read_as_github_reads_the_trigger(
    tmp_path: Path, on: str, *, wanted: bool
) -> None:
    """Each shape `on:` takes reaches `main` or not as GitHub reads it.

    :param tmp_path: where the workflow is written.
    :param on: the workflow's `on:` block.
    :param wanted: whether a push to `main` runs it.
    """
    workflow = tmp_path / "w.yml"
    workflow.write_text(f"{on}jobs: {{}}\n", encoding="utf-8")
    assert pushed_to_main(workflow) is wanted


KEY = (
    "  group: >-\n    {name}-${{{{ github.event_name == 'push' && github.sha\n"
    "    || github.event.pull_request.number || github.ref }}}}{tail}\n"
)
"""Section 10's block as a tree writes it, the name and suffix filled."""

PUSHED = "  push:\n    branches: [main]\n"
REVIEWED = PUSHED + "  pull_request:\n"
CALLED = (
    "  workflow_call:\n    inputs:\n      concurrency-suffix:\n        type: string\n"
)
PUBLISHING = "permissions:\n  id-token: write\n"
PER_REF = "${{ github.event.pull_request.number || github.ref }}"


def written(tmp_path: Path, on: str, group_block: str, permissions: str = "") -> Path:
    """Write a workflow of one job and no steps.

    :param tmp_path: where it is written.
    :param on: the events under `on:`.
    :param group_block: the lines under `concurrency:`.
    :param permissions: a workflow-level `permissions:` block, or none.
    :returns: the file.
    """
    workflow = tmp_path / "w.yml"
    workflow.write_text(
        f"on:\n{on}concurrency:\n{group_block}  cancel-in-progress: true\n"
        f"{permissions}jobs: {{}}\n",
        encoding="utf-8",
    )
    return workflow


def line(key: str) -> str:
    """Write a group on one line.

    :param key: the group.
    :returns: the line under `concurrency:`.
    """
    return f"  group: {key}\n"


@pytest.mark.parametrize(
    ("on", "group_block", "permissions", "wanted"),
    [
        (REVIEWED, KEY.format(name="lint", tail=""), "", True),
        (REVIEWED + CALLED, KEY.format(name="test", tail=SUFFIX), "", True),
        (REVIEWED + CALLED, KEY.format(name="test", tail=""), "", False),
        (REVIEWED, KEY.format(name="test", tail=SUFFIX), "", False),
        (
            REVIEWED,
            line(
                "lint-${{ github.event_name == 'push' && github.sha"
                " || github.event.pull_request.number || github.ref }}"
            ),
            "",
            True,
        ),
        (
            REVIEWED,
            line(
                "lint-${{ github.event.pull_request.number"
                " || github.event_name == 'push' && github.sha || github.ref }}"
            ),
            "",
            False,
        ),
        (
            REVIEWED,
            line("lint-${{ github.event.pull_request.number || github.ref }}"),
            "",
            False,
        ),
        (PUSHED, line("v-${{ github.sha }}"), "", True),
        (REVIEWED, line("v-${{ github.sha }}"), "", False),
        (PUSHED + CALLED, line("v-${{ github.sha }}"), "", False),
        (PUSHED + CALLED, line("v-${{ github.sha }}" + SUFFIX), "", True),
        (PUSHED, line("scorecard-${{ github.ref }}"), PUBLISHING, True),
        (
            PUSHED,
            line("scorecard-${{ github.ref }}-${{ github.run_id }}"),
            PUBLISHING,
            False,
        ),
        (PUSHED, line("scorecard-${{ github.sha }}"), PUBLISHING, False),
        (
            REVIEWED,
            line("website-${{ github.event.pull_request.number || github.ref }}"),
            PUBLISHING,
            True,
        ),
        (REVIEWED, KEY.format(name="website", tail=""), PUBLISHING, False),
        (REVIEWED, line("website-${{ github.ref }}"), PUBLISHING, False),
        (PUSHED, line(f"scorecard-{PER_REF}"), PUBLISHING, True),
        (PUSHED + CALLED, line(f"scorecard-{PER_REF}{SUFFIX}"), PUBLISHING, True),
        (PUSHED + CALLED, line(f"scorecard-{PER_REF}"), PUBLISHING, False),
        (
            PUSHED + CALLED,
            line("scorecard-${{ github.ref }}" + SUFFIX),
            PUBLISHING,
            True,
        ),
        (PUSHED, KEY.format(name="w", tail=""), "permissions: write-all\n", False),
        (PUSHED, line("w-${{ github.ref }}"), "permissions: write-all\n", True),
        (REVIEWED, "  group: ''\n", "", False),
    ],
    ids=[
        "the key",
        "the key and the suffix",
        "the suffix missing",
        "a suffix never declared",
        "the key on one line",
        "the terms swapped",
        "the per-ref key",
        "the commit alone, no pull request",
        "the commit alone, with a pull request",
        "the commit alone, the suffix missing",
        "the commit alone and the suffix",
        "a publisher on its ref",
        "a publisher on its ref and its run",
        "a publisher on its commit",
        "a publisher with a pull request, on its ref",
        "a publisher with a pull request, on its commit",
        "a publisher with a pull request, on its ref alone",
        "a publisher with no pull request, on the per-ref key",
        "a publisher on the per-ref key and the suffix",
        "a publisher on the per-ref key, the suffix missing",
        "a publisher on its ref and the suffix",
        "write-all, on its commit",
        "write-all, on its ref",
        "an empty group",
    ],
)
def test_a_group_is_keyed_as_section_10_asks(
    tmp_path: Path,
    on: str,
    group_block: str,
    permissions: str,
    *,
    wanted: bool,
) -> None:
    """Each group reads as the key section 10 gives, or as a departure.

    :param tmp_path: where the workflow is written.
    :param on: the events under `on:`.
    :param group_block: the lines under `concurrency:`.
    :param permissions: a workflow-level `permissions:` block, or none.
    :param wanted: whether the group is the one asked.
    """
    workflow = written(tmp_path, on, group_block, permissions)
    assert keyed_as_asked(workflow, keyed()) is wanted


@pytest.mark.parametrize(
    ("text", "wanted"),
    [
        ("permissions:\n  id-token: write\njobs: {}\n", True),
        ("permissions: write-all\njobs: {}\n", True),
        (
            "permissions:\n  contents: read\njobs:\n  a:\n    permissions: write-all\n",
            True,
        ),
        (
            (
                "permissions:\n  contents: read\n"
                "jobs:\n  a:\n    permissions:\n      id-token: write\n"
            ),
            True,
        ),
        ("permissions: read-all\njobs: {}\n", False),
        ("permissions:\n  id-token: read\njobs: {}\n", False),
        ("permissions:\n  contents: read\njobs:\n  a:\n    permissions: {}\n", False),
        ("jobs: {}\n", False),
    ],
    ids=[
        "id-token at the workflow's level",
        "write-all at the workflow's level",
        "write-all on a job",
        "id-token on a job",
        "read-all",
        "id-token read",
        "nothing granted",
        "no permissions block",
    ],
)
def test_a_workflow_granting_the_id_token_publishes(
    tmp_path: Path, text: str, *, wanted: bool
) -> None:
    """A block granting `id-token: write`, `write-all` included, publishes.

    :param tmp_path: where the workflow is written.
    :param text: the workflow.
    :param wanted: whether it publishes.
    """
    workflow = tmp_path / "w.yml"
    workflow.write_text(text, encoding="utf-8")
    assert publishes(workflow) is wanted


def test_a_job_granting_write_all_keeps_its_ref(tmp_path: Path) -> None:
    """A job's `write-all` under a read-only workflow refuses the commit key.

    :param tmp_path: where the workflow is written.
    """
    workflow = tmp_path / "w.yml"
    workflow.write_text(
        f"on:\n{PUSHED}concurrency:\n{KEY.format(name='w', tail='')}"
        "permissions:\n  contents: read\n"
        "jobs:\n  a:\n    permissions: write-all\n",
        encoding="utf-8",
    )
    assert not keyed_as_asked(workflow, keyed())
