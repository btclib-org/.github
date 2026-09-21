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

FENCE = re.compile(r"```shell\n(.*?)\n```", re.DOTALL)
"""A fenced shell block, fence to fence."""

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
    line, or a comment; the comment lines immediately after that run,
    where there are any, are its recorded answer. A command with none
    directly below it -- the `PUT` a heredoc closes, the topics `diff`
    invocation -- names no pair.

    :param block: one fenced block's text, fences excluded.
    :returns: each command against the answer lines that follow it,
        joined back into one string.
    """
    lines = block.splitlines()
    pairs: list[tuple[str, str]] = []
    i = 0
    while i < len(lines):
        if not lines[i].startswith("gh api"):
            i += 1
            continue
        command = [lines[i]]
        i += 1
        while (
            i < len(lines)
            and lines[i]
            and not lines[i].startswith("#")
            and not lines[i].startswith("gh api")
        ):
            command.append(lines[i])
            i += 1
        answer: list[str] = []
        while i < len(lines) and lines[i].startswith("#"):
            answer.append(lines[i].removeprefix("#").strip())
            i += 1
        if answer:
            pairs.append(("\n".join(command), "\n".join(answer)))
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
        for block in FENCE.findall(section):
            for command, answer in _fenced_pairs(block):
                out.append((command, answer, observed))
        for command, answer in INLINE.findall(section):
            out.append((command, answer, observed))
    return out


def endpoint(command: str) -> str | None:
    """Read the path a `gh api` command asks, after the verb and any flag.

    :param command: the command, as `readings` extracted it.
    :returns: the endpoint, or ``None`` where the command does not open
        `gh api`.
    """
    match = re.match(r"gh api (?:-X \S+ )?(\S+)", command)
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
