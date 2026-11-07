# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What bounds the mention job of `reusable-claude-review.yml`.

The job runs in tag mode, whose own allow list no argument removes, so
its bound is `--tools`, `--restricted` and its deny list. An edit to any
of them reaches no run until somebody mentions the bot, so these tests
are what turns red first (btclib-org/.github#1833).

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


def values(flag: str) -> list[list[str]]:
    """Collect what each occurrence of a flag names.

    A value is the text after `=`, or else every argument after the flag
    up to the next one starting `--`, each split on commas.

    :param flag: the flag, with its leading `--`.
    :returns: the names, one list per occurrence.
    """
    args = arguments()
    found: list[list[str]] = []
    for index, arg in enumerate(args):
        name, equals, value = arg.partition("=")
        if name != flag:
            continue
        given = [value] if equals else []
        if not equals:
            for following in args[index + 1 :]:
                if following.startswith("--"):
                    break
                given.append(following)
        found.append([tool.strip() for text in given for tool in text.split(",")])
    return found


def test_tools_names_tool_search_alone() -> None:
    """`--tools` is passed once, and names ToolSearch and nothing else.

    It withholds every built-in tool it does not name, so another name
    would offer one to an answer (btclib-org/.github#2114).
    """
    assert values("--tools") == [["ToolSearch"]]


def test_restricted_is_passed_as_a_flag() -> None:
    """`--restricted` is followed by another flag or by nothing.

    The action reads an argument after any flag as that flag's value
    unless it starts `--`, so a word after `--restricted` would be taken
    as one.
    """
    args = arguments()
    after = args[args.index("--restricted") + 1 :]
    assert not after or after[0].startswith("--")


def test_the_file_operation_tools_are_denied_by_name() -> None:
    """`--tools` keeps every MCP tool, so the deny list names these."""
    denied = {tool for found in values("--disallowedTools") for tool in found}
    assert denied >= {
        "mcp__github_file_ops__commit_files",
        "mcp__github_file_ops__delete_files",
    }
