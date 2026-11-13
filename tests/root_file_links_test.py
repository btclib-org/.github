# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 14's verbatim part of `docs/source/conf.py`, `RootFileLinks`.

`SOURCE` holds the part below the line `START`. Every tree that tracks
`CONF` carries it byte for byte. It is a part of a file and not a file,
so `verbatim_test.py`, which compares copies by path, does not reach it:
section 14's *A part is held against this file* is the shape asked here.

The part reads a page's include fences as `check_included_links.py`
does, since that script refuses what the part leaves at `BLOB`: the two
fence readers are the same code, and are run on the script's own cases.

The transform runs on a hand-made doctree, its `conf.py` a copy of
`SOURCE` in a stand-in tree with root files, shims and pages of its own.
"""

from __future__ import annotations

import ast
import importlib
import importlib.util
import itertools
import re
import shutil
import timeit
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from . import ROOT, tracked
from .check_included_links_test import FENCES

# Where this repository keeps the part, below the names a tree sets itself.
SOURCE = "shared/root_file_links.py"

# Where section 2 puts a tree's sphinx configuration.
CONF = "docs/source/conf.py"

# The line of `SOURCE` that the part follows, and that no copy carries.
START = b"# section 14's verbatim part of docs/source/conf.py starts below this line\n"

# How every tree's `setup` registers the transform today.
REGISTERED = b"app.add_post_transform(RootFileLinks)"

# The docs check whose fence reading the part shares.
SCRIPT = ".github/scripts/check_included_links.py"

# The names, top level in both files, that read a page's include fences.
READER = (
    "FENCE",
    "INCLUDE",
    "DIRECTIVE",
    "CONTAINER",
    "ITEM",
    "HTML_BLOCKS",
    "HTML_NAMED",
    "_LOW_SPACE",
    "_HIGH_SPACE",
    "_NAME",
    "_NAMES",
    "_QUOTED",
    "_UNQUOTED",
    "_TO_EQUALS",
    "_TO_END",
    "HTML_TAG",
    "BLANK",
    "HEADING",
    "UNDERLINE",
    "LABEL",
    "UNSAFE",
    "IMAGE",
    "PARSED",
    "VERSIONS",
    "PLACED",
    "BARE",
    "UNARGUED",
    "QUOTES",
    "ATTRIBUTION",
    "fence_end",
    "opens_html",
    "html_block",
    "interrupts",
    "destination",
    "title",
    "definition",
    "top_line",
    "options",
    "attribution",
    "front_matter",
    "markdown_start",
    "dedent",
    "ends_containers",
    "opens_container",
    "inner_line",
    "fenced",
    "Reading",
    "read_page",
    "includes",
)


def part(source: bytes) -> bytes:
    """Read the part out of the source.

    :param source: the bytes of `SOURCE`.
    :returns: everything after `START`.
    :raises LookupError: where the source holds no `START` line.
    """
    at = source.find(START)
    if at < 0:
        msg = f"{SOURCE} holds no line {START!r}"
        raise LookupError(msg)
    return source[at + len(START) :]


def test_the_part_is_what_follows_its_start_line() -> None:
    """The line itself is out, and a source without it raises."""
    assert part(b"ROOT = 1\n" + START + b"INCLUDE = 2\n") == b"INCLUDE = 2\n"
    with pytest.raises(LookupError, match="holds no line"):
        part(b"INCLUDE = 2\n")


def test_the_source_holds_the_transform() -> None:
    """The part read off `SOURCE` holds the class: the line is above it."""
    assert b"\nclass RootFileLinks(SphinxPostTransform):\n" in part(
        (ROOT / SOURCE).read_bytes()
    )


def reader(path: Path) -> dict[str, ast.stmt]:
    """Read the statements of a file that define `READER`, in file order.

    :param path: the file.
    :returns: each name of `READER` the file defines at top level,
        against the statement that defines it.
    """
    out: dict[str, ast.stmt] = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            name = node.name
        elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
        else:
            continue
        if name in READER:
            out[name] = node
    return out


def test_the_part_reads_fences_with_the_script_s_code() -> None:
    """Both files define every name of `READER`, and define it alike.

    Compared as syntax trees, so a comment may differ and code may not.
    """
    ours, theirs = reader(ROOT / SOURCE), reader(ROOT / SCRIPT)
    assert tuple(ours) == READER
    assert [ast.dump(node) for node in ours.values()] == [
        ast.dump(node) for node in theirs.values()
    ]


_REPOSITORY = "https://github.com/btclib-org/stand-in"
_BLOB = f"{_REPOSITORY}/blob/main/"

# the stand-in's pages, and what each holds: two shims, a page other than
# a shim including a root file, and pages that include nothing
_PAGES = {
    "readme_link.md": "```{include} ../../README.md\n```\n",
    "security_link.md": "```{include} ../../SECURITY.md\n```\n",
    "changes.md": "# Changes\n\n```{include} ../../CHANGELOG.md\n```\n",
    "index.md": "# Stand-in\n",
    "guide.md": "# Guide\n",
    "api.rst": "API\n===\n",
}


@pytest.fixture(scope="module")
def conf(tmp_path_factory: pytest.TempPathFactory) -> ModuleType:
    """Return `SOURCE`, executed as the `conf.py` of a stand-in tree.

    :param tmp_path_factory: where the stand-in is written.
    :returns: the module.
    """
    root = tmp_path_factory.mktemp("stand-in")
    (root / "pyproject.toml").write_text(
        f'[project]\nname = "stand-in"\n[project.urls]\nrepository = "{_REPOSITORY}"\n',
        encoding="utf-8",
    )
    for name in ("README.md", "SECURITY.md", "CHANGELOG.md", "LICENSE"):
        (root / name).write_text(f"{name}\n", encoding="utf-8")
    source = root / "docs" / "source"
    source.mkdir(parents=True)
    for name, text in _PAGES.items():
        (source / name).write_text(text, encoding="utf-8")
    shutil.copyfile(ROOT / SOURCE, source / "conf.py")
    spec = importlib.util.spec_from_file_location("stand_in_conf", source / "conf.py")
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("page", "paths"), FENCES)
def test_the_part_finds_the_includes_the_script_finds(
    conf: ModuleType, page: str, paths: list[str]
) -> None:
    """The part's own `includes`, run on each of the script's cases.

    :param conf: the part, as a stand-in's `conf.py`.
    :param page: the text of the page.
    :param paths: what the script reads as its include fences.
    """
    assert conf.includes(page) == paths


def test_a_page_other_than_a_shim_renders_what_it_includes(conf: ModuleType) -> None:
    """Every page's include is read, a `*_link.md` shim's or not.

    :param conf: the part, as a stand-in's `conf.py`.
    """
    assert conf.INCLUDED == {
        "CHANGELOG.md": "changes",
        "README.md": "readme_link",
        "SECURITY.md": "security_link",
    }


def test_a_page_with_two_include_fences_is_refused(
    conf: ModuleType, tmp_path: Path
) -> None:
    """A relative link on it would have two files to start from.

    :param conf: the part, as a stand-in's `conf.py`.
    :param tmp_path: where the page is written.
    """
    page = tmp_path / "both.md"
    page.write_text(
        _PAGES["readme_link.md"] + _PAGES["security_link.md"], encoding="utf-8"
    )
    with pytest.raises(ValueError, match="2 include fences"):
        conf.included(page)


def _run(conf: ModuleType, node: Any, docname: str) -> Any:  # noqa: ANN401
    """Run `RootFileLinks` on a page holding `node`; return its replacement.

    :param conf: the part, as a stand-in's `conf.py`.
    :param node: the link, as myst makes it.
    :param docname: the page the link is on.
    :returns: the node in the link's place once the transform has run.
    """
    source = conf.ROOT / "docs" / "source"
    paths = {Path(name).stem: str(source / name) for name in _PAGES}
    document = importlib.import_module("docutils.utils").new_document("<test>")
    document.settings.env = SimpleNamespace(
        docname=docname,
        all_docs=dict.fromkeys(paths, 0.0),
        found_docs=set(paths),
        doc2path=paths.__getitem__,
    )
    paragraph = conf.nodes.paragraph()
    paragraph += node
    document += paragraph
    conf.RootFileLinks(document).run()
    return paragraph[0]


def _blob(conf: ModuleType, path: str) -> Any:  # noqa: ANN401
    """Return the reference myst makes from a link to `BLOB` and `path`.

    :param conf: the part, as a stand-in's `conf.py`.
    :param path: what follows `BLOB`.
    :returns: the reference.
    """
    assert conf.BLOB == _BLOB
    return conf.nodes.reference("", "it", refuri=f"{_BLOB}{path}")


def _relative(conf: ModuleType, target: str, docname: str) -> Any:  # noqa: ANN401
    """Return the xref myst makes from a relative link it cannot resolve.

    :param conf: the part, as a stand-in's `conf.py`.
    :param target: the link's destination.
    :param docname: the page the link is on.
    :returns: the xref.
    """
    return conf.pending_xref(
        "",
        conf.nodes.inline("", "it"),
        reftype="myst",
        refdomain=None,
        reftarget=target,
        refdoc=docname,
    )


def _page(conf: ModuleType, node: Any) -> tuple[str, str | None]:  # noqa: ANN401
    """Return the page and the anchor a link resolved to.

    :param conf: the part, as a stand-in's `conf.py`.
    :param node: what `_run` returned.
    :returns: the docname and the anchor.
    """
    assert isinstance(node, conf.pending_xref)
    assert node["refdomain"] == "doc"
    return node["reftarget"], node["reftargetid"]


@pytest.mark.parametrize(
    ("path", "page"),
    [
        pytest.param("docs/source/guide.md", "guide", id="md"),
        pytest.param("docs/source/api.rst", "api", id="rst"),
    ],
)
def test_a_link_to_a_page_no_shim_includes_is_that_page(
    conf: ModuleType, path: str, page: str
) -> None:
    """A `BLOB` link and a relative one in an included file alike.

    :param conf: the part, as a stand-in's `conf.py`.
    :param path: the page's file, from the root of the tree.
    :param page: its docname.
    """
    assert _page(conf, _run(conf, _blob(conf, path), "index")) == (page, None)
    relative = _relative(conf, f"./{path}", "readme_link")
    assert _page(conf, _run(conf, relative, "readme_link")) == (page, None)


@pytest.mark.parametrize(
    ("suffix", "anchor"),
    [
        pytest.param("?plain=1", None, id="query"),
        pytest.param("?plain=1#reporting", "reporting", id="query-anchor"),
    ],
)
def test_a_query_is_dropped(conf: ModuleType, suffix: str, anchor: str | None) -> None:
    """`?plain=1` is GitHub's, and the page is reached without it.

    :param conf: the part, as a stand-in's `conf.py`.
    :param suffix: what follows the file's path.
    :param anchor: what the link keeps of it.
    """
    blob = _run(conf, _blob(conf, f"SECURITY.md{suffix}"), "index")
    assert _page(conf, blob) == ("security_link", anchor)
    included = _relative(conf, f"./SECURITY.md{suffix}", "readme_link")
    assert _page(conf, _run(conf, included, "readme_link")) == ("security_link", anchor)
    # on a page including nothing, the link is relative to the page
    plain = _relative(conf, f"../../SECURITY.md{suffix}", "index")
    assert _page(conf, _run(conf, plain, "index")) == ("security_link", anchor)


def test_a_relative_link_to_a_file_no_page_renders_is_at_blob(conf: ModuleType) -> None:
    """`LICENSE`, included by no page, stays on GitHub, query dropped.

    :param conf: the part, as a stand-in's `conf.py`.
    """
    node = _run(
        conf, _relative(conf, "./LICENSE?plain=1", "readme_link"), "readme_link"
    )
    assert isinstance(node, conf.nodes.reference)
    assert node["refuri"] == f"{_BLOB}LICENSE"


# markdown-it-py's own pattern for a line opening an html block of type
# 7, as its `markdown_it/common/html_re.py` spells it at 4.2.0, the
# version the trees lock, behind the indent the part allows. Copied under
# the MIT licence, whose permission notice is this repository's LICENSE
# word for word: Copyright (c) 2020 ExecutableBookProject, of
# markdown-it-py, and Copyright (c) 2014 Vitaly Puzrin, Alex Kocharin, of
# markdown-it, which it ports.
_ATTRIBUTE = (
    "(?:\\s+[a-zA-Z_:][a-zA-Z0-9:._-]*"
    "(?:\\s*=\\s*(?:[^\"'=<>`\\x00-\\x20]+|'[^']*'|\"[^\"]*\"))?)"
)
_OPEN_TAG = "<[A-Za-z][A-Za-z0-9\\-]*" + _ATTRIBUTE + "*\\s*\\/?>"
_CLOSE_TAG = "<\\/[A-Za-z][A-Za-z0-9\\-]*\\s*>"
_MARKDOWN_IT = re.compile("^ {0,3}(?:" + _OPEN_TAG + "|" + _CLOSE_TAG + ")\\s*$")

# lines in the shapes of an html block's and of raw html's tags, alone
# on the line or not: names, attributes of each kind, the indent, and
# what makes a line no tag
_TAGS = (
    "<p>",
    "</p>",
    "<P>",
    "</Section >",
    "<h2-x>",
    "<my-tag9>",
    "<x/>",
    "<x />",
    "<img src=pic.png/>",
    '<a href="y">',
    "<a href='y'>",
    "<a href=y>",
    "<a href = y >",
    "<a href=\"y\" title='z' hidden>",
    '<a b:c="1" _d=2 e.f-g>',
    "<input disabled\tchecked>",
    "   <p>",
    "    <p>",
    " </p>  ",
    "<p>\t",
    "<p><span>",
    "<p>text",
    "<p></p>",
    "text <p>",
    "<p",
    "<p class",
    '<p class="x',
    "< p>",
    "<9p>",
    "</p class=x>",
    "</p/>",
    "<a b=c=d>",
    "<a b=c<d>",
    "<a b=`c`>",
    "<a b='c\"d'>",
    '<a b="c\'d">',
    "<a b='c'd>",
    "<a *b>",
    "<a b!>",
    "<a b=>",
    "<a =b>",
    "<a  />",
    "<a/ >",
)

# a character of each class the two patterns tell apart, and a line that
# leaves `_MARKDOWN_IT` in each of its states other than refusal and
# match: in the indent, a tag, a name, a value, the whitespace after a
# value, and a value of whitespace above \x20
_CHARACTERS = "\x00\t\n !\"'-./:<=>a\xa0"
_PREFIXES = (
    "",
    " ",
    "  ",
    "   ",
    "<",
    "</",
    "</a",
    "</a ",
    "<a",
    "<a ",
    "<a/",
    "<a>",
    "<a b",
    "<a b ",
    "<a b=",
    "<a b=x",
    '<a b="x',
    "<a b='x",
    "<a b='x'",
    "<a b=\xa0",
    "<a b=\xa0 ",
    "<a b=x\xa0",
    "<a b=x\xa0c",
    "<a b=x\xa0c\xa0",
)

# the longest word `_CHARACTERS` makes after a prefix, and what may end
# the line after it: nothing, a tag's end, or a value and a tag's end
_WORD = 3
_ENDS = ("", ">", "=a>")

# CodeQL's input with `_SHORT` attributes, and with `_LONGER` times as
# many: a linear `HTML_TAG` takes about `_LONGER` times as long on the
# second, and at most `_BOUND` times as long passes
_SHORT = 64
_LONGER = 8
_BOUND = 4 * _LONGER


@pytest.mark.parametrize("line", _TAGS)
def test_html_tag_reads_tags_as_markdown_it_does(conf: ModuleType, line: str) -> None:
    """The part opens an html block of type 7 where markdown-it-py does.

    :param conf: the part, as a stand-in's `conf.py`.
    :param line: a line of `_TAGS`.
    """
    assert bool(conf.HTML_TAG.match(line)) == bool(_MARKDOWN_IT.match(line))


def test_html_tag_matches_every_short_line_markdown_it_matches(
    conf: ModuleType,
) -> None:
    """Every word of `_CHARACTERS` after each prefix, then each end.

    :param conf: the part, as a stand-in's `conf.py`.
    """
    lines = [
        prefix + "".join(word) + end
        for prefix in _PREFIXES
        for size in range(_WORD + 1)
        for word in itertools.product(_CHARACTERS, repeat=size)
        for end in _ENDS
    ]
    assert any(map(_MARKDOWN_IT.match, lines))
    differ = [
        line
        for line in lines
        if bool(conf.HTML_TAG.match(line)) != bool(_MARKDOWN_IT.match(line))
    ]
    assert not differ


def test_html_tag_refuses_codeql_s_input_in_linear_time(conf: ModuleType) -> None:
    """CodeQL's py/redos input, with a no-break space after each value.

    markdown-it-py's pattern takes twice as long for each attribute it
    is given: refusing the short line takes it longer than this suite's
    timeout.

    :param conf: the part, as a stand-in's `conf.py`.
    """

    def best(count: int) -> float:
        line = "<a :=" + "!\xa0 :=" * count + "!\x00"
        return min(
            timeit.repeat(lambda: conf.HTML_TAG.match(line), number=20, repeat=5)
        )

    assert best(_SHORT * _LONGER) / best(_SHORT) < _BOUND


def test_a_copy_differing_by_a_byte_is_not_the_part() -> None:
    """A planted copy holds the part; with one byte changed, it does not.

    The planted copy has a tree's own lines around the part, as a
    `conf.py` does.
    """
    shared = part((ROOT / SOURCE).read_bytes())
    assert shared in b"ROOT = 1\n\n\n" + shared + b"\n\ndef setup(): ...\n"
    changed = shared.replace(b"default_priority = 5", b"default_priority = 6")
    assert changed != shared
    assert shared not in b"ROOT = 1\n\n\n" + changed


def test_a_conf_py_carries_section_14_s_root_file_links(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """A tree's `conf.py` holds the part byte for byte, and registers it.

    A tree that tracks no `conf.py` owes nothing here and is skipped.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    if not tracked(root, CONF):
        pytest.skip(f"{repository} tracks no {CONF}")
    conf = (root / CONF).read_bytes()
    assert part((ROOT / SOURCE).read_bytes()) in conf, (
        f"{CONF} does not carry, byte for byte, the part of btclib-org/.github's"
        f" {SOURCE} below its line {START.decode().strip()!r}"
    )
    assert REGISTERED in conf, f"{CONF} carries the part and no {REGISTERED.decode()}"
