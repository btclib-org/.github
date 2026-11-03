# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What keeps `reusable-claude-implement.yml` within section 10's rule.

The rule is section 10's, and the workflow's header says how the file
keeps it. These tests read that configuration: the scopes each token is
asked for, the agent's allow list and the job that runs the agent's
edit. The scripts `comment`, `label`, `check-admission` and
`check-message`, the command running the gates and the step committing
the edit are read out of the workflow and run here, the scripts against
a stand-in `gh`, so what is asked is what the runner writes.
"""

from __future__ import annotations

import itertools
import json
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any, NamedTuple

import pytest

from . import ROOT
from .workflows_test import document, jobs

# the reusable workflow, which holds the jobs and their scripts
WORKFLOW = ROOT / ".github/workflows/reusable-claude-implement.yml"

# the jobs that run the agent
AGENTS = ("assess", "implement")

# the scripts' exit status for arguments they refuse
REFUSED = 2

# what the step writes beside the scripts: the number and the repository
TARGET = "7 o/r\n"

# the keys the action requests at their default, `write`, unless listed
DEFAULTS = {"contents", "issues", "pull_requests"}

# the one Bash rule shape an agent gets: a script of its job's directory
SCRIPT_RULE = re.compile(r"^Bash\(\$\{\{ runner\.temp \}\}/claude-(\w+)/(\w+):\*\)$")


def action(job: str) -> dict[str, str]:
    """Read the `with:` of a job's claude-code-action step.

    :param job: the job's id.
    :returns: the step's inputs.
    """
    found: list[dict[str, str]] = [
        step["with"]
        for step in jobs(WORKFLOW)[job]["steps"]
        if step.get("uses", "").startswith("anthropics/claude-code-action@")
    ]
    (inputs,) = found
    return inputs


def tools(job: str, flag: str) -> list[str]:
    """Read the rules after one flag of a job's `claude_args`.

    :param job: the job's id.
    :param flag: `--allowedTools` or `--disallowedTools`.
    :returns: the rules, up to the next flag.
    """
    args = shlex.split(action(job)["claude_args"])
    rules: list[str] = []
    for arg in args[args.index(flag) + 1 :]:
        if arg.startswith("--"):
            break
        rules.append(arg)
    return rules


def scripts(job: str) -> dict[str, str]:
    """Read the scripts a job writes, by name, out of its heredocs.

    :param job: the job's id.
    :returns: each script's text.
    """
    found = {}
    for step in jobs(WORKFLOW)[job]["steps"]:
        run = step.get("run", "")
        for match in re.finditer(r'cat > "\$DIR/([\w-]+)" <<\'SCRIPT\'\n', run):
            found[match[1]] = run[match.end() :].split("\nSCRIPT\n", 1)[0] + "\n"
    return found


@pytest.mark.parametrize("job", AGENTS)
def test_the_agent_s_token_lists_every_default_and_cannot_push(job: str) -> None:
    """Each default is named, and `contents` is read-only.

    A key left out keeps the action's `write`.

    :param job: the job's id.
    """
    listed: dict[str, str] = {}
    for line in action(job)["additional_permissions"].splitlines():
        if line.strip():
            key, value = line.split(":", 1)
            listed[key.strip()] = value.strip()
    assert set(listed) == DEFAULTS
    assert listed["contents"] == "read"


def test_the_published_token_is_asked_for_no_workflows_scope() -> None:
    """`publish` asks for contents and pull requests, nothing more."""
    (run,) = [
        step["run"]
        for step in jobs(WORKFLOW)["publish"]["steps"]
        if "github-app-token-exchange" in step.get("run", "")
    ]
    assert '{"permissions": {"contents": "write", "pull_requests": "write"}}' in run


@pytest.mark.parametrize("job", AGENTS)
def test_the_agent_runs_nothing_but_its_job_s_scripts(job: str) -> None:
    """Every Bash rule names a script of the job's own directory.

    :param job: the job's id.
    """
    rules = [rule for rule in tools(job, "--allowedTools") if rule.startswith("Bash")]
    assert rules
    for rule in rules:
        found = SCRIPT_RULE.match(rule)
        assert found, rule
        assert found[1] == job
        assert found[2] in scripts(job)


def test_the_editing_agent_is_kept_out_of_git() -> None:
    """Edit and Write are denied `.git/`, a deny winning over an allow."""
    assert {"Edit(./.git/**)", "Write(./.git/**)"} <= set(
        tools("implement", "--disallowedTools")
    )


def test_the_job_running_the_edit_asks_for_no_secret_and_no_oidc_token() -> None:
    """`gates` reads the tree, names no secret, and uploads nothing."""
    job: dict[str, Any] = jobs(WORKFLOW)["gates"]
    assert job["permissions"] == {"contents": "read"}
    assert "secrets." not in str(job)
    assert not [
        step for step in job["steps"] if "upload-artifact" in step.get("uses", "")
    ]


def conjuncts(condition: str) -> list[str]:
    """Cut a condition at its top-level `&&`, its spaces collapsed.

    :param condition: a job's `if:`, inside `${{ }}` or bare.
    :returns: the conjuncts, none where a top-level `||` makes it a
        disjunction.
    """
    text = condition.strip().removeprefix("${{").removesuffix("}}")
    parts: list[str] = []
    depth, start, quoted = 0, 0, False
    for index, char in enumerate(text):
        if char == "'":
            quoted = not quoted
        elif quoted:
            continue
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif depth == 0 and text.startswith("||", index):
            return []
        elif depth == 0 and text.startswith("&&", index):
            parts.append(text[start:index])
            start = index + 2
    parts.append(text[start:])
    return [" ".join(part.split()) for part in parts]


def re_runnable(workflow: Path) -> list[str]:
    """Name each job that no top-level conjunct holds to the first attempt.

    :param workflow: the file to read.
    :returns: the jobs' ids.
    """
    return [
        name
        for name, job in jobs(workflow).items()
        if "github.run_attempt == 1" not in conjuncts(job.get("if", ""))
    ]


def test_no_job_runs_again_on_a_re_run() -> None:
    """Each job's condition is `github.run_attempt == 1 && ...`, in some order.

    The header says a re-run is refused, and "Re-run failed jobs" can re-run
    any job.
    """
    assert re_runnable(WORKFLOW) == []


@pytest.mark.parametrize(
    ("old", "new"),
    [
        pytest.param(
            "github.run_attempt == 1\n",
            "github.run_attempt == 10\n",
            id="another attempt",
        ),
        pytest.param(
            "github.run_attempt == 1\n",
            "github.run_attempt == 1 || github.event_name == 'issues'\n",
            id="an alternative",
        ),
        pytest.param("&& github.run_attempt == 1\n", "\n", id="dropped"),
        pytest.param(
            "&& github.run_attempt == 1\n",
            "&& (github.run_attempt == 1 || true)\n",
            id="inside an alternative",
        ),
    ],
)
def test_the_re_run_check_sees_a_weakened_condition(
    tmp_path: Path, old: str, new: str
) -> None:
    """A copy of the workflow with the conjunct weakened in the first job.

    :param tmp_path: a directory of this test's own.
    :param old: the text the copy replaces, the first time it occurs.
    :param new: what it puts there.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    assert old in text
    mutant = tmp_path / "mutant.yml"
    mutant.write_text(text.replace(old, new, 1), encoding="utf-8")
    assert re_runnable(mutant) == [next(iter(jobs(WORKFLOW)))]


def test_a_job_behind_a_skipped_one_still_runs() -> None:
    """Each job with `needs:` opens with `!cancelled()` and reads each result.

    Without a status function, a skipped `assess` skips every job behind
    it, whatever their conditions say.
    """
    for name, job in jobs(WORKFLOW).items():
        needs = job.get("needs", [])
        for needed in [needs] if isinstance(needs, str) else needs:
            assert job["if"].startswith("${{ !cancelled()"), name
            assert f"needs.{needed}.result" in job["if"], (name, needed)


# a word naming `gh` or `curl`, a path to either included
CALL = re.compile(r"(\S*/)?(gh|curl)")

# where a substitution cut out of a script stands, by its unit's number
PLACEHOLDER = "\x01{}\x01"

# an assignment of one substitution and nothing else
ASSIGNMENT = re.compile(r"\w+=\x01(\d+)\x01")

# a flag of `set` that turns `errexit` off, `+o errexit` aside
ERREXIT_OFF = re.compile(r"\+[a-zA-Z]*e[a-zA-Z]*")

# the pieces a script is read in, each named for what becomes of it
PIECE = re.compile(
    r"(?P<join>\\\n)|(?P<escape>\\.)|(?P<ansi>\$'(\\.|[^\\'])*')"
    r"|(?P<single>'[^']*')|(?P<unclosed>')"
    r'|(?P<double>")|(?P<comment>(?<![^\s;(])#[^\n]*)'
    r"|(?P<substitution>\$\(|<\(|>\(|`)|(?P<string><<<)"
    r"""|(?P<heredoc><<(?P<dash>-?)\s*(?P<quote>['"]?)(?P<backslash>\\?)"""
    r"(?P<tag>\w+)(?P=quote))"
    r"|(?P<opening>\()|(?P<closing>\))|(?P<newline>\n)"
    r"""|(?P<other>[^\\'"#$<>()`\n]+|.)""",
    re.DOTALL,
)

# what a piece leaves in the skeleton, where that is not its own text
LEFT = {"join": " ", "escape": "x", "ansi": "''", "single": "''", "comment": ""}

# the pieces of a double-quoted string, and of a heredoc body that expands
QUOTED = re.compile(r'(?P<end>")|\\.|(?P<substitution>\$\(|`)|[^"\\$`]+|.', re.DOTALL)
EXPANDED = re.compile(r"\\.|(?P<substitution>\$\(|`)|[^\\$`]+|.", re.DOTALL)

# the tokens of a skeleton
TOKEN = re.compile(
    r"(?P<space>[ \t\r]+)|(?P<newline>\n)"
    r"|(?P<redirect>[0-9]*(&>>?|>>|>&|<&|<<<|<<-?|<>|>\||[<>]))"
    r"|(?P<operator>;;&?|;&|\|\||&&|\|&|[;|&()])"
    r"|(?P<word>[^\s;&|()<>]+)"
)


class Reader:
    """Read a shell script as its commands, nothing quoted left in them.

    A comment goes, a continuation joins its lines, and a quoted string
    keeps its quotes and only the substitutions inside it. Each
    substitution, `$(...)`, `<(...)`, `>(...)` or backticks, is cut out
    into a unit of its own and stands as a placeholder naming the unit. A
    heredoc's body is a unit of its own: the substitutions it expands where
    its word is not quoted, and a script where its body starts with `#!`,
    its word quoted or not.
    """

    def __init__(self, text: str, units: list[tuple[str, str]]) -> None:
        """Take the script, and where its units go.

        :param text: the script.
        :param units: where each unit is added, as its kind and its skeleton.
        """
        self.text = text
        self.units = units

    def read(self, index: int = 0, *, closing: bool = False) -> tuple[str, int]:
        """Read from `index` to the end, or to a substitution's closing `)`.

        :param index: where to start.
        :param closing: whether a `)` of this level ends the reading.
        :returns: the skeleton, and where the reading stopped.
        :raises ValueError: where a quote, a substitution or a heredoc is
            left open.
        """
        out: list[str] = []
        depth = 0
        heredocs: list[tuple[str, bool, bool]] = []
        while index < len(self.text):
            piece = PIECE.match(self.text, index)
            assert piece
            kind, index = piece.lastgroup, piece.end()
            if kind == "closing" and closing and not depth:
                return "".join(out), index
            if kind in {"double", "substitution", "unclosed"}:
                text, index = getattr(self, str(kind))(piece[0], index)
                out.append(text)
                continue
            if kind == "heredoc":
                quoted = bool(piece["quote"] or piece["backslash"])
                heredocs.append((piece["tag"], quoted, bool(piece["dash"])))
            elif kind == "newline" and heredocs:
                index = self.heredocs(heredocs, index)
                heredocs = []
            depth = max(depth + {"opening": 1, "closing": -1}.get(str(kind), 0), 0)
            out.append(LEFT.get(str(kind), piece[0]))
        if closing or heredocs:
            message = "a substitution or a heredoc is left open"
            raise ValueError(message)
        return "".join(out), index

    def unclosed(self, _: str, index: int) -> tuple[str, int]:
        """Refuse a single quote left open.

        :param _: the quote.
        :param index: where the string would start.
        :raises ValueError: always.
        """
        message = f"a single quote is left open at {index}"
        raise ValueError(message)

    def double(self, _: str, index: int) -> tuple[str, int]:
        """Read a double-quoted string, keeping only its substitutions.

        :param _: the opening quote.
        :param index: where the string starts.
        :returns: its skeleton, and where the text goes on after it.
        :raises ValueError: where the string is left open.
        """
        out = ['"']
        while index < len(self.text):
            piece = QUOTED.match(self.text, index)
            assert piece
            index = piece.end()
            if piece["end"]:
                return "".join([*out, '"']), index
            if piece["substitution"]:
                text, index = self.substitution(piece[0], index)
                out.append(text)
        message = "a double quote is left open"
        raise ValueError(message)

    def expanded(self) -> str:
        """Read a heredoc body that expands, keeping only its substitutions.

        :returns: their placeholders.
        """
        out: list[str] = []
        index = 0
        while index < len(self.text):
            piece = EXPANDED.match(self.text, index)
            assert piece
            index = piece.end()
            if piece["substitution"]:
                text, index = self.substitution(piece[0], index)
                out.append(text)
        return " ".join(out)

    def substitution(self, opening: str, index: int) -> tuple[str, int]:
        """Cut a substitution out into a unit of its own.

        :param opening: `$(`, `<(`, `>(` or a backtick.
        :param index: where its text starts.
        :returns: its placeholder, and where the text goes on after it.
        """
        if opening == "`":
            end = self.text.index("`", index)
            unit, _ = Reader(self.text[index:end], self.units).read()
            index = end + 1
        else:
            unit, index = self.read(index, closing=True)
        self.units.append((opening, unit))
        return PLACEHOLDER.format(len(self.units) - 1), index

    def heredocs(self, tags: list[tuple[str, bool, bool]], index: int) -> int:
        """Read the bodies of the heredocs a line opened, from the next line.

        A body that expands is read for its substitutions, which run as it
        is written; one that opens with `#!` is read as a script too, its
        leading tabs gone after `<<-`.

        :param tags: the words that end them, in order, each with whether
            it is quoted and whether it follows `<<-`.
        :param index: where the first body starts.
        :returns: where the text goes on after the last.
        :raises ValueError: where a body is left open.
        """
        for tag, quoted, dash in tags:
            # the tag ends the body in the first column, or after tabs
            # under `<<-`
            indent = r"\t*" if dash else ""
            ended = re.compile(rf"^{indent}{tag}$", re.MULTILINE)
            end = ended.search(self.text, index)
            if end is None:
                message = f"the heredoc {tag} is left open"
                raise ValueError(message)
            text = self.text[index : end.start()]
            body = Reader(re.sub(r"(?m)^\t+", "", text) if dash else text, self.units)
            if not quoted:
                self.units.append(("text", body.expanded()))
            if body.text.startswith("#!"):
                # the script runs with `errexit` only where its `#!` says so
                shebang = body.text.split("\n", 1)[0]
                kind = "script -e" if re.search(r"\s-\w*e", shebang) else "script"
                self.units.append((kind, body.read()[0]))
            index = end.end()
        return index


class Simple(NamedTuple):
    """A simple command: its words, then its redirections."""

    words: list[str]
    redirects: list[str]


class Compound(NamedTuple):
    """A compound command, each part with its role.

    The role is `condition`, `body`, `function` or `words`, the last for
    the words of `for` and `case`.
    """

    parts: list[tuple[str, list[AndOr]]]
    redirects: list[str]


class Pipeline(NamedTuple):
    """Commands joined by `|`, negated by `!` or not."""

    negated: bool
    commands: list[Simple | Compound]


class AndOr(NamedTuple):
    """Pipelines joined by `&&` and `||`, run in the background or not."""

    pipelines: list[Pipeline]
    operators: list[str]
    background: bool


# the words that open a compound command, and the method reading each
OPENERS = {
    "if": "conditional",
    "while": "loop",
    "until": "loop",
    "for": "iteration",
    "case": "choice",
    "{": "group",
    "(": "group",
}


def wrapped(words: list[str]) -> list[AndOr]:
    """Wrap words as one simple command, for the walk to read them.

    :param words: the words.
    :returns: the command, as a list.
    """
    command = Pipeline(negated=False, commands=[Simple(words, [])])
    return [AndOr(pipelines=[command], operators=[], background=False)]


class Parser:
    """Parse a skeleton into the commands the check walks."""

    def __init__(self, skeleton: str) -> None:
        """Cut the skeleton into its tokens.

        :param skeleton: what `Reader` left of a script.
        """
        self.tokens = [
            (str(token.lastgroup), token[0])
            for token in TOKEN.finditer(skeleton)
            if token.lastgroup != "space"
        ]
        self.at = 0

    def peek(self, ahead: int = 0) -> str | None:
        """Read a token without taking it.

        :param ahead: how far past the next one.
        :returns: its text, None past the end.
        """
        at = self.at + ahead
        return self.tokens[at][1] if at < len(self.tokens) else None

    def kind(self) -> str | None:
        """Read the next token's kind.

        :returns: the kind, None past the end.
        """
        return self.tokens[self.at][0] if self.at < len(self.tokens) else None

    def take(self, expected: str | None = None) -> str:
        """Take the next token.

        :param expected: the text it must have, any where None.
        :returns: its text.
        :raises ValueError: where there is none, or another.
        """
        found = self.peek()
        if found is None or expected not in {None, found}:
            message = f"{expected!r} expected at token {self.at}, not {found!r}"
            raise ValueError(message)
        self.at += 1
        return found

    def skip(self, separators: frozenset[str] = frozenset({"\n"})) -> None:
        """Skip separators.

        :param separators: the tokens skipped.
        """
        while self.peek() in separators:
            self.at += 1

    def script(self) -> list[AndOr]:
        """Parse the whole skeleton.

        :returns: its commands.
        :raises ValueError: where tokens are left over.
        """
        found = self.items(frozenset())
        if self.peek() is not None:
            message = f"{self.peek()!r} unexpected at token {self.at}"
            raise ValueError(message)
        return found

    def items(self, stops: frozenset[str]) -> list[AndOr]:
        """Parse a list of commands, up to a word that ends it.

        :param stops: the words that end it.
        :returns: the commands.
        """
        found: list[AndOr] = []
        while True:
            self.skip(frozenset({"\n", ";"}))
            if self.peek() is None or self.peek() in stops:
                return found
            found.append(self.and_or())

    def and_or(self) -> AndOr:
        """Parse pipelines joined by `&&` and `||`.

        :returns: the list.
        """
        pipelines = [self.pipeline()]
        operators = []
        while self.peek() in {"&&", "||"}:
            operators.append(self.take())
            self.skip()
            pipelines.append(self.pipeline())
        background = self.peek() == "&"
        self.at += background
        return AndOr(pipelines, operators, background)

    def pipeline(self) -> Pipeline:
        """Parse commands joined by `|`, `!` before them or not.

        :returns: the pipeline.
        """
        negated = self.peek() == "!"
        self.at += negated
        commands = [self.command()]
        while self.peek() in {"|", "|&"}:
            self.at += 1
            self.skip()
            commands.append(self.command())
        return Pipeline(negated, commands)

    def command(self) -> Simple | Compound:
        """Parse one command, simple or compound.

        :returns: the command.
        """
        opener = self.peek()
        if opener in OPENERS:
            parts = getattr(self, OPENERS[str(opener)])()
        elif opener == "function" or (self.peek(1), self.peek(2)) == ("(", ")"):
            parts = self.function()
        else:
            return self.simple()
        return Compound(parts, self.redirects())

    def redirects(self) -> list[str]:
        """Parse the redirections after a command.

        :returns: each, with its target.
        """
        found = []
        while self.kind() == "redirect":
            found.append(self.take() + self.take())
        return found

    def simple(self) -> Simple:
        """Parse a simple command.

        :returns: the command.
        :raises ValueError: where it has no word.
        """
        words: list[str] = []
        redirects: list[str] = []
        while self.kind() in {"word", "redirect"}:
            if self.kind() == "redirect":
                redirects += self.redirects()
            else:
                words.append(self.take())
        if not words and not redirects:
            message = f"a command expected at token {self.at}, not {self.peek()!r}"
            raise ValueError(message)
        return Simple(words, redirects)

    def conditional(self) -> list[tuple[str, list[AndOr]]]:
        """Parse `if`, its `elif`s and its `else`.

        :returns: the conditions and the bodies.
        """
        parts = []
        keyword = self.take("if")
        while keyword in {"if", "elif"}:
            parts.append(("condition", self.items(frozenset({"then"}))))
            self.take("then")
            parts.append(("body", self.items(frozenset({"elif", "else", "fi"}))))
            keyword = self.take()
        if keyword == "else":
            parts.append(("body", self.items(frozenset({"fi"}))))
            keyword = self.take()
        if keyword != "fi":
            message = f"'fi' expected at token {self.at}, not {keyword!r}"
            raise ValueError(message)
        return parts

    def loop(self) -> list[tuple[str, list[AndOr]]]:
        """Parse `while` or `until`.

        :returns: the condition and the body.
        """
        self.take()
        condition = self.items(frozenset({"do"}))
        self.take("do")
        body = self.items(frozenset({"done"}))
        self.take("done")
        return [("condition", condition), ("body", body)]

    def iteration(self) -> list[tuple[str, list[AndOr]]]:
        """Parse `for`.

        :returns: its words and its body.
        """
        self.take("for")
        words = [self.take()]
        self.skip()
        if self.peek() == "in":
            while self.kind() == "word":
                words.append(self.take())
        self.skip(frozenset({"\n", ";"}))
        self.take("do")
        body = self.items(frozenset({"done"}))
        self.take("done")
        return [("words", wrapped(words)), ("body", body)]

    def choice(self) -> list[tuple[str, list[AndOr]]]:
        """Parse `case`.

        :returns: its word and its arms' bodies.
        """
        self.take("case")
        parts = [("words", wrapped([self.take()]))]
        self.skip()
        self.take("in")
        while True:
            self.skip()
            if self.peek() == "esac":
                self.take()
                return parts
            while self.peek() not in {")", None}:
                self.take()
            self.take(")")
            ends = frozenset({";;", ";&", ";;&", "esac"})
            parts.append(("body", self.items(ends)))
            self.at += self.peek() in ends - {"esac"}

    def group(self) -> list[tuple[str, list[AndOr]]]:
        """Parse `{ ... }` or `( ... )`.

        :returns: the body.
        """
        closer = "}" if self.take() == "{" else ")"
        body = self.items(frozenset({closer}))
        self.take(closer)
        return [("body" if closer == "}" else "subshell", body)]

    def function(self) -> list[tuple[str, list[AndOr]]]:
        """Parse a function's definition.

        :returns: its body.
        """
        if self.take() == "function":
            self.take()
        if self.peek() == "(":
            self.take("(")
            self.take(")")
        self.skip()
        command = self.command()
        pipeline = Pipeline(negated=False, commands=[command])
        body = AndOr(pipelines=[pipeline], operators=[], background=False)
        return [("function", [body])]


def single_call(unit: str) -> bool:
    """Say whether a substitution's text is one `gh` or `curl` call alone.

    :param unit: the substitution's skeleton.
    :returns: whether it is the call, on one line, with no redirection.
    """
    if "\n" in unit.strip():
        return False
    try:
        (and_or,) = Parser(unit).script()
    except ValueError:
        return False
    if len(and_or.pipelines) != 1:
        return False
    (pipeline,) = and_or.pipelines
    command = pipeline.commands[0]
    return (
        not and_or.background
        and not pipeline.negated
        and len(pipeline.commands) == 1
        and isinstance(command, Simple)
        and not command.redirects
        and bool(CALL.fullmatch("".join(command.words[:1])))
    )


class Check:
    """Walk a step's scripts, keeping what could carry on past a failed call.

    A command is held to its result where it is a pipeline of its own, not
    negated, not in the background, not beside `&&` or `||`, not in a
    condition or a function's body, and inside nothing that is not held
    too. A simple command followed by `|| exit`, `|| exit $?` or `|| exit`
    with a literal non-zero status is held as well. A subshell's body is
    held only where the script has `errexit`, since an `exit` inside it
    ends the subshell alone.
    """

    def __init__(self, units: list[tuple[str, str]]) -> None:
        """Take the step's units.

        :param units: each unit's kind and skeleton.
        """
        self.units = units
        self.calls = {
            number
            for number, (_, unit) in enumerate(units)
            if any(
                token.lastgroup == "word" and CALL.fullmatch(token[0])
                for token in TOKEN.finditer(unit)
            )
        }
        self.accepted: set[int] = set()
        self.found: list[str] = []
        self.errexit = True

    def script(self, unit: str, *, errexit: bool) -> None:
        """Walk one script.

        :param unit: its skeleton.
        :param errexit: whether it runs with `errexit`.
        """
        self.errexit = errexit
        try:
            self.items(Parser(unit).script(), held=True)
        except ValueError as error:
            self.found.append(f"not read: {error}")

    def items(self, items: list[AndOr], *, held: bool) -> None:
        """Walk a list of commands.

        :param items: the commands.
        :param held: whether the list is held to its result.
        """
        for and_or in items:
            first = and_or.pipelines[0].commands
            exits = (
                and_or.operators == ["||"]
                and is_exit(and_or.pipelines[1])
                and len(first) == 1
                and isinstance(first[0], Simple)
            )
            alone = len(and_or.pipelines) == 1 or exits
            for index, pipeline in enumerate(and_or.pipelines):
                self.pipeline(
                    pipeline,
                    held=held and alone and not and_or.background,
                    exits=exits and index == 0,
                )

    def pipeline(self, pipeline: Pipeline, *, held: bool, exits: bool) -> None:
        """Walk a pipeline.

        :param pipeline: the pipeline.
        :param held: whether its list holds it to its result.
        :param exits: whether `|| exit` follows it.
        """
        held = held and not pipeline.negated and len(pipeline.commands) == 1
        for command in pipeline.commands:
            if isinstance(command, Compound):
                for role, items in command.parts:
                    # an `exit` in a subshell ends the subshell alone
                    body = role == "body" or (role == "subshell" and self.errexit)
                    self.items(items, held=held and body)
            else:
                self.simple(command, held=held, exits=exits)

    def simple(self, command: Simple, *, held: bool, exits: bool) -> None:
        """Walk a simple command: accept its call, or keep it.

        :param command: the command.
        :param held: whether it is held to its result.
        :param exits: whether `|| exit` follows it.
        """
        words = command.words
        if errexit_off(words):
            self.found.append(" ".join(words))
        assigned = ASSIGNMENT.fullmatch(words[0]) if len(words) == 1 else None
        if assigned and int(assigned[1]) in self.calls:
            kind, unit = self.units[int(assigned[1])]
            if held and (self.errexit or exits) and kind in {"$(", "`"}:
                self.accepted.update([int(assigned[1])] if single_call(unit) else [])
            return
        if not any(CALL.fullmatch(word) for word in words):
            return
        rest = list(itertools.dropwhile(re.compile(r"\w+=\S*").fullmatch, words))
        executed = rest[:1] == ["exec"]
        rest = rest[executed:]
        direct = bool(rest) and bool(CALL.fullmatch(rest[0]))
        if not (held and direct and (self.errexit or executed)):
            self.found.append(" ".join(words))


def errexit_off(words: list[str]) -> bool:
    """Say whether a command turns `errexit` off, or hides an error from it.

    :param words: the command's words.
    :returns: whether it is `set +e` or `+o errexit`, through `command` or
        `builtin` or not, `shopt -u -o errexit`, or `trap ... ERR`.
    """
    words = list(itertools.dropwhile({"command", "builtin"}.__contains__, words))
    head = words[:1]
    return (
        (head == ["set"] and any(ERREXIT_OFF.fullmatch(word) for word in words))
        or (head == ["set"] and "+o errexit" in " ".join(words))
        or (
            head == ["shopt"]
            and "errexit" in words
            and any(re.fullmatch(r"-\w*u\w*", word) for word in words)
        )
        or (head == ["trap"] and "ERR" in words)
    )


# what `exit` may take to fail: nothing, `$?`, or a status of 1 to 255,
# since bash keeps the status modulo 256
STATUS = re.compile(r"(\$\?|0*([1-9][0-9]?|1[0-9]{2}|2[0-4][0-9]|25[0-5]))?")


def is_exit(pipeline: Pipeline) -> bool:
    """Say whether a pipeline is `exit` with a status other than 0.

    :param pipeline: the pipeline.
    :returns: whether it is bare `exit`, `exit $?` or a literal non-zero
        status.
    """
    (command, *others) = pipeline.commands
    return (
        not others
        and not pipeline.negated
        and isinstance(command, Simple)
        and command.words[:1] == ["exit"]
        and not command.words[2:]
        and bool(STATUS.fullmatch("".join(command.words[1:])))
    )


def hidden_calls(run: str) -> list[str]:
    r"""List what in a step could carry on past a failed `gh` or `curl` call.

    The step's script runs under `bash -e`, which
    `test_no_step_hides_a_failed_gh_call` asserts by finding no `shell:`
    or `defaults:`. A script the step writes in a heredoc runs with
    `errexit` only where its `#!` line has `-e`; a `set -e` inside it is
    not read. A call passes as the whole of an assignment, `x=$(gh ...)` or
    its backtick form alone, with no redirection inside the substitution,
    and followed by `|| exit` where the script has no `errexit`. It passes
    as a direct call too, after variables and with any redirection, after
    `exec` where the script has no `errexit`. Either is held to its result,
    as `Check` says. Anything else is kept, and so are `set +e` and
    `set +o errexit`, through `command` or `builtin` or not,
    `shopt -u -o errexit`, its flags joined or not, and `trap ... ERR`.

    The check reads a call by its name, as a word: it does not follow a
    name built by quoting, expansion or substitution (`"gh"`, `\gh`,
    `''gh`, `$(true)gh`, `{gh,}`, `$GH`), nor a call run by `eval`,
    `bash -c` or `sh -c`, nor one in a quoted heredoc that does not open
    with `#!` but is run all the same (`bash <<'EOF'`). A heredoc body
    that opens with `#!` is read as a script, quoted or not. A call inside
    a function is kept, whatever calls the function. A script it cannot
    read is kept whole.

    :param run: the step's script.
    :returns: each command kept, a substitution as its unit.
    """
    units: list[tuple[str, str]] = []
    try:
        units.append(("script -e", Reader(run, units).read()[0]))
    except ValueError as error:
        return [f"not read: {error}"]
    check = Check(units)
    for kind, unit in units:
        if kind.startswith("script"):
            check.script(unit, errexit=kind == "script -e")
    found = check.found + [
        f"{units[number][0]}{units[number][1].strip()})"
        for number in sorted(check.calls - check.accepted)
        if not units[number][0].startswith("script")
    ]
    return [re.sub("\x01(\\d+)\x01", r"$(#\1)", line) for line in found]


def test_no_step_hides_a_failed_gh_call() -> None:
    """Each `gh` or `curl` call is an assignment's whole or a direct call.

    The steps run under `bash -e` without `pipefail`, so a pipe, an `if`,
    an argument, a test, `local`, an `||` or a `set +e` would carry on past
    a failed call with an empty answer. `hidden_calls` says what the check
    does not follow.
    """
    assert "defaults" not in document(WORKFLOW)
    for name, job in jobs(WORKFLOW).items():
        assert "defaults" not in job, name
        for step in job["steps"]:
            assert "shell" not in step, (name, step.get("name"))
            assert hidden_calls(step.get("run", "")) == [], (name, step.get("name"))


# a line of the workflow most mutants rewrite, the call it holds, and the
# indentation of the step's script
LABELS = """labels=$(gh api "repos/$REPO/issues/$NUMBER/labels" --jq '.[].name')"""
CALLED = """gh api "repos/$REPO/issues/$NUMBER/labels" --jq '.[].name'"""
INDENT = "\n" + " " * 10

# a call of check-admission, which runs without `errexit`
ADMISSION = """labels=$(gh api "repos/$1/issues/$2/labels" --jq '.[].name') || exit 1"""

# check-admission's loop over the label's events, and that loop in a pipe
LOOP = """admitted=
          while read -r kind actor at; do"""
PIPED = """admitted=$(printf '%s\\n' "$agent" \\
            | while read -r kind actor at; do"""


@pytest.mark.parametrize(
    ("old", "new"),
    [
        pytest.param(LABELS, f"labels=$({CALLED} | sort)", id="a pipe"),
        pytest.param(LABELS, f"labels=$({CALLED}) || :", id="|| :"),
        pytest.param(LABELS, f"labels=$({CALLED}) || true", id="|| true"),
        pytest.param(LABELS, f"labels=$({CALLED}) || echo none", id="|| echo"),
        pytest.param(LABELS, f"{CALLED} | sort", id="a direct call piped"),
        pytest.param(LABELS, f"{CALLED} || :", id="a direct call excused"),
        pytest.param(LABELS, f"read -r labels < <({CALLED})", id="< <(gh)"),
        pytest.param(LABELS, f'echo "labels=$({CALLED})"', id="in an argument"),
        pytest.param(LABELS, f'[ -z "$({CALLED})" ] || exit 1', id="in a test"),
        pytest.param(LABELS, f"local labels=$({CALLED})", id="local"),
        pytest.param(LABELS, f"if {CALLED}; then :; fi", id="if"),
        pytest.param(
            LABELS, f"labels=$({CALLED}{INDENT}  echo agent)", id="a second line"
        ),
        pytest.param(
            LABELS, f"{{{INDENT}  {CALLED} > l{INDENT}}} || true", id="a group excused"
        ),
        pytest.param(
            LABELS, f"({INDENT}  {CALLED} > l{INDENT}) || :", id="a subshell excused"
        ),
        pytest.param(
            LABELS,
            f"if{INDENT}  {CALLED} > l{INDENT}then :; fi",
            id="an if over lines",
        ),
        pytest.param(
            LABELS,
            f"while{INDENT}  {CALLED} > l{INDENT}do break; done",
            id="a while over lines",
        ),
        pytest.param(
            LABELS,
            f"f() {{{INDENT}  {CALLED}{INDENT}}}{INDENT}labels=$(f | sort)",
            id="a function piped",
        ),
        pytest.param(
            LABELS,
            f"cat > l <<EOF{INDENT}$({CALLED} | sort){INDENT}EOF",
            id="a heredoc that expands",
        ),
        pytest.param(LABELS, f"set +e{INDENT}{LABELS}", id="set +e"),
        pytest.param(LABELS, f"set -u +e{INDENT}{LABELS}", id="set -u +e"),
        pytest.param(LABELS, f"set -x +e{INDENT}{LABELS}", id="set -x +e"),
        pytest.param(LABELS, f"set +o errexit{INDENT}{LABELS}", id="set +o errexit"),
        pytest.param(LABELS, f"trap '' ERR{INDENT}{LABELS}", id="trap ERR"),
        pytest.param(") || exit 1\n", ")\n", id="a script without errexit"),
        pytest.param(LABELS, f"labels=$(cd /;{CALLED})", id="after a ;"),
        pytest.param(LABELS, f"labels=$(true&&{CALLED}) || :", id="after &&"),
        pytest.param(LABELS, f"labels=$( ({CALLED}) )", id="in a subshell"),
        pytest.param(LABELS, f"labels=$({CALLED}|sort)", id="before a |"),
        pytest.param(LABELS, f"{LABELS} || exit 0", id="|| exit 0"),
        pytest.param(LABELS, f"{LABELS} || exit 256", id="|| exit 256"),
        pytest.param(") || exit 1\n", ") || exit 0\n", id="a script's || exit 0"),
        pytest.param(ADMISSION, f"( {ADMISSION} )", id="a script's subshell"),
        pytest.param(
            LABELS, f"{{{INDENT}  {LABELS}{INDENT}  :{INDENT}}} || exit 1", id="a group"
        ),
        pytest.param(
            LABELS,
            f"cat > s <<S{INDENT}#!/bin/sh{INDENT}{CALLED} | sort{INDENT}S",
            id="a script in a heredoc that expands",
        ),
        pytest.param(
            LABELS,
            f"cat > s <<-'S'{INDENT}\t#!/bin/sh{INDENT}\t{CALLED} | sort{INDENT}\tS",
            id="a script after <<-",
        ),
        pytest.param(LABELS, f"command set +e{INDENT}{LABELS}", id="command set +e"),
        pytest.param(
            LABELS, f"shopt -u -o errexit{INDENT}{LABELS}", id="shopt -u -o errexit"
        ),
        pytest.param(LABELS, f"shopt -uo errexit{INDENT}{LABELS}", id="shopt -uo"),
        pytest.param(LOOP, PIPED, id="a loop in a pipe"),
    ],
)
def test_the_hidden_call_check_sees_each_form(
    tmp_path: Path, old: str, new: str
) -> None:
    """A copy of the workflow with the form in place of what it held.

    :param tmp_path: a directory of this test's own.
    :param old: the text the copy replaces, each time it occurs.
    :param new: what it puts there.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    assert old in text
    if new == PIPED:
        # the pipe's loop ends in `done)`, not in a here-string
        text = text.replace('done <<< "$agent"', "done)")
    mutant = tmp_path / "mutant.yml"
    mutant.write_text(text.replace(old, new), encoding="utf-8")
    found = [
        line
        for job in jobs(mutant).values()
        for step in job["steps"]
        for line in hidden_calls(step.get("run", ""))
    ]
    # the rule's own finding, not a script the check could not read
    assert [line for line in found if not line.startswith("not read: ")], found


@pytest.mark.parametrize("substitution", ["$(gh api x||true)", "$(true && gh api x)"])
def test_a_list_in_a_substitution_is_a_hidden_call(substitution: str) -> None:
    """It is kept as the call it hides, and the script is read past it.

    :param substitution: an assignment's substitution holding a list.
    """
    found = hidden_calls(f"labels={substitution}\ngh api y | sort\n")
    assert sorted(found) == sorted([substitution, "gh api y"]), found


def waiting() -> list[str]:
    """Read the labels that say why an issue waits, from the label script.

    :returns: the labels.
    """
    script = scripts("assess")["label"]
    (case,) = re.findall(r"^\s*([\w|-]+)\) ;;$", script, re.MULTILINE)
    labels: list[str] = str(case).split("|")
    return labels


def test_implement_starts_on_no_issue_that_waits() -> None:
    """Its condition, on every path, refuses each label saying an issue waits.

    The removal of `decision` skips `assess`, which reads the labels on the
    other path.
    """
    condition = jobs(WORKFLOW)["implement"]["if"]
    head = condition.split("&& (needs.assess", 1)[0]
    assert waiting() == ["decision", "needs-hardware", "needs-maintainer"]
    for label in waiting():
        assert f"!contains(github.event.issue.labels.*.name, '{label}')" in head


def test_the_gates_run_as_a_user_of_their_own() -> None:
    """The one step running the caller's gates runs them through `sudo -u`.

    `env -i` hands that user none of the runner's variables.
    """
    (run,) = [
        step["run"]
        for step in jobs(WORKFLOW)["gates"]["steps"]
        if "gates.sh" in step.get("run", "")
    ]
    assert "sudo useradd --create-home --shell /bin/bash claude-gates" in run
    command = gates_command(run)
    assert command.startswith(DROP), command
    lines = commands(run)
    (probe,) = [
        index
        for index, line in enumerate(lines)
        if line.startswith(DROP) and "/home/claude-gates/probe " in line
    ]
    assert probe < lines.index(command)


# how the step drops to the gates' user, with none of the runner's variables
DROP = "sudo -u claude-gates -H env -i "


def commands(run: str) -> list[str]:
    """Read a step's script as commands, each continuation joined.

    :param run: the step's script.
    :returns: its lines, a command on each.
    """
    return [line.strip() for line in re.sub(r"\\\n\s*", " ", run).splitlines()]


def gates_command(run: str) -> str:
    """Read the one command that runs `gates.sh`, its continuations joined.

    :param run: the step's script.
    :returns: the command, on one line.
    """
    (command,) = [
        line for line in commands(run) if "bash -e /home/claude-gates/gates.sh" in line
    ]
    return command


def test_the_gates_command_reader_sees_a_dropped_privilege_drop() -> None:
    """The mutation the check exists for: the same command without `sudo -u`."""
    mutated = (
        "sudo -u claude-gates -H env -i /home/claude-gates/probe\n"
        'bash -c "cd /home/claude-gates/tree && git add -A \\\n'
        '  && bash -e /home/claude-gates/gates.sh"\n'
    )
    assert not gates_command(mutated).startswith("sudo -u claude-gates")


def test_the_probe_asks_for_each_thing_the_gates_user_must_not_reach() -> None:
    """The runner's home, the docker socket, other users' environ, sudo."""
    (run,) = [
        step["run"]
        for step in jobs(WORKFLOW)["gates"]["steps"]
        if "gates.sh" in step.get("run", "")
    ]
    probe = run.split("<<'SCRIPT'\n", 1)[1].split("\nSCRIPT\n", 1)[0]
    for asked in ("/home/runner", "docker.sock", "/proc/", "sudo -n true"):
        assert asked in probe, asked
    assert "usermod" not in run
    assert "sudoers" not in run


@pytest.fixture
def bench(tmp_path: Path) -> Path:
    """Make a stand-in for `gh` that records its arguments.

    :param tmp_path: a directory of this test's own.
    :returns: the directory, first on the path the scripts run with.
    """
    stand_in = tmp_path / "gh"
    stand_in.write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" > {tmp_path}/gh.argv\n')
    stand_in.chmod(0o755)
    (tmp_path / "target").write_text(TARGET)
    return tmp_path


def run(
    bench: Path, job: str, name: str, *args: str
) -> subprocess.CompletedProcess[str]:
    """Write one of a job's scripts beside the stand-in and run it.

    :param bench: the stand-in's directory.
    :param job: the job whose script runs.
    :param name: the script's name.
    :param args: its arguments.
    :returns: the finished process.
    """
    script = bench / name
    script.write_text(scripts(job)[name])
    script.chmod(0o755)
    env = {**os.environ, "PATH": f"{bench}:{os.environ['PATH']}"}
    return subprocess.run(
        [str(script), *args],
        input="body\n",
        capture_output=True,
        encoding="utf-8",
        check=False,
        env=env,
    )


def recorded(bench: Path) -> list[str] | None:
    """Read what the stand-in was called with.

    :param bench: the stand-in's directory.
    :returns: its arguments, or None where it never ran.
    """
    argv = bench / "gh.argv"
    return argv.read_text().splitlines() if argv.exists() else None


@pytest.mark.parametrize("job", AGENTS)
def test_each_agent_job_writes_its_scripts(job: str) -> None:
    """A comment and a label for the agent, and the anchor for the step.

    :param job: the job's id.
    """
    assert set(scripts(job)) == {"comment", "label", "check-admission"}
    assert not [
        rule for rule in tools(job, "--allowedTools") if "check-admission" in rule
    ]


def test_publish_checks_the_admission_and_the_message() -> None:
    """The admission is read again where the edit is published."""
    assert set(scripts("publish")) == {"check-admission", "check-message"}


def test_the_agent_can_write_its_message_after_the_setup(tmp_path: Path) -> None:
    """The message's directory is made writable, outside the locked one.

    :param tmp_path: stands in for the runner's temporary directory.
    """
    steps = jobs(WORKFLOW)["implement"]["steps"]
    (make,) = [step for step in steps if "MESSAGE" in step.get("env", {})]
    message = make["env"]["MESSAGE"].replace("${{ runner.temp }}", str(tmp_path))
    locked = "${{ runner.temp }}/claude-implement"
    assert not make["env"]["MESSAGE"].startswith(locked + "/")
    (tmp_path / "claude-implement").mkdir(mode=0o555)
    subprocess.run(
        ["bash", "-e", "-c", make["run"]],
        env={**os.environ, "MESSAGE": message},
        check=True,
    )
    (Path(message) / "message").write_text("Do it (closes #7)\n")
    assert (Path(message) / "message").read_text() == "Do it (closes #7)\n"
    rule = "Write(/${{ runner.temp }}/claude-implement-message/message)"
    assert rule in tools("implement", "--allowedTools")


@pytest.mark.parametrize("job", AGENTS)
@pytest.mark.parametrize("label", ["decision", "needs-hardware", "needs-maintainer"])
def test_the_label_script_applies_a_label_that_says_why_an_issue_waits(
    bench: Path, job: str, label: str
) -> None:
    """A label saying why an issue waits reaches `gh issue edit`, no more.

    :param bench: the stand-in's directory.
    :param job: the job whose script runs.
    :param label: the label asked for.
    """
    done = run(bench, job, "label", label)
    assert done.returncode == 0, done.stderr
    assert recorded(bench) == ["issue", "edit", "7", "-R", "o/r", "--add-label", label]


@pytest.mark.parametrize("job", AGENTS)
@pytest.mark.parametrize(
    "args",
    [
        pytest.param([], id="no argument"),
        pytest.param(["agent"], id="agent"),
        pytest.param(["security"], id="another label"),
        pytest.param(["decision", "agent"], id="two"),
        pytest.param(["decision,agent"], id="a list"),
        pytest.param(["--remove-label"], id="a flag"),
    ],
)
def test_the_label_script_refuses_any_other(
    bench: Path, job: str, args: list[str]
) -> None:
    """Anything else is refused, status 2, `gh` unrun.

    :param bench: the stand-in's directory.
    :param job: the job whose script runs.
    :param args: the arguments.
    """
    done = run(bench, job, "label", *args)
    assert done.returncode == REFUSED
    assert done.stderr.startswith("label: "), done.stderr
    assert recorded(bench) is None


@pytest.mark.parametrize("job", AGENTS)
def test_the_comment_script_posts_on_the_issue_from_standard_input(
    bench: Path, job: str
) -> None:
    """No argument; the body is read by `gh` from standard input.

    :param bench: the stand-in's directory.
    :param job: the job whose script runs.
    """
    done = run(bench, job, "comment", "--edit-last")
    assert done.returncode == REFUSED
    assert done.stderr == "comment: takes no argument\n", done.stderr
    assert recorded(bench) is None
    done = run(bench, job, "comment")
    assert done.returncode == 0, done.stderr
    assert recorded(bench) == ["issue", "comment", "7", "-R", "o/r", "--body-file", "-"]


def check(
    bench: Path, message: str, number: str = "7"
) -> subprocess.CompletedProcess[str]:
    """Run `publish`'s message check on a message.

    :param bench: the stand-in's directory.
    :param message: the message, on standard input.
    :param number: the issue's number, as the argument.
    :returns: the finished process.
    """
    script = bench / "check-message"
    script.write_text(scripts("publish")["check-message"])
    script.chmod(0o755)
    return subprocess.run(
        [str(script), number],
        input=message,
        capture_output=True,
        encoding="utf-8",
        check=False,
    )


@pytest.mark.parametrize(
    "message",
    [
        "Do the thing (closes #7)\n",
        "Do the thing (closes #7)\n\nIt fixes the parser, see #8.\n",
        "Do the thing (closes #7)\n\nMail me at a@b.org.\n",
        "Do the thing (closes #7)\n\nMail first.last@b.org instead.\n",
        "Do the thing (closes #7)\n\nThe parser is used by: the CLI.\n",
        "Do the thing (closes #7)\n\nThe node waits on stand-by: idle.\n",
    ],
)
def test_the_message_check_passes_the_issue_s_own_citation(
    bench: Path, message: str
) -> None:
    """The subject's own `(closes #7)`, a bare reference, an address.

    :param bench: the stand-in's directory.
    :param message: the message.
    """
    done = check(bench, message)
    assert done.returncode == 0, done.stdout + done.stderr


@pytest.mark.parametrize(
    "message",
    [
        pytest.param("Do the thing\n", id="no citation"),
        pytest.param("Do the thing (closes #8)\n", id="another issue"),
        pytest.param("Do it (closes #7)\n\nCloses #8\n", id="body keyword"),
        pytest.param("Do it (closes #7)\n\nfixes: o/r#3\n", id="qualified"),
        pytest.param("Do it (closes #7)\n\nFixes o/r#8\n", id="same line"),
        pytest.param("Do it (closes #7)\n\nFixes\no/r#8\n", id="across lines"),
        pytest.param("Do it (closes #7)\n\nCloses\n\n#8\n", id="across a blank line"),
        pytest.param(
            "Do it (closes #7)\n\nResolves https://github.com/o/r/issues/3\n",
            id="url",
        ),
        pytest.param("Do it (closes #7) fixes #9 (closes #7)\n", id="in subject"),
        pytest.param("Do it (closes #7)\n\nThanks @someone\n", id="mention"),
        pytest.param("Do it (closes #7)\n\nsee .@someone\n", id="after a dot"),
        pytest.param("Do it (closes #7)\n\nx-@someone\n", id="after a hyphen"),
        pytest.param("Do it (closes #7)\n\n@someone\n", id="line start"),
        pytest.param("Do it (closes #7)\n\ncafé@someone\n", id="after an accent"),
        pytest.param("Do it (closes #7)\n\n見@someone\n", id="after a CJK letter"),
        pytest.param("Do it (closes #7)\n\nThanks _@octocat_\n", id="emphasis"),
        pytest.param("Do it (closes #7)\n\nIt _fixes #8_ too\n", id="keyword emphasis"),
        pytest.param("Do it (closes #7)\nand more\n\nbody\n", id="subject runs on"),
        pytest.param("Do it (closes #7)\n \nbody\n", id="spaces on line two"),
        pytest.param(
            "Do it (closes #7)\n\nCo-authored-by: A <a@b.org>\n", id="co-author"
        ),
        pytest.param(
            "Do it (closes #7)\n\nSigned-off-by: A <a@b.org>\n", id="sign-off"
        ),
        pytest.param("Do it (closes #7)\n\nreviewed-by : A\n", id="any -by: trailer"),
        pytest.param(
            "Do it (closes #7)\n\n  Co-authored-by: A <a@b.org>\n", id="indented"
        ),
        pytest.param(
            "Do it (closes #7)\n\n\tCo-authored-by: A <a@b.org>\n", id="tab-indented"
        ),
    ],
)
def test_the_message_check_refuses_any_other_closing_or_mention(
    bench: Path, message: str
) -> None:
    """Any other closing reference, a mention, a `-by:` trailer, a long subject.

    :param bench: the stand-in's directory.
    :param message: the message.
    """
    done = check(bench, message)
    assert done.returncode == 1
    # one of the check's own refusals, not a failure of the script
    refusal = re.compile(r"^check-message: (the|a) ", re.MULTILINE)
    assert refusal.search(done.stderr), done.stderr


@pytest.mark.parametrize("number", ["", "7a", "$(id)"])
def test_the_message_check_takes_a_number(bench: Path, number: str) -> None:
    """The argument is digits or the check refuses to run.

    :param bench: the stand-in's directory.
    :param number: the argument.
    """
    done = check(bench, "Do the thing (closes #7)\n", number)
    assert done.returncode == REFUSED
    assert done.stderr == "check-message: not a number\n", done.stderr


# a stand-in `gh` for `check-admission`: the events, the labels and the
# last edit from files beside it, an administrator and a writer by name,
# and any other login's permission from a file
ADMISSION_GH = """#!/bin/sh
here=${0%/*}
case $2 in
  repos/o/r/issues/7/events)
    [ -f "$here/events.json" ] || { echo "gh: HTTP 502" >&2; exit 1; }
    cat "$here/events.json" ;;
  repos/o/r/issues/7/labels)
    [ -f "$here/labels.txt" ] || { echo "gh: HTTP 502" >&2; exit 1; }
    cat "$here/labels.txt" ;;
  repos/o/r/collaborators/admin1/permission) echo admin ;;
  repos/o/r/collaborators/writer/permission) echo write ;;
  repos/o/r/collaborators/*/permission)
    [ -f "$here/permission.txt" ] || { echo "gh: HTTP 502" >&2; exit 1; }
    cat "$here/permission.txt" ;;
  graphql)
    [ -f "$here/edited.txt" ] || { echo "gh: HTTP 502" >&2; exit 1; }
    cat "$here/edited.txt" ;;
  *) echo "gh: Not Found (HTTP 404)" >&2; exit 1 ;;
esac
"""

T0 = "2026-11-03T10:00:00Z"
T1 = "2026-11-03T10:00:01Z"
T_BEFORE = "2026-11-03T09:59:59Z"


def event(kind: str, login: str | None, at: str) -> dict[str, Any]:
    """Make one `agent` label event, or a rename where the kind says so.

    :param kind: `labeled`, `unlabeled` or `renamed`.
    :param login: the actor's login, None for a deleted account.
    :param at: the event's time.
    :returns: the event, as the API gives it.
    """
    actor = None if login is None else {"login": login}
    return {"event": kind, "label": {"name": "agent"}, "actor": actor, "created_at": at}


ADMIN = event("labeled", "admin1", T0)


@pytest.mark.parametrize(
    ("events", "labels", "edited", "expected"),
    [
        pytest.param([ADMIN], "agent", "", 0, id="admitted"),
        pytest.param(
            [ADMIN, event("labeled", "claude[bot]", T1)],
            "agent",
            "",
            0,
            id="a bot after",
        ),
        pytest.param(
            [ADMIN, event("labeled", None, T1)], "agent", "", 0, id="ghost after"
        ),
        pytest.param(
            [ADMIN, event("labeled", "writer", T1)], "agent", "", 0, id="a writer after"
        ),
        pytest.param([ADMIN], "agent", T_BEFORE, 0, id="edited before"),
        pytest.param([ADMIN], "agent", T0, 1, id="edited in the same second"),
        pytest.param([ADMIN], "agent", T1, 1, id="edited after"),
        pytest.param(
            [ADMIN, event("renamed", "someone", T1)], "agent", "", 1, id="renamed after"
        ),
        pytest.param(
            [ADMIN, event("unlabeled", "writer", T1)], "", "", 1, id="withdrawn"
        ),
        pytest.param(
            [
                ADMIN,
                event("unlabeled", "writer", T1),
                event("labeled", "writer", "2026-11-03T10:00:02Z"),
            ],
            "agent",
            "",
            1,
            id="withdrawn and relabelled by a writer",
        ),
        pytest.param([ADMIN], "", "", 1, id="label gone"),
        pytest.param([ADMIN], "agent-x", "", 1, id="a longer label"),
        pytest.param([event("labeled", "writer", T0)], "agent", "", 1, id="no admin"),
        pytest.param([], "", "", 1, id="never labelled"),
    ],
)
def test_the_admission_covers_the_issue_until_withdrawn_or_edited(
    tmp_path: Path,
    events: list[dict[str, Any]],
    labels: str,
    edited: str,
    expected: int,
) -> None:
    """An administrator's label, still carried, and nothing changed since.

    :param tmp_path: a directory of this test's own.
    :param events: the issue's events, one page.
    :param labels: the labels the issue carries now, one per line.
    :param edited: the body's last edit, empty where never edited.
    :param expected: the exit status.
    """
    (tmp_path / "events.json").write_text(json.dumps([events]))
    (tmp_path / "labels.txt").write_text(labels + "\n" if labels else "")
    (tmp_path / "edited.txt").write_text(edited + "\n")
    # what GitHub answers for a bot
    (tmp_path / "permission.txt").write_text("none\n")
    done = admission(tmp_path)
    assert done.returncode == expected, done.stdout + done.stderr
    # a refusal is the script's own, with its reason, not a failed call
    assert ("::error::#7: " in done.stdout) == bool(expected), done.stdout


@pytest.mark.parametrize(
    "missing", ["events.json", "labels.txt", "edited.txt", "permission.txt"]
)
def test_the_admission_fails_where_the_api_cannot_be_read(
    tmp_path: Path, missing: str
) -> None:
    """A failed call is an error, not an answer: no refusal stands in for it.

    :param tmp_path: a directory of this test's own.
    :param missing: the answer the stand-in fails to give.
    """
    bot = event("labeled", "claude[bot]", T1)
    (tmp_path / "events.json").write_text(json.dumps([[ADMIN, bot]]))
    (tmp_path / "labels.txt").write_text("agent\n")
    (tmp_path / "edited.txt").write_text("\n")
    (tmp_path / "permission.txt").write_text("none\n")
    (tmp_path / missing).unlink()
    done = admission(tmp_path)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "::error::" not in done.stdout, done.stdout
    assert "gh: HTTP 502" in done.stderr, done.stderr


def admission(bench: Path) -> subprocess.CompletedProcess[str]:
    """Run `check-admission` against the stand-in.

    :param bench: where the stand-in and its answers go.
    :returns: the finished process.
    """
    stand_in = bench / "gh"
    stand_in.write_text(ADMISSION_GH)
    stand_in.chmod(0o755)
    script = bench / "check-admission"
    script.write_text(scripts("assess")["check-admission"])
    script.chmod(0o755)
    env = {**os.environ, "PATH": f"{bench}:{os.environ['PATH']}"}
    return subprocess.run(
        [str(script), "o/r", "7"],
        capture_output=True,
        encoding="utf-8",
        check=False,
        env=env,
    )


def gated(tree: Path, gates: str) -> subprocess.CompletedProcess[str]:
    """Stage a tree as the runner does, then run the gates' user's command.

    The runner's `git add -A` is the unpack step's; what the gates' user
    then runs is the command the workflow gives it, its paths pointed here.

    :param tree: a git checkout holding the edit, unstaged.
    :param gates: the gates' script.
    :returns: the finished command.
    """
    subprocess.run(["git", "-C", str(tree), "add", "-A"], check=True)
    (tree.parent / "gates.sh").write_text(gates)
    (run,) = [
        step["run"]
        for step in jobs(WORKFLOW)["gates"]["steps"]
        if "gates.sh" in step.get("run", "")
    ]
    inner = gates_command(run).split('bash -c "', 1)[1].rsplit('"', 1)[0]
    inner = inner.replace("/home/claude-gates/tree", str(tree))
    inner = inner.replace("/home/claude-gates/gates.sh", str(tree.parent / "gates.sh"))
    return subprocess.run(
        ["bash", "-c", inner], capture_output=True, encoding="utf-8", check=False
    )


@pytest.mark.parametrize(("ignored", "expected"), [("", 0), ("dep.py\n", 1)])
def test_the_gates_run_on_the_files_the_commit_holds(
    tmp_path: Path, ignored: str, expected: int
) -> None:
    """A dependency `.gitignore` keeps out of the commit is gone for the gates.

    :param tmp_path: a directory of this test's own.
    :param ignored: the tree's `.gitignore`, naming the new dependency or not.
    :param expected: the gates' exit status.
    """
    tree = tmp_path / "tree"
    tree.mkdir()
    subprocess.run(["git", "-C", str(tree), "init", "-q"], check=True)
    (tree / ".gitignore").write_text(ignored)
    (tree / "uses.py").write_text("import dep\n")
    (tree / "dep.py").write_text("")
    done = gated(tree, f"cd {tree} && python3 -c 'import uses'\n")
    assert done.returncode == expected, done.stderr
    assert ("No module named 'dep'" in done.stderr) == bool(expected), done.stderr


def test_publish_commits_only_the_tree_the_gates_ran_on() -> None:
    """The commit step compares its index with the tree `gates` recorded."""
    (step,) = [
        step
        for step in jobs(WORKFLOW)["publish"]["steps"]
        if step.get("name") == "Commit the edit"
    ]
    assert step["env"]["GATED"] == "${{ needs.gates.outputs.tree }}"
    assert '"$(git write-tree)" != "$GATED"' in step["run"]


def committed(
    tree: Path, edit: str | None, name: str = ".coderabbit.yaml"
) -> subprocess.CompletedProcess[str]:
    """Stage an edit and run `publish`'s commit step on it, `commit` stubbed.

    :param tree: a git checkout holding `.coderabbit.yaml` at HEAD.
    :param edit: the new text of the file named, None to leave it.
    :param name: the file the edit writes.
    :returns: the finished step.
    """
    (tree / "other.txt").write_text("an edit\n")
    if edit is not None:
        (tree / name).write_text(edit)
    subprocess.run(["git", "-C", str(tree), "add", "-A"], check=True)
    gated = subprocess.run(
        ["git", "-C", str(tree), "write-tree"],
        capture_output=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()
    (step,) = [
        step
        for step in jobs(WORKFLOW)["publish"]["steps"]
        if step.get("name") == "Commit the edit"
    ]
    run = step["run"].split("git -c user.name=", 1)[0] + "echo committed\n"
    return subprocess.run(
        ["bash", "-e", "-c", run],
        cwd=tree,
        env={**os.environ, "BRANCH": "claude/issue-7", "GATED": gated},
        capture_output=True,
        encoding="utf-8",
        check=False,
    )


def coderabbit_tree(tmp_path: Path) -> Path:
    """Make a checkout whose HEAD holds a `.coderabbit.yaml`.

    :param tmp_path: a directory of this test's own.
    :returns: the checkout.
    """
    tree = tmp_path / "tree"
    tree.mkdir()
    git = ["git", "-C", str(tree)]
    subprocess.run([*git, "init", "-q"], check=True)
    (tree / ".coderabbit.yaml").write_text("reviews:\n  auto_approve: false\n")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run(
        [*git, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"],
        check=True,
    )
    return tree


def test_publish_commits_an_edit_that_leaves_coderabbit_alone(tmp_path: Path) -> None:
    """The control: an edit elsewhere reaches the commit.

    :param tmp_path: a directory of this test's own.
    """
    done = committed(coderabbit_tree(tmp_path), None)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "committed" in done.stdout


@pytest.mark.parametrize(
    "name", [".coderabbit.yaml", ".coderabbit.yml", ".CodeRabbit.yml"]
)
def test_publish_refuses_an_edit_to_coderabbit(tmp_path: Path, name: str) -> None:
    """A staged `.coderabbit.yaml` or `.coderabbit.yml`, any case, stops it.

    :param tmp_path: a directory of this test's own.
    :param name: the file the edit writes.
    """
    tree = coderabbit_tree(tmp_path)
    done = committed(tree, "reviews:\n  auto_approve: true\n", name)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "CodeRabbit's configuration" in done.stdout
    assert "committed" not in done.stdout
