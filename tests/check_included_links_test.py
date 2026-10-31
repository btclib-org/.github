# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the docs check of `.github/scripts/check_included_links.py`.

The script runs in a tree's docs job, so no pull request here reaches it:
a stand-in tree in a temporary directory, with a `pyproject.toml`, two
shims and a built page, is what it is asked of. The script is loaded by
path, `.github/scripts` being no package, as the other scripts under it
are tested.
"""

from __future__ import annotations

import importlib.util
import os
from typing import TYPE_CHECKING

import pytest

from . import ROOT
from .workflows_test import steps

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

_SCRIPT = ROOT / ".github" / "scripts" / "check_included_links.py"
_WORKFLOW = ROOT / ".github" / "workflows" / "reusable-docs.yml"
_REPOSITORY = "https://github.com/btclib-org/stand-in"
_BLOB = f"{_REPOSITORY}/blob/main/"


@pytest.fixture(scope="module")
def script() -> ModuleType:
    """Load the script as a module.

    :returns: the module.
    """
    spec = importlib.util.spec_from_file_location("check_included_links", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tree(root: Path, page: str) -> Path:
    """Write a stand-in tree whose shims render SECURITY.md and README.md.

    :param root: where the tree is written.
    :param page: the body of the one built page.
    :returns: the directory the build wrote.
    """
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "stand-in"\n[project.urls]\nrepository = "{_REPOSITORY}"\n',
        encoding="utf-8",
    )
    source = root / "docs" / "source"
    source.mkdir(parents=True)
    for name, path in (("security", "SECURITY.md"), ("readme", "README.md")):
        (source / f"{name}_link.md").write_text(
            f"```{{include}} ../../{path}\n```\n", encoding="utf-8"
        )
    html = root / "docs" / "build" / "html"
    html.mkdir(parents=True)
    (html / "readme_link.html").write_text(page, encoding="utf-8")
    return html


@pytest.mark.parametrize(
    ("href", "refused"),
    [
        pytest.param(f"{_BLOB}SECURITY.md", True, id="included"),
        pytest.param(f"{_BLOB}SECURITY.md#known-limitations", True, id="anchor"),
        pytest.param("security_link.html", False, id="page"),
        pytest.param(f"{_BLOB}RELEASING.md", False, id="not-included"),
        pytest.param(f"{_REPOSITORY}/blob/v1/SECURITY.md", False, id="tag"),
        pytest.param(
            "https://github.com/btclib-org/other/blob/main/SECURITY.md",
            False,
            id="other-repository",
        ),
    ],
)
def test_a_built_page_linking_an_included_file_at_blob_is_refused(
    script: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    href: str,
    refused: bool,  # noqa: FBT001
) -> None:
    """Only a link to `BLOB` plus a path a shim includes is reported.

    :param script: the module under test.
    :param tmp_path: where the stand-in tree is written.
    :param monkeypatch: to run from the root of the stand-in.
    :param href: the link the built page carries.
    :param refused: whether the script reports it.
    """
    html = tree(tmp_path, f'<p>\n<a href="{href}">it</a>\n</p>\n')
    monkeypatch.chdir(tmp_path)
    assert script.main([os.fspath(html)]) == (1 if refused else 0)


def test_the_report_names_the_page_and_the_line(
    script: ModuleType,
    tmp_path: Path,
) -> None:
    """Each link is reported as `page:line: url`.

    :param script: the module under test.
    :param tmp_path: where the stand-in tree is written.
    """
    html = tree(tmp_path, f'<p>\n<a href="{_BLOB}README.md">it</a>\n')
    paths = script.included(tmp_path)
    assert paths == {"SECURITY.md", "README.md"}
    assert script.blob(tmp_path) == _BLOB
    found = script.links(html, _BLOB, paths)
    assert found == [f"{html / 'readme_link.html'}:2: {_BLOB}README.md"]


def test_a_shim_with_two_fences_stops_the_check(
    script: ModuleType,
    tmp_path: Path,
) -> None:
    """A shim that does not name one file is an error, not a skipped shim.

    :param script: the module under test.
    :param tmp_path: where the stand-in tree is written.
    """
    tree(tmp_path, "")
    shim = tmp_path / "docs" / "source" / "security_link.md"
    shim.write_text(shim.read_text(encoding="utf-8") * 2, encoding="utf-8")
    with pytest.raises(ValueError, match="2 include fences"):
        script.included(tmp_path)


def test_the_docs_job_runs_the_check_after_the_build() -> None:
    """The step runs the script on the directory the build wrote."""
    runs = [str(step.get("run", "")) for step in steps(_WORKFLOW)]
    build = next(i for i, run in enumerate(runs) if "sphinx-build" in run)
    check = next(i for i, run in enumerate(runs) if _SCRIPT.name in run)
    assert build < check
    assert runs[check].split()[-1] == "docs/build/html"


@pytest.mark.parametrize(
    "argv",
    [
        pytest.param([], id="none"),
        pytest.param(["docs/build/html", "extra"], id="two"),
    ],
)
def test_a_wrong_argument_count_exits_2(script: ModuleType, argv: list[str]) -> None:
    """Anything but the one directory is a usage error.

    :param script: the module under test.
    :param argv: the arguments given.
    """
    assert script.main(argv) == 2  # noqa: PLR2004


@pytest.mark.parametrize("built", [True, False], ids=["empty", "missing"])
def test_a_directory_holding_no_page_exits_2(
    script: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    built: bool,  # noqa: FBT001
) -> None:
    """A directory with no html, or none at all, is not a clean build.

    :param script: the module under test.
    :param tmp_path: where the stand-in tree is written.
    :param monkeypatch: to run from the root of the stand-in.
    :param built: whether the directory exists, empty.
    """
    html = tree(tmp_path, "")
    (html / "readme_link.html").unlink()
    if not built:
        html.rmdir()
    monkeypatch.chdir(tmp_path)
    assert script.main([os.fspath(html)]) == 2  # noqa: PLR2004
