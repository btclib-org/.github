# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Install the Bitcoin Core release `reusable-integration-bitcoind.yml` needs.

Download the release archive over `https` and nothing it redirects to,
compare its sha256 against the one the caller pinned before anything is
opened, and unpack the daemon alone -- the tarball also carries the cli,
the wallet tool and the gui's libraries, and the tests speak rpc.

Every line this prints on success is the daemon's own resolved path, and
nothing else: the calling step captures stdout with
`daemon=$(uv run ... install_bitcoind.py ...)`, so a second line there is
a second word in a shell variable a caller then hands to `bitcoind`
itself. A failure is reported on stderr instead, precisely because that
capture is in play -- stdout captured under `bash -e` on a failing
command leaves the error trapped in the unused variable and the log
empty. `tests/install_bitcoind_test.py` asserts success writes only the
path to stdout and nothing to stderr, and a failure the reverse.

`fetch` is the one function `tests/install_bitcoind_test.py` substitutes
for a test of `install` or `main`; a direct test of `fetch` itself
substitutes `build_opener` instead, to drive its own retry.

    uv run --no-project --python 3.15 \
        .github/scripts/install_bitcoind.py "$VERSION" "$SHA256"
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import tarfile
from http.client import HTTPException
from pathlib import Path
from typing import TYPE_CHECKING, override
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

if TYPE_CHECKING:
    from http.client import HTTPMessage
    from typing import IO
    from urllib.request import OpenerDirector

# the release archives, one directory per version, the caller's own claim
# about the node it tests against and never something this file could pin
BASE_URL = "https://bitcoincore.org/bin"
# large enough that a run reads the archive in a handful of chunks rather
# than a byte at a time, small enough that neither the download nor the
# digest holds more than this much of it in memory at once
CHUNK_SIZE = 1 << 20
# bounded retries on a failed download attempt, so a reset connection
# costs one more attempt rather than the job. No delay between attempts:
# a fixed count is what a test drives without a clock to mock
RETRIES = 3
# the boundary below which a status is a client error -- the server's own
# answer, and not a connection worth retrying
SERVER_ERROR_FLOOR = 500


class _HTTPSOnly(HTTPRedirectHandler):
    """Refuse a redirect that would leave `https`.

    `urlopen` follows a redirect wherever the server points it unless
    told otherwise; refusing it here, once, is what stands in for
    `curl --proto '=https' --proto-redir '=https'`.
    """

    @override
    def redirect_request(
        self,
        req: Request,
        fp: IO[bytes],
        code: int,
        msg: str,
        headers: HTTPMessage,
        newurl: str,
    ) -> Request | None:
        """Refuse the redirect outright where its target is not `https`."""
        if not newurl.startswith("https://"):
            reason = f"refusing a redirect off https: {newurl}"
            raise URLError(reason)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def tarball_name(version: str) -> str:
    """Return the release archive's own file name."""
    return f"bitcoin-{version}-x86_64-linux-gnu.tar.gz"


def _download_once(opener: OpenerDirector, request: Request, dest: Path) -> None:
    """Make one attempt at the whole download, no retry of its own."""
    with opener.open(request) as response, dest.open("wb") as archive:
        while chunk := response.read(CHUNK_SIZE):
            archive.write(chunk)


def fetch(version: str, dest: Path, retries: int = RETRIES) -> None:
    """Download the release archive to `dest`, retrying a failed attempt.

    An `HTTPError` below 500 -- a 404 on a mistyped version, for one -- is
    the server's own answer rather than a transient failure, so it is
    raised on the first attempt instead of spending the retries on it.
    """
    url = f"{BASE_URL}/bitcoin-core-{version}/{tarball_name(version)}"
    opener = build_opener(_HTTPSOnly)
    request = Request(url, method="GET")  # noqa: S310
    for attempt in range(retries + 1):
        try:
            _download_once(opener, request, dest)
        except HTTPError as error:
            if error.code < SERVER_ERROR_FLOOR or attempt == retries:
                raise
        except OSError:
            if attempt == retries:
                raise
        except HTTPException:
            if attempt == retries:
                raise
        else:
            return


def verify(archive: Path, sha256: str) -> None:
    """Raise if the archive's digest does not match the published one."""
    digest = hashlib.sha256()
    with archive.open("rb") as opened:
        while chunk := opened.read(CHUNK_SIZE):
            digest.update(chunk)
    computed = digest.hexdigest()
    if computed.lower() != sha256.lower():
        reason = f"sha256 mismatch: expected {sha256}, got {computed}"
        raise ValueError(reason)


def extract(archive: Path, version: str, dest_dir: Path) -> Path:
    """Unpack the daemon alone out of the archive, and return its path."""
    member = f"bitcoin-{version}/bin/bitcoind"
    with tarfile.open(archive) as opened:
        opened.extract(member, path=dest_dir, filter="data")
    return dest_dir / member


def install(version: str, sha256: str, dest_dir: Path) -> Path:
    """Download, verify and unpack one release, and return the daemon's path."""
    archive = dest_dir / tarball_name(version)
    fetch(version, archive)
    verify(archive, sha256)
    return extract(archive, version, dest_dir)


def _failed(error: BaseException) -> int:
    """Report a failed install on stderr, never on the captured stdout."""
    print(f"::error::{error}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    """Read the version and its digest from the command line, and install it."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help='the release, "31.1" rather than "v31.1"')
    parser.add_argument("sha256", help="the published sha256 of its linux tarball")
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path(),
        help="where to unpack the daemon, the current directory by default",
    )
    args = parser.parse_args(argv)

    # one clause per exception rather than a tuple: ruff-format rewrites a
    # parenthesised tuple into PEP 758's unparenthesised form wherever
    # requires-python is 3.14, which is a syntax error to an interpreter
    # older than that (btclib-org/.github#1160). OSError and HTTPException
    # are what a retry-exhausted fetch raises, tarfile.TarError and
    # KeyError are what extract raises on a corrupt archive or a missing
    # member, and ValueError is verify's checksum mismatch
    try:
        daemon = install(args.version, args.sha256, args.dest)
    except OSError as error:
        return _failed(error)
    except HTTPException as error:
        return _failed(error)
    except tarfile.TarError as error:
        return _failed(error)
    except KeyError as error:
        return _failed(error)
    except ValueError as error:
        return _failed(error)
    print(daemon.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
