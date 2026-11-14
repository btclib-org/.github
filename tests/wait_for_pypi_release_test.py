# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the release wait of `.github/scripts`.

A run of `pypi-install.yml` shows the answer the index gives that day:
whether it serves a release's version, or, on a schedule and on a
dispatch, whose tag is empty, whether it has the project. What is waited
on is somebody else's upload and somebody else's index, which neither a
release nor a rehearsal can arrange to be late or down, so the retry,
the deadline and the `::error::` of either question are reached here or
nowhere.

Both of the wait's inputs are substituted for that. `_Transport` is the
index asked for a version, and `_Project` the index asked for the
project: each a scripted sequence of answers that also records what it
was asked, timeout included. `_Clock` is the clock, and it moves only
when the script sleeps on it, which is what makes the deadline arrive in
no time at all and the attempts before it exact rather than
approximate.

The script is loaded by path, `.github/scripts` being no package, as the
other scripts under it are tested.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from contextlib import closing, contextmanager
from email.message import Message
from http import HTTPStatus
from http.client import IncompleteRead
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.error import HTTPError

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator
    from contextlib import AbstractContextManager
    from types import ModuleType

_SCRIPT = Path(__file__).parents[1] / ".github" / "scripts" / "wait_for_pypi_release.py"
_URL = "https://pypi.org/simple/btclib/"
# a 300 s deadline at the shipped interval: the script asks once
# before each sleep, and the last sleep is cut to what is left
_ASKED_IN_300_S = 20


class _Clock:
    """A monotonic clock that stands still until the script sleeps on it."""

    def __init__(self) -> None:
        self.now = 0.0
        self.slept: list[float] = []

    def monotonic(self) -> float:
        """Return the reading, which only `sleep` below moves."""
        return self.now

    def sleep(self, seconds: float) -> None:
        """Spend the seconds a wait on a real clock would have spent."""
        self.slept.append(seconds)
        self.now += seconds


class _Transport:
    """The answers the index gives, in order, and the questions it got."""

    def __init__(self, answers: list[bool]) -> None:
        self.answers = answers
        self.asked: list[tuple[str, float]] = []

    def __call__(self, url: str, version: str, timeout: float) -> bool:
        """Answer the next verdict in the script, and record the question."""
        assert version == "2026.9.1"
        self.asked.append((url, timeout))
        return self.answers.pop(0) if self.answers else False


class _Answer(io.BytesIO):
    """What `served` reads of a response: its status and its body."""

    status: int = HTTPStatus.OK


@contextmanager
def _answering(body: object = None, status: int = HTTPStatus.OK) -> Iterator[_Answer]:
    """Hand out a response the way `urlopen` hands one to a `with`."""
    answer = _Answer(body if isinstance(body, bytes) else json.dumps(body).encode())
    answer.status = status
    yield answer


def _page(*filenames: str) -> dict[str, object]:
    """Return a simple-index page listing these files, as PEP 691 has it."""
    return {
        "meta": {"api-version": "1.4"},
        "name": "btclib",
        "files": [{"filename": name, "yanked": False} for name in filenames],
    }


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("wait_for_pypi_release", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "wait_for_pypi_release", module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def clock(script: ModuleType, monkeypatch: pytest.MonkeyPatch) -> _Clock:
    """Put a clock this test moves where the script reads a real one."""
    fake = _Clock()
    monkeypatch.setattr(script, "time", fake)
    return fake


def _index(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, answers: list[bool]
) -> _Transport:
    """Put a scripted sequence of answers where the index would be."""
    transport = _Transport(answers)
    monkeypatch.setattr(script, "served", transport)
    return transport


class _Project:
    """Whether the index has the project, in order, and what it was asked."""

    def __init__(self, answers: list[bool | None]) -> None:
        self.answers = answers
        self.asked: list[tuple[str, float]] = []

    def __call__(self, url: str, timeout: float) -> bool | None:
        """Answer the next verdict in the script, and record the question."""
        self.asked.append((url, timeout))
        return self.answers.pop(0) if self.answers else None


def _project(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, answers: list[bool | None]
) -> _Project:
    """Put a scripted sequence of answers where the project question goes."""
    project = _Project(answers)
    monkeypatch.setattr(script, "known", project)
    return project


@pytest.mark.usefixtures("clock")
def test_an_empty_tag_asks_for_the_project_not_a_version(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """A run with no release behind it asks for no version, only the project.

    `clock` is asked for through `usefixtures` although nothing here
    should sleep, and that is the point: without it a regressed guard
    falls through to the real `time.sleep` and the suite sits for the
    whole default budget before reporting anything, where the fake turns
    the same regression into an immediate failure.
    """
    index = _index(script, monkeypatch, [])
    project = _project(script, monkeypatch, [True])
    output = tmp_path / "output"

    assert script.main(["btclib", "", "--output", str(output)]) == 0

    assert index.asked == []
    assert project.asked == [(_URL, 10.0)]
    assert output.read_text() == "published=true\n"
    assert "asking whether the index has btclib" in capsys.readouterr().out


@pytest.mark.usefixtures("clock")
def test_a_bare_v_is_refused_rather_than_read_as_no_tag(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """A tag naming no version asks the index nothing and writes nothing."""
    index = _index(script, monkeypatch, [])
    project = _project(script, monkeypatch, [False])
    output = tmp_path / "output"

    assert script.main(["coin-addresses", "v", "--output", str(output)]) == 1

    assert index.asked == []
    assert project.asked == []
    assert not output.exists()
    assert "::error::the tag 'v' names no version" in capsys.readouterr().out


@pytest.mark.usefixtures("clock")
def test_a_project_the_index_never_had_is_not_published(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """The one answer that skips the matrix, and the run still passes."""
    _project(script, monkeypatch, [False])
    output = tmp_path / "output"

    assert script.main(["coin-addresses", "", "--output", str(output)]) == 0

    assert output.read_text() == "published=false\n"
    assert "the index has no project coin-addresses" in capsys.readouterr().out


def test_an_index_that_never_says_fails_the_run(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """An index that is down is asked until the deadline, then fails.

    No output is written, so the matrix runs if the job is ever read as
    passing: a silent index never reads as a package never published.
    """
    project = _project(script, monkeypatch, [])
    output = tmp_path / "output"

    assert script.main(["btclib", "", "--output", str(output)]) == 1

    assert clock.now == pytest.approx(300.0)
    assert len(project.asked) == _ASKED_IN_300_S
    assert not output.exists()
    reported = capsys.readouterr().out
    assert "::error::the index did not say within 300 s whether it has btclib" in (
        reported
    )


def test_an_index_that_answers_late_is_waited_for(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """An unanswered question costs an interval, not the run."""
    _project(script, monkeypatch, [None, None, False])
    output = tmp_path / "output"

    assert script.main(["coin-addresses", "", "--output", str(output)]) == 0

    assert clock.slept == [15.0, 15.0]
    assert output.read_text() == "published=false\n"


def test_a_tagged_run_writes_no_output(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A release's run never reads as a package never published.

    The callers skip the matrix on `published=false` alone, and a
    release's post-publish check that skipped would read as one that
    passed.
    """
    _index(script, monkeypatch, [True])
    project = _project(script, monkeypatch, [False])
    output = tmp_path / "output"

    assert script.main(["coin-addresses", "v2026.9.1", "--output", str(output)]) == 0

    assert project.asked == []
    assert not output.exists()


def test_the_version_asked_for_is_the_one_the_tag_names(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The `v` of a tag is no part of the version the index serves."""
    index = _index(script, monkeypatch, [True])

    assert script.main(["btclib", "v2026.9.1"]) == 0

    assert index.asked == [(_URL, 10.0)]
    assert clock.slept == []
    assert "the index serves 2026.9.1" in capsys.readouterr().out


def test_a_version_not_served_yet_is_waited_for(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An index that has not caught up yet costs an interval, not the run."""
    index = _index(script, monkeypatch, [False, False, True])

    assert script.main(["btclib", "2026.9.1", "--interval", "15"]) == 0

    assert [url for url, _ in index.asked] == [_URL, _URL, _URL]
    assert clock.slept == [15.0, 15.0]
    assert "the index serves 2026.9.1 after 30 s" in capsys.readouterr().out


def test_a_version_that_never_arrives_is_the_deadline_speaking(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The wait ends where its deadline is, and names what never came."""
    index = _index(script, monkeypatch, [])

    assert script.main(["btclib", "2026.9.1", "--timeout", "300"]) == 1

    assert clock.now == pytest.approx(300.0)
    assert len(index.asked) == _ASKED_IN_300_S
    reported = capsys.readouterr().out
    assert "::error::2026.9.1 is not on the index 300 s later" in reported


def test_the_last_wait_is_cut_to_what_is_left_of_the_deadline(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A deadline that is no multiple of the interval is still the deadline."""
    index = _index(script, monkeypatch, [])

    assert (
        script.main(["btclib", "2026.9.1", "--timeout", "20", "--interval", "15"]) == 1
    )

    assert clock.slept == [15.0, 5.0]
    assert clock.now == pytest.approx(20.0)
    assert [timeout for _, timeout in index.asked] == [10.0, 5.0]


def test_a_request_outlasting_the_deadline_leaves_no_negative_sleep(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A request that overruns its share still ends in the annotation.

    `served` is bounded by a socket timeout, which applies per blocking
    read, so an index answering a byte at a time can return after the
    deadline has already passed. What is left is then negative, and the
    clamp is what keeps `time.sleep` from being handed it -- a real one
    raises on a negative number, which would replace the `::error::`
    this exists to print with a traceback.
    """
    asked: list[tuple[str, float]] = []

    def slow(url: str, _version: str, timeout: float) -> bool:
        """Answer no, having spent longer than the whole budget."""
        asked.append((url, timeout))
        clock.now += 40.0
        return False

    monkeypatch.setattr(script, "served", slow)

    assert script.main(["btclib", "2026.9.1", "--timeout", "30"]) == 1

    assert asked == [(_URL, 10.0)]
    assert clock.slept == [0.0]
    assert "::error::2026.9.1 is not on the index 30 s later" in capsys.readouterr().out


def test_the_defaults_are_the_budget_a_release_actually_gets(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The workflow passes no budget, so the shipped one is what bounds it.

    `DEFAULT_TIMEOUT` is the figure the job's `timeout-minutes` is set
    above. This is the run the workflow makes with a tag;
    `test_an_index_that_never_says_fails_the_run` is the one it makes
    without, under the same deadline.
    """
    index = _index(script, monkeypatch, [])

    assert script.main(["btclib", "2026.9.1"]) == 1

    assert clock.now == pytest.approx(300.0)
    assert clock.slept == [15.0] * 20
    assert [timeout for _, timeout in index.asked] == [10.0] * 20


def _urlopen(
    monkeypatch: pytest.MonkeyPatch, script: ModuleType, page: object
) -> list[tuple[str, dict[str, str], float]]:
    """Serve this page, and record what urlopen was asked, header included."""
    asked: list[tuple[str, dict[str, str], float]] = []

    def urlopen(request: object, *, timeout: float) -> AbstractContextManager[_Answer]:
        """Answer as the index does with the page it holds."""
        asked.append(
            (
                request.full_url,  # type: ignore[attr-defined]
                dict(request.header_items()),  # type: ignore[attr-defined]
                timeout,
            )
        )
        return _answering(page)

    monkeypatch.setattr(script, "urlopen", urlopen)
    return asked


def test_the_page_is_asked_for_in_its_json_form(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The header is pip's, whole: the index varies its answer on it."""
    asked = _urlopen(monkeypatch, script, _page("btclib-2026.9.1.tar.gz"))

    assert script.served(_URL, "2026.9.1", 10.0)
    assert asked == [
        (
            _URL,
            {
                "Accept": "application/vnd.pypi.simple.v1+json, "
                "application/vnd.pypi.simple.v1+html; q=0.1, text/html; q=0.01"
            },
            10.0,
        )
    ]


@pytest.mark.parametrize(
    "filename",
    [
        "btclib-2026.9.1.tar.gz",
        "btclib-2026.9.1-py3-none-any.whl",
        "btclib_ecc-2026.9.1-cp311-cp311-manylinux_2_28_x86_64.whl",
        "btclib-2026.9.1.zip",
    ],
)
def test_a_file_of_the_version_is_the_version_served(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, filename: str
) -> None:
    """Any distribution of the version lists it, wheel or sdist."""
    _urlopen(monkeypatch, script, _page("btclib-2026.9.0.tar.gz", filename))

    assert script.served(_URL, "2026.9.1", 10.0)


@pytest.mark.parametrize(
    "filenames",
    [
        [],
        ["btclib-2026.9.0.tar.gz", "btclib-2026.9.0-py3-none-any.whl"],
        ["btclib-2026.9.10.tar.gz", "btclib-12026.9.1.tar.gz"],
        ["btclib-2026.9.1.tar.gz.asc", "notes.txt", "btclib.whl"],
    ],
)
def test_a_page_without_a_file_of_the_version_is_not_serving_it(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, filenames: list[str]
) -> None:
    """The project's page answering 200 is not the version being on it.

    The older versions, and the one whose text merely begins with this
    one's, are what a page holds in the interval this waits out.
    """
    _urlopen(monkeypatch, script, _page(*filenames))

    assert not script.served(_URL, "2026.9.1", 10.0)


@pytest.mark.parametrize("page", [[], {"files": None}, {"files": [1, "x"]}, {}])
def test_a_document_of_another_shape_is_not_serving_the_version(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, page: object
) -> None:
    """Whatever the index answers that is not a page is one more wait."""
    _urlopen(monkeypatch, script, page)

    assert not script.served(_URL, "2026.9.1", 10.0)


def test_a_body_that_is_not_json_is_not_serving_the_version(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An index that ignores the header answers HTML, and that is a wait."""
    monkeypatch.setattr(
        script,
        "urlopen",
        lambda *_args, **_kwargs: _answering(b"<!DOCTYPE html><html>"),
    )

    assert not script.served(_URL, "2026.9.1", 10.0)


def test_a_2xx_that_is_not_ok_is_not_the_index_serving_it(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`served` compares the status rather than that a status arrived."""
    monkeypatch.setattr(
        script,
        "urlopen",
        lambda *_args, **_kwargs: _answering(
            _page("btclib-2026.9.1.tar.gz"), HTTPStatus.NO_CONTENT
        ),
    )

    assert not script.served(_URL, "2026.9.1", 10.0)


def test_a_404_is_not_the_index_serving_the_version(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A 404 for a project the index does not hold is one more wait.

    `closing` is what keeps the failure from ending the run somewhere
    else: `HTTPError` is a response as well as an exception, and inherits
    `tempfile._TemporaryFileWrapper` through `urllib.response.addbase`,
    so one collected without being closed raises `ResourceWarning` --
    which this suite turns into an error, against whichever test happens
    to be running when the collector reaches it.
    """
    failure = HTTPError(_URL, HTTPStatus.NOT_FOUND, "Not Found", Message(), None)

    def urlopen(*_args: object, **_kwargs: object) -> AbstractContextManager[_Answer]:
        """Fail the way the index fails for a project it does not hold."""
        raise failure

    monkeypatch.setattr(script, "urlopen", urlopen)

    with closing(failure):
        assert not script.served(_URL, "2026.9.1", 10.0)


@pytest.mark.parametrize(
    "failure",
    [
        TimeoutError("timed out"),
        ConnectionResetError("reset by peer"),
        IncompleteRead(b"{"),
    ],
)
def test_an_index_that_does_not_answer_is_not_serving_the_version(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, failure: Exception
) -> None:
    """Every way the exchange can fail is one more reason to keep waiting."""

    def urlopen(*_args: object, **_kwargs: object) -> AbstractContextManager[_Answer]:
        """Fail the way the index fails while the upload is still landing."""
        raise failure

    monkeypatch.setattr(script, "urlopen", urlopen)

    assert not script.served(_URL, "2026.9.1", 10.0)


@pytest.mark.parametrize(
    ("package", "url"),
    [
        ("btclib", "https://pypi.org/simple/btclib/"),
        ("btclib-ecc", "https://pypi.org/simple/btclib-ecc/"),
        ("Btclib_Ecc", "https://pypi.org/simple/btclib-ecc/"),
        ("btclib.ecc", "https://pypi.org/simple/btclib-ecc/"),
        ("btclib-.-_ecc", "https://pypi.org/simple/btclib-ecc/"),
    ],
)
def test_the_package_is_keyed_the_way_the_index_keys_it(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    package: str,
    url: str,
) -> None:
    """PEP 503's normalization, so the request needs no redirect."""
    index = _index(script, monkeypatch, [True])

    assert script.main([package, "v2026.9.1"]) == 0

    assert index.asked == [(url, 10.0)]
    assert clock.slept == []


def test_a_page_of_the_project_is_the_project_known(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A 200 for the project's page is a yes, whatever it lists."""
    asked = _urlopen(monkeypatch, script, _page())

    assert script.known(_URL, 10.0) is True
    assert [url for url, _, _ in asked] == [_URL]


def test_a_2xx_that_is_not_ok_says_nothing_of_the_project(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`known` compares the status rather than that a status arrived."""
    monkeypatch.setattr(
        script,
        "urlopen",
        lambda *_args, **_kwargs: _answering(_page(), HTTPStatus.NO_CONTENT),
    )

    assert script.known(_URL, 10.0) is None


def _failing(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, status: HTTPStatus
) -> HTTPError:
    """Have the index answer every request with this status."""
    failure = HTTPError(_URL, status, status.phrase, Message(), None)

    def urlopen(*_args: object, **_kwargs: object) -> AbstractContextManager[_Answer]:
        """Fail with this status."""
        raise failure

    monkeypatch.setattr(script, "urlopen", urlopen)
    return failure


def test_a_404_says_the_index_never_had_the_project(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The one answer read as a no."""
    with closing(_failing(script, monkeypatch, HTTPStatus.NOT_FOUND)):
        assert script.known(_URL, 10.0) is False


@pytest.mark.parametrize(
    "status",
    [
        HTTPStatus.GONE,
        HTTPStatus.INTERNAL_SERVER_ERROR,
        HTTPStatus.SERVICE_UNAVAILABLE,
    ],
)
def test_any_other_failure_says_nothing_of_the_project(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, status: HTTPStatus
) -> None:
    """A failing index is no answer, and never reads as a project it lacks."""
    with closing(_failing(script, monkeypatch, status)):
        assert script.known(_URL, 10.0) is None


@pytest.mark.parametrize(
    "failure",
    [
        TimeoutError("timed out"),
        ConnectionRefusedError("refused"),
        IncompleteRead(b"{"),
    ],
)
def test_an_index_that_does_not_answer_says_nothing_of_the_project(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, failure: Exception
) -> None:
    """An index that is down never reads as a project it never had."""

    def urlopen(*_args: object, **_kwargs: object) -> AbstractContextManager[_Answer]:
        """Fail the way an index that is down fails."""
        raise failure

    monkeypatch.setattr(script, "urlopen", urlopen)

    assert script.known(_URL, 10.0) is None
