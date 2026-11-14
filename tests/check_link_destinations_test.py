# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 4's `local-link-prefix` and `readme-absolute-link`.

Each runs `.github/scripts/check_link_destinations.py`, the copy
section 14 lists, in `language: python` with markdown-it-py pinned, so
their stanzas are read first: they split the files, and their pin is
the test group's and uv.lock's, the version these tests parse with. The
script is then asked the shapes each rule refuses and the ones it
admits, a file at a time, as pre-commit hands it the files.

The script is loaded by path, `.github/scripts` being no package.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tomllib
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import ROOT

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

SCRIPT = ROOT / ".github" / "scripts" / "check_link_destinations.py"
PREFIX = "local-link-prefix"
README = "readme-absolute-link"
PARSER = "markdown-it-py"


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs.

    :param monkeypatch: undoes the registration.
    :returns: the module.
    """
    spec = importlib.util.spec_from_file_location("check_link_destinations", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "check_link_destinations", module)
    spec.loader.exec_module(module)
    return module


def stanzas() -> dict[str, list[dict[str, Any]]]:
    """Read the link hooks out of this tree's gate, by id.

    :returns: each id's stanzas, with the url of each block under `repo`,
        so that a second stanza of one id is seen rather than replaced.
    """
    parsed = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text("utf-8"))
    found: dict[str, list[dict[str, Any]]] = {PREFIX: [], README: []}
    for block in parsed["repos"]:
        for hook in block["hooks"]:
            if hook["id"] in found:
                found[hook["id"]].append({**hook, "repo": block["repo"]})
    return found


def locked(name: str) -> tuple[str, list[str]]:
    """Read what `uv.lock` holds for a package of the test group.

    :param name: the package.
    :returns: the version it resolves, and the specifiers the project's
        own entry records for it in the test group.
    """
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    packages = {package["name"]: package for package in lock["package"]}
    root = packages[project["project"]["name"]]
    specifiers = [
        entry.get("specifier", "")
        for entry in root["metadata"]["requires-dev"]["test"]
        if entry["name"] == name
    ]
    version: str = packages[name]["version"]
    return version, specifiers


def test_the_hooks_run_the_copy_at_the_locked_parser() -> None:
    """Each stanza runs the copy at the pin of the test group and the lock."""
    hooks = stanzas()
    version, specifiers = locked(PARSER)
    pin = f"{PARSER}=={version}"
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert pin in pyproject["dependency-groups"]["test"]
    assert specifiers == [f"=={version}"]
    assert [len(hooks[PREFIX]), len(hooks[README])] == [1, 1]
    script = SCRIPT.relative_to(ROOT)
    for rule, flag in ((PREFIX, "--prefixed"), (README, "--absolute")):
        [hook] = hooks[rule]
        assert hook["repo"] == "local"
        assert hook["language"] == "python"
        assert hook["additional_dependencies"] == [pin]
        assert hook["entry"] == f"python {script} {flag} --"
    assert hooks[PREFIX][0]["exclude"] == hooks[README][0]["files"] == r"^README\.md$"


def refuses(script: ModuleType, text: str, *, absolute: bool) -> list[str]:
    """Ask the script which destinations of one file a rule refuses.

    :param script: the module.
    :param text: the file.
    :param absolute: `readme-absolute-link`'s rule, else `local-link-prefix`'s.
    :returns: the refused destinations, in file order.
    """
    return [destination for _, destination in script.refusals(text, absolute=absolute)]


# a fenced line that a pattern reading one line at a time takes for a link
FENCED = '```python\nok = hashes[row["fragment"]](preimage).hex() == row["digest"]\n```'


@pytest.mark.parametrize(
    ("text", "refused"),
    [
        pytest.param("[a](./CONTRIBUTING.md)", ["./CONTRIBUTING.md"], id="dot"),
        pytest.param("[a](../x/y.md#z)", ["../x/y.md#z"], id="dot-dot"),
        pytest.param("[a](SECURITY.md)", ["SECURITY.md"], id="bare"),
        pytest.param("![a](./logo.svg)", ["./logo.svg"], id="image"),
        pytest.param("[a]: ./RELEASING.md", ["./RELEASING.md"], id="definition"),
        pytest.param("[a](https://github.com/o/r/blob/main/x.md)", [], id="url"),
        pytest.param("[a](#a-heading)", [], id="anchor"),
        pytest.param("[a](mailto:a@example.org)", [], id="scheme"),
        pytest.param("[a]()", [], id="empty"),
        pytest.param("`[a](./x.md)`", [], id="code"),
        pytest.param(
            "[the [legacy] guide](./CONTRIBUTING.md)", ["./CONTRIBUTING.md"], id="pair"
        ),
        pytest.param("[the [legacy] guide](https://x.org/a.md)", [], id="pair-url"),
        pytest.param("[a [b [c]] d](./x.md)", ["./x.md"], id="pair-in-pair"),
        pytest.param("[a [b [c [d]]] e](./x.md)", ["./x.md"], id="pairs-deep"),
        pytest.param(r"[a \] b](./x.md)", ["./x.md"], id="escaped-close"),
        pytest.param(r"[a \[ b](./x.md)", ["./x.md"], id="escaped-open-inside"),
        pytest.param(r"\[a](./x.md)", [], id="escaped-open"),
        pytest.param(r"\![a](x.md)", ["x.md"], id="escaped-bang"),
        pytest.param(r"\\[a](x.md)", ["x.md"], id="escaped-backslash"),
        pytest.param(
            r"\\[the [legacy] guide](<x.md>)", ["x.md"], id="escaped-backslash-pair"
        ),
        pytest.param(r"\\\[a](x.md)", [], id="escaped-backslash-then-open"),
        pytest.param(
            "[rules](<https://github.com/btclib-org/ai-agents-process/blob/main/CONTRIBUTING.md>)",
            [],
            id="angle-url",
        ),
        pytest.param("[a](<./CONTRIBUTING.md>)", ["./CONTRIBUTING.md"], id="angle-dot"),
        pytest.param("[a](<CONTRIBUTING.md>)", ["CONTRIBUTING.md"], id="angle-bare"),
        pytest.param("[a](<#a-heading>)", [], id="angle-anchor"),
        pytest.param("[a](<>)", [], id="angle-empty"),
        pytest.param("[a](<x y.md>)", ["x y.md"], id="angle-space"),
        pytest.param('[a](./x.md "A title")', ["./x.md"], id="title"),
        pytest.param("[a](x.md 'A title')", ["x.md"], id="title-single"),
        pytest.param("[a](x.md (A title))", ["x.md"], id="title-parenthesis"),
        pytest.param('[a](<https://x.org/a.md> "A title")', [], id="angle-title"),
        pytest.param("[a]( ./x.md)", ["./x.md"], id="space"),
        pytest.param("[a](\t./x.md)", ["./x.md"], id="tab"),
        pytest.param("[a](\nx.md)", ["x.md"], id="break-before"),
        pytest.param("[a\nb](x.md)", ["x.md"], id="label-over-lines"),
        pytest.param("[a\n\nb](x.md)", [], id="label-over-paragraphs"),
        pytest.param("[a] (x.md)", [], id="space-before-parenthesis"),
        pytest.param("[a](x(1).md)", ["x(1).md"], id="parentheses"),
        pytest.param("[a](x(1.md)", [], id="parenthesis-open"),
        pytest.param(
            "[![b](https://x.org/b.svg)](./x.md)", ["./x.md"], id="badge-link"
        ),
        pytest.param("[![b](./b.svg)](https://x.org/a)", ["./b.svg"], id="badge-image"),
        pytest.param("[![b](https://x.org/b.svg)](https://x.org/a)", [], id="badge"),
        pytest.param("`[![b](./b.svg)](./x.md)`", [], id="badge-code"),
        pytest.param("[x [a](./b) y](c)", ["./b"], id="link-in-label"),
        pytest.param("![x [a](./b) y](c)", ["c"], id="link-in-image"),
        pytest.param("> ```\n> code\n\n[a](x.md)", ["x.md"], id="after-a-quote"),
        pytest.param("- ```\n  [a](x.md)\n  ```", [], id="fence-in-a-list"),
        pytest.param(
            "[outer [inner][ref]](x.md)\n\n[ref]: https://x.org",
            [],
            id="reference-in-label",
        ),
        pytest.param("[a](x\u00a0y.md)", ["x\u00a0y.md"], id="no-break-space"),
        pytest.param("`hello\n[a]: x.md\n`", [], id="definition-in-code"),
        pytest.param("[a\nb]: x.md", ["x.md"], id="definition-label-over-lines"),
        pytest.param(
            '[a]: https://x.org "[b](y.md)"\n\n[a]', [], id="definition-title"
        ),
        pytest.param("[a](https&#58;//x.org)", [], id="character-reference"),
        pytest.param("[a](&num;heading)", [], id="character-reference-anchor"),
        pytest.param('<a href="x.md">a</a>', [], id="html"),
        pytest.param("Text[^1].\n\n[^1]: Note.", [], id="footnote-one-word"),
        pytest.param("> [^n]: Note.", [], id="footnote-quoted"),
        pytest.param("- [^n]: Note.", [], id="footnote-listed"),
        pytest.param("[^n](x.md)", ["x.md"], id="caret-label-link"),
        pytest.param("[outer\n[^n]](x.md)", ["x.md"], id="caret-inside-label"),
        pytest.param("![outer\n[^n]](x.md)", ["x.md"], id="caret-inside-image"),
        pytest.param(
            "[a]: https://example.org\n[a]: x.md", ["x.md"], id="definition-repeated"
        ),
        pytest.param("[z](z.md) [a](a.md)", ["z.md", "a.md"], id="order-in-a-line"),
        pytest.param("> `a\n>\n> [a](x.md)\n> `", ["x.md"], id="span-over-a-quote"),
        pytest.param("[a](" * 6000, [], id="unclosed-many"),
        pytest.param("<https://x.org/a>\nand [a](x.md)", ["x.md"], id="autolink"),
        pytest.param("[a]: <./x.md>", ["./x.md"], id="angle-definition"),
        pytest.param(
            '[a]: <https://x.org/a.md> "A title"', [], id="angle-definition-url"
        ),
        pytest.param(r"[a \] b]: ./x.md", ["./x.md"], id="escaped-definition"),
        pytest.param("[a]:\n  ./x.md", ["./x.md"], id="definition-next-line"),
        pytest.param("[a][ref] and [ref]", [], id="reference"),
        pytest.param(
            "[a][ref] and [ref]\n\n[ref]: ./r.md",
            ["./r.md", "./r.md", "./r.md"],
            id="reference-defined",
        ),
        pytest.param("[^note]: A footnote.", [], id="footnote"),
        pytest.param("[^note]: See [a](x.md).", ["x.md"], id="footnote-link"),
        pytest.param("`code [the [legacy] guide](x.md)`", [], id="code-span"),
        pytest.param("``[a](x.md)``", [], id="code-span-double"),
        pytest.param("`` ` [a](x.md) ``", [], id="code-span-backtick"),
        pytest.param("`a [b](x.md)", ["x.md"], id="backtick-unmatched"),
        pytest.param(FENCED, [], id="fence"),
        pytest.param("  ```python\n  [a](x.md)\n  ```", [], id="fence-indented"),
        pytest.param("> ```\n> [a](x.md)\n> ```", [], id="fence-quoted"),
        pytest.param("~~~\n[a](x.md)\n~~~", [], id="fence-tilde"),
        pytest.param("````\n```\n[a](x.md)\n````", [], id="fence-longer"),
        pytest.param("```\n[a](x.md)", [], id="fence-unclosed"),
        pytest.param("```\n```\n[a](x.md)", ["x.md"], id="fence-closed"),
        pytest.param("``` a`b\n[a](x.md)", ["x.md"], id="fence-not"),
        pytest.param("<!-- [a](x.md) -->", [], id="comment"),
        pytest.param("<!--\n[a](x.md)\n-->\n[b](y.md)", ["y.md"], id="comment-block"),
        pytest.param("a <!-- [a](x.md) --> b", [], id="comment-inline"),
        pytest.param("> [a](x.md)", ["x.md"], id="quote"),
        pytest.param("| a | [b](x.md) |\n|---|---|", ["x.md"], id="table"),
    ],
)
def test_the_readme_rule_refuses_every_local_destination(
    script: ModuleType, text: str, refused: list[str]
) -> None:
    """A local destination is refused, prefixed or not; nothing else is.

    A definition is refused whether a link uses it or not, and each link
    using it is refused too; a reference to no definition is no link.

    :param script: the module.
    :param text: a root `README.md`.
    :param refused: the destinations `readme-absolute-link` refuses.
    """
    assert refuses(script, text, absolute=True) == refused


@pytest.mark.parametrize(
    ("text", "refused"),
    [
        pytest.param("[a](./x.md)", [], id="dot"),
        pytest.param("[a](../x.md)", [], id="dot-dot"),
        pytest.param("[a](x.md)", ["x.md"], id="bare"),
        pytest.param("[a](<./x.md>)", [], id="angle-dot"),
        pytest.param("[a](<../x.md>)", [], id="angle-dot-dot"),
        pytest.param("[a](<x.md>)", ["x.md"], id="angle-bare"),
        pytest.param("[the [legacy] guide](./x.md)", [], id="pair-dot"),
        pytest.param("[the [legacy] guide](x.md)", ["x.md"], id="pair-bare"),
        pytest.param("[a]( x.md)", ["x.md"], id="space-bare"),
        pytest.param(r"\![a](x.md)", ["x.md"], id="escaped-bang"),
        pytest.param(r"\![a](./x.md)", [], id="escaped-bang-dot"),
        pytest.param(r"\\[a](x.md)", ["x.md"], id="escaped-backslash"),
        pytest.param("[a]: x.md", ["x.md"], id="definition-bare"),
        pytest.param("[a]: ./x.md", [], id="definition-dot"),
        pytest.param("[a](//host/x.md)", ["//host/x.md"], id="network-path"),
        pytest.param(FENCED, [], id="fence"),
        pytest.param("[^note]: A footnote.", [], id="footnote"),
    ],
)
def test_the_prefix_rule_refuses_a_local_destination_without_a_prefix(
    script: ModuleType, text: str, refused: list[str]
) -> None:
    """A local destination is refused where it begins neither ./ nor ../.

    :param script: the module.
    :param text: a markdown file other than the root `README.md`.
    :param refused: the destinations `local-link-prefix` refuses.
    """
    assert refuses(script, text, absolute=False) == refused


def test_a_refusal_names_the_file_and_the_line(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Each refusal is printed at the line its link opens on.

    :param script: the module.
    :param tmp_path: holds the files.
    :param capsys: reads what the script prints.
    """
    page = tmp_path / "page.md"
    page.write_text("# A page\n\n[a\nb](\nx.md) and [c](y.md)\n", encoding="utf-8")
    clean = tmp_path / "clean.md"
    clean.write_text("[c](./y.md)\n", encoding="utf-8")
    assert script.main(["--prefixed", str(page), str(clean)]) == 1
    why = "is local and begins neither ./ nor ../"
    assert capsys.readouterr().out == (
        f"{page}:3: the link destination 'x.md' {why}\n"
        f"{page}:5: the link destination 'y.md' {why}\n"
    )
    assert script.main(["--prefixed", str(clean)]) == 0
    assert script.main(["--absolute", str(clean)]) == 1
    assert capsys.readouterr().out == (
        f"{clean}:1: the link destination './y.md' is local, where the page is"
        " read on the package index\n"
    )


@pytest.mark.parametrize(
    ("text", "found"),
    [
        pytest.param("[^n]: [a](x.md)", [(1, "x.md")], id="link"),
        pytest.param("[^n]: ![a](x.md)", [(1, "x.md")], id="image"),
        pytest.param("[^n]: [a](x.md).", [(1, "x.md")], id="link-then-text"),
        pytest.param("[^n]: [a](<x.md>)", [(1, "x.md")], id="angle"),
        pytest.param("> [^n]: [a](x.md)", [(1, "x.md")], id="quoted"),
        pytest.param("- [^n]: [a](x.md)", [(1, "x.md")], id="listed"),
        pytest.param("[^n]:\n    [a](x.md)", [(2, "x.md")], id="continued"),
        pytest.param("Text[^n].\n\n[^n]: Note.", [], id="prose"),
        pytest.param(
            "[^note]: Note.\n[ref]: x.md\n\n[text][ref]",
            [(2, "x.md"), (4, "x.md")],
            id="definition-after",
        ),
        pytest.param(
            "> [^note]: Note.\n> [ref]: x.md\n\n[text][ref]",
            [(2, "x.md"), (4, "x.md")],
            id="definition-after-quoted",
        ),
        pytest.param(
            "- [^note]: Note.\n  [ref]: x.md\n\n[text][ref]",
            [(2, "x.md"), (4, "x.md")],
            id="definition-after-listed",
        ),
        pytest.param(
            "[a]: ./a.md\n[^n]: Note.\n[b]: b.md",
            [(1, "./a.md"), (3, "b.md")],
            id="between-definitions",
        ),
        pytest.param("[^caret]: x.md\n\n[text][^caret]", [(3, "x.md")], id="used"),
        pytest.param("> [^c]: x.md\n\n[text][^c]", [(3, "x.md")], id="used-quoted"),
        pytest.param("[^n]: notes.md\n\nSee[^n].", [], id="path-like-body"),
        pytest.param("[^n]: notes.md\n\nSee[^n][].", [], id="path-like-collapsed"),
        pytest.param(
            "[^n]: Note.\n[^n]: [a](y.md)", [(2, "y.md")], id="repeated-label"
        ),
    ],
)
def test_a_link_in_a_footnote_is_read_as_any_other(
    script: ModuleType, text: str, found: list[tuple[int, str]]
) -> None:
    """A footnote's label is no destination, and its body is markdown.

    A use naming the label alone is the footnote's reference, and a link
    naming it as its reference is a link to the body as a destination.

    :param script: the module.
    :param text: a file holding a footnote.
    :param found: each destination and the line it is on.
    """
    assert list(script.destinations(text)) == found


@pytest.mark.parametrize(
    ("text", "destination"),
    [
        pytest.param("[a](%2E%2Fx.md)", ".%2Fx.md", id="escaped-prefix"),
        pytest.param("[a](%23head)", "%23head", id="escaped-anchor"),
    ],
)
def test_an_escaped_reserved_character_stays_escaped(
    script: ModuleType, text: str, destination: str
) -> None:
    """`%2F` is no `/` and `%23` no `#`, so each rule refuses these.

    :param script: the module.
    :param text: a file holding the link.
    :param destination: what `normalizeLinkText` gives for it.
    """
    assert refuses(script, text, absolute=False) == [destination]
    assert refuses(script, text, absolute=True) == [destination]


def test_a_link_opens_on_its_own_line(script: ModuleType) -> None:
    """A line break inside an earlier link's label moves the next one down.

    :param script: the module.
    """
    text = "[outer\n[^n](x.md)](https://example.org)\n\n[a\nb](\nc.md) [d](d.md)"
    assert list(script.destinations(text)) == [
        (2, "x.md"),
        (4, "c.md"),
        (6, "d.md"),
    ]


def test_a_file_named_with_a_dash_is_read_after_the_terminator(
    script: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The entry's `--` keeps a file named `-i.md` from reading as an option.

    :param script: the module.
    :param tmp_path: holds the file.
    :param monkeypatch: runs from that directory.
    :param capsys: reads what the script prints.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "-i.md").write_text("[a](x.md)\n", encoding="utf-8")
    assert script.main(["--prefixed", "--", "-i.md"]) == 1
    assert capsys.readouterr().out == (
        "-i.md:1: the link destination 'x.md' is local and begins neither ./ nor ../\n"
    )
    (tmp_path / "-i.md").write_text("[a](./x.md)\n", encoding="utf-8")
    assert script.main(["--prefixed", "--", "-i.md"]) == 0


def test_a_missing_file_is_an_argument_error(
    script: ModuleType, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A file that is not there exits 2 with a message, not a traceback.

    :param script: the module.
    :param tmp_path: where the file is not.
    :param capsys: reads what the script prints.
    """
    missing = tmp_path / "missing.md"
    with pytest.raises(SystemExit) as raised:
        script.main(["--absolute", "--", str(missing)])
    assert raised.value.code == 2  # noqa: PLR2004
    assert f"{missing} is not a file" in capsys.readouterr().err


def test_a_file_over_the_limit_is_refused_unread(
    script: ModuleType,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A file past `LIMIT` is a refusal of its own, and nothing is parsed.

    :param script: the module.
    :param tmp_path: holds the file.
    :param capsys: reads what the script prints.
    :param monkeypatch: lowers the limit.
    """
    page = tmp_path / "page.md"
    page.write_text("[a](./x.md)\n", encoding="utf-8")
    monkeypatch.setattr(script, "LIMIT", 4)
    assert script.main(["--prefixed", str(page)]) == 1
    assert capsys.readouterr().out == (
        f"{page}: larger than 4 bytes, which this does not read\n"
    )


def test_the_script_runs_as_pre_commit_runs_it(tmp_path: Path) -> None:
    """The hook's entry runs the file with a rule and the files after it.

    :param tmp_path: holds the file.
    """
    page = tmp_path / "README.md"
    page.write_text("[a](x.md)\n", encoding="utf-8")
    ran = subprocess.run(
        [sys.executable, str(SCRIPT), "--absolute", "--", str(page)],
        capture_output=True,
        check=False,
        encoding="utf-8",
    )
    assert ran.returncode == 1
    assert ran.stdout == (
        f"{page}:1: the link destination 'x.md' is local, where the page is"
        " read on the package index\n"
    )
    refused = subprocess.run(
        [sys.executable, str(SCRIPT), str(page)], capture_output=True, check=False
    )
    assert refused.returncode == 2  # noqa: PLR2004
