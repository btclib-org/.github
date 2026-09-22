# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""A `REPOSITORY.md` line answers a live endpoint, or says it will not.

Section 11's *A recorded answer is a setting or an observation* is the
rule this reads back: a copy quotes a `gh api` command and the answer it
gave, and nothing before this module ran that command again to ask
whether the answer still holds -- btclib-org/.github#1017 is the drift
that went unnoticed this way, a `built` recorded for a Pages site having
become a `404` when the site moved.

A quoted pair is read back only where its own section -- the span its
nearest `##` or `###` heading opens -- does not carry `OBSERVATION`, the
words section 11 gives a copy for marking a reading this module does not
gate; carrying them is what takes a line out of the comparison, and
their absence is what leaves the default -- gated -- in force, so a line
marked the wrong way round is a red cell rather than a silent gap either
way it errs.

What is read back is narrower still than *every quoted pair not marked
an observation*, for three reasons this module does not paper over:

- **The endpoint has to be this repository's own.** A command under
  `orgs/<org>/...` answers for the organization rather than for the row
  a per-repository test occupies, and asking it once per repository
  would repeat the same call for every tree that quotes it -- so this
  reads back a command only where its endpoint opens
  `repos/<org>/<repository>`, the repository the test is asked about,
  and an organization-level command is left to a reader exactly as an
  observation is, without needing the words that mark one.
- **The command has to be one this module can safely run again.** A
  `-X` write -- the `PUT` that restores branch protection -- is never
  executed, and a command with no recorded answer at all, a diff
  invocation among them, records nothing this module can compare
  against.
- **The alignment sentinel's own token has to be able to answer it.**
  `WRITE_GATED` names the readings GitHub withholds from any read-only
  token by the endpoint's own design, and `UNGRANTED` names the
  readings the sentinel's App grant does not reach though GitHub gates
  each at `read` -- gating any of them would read a permission gap as
  the repository's own drift on every scheduled run.
  btclib-org/.github#1233 is where `UNGRANTED` is tracked; `WRITE_GATED`
  has no open question left.

**Only one tree is asked.** Marking an observation is new with this
module, and no `REPOSITORY.md` but this repository's own carries the
words yet -- `CONVERGED` is where a tree joins once it does, one at a
time, the way every convention here has rolled out. A tree not in it is
skipped, not failed: gating a copy that has never had the chance to mark
its volatile answers would gate answers nobody has sorted yet, which is
the fragile parser section 11 also warns against.

A recorded answer's shape is not one thing either. Most are a fenced
```shell block whose command is followed by the literal lines it printed
-- one or several, a single JSON document or a value jq streamed one
line at a time -- and a few are a sentence naming the command and its
answer inline, backtick to backtick. Both are read; what neither reads
is a block whose comment continues past the shape either parser
expects, which is why a `-X` write's restoring `PUT` -- ended by a
heredoc, not a comment -- and the topics comparison's own `diff` --
ended by nothing at all -- both fall out on their own, empty-handed
rather than misread.
"""

from __future__ import annotations

import json
import re
import subprocess
from typing import TYPE_CHECKING, Any

import pytest

from . import ORG, SELF, TIMEOUT, by_hand

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

SETTINGS = "REPOSITORY.md"
"""The root file section 2's table owes every tier."""

CONVERGED = frozenset({SELF})
"""Which trees' copies mark their observations, and so are read back.

A tree not here has not adopted section 11's marking convention, and a
row would gate whatever this module happened to find unmarked in a file
nobody has sorted into settings and observations yet -- the exact
fragility section 11 asks a reader to avoid forcing. Porting the
convention to a tree is what adds it here, one at a time.
"""

OBSERVATION = "a fact about a changing world"
"""Section 11's own words for a reading this module does not gate."""

FENCE = re.compile(r"^([ \t]*)```shell\n(.*?)\n\1```", re.DOTALL | re.MULTILINE)
"""A fenced shell block, fence to fence.

The opening and closing delimiters are required to carry the same
leading whitespace, captured so `readings` can strip it back off before
handing the body to `_fenced_pairs`: a block nested as a list
continuation -- ordinary, valid Markdown -- indents both fences and
every line between them alike, and neither `_fenced_pairs` nor `own`
reads a `gh api` or a `#` line that does not open at the start of its
own line. btclib-org/.github#1257 is where the unindented pattern
returned one block from a section whose text held four.
"""

INLINE = re.compile(r"`(gh api [^`]+)`\s+answers\s+`([^`]*)`")
"""A command and its answer, given inline rather than fenced.

Both backtick-quoted, the second following the word the sentence itself
uses -- *What this file passes over*'s bullets are the paragraphs
written this way.
"""

STATUS = re.compile(r"^\d{3}$")
"""A recorded answer that is a bare HTTP status rather than a body.

`gh api` exits non-zero on one of these and prints nothing to standard
output, the status itself going to standard error instead -- `/pages`
answering `404` is section 11's own example of why this is read back at
all.
"""

HTTP = re.compile(r"HTTP (\d+)")
"""How `gh`'s own stderr names the status a non-2xx answer carried."""


def _fenced_pairs(block: str) -> list[tuple[str, str]]:
    """Split one fenced block into its command/answer pairs.

    A pair is a run of lines opened by one starting `gh api`, up to but
    not including the next line that starts a new command, a blank
    line, or a comment. Where two or more such runs sit back to back
    with no comment of its own between them, the comment that follows
    the last one is read as each of theirs: btclib-org/.github#1255 is
    a `REPOSITORY.md` pairing two `gh api` commands under one trailing
    `# 0, both`, where the first used to be dropped -- not merely
    unmarked, absent from `readings()`'s output. A blank line between
    two such runs starts the next run fresh rather than reaching back
    across it, and a command with nothing following it at all -- the
    `PUT` a heredoc closes, the topics `diff` invocation -- names no
    pair.

    :param block: one fenced block's text, fences excluded.
    :returns: each command against the answer lines that follow it,
        joined back into one string; a command sharing its answer with
        another appears once for each, both carrying the same text.
    """
    lines = block.splitlines()
    pairs: list[tuple[str, str]] = []
    pending: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("gh api"):
            command = [line]
            i += 1
            while (
                i < len(lines)
                and lines[i]
                and not lines[i].startswith("#")
                and not lines[i].startswith("gh api")
            ):
                command.append(lines[i])
                i += 1
            pending.append("\n".join(command))
            continue
        if line.startswith("#"):
            answer: list[str] = []
            while i < len(lines) and lines[i].startswith("#"):
                answer.append(lines[i].removeprefix("#").strip())
                i += 1
            joined = "\n".join(answer)
            pairs.extend((command, joined) for command in pending)
            pending = []
            continue
        pending = []
        i += 1
    return pairs


SECTION = re.compile(r"^#{2,3} .*$", re.MULTILINE)
"""A heading opening one of this file's sections or subsections.

Every fenced block in this file sits under a blank line, so the
blank-line paragraph a fenced answer occupies is the fence alone --
what marks it an observation has to sit in the heading's section
instead, which is also the unit a reader already reads it in.
"""


def _sections(text: str) -> list[str]:
    """Split a copy into the spans its own `##` and `###` headings open.

    :param text: the copy's full text.
    :returns: each heading's text up to the next one, or to the end of
        the file for the last; the text before the first heading, if
        any, is not returned, since no reading this module extracts
        sits there.
    """
    starts = [match.start() for match in SECTION.finditer(text)]
    ends = [*starts[1:], len(text)]
    return [text[start:end] for start, end in zip(starts, ends, strict=True)]


def _dedent(indent: str, block: str) -> str:
    """Strip one fence's own leading whitespace back off its body.

    :param indent: the whitespace `FENCE` captured ahead of the fence,
        possibly empty.
    :param block: the fence's own content, that indent included.
    :returns: `block` with `indent` removed from the start of every
        line that carries it; a line that does not is left as it is.
    """
    if not indent:
        return block
    return re.sub(rf"(?m)^{re.escape(indent)}", "", block)


def readings(text: str) -> list[tuple[str, str, bool]]:
    """Read every command/answer pair a copy quotes, section by section.

    A section is asked for `OBSERVATION` on its own, so that the words
    marking one reading do not also silence an unrelated one under a
    different heading.

    :param text: the copy's full text.
    :returns: each pair found, with whether its own section carries
        `OBSERVATION`.
    """
    out: list[tuple[str, str, bool]] = []
    for section in _sections(text):
        observed = OBSERVATION in section
        for indent, raw in FENCE.findall(section):
            block = _dedent(indent, raw)
            for command, answer in _fenced_pairs(block):
                out.append((command, answer, observed))
        for command, answer in INLINE.findall(section):
            out.append((command, answer, observed))
    return out


_FLAG_VALUE = r"(?:'[^']*'|\"[^\"]*\"|\S+)"
"""One flag's own argument: single- or double-quoted, or a bare token.

A quoted argument may carry spaces of its own -- `--jq '{name, type}'`
-- which a bare `\\S+` stops at, reading only the part before the first
one.
"""

ENDPOINT = re.compile(rf"gh api (?:-i |-X {_FLAG_VALUE} |--jq {_FLAG_VALUE} )*(\S+)")
"""The path past `gh api`, the verb and any flag ahead of it skipped.

`-i` carries no value of its own; `-X` and `--jq` each take the token
right after them. btclib-org/.github#1253 and btclib-org/.github#1256
are where a command opening with `-i` or `--jq` first read as though the
flag itself were the endpoint, `own()` then answering `False` for a
reading that was this repository's own all along.

A flag this pattern does not name -- `-F`, `-H`, `--verbose` -- is left
unskipped on purpose: none of them opens a candidate pair
`_fenced_pairs` extracts today (measured across every copy at
btclib-org/.github#1256's own census), and skipping a flag this module
has not confirmed the shape of risks reading its value, or the flag
after it, as the endpoint instead.
"""


def endpoint(command: str) -> str | None:
    r"""Read the path a `gh api` command asks, after the verb and any flags.

    A command `_fenced_pairs` joined from more than one line carries the
    shell's own `\` line-continuation, and whatever indentation sits
    either side of it, where the break fell; that whole run collapses to
    one space first, so a flag's quoted argument spanning the break --
    `--jq '...' \` then the path on the next line -- reads as one flag
    and its value rather than leaving a second space `ENDPOINT` does not
    expect between them.

    :param command: the command, as `readings` extracted it.
    :returns: the endpoint, or ``None`` where the command does not open
        `gh api`.
    """
    joined = re.sub(r"\s*\\\n\s*", " ", command)
    match = ENDPOINT.match(joined)
    return match.group(1) if match else None


def own(command: str, repository: str) -> bool:
    """Say whether a command asks about this repository and not another.

    An `orgs/<org>/...` command, or one naming a different repository,
    is out of the row this test occupies -- section 11 leaves it to a
    reader rather than gating it here, where asking it once per
    repository would ask the same question of the API once per tree
    that happens to quote it.

    :param command: the command, as `readings` extracted it.
    :param repository: the repository this reading is asked about.
    :returns: whether the endpoint opens `repos/<org>/<repository>`.
    """
    asked = endpoint(command)
    if asked is None:
        return False
    head = f"repos/{ORG}/{repository}"
    return asked == head or asked.startswith(head + "/")


WRITE_GATED = (
    "allow_squash_merge",
    "bypass_actors",
)
"""A fragment naming a command whose answer GitHub withholds from any
read-only token, by the endpoint's own design rather than by a gap in
the sentinel's grant.

`repos/{owner}/{repo}`'s merge-method fields answer only where the
token holds `contents:write` beside `contents:read` -- GitHub's own
words, on *Get a repository*: "To view merge-related settings, you must
have the `contents:read` and `contents:write` permissions." A ruleset's
`bypass_actors` is returned only to a token with write access to the
ruleset -- GitHub's own words, on *Get a repository ruleset*: "To
prevent leaking sensitive information, the `bypass_actors` property is
only returned if the user making the API request has write access to
the ruleset." A reader is the permanent check on both;
btclib-org/.github#1233 is where that is established.
"""

UNGRANTED = (
    "/actions/secrets",
    "/actions/variables",
    "/dependabot/secrets",
)
"""A fragment naming a command the alignment sentinel's own App
installation does not reach, though GitHub gates each at `read`:
`actions/secrets`, `actions/variables` and `dependabot/secrets` each
exit `gh: Resource not accessible by integration (HTTP 403)` under the
installation's present grant of
actions/administration/contents/issues/metadata, all at `read` and
nothing wider. Widening the installation to add them at `read` is an
organization-owner action nobody has taken. btclib-org/.github#1233 is
where that stands; gating one of these ahead of it would read the
App's own reach as the repository's drift, every run.
"""


def granted(command: str) -> bool:
    """Say whether the alignment sentinel's own token can verify a command.

    :param command: the command, as `readings` extracted it.
    :returns: whether `command` names none of `WRITE_GATED` or
        `UNGRANTED`.
    """
    return not any(fragment in command for fragment in (*WRITE_GATED, *UNGRANTED))


def _stream(text: str) -> list[Any] | None:
    """Parse zero or more whitespace-separated JSON values from text.

    `jq` streams one document per matched element rather than wrapping
    them in an array, which is what a copy's rulesets pairing quotes
    three of, so this reads as many complete values as the text holds
    and refuses only where something is left over that is not one.

    :param text: the text to parse.
    :returns: the values found, in order; ``None`` where the text does
        not parse as a run of JSON values end to end.
    """
    decoder = json.JSONDecoder()
    values: list[Any] = []
    text = text.strip()
    index = 0
    while index < len(text):
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            break
        try:
            value, index = decoder.raw_decode(text, index)
        except json.JSONDecodeError:
            return None
        values.append(value)
    return values


def equivalent(actual: str, recorded: str) -> bool:
    """Say whether a live answer and a recorded one carry the same value.

    Compared as JSON where both parse that way, so that `gh`'s own key
    order -- alphabetical, where a copy's prose wraps a filter's fields
    in the order it wrote them -- is not read as a difference; as text
    with every run of whitespace collapsed otherwise, which is what a
    copy's own line wrapping is and nothing a live answer ever carries.

    :param actual: what the command printed just now.
    :param recorded: what the copy quotes.
    :returns: whether the two carry the same value.
    """
    live = _stream(actual)
    quoted = _stream(recorded)
    if live is not None and quoted is not None:
        return live == quoted
    return "".join(actual.split()) == "".join(recorded.split())


def mismatch(command: str, recorded: str) -> str | None:
    """Run one command and say how its answer differs from what is recorded.

    A recorded answer that is a bare HTTP status is compared against the
    status `gh` reports on its own failure, `-X` never being part of a
    command this reads, so the process this runs is always a `GET`.

    :param command: the command to run, exactly as the copy gives it.
    :param recorded: the answer the copy quotes for it.
    :returns: ``None`` where the two agree; otherwise a message naming
        both.
    """
    completed = subprocess.run(
        ["bash", "-c", command],
        capture_output=True,
        encoding="utf-8",
        timeout=TIMEOUT,
        check=False,
    )
    recorded_stripped = recorded.strip()
    if STATUS.match(recorded_stripped):
        found = HTTP.search(completed.stderr)
        status = found.group(1) if found else str(completed.returncode)
        if status == recorded_stripped:
            return None
        return f"{command!r} answers HTTP {status}, not {recorded_stripped}"
    if completed.returncode:
        return f"{command!r} exited {completed.returncode}: {completed.stderr.strip()}"
    if equivalent(completed.stdout, recorded):
        return None
    return f"{command!r} answers {completed.stdout.strip()!r}, not {recorded!r}"


def test_the_settings_file_reads_its_settings_back(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 11: a setting a copy quotes still answers what it quotes.

    A pair `readings` finds unmarked, scoped to this repository's own
    endpoints and to what the sentinel's own token can answer, is run
    again; the two failure shapes `mismatch` reports -- a changed
    answer, and a command that no longer succeeds where its recorded
    answer is not itself a status -- are both drift a reader would
    otherwise be the only check on.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :raises pytest.skip.Exception: where the repository has not adopted
        section 11's marking convention, or carries no `REPOSITORY.md`.
    """
    if repository not in CONVERGED:
        pytest.skip(f"{repository} has not adopted section 11's marking convention")
    path = trees[repository] / SETTINGS
    if not path.is_file():
        pytest.skip(f"{repository} has no {SETTINGS}")
    text = path.read_text(encoding="utf-8")
    failures = [
        found
        for command, recorded, observed in readings(text)
        if not observed and own(command, repository) and granted(command)
        for found in [mismatch(command, recorded)]
        if found is not None
    ]
    assert not failures, (
        f"{SETTINGS} quotes an answer that no longer holds: {failures}; "
        + by_hand(repository, "see REPOSITORY.md's own commands")
    )


def test_a_status_line_behind_dash_i_would_reach_the_comparison() -> None:
    """The cell above is green on a `-i` reading that drifted, however it reads.

    `own()` is what the cell above gates a reading on before `mismatch`
    ever runs it; asked of a command shaped exactly as
    btclib-org/.github#1253 measured it in `portanode`'s own copy -- `-i`
    ahead of the path -- it has to answer `True`, or a drift behind that
    shape would stay unread rather than reported.
    """
    command = "gh api -i repos/btclib-org/.github/pages 2>/dev/null | head -1"
    assert own(command, SELF) is True, (
        f"{command!r} reads as another repository's, or as no repository's"
        " at all: the flag ahead of the path is captured as the endpoint"
    )


def test_a_filter_behind_dash_dash_jq_would_reach_the_comparison() -> None:
    """The cell above is green on a `--jq` drift too, however it reads.

    Shaped as btclib-org/.github#1256 measured it in `btclib-secp256k1`'s
    own copy -- `--jq` and its quoted filter ahead of the path, the line
    broken where the file itself breaks it. `own()` has to answer `True`
    for the same reason as the cell above.
    """
    command = (
        "gh api --jq '.branch_policies[] | {name, type}' \\\n"
        "  repos/btclib-org/.github/environments/pypi/deployment-branch-policies"
    )
    assert own(command, SELF) is True, (
        f"{command!r} reads as another repository's, or as no repository's"
        " at all: the flag and its quoted value ahead of the path are"
        " captured as the endpoint, or the match fails at the line break"
    )


def test_an_unrecognized_flag_does_not_swallow_the_endpoint() -> None:
    """`endpoint()` skips a flag it names, not any token spelled like one.

    `-H`, ordinary `gh api` usage for a request header, is not among the
    flags this module recognizes, because no candidate pair carries it
    ahead of a path today. Skipping it anyway -- or skipping its value
    along with it -- would risk reading a future flag's argument, or the
    flag after it, as the endpoint instead of the path.
    """
    command = "gh api -H 'Accept: application/vnd.github+json' repos/btclib-org/.github"
    assert endpoint(command) == "-H", (
        f"{command!r} reads past an unrecognized flag: this module would"
        " swallow a flag it has not confirmed the shape of, rather than"
        " stopping the match at it"
    )


def test_a_shared_trailing_comment_reaches_every_command_it_precedes() -> None:
    """`_fenced_pairs` used to drop the first of two commands sharing an answer.

    Shaped as btclib-org/.github#1255 measured it in `btclib-node`,
    `bitcoin-core-rpc` and `bbt`'s own copies: a `gh api` command with no
    comment of its own, immediately followed by a second `gh api` line
    that does carry one. The comment is the first command's answer too,
    not only the second's -- the first used to name no pair at all.
    """
    first = "gh api repos/btclib-org/x/actions/secrets --jq '.total_count'"
    second = "gh api repos/btclib-org/x/dependabot/secrets --jq '.total_count'"
    block = f"{first}\n{second}\n# 0, both"
    pairs = _fenced_pairs(block)
    assert pairs == [(first, "0, both"), (second, "0, both")], (
        f"the leading command of a shared trailing comment is missing from"
        f" {pairs!r}: it names no pair rather than sharing the one below it"
    )


def test_a_blank_line_still_starts_the_next_shared_comment_fresh() -> None:
    """The fix above does not reach back across a blank line.

    Two runs of commands, each ended by a blank line before the next
    begins, are two separate pairings; a blank line is what
    `_fenced_pairs`'s own docstring already stops a single command's
    continuation at, and it stops a shared comment's reach the same way.
    This holds identically before and after btclib-org/.github#1255's
    fix: it guards the boundary the fix must not cross, rather than the
    defect the fix corrects.
    """
    block = (
        "gh api repos/btclib-org/x/a --jq '.n'\n"
        "\n"
        "gh api repos/btclib-org/x/b --jq '.n'\n"
        "# 5"
    )
    pairs = _fenced_pairs(block)
    assert pairs == [("gh api repos/btclib-org/x/b --jq '.n'", "5")], (
        f"a command separated from a later comment by a blank line picked"
        f" it up anyway: {pairs!r}"
    )


def test_fence_finds_a_block_indented_as_a_list_continuation() -> None:
    """`FENCE` used to require both fence delimiters to open at column zero.

    Shaped as btclib-org/.github#1257 measured it in `btclib-node`'s own
    copy: a ```` ```shell ```` block nested two spaces in, as the
    continuation of a bulleted list item -- ordinary, valid Markdown that
    the unindented pattern silently returned nothing for.
    """
    section = (
        "## Heading\n\n"
        "- **bullet**:\n\n"
        "  ```shell\n"
        "  gh api repos/btclib-org/x --jq '.homepage'\n"
        "  # https://x.example\n"
        "  ```\n"
    )
    found = readings(section)
    assert found == [
        ("gh api repos/btclib-org/x --jq '.homepage'", "https://x.example", False)
    ], f"the indented block named no reading: {found!r}"
