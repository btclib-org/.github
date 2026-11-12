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
        pytest.param(f"{_BLOB}SECURITY.md?plain=1", True, id="query"),
        pytest.param(f"{_BLOB}SECURITY.md?plain=1#L3", True, id="query-anchor"),
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
    """Only a link to `BLOB` plus a path a page includes is reported.

    :param script: the module under test.
    :param tmp_path: where the stand-in tree is written.
    :param monkeypatch: to run from the root of the stand-in.
    :param href: the link the built page carries.
    :param refused: whether the script reports it.
    """
    html = tree(tmp_path, f'<p>\n<a href="{href}">it</a>\n</p>\n')
    monkeypatch.chdir(tmp_path)
    assert script.main([os.fspath(html)]) == (1 if refused else 0)


def test_the_repository_key_is_read_whatever_its_case(
    script: ModuleType,
    tmp_path: Path,
) -> None:
    """Section 3's `[project.urls]` keys compare case-insensitively.

    :param script: the module under test.
    :param tmp_path: where the stand-in tree is written.
    """
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nname = "stand-in"\n[project.urls]\nRepository = "{_REPOSITORY}"\n',
        encoding="utf-8",
    )
    assert script.blob(tmp_path) == _BLOB


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


def test_a_page_other_than_a_shim_renders_what_it_includes(
    script: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`index.md` including `README.md` renders it, as a shim would.

    A page with no include fence renders no root file.

    :param script: the module under test.
    :param tmp_path: where the stand-in tree is written.
    :param monkeypatch: to run from the root of the stand-in.
    """
    html = tree(tmp_path, f'<a href="{_BLOB}README.md">it</a>\n')
    source = tmp_path / "docs" / "source"
    (source / "readme_link.md").unlink()
    (source / "index.md").write_text(
        "# Stand-in\n\n```{include} ../../README.md\n```\n", encoding="utf-8"
    )
    (source / "api.md").write_text("# API\n", encoding="utf-8")
    assert script.included(tmp_path) == {"SECURITY.md", "README.md"}
    monkeypatch.chdir(tmp_path)
    assert script.main([os.fspath(html)]) == 1


# pages, and the paths of the include fences each holds;
# root_file_links_test.py asks the same of section 14's part of conf.py
FENCES = [
    pytest.param(
        "```{include} a.md\n```\n\n```\n```{include} b.md\n```\n",
        ["a.md"],
        id="backticks",
    ),
    pytest.param("~~~\n```{include} b.md\n```\n~~~\n", [], id="tildes"),
    pytest.param("````markdown\n```{include} b.md\n```\n````\n", [], id="nested"),
    pytest.param("~~~~text\n~~~\n```{include} b.md\n```\n", [], id="shorter-marker"),
    pytest.param(
        "````{note}\n```{include} a.md\n```\n````\n", ["a.md"], id="directive"
    ),
    pytest.param(
        "````{code-block} markdown\n```{include} b.md\n```\n````\n",
        [],
        id="code-block",
    ),
    pytest.param("````{eval-rst}\n```{include} b.md\n```\n````\n", [], id="eval-rst"),
    pytest.param("~~~{include} a.md\n~~~\n", ["a.md"], id="tilde-include"),
    pytest.param("````{include} a.md\n````\n", ["a.md"], id="long-include"),
    pytest.param(
        "```text\nexample\n ```\n```{include} a.md\n```\n",
        ["a.md"],
        id="indented-close",
    ),
    pytest.param(
        "- ```text\n  x\n  ```\n\n```{include} a.md\n```\n",
        ["a.md"],
        id="bullet-item-fence",
    ),
    pytest.param(
        "1. ```text\n   x\n   ```\n\n```{include} a.md\n```\n",
        ["a.md"],
        id="numbered-item-fence",
    ),
    pytest.param(
        "- a\n\n  ```text\n  ```\n\n ```{include} a.md\n ```\n",
        ["a.md"],
        id="item-code",
    ),
    pytest.param("- a\n# H\n  ```text\n ```{include} b.md\n ```\n", [], id="heading"),
    pytest.param("* * *\n  ```text\n ```{include} b.md\n ```\n", [], id="break"),
    pytest.param("- a\n> q\n\n  ```text\n ```{include} b.md\n ```\n", [], id="quote"),
    pytest.param(
        "text\n2) d\n   ```{include} a.md\n   ```\n", ["a.md"], id="lazy-item"
    ),
    pytest.param(
        " ````{note}\n    ```\n   ~~~{include} b.md\n   ~~~\n ````\n",
        [],
        id="indented-directive",
    ),
    pytest.param(
        "````{note}\n---\nclass: x\n---\n```{include} a.md\n```\n````\n",
        ["a.md"],
        id="options",
    ),
    pytest.param(
        "---\n```{include} b.md\n```\n---\n```{include} a.md\n```\n",
        ["a.md"],
        id="front-matter",
    ),
    pytest.param(
        "<div>\n```{include} b.md\n```\n\n```{include} a.md\n```\n",
        ["a.md"],
        id="html-block",
    ),
    pytest.param(
        "<pre>\n\n```{include} b.md\n```\n</pre>\n\n```{include} a.md\n```\n",
        ["a.md"],
        id="html-pre",
    ),
    pytest.param(
        "text\n<span>\n```{include} a.md\n```\n", ["a.md"], id="html-tag-in-text"
    ),
    pytest.param("- a\n```{include} a.md\n```\n", ["a.md"], id="fence-ends-item"),
    pytest.param("- a\n  <!--\n```{include} a.md\n```\n", ["a.md"], id="item-comment"),
    pytest.param(" ```{include} a.md\n ```\n", ["a.md"], id="indented-include"),
    pytest.param(
        "   ```text\nx\n```\n\n```{include} a.md\n```\n", ["a.md"], id="indented-code"
    ),
    pytest.param(
        "<!--\n```{include} b.md\n```\n-->\n\n```{include} a.md\n```\n",
        ["a.md"],
        id="comment",
    ),
    pytest.param(
        "<!-- x -->\n```{include} a.md\n```\n", ["a.md"], id="one-line-comment"
    ),
    pytest.param(
        "````{note}\n<!--\n````\n```{include} a.md\n```\n",
        ["a.md"],
        id="comment-in-directive",
    ),
    pytest.param("    <!--\n```{include} a.md\n```\n", ["a.md"], id="indented-comment"),
    pytest.param("    ```{include} b.md\n    ```\n", [], id="four-spaces"),
    pytest.param(
        "```text\n    ```\n```{include} b.md\n```\n", [], id="four-spaces-close"
    ),
    pytest.param("\tx\n<br>\n ```{include} b.md\n ```\n", [], id="tab-code"),
    pytest.param(
        " ````{note}\n\t```\n```{include} b.md\n```\n", [], id="tab-in-directive"
    ),
    pytest.param(
        " ````{note}\n \t```\n```{include} a.md\n",
        ["a.md"],
        id="tab-left-in-directive",
    ),
    pytest.param(
        " `````{note}\n  ````{tip}\n \t ```{include} b.md\n  ````\n `````\n",
        [],
        id="tab-in-nested-directive",
    ),
    pytest.param(
        "[r]: http://x\n<br>\n ```{include} b.md\n ```\n", [], id="definition"
    ),
    pytest.param("[^n]:\n<span>\n ```{include} b.md\n ```\n", [], id="footnote"),
    pytest.param(
        "a[^n]\n\n[^n]: first\n\n    second\n<span>\n```{include} a.md\n```\n",
        ["a.md"],
        id="footnote-paragraphs",
    ),
    pytest.param(
        "a[^m]\n\n[^m]: ```text\n    x\n    ```\n<span>\n ```{include} b.md\n ```\n",
        [],
        id="footnote-fence",
    ),
    pytest.param(
        "---\n```{include} b.md\n```\n  ...\n```{include} a.md\n```\n",
        ["a.md"],
        id="front-matter-dots",
    ),
    pytest.param(
        "---\n```{include} a.md\n```\n...\n", ["a.md"], id="front-matter-dots-last"
    ),
    pytest.param(
        "````{versionchanged} 2.0\n---\n```{include} a.md\n```\n````\n",
        ["a.md"],
        id="no-options-dashes",
    ),
    pytest.param(
        "````{only} html\n---\n```{include} a.md\n```\n````\n",
        ["a.md"],
        id="no-options-only",
    ),
    pytest.param(
        "````{versionadded} 1.2\n:f: x\n<span>\n```{include} a.md\n```\n````\n",
        ["a.md"],
        id="no-options-colon",
    ),
    pytest.param(
        "````{note}\n---\nclass: x\n---X```{include} a.md\n```\n````\n",
        ["a.md"],
        id="options-closer-text",
    ),
    pytest.param(
        "````{note}\n:class: x\n\n---\n```{include} a.md\n```\n...\n````\n",
        ["a.md"],
        id="body-dots-last",
    ),
    pytest.param(
        "````{note}\n:class: x\n\n---\n```{include} a.md\n```\n...\n\n````\n",
        ["a.md"],
        id="body-dots-one-blank",
    ),
    pytest.param(
        "````{note}\n:class: x\n\n---\n```{include} b.md\n```\n...\n\n\n````\n",
        [],
        id="body-dots-two-blanks",
    ),
    pytest.param(
        "````{note}\n:class: x\n<br>\n ```{include} b.md\n ```\n````\n",
        [],
        id="colon-options",
    ),
    pytest.param(
        "````{note}\n\n---\n```{include} b.md\n```\n---\n````\n",
        [],
        id="blank-front-matter",
    ),
    pytest.param(
        "````{note}\n```{topic} T\n```{include} b.md\n```\n```\n````\n",
        [],
        id="topic-in-note",
    ),
    pytest.param(
        "````{sidebar} S\n```{topic} T\n```{include} a.md\n```\n```\n````\n",
        ["a.md"],
        id="topic-in-sidebar",
    ),
    pytest.param(
        "````{note} text\n<span>\n```{include} a.md\n```\n````\n",
        ["a.md"],
        id="opener-text-html",
    ),
    pytest.param(
        "````{tip} text\n\n---\n```{include} a.md\n```\n---\n````\n",
        ["a.md"],
        id="opener-text-blank",
    ),
    pytest.param(
        "````{epigraph} text\n---\n```{include} a.md\n```\n---\n````\n",
        ["a.md"],
        id="opener-text-quote",
    ),
    pytest.param(
        " ````{hint} <!--\n ```{include} b.md\n ```\n ````\n",
        [],
        id="opener-comment",
    ),
    pytest.param(
        "````{note} text\n[r]: http://x\n<br>\n```{include} a.md\n```\n````\n",
        ["a.md"],
        id="opener-text-definition",
    ),
    pytest.param(
        "````{note} text\n:class: x\n<span>\n```{include} a.md\n```\n````\n",
        ["a.md"],
        id="opener-text-colon-options",
    ),
    pytest.param(
        "````{note} text\n---\nclass: x\n---\n<span>\n```{include} a.md\n```\n````\n",
        ["a.md"],
        id="opener-text-dash-options",
    ),
    pytest.param(
        "````{compound} text\n<span>\n```{include} a.md\n```\n````\n",
        ["a.md"],
        id="opener-text-compound",
    ),
    pytest.param(
        "````{pull-quote} text\n---\n```{include} a.md\n```\n---\n````\n",
        ["a.md"],
        id="opener-text-pull-quote",
    ),
    pytest.param(
        "```{note}text\n```{include} b.md\n```\n",
        [],
        id="name-run-on",
    ),
    pytest.param(
        "`````{versionadded} 1\n````{topic} T\n```{include} a.md\n```\n````\n`````\n",
        ["a.md"],
        id="topic-in-version",
    ),
    pytest.param(
        "`````{versionadded} 1\n````{sidebar} S\n```{include} a.md\n```\n````\n`````\n",
        ["a.md"],
        id="sidebar-in-version",
    ),
    pytest.param(
        "``````{epigraph}\n\n\n-->\n ```{include} b.md\n",
        [],
        id="attribution",
    ),
    pytest.param("````{acks}\n```{include} b.md\n```\n````\n", [], id="acks"),
    pytest.param(
        "````{acks}\n ```{include} b.md\n ```\n````\n", [], id="acks-indented"
    ),
    pytest.param(
        "<!x\n```{include} a.md\n```\n",
        ["a.md"],
        id="lowercase-declaration",
    ),
    pytest.param(
        "<!doctype html\n```{include} a.md\n```\n",
        ["a.md"],
        id="lowercase-doctype",
    ),
    pytest.param(
        "<!doctype html>\n<span>\n```{include} a.md\n```\n",
        ["a.md"],
        id="lowercase-doctype-text",
    ),
    pytest.param(
        "````{note}\n<!x\n```{include} a.md\n```\n````\n",
        ["a.md"],
        id="lowercase-declaration-in-directive",
    ),
    pytest.param(
        "<!X\n```{include} b.md\n```\n>\n\n```{include} a.md\n```\n",
        ["a.md"],
        id="uppercase-declaration",
    ),
    pytest.param(
        "````{note} ```{include} b.md\n````\n",
        [],
        id="backtick-in-info",
    ),
    pytest.param(
        "````{note} ```{include} b.md\n```{include} a.md\n```\n",
        ["a.md"],
        id="backtick-in-info-then-include",
    ),
    pytest.param(
        "```text `x`\n```{include} a.md\n```\n",
        ["a.md"],
        id="backtick-in-code-info",
    ),
    pytest.param(
        "<div>\n\xa0\n```{include} b.md\n```\n", [], id="no-break-space-not-blank"
    ),
    pytest.param(
        "```text\nx\n```\xa0\n```{include} b.md\n```\n```\n",
        [],
        id="no-break-space-not-closer",
    ),
    pytest.param("<pre\xa0\n```{include} b.md\n```\n", [], id="no-break-space-tag"),
    pytest.param(
        "[a]: x(\n<span>\n```{include} a.md\n```\n",
        ["a.md"],
        id="definition-open-paren",
    ),
    pytest.param(
        "[a]: x)\n<span>\n```{include} a.md\n```\n",
        ["a.md"],
        id="definition-close-paren",
    ),
    pytest.param(
        "[a]: x" + "(" * 33 + ")" * 33 + "\n<span>\n```{include} a.md\n```\n",
        ["a.md"],
        id="definition-deep-parens",
    ),
    pytest.param(
        '[a]: x "a\\"\n<span>\n```{include} a.md\n```\n',
        ["a.md"],
        id="definition-escaped-double-quote",
    ),
    pytest.param(
        "[a]: x 'a\\'\n<span>\n```{include} a.md\n```\n",
        ["a.md"],
        id="definition-escaped-single-quote",
    ),
    pytest.param(
        "# T\n\n[a]: https://example.com/x_(y\n<span>\n```{include} a.md\n```\n",
        ["a.md"],
        id="definition-url-paren",
    ),
    pytest.param(
        "[a]: x\n<span>\n```{include} b.md\n```\n",
        [],
        id="definition-control",
    ),
    pytest.param(
        "```\xa0{include} a.md\n```\n",
        ["a.md"],
        id="info-no-break-space",
    ),
    pytest.param(
        "```\u3000{include} a.md\n```\n",
        ["a.md"],
        id="info-ideographic-space",
    ),
    pytest.param(
        "```\x1f{include} a.md\n```\n",
        ["a.md"],
        id="info-unit-separator",
    ),
    pytest.param(
        "````\xa0{note}\n```{include} a.md\n```\n````\n",
        ["a.md"],
        id="info-no-break-space-directive",
    ),
    pytest.param(
        "```{include} a.md\xa0\n```\n",
        ["a.md"],
        id="info-trailing-no-break-space",
    ),
    pytest.param(
        "[a]: x(y)\n   <br>\n ````\x1f{include} b.md\n", [], id="definition-parens"
    ),
    pytest.param(
        "[a]: x\\y\n   <span>\n ````\x1f{include} b.md\n",
        [],
        id="definition-backslash",
    ),
    pytest.param(
        ">\n<!x\n``` `\n## Sec\n  <br>\n```\xa0{include} b.md\xa0\n",
        [],
        id="no-html-after-quote",
    ),
]


@pytest.mark.parametrize(("page", "paths"), FENCES)
def test_a_fence_shown_in_a_code_block_is_no_include(
    script: ModuleType,
    page: str,
    paths: list[str],
) -> None:
    """A code block shows its fences; a parsed directive's body is read.

    :param script: the module under test.
    :param page: the text of the page.
    :param paths: what the page includes.
    """
    assert script.includes(page) == paths


def test_a_page_with_two_fences_stops_the_check(
    script: ModuleType,
    tmp_path: Path,
) -> None:
    """A page naming more than one file is an error, not a skipped page.

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
