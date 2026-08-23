"""The organization, and how this suite asks GitHub about it."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

ORG = "btclib-org"

SELF = ".github"
"""The organization's profile repository, and the tree this file is in.

Cloning it would fetch a second copy of what is already on the machine,
and the wrong copy: a pull request that edits the calendar has to be
checked against the calendar it proposes. The `trees` fixture maps this
name to `ROOT` instead.
"""

ROOT = Path(__file__).parents[1]


def gh(endpoint: str, jq: str) -> list[str]:
    """Ask the GitHub API and return one line of its answer per element.

    :param endpoint: the path after `gh api`, its query string included.
    :param jq: the `--jq` filter, whose output is split on newlines.
    :returns: the non-empty lines, in the order the API answered.
    """
    out = subprocess.run(
        ["gh", "api", endpoint, "--paginate", "--jq", jq],
        capture_output=True,
        check=True,
        encoding="utf-8",
    ).stdout
    return [line for line in out.splitlines() if line]


def gh_json(endpoint: str) -> Any:
    """Ask the GitHub API for one document and parse it.

    :param endpoint: the path after `gh api`.
    :returns: whatever the endpoint answers, parsed.
    """
    out = subprocess.run(
        ["gh", "api", endpoint],
        capture_output=True,
        check=True,
        encoding="utf-8",
    ).stdout
    return json.loads(out)


def by_hand(repository: str, command: str) -> str:
    """Say how a failure is decided without this suite.

    Section 15 gives every question of the standard as a command a
    person runs in one checkout, and a failure here names that command
    so the reader can take it there: the message is the section's line
    for that repository rather than a restatement of it.

    :param repository: the repository the assertion was asked of.
    :param command: the shell that decides it in a checkout of that tree.
    :returns: the text an assertion message ends with.
    """
    return f"by hand, in a checkout of {ORG}/{repository}: {command}"


def tracked(root: Path, *patterns: str) -> list[str]:
    """List the files a tree tracks under some pathspecs.

    `git ls-files` rather than a walk, so a checkout's own environment
    -- the `.venv` this tree keeps beside its suite -- is not read as
    part of it.

    :param root: the root of the checkout.
    :param patterns: git pathspecs, `*.toml` and the like.
    :returns: the paths, relative to the root, in git's order.
    """
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--", *patterns],
        capture_output=True,
        check=True,
        encoding="utf-8",
    ).stdout
    return out.splitlines()
