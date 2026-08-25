# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 7's layout, read off the tree rather than off the hook.

The hook is section 4's and `hooks_test.py` asks whether it runs; this
asks whether the tree keeps the rule the hook would enforce, which is
the half a gate that is not installed cannot answer for.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import Tier, by_hand

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

EXEMPT = ("__init__.py", "conftest.py")
"""The two names `name-tests-test` passes over at any setting.

The package file and pytest's own, neither of which is a test module
and both of which section 7 puts under `tests/`.
"""


@pytest.mark.tier(Tier.PYTHON)
def test_every_test_file_is_named_so_pytest_collects_it(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 7: `*_test.py`, which is what `name-tests-test` enforces.

    Every `.py` under `tests/` but the two exempt names, which is the
    hook's own reading of the rule: a helper module goes in the package
    `__init__.py` by section 7's next bullet, so a module named any
    other way is what the hook refuses -- a test spelled some other way,
    or shared code in the wrong file.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    if not (root / "tests").is_dir():
        pytest.skip(f"{repository} has no tests/ directory")
    wrong = sorted(
        str(path.relative_to(root))
        for path in (root / "tests").rglob("*.py")
        if path.name not in EXEMPT and not path.name.endswith("_test.py")
    )
    assert not wrong, f"files under tests/ not named *_test.py: {wrong}; " + by_hand(
        repository,
        "git ls-files 'tests/**.py' | grep -vE '(_test|/__init__|/conftest)\\.py$'",
    )
