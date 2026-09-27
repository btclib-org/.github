# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the node-ran check of `.github/scripts`.

No run of `reusable-integration-bitcoind.yml` can show every shape this
guards against at once: a caller either sets `exclude-classname`, or
`skip-reason-prefix`, or neither, or both together, and its own report
holds whatever its own suite produced that day. So every combination of
the two inputs, and the guards this step exists for -- an empty report,
and a skip nothing exempts -- are exercised here against a JUnit report
this module builds itself.

The script is loaded by path, `.github/scripts` being no package, as the
other scripts under it are tested.
"""

from __future__ import annotations

import importlib.util
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

_SCRIPT = Path(__file__).parents[1] / ".github" / "scripts" / "check_node_ran.py"


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("check_node_ran", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "check_node_ran", module)
    spec.loader.exec_module(module)
    return module


def _report(tmp_path: Path, cases: list[dict[str, str]]) -> Path:
    """Write a JUnit report holding the given testcases, and return its path."""
    root = ET.Element("testsuite")
    for case in cases:
        elem = ET.SubElement(
            root, "testcase", classname=case["classname"], name=case["name"]
        )
        if "skipped" in case:
            ET.SubElement(elem, "skipped", message=case["skipped"])
    path = tmp_path / "integration.xml"
    ET.ElementTree(root).write(path)
    return path


def test_every_case_ran_is_a_pass(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """No skips at all is the ordinary, green case."""
    report = _report(
        tmp_path,
        [{"classname": "tests.integration.test_a", "name": "test_one"}],
    )

    assert script.main([str(report)]) == 0
    assert "1 test(s) ran against the node" in capsys.readouterr().out


def test_an_empty_report_fails_even_with_nothing_skipped(
    script: ModuleType, tmp_path: Path
) -> None:
    """A fixture that stopped finding the node asks nothing, and that fails."""
    report = _report(tmp_path, [])

    assert script.main([str(report)]) == 1


def test_an_unexempted_skip_fails_the_job(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The ordinary case this step exists for: a skip nobody declared."""
    report = _report(
        tmp_path,
        [
            {
                "classname": "tests.integration.test_a",
                "name": "test_one",
                "skipped": "node does not answer",
            }
        ],
    )

    assert script.main([str(report)]) == 1
    out = capsys.readouterr().out
    assert "::error::test_one skipped: node does not answer" in out


def test_exclude_classname_removes_the_case_from_judgment_entirely(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A matching classname is not counted, skipped or not."""
    report = _report(
        tmp_path,
        [
            {
                "classname": "tests.integration.test_btclib_node",
                "name": "test_one",
                "skipped": "no btclib-node in this job",
            },
            {"classname": "tests.integration.test_a", "name": "test_two"},
        ],
    )

    assert script.main([str(report), "--exclude-classname", "btclib_node"]) == 0
    assert "1 test(s) ran against the node" in capsys.readouterr().out


def test_exclude_classname_does_not_rescue_an_unmatched_skip(
    script: ModuleType, tmp_path: Path
) -> None:
    """The substring is compared, not merely present somewhere in the report."""
    report = _report(
        tmp_path,
        [
            {
                "classname": "tests.integration.test_a",
                "name": "test_one",
                "skipped": "node does not answer",
            }
        ],
    )

    assert script.main([str(report), "--exclude-classname", "btclib_node"]) == 1


def test_skip_reason_prefix_exempts_a_matching_skip(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A skip whose reason carries the declared prefix does not fail the job."""
    report = _report(
        tmp_path,
        [
            {
                "classname": "tests.integration.test_a",
                "name": "test_one",
                "skipped": "node does not declare bip324",
            }
        ],
    )

    assert (
        script.main([str(report), "--skip-reason-prefix", "node does not declare "])
        == 0
    )
    out = capsys.readouterr().out
    assert "test_one skipped and exempt: node does not declare bip324" in out
    assert "::error::" not in out


def test_skip_reason_prefix_does_not_exempt_a_different_reason(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Only a reason actually carrying the prefix is exempt."""
    report = _report(
        tmp_path,
        [
            {
                "classname": "tests.integration.test_a",
                "name": "test_one",
                "skipped": "no bitcoind reachable at all",
            }
        ],
    )

    assert (
        script.main([str(report), "--skip-reason-prefix", "node does not declare "])
        == 1
    )
    assert "::error::test_one skipped" in capsys.readouterr().out


def test_the_case_a_reason_prefix_exempts_still_counts_as_ran(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Unlike exclude-classname, an exempt skip still counts as one that ran."""
    report = _report(
        tmp_path,
        [
            {
                "classname": "tests.integration.test_a",
                "name": "test_one",
                "skipped": "node does not declare bip324",
            }
        ],
    )

    script.main([str(report), "--skip-reason-prefix", "node does not declare "])

    assert "1 test(s) ran against the node" in capsys.readouterr().out


def test_both_exemptions_apply_independently(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A caller mid-migration can carry both at once, each doing its own job."""
    report = _report(
        tmp_path,
        [
            {
                "classname": "tests.integration.test_btclib_node",
                "name": "test_one",
                "skipped": "no btclib-node in this job",
            },
            {
                "classname": "tests.integration.test_a",
                "name": "test_two",
                "skipped": "node does not declare bip324",
            },
            {"classname": "tests.integration.test_a", "name": "test_three"},
        ],
    )

    assert (
        script.main(
            [
                str(report),
                "--exclude-classname",
                "btclib_node",
                "--skip-reason-prefix",
                "node does not declare ",
            ]
        )
        == 0
    )
    assert "2 test(s) ran against the node" in capsys.readouterr().out


def test_considered_reads_every_case_with_no_exclusion(script: ModuleType) -> None:
    """An empty exclude-classname filters nothing out."""
    root = ET.Element("testsuite")
    ET.SubElement(root, "testcase", classname="a", name="one")
    ET.SubElement(root, "testcase", classname="b", name="two")

    assert [case.get("name") for case in script.considered(root, "")] == [
        "one",
        "two",
    ]


def test_skip_reason_is_none_for_a_case_that_ran(script: ModuleType) -> None:
    """A testcase with no `skipped` child is not a skip at all."""
    case = ET.Element("testcase", classname="a", name="one")

    assert script.skip_reason(case) is None
