# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The alignment suite: whether the repositories still agree with README.md.

Section 7 of README.md says a test never reaches the network, and every
test here that asks about another repository does. That is the whole
reason this suite is in this repository rather than spread across the
others: what it measures is agreement with the standard, and the
standard is here. A test in a repository's own tree answers for that
repository's reading of a rule on the day it was written; a test here
reads the rule as the file states it now, and asks it of every
repository at once. Section 15 of that file is the audit this is the
running half of.

A test that takes a `repository` argument is asked once per repository,
`conftest.py` parametrizing it at collection, and this module says
which tier of repository a question reaches and which failures the
tracker already records. A test that takes the session fixtures instead
asks what no single tree can answer -- the calendar, the verbatim
copies -- and runs once.

Each test that reaches GitHub is marked `integration`, which is how a
run selects or deselects them by name -- a module whose subject is this
tree rather than the organization asks nothing of GitHub and carries
none; what skips the suite without `BTCLIB_INTEGRATION` in the
environment is `conftest.py` at collection, a marker being a label
rather than a condition::

    BTCLIB_INTEGRATION=1 uv run --locked --group test pytest

The shared code is here rather than in modules of its own, for the
reason section 7 gives: `name-tests-test` runs at its default, so every
Python file under `tests/` is a test file but the two basenames the hook
exempts, and a helper named any other way is what the hook refuses --
a test spelled some other way, or shared code in the wrong file. What is
shared is these parts:

- **the organization, and how this suite asks GitHub about it** --
  `ORG`, `SELF`, `ROOT`, `output` and the bound it holds a call to, the
  two `gh` callers, `by_hand` and `tracked`;
- **which repositories the standard applies to, how far, and what is
  owed** -- kept together, so that a change to any of them is made in
  one place: *which repositories
  there are*, asked of the API rather than listed, for the reason
  `names` gives; *how far the standard reaches each one*, section 2's
  tier, measured off the tree by the two files that section names, the
  section's own table being a claim `tiers_test.py` checks against this
  measurement; and *which findings are already filed*, the backlog,
  one row per issue, so that a failure the tracker knows about is
  reported as expected and a repository that catches up is reported as
  a row to delete, `xfail_strict` in `pyproject.toml` being what turns
  the second into a failure;
- **reading a table of README.md as data** -- section 10's calendar is
  prose a person reads and a rule a machine has to enforce, and those
  are the same table rather than two copies of it: the file is the
  source, `rows` is how the suite reads it. A row added there is
  checked from the moment it is added, and a row nobody maintains
  fails against the trees instead of going quietly stale. A list of
  that file is read the same way: `bulleted` returns its bullets, and
  `subjects` keys them by the subject each opens with, which is how
  section 10's record of which trees carry which sentinel, section 14's
  paths and section 7's conventions are read.
"""

from __future__ import annotations

import enum
import functools
import json
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any, override

ORG = "btclib-org"

SELF = ".github"
"""The organization's profile repository, and the tree this file is in.

Cloning it would fetch a second copy of what is already on the machine,
and the wrong copy: a pull request that edits the calendar has to be
checked against the calendar it proposes. The `trees` fixture maps this
name to `ROOT` instead.
"""

ROOT = Path(__file__).parents[1]

TIMEOUT = 60
"""The seconds a call may take before it is a hang rather than a wait.

A run's first fetch is made at collection, `conftest.py` parametrizing
the per-repository tests over the names the API answers with, and
`pytest-timeout`'s per-test bound does not reach there: it is installed
in `pytest_runtest_protocol`, which runs once an item exists. Unbounded,
a call that never returns ends the run with `alignment.yml` cancelled at
its `timeout-minutes`, naming the job and no test, so what covers
collection is a bound on the call.

Under `pyproject.toml`'s `timeout`, so that a call hanging inside a test
is reported as the command that hung rather than as whichever test was
being asked when it did; and far over what a call here takes, which

    time gh api 'orgs/btclib-org/repos?per_page=100' --paginate

measures, so that a slow answer is not turned into a finding about the
organization.
"""


class Refused(subprocess.CalledProcessError):
    """A `gh` or `git` call that came back non-zero, saying what it said.

    The reason a call failed is on standard error, and
    `CalledProcessError` carries the exit status alone into pytest's
    report: a 404, a revoked token and a secondary rate limit read
    alike there. This says what the tool said, and names the command
    the way `by_hand` does, as a line the reader can take to a
    terminal.

    A `CalledProcessError` still, so that a caller telling one refusal
    from another reads `stderr` off it as before.
    """

    @override
    def __str__(self) -> str:
        return f"{shlex.join(self.cmd)} exited {self.returncode}: {self.stderr.strip()}"


def output(*command: str) -> str:
    """Run a command that has to answer, and return what it wrote.

    What a failure raises is `Refused` and not an assertion: the
    backlog's rows are strict expected failures keyed on
    `AssertionError`, so an assertion here would be excused as the
    finding a row records -- reported as an expected failure, in a green
    run, whether it was raised in a test's body or in a fixture that
    test asked for. A refused API call is neither the finding nor
    expected.

    A wait past `TIMEOUT` raises `subprocess.TimeoutExpired`, whose own
    message names the command and the bound it passed.

    :param command: the argument list, run without a shell.
    :returns: what the command wrote to standard output.
    :raises Refused: where the command comes back non-zero.
    """
    completed = subprocess.run(
        command,
        capture_output=True,
        check=False,
        encoding="utf-8",
        timeout=TIMEOUT,
    )
    if completed.returncode:
        raise Refused(completed.returncode, command, completed.stdout, completed.stderr)
    return completed.stdout


def gh(endpoint: str, jq: str) -> list[str]:
    """Ask the GitHub API and return one line of its answer per element.

    :param endpoint: the path after `gh api`, its query string included.
    :param jq: the `--jq` filter, whose output is split on newlines.
    :returns: the non-empty lines, in the order the API answered.
    """
    out = output("gh", "api", endpoint, "--paginate", "--jq", jq)
    return [line for line in out.splitlines() if line]


# the API's own answer, its shape different at every call site: a
# document, a list of them, a bare string. Any is what that is, not a
# narrower type this function would have to lie about.
def gh_json(endpoint: str) -> Any:  # noqa: ANN401
    """Ask the GitHub API for one document and parse it.

    :param endpoint: the path after `gh api`.
    :returns: whatever the endpoint answers, parsed.
    """
    return json.loads(output("gh", "api", endpoint))


def by_hand(repository: str, command: str) -> str:
    """Say how a failure is decided without this suite.

    Section 15 gives every question of the standard as a command a
    person runs in one checkout, and a failure here names that command
    so the reader can take it there: the message is the section's line
    for that repository rather than a restatement of it.

    :param repository: the repository the assertion was asked of.
    :param command: the shell that decides it in a checkout of that tree.
    :returns: the text an assertion message ends with.
    """
    return f"by hand, in a checkout of {ORG}/{repository}: {command}"


def tracked(root: Path, *patterns: str) -> list[str]:
    """List the files a tree tracks under some pathspecs.

    `git ls-files` rather than a walk, so a checkout's own environment
    -- the `.venv` this tree keeps beside its suite -- is not read as
    part of it.

    :param root: the root of the checkout.
    :param patterns: git pathspecs, `*.toml` and the like.
    :returns: the paths, relative to the root, in git's order.
    """
    return output("git", "-C", str(root), "ls-files", "--", *patterns).splitlines()


class Tier(enum.IntEnum):
    """Section 2's three tiers, numbered as that section numbers them.

    Tier 1 owes the whole file and tier 3 the least, so the number goes
    up as what is owed goes down. A test names the tier it applies down
    to, and a repository of a higher number is skipped with the reason
    rather than failed: a checklist about a wheel is not a finding
    against a tree that builds none.
    """

    PUBLISHER = 1
    """A Python package that publishes, which is the standard entire."""

    PYTHON = 2
    """A Python project that publishes nothing."""

    ANY = 3
    """Any repository, whatever it is written in."""

    def binds(self, repository_tier: Tier) -> bool:
        """Say whether a rule of this tier reaches a repository of that one.

        :param repository_tier: the repository's tier.
        :returns: whether the repository owes what this tier owes.
        """
        return repository_tier <= self


def tier(root: Path) -> Tier:
    """Measure a repository's tier off its tree, as section 2 does.

    A repository is Python where it holds a `pyproject.toml`, and
    publishes where it holds `release.yml`; the section's loop asks the
    API for the same two files.

    :param root: the root of the checkout.
    :returns: the tier the tree answers to.
    """
    if not (root / "pyproject.toml").is_file():
        return Tier.ANY
    if (root / ".github" / "workflows" / "release.yml").is_file():
        return Tier.PUBLISHER
    return Tier.PYTHON


@functools.cache
def names() -> list[str]:
    r"""Ask the API for every repository, rather than listing them here.

    A list written down here would be one more place to remember a new
    repository, and the one place nobody would think to look: a tree that
    joins the organization is in scope for this suite the moment it
    exists. Archived repositories are out -- what they agree with is the
    standard of the day they were archived.

    Forks are out too, a fork's conventions being upstream's. That
    argument fails for a fork the organization has taken over, whose
    commits since the takeover are its own and whose downstream forks
    are of this copy rather than of the original: excluding such a tree
    silences the suite about the one repository the argument is wrong
    about.

    The organization holds no fork, so the filter selects nothing out
    and is a guard rather than a description::

        gh api 'orgs/btclib-org/repos?per_page=100' \
          --jq '[.[] | select(.fork == true)] | length'

    What it asks about is a state, not how a tree reached it: a
    repository detached from its upstream and one rebuilt from scratch
    answer it alike.

    Cached, because the list is read once at collection to parametrize
    the per-repository tests and once more by the `repositories` fixture,
    and the two have to be the same list.

    :returns: the repository names, `.github` among them.
    """
    return gh(
        f"orgs/{ORG}/repos?per_page=100",
        ".[] | select(.archived == false and .fork == false) | .name",
    )


BACKLOG: tuple[tuple[int, str, tuple[str, ...]], ...] = (
    (
        551,
        "test_the_settings_file_does_not_claim_to_be_the_whole_of_them",
        ("portanode",),
    ),
    (
        565,
        "test_the_settings_file_says_what_it_passes_over",
        ("portanode",),
    ),
    # deps-oldest: these trees are short of the workflow; btclib-node
    # schedules it (btclib-org/btclib-node#739)
    (
        323,
        "test_a_tree_carries_the_sentinels_its_entries_give_it",
        (
            "bitcoin-core-rpc",
            "btclib",
            "btclib-benchmarks",
            "btclib-secp256k1",
        ),
    ),
    # sdist-rebuild: the row landed ahead of the trees it names
    (
        523,
        "test_a_tree_carries_the_sentinels_its_entries_give_it",
        (
            "bitcoin-core-rpc",
            "btclib",
            "btclib-secp256k1",
        ),
    ),
    # the uv floor: each of these sits below the ceiling
    # dependabot-core's uv/Dockerfile pins, and the row goes with the
    # bump
    (
        448,
        "test_the_uv_floor_is_what_dependabot_bundles",
        (
            ".github",
            "bbt",
            "bitcoin-core-rpc",
            "btclib",
            "btclib-benchmarks",
            "btclib-node",
            "btclib-secp256k1",
        ),
    ),
)
"""What the tracker already knows, read by `conftest.py` at collection.

The number is an issue of this repository's own tracker, which is what
`conftest.py`'s `cited()` spells it as. A row keyed on a number from a
tree this suite measures is not caught: those trackers number in the
same range, so the citation names a real issue about something else.

Empty is where this returns rather than where it always is: a row is an
exemption, and the rows are strict expected failures so that a
repository catching up is *reported* rather than quietly excused.
Nothing here is a place a new failure belongs -- a red cell is answered
in the tree that is red, and a row is what says the answer is already
written down and waiting.
"""


def filed(test: str, repository: str) -> list[int]:
    """Return the issues recording that a test fails on a repository.

    :param test: the test function's name.
    :param repository: the repository's name.
    :returns: the issue numbers, empty where none is filed.
    """
    return [
        issue
        for issue, subject, repositories in BACKLOG
        if subject == test and repository in repositories
    ]


def rows(document: Path, *columns: str) -> list[dict[str, str]]:
    """Read the one markdown table whose header is exactly these columns.

    :param document: the markdown file to read.
    :param columns: the header cells, in order, naming the table.
    :returns: one mapping per body row, column name against cell text.
    :raises LookupError: if no table, or more than one, has that header.
    """
    header = "| " + " | ".join(columns) + " |"
    lines = document.read_text(encoding="utf-8").splitlines()
    starts = [i for i, line in enumerate(lines) if line == header]
    if len(starts) != 1:
        msg = f"{document.name} has {len(starts)} tables headed {header}"
        raise LookupError(msg)
    out: list[dict[str, str]] = []
    # the header, then the delimiter row, then the body until a line that
    # is not a row -- a blank line, prose, or the next table's header
    for line in lines[starts[0] + 2 :]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        out.append(dict(zip(columns, cells, strict=True)))
    return out


def name(cell: str) -> str:
    """Take the name out of a cell that quotes it as code.

    :param cell: the cell text, `like this` or plain.
    :returns: the text with the backticks removed.
    """
    return cell.strip("`")


SUBJECT = re.compile(r"^- `([^`]+)` — (.+)")
"""How a bullet of a list this module reads names what it is about.

The backticks and the spaced em dash are the shape, and a bullet written
any other way is one this cannot answer for. What follows the dash is
the rest of the bullet, for a caller reading the clause it opens with.
"""

EMPHASISED = re.compile(r"^- \*\*([^*]+)\*\* — (.+)")
"""The same shape where the subject is prose rather than a name.

A list whose subjects are paths quotes them as code, and section 7's
conventions are phrases of English -- *the public surface*, *the
changelog* -- which the file emphasises instead. Which of the two a
list uses is the document's to choose, so it is the caller's to pass.
"""


def sole(document: Path, lines: list[str], text: str) -> int:
    """Return the index of the one line holding a piece of prose.

    :param document: the file the lines came from, for the message.
    :param lines: the file's lines.
    :param text: the substring naming the line.
    :returns: the index of the line holding it.
    :raises LookupError: if no line, or more than one, holds it.
    """
    found = [i for i, line in enumerate(lines) if text in line]
    if len(found) != 1:
        msg = f"{document.name} has {len(found)} lines holding {text!r}"
        raise LookupError(msg)
    return found[0]


def fenced(document: Path, opening: str, language: str) -> str:
    """Read the one fenced block of a language that a section shows.

    A block a section gives as the configuration to copy is what the
    trees are compared against, so it is read rather than transcribed:
    a transcription is the copy that goes stale.

    A block is a line that is exactly the opening fence, a run of lines,
    and a line that is exactly ``` — at column zero and with nothing
    trailing, which is every fence this file's markdownlint accepts. A
    fence the section opens and does not close is no block: it would
    otherwise read to the end of the file, past the section that was
    asked for, and return that.

    :param document: the markdown file to read.
    :param opening: a substring of the line the section opens with.
    :param language: the fence's language, `toml` and the like.
    :returns: the block's text, the fences excluded.
    :raises LookupError: if the section does not hold exactly one.
    """
    lines = document.read_text(encoding="utf-8").splitlines()
    fence = f"```{language}"
    blocks: list[list[str]] = []
    inside = False
    for line in lines[sole(document, lines, opening) + 1 :]:
        if line.startswith("## ") and not inside:
            break
        if not inside and line == fence:
            inside = True
            blocks.append([])
        elif inside and line == "```":
            inside = False
        elif inside:
            blocks[-1].append(line)
    if inside:
        blocks.pop()
    if len(blocks) != 1:
        msg = f"{document.name} has {len(blocks)} {fence} blocks under {opening!r}"
        raise LookupError(msg)
    return "\n".join(blocks[0]) + "\n"


def bulleted(document: Path, opening: str, closing: str) -> list[str]:
    """Read the list between two lines, one string per bullet.

    A bullet is its own line and every indented line after it, which is
    how a bullet wraps at the margin, so a caller matching a pattern
    against what comes back is asking about the bullet rather than about
    where the file broke the line. `opening` and `closing` are the prose
    either side of the list, so moving it within its section does not
    need the caller changed.

    :param document: the markdown file to read.
    :param opening: a substring of the line the list follows.
    :param closing: a substring of the line the list stops at.
    :returns: the bullets, in the order the list gives them.
    :raises LookupError: where either end is not found exactly once, or
        the closing line comes before the opening one.
    """
    lines = document.read_text(encoding="utf-8").splitlines()
    start = sole(document, lines, opening)
    end = sole(document, lines, closing)
    if end < start:
        msg = f"{document.name} holds {closing!r} before {opening!r}"
        raise LookupError(msg)
    bullets: list[str] = []
    for line in lines[start + 1 : end]:
        if line.startswith("- "):
            bullets.append(line)
        elif line.startswith("  ") and bullets:
            bullets[-1] += " " + line.strip()
    return bullets


def subjects(
    document: Path, opening: str, closing: str, pattern: re.Pattern[str] = SUBJECT
) -> dict[str, str]:
    """Read every bullet between two lines, by the subject it opens with.

    A bullet's subject is what it is about, and a list whose subjects are
    paths is a list a test can act on; what the bullet then says about it
    is the caller's to read, `bulleted` being what reads the list itself.

    Every way of reading nothing here is an error rather than an empty
    answer, for the reason `rows` refuses a header it finds twice: a
    caller that gets `{}` compares no files and reports that as
    agreement. So both ends have to be found exactly once and in that
    order, the list between them has to hold a bullet, and every bullet
    it holds has to carry a subject of its own -- a list rewritten into a
    shape this cannot read is the failure, not a run that quietly checks
    nothing. Of its own, because a subject named twice would leave one
    bullet read and the other dropped, which is the same silence one
    line down.

    :param document: the markdown file to read.
    :param opening: a substring of the line the list follows.
    :param closing: a substring of the line the list stops at.
    :param pattern: how a bullet of this list names its subject.
    :returns: each subject against the rest of its bullet, the lines it
        wraps over joined by a space, in the order the list gives them.
    :raises LookupError: where either end is not found exactly once, the
        closing line comes first, a bullet between them names no subject
        the pattern reads, or two bullets carry the same one.
    """
    read: list[tuple[str, str]] = []
    unread: list[str] = []
    for bullet in bulleted(document, opening, closing):
        found = pattern.match(bullet)
        if found:
            read.append((found.group(1), found.group(2)))
        else:
            unread.append(bullet)
    out = dict(read)
    if unread or not out or len(out) != len(read):
        msg = (
            f"{document.name} names {len(read)} bullets between {opening!r}"
            f" and {closing!r}, {len(out)} of them by a subject of their"
            f" own, and these name none: {unread}"
        )
        raise LookupError(msg)
    return out
