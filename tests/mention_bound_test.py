# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What bounds the mention job of `reusable-claude-review.yml`.

The job runs in tag mode, whose own allow list no argument removes, so
its bound is `--restricted` and its deny list. An edit to either reaches
no run until somebody mentions the bot, so these tests are what turns
red first (btclib-org/.github#1833).

The action reads `claude_args` with shell-quote
(`parseClaudeArgsToExtraArgs` in its `base-action/src/parse-sdk-options.ts`),
and `shlex.split` splits these arguments as shell-quote does: they hold
none of the shell operators, globs or comment lines the action handles
on its own.
"""

from __future__ import annotations

import shlex

from . import ROOT
from .workflows_test import jobs

# the reusable review, which holds the mention job
WORKFLOW = ROOT / ".github/workflows/reusable-claude-review.yml"


def arguments() -> list[str]:
    """Split the mention job's `claude_args` into its arguments.

    :returns: the arguments, in order.
    """
    (step,) = (
        step
        for step in jobs(WORKFLOW)["mention"]["steps"]
        if step.get("uses", "").startswith("anthropics/claude-code-action@")
    )
    return shlex.split(step["with"]["claude_args"])


def denied() -> set[str]:
    """Collect the tools the mention job's `--disallowedTools` names.

    The action takes every argument after the flag up to the next one
    starting `--`, and splits each on commas.

    :returns: the tool names.
    """
    args = arguments()
    start = args.index("--disallowedTools") + 1
    values: list[str] = []
    for arg in args[start:]:
        if arg.startswith("--"):
            break
        values.append(arg)
    return {tool.strip() for value in values for tool in value.split(",")}


def test_restricted_is_passed_as_a_flag() -> None:
    """`--restricted` is followed by another flag or by nothing.

    The action reads an argument after any flag as that flag's value
    unless it starts `--`, so a word after `--restricted` would be taken
    as one.
    """
    args = arguments()
    after = args[args.index("--restricted") + 1 :]
    assert not after or after[0].startswith("--")


def test_no_tool_is_kept_out_of_the_restricted_mode() -> None:
    """No `--tools`: the CLI leaves a tool it names out of what is denied."""
    assert not [arg for arg in arguments() if arg.split("=")[0] == "--tools"]


def test_sub_agents_are_denied_by_name() -> None:
    """Agent and Skill are not marked `enablesCodeExecution` on 2.1.309.

    So `--restricted` does not deny them, and the deny list has to.
    Workflow is named for the same reason it is denied, the sub-agents
    it starts (btclib-org/.github#1809).
    """
    assert {"Agent", "Skill", "Workflow"} <= denied()
