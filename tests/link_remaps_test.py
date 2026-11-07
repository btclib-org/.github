# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The `--remap` rules of `reusable-links.yml`, applied as lychee applies them.

The rules are read from the step's `args:`, in their order, and applied
to links written here, so nothing outside this tree is reached.
"""

from __future__ import annotations

import re
import shlex

import pytest

from . import ROOT
from .links_test import ACTION, REUSABLE
from .workflows_test import steps

# a group in a lychee replacement, which Python spells `\g<N>`
GROUP = re.compile(r"\$(\d+)")


def remaps() -> list[tuple[re.Pattern[str], str]]:
    """Read the step's `--remap` rules, in the order lychee tries them.

    :returns: each rule's pattern and its replacement in Python's form.
    """
    (step,) = [
        step
        for step in steps(ROOT / ".github" / "workflows" / REUSABLE)
        if str(step.get("uses", "")).startswith(ACTION)
    ]
    words = shlex.split(str(step["with"]["args"]))
    rules = [words[index + 1] for index, word in enumerate(words) if word == "--remap"]
    out = []
    for rule in rules:
        pattern, replacement = rule.split()
        out.append((re.compile(pattern), GROUP.sub(r"\\g<\1>", replacement)))
    return out


def remapped(url: str) -> str:
    """Rewrite a URL by the first rule that matches it.

    :param url: the URL a tree links to.
    :returns: the URL lychee asks for, the same one where no rule matches.
    """
    for pattern, replacement in remaps():
        if pattern.search(url):
            return pattern.sub(replacement, url)
    return url


OLD = "https://github.com/btclib-org/btclib-benchmarks"
NEW = "https://github.com/btclib-org/benchmarks"


# each old name `gh api repos/btclib-org/<old> --jq .full_name` answers
# with a current name, and that name
RENAMED = {
    "bitcoin-node-tests": "functional-tests",
    "btclib-benchmarks": "benchmarks",
    "btclib-bitcoin-core-rpc": "bitcoin-core-rpc",
    "btclib-ecc": "ecc",
    "btclib-functional-tests": "functional-tests",
    "btclib-libsecp256k1": "btclib-secp256k1",
    "btclib-mnemonics": "bip39-slip39",
    "btclib_node": "btclib-node",
    "claude-process": "ai-agents-process",
    "ellipticcurves": "ecc",
}


@pytest.mark.parametrize(("old", "new"), sorted(RENAMED.items()))
def test_an_old_name_issue_link_is_asked_at_the_current_name(
    old: str, new: str
) -> None:
    """An issue link under an old name is asked at the current name.

    A comment fragment is dropped, as for a current name, and any other
    fragment is kept.

    :param old: the repository's old name.
    :param new: its current name.
    """
    was = f"https://github.com/btclib-org/{old}/issues/23"
    now = f"https://github.com/btclib-org/{new}/issues/23"
    assert remapped(was) == now
    assert remapped(f"{was}#issuecomment-1") == now
    assert remapped(f"{was}#event-9") == f"{now}#event-9"


@pytest.mark.parametrize(
    ("url", "asked"),
    [
        (f"{NEW}/issues/23", f"{NEW}/issues/23"),
        (f"{NEW}/issues/23#issuecomment-1", f"{NEW}/issues/23"),
        (f"{OLD}-x/issues/1", f"{OLD}-x/issues/1"),
        (f"{OLD}/pull/2", f"{OLD}/pull/2"),
        (
            "https://github.com/other/btclib-benchmarks/issues/1",
            "https://github.com/other/btclib-benchmarks/issues/1",
        ),
        (
            "https://github.com/btclib-org/claude-process/blob/025b4721192ce245451ef2d8617a8ce8e31b1ffb/README.md#L3",
            "https://raw.githubusercontent.com/btclib-org/claude-process/025b4721192ce245451ef2d8617a8ce8e31b1ffb/README.md",
        ),
    ],
)
def test_the_rename_leaves_every_other_link_to_the_other_rules(
    url: str, asked: str
) -> None:
    """A current name, a longer name, another owner, a pull or a blob.

    :param url: the link as a tree writes it.
    :param asked: the URL lychee should ask for.
    """
    assert remapped(url) == asked
