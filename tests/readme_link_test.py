# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 4's `readme-absolute-link`, read off this tree's own gate.

The hook is `local-link-prefix` with `./` and `../` no longer admitted,
over the one file that hook excludes, so the two are read together: a
pattern edited in one and not the other refuses in one file what it
admits in all the rest. The pattern is then asked the shapes it refuses
and the ones it admits, compiled as pygrep compiles it.
"""

from __future__ import annotations

import re
from typing import Any

import pytest
import yaml

from . import ROOT

PREFIX = "local-link-prefix"
README = "readme-absolute-link"

ADMITTED = r"\.\.?/|"
"""The alternative of `PREFIX`'s lookahead that `README` drops."""

ROOT_README = r"^README\.md$"
"""The file `README` reads and `PREFIX` excludes."""


def local() -> dict[str, dict[str, Any]]:
    """Read the hooks of this tree's `local` blocks, by id.

    :returns: each hook's mapping.
    """
    config = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text("utf-8"))
    return {
        hook["id"]: hook
        for block in config["repos"]
        if block["repo"] == "local"
        for hook in block["hooks"]
    }


def test_the_readme_hook_is_the_prefix_hook_over_the_readme() -> None:
    """The two entries differ by the prefixes alone, and split the files."""
    hooks = local()
    prefix, readme = hooks[PREFIX], hooks[README]
    assert ADMITTED in prefix["entry"]
    assert readme["entry"] == prefix["entry"].replace(ADMITTED, "", 1)
    assert prefix["exclude"] == readme["files"] == ROOT_README
    assert prefix["types"] == readme["types"] == ["markdown"]


@pytest.mark.parametrize(
    ("line", "refused"),
    [
        pytest.param("[a](./CONTRIBUTING.md)", True, id="dot"),
        pytest.param("[a](../x/y.md#z)", True, id="dot-dot"),
        pytest.param("[a](SECURITY.md)", True, id="bare"),
        pytest.param("![a](./logo.svg)", True, id="image"),
        pytest.param("[a]: ./RELEASING.md", True, id="definition"),
        pytest.param("[a](https://github.com/o/r/blob/main/x.md)", False, id="url"),
        pytest.param("[a](#a-heading)", False, id="anchor"),
        pytest.param("`[a](./x.md)`", False, id="code"),
    ],
)
def test_the_readme_pattern_refuses_every_local_destination(
    line: str,
    refused: bool,  # noqa: FBT001
) -> None:
    """A local destination is refused, prefixed or not; a URL is not.

    :param line: a line of a `README.md`.
    :param refused: whether the hook reports it.
    """
    pattern = re.compile(local()[README]["entry"])
    assert (pattern.search(line) is not None) is refused
