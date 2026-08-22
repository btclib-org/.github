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
