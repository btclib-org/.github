# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

r"""A `REPOSITORY.md` keeps each recorded answer out of its `shell` fences.

Section 9's *A placeholder is bare, and last* puts a comment above the
fence as prose, and a recorded answer in a fence of its own below its
command's. A `#` line inside a `shell` fence is either, and a reader
pasting the fence into an interactive `zsh` runs it as a command. So a
`#` line there is refused, wherever it is indented. A heredoc's body is
its command's input and no command, so a `#` line there stays.

A `json` fence holds one JSON object or array, a document a JSON parser
reads whole, and a fence that does not parse as one is refused.

This tree's own file is asked without the network, so `lint.yml`'s
required job refuses a regression here. Every tree's is asked once per
repository, and `BACKLOG` names the trees the port has not reached.

What this does not read: a fence opened on a list marker's line or in
a block quote, a delimiter such as `<<\EOF`, `<<''` or `<<E"OF"`, and
a second heredoc on one command line.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, NamedTuple

import pytest

from . import ROOT, by_hand

if TYPE_CHECKING:
    from pathlib import Path

SETTINGS = "REPOSITORY.md"
"""The root file that records each setting with its read-back."""

FENCE = re.compile(r"^(?P<indent> *)(?P<marks>`{3,}|~{3,})(?P<info>.*)$")
"""A fence line, at any indent a list item gives it.

What follows the marks is the info string, whose first word is the
language; a line whose info string is empty can also close a fence.
"""


def nested(depth: int) -> str:
    """Return a pattern for one character of an arithmetic expression.

    :param depth: how many levels of parentheses it may open inside.
    :returns: the pattern, a character other than a parenthesis or a
        parenthesized run of them.
    """
    pattern = "[^()]"
    for _ in range(depth):
        pattern = rf"(?:[^()]|\({pattern}*\))"
    return pattern


DEPTH = 8
"""How deep the parentheses inside one arithmetic expression may go."""

HEREDOC = re.compile(
    r"'[^']*'"
    r'|"(?:[^"\\]|\\.)*"'
    r"|(?<!\S)#.*"
    rf"|\$?\(\({nested(DEPTH)}*\)\)"
    r"|\$\[[^]]*\]"
    r"|(?<!<)<<(?P<dash>-?)[ \t]*"
    r"(?:'(?P<single>[^']+)'"
    r'|"(?P<double>[^"]+)"'
    r"""|(?P<bare>[^\s'"<>|;&()\\]+))"""
)
"""A heredoc's opening, and the word that ends its body.

A quoted argument, a backslash escaping a quote inside double quotes,
a trailing comment and an arithmetic expression, `$((...))`, `((...))`
or `$[...]`, nested up to `DEPTH`, are matched whole, so a `<<` inside
one opens nothing. The lookbehind keeps a here-string's `<<<` from
reading as one. A quote that one line opens and the next closes is read
as no quote.
"""

BY_HAND = (
    "awk '/^ *```/ {inside = !inside; shell = /```shell$/; next} "
    'inside && shell && /^ *#/ {print FNR": "$0}\' ' + SETTINGS
)
"""The command that lists those lines in a checkout.

It reads a bare ```` ```shell ```` opening only, and does not except a
heredoc's body.
"""

BY_HAND_JSON = (
    "awk '/^ *```json/ {f = 1; next} f && /^ *```/ {f = 0} f' "
    + SETTINGS
    + " | jq -c type"
)
"""The command that prints the type of each value the `json` fences hold.

Each fence should print one line, `"object"` or `"array"`.
"""


class Fence(NamedTuple):
    """A fence of a markdown text."""

    number: int
    """The line number of its opening line, from 1."""

    language: str
    """The first word of its info string."""

    lines: tuple[tuple[int, str], ...]
    """Each line inside it, by number, its own indent removed."""


def fences(text: str) -> list[Fence]:
    """Return the fences of a markdown text, empty ones included.

    A fence closes on a line of the same mark, at least as long, with no
    info string. A fence left open runs to the end of the text, as
    CommonMark has it.

    :param text: the markdown text.
    :returns: the fences, in order.
    """
    found: list[Fence] = []
    marks = ""
    indent = 0
    for number, line in enumerate(text.splitlines(), start=1):
        fence = FENCE.match(line)
        if not marks:
            if fence and (fence["marks"][0] != "`" or "`" not in fence["info"]):
                marks, indent = fence["marks"], len(fence["indent"])
                language = (fence["info"].split() or [""])[0]
                found.append(Fence(number, language, ()))
            continue
        if (
            fence
            and not fence["info"].strip()
            and fence["marks"][0] == marks[0]
            and len(fence["marks"]) >= len(marks)
        ):
            marks = ""
            continue
        spaces = len(line) - len(line.lstrip(" "))
        last = found[-1]
        content = (number, line[min(indent, spaces) :])
        found[-1] = last._replace(lines=(*last.lines, content))
    return found


def commented(text: str) -> list[int]:
    """Return the lines inside a `shell` fence that open with `#`.

    :param text: the markdown text.
    :returns: the line numbers, from 1, a heredoc's body left out.
    """
    found: list[int] = []
    for fence in fences(text):
        if fence.language != "shell":
            continue
        ending = ""
        dash = False
        for number, content in fence.lines:
            if ending:
                if (content.lstrip("\t") if dash else content) == ending:
                    ending = ""
            elif content.lstrip().startswith("#"):
                found.append(number)
            else:
                ending, dash = opened(content)
    return found


def unparsed(text: str) -> list[int]:
    """Return the `json` fences that hold no single JSON object or array.

    :param text: the markdown text.
    :returns: the line numbers of their openings, from 1.
    """
    found: list[int] = []
    for fence in fences(text):
        if fence.language != "json":
            continue
        try:
            value = json.loads("\n".join(content for _, content in fence.lines))
        except ValueError:
            value = None
        if not isinstance(value, dict | list):
            found.append(fence.number)
    return found


def opened(line: str) -> tuple[str, bool]:
    """Return the word that ends the heredoc a shell line opens.

    :param line: a line of a `shell` fence, the fence's indent removed.
    :returns: the word, or the empty string where the line opens none,
        and whether the opening is `<<-`, whose body strips leading tabs.
    """
    for match in HEREDOC.finditer(line):
        if word := match["single"] or match["double"] or match["bare"]:
            return word, bool(match["dash"])
    return "", False


def test_this_tree_keeps_its_answers_out_of_its_shell_fences() -> None:
    """Section 9: this tree's own `REPOSITORY.md`, without the network."""
    lines = commented((ROOT / SETTINGS).read_text(encoding="utf-8"))
    assert not lines, f"{SETTINGS} has a # line in a shell fence at {lines}"


def test_this_tree_s_json_answers_parse() -> None:
    """Section 9: each `json` fence of this tree's file is one value."""
    text = (ROOT / SETTINGS).read_text(encoding="utf-8")
    assert any(fence.language == "json" for fence in fences(text)), (
        f"{SETTINGS} has no json fence, so this asks nothing"
    )
    lines = unparsed(text)
    assert not lines, f"{SETTINGS} has a json fence that does not parse at {lines}"


@pytest.mark.integration
def test_a_tree_keeps_its_answers_out_of_its_shell_fences(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 9: no `REPOSITORY.md` holds a `#` line in a `shell` fence.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    path = trees[repository] / SETTINGS
    if not path.is_file():
        pytest.skip(f"{repository} has no {SETTINGS}")
    lines = commented(path.read_text(encoding="utf-8"))
    assert not lines, (
        f"{SETTINGS} has a # line in a shell fence at {lines}; "
        + by_hand(repository, BY_HAND)
    )


@pytest.mark.integration
def test_a_tree_s_json_answers_are_one_object_or_array(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 9: each `json` fence of a `REPOSITORY.md` is one value.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    path = trees[repository] / SETTINGS
    if not path.is_file():
        pytest.skip(f"{repository} has no {SETTINGS}")
    lines = unparsed(path.read_text(encoding="utf-8"))
    assert not lines, (
        f"{SETTINGS} has a json fence that does not parse at {lines}; "
        + by_hand(repository, BY_HAND_JSON)
    )


@pytest.mark.parametrize(
    "body",
    ["true", "0", '"main"', "null", '{"a": 1}\n{"b": 2}', "", "{"],
    ids=["true", "number", "string", "null", "stream", "empty", "broken"],
)
def test_a_json_fence_holding_no_object_or_array_is_refused(body: str) -> None:
    """A scalar, a stream, an empty fence or broken JSON is no one value.

    :param body: what the fence holds.
    """
    fence = f"```json\n{body}\n```\n" if body else "```json\n```\n"
    assert unparsed(f"Prose.\n\n{fence}") == [3]


def test_a_json_fence_holding_one_object_or_array_passes() -> None:
    """An object, an array, and an object wrapped across lines."""
    text = '```json\n{"a": 1}\n```\n\n```json\n[]\n```\n\n```json\n{"a":\n 1}\n```\n'
    assert unparsed(text) == []


def test_an_answer_inside_the_command_s_fence_is_refused() -> None:
    """The shape the trees carry: the answer as a `#` line under the command."""
    text = "Prose.\n\n```shell\ngh api repos/o/r --jq .default_branch\n# main\n```\n"
    assert commented(text) == [5]


def test_an_answer_in_a_fence_of_its_own_passes() -> None:
    """A `text` or `json` fence is no shell, so a `#` there is the answer's."""
    text = (
        "```shell\ngh api repos/o/r --jq .default_branch\n```\n\n"
        "```text\nmain\n# printed by the command\n```\n\n"
        '```json\n{"enabled": true}\n```\n'
    )
    assert commented(text) == []


def test_a_fence_inside_a_list_item_is_read() -> None:
    """A fence indented under a bullet is a `shell` fence all the same."""
    text = "- A bullet:\n\n  ```shell\n  curl -sI http://x/\n  # HTTP/1.1 301\n  ```\n"
    assert commented(text) == [5]


def test_a_hash_line_in_a_heredoc_passes_and_the_lines_after_it_are_read() -> None:
    """A heredoc's body is input; the fence is read again after its end."""
    text = (
        "```shell\ncat > x.yml <<'YAML'\n# a comment of the file written\n"
        "key: value\nYAML\n# an answer\n```\n"
    )
    assert commented(text) == [6]


def test_a_here_string_opens_no_heredoc() -> None:
    """`<<<` is a here-string: the line after it is still the shell's."""
    text = "```shell\nwc -c <<< word\n# 5\n```\n"
    assert commented(text) == [3]


@pytest.mark.parametrize(
    "line",
    [
        "printf '%s\\n' '<<EOF'",
        'printf "<<EOF"',
        "echo x # <<EOF",
        'printf \'%s\\n\' "literal \\" <<EOF"',
    ],
)
def test_a_quoted_or_commented_operator_opens_no_heredoc(line: str) -> None:
    """A `<<` inside a quote or a comment is text, not the shell's operator.

    :param line: the command, carrying a `<<` that opens nothing.
    """
    text = f"```shell\n{line}\n# an answer\n```\n"
    assert commented(text) == [3]


@pytest.mark.parametrize("opening", ["<<EOF-JSON", "<<'EOF-JSON'", '<<"EOF-JSON"'])
def test_a_delimiter_is_read_whole(opening: str) -> None:
    """A delimiter holding a hyphen ends the body only where it stands whole.

    :param opening: the operator and its delimiter, quoted or bare.
    """
    text = f"```shell\ncat {opening}\nEOF\n# data\nEOF-JSON\n# an answer\n```\n"
    assert commented(text) == [6]


@pytest.mark.parametrize(
    "opening", ["``` shell", "```shell title=x", "~~~shell", "````shell"]
)
def test_any_opening_of_a_shell_fence_is_read(opening: str) -> None:
    """A space, a longer info string, tildes or more backticks: still shell.

    :param opening: the fence's opening line.
    """
    closing = opening.split("shell", maxsplit=1)[0].strip()
    text = f"{opening}\ngh api x\n# an answer\n{closing}\n"
    assert commented(text) == [3]


@pytest.mark.parametrize(
    ("opening", "inner", "closing"),
    [("````shell", "```", "````"), ("~~~shell", "```", "~~~")],
)
def test_a_fence_is_closed_by_its_own_mark_only(
    opening: str, inner: str, closing: str
) -> None:
    """A shorter run, or the other mark, is a line of the fence's content.

    :param opening: the fence's opening line.
    :param inner: a line that closes no fence of that opening.
    :param closing: the line that closes it.
    """
    text = f"{opening}\ngh api x\n{inner}\n# an answer\n{closing}\n"
    assert commented(text) == [4]


def test_an_unclosed_fence_runs_to_the_end() -> None:
    """CommonMark ends a fence left open at the end of the document."""
    assert commented("```shell\ngh api x\n# an answer\n") == [3]


@pytest.mark.parametrize(
    "line",
    [
        "echo $((1 << n))",
        "echo $((1 << 2))",
        "(( x = (1 << n) ))",
        "echo $[1 << 2]",
        "echo $((1 << 2 + (3 * (4 + 5))))",
    ],
)
def test_an_arithmetic_shift_opens_no_heredoc(line: str) -> None:
    """A `<<` inside an arithmetic expression is a shift, not a heredoc.

    :param line: the command, carrying a shift.
    """
    assert commented(f"```shell\n{line}\n# an answer\n```\n") == [3]


def test_a_delimiter_line_ends_the_body_only_exactly() -> None:
    """Under `<<`, a delimiter with a space before or after it is body."""
    text = "```shell\ncat <<'END'\n END\n# body\nEND \n# body\nEND\n# an answer\n```\n"
    assert commented(text) == [8]


def test_a_dash_strips_tabs_and_only_a_dash_does() -> None:
    """`<<-` ends its body on a tab-indented delimiter; `<<` does not."""
    dash = "```shell\ncat <<-EOF\n\t# body\n\tEOF\n# an answer\n```\n"
    plain = "```shell\ncat <<EOF\n\tEOF\n# body\nEOF\n# an answer\n```\n"
    assert (commented(dash), commented(plain)) == ([5], [6])


def test_a_hash_line_after_spaces_is_refused() -> None:
    """Spaces before the `#` leave it a word that opens a command."""
    assert commented("```shell\ngh api x\n   # an answer\n```\n") == [3]


def test_a_heredoc_in_a_fence_under_a_bullet_ends_at_its_delimiter() -> None:
    """The fence's own indent is not part of the delimiter line."""
    text = (
        "- A bullet:\n\n  ```shell\n  cat <<'EOF'\n  # body\n  EOF\n"
        "  # an answer\n  ```\n"
    )
    assert commented(text) == [7]


def test_a_heredoc_left_open_ends_with_its_fence() -> None:
    """The next `shell` fence is read from its first line."""
    text = "```shell\ncat <<'EOF'\n```\n\n```shell\n# an answer\n```\n"
    assert commented(text) == [6]


def test_a_numeric_delimiter_opens_a_heredoc() -> None:
    """`<<123` is a heredoc: the shell reads any word as its delimiter."""
    assert commented("```shell\ncat <<123\n# data\n123\n# an answer\n```\n") == [5]


def test_a_backtick_run_with_a_backtick_after_it_opens_no_fence() -> None:
    """CommonMark reads ```` ```shell `x` ```` as inline code, not a fence."""
    assert commented("```shell `x`\n# a heading\n") == []
