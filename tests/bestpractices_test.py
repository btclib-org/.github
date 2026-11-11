# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the bestpractices.dev answers, and for how old a review gets.

The script's tests are offline: `gh` and the bestpractices.dev fetch are
replaced by fixtures. The script is loaded by path, `.github/scripts`
being no package, as the other scripts under it are tested. The last test
asks the API how long ago each registered tree released.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qsl, urlsplit

import pytest

from . import ORG, by_hand, gh_json
from .grid_test import record

if TYPE_CHECKING:
    from types import ModuleType

_ROOT = Path(__file__).parents[1]
_SCRIPT = _ROOT / ".github" / "scripts" / "bestpractices.py"

# the shapes measured on a real entry: a criterion with both keys, one
# with a status and no justification key, an OSPS key in upper case, a
# justification that is null, and a field that is no criterion
_PROJECT: dict[str, Any] = {
    "id": 1,
    "name": "btclib",
    "description_good_status": "Met",
    "sites_https_status": "Met",
    "sites_https_justification": "Signed v2026.9.1 and v2026.10.4.",
    "OSPS-QA-05.02_status": "Unmet",
    "OSPS-QA-05.02_justification": None,
}

# what the file holds for `_PROJECT`
_FILE: dict[str, Any] = {
    "description_good_status": "Met",
    "osps_qa_05_02_status": "Unmet",
    "sites_https_justification": "Signed v2026.9.1 and v2026.10.4.",
    "sites_https_status": "Met",
}

_ID = 14253
_README = """
[![Best Practices](https://www.bestpractices.dev/projects/14253/badge)](https://www.bestpractices.dev/projects/14253)
[![Baseline](https://www.bestpractices.dev/projects/14253/baseline)](https://www.bestpractices.dev/projects/14253)
"""


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("bestpractices", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "bestpractices", module)
    spec.loader.exec_module(module)
    return module


def _files(tmp_path: Path, held: dict[str, dict[str, Any]]) -> Path:
    """Write each tree's file where `--seed` puts it, and return the root."""
    for tree, given in held.items():
        (tmp_path / tree).mkdir()
        (tmp_path / tree / ".bestpractices.json").write_text(json.dumps(given))
    return tmp_path


def test_answers_are_flat_and_named_as_the_site_reads_them(
    script: ModuleType,
) -> None:
    """An OSPS key is lower case with `_`; a null justification is dropped."""
    assert script.answers(_PROJECT) == _FILE


def test_render_does_not_depend_on_the_order_fetched(script: ModuleType) -> None:
    """Keys are sorted and the file ends in a newline."""
    forward = script.answers(_PROJECT)
    backward = script.answers(dict(reversed(_PROJECT.items())))
    assert list(forward) != list(backward)
    assert script.render(forward) == script.render(backward)
    assert script.render(forward).endswith("}\n")


def test_the_badge_names_the_project(script: ModuleType) -> None:
    """One id, repeated across badges, is the project; none is no project."""
    assert script.project_id(_README) == _ID
    assert script.project_id("www.bestpractices.dev/projects/<id>/badge") is None
    with pytest.raises(ValueError, match="several"):
        script.project_id(_README + "bestpractices.dev/projects/14813")


def test_stale_lists_what_is_older_than_the_release(script: ModuleType) -> None:
    """Older versions and dates, and the undated words, are listed."""
    given = {
        "a_justification": "Since v2026.9.30, 2026-10-01 and v2026.9.30.",
        "b_justification": "In the next release; the Draft says so.",
        "c_justification": "v2026.10.4 and v2026.11.1, until 2027-09-30.",
        "d_justification": "2026.9.30 without its v, Python 3.10.",
        "e_status": "Met",
    }
    assert script.stale(given, "v2026.10.4", "2026-10-03T22:09:48Z") == [
        "a: v2026.9.30, 2026-10-01",
        "b: next release, draft",
    ]


def test_seed_writes_a_file_per_tree_and_a_rerun_the_same(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Only a tree with a badge is written, and a second run changes nothing."""
    readmes = {"btclib": _README, "bbt": "no badge here"}

    def gh(*args: str) -> str:
        if "--paginate" in args:
            return "btclib\nbbt\n"
        return readmes[args[-1].split("/")[2]]

    monkeypatch.setattr(script, "gh", gh)
    monkeypatch.setattr(script, "fetch", lambda number: {**_PROJECT, "id": number})
    assert script.main(["--seed", str(tmp_path)]) == 0
    written = tmp_path / "btclib" / ".bestpractices.json"
    first = written.read_bytes()
    assert script.main(["--seed", str(tmp_path)]) == 0
    assert [path.name for path in tmp_path.iterdir()] == ["btclib"]
    assert [path.name for path in written.parent.iterdir()] == [written.name]
    assert written.read_bytes() == first
    assert first.decode() == script.render(_FILE)


def test_a_mode_is_required(script: ModuleType) -> None:
    """With no mode the script stops before it reads anything."""
    with pytest.raises(SystemExit, match="2"):
        script.main([])


def test_differ_lists_a_status_not_the_same_in_every_tree(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Only a criterion whose statuses differ is listed, trees sorted."""
    held = {
        "btclib": {"a_status": "Met", "b_status": "Met"},
        "bitcoin-core-rpc": {"a_status": "Unmet", "b_status": "Met"},
        "btclib-ecc": {"a_status": "Met", "b_status": "Met", "c_status": "Met"},
    }
    files = _files(tmp_path, held)
    trees = dict.fromkeys(sorted([*held, "ecc"]), _ID)
    monkeypatch.setattr(script, "registered", lambda: trees)
    assert script.main(["--differ", "--files", str(files)]) == 0
    assert capsys.readouterr().out == (
        "ecc: no .bestpractices.json\n"
        "a: bitcoin-core-rpc Unmet, btclib Met, btclib-ecc Met\n"
        "c: bitcoin-core-rpc -, btclib -, btclib-ecc Met\n"
    )


def test_stale_reads_the_files_and_the_latest_release(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Each line names the tree, its release, the criterion and what is old."""
    files = _files(tmp_path, {"btclib": _FILE})
    monkeypatch.setattr(script, "registered", lambda: {"btclib": _ID, "ecc": 1})
    release = {"tag_name": "v2026.10.4", "published_at": "2026-10-03T22:09:48Z"}
    asked: list[tuple[str, ...]] = []

    def gh(*args: str) -> str:
        asked.append(args)
        return json.dumps(release)

    monkeypatch.setattr(script, "gh", gh)
    assert script.main(["--stale", "--files", str(files)]) == 0
    assert asked == [("repos/btclib-org/btclib/releases/latest",)]
    assert capsys.readouterr().out == (
        "ecc: no .bestpractices.json\nbtclib v2026.10.4: sites_https: v2026.9.1\n"
    )


def test_drift_prints_nothing_for_a_tree_that_agrees(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The file `--seed` writes agrees with the site it was read from."""
    monkeypatch.setattr(script, "registered", lambda: {"btclib": _ID})
    monkeypatch.setattr(script, "fetch", lambda number: {**_PROJECT, "id": number})
    assert script.main(["--seed", str(tmp_path)]) == 0
    assert script.main(["--drift", "--files", str(tmp_path)]) == 0
    assert capsys.readouterr().out == ""


def test_drift_lists_what_differs_and_proposes_the_file(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Each differing criterion, then a URL forcing the file's values."""
    given = {
        **_FILE,
        "description_good_status": "Unmet",
        "description_good_justification": "Says what & why.",
        "osps_qa_05_02_status": "Met",
        "sites_https_justification": "Signed v2026.11.1.",
    }
    files = _files(tmp_path, {"btclib": given, "btclib-ecc": _FILE})
    trees = {"btclib": _ID, "btclib-ecc": 2, "ecc": 3}
    monkeypatch.setattr(script, "registered", lambda: trees)
    monkeypatch.setattr(script, "fetch", lambda number: {**_PROJECT, "id": number})
    assert script.main(["--drift", "--files", str(files)]) == 0
    *listed, last = capsys.readouterr().out.splitlines()
    assert listed == [
        "ecc: no .bestpractices.json",
        "btclib: description_good: status, justification",
        "btclib: osps_qa_05_02: status",
        "btclib: sites_https: justification",
    ]
    tree, url = last.split(": ", 1)
    assert tree == "btclib"
    parts = urlsplit(url)
    assert (parts.scheme, parts.netloc, parts.path) == (
        "https",
        "www.bestpractices.dev",
        f"/projects/{_ID}/choose/edit",
    )
    query = parse_qsl(parts.query, keep_blank_values=True)
    assert query == [
        ("description_good_status", "Unmet"),
        ("description_good_justification", "Says what & why."),
        ("osps_qa_05_02_status", "Met"),
        ("osps_qa_05_02_justification", ""),
        ("sites_https_status", "Met"),
        ("sites_https_justification", "Signed v2026.11.1."),
        ("overrides", ",".join(key for key, _ in query[:-1])),
    ]


@pytest.mark.parametrize(
    ("code", "stderr", "expected"),
    [(0, "", "{}\n"), (1, "gh: Not Found (HTTP 404)\n", None)],
    ids=["found", "missing"],
)
def test_a_tree_file_is_read_from_its_default_branch(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    code: int,
    stderr: str,
    expected: str | None,
) -> None:
    """The raw contents of the file, or `None` where the API has none."""
    asked: list[list[str]] = []

    def run(args: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        asked.append(args)
        return subprocess.CompletedProcess(
            args, code, "{}\n" if code == 0 else "", stderr
        )

    monkeypatch.setattr(script.subprocess, "run", run)
    assert script.tree_file("btclib") == expected
    assert asked == [
        [
            "gh",
            "api",
            "-H",
            "Accept: application/vnd.github.raw",
            "repos/btclib-org/btclib/contents/.bestpractices.json",
        ]
    ]
    assert script.read("btclib", None) == (None if expected is None else {})


def test_a_failure_other_than_a_missing_file_stops(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A tree is not listed as having no file because the API failed."""

    def run(args: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args, 1, "", "gh: Bad credentials (HTTP 401)\n"
        )

    monkeypatch.setattr(script.subprocess, "run", run)
    with pytest.raises(subprocess.CalledProcessError):
        script.tree_file("btclib")


# the longest a registered tree goes without a release, and so a review
_SIX_MONTHS = timedelta(days=183)


@pytest.mark.integration
def test_a_registered_tree_released_within_six_months(repository: str) -> None:
    """Section 10 reviews the answers at a release, so a release is due.

    A failure is answered by an issue asking for the review, cited by a
    `BACKLOG` row until the tree releases.

    :param repository: the repository asked about.
    """
    if repository not in record()["scorecard"]:
        pytest.skip(f"section 10's scorecard entry does not name {repository}")
    published = gh_json(f"repos/{ORG}/{repository}/releases/latest")["published_at"]
    age = datetime.now(UTC) - datetime.fromisoformat(published)
    assert age < _SIX_MONTHS, (
        f"{repository} last released at {published}: open an issue in"
        f" {ORG}/.github asking for its bestpractices.dev review; "
        + by_hand(repository, "gh release view --json tagName,publishedAt")
    )
