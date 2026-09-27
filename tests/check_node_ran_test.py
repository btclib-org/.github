# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the node-ran check of `.github/scripts`.

No run of `reusable-integration-bitcoind.yml` can show every shape this
guards against at once: a caller either sets `skip-reason-prefix` or
does not, and its own report holds whatever its own suite produced that
day. So both, and the guards this step exists for -- an empty report, a
report of exempt skips alone, and a skip nothing exempts -- are
exercised here against a JUnit report this module builds itself.

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
            },
            {"classname": "tests.integration.test_a", "name": "test_two"},
        ],
    )

    assert script.main([str(report)]) == 1
    out = capsys.readouterr().out
    assert "::error::test_one skipped: node does not answer" in out
    assert "::error::1 test(s) ran, 1 of 1 skip(s) unexempted" in out


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
            },
            {"classname": "tests.integration.test_a", "name": "test_two"},
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
            },
            {"classname": "tests.integration.test_a", "name": "test_two"},
        ],
    )

    assert (
        script.main([str(report), "--skip-reason-prefix", "node does not declare "])
        == 1
    )
    out = capsys.readouterr().out
    assert "::error::test_one skipped" in out
    assert "::error::1 test(s) ran, 1 of 1 skip(s) unexempted" in out


def test_a_report_of_exempt_skips_alone_fails(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """An exempt skip does not count as a test that ran, so none ran here."""
    report = _report(
        tmp_path,
        [
            {
                "classname": "tests.integration.hwi_device_test",
                "name": f"test_{i}",
                "skipped": "set BTCLIB_HWI to run against a device",
            }
            for i in range(2)
        ],
    )

    assert script.main([str(report), "--skip-reason-prefix", "set BTCLIB_HWI"]) == 1
    out = capsys.readouterr().out
    assert "::error::0 test(s) ran, 0 of 2 skip(s) unexempted" in out


@pytest.mark.parametrize(
    ("passed", "exempt"),
    [
        pytest.param(3, 3, id="as-many-exempt-as-ran"),
        pytest.param(176, 151, id="more-ran-than-exempt"),
    ],
)
def test_only_the_cases_that_ran_are_counted(
    script: ModuleType,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    passed: int,
    exempt: int,
) -> None:
    """A report mixing ran and exempt cases passes, counting only what ran."""
    ran = [
        {"classname": "tests.integration.node_test", "name": f"test_ran_{i}"}
        for i in range(passed)
    ]
    skipped = [
        {
            "classname": "tests.integration.node_test",
            "name": f"test_skipped_{i}",
            "skipped": "node does not declare bip324",
        }
        for i in range(exempt)
    ]
    report = _report(tmp_path, ran + skipped)

    assert (
        script.main([str(report), "--skip-reason-prefix", "node does not declare "])
        == 0
    )
    out = capsys.readouterr().out
    assert (
        f"{passed} test(s) ran against the node, "
        f"{exempt} exempt skip(s) not counted among them"
    ) in out


def test_skip_reason_is_none_for_a_case_that_ran(script: ModuleType) -> None:
    """A testcase with no `skipped` child is not a skip at all."""
    case = ET.Element("testcase", classname="a", name="one")

    assert script.skip_reason(case) is None
