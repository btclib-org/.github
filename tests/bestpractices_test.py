# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the bestpractices.dev snapshot, and for how old a review gets.

The script's tests are offline: `gh` and the bestpractices.dev fetch are
replaced by fixtures. The script is loaded by path, `.github/scripts`
being no package, as the other scripts under it are tested. The last test
asks the API how long ago each registered tree released.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

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


def test_answers_keep_status_and_justification_only(script: ModuleType) -> None:
    """Each criterion has both fields, a missing justification as `None`."""
    assert script.answers(_PROJECT) == {
        "description_good": {"status": "Met", "justification": None},
        "sites_https": {
            "status": "Met",
            "justification": "Signed v2026.9.1 and v2026.10.4.",
        },
        "OSPS-QA-05.02": {"status": "Unmet", "justification": None},
    }


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
    saved = {
        "a": {"justification": "Since v2026.9.30, 2026-10-01 and v2026.9.30."},
        "b": {"justification": "In the next release; the Draft says so."},
        "c": {"justification": "v2026.10.4 and v2026.11.1, until 2027-09-30."},
        "d": {"justification": "2026.9.30 without its v, Python 3.10."},
        "e": {"justification": None},
    }
    assert script.stale(saved, "v2026.10.4", "2026-10-03T22:09:48Z") == [
        "a: v2026.9.30, 2026-10-01",
        "b: next release, draft",
    ]


def test_a_rerun_with_nothing_changed_writes_the_same_files(
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
    assert script.main(["--saved", str(tmp_path)]) == 0
    first = (tmp_path / "btclib.json").read_bytes()
    assert script.main(["--saved", str(tmp_path)]) == 0
    assert [path.name for path in tmp_path.iterdir()] == ["btclib.json"]
    assert (tmp_path / "btclib.json").read_bytes() == first


def test_the_file_of_a_tree_no_longer_registered_is_removed(
    script: ModuleType, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A saved file whose tree has lost its badge goes with it."""
    (tmp_path / "bbt.json").write_text("{}\n")
    monkeypatch.setattr(script, "registered", lambda: {"btclib": _ID})
    monkeypatch.setattr(script, "fetch", lambda number: {**_PROJECT, "id": number})
    assert script.main(["--saved", str(tmp_path)]) == 0
    assert [path.name for path in tmp_path.iterdir()] == ["btclib.json"]


def test_differ_lists_a_status_not_the_same_in_every_tree(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Only a criterion whose statuses differ is listed, trees sorted."""
    saved = {
        "btclib": {"a": {"status": "Met"}, "b": {"status": "Met"}},
        "bitcoin-core-rpc": {"a": {"status": "Unmet"}, "b": {"status": "Met"}},
        "btclib-ecc": {
            "a": {"status": "Met"},
            "b": {"status": "Met"},
            "c": {"status": "Met"},
        },
    }
    for tree, given in saved.items():
        (tmp_path / f"{tree}.json").write_text(json.dumps(given))
    assert script.main(["--differ", "--saved", str(tmp_path)]) == 0
    assert capsys.readouterr().out == (
        "a: bitcoin-core-rpc Unmet, btclib Met, btclib-ecc Met\n"
        "c: bitcoin-core-rpc -, btclib -, btclib-ecc Met\n"
    )


def test_stale_reads_the_saved_files_and_the_latest_release(
    script: ModuleType,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Each line names the tree, its release, the criterion and what is old."""
    (tmp_path / "btclib.json").write_text(script.render(script.answers(_PROJECT)))
    release = {"tag_name": "v2026.10.4", "published_at": "2026-10-03T22:09:48Z"}
    asked: list[tuple[str, ...]] = []

    def gh(*args: str) -> str:
        asked.append(args)
        return json.dumps(release)

    monkeypatch.setattr(script, "gh", gh)
    assert script.main(["--stale", "--saved", str(tmp_path)]) == 0
    assert asked == [("repos/btclib-org/btclib/releases/latest",)]
    assert capsys.readouterr().out == "btclib v2026.10.4: sites_https: v2026.9.1\n"


@pytest.mark.parametrize(
    "path", sorted((_ROOT / "bestpractices").glob("*.json")), ids=lambda p: p.name
)
def test_a_saved_file_is_what_the_script_writes(script: ModuleType, path: Path) -> None:
    """A hand edit that the next run would undo is refused now."""
    text = path.read_text(encoding="utf-8")
    assert script.render(json.loads(text)) == text


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
