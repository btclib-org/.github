#!/usr/bin/env python3
# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Refuse an entry written outside a release's own pull request.

A pull request adds no entry, and the last check below refuses one. The
others read what a conflict resolved by deleting its markers breaks: two
branches appending an entry at the same anchor conflict there, and
deleting the markers keeps both sides and, at git's default conflict
style, writes once the lines both blocks start or end with. The
`merge=union` driver, which section 9 of README.md rejects, writes the
same; btclib-org/.github#21 and btclib-org/.github#760 measured what that
costs under it. They stay as the shape checks of a release's own
section. Every check but the last runs once over the file's own open
section -- the first `## ` heading's, up to the line before the second,
or to the end of the file where there is no second. A
`## ` or `### ` line inside a fenced code block is a markdown example
rather than a heading of the file's own, and is blanked out before
either is matched (btclib-org/.github#1372) -- character for character,
unlike `_CODE_SPAN` below, which removes what it strips outright rather
than preserving its length.

Three checks, all of them shapes a conflict resolved by deleting its
markers produces -- a fourth, below them, that is section 9's own bound
on an entry -- a fifth that backs the fourth's own exemption, which
trusts a placement rule nothing else here checks -- and a sixth,
unrelated to the rebase, that catches a citation number
`markdownlint-cli2`'s own `--fix` mangles once it opens a line:

- a `### ` heading repeated within the section -- measured against real
  rebases under `merge=union`, which writes what deleting the markers
  writes. Two branches each adding their *own* new heading, worded
  exactly alike, at the section's one shared anchor is *not* this
  shape: the merge folds the two into a single entry, one heading and
  both sides' bullets, with nothing for this check to find -- which is
  not a fix landing quietly, it is the shape the next check's own blind
  spot leans on. A heading repeats instead where the matching text does
  not end up adjacent once the merge is done -- one side's own further
  entry landing between the two closes the gap that would otherwise let
  them fold -- or where a single branch's new heading, no second branch or
  merge required, repeats one already in the section at its own base.
  `markdownlint-cli2` already refuses a same-level heading repeated
  anywhere in the file as MD024, `.markdownlint.jsonc` leaving that
  rule at its own default rather than the `siblings_only`
  bitcoin-core-rpc's, btclib's and btclib-secp256k1's `CHANGELOG.md`
  each set for their own, deliberate, per-release repeat; unlike MD022
  below, MD024 is not autofixable, so a run this check would also catch
  already fails on it. What this check adds is the line number scoped
  to the open section;
- two entries in the section that each `(closes #N)` the same number --
  btclib-org/btclib#1168 and btclib-org/btclib#1170 is the pair
  btclib-org/.github#21 opens with, each entry closing the same defect
  under a number of its own. Scoped to `closes` and not `issue`: an
  issue a change advances without closing is cited `(issue #N)` by
  design, and a long-lived issue is cited that way by several unrelated
  entries over as many weeks -- measured against this file's own
  history, which carries that repeat with nothing wrong in it. Closing
  the same issue twice has no such reading: `closes` names the entry
  that answers an issue for good, and an issue answered twice is what
  keeping both sides produces when two branches each believe they are
  first. A cross-repository citation, `(closes
  owner/repo#N)`, compares against another written exactly the same
  rather than against the number alone, since two different trackers
  numbering their own issues alike name two different issues;
- a `### ` heading with no blank line above it, which is the line
  deleting the markers loses at the seam where two sides' added lines
  abut (btclib-org/.github#760). `markdownlint-cli2` already reports
  this as MD022, but only as an autofix note -- "files were modified by
  this hook" is what a developer's terminal shows, the same sentence it
  prints for a stray trailing space, naming neither the conflict nor
  the rebase that lost the line. This check is the one thing in the
  gate that knows the difference and says so.

**What this cannot see.** Two entries citing *different* issue numbers
that are themselves duplicates of one another -- which is the actual
shape of #1168/#1170, one of the pair having been filed against an
issue the other already covered -- needs each number resolved and
compared through the tracker's own state, `closingIssuesReferences` or
an issue's `NOT_PLANNED` closure. That is one API call per citation, and
a `pre-commit` hook that reaches the network is the wrong place to put
one; btclib-org/.github#21's own ruling says so. Nor does this catch a
block misplaced within the open section, or a revived, previously-refuted
paragraph. That comparison splices the entry as it stood before the
rebase into the file at the new base and reads the result against the
rebased tip byte for byte; those two inputs are the rebase's own, and a
`pre-commit` hook sees neither.
Nor, for the reason the second check gives, does it see two entries that
merely *advance* the same issue without either closing it: the same issue
is cited `(issue #N)` across a tree's history by design.

Three more gaps, none of them the network one above, and none named
until this file's own review found them:

- the fold the first check leaves alone -- two branches' own
  identically-worded new headings, described above, united by the
  merge into one entry -- is exactly what hides a real double-close
  from the second check too. A citation repeated across one entry's own
  bullets is not reported by design, and a folded entry reads the same
  way: two different branches each closing the same issue under the one
  heading their merge united is indistinguishable, to this script, from
  one author citing an issue twice in one entry;
- a section with no `### ` heading at all -- prose bullets straight
  under the release heading with nothing this file's `_ENTRY_HEADING`
  matches -- leaves every check here vacuous rather than failing:
  nothing to repeat, nothing to split into entries, nothing to find a
  blank line above;
- two bullets from different entries that a rebase's seam leaves
  touching, with no blank line between them and no heading in sight.
  Valid CommonMark reads them as one list either way, so neither
  `markdownlint-cli2`'s MD022/MD032 nor this file's third check, both
  keyed on a heading's own blank line, has a line to object to.

The fourth check is an entry's length: section 9 of README.md bounds an
entry to its `### ` title and three lines of body, from the entry that
brought the rule in. Entries above the heading `RULE_HEADING` names
predate the rule and stay as written; where the open section no longer
holds that heading -- a release closed over it -- every entry is
measured. A heading-less entry is outside it, and outside the first
and third checks above, but not the second: `duplicate_closes` reads
the heading-less entry too, comparing its own citations against a
headed entry's.

That exemption is a trust, not a check: an entry above `RULE_HEADING`
is read as older than the rule because a new entry was appended after
it, and nothing before this fifth check verified that placement was
honoured. btclib-org/.github#1204 measured
what that costs -- a branch that landed an eighteen-line entry above
`RULE_HEADING`, in a file whose whole history sits above that heading,
passed `pre-commit run --all-files` clean, the fourth check never
reading an entry it believed predated the rule it postdated. The fifth
check is a count -- how many entries the open section held above
`RULE_HEADING` the day this check was added -- and a branch that only
ever appends below `RULE_HEADING` never grows that count on its own;
where the open section holds more, one has landed above it instead, and
this is refused for the placement rather than measured for the length.
The count is not an identity: it does not name which entry above the
line is the new one, and it does not see a grandfathered entry rewritten
in place without the count changing -- neither is the shape #1204
measured.

**The count is a fact about a repository's history rather than about
this script, so it arrives as `--grandfathered`** and the gate that
runs the hook is where each tree writes its own. The default is zero,
which is the answer for an open section holding no entry above
`RULE_HEADING` at all.

The sixth check is a citation number that opens a line at column zero:
`#<digits>`, the shape `markdownlint-cli2`'s MD018
(no-missing-space-atx) reads as an ATX heading missing its space.
`--fix` turns it into `# <digits>`, which is refused too: the citation
no longer matches `_CITATION_TOKEN` once the space is inserted, and the
now heading-shaped line goes on to trip MD022, MD025, MD026 and MD001 on
whatever heading follows -- none of which names the actual cause
(btclib-org/.github#1398). Measured directly against `markdownlint-cli2`
rather than assumed from MD018's name: a line indented by even one space
is not read as a heading at all and trips nothing, so the continuation a
list-item entry wraps to is outside this, and so is a bare paragraph's
wrap once it is indented to stay part of the paragraph above it -- only
a wrap that lands at the line's own first column is the shape that
mangles. A `### ` or `## ` heading opens with two or three hashes, not
one, so it is not this shape either; a fenced block is blanked out
before this ever runs, the same as for the checks above; and a qualified
citation, `owner/repo#N`, does not open the line with `#` at all, so
MD018 does not read it as a heading and this does not refuse it.

The six checks above read the file's first `## ` section: the newest
release, or, in a tree that releases nothing, the one section the file
holds, this repository's own `CHANGELOG.md` among them. They read
nothing an earlier release holds.

The seventh check is the one section 9 states: a pull request adds no
entry, and a release's section is written in the pull request that cuts
it. It reads every `### ` heading of the file against the merge base of
`HEAD` and `origin/main`, the base being that merge base because the
gate runs `pre-commit run --all-files`, which sets no from and to refs,
and `HEAD` already holds an entry the branch committed. A heading is
refused where the base does not hold it under that same `## ` heading,
unless that `## ` heading is a `## v<version>` (alone on its line) that the
base lacks. The check reads headings and not whether a release is real: a
diff that adds a `## v<version>` heading passes, and a reviewer sees it.

So an entry added under any release the base holds is refused, the
newest included, and so is one under a new heading that is no release.
A work-in-progress heading retitled to its release is a new release
heading and passes. A `### ` heading inside a fenced block is an example
and is not read.

A bullet added under a heading the base already holds is not seen.

Where git finds no merge base, or the base holds no `CHANGELOG.md`,
nothing is compared and the output says so. The manifest sets `verbose:
true`, so a run that passes shows that output too.

    check_changelog.py --grandfathered N
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# relative to the working directory, which `pre-commit` sets to the
# root of the repository being checked: this file is served from
# btclib-org/.github, so a path built from `__file__` would name the
# hook repository's own clone in the cache rather than the tree the
# hook was invoked over
_CHANGELOG = Path("CHANGELOG.md")
_MAIN = "origin/main"

_RELEASE_HEADING = re.compile(r"^## .*$", re.MULTILINE)
_ENTRY_HEADING = re.compile(r"^### (?P<title>.*)$", re.MULTILINE)
# a `## ` or `### ` heading, in file order
_ANY_HEADING = re.compile(
    r"^(?:## (?P<release>.*)|### (?P<title>.*))$",
    re.MULTILINE,
)
# a release: the heading text after `## ` is `v<version>` alone, as
# reusable-version-check.yml's release-only check requires of the tag's own
_VERSION_HEADING = re.compile(r"v\d+(\.\d+)*")
# a fenced code block, opened by a line of three or more backticks --
# tildes are not read: CommonMark allows them too, but `.markdownlint.jsonc`
# fixes this house style at MD048's default, backtick fences only -- with
# no backtick in the info string that follows them on the opening line,
# a backtick there being ambiguous with an inline code span, and closed
# by a line of at least as many backticks as the opening, which need not
# match its indentation. A `## ` or `### ` line inside one is a markdown
# example, not a heading of this file's own, and is blanked out before
# either pattern above ever runs (btclib-org/.github#1372). The closing
# fence is `\1` and not a second capture of the run's own length: a
# fence closes on a line with *at least* as many backticks as it opened
# with, not exactly as many, so a longer closing fence still closes the
# block and a shorter one is not mistaken for a close at all
_FENCED_BLOCK = re.compile(
    r"^ {0,3}(`{3,})[^`\n]*\n(?:.*\n)*?^ {0,3}\1`*[ \t]*$\n?",
    re.MULTILINE,
)
# a parenthetical naming an issue is not always spelled the same way
# twice in one entry -- "closes #593, issue #571", "issues #327, #339
# and #342" -- so this reads the whole group once either keyword is
# found in it, and two more patterns read the keywords and the tokens
# out of that group separately, a token taking whichever keyword sits
# nearest before it rather than the group's first
_CITATION_GROUP = re.compile(
    r"\((?P<body>[^()]*?\b(?:closes?|issues?)\b[^()]*?)\)",
    re.IGNORECASE | re.DOTALL,
)
_KEYWORD = re.compile(r"\b(closes?|issues?)\b", re.IGNORECASE)
_CITATION_TOKEN = re.compile(r"(?:[\w.-]+/[\w.-]+)?#\d+")
# a code span quotes a citation's own shape as an example of prose --
# this file explains the standard's citation rules -- rather than citing
# anything itself; stripped before either pattern above ever sees it.
# Single backticks, not crossing a blank line: this house style's own
# code spans do not
_CODE_SPAN = re.compile(r"`[^`\n]*`")
# a citation's own number, wrapped so it opens a line at column zero --
# `#\d+`, or `# \d+` where markdownlint-cli2's MD018 has already turned
# the missing space into one. A `##`/`###` heading never matches: its
# second character is itself a `#`, where `[ \t]?\d+` wants a space, a
# tab or a digit there instead; the leading `^` with no `\s*` ahead of
# it excludes an indented line, measured against `markdownlint-cli2` to
# trip nothing at all, which is every wrap a list-item entry or an
# indented paragraph continuation produces
_WRAPPED_CITATION = re.compile(r"^#[ \t]?\d+\b", re.MULTILINE)

_BLANK_LINE = "\n\n"
"""Two newlines: the empty line above a heading, read as a literal pair."""

RULE_HEADING = "A changelog entry is its title and at most three lines"
"""The entry section 9's bound enters with; entries above it predate it."""
_MAX_BODY_LINES = 3
# a reference-style link definition is plumbing an entry's text points
# at, not a line of the entry; btclib-benchmarks keeps a block of them at
# the end of the file, inside whatever entry is last
_LINK_DEFINITION = re.compile(r"^\[[^\]]+\]:\s")


def _blank_fenced_blocks(text: str) -> str:
    """Return `text` with each fenced code block's own characters blanked.

    Every newline stays where it was and every other character of a
    fenced block becomes a space, so the result is the same length as
    `text` and `line_at()` reports the same line for the same offset in
    either -- unlike `_CODE_SPAN.sub("", body)` below, which shortens
    what it strips because nothing downstream of it depends on an
    offset into the original file.

    :param text: the whole file, or one of its sections.
    :returns: `text`, with each fenced block's own characters replaced.
    """

    def _blank(match: re.Match[str]) -> str:
        return "".join(char if char == "\n" else " " for char in match.group(0))

    return _FENCED_BLOCK.sub(_blank, text)


def open_section(text: str) -> tuple[str, int]:
    """Return the file's open section, and the offset it starts at.

    :param text: the whole file.
    :returns: the text from the first `## ` heading's line to the line
        before the second, or to the end where there is no second; and
        the offset into `text` that text begins at.
    """
    headings = list(_RELEASE_HEADING.finditer(_blank_fenced_blocks(text)))
    if not headings:
        return text, 0
    start = headings[0].end()
    end = headings[1].start() if len(headings) > 1 else len(text)
    return text[start:end], start


def line_at(text: str, offset: int) -> int:
    """Return the 1-based line of `text` that `offset` falls on.

    :param text: the whole file the offset is into.
    :param offset: a character offset into `text`.
    :returns: the line number.
    """
    return text.count("\n", 0, offset) + 1


def closing_tokens(body: str) -> set[str]:
    """Return every issue token a `closes`/`closed` citation names.

    Scoped to that keyword and not to `issue`: section 9 of README.md
    lets a branch advance an issue under `(issue #N)` without closing
    it, so the same number recurs wherever a long-lived issue is
    answered across several entries over as many weeks -- normal, and
    not what this asks about. A token takes
    whichever keyword sits nearest before it in its own parenthetical,
    so `(closes #593, issue #571)` reads only the first as closed. A
    code span is stripped first, so an entry quoting a citation's shape
    as an example -- this file explains what one looks like -- is not
    read as making one of its own.

    :param body: the text to search -- an entry's heading and body both.
    :returns: each closed token, as written: `#N` or `owner/repo#N`.
    """
    body = _CODE_SPAN.sub("", body)
    tokens: set[str] = set()
    for group in _CITATION_GROUP.finditer(body):
        text = group.group("body")
        keywords = list(_KEYWORD.finditer(text))
        for token in _CITATION_TOKEN.finditer(text):
            before = [k for k in keywords if k.start() < token.start()]
            if before and before[-1].group(1).lower().startswith("close"):
                tokens.add(token.group(0))
    return tokens


def entries(section: str) -> list[tuple[str | None, str, int]]:
    """Split the open section into its entries.

    A `### ` heading names one entry, section 9 of README.md's own rule,
    so a heading and everything under it -- up to the next heading or
    the section's end -- is one entry. Content above the first heading
    is a tree whose convention has no `### `, or an open section that
    has not taken its first entry yet; it is read as a single entry
    with no title, there being nothing in a heading-less section to say
    where one such entry ends and the next begins.

    :param section: the open section's own text.
    :returns: each entry's heading text (`None` where it has none), its
        own span -- heading line included, where it has one -- and the
        offset that span starts at within `section`.
    """
    headings = list(_ENTRY_HEADING.finditer(_blank_fenced_blocks(section)))
    out: list[tuple[str | None, str, int]] = []
    preamble_end = headings[0].start() if headings else len(section)
    preamble = section[:preamble_end]
    if preamble.strip():
        out.append((None, preamble, 0))
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(section)
        out.append(
            (
                heading.group("title").strip(),
                section[heading.start() : end],
                heading.start(),
            ),
        )
    return out


def repeated_headings(text: str, section: str, base: int) -> list[str]:
    """Report a `### ` heading that repeats one already seen.

    :param text: the whole file, for the line numbers reported.
    :param section: the open section's own text.
    :param base: the offset `section` starts at within `text`.
    :returns: one message per repeat.
    """
    seen: dict[str, int] = {}
    problems = []
    for heading in _ENTRY_HEADING.finditer(_blank_fenced_blocks(section)):
        title = heading.group("title").strip()
        line = line_at(text, base + heading.start())
        if title in seen:
            problems.append(
                f"line {line}: heading {title!r} repeats the heading at"
                f" line {seen[title]}",
            )
        else:
            seen[title] = line
    return problems


def duplicate_closes(text: str, section: str, base: int) -> list[str]:
    """Report two entries of the open section closing the same issue.

    A citation repeated across the bullets of *one* entry is not
    reported: section 9 of README.md has the body cite the issue in its
    own text, so a list body cites it in each bullet that claims
    something of it. What this asks is whether two different entries --
    two different `### ` headings, or the one heading-less entry
    against a headed one -- each `(closes #N)` the same issue, which
    keeping both sides of a conflicted append is what produces.

    :param text: the whole file, for the line numbers reported.
    :param section: the open section's own text.
    :param base: the offset `section` starts at within `text`.
    :returns: one message per repeat.
    """
    first_seen: dict[str, tuple[str, int]] = {}
    problems = []
    for title, body, offset in entries(section):
        line = line_at(text, base + offset)
        label = f"heading {title!r}" if title is not None else "the heading-less entry"
        for token in sorted(closing_tokens(body)):
            if token in first_seen:
                other_label, other_line = first_seen[token]
                problems.append(
                    f"line {line}: {label} closes {token}, already closed by"
                    f" {other_label} at line {other_line}",
                )
            else:
                first_seen[token] = (label, line)
    return problems


def unblanked_headings(text: str, section: str, base: int) -> list[str]:
    """Report a `### ` heading with no blank line directly above it.

    :param text: the whole file, for the line numbers reported.
    :param section: the open section's own text.
    :param base: the offset `section` starts at within `text`.
    :returns: one message per heading found glued to the line above it.
    """
    problems = []
    for heading in _ENTRY_HEADING.finditer(_blank_fenced_blocks(section)):
        pos = heading.start()
        above = section[max(pos - len(_BLANK_LINE), 0) : pos]
        if above != _BLANK_LINE:
            line = line_at(text, base + pos)
            title = heading.group("title").strip()
            problems.append(
                f"line {line}: heading {title!r} has no blank line above"
                " it -- the line deleting a conflict's markers loses",
            )
    return problems


def misplaced_entries(
    text: str,
    section: str,
    base: int,
    grandfathered: int = 0,
) -> list[str]:
    """Report more entries above `RULE_HEADING` than were grandfathered.

    `long_bodies()` below reads an entry above `RULE_HEADING` as older
    than the rule, on the strength of a placement rule -- a new entry
    goes below it -- which nothing else here checks. A branch that only
    ever appends below `RULE_HEADING` never grows the count of entries
    above it; where the open section holds more than `grandfathered`
    names, one has landed above it instead, and is refused here rather
    than silently read as predating a rule it postdates.

    :param text: the whole file, for the line number reported.
    :param section: the open section's own text.
    :param base: the offset `section` starts at within `text`.
    :param grandfathered: how many entries the open section held above
        `RULE_HEADING` when this check reached the repository, which
        `main()` takes on the command line.
    :returns: one message, naming `RULE_HEADING`'s own line, where the
        section holds more entries above it than were grandfathered.
    """
    before = 0
    rule_offset = None
    for title, _, offset in entries(section):
        if title == RULE_HEADING:
            rule_offset = offset
            break
        if title is not None:
            before += 1
    if rule_offset is None or before <= grandfathered:
        return []
    line = line_at(text, base + rule_offset)
    message = (
        f"line {line}: {before} entries land above the rule heading, more"
        f" than the {grandfathered} this repository grandfathers --"
        " an entry has landed above it instead of below it"
    )
    return [message]


def long_bodies(text: str, section: str, base: int) -> list[str]:
    """Report an entry whose body runs past `_MAX_BODY_LINES` non-blank lines.

    Measured from the entry titled `RULE_HEADING` onward, and from the
    section's first entry where that heading is not in it. A blank line
    and a reference-style link definition are not lines of the body.

    :param text: the whole file, for the line numbers reported.
    :param section: the open section's own text.
    :param base: the offset `section` starts at within `text`.
    :returns: one message per entry past the bound.
    """
    found = entries(section)
    measuring = all(title != RULE_HEADING for title, _, _ in found)
    problems = []
    for title, body, offset in found:
        measuring = measuring or title == RULE_HEADING
        if not measuring or title is None:
            continue
        kept = [
            line
            for line in body.splitlines()[1:]
            if line.strip() and not _LINK_DEFINITION.match(line)
        ]
        if len(kept) > _MAX_BODY_LINES:
            line = line_at(text, base + offset)
            problems.append(
                f"line {line}: heading {title!r} has {len(kept)} lines of body,"
                f" section 9 allowing {_MAX_BODY_LINES}",
            )
    return problems


def wrapped_citations(text: str, section: str, base: int) -> list[str]:
    """Report a citation number that has wrapped to the start of a line.

    `(closes #N)` / `(issue #N)` wraps at 80 columns like any other
    prose, and where the wrap lands the number at a line's own first
    column, `markdownlint-cli2`'s MD018 reads the bare `#N` as an ATX
    heading missing its space and `--fix` inserts one, so `#2291).`
    becomes `# 2291).` -- still refused here, since the citation is
    unrecognisable to `_CITATION_TOKEN` either way and the now
    heading-shaped line goes on to trip MD022, MD025, MD026 and MD001 on
    the next real heading, none of them naming the actual cause
    (btclib-org/.github#1398).

    :param text: the whole file, for the line numbers reported.
    :param section: the open section's own text.
    :param base: the offset `section` starts at within `text`.
    :returns: one message per line found opening with a citation number.
    """
    problems = []
    for match in _WRAPPED_CITATION.finditer(_blank_fenced_blocks(section)):
        line = line_at(text, base + match.start())
        problems.append(
            f"line {line}: {match.group(0)!r} opens the line -- a citation"
            " number wrapped to a line's start, which markdownlint-cli2's"
            " MD018 reads as a heading missing its space and mangles;"
            " rejoin it to the line above",
        )
    return problems


def entries_by_release(text: str) -> list[tuple[str | None, str, int]]:
    """Read each `### ` heading with the `## ` heading it sits under.

    :param text: the whole file.
    :returns: each entry's release heading's text (`None` above the
        first), its own title, and the offset of its line.
    """
    release: str | None = None
    found = []
    for heading in _ANY_HEADING.finditer(_blank_fenced_blocks(text)):
        if heading.group("release") is not None:
            release = heading.group("release").strip()
        else:
            found.append((release, heading.group("title").strip(), heading.start()))
    return found


def entries_outside_a_release(text: str, base: tuple[str, str]) -> list[str]:
    """Report a `### ` heading new to a release the base already holds.

    A heading is new where the base does not hold it under the same `## `
    heading. It is allowed where its `## ` heading is a release,
    `## v<version>` alone, that the base does not hold either: the
    release cut in this very diff.

    :param text: the whole file.
    :param base: the merge base's sha, and the whole file there.
    :returns: one message per entry written outside a release's own pull
        request.
    """
    sha, before = base
    held = {(release, title) for release, title, _ in entries_by_release(before)}
    old_releases = {
        heading.group("release").strip()
        for heading in _ANY_HEADING.finditer(_blank_fenced_blocks(before))
        if heading.group("release") is not None
    }
    problems = []
    for release, title, offset in entries_by_release(text):
        if (release, title) in held:
            continue
        if (
            release is not None
            and release not in old_releases
            and _VERSION_HEADING.fullmatch(release)
        ):
            continue
        where = f"under {release!r}"
        if release is None:
            where = "above the first release heading"
        problems.append(
            f"line {line_at(text, offset)}: heading {title!r} is new {where},"
            f" in a file whose base {sha} (the merge base with {_MAIN}) does"
            " not hold it there -- an entry is written in the pull request"
            " that cuts its release (section 9)",
        )
    return problems


def at_merge_base() -> tuple[str, str] | None:
    """Return the merge base of `HEAD` and `_MAIN`, and `CHANGELOG.md` there.

    :returns: the sha and the file, or None where git finds no merge
        base or the base holds no such file.
    """

    def git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(  # noqa: S603
            ["git", "-C", str(_CHANGELOG.parent), *args],  # noqa: S607
            capture_output=True,
            encoding="utf-8",
            check=False,
        )

    base = git("merge-base", "HEAD", _MAIN)
    if base.returncode:
        return None
    sha = base.stdout.strip()
    shown = git("show", f"{sha}:./{_CHANGELOG.name}")
    return None if shown.returncode else (sha, shown.stdout)


def problems(
    text: str,
    grandfathered: int = 0,
    base: tuple[str, str] | None = None,
) -> list[str]:
    """Return every way the file fails the checks.

    :param text: the whole file.
    :param grandfathered: what `misplaced_entries()` measures against.
    :param base: the merge base's sha and the whole file there, or None
        where there is none to compare against.
    :returns: one message per finding, in the order the checks run.
    """
    section, start = open_section(text)
    return [
        *repeated_headings(text, section, start),
        *duplicate_closes(text, section, start),
        *unblanked_headings(text, section, start),
        *misplaced_entries(text, section, start, grandfathered),
        *long_bodies(text, section, start),
        *wrapped_citations(text, section, start),
        *(entries_outside_a_release(text, base) if base is not None else []),
    ]


def main(argv: Sequence[str] | None = None) -> int:
    """Report every problem `CHANGELOG.md` has.

    :param argv: the arguments, `sys.argv[1:]` where none is given.
    :returns: 1 where a problem was found, 0 where the file is clean.
    """
    parser = argparse.ArgumentParser(
        description="Refuse a CHANGELOG.md section a rebase conflict can"
        " break, a citation number markdownlint-cli2's own fixer mangles,"
        " or an entry written outside a release's own pull request.",
    )
    parser.add_argument(
        "--grandfathered",
        type=int,
        default=0,
        metavar="N",
        help=(
            "how many entries this repository's open section held above"
            " the rule heading when the fifth check reached it; an entry"
            " past that count has landed above it"
        ),
    )
    arguments = parser.parse_args(argv)
    base = at_merge_base()
    found = problems(
        _CHANGELOG.read_text(encoding="utf-8"),
        arguments.grandfathered,
        base,
    )
    for problem in found:
        print(f"{_CHANGELOG}: {problem}")
    if not found:
        print(
            f"{_CHANGELOG}: the open section repeats no heading, no two"
            " entries close the same issue, no heading has lost its blank"
            " line, no entry lands above the rule out of place, no entry"
            " runs past three lines, and no citation number opens a line.",
        )
    if base is None:
        print(
            f"{_CHANGELOG}: no entry compared with the base: no merge base with"
            f" {_MAIN}, or no such file there.",
        )
    elif not found:
        print(f"{_CHANGELOG}: no entry is new outside a release's own section.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
