# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 10's rule that macOS is supported on arm64 alone.

A workflow names its runner as a string: in `runs-on:`, in a matrix
list, or inside the JSON a caller passes to a reusable workflow. Every
string value of the parsed document is read, so a comment naming an
image is not a finding.

GitHub's x86_64 macOS labels end in `-intel` or `-large`; `-xlarge` is
arm64. The table in actions/runner-images's `README.md` gives them.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import by_hand
from .workflows_test import gated

if TYPE_CHECKING:
    from pathlib import Path

# an x86_64 macOS runner label, such as `macos-26-intel`
X86_64 = re.compile(r"\bmacos-(?:\d+|latest)-(?:intel|large)\b")

# the same question in a checkout; it also prints comments
BY_HAND = r"git grep -nE 'macos-([0-9]+|latest)-(intel|large)' -- .github/workflows"


def images(node: Any) -> list[str]:  # noqa: ANN401
    """Return the x86_64 macOS labels a parsed document's strings name.

    :param node: a parsed YAML document, or any part of one.
    :returns: each label, in the order of the document.
    """
    if isinstance(node, str):
        return X86_64.findall(node)
    if isinstance(node, dict):
        return [label for value in node.values() for label in images(value)]
    if isinstance(node, list):
        return [label for value in node for label in images(value)]
    return []


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("runs-on: macos-26-intel\n", ["macos-26-intel"]),
        ("os: [ubuntu-latest, macos-15-intel]\n", ["macos-15-intel"]),
        (
            'with:\n  runners: \'["macos-26-large", "macos-latest"]\'\n',
            ["macos-26-large"],
        ),
        ("runs-on: macos-latest-large\n", ["macos-latest-large"]),
        ("os: [macos-latest, macos-26, macos-26-xlarge]\n", []),
        ("# macos-26-intel is gone\nruns-on: macos-latest\n", []),
    ],
)
def test_images_finds_an_x86_64_label_and_nothing_else(
    source: str, expected: list[str]
) -> None:
    """An `-intel` or `-large` label is found; arm64 and a comment are not.

    :param source: a planted workflow.
    :param expected: the labels owed.
    """
    assert images(yaml.safe_load(source)) == expected


@pytest.mark.integration
def test_no_workflow_runs_on_an_x86_64_macos_image(
    repository: str, trees: dict[str, Path]
) -> None:
    """Section 10: no workflow names an x86_64 macOS runner.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    found = [
        f"{workflow.name}: {label}"
        for workflow in gated(repository, trees)
        for label in images(yaml.safe_load(workflow.read_text(encoding="utf-8")))
    ]
    assert not found, (
        f"{found} run on x86_64 macOS, which section 10 refuses: macOS is"
        " supported on arm64 alone; " + by_hand(repository, BY_HAND)
    )
