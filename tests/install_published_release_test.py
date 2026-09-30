# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the pinned install of `.github/scripts`.

What a run of `pypi-install.yml` shows is the install that does not
retry: on a schedule the tag is empty, and after a release the edge a
cell reads through has usually caught up. What no run can show is a cell
whose edge is stale for as long as the deadline, or the installer failing
for a reason that is not the index's -- so the retry, the deadline, the
`::error::` and the refusal to retry anything else are reached here or
nowhere.

The installer and the clock are substituted for that. `_Installer` is a
scripted sequence of attempts that records the commands it was given,
and `_Clock` moves only when the script sleeps on it, which makes the
deadline arrive in no time at all. `run_installer` alone is exercised
against a real child process, since what it promises -- output shown
while the child still runs, standard error merged in -- is what a
substitute cannot show.

The script is loaded by path, `.github/scripts` being no package, as the
other scripts under it are tested.
"""

from __future__ import annotations

import importlib.util
import io
import sys
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import ModuleType

_SCRIPT = (
    Path(__file__).parents[1] / ".github" / "scripts" / "install_published_release.py"
)
_BUILD_FAILED = 2
_OTHER_FAILURE = 7
_ATTEMPTS_TO_RESOLVE = 3
_USAGE = 2
# one attempt before each sleep of a 15 s interval, and the one at the deadline
_ATTEMPTS_IN_60_S = 5
_PIP = ["python", "-m", "pip", "install", "--no-cache-dir"]
_UNSERVED = "ERROR: No matching distribution found for btclib-ecc==2026.9.1\n"
_UV_UNSERVED = (
    "  cause: Because there is no version of btclib-ecc==2026.9.1 and you "
    "require btclib-ecc==2026.9.1, we can conclude that your requirements "
    "are unsatisfiable.\n"
)


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


class _Installer:
    """The attempts the installer makes, in order, and the commands it got."""

    def __init__(self, attempts: list[tuple[int, str]]) -> None:
        self.attempts = attempts
        self.commands: list[list[str]] = []

    def __call__(
        self, command: list[str], emit: Callable[[str], None]
    ) -> tuple[int, str]:
        """Answer with the next scripted attempt, showing its output."""
        self.commands.append(command)
        status, output = self.attempts.pop(0) if self.attempts else (1, _UNSERVED)
        emit(output)
        return status, output


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("install_published_release", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "install_published_release", module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def clock(script: ModuleType, monkeypatch: pytest.MonkeyPatch) -> _Clock:
    """Put a clock this test moves where the script reads a real one."""
    fake = _Clock()
    monkeypatch.setattr(script, "time", fake)
    return fake


def _installer(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, attempts: list[tuple[int, str]]
) -> _Installer:
    """Put a scripted sequence of attempts where the installer would be."""
    installer = _Installer(attempts)
    monkeypatch.setattr(script, "run_installer", installer)
    return installer


def _run(script: ModuleType, *arguments: str, requirement: str = "btclib-ecc") -> int:
    """Run the script the way a cell does, installer after `--`."""
    result = script.main([requirement, *arguments])
    assert isinstance(result, int)
    return result


def test_an_empty_tag_installs_the_unpinned_requirement_once(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A run with no release behind it wants the newest, and asks once.

    The installer is scripted to fail with the unserved message, which
    a retry would answer: the single command is what shows there is none.
    """
    installer = _installer(script, monkeypatch, [(1, _UNSERVED)])

    assert _run(script, "", "--", *_PIP) == 1

    assert installer.commands == [[*_PIP, "btclib-ecc"]]
    assert clock.slept == []


def test_the_version_pinned_is_the_one_the_tag_names(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The `v` of a tag is no part of the version; extras stay in front."""
    installer = _installer(script, monkeypatch, [(0, "ok\n")])

    assert _run(script, "v2026.9.1", "--", *_PIP, requirement="btclib[secp256k1]") == 0

    assert installer.commands == [[*_PIP, "btclib[secp256k1]==2026.9.1"]]
    assert clock.slept == []


def test_an_unserved_version_is_retried_until_it_resolves(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A stale edge costs an interval or two, not the cell."""
    installer = _installer(
        script, monkeypatch, [(1, _UNSERVED), (1, _UV_UNSERVED), (0, "done\n")]
    )

    assert _run(script, "2026.9.1", "--interval", "15", "--", *_PIP) == 0

    assert len(installer.commands) == _ATTEMPTS_TO_RESOLVE
    assert clock.slept == [15.0, 15.0]
    shown = capsys.readouterr().out
    assert _UNSERVED in shown
    assert "btclib-ecc==2026.9.1 is not resolvable yet" in shown


def test_the_installer_output_is_shown_and_not_only_searched(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A failure that is not retried still shows what the installer said."""
    _installer(script, monkeypatch, [(_BUILD_FAILED, "error: build failed\n")])

    assert _run(script, "2026.9.1", "--", *_PIP) == _BUILD_FAILED

    assert "error: build failed" in capsys.readouterr().out
    assert clock.slept == []


@pytest.mark.parametrize(
    "output",
    [
        "error: build failed\n",
        "",
        # another version of the package, and another package at the version
        "ERROR: No matching distribution found for btclib-ecc==2026.9.10\n",
        "ERROR: No matching distribution found for btclib-ecc==2026.9.1.post1\n",
        "ERROR: No matching distribution found for btclib==2026.9.1\n",
        "ERROR: No matching distribution found for other-btclib-ecc==2026.9.1\n",
        # the words with no requirement after them, or a different sentence
        "ERROR: No matching distribution found for\n",
        "ERROR: Could not find a version that satisfies btclib-ecc==2026.9.1\n",
    ],
)
def test_any_other_failure_ends_at_once(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch, output: str
) -> None:
    """Waiting is for the one message the index's lag explains."""
    installer = _installer(script, monkeypatch, [(1, output)])

    assert _run(script, "2026.9.1", "--", *_PIP) == 1

    assert len(installer.commands) == 1
    assert clock.slept == []


def test_the_status_of_the_installer_is_the_status_of_the_script(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failure the script does not retry is reported as the installer's."""
    _installer(script, monkeypatch, [(1, _UNSERVED), (_OTHER_FAILURE, "boom\n")])

    assert _run(script, "2026.9.1", "--", *_PIP) == _OTHER_FAILURE
    assert clock.slept == [15.0]


@pytest.mark.parametrize(
    ("requirement", "output"),
    [
        ("btclib-ecc", _UNSERVED),
        ("btclib-ecc", _UV_UNSERVED),
        # pip drops the extras from what it echoes, uv keeps them
        (
            "btclib[secp256k1]",
            "ERROR: No matching distribution found for btclib==2026.9.1\n",
        ),
        (
            "btclib[secp256k1]",
            "no version of btclib[secp256k1]==2026.9.1 and you require\n",
        ),
        # pip echoes the name as typed, uv as the index keys it
        ("Btclib_Ecc", _UNSERVED),
        ("btclib.ecc", "No matching distribution found for btclib-ecc==2026.9.1."),
    ],
)
def test_what_the_installer_says_of_an_unserved_pin_is_recognised(
    script: ModuleType, requirement: str, output: str
) -> None:
    """Both installers' wording, with and without extras, in either spelling."""
    assert script.unresolvable(output, requirement, "2026.9.1")


def test_a_pin_that_never_resolves_is_the_deadline_speaking(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The retry ends where its deadline is, naming both possible causes."""
    installer = _installer(script, monkeypatch, [])

    assert _run(script, "2026.9.1", "--timeout", "60", "--", *_PIP) == 1

    assert clock.now == pytest.approx(60.0)
    assert len(installer.commands) == _ATTEMPTS_IN_60_S
    reported = capsys.readouterr().out
    assert "::error::btclib-ecc==2026.9.1 did not resolve within 60 s" in reported
    assert "has not served it to this runner yet" in reported
    assert "no file this cell can install" in reported


def test_the_last_pause_is_cut_to_what_is_left_of_the_deadline(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A deadline that is no multiple of the interval is still the deadline."""
    _installer(script, monkeypatch, [])

    assert (
        _run(script, "2026.9.1", "--timeout", "20", "--interval", "15", "--", *_PIP)
        == 1
    )

    assert clock.slept == [15.0, 5.0]
    assert clock.now == pytest.approx(20.0)


def test_an_attempt_outlasting_the_deadline_is_the_last_one(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An attempt that ends past the deadline is followed by the error.

    An installer bounded only by the job takes what it takes, so the
    clock can be past the deadline when it returns: what is left is
    then negative, and it ends in the annotation rather than in a
    `time.sleep` handed a negative number, which raises.
    """

    def slow(_command: list[str], emit: Callable[[str], None]) -> tuple[int, str]:
        """Fail as unserved, having spent longer than the whole budget."""
        emit(_UNSERVED)
        clock.now += 90.0
        return 1, _UNSERVED

    monkeypatch.setattr(script, "run_installer", slow)

    assert _run(script, "2026.9.1", "--timeout", "60", "--", *_PIP) == 1

    assert clock.slept == []
    assert "::error::" in capsys.readouterr().out


def test_the_defaults_are_the_budget_a_release_actually_gets(
    script: ModuleType, clock: _Clock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The workflow passes no budget, so the shipped one is what bounds it."""
    _installer(script, monkeypatch, [])

    assert _run(script, "2026.9.1", "--", *_PIP) == 1

    assert clock.now == pytest.approx(600.0)
    assert clock.slept == [15.0] * 40


@pytest.mark.parametrize("arguments", [["btclib", "v1"], ["btclib", "v1", "--"]])
def test_the_installer_command_is_required(
    script: ModuleType, arguments: list[str]
) -> None:
    """A call without an installer is a usage error, not an install."""
    with pytest.raises(SystemExit) as raised:
        script.main(arguments)

    assert raised.value.code == _USAGE


@pytest.mark.usefixtures("clock")
def test_main_reads_the_command_line_when_no_arguments_are_given(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A cell passes no `argv`: the script reads the process's own."""
    installer = _installer(script, monkeypatch, [(0, "")])
    monkeypatch.setattr(sys, "argv", ["prog", "btclib", "v1", "--", "uv", "pip"])

    assert script.main() == 0

    assert installer.commands == [["uv", "pip", "btclib==1"]]


def test_the_output_of_a_real_child_is_shown_while_it_runs(
    script: ModuleType, tmp_path: Path
) -> None:
    """A line is emitted before the child exits, and stderr is in the stream.

    The child prints a line and then waits for a file that only `emit`
    creates. Output held back until the child ends would leave it
    waiting until its own limit, and it would exit 3 rather than 0.
    """
    signal = tmp_path / "seen"
    child = textwrap.dedent(
        """
        import pathlib, sys, time
        print("first", flush=True)
        for _ in range(300):
            if pathlib.Path(sys.argv[1]).exists():
                break
            time.sleep(0.1)
        else:
            sys.exit(3)
        print("second", file=sys.stderr, flush=True)
        """
    )
    shown: list[str] = []

    def emit(line: str) -> None:
        """Record the line, and let the child go on once it has arrived."""
        shown.append(line)
        signal.write_text("seen")

    status, output = script.run_installer(
        [sys.executable, "-c", child, str(signal)], emit
    )

    assert status == 0
    assert shown == ["first\n", "second\n"]
    assert output == "first\nsecond\n"


def test_show_prints_the_line_as_it_is(
    script: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    """The installer's own newlines are kept, and none is added."""
    script.show("a\n")
    script.show("b")

    assert capsys.readouterr().out == "a\nb"


def test_a_stream_that_cannot_encode_the_output_does_not_fail_the_install(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A cp1252 stdout shows a character it lacks as `?`, and exits 0."""
    raw = io.BytesIO()
    stream = io.TextIOWrapper(raw, encoding="cp1252", write_through=True)
    monkeypatch.setattr(sys, "stdout", stream)

    def installer(_command: list[str], emit: Callable[[str], None]) -> tuple[int, str]:
        """Show one line holding a character cp1252 has no code for."""
        emit("a\ufffdb\n")
        return 0, ""

    monkeypatch.setattr(script, "run_installer", installer)

    assert script.main(["btclib", "", "--", "pip"]) == 0

    assert raw.getvalue() == b"a?b\n"


def test_the_pause_shown_is_the_pause_taken(
    script: ModuleType,
    clock: _Clock,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The last pause is cut to the deadline, and the line says so."""
    _installer(script, monkeypatch, [])

    _run(script, "2026.9.1", "--timeout", "20", "--interval", "15", "--", *_PIP)

    shown = capsys.readouterr().out
    assert "trying again in 15 s" in shown
    assert "trying again in 5 s" in shown
    assert clock.slept == [15.0, 5.0]
