# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""A backlog row that has stopped excusing anything, and a green run.

A row of `tests/__init__.py`'s `BACKLOG` excuses a failure the tracker
records, as a strict expected failure, so that a repository that catches
up is reported until its name is taken out. `conftest.py` refuses at
collection a row naming a test or a repository that does not exist, or
no repository at all -- one `pytester` test here asks that of it -- and
what is left to this module is the pair of ways a row stops recording
anything with the report unchanged: the cell it excuses is skipped
rather than asked, and the issue it cites is closed.

A repository the run skips -- the file the test reads gone from the
tree, its tier moved past the one the test asks -- is reported as
neither a failure nor an expected one, and the row goes on excusing a
cell nobody asks. `conftest.py`'s `pytest_runtest_makereport` fails such
a cell, and the `pytester` test here runs it on a suite of four tests in
a temporary directory, the hook imported from the conftest rather than
copied, so that what is asked is the hook and not a reading of it.

A closed issue leaves the cell excused and the record gone: nothing
changes colour, and the reason beside the expected failure points at an
issue that no longer says the gap is waiting. That question is the
tracker's, so the tests asking it carry `integration`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import BACKLOG, ORG, SELF, conftest, hooks_test, still_open

if TYPE_CHECKING:
    from collections.abc import Iterable

PRECEDENT = 367
"""A closed issue of this tracker, read as the control on the check below.

The check is an absence, and every row of `BACKLOG` cites an open
issue: a reader that told no state from another -- one answering `open`
for a 404, or for a field the API has renamed -- would pass it with
nothing measured. btclib-org/.github#367 is the issue that recorded a
row outliving its own citation, and it is closed.
"""


def settled(issues: Iterable[int]) -> list[str]:
    """Return which of these issues of this tracker the API reports closed.

    :param issues: issue numbers, as a row of `BACKLOG` carries them.
    :returns: the closed ones, sorted, qualified the way `still_open`
        reads a reference.
    """
    asked = {f"{ORG}/{SELF}#{issue}" for issue in issues}
    return sorted(reference for reference in asked if not still_open(reference))


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
            (
                "*excuses"
                " test_a_skip_on_an_excused_cell_fails.py::test_skips_in_a_fixture for"
                " btclib-org/.github#999*: tier 3, and this asks tier 2.*"
            ),
            (
                "*excuses"
                " test_a_skip_on_an_excused_cell_fails.py::test_skips_in_the_body for"
                " btclib-org/.github#999*: no links.yml.*"
            ),
        ]
    )


def test_a_row_naming_nothing_is_refused_at_collection(
    pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The three shapes the guard refuses, in one table with one it must not.

    A row whose repository tuple is empty, one naming a repository the
    API does not list and one naming a test no module asks per
    repository are refused by one run, which also carries a well-formed
    row: the message naming exactly the three is what tells the guard
    from one refusing everything or nothing. The well-formed row and the
    two bad ones over a real test name it off the function rather than
    by a string, so a rename reads as the rename and not as a fourth
    refusal.

    :param pytester: a pytest running in a directory of its own.
    :param monkeypatch: what plants the table and the names in `conftest`.
    """
    asked = hooks_test.test_the_local_hooks_run.__name__
    listed = "btclib"
    planted: tuple[tuple[int, str, tuple[str, ...]], ...] = (
        (999, asked, ()),
        (999, asked, ("nope",)),
        (999, "test_renamed_away", (listed,)),
        (999, asked, (listed,)),
    )
    monkeypatch.setenv(conftest.SWITCH, "1")
    monkeypatch.setattr(conftest, "BACKLOG", planted)
    monkeypatch.setattr(conftest, "names", lambda: [listed])
    pytester.makeini("[pytest]\n")
    pytester.makeconftest("from tests.conftest import pytest_collection_modifyitems\n")
    pytester.makepyfile("def test_anything(): pass\n")
    result = pytester.runpytest("-p", "no:cacheprovider")
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    refused = [
        f"#999: {asked} names no repository",
        f"#999: {asked} on nope",
        f"#999: test_renamed_away on {listed}",
    ]
    assert f"lists rows no test answers to: {refused}" in result.stderr.str()


@pytest.mark.integration
def test_every_backlog_row_cites_an_open_issue() -> None:
    """A row goes when its issue closes, and nothing else here says so.

    `conftest.py` refuses a row that would excuse no cell. A row whose
    issue has closed excuses its cell exactly as it did, and what has
    stopped being true is the citation: the run is green, and the
    expected failure names an issue that no longer records the gap.
    btclib-org/.github#367 states the rule and is the case that produced
    it -- a commit closed the issue a row cited while touching neither
    the row nor any other file of this suite, and a person found it.
    """
    stale = settled(issue for issue, _, _ in BACKLOG)
    assert not stale, (
        f"BACKLOG in tests/__init__.py cites issues that have closed: {stale}."
        " A row goes when its issue closes; where the gap it excuses is still"
        " there, the row cites the issue recording it now"
    )


@pytest.mark.integration
def test_a_reader_that_answered_open_for_everything_would_be_caught() -> None:
    """The check above passes on an empty answer, however it came to be one.

    It is green where every row cites an open issue and green where no
    state was read at all. Asking the same function for an issue that is
    closed is what tells the two apart.
    """
    reference = f"{ORG}/{SELF}#{PRECEDENT}"
    assert settled([PRECEDENT]) == [reference], (
        f"{reference} did not come back closed: either it was reopened, and"
        " the control needs an issue that is not, or a state is no longer"
        " being read"
    )
