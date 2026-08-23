# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""A backlog row on a cell the run skips is a failure, not a skip.

The one module here whose subject is this tree's own `conftest.py`
rather than the organization. A row of `tests/__init__.py`'s `BACKLOG`
excuses a failure the tracker records, as a strict expected failure, so
that a repository that catches up is reported until its name is taken
out. A repository the run skips instead -- the file the test reads gone
from the tree, its tier moved past the one the test asks -- would be
reported as neither, and the row would go on excusing a cell nobody
asks.
`conftest.py`'s `pytest_runtest_makereport` fails such a cell, and this
runs it on a suite of four tests in a temporary directory, the hook
imported from the conftest rather than copied, so that what is asked is
the hook and not a reading of it.
"""

from __future__ import annotations

import pytest


def test_a_skip_on_an_excused_cell_fails(pytester: pytest.Pytester) -> None:
    """Each phase a skip happens in, and the two neighbours it must not touch.

    A skip in the test body is a failure, and one in a fixture is an
    error, both naming the row; an expected failure that held stays the
    expected failure, and a skip on a cell no row excuses stays a skip.

    :param pytester: a pytest running in a directory of its own.
    """
    pytester.makeini("[pytest]\nmarkers = backlog\n")
    pytester.makeconftest("from tests.conftest import pytest_runtest_makereport\n")
    pytester.makepyfile(
        """
        import pytest

        excused = pytest.mark.backlog(999)
        expected = pytest.mark.xfail(strict=True, raises=AssertionError, reason="x")

        @pytest.fixture
        def unbound():
            pytest.skip("tier 3, and this asks tier 2")

        @excused
        @expected
        def test_skips_in_the_body():
            pytest.skip("no links.yml")

        @excused
        @expected
        def test_skips_in_a_fixture(unbound):
            pass

        @excused
        @expected
        def test_fails_as_expected():
            assert False

        @expected
        def test_skips_unexcused():
            pytest.skip("no links.yml")
        """
    )
    result = pytester.runpytest("-p", "no:cacheprovider")
    result.assert_outcomes(failed=1, errors=1, xfailed=1, skipped=1)
    result.stdout.fnmatch_lines(
        [
            "*excuses test_a_skip_on_an_excused_cell_fails.py::test_skips_in_a_fixture"
            " for btclib-org/.github#999*: tier 3, and this asks tier 2.*",
            "*excuses test_a_skip_on_an_excused_cell_fails.py::test_skips_in_the_body"
            " for btclib-org/.github#999*: no links.yml.*",
        ]
    )
