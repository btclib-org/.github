# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the bitcoind install of `.github/scripts`.

No run of `reusable-integration-bitcoind.yml` can show a checksum
mismatch, a redirect off `https`, or a flaky connection: the pinned
sha256 is the caller's own claim about a real release, so a run either
fetches the real archive and matches it or the release directory has
changed under everybody at once. So the network is substituted here, and
only `fetch` and `build_opener` are: `install` and `main` are otherwise
exercised as written, against a small archive this module builds itself.

The calling step captures stdout (`daemon=$(uv run ... install_bitcoind.py
...)`), so which stream carries what is part of the contract: a success
test asserts stdout is the path and nothing else, and a failure test
asserts the opposite.

The script is loaded by path, `.github/scripts` being no package, as the
other scripts under it are tested.
"""

from __future__ import annotations

import hashlib
import importlib.util
import io
import sys
import tarfile
from http.client import HTTPException, HTTPMessage
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Self
from urllib.error import HTTPError, URLError

import pytest

if TYPE_CHECKING:
    from types import ModuleType

_SCRIPT = Path(__file__).parents[1] / ".github" / "scripts" / "install_bitcoind.py"
_VERSION = "31.1"


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("install_bitcoind", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "install_bitcoind", module)
    spec.loader.exec_module(module)
    return module


def _archive(tmp_path: Path, daemon_bytes: bytes, *, extra_member: bool = True) -> Path:
    """Build a release archive the same shape as Core's own, and return it."""
    path = tmp_path / "source.tar.gz"
    with tarfile.open(path, "w:gz") as tar:
        daemon = tarfile.TarInfo(f"bitcoin-{_VERSION}/bin/bitcoind")
        daemon.size = len(daemon_bytes)
        tar.addfile(daemon, io.BytesIO(daemon_bytes))
        if extra_member:
            cli_bytes = b"not the daemon"
            cli = tarfile.TarInfo(f"bitcoin-{_VERSION}/bin/bitcoin-cli")
            cli.size = len(cli_bytes)
            tar.addfile(cli, io.BytesIO(cli_bytes))
    return path


def test_tarball_name_is_the_release_directory_own_name(script: ModuleType) -> None:
    """The name matches what bitcoincore.org actually serves."""
    assert script.tarball_name("31.1") == "bitcoin-31.1-x86_64-linux-gnu.tar.gz"


def test_verify_accepts_a_matching_digest(script: ModuleType, tmp_path: Path) -> None:
    """A digest that matches, in any case, raises nothing."""
    archive = _archive(tmp_path, b"daemon bytes")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()

    script.verify(archive, digest.upper())


def test_verify_refuses_a_mismatched_digest(script: ModuleType, tmp_path: Path) -> None:
    """A wrong digest is refused before anything is unpacked."""
    archive = _archive(tmp_path, b"daemon bytes")

    with pytest.raises(ValueError, match="sha256 mismatch"):
        script.verify(archive, "0" * 64)


def test_extract_unpacks_the_daemon_alone(script: ModuleType, tmp_path: Path) -> None:
    """The cli beside the daemon in the archive is never written out."""
    archive = _archive(tmp_path, b"daemon bytes")
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    daemon = script.extract(archive, _VERSION, dest_dir)

    assert daemon == dest_dir / f"bitcoin-{_VERSION}" / "bin" / "bitcoind"
    assert daemon.read_bytes() == b"daemon bytes"
    assert not (dest_dir / f"bitcoin-{_VERSION}" / "bin" / "bitcoin-cli").exists()


class _FlakyResponse:
    """What a `_FlakyOpener` hands back on success, read once."""

    def __init__(self, payload: bytes) -> None:
        self._payload = payload
        self._sent = False

    def __enter__(self) -> Self:
        """Answer the way `urlopen`'s own result does under `with`."""
        return self

    def __exit__(self, *exc: object) -> Literal[False]:
        """Close nothing: there is nothing real behind this response."""
        return False

    def read(self, _size: int) -> bytes:
        """Answer the whole payload once, then answer nothing."""
        if self._sent:
            return b""
        self._sent = True
        return self._payload


class _FlakyOpener:
    """An opener that fails a fixed number of attempts, then answers."""

    def __init__(self, failures: int, payload: bytes, *, reason: str = "reset") -> None:
        self.failures = failures
        self.payload = payload
        self.reason = reason
        self.attempts = 0

    def open(self, _request: object) -> _FlakyResponse:
        """Fail until `failures` attempts are behind it, then answer."""
        self.attempts += 1
        if self.attempts <= self.failures:
            raise OSError(self.reason)
        return _FlakyResponse(self.payload)


_RETRY_BOUND = 2
_EXPECTED_TWO_ATTEMPTS = 2


def test_fetch_retries_a_transient_failure_and_succeeds(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A connection reset costs an attempt, not the install."""
    opener = _FlakyOpener(failures=_RETRY_BOUND, payload=b"daemon bytes")
    monkeypatch.setattr(script, "build_opener", lambda *_args: opener)

    dest = tmp_path / "archive"
    script.fetch(_VERSION, dest)

    assert opener.attempts == _RETRY_BOUND + 1
    assert dest.read_bytes() == b"daemon bytes"


def test_fetch_gives_up_once_the_bound_is_spent(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A failure on every attempt is not swallowed forever."""
    opener = _FlakyOpener(failures=99, payload=b"unreachable")
    monkeypatch.setattr(script, "build_opener", lambda *_args: opener)

    dest = tmp_path / "archive"
    with pytest.raises(OSError, match="reset"):
        script.fetch(_VERSION, dest, retries=_RETRY_BOUND)

    assert opener.attempts == _RETRY_BOUND + 1


def test_fetch_retries_an_http_exception_too(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """An incomplete response is the other half of a flaky connection."""

    class _FlakyHTTPOpener:
        """The same shape as `_FlakyOpener`, failing with `HTTPException`."""

        def __init__(self) -> None:
            self.attempts = 0

        def open(self, _request: object) -> _FlakyResponse:
            """Fail once, then answer, exactly as a reset connection would."""
            self.attempts += 1
            if self.attempts == 1:
                reason = "truncated"
                raise HTTPException(reason)
            return _FlakyResponse(b"daemon bytes")

    opener = _FlakyHTTPOpener()
    monkeypatch.setattr(script, "build_opener", lambda *_args: opener)

    dest = tmp_path / "archive"
    script.fetch(_VERSION, dest)

    assert opener.attempts == _EXPECTED_TWO_ATTEMPTS
    assert dest.read_bytes() == b"daemon bytes"


_CLIENT_ERROR_CODE = 404


def test_fetch_does_not_retry_a_client_error(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A 404 is the server's own answer, not a connection worth retrying."""

    class _AlwaysNotFoundOpener:
        """An opener answering the same client error on every attempt."""

        def __init__(self) -> None:
            self.attempts = 0

        def open(self, _request: object) -> _FlakyResponse:
            """Answer 404, as a mistyped version would on every attempt."""
            self.attempts += 1
            url, reason = "https://example.invalid", "Not Found"
            raise HTTPError(url, _CLIENT_ERROR_CODE, reason, HTTPMessage(), None)

    opener = _AlwaysNotFoundOpener()
    monkeypatch.setattr(script, "build_opener", lambda *_args: opener)

    dest = tmp_path / "archive"
    # HTTPError wraps a response of its own and warns if garbage-collected
    # unclosed; closing it is the test double's own upkeep, not fetch's
    with pytest.raises(HTTPError) as raised:
        script.fetch(_VERSION, dest)
    raised.value.close()

    assert opener.attempts == 1


def test_install_downloads_verifies_and_unpacks(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The whole flow, with only the network substituted."""
    source = _archive(tmp_path, b"daemon bytes", extra_member=False)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    requested: list[str] = []

    def fake_fetch(version: str, dest: Path) -> None:
        """Stand in for the network: copy the prebuilt archive into place."""
        requested.append(version)
        dest.write_bytes(source.read_bytes())

    monkeypatch.setattr(script, "fetch", fake_fetch)
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    daemon = script.install(_VERSION, digest, dest_dir)

    assert requested == [_VERSION]
    assert daemon.read_bytes() == b"daemon bytes"


def test_install_refuses_before_extracting_on_a_bad_digest(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A mismatch stops the flow before the daemon is ever written out."""
    source = _archive(tmp_path, b"daemon bytes")
    monkeypatch.setattr(
        script, "fetch", lambda _version, dest: dest.write_bytes(source.read_bytes())
    )
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    with pytest.raises(ValueError, match="sha256 mismatch"):
        script.install(_VERSION, "0" * 64, dest_dir)

    assert not (dest_dir / f"bitcoin-{_VERSION}").exists()


def test_https_only_redirect_handler_refuses_a_plain_http_target(
    script: ModuleType,
) -> None:
    """The one safeguard `curl --proto-redir '=https'` gave, reproduced."""
    handler = script._HTTPSOnly()  # noqa: SLF001

    with pytest.raises(URLError, match="refusing a redirect off https"):
        handler.redirect_request(
            script.Request("https://bitcoincore.org/x"),
            io.BytesIO(),
            302,
            "Found",
            HTTPMessage(),
            "http://elsewhere.example/x",
        )


def test_main_prints_only_the_resolved_path_on_success(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Stdout is the path alone: the calling step captures it whole.

    `daemon=$(uv run ... install_bitcoind.py ...)` takes every line of
    stdout into the variable it names, so a second line there would be a
    second word the caller hands to `bitcoind` itself.
    """
    source = _archive(tmp_path, b"daemon bytes", extra_member=False)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    monkeypatch.setattr(
        script, "fetch", lambda _version, dest: dest.write_bytes(source.read_bytes())
    )

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()
    assert script.main([_VERSION, digest, "--dest", str(dest_dir)]) == 0

    daemon = dest_dir / f"bitcoin-{_VERSION}" / "bin" / "bitcoind"
    captured = capsys.readouterr()
    assert captured.out == f"{daemon.resolve()}\n"
    assert captured.err == ""


def test_main_fails_on_a_checksum_mismatch(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The command line reports the same refusal `install` raises, on stderr.

    Not stdout: the calling step's `daemon=$(...)` captures that stream,
    so a failure printed there is a message trapped in a shell variable
    nobody reads, with the run log holding neither the error nor the path.
    """
    source = _archive(tmp_path, b"daemon bytes")
    monkeypatch.setattr(
        script, "fetch", lambda _version, dest: dest.write_bytes(source.read_bytes())
    )

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()
    assert script.main([_VERSION, "0" * 64, "--dest", str(dest_dir)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "::error::sha256 mismatch" in captured.err


def test_main_fails_on_a_download_error(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A network failure is reported on stderr, never left as a traceback."""

    def failing_fetch(_version: str, _dest: Path) -> None:
        """Fail the way a download fails."""
        reason = "name resolution failed"
        raise URLError(reason)

    monkeypatch.setattr(script, "fetch", failing_fetch)

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()
    assert script.main([_VERSION, "0" * 64, "--dest", str(dest_dir)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "::error::" in captured.err
