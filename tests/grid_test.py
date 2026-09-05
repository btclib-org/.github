# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Every scheduled run in the organization is on section 10's calendar.

The calendar is two tables: a workflow owns a day and an hour, a
repository owns the minute. Between them they name an instant for every
`cron:` in the organization, and this is what says so -- a row that
drifts from the trees, or a tree that drifts from the rows, fails here
rather than being noticed the week a notification arrives on the wrong
day.

The record beside the calendar, section 10's *Which trees carry which
sentinel*, is read here too, against each tree's `.github/workflows/`:
an entry names the trees carrying a sentinel, and a tree short of one
its entry names, or carrying one no entry gives it, is the pair of
findings section 10 states beside the record, reported per tree.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import ORG, ROOT, SELF, bulleted, by_hand, name, rows, still_open, subjects
from .workflows_test import workflows

if TYPE_CHECKING:
    from pathlib import Path

# cron numbers the weekday from Sunday, and the table spells the day out
WEEKDAYS = {
    "Sunday": 0,
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6,
}

FIELDS = 5
"""How many fields a cron expression has. Not a choice of anybody's."""

pytestmark = pytest.mark.integration


def calendar() -> dict[str, tuple[str, str]]:
    """Read the workflow table of section 10.

    :returns: each workflow name against its day and its hour.
    """
    return {
        name(row["workflow"]): (row["day"], row["hour"])
        for row in rows(ROOT / "README.md", "workflow", "day", "hour")
    }


def minutes() -> dict[str, str]:
    """Read the repository table of section 10.

    :returns: each repository name against its minute.
    """
    return {
        name(row["repository"]): row["minute"]
        for row in rows(ROOT / "README.md", "repository", "minute")
    }


RECORD = (
    "This is the record: one entry per calendar row",
    "**An entry is what was decided, not what a tree happens to hold**",
)
"""The prose either side of section 10's record, as `subjects` wants it."""

EVERY = "every repository"
"""How an entry names the whole organization rather than listing it."""

TREE = re.compile(r"`[^`]+`")
"""How an entry spells one tree: its name, quoted as code."""


def record() -> dict[str, list[str]]:
    """Read section 10's record of which trees carry which sentinel.

    An entry's clause is its trees, each quoted as code and separated by
    a comma, or `EVERY`; the list's own punctuation, a semicolon between
    entries and a full stop after the last, is stripped and nothing
    else is. `EVERY` is the minute table's repositories, in its order:
    a tree with no minute can schedule nothing on the calendar, so that
    table is what the organization is here. A clause written any other
    way is refused, for the reason `subjects` refuses a bullet it cannot
    read -- an entry read as naming no tree is a sentinel asked of
    nobody, and a run that reports that as agreement.

    :returns: each sentinel against the trees carrying it, in the order
        the record gives both.
    :raises LookupError: where a clause is neither `EVERY` nor names
        quoted as code and separated by commas.
    """
    out: dict[str, list[str]] = {}
    for sentinel, clause in subjects(ROOT / "README.md", *RECORD).items():
        trees = clause.rstrip(";.")
        if trees == EVERY:
            out[sentinel] = list(minutes())
            continue
        cells = trees.split(", ")
        if not all(TREE.fullmatch(cell) for cell in cells):
            msg = f"section 10's entry for {sentinel} names its trees as {clause!r}"
            raise LookupError(msg)
        out[sentinel] = [name(cell) for cell in cells]
    return out


OWED = (
    "Where a property of the tree decides membership it is stated below",
    "### The aggregate job, and the required check",
)
"""The prose either side of section 10's paragraphs on the entries."""

ROW = re.compile(r"^- \*\*`([^`]+)`")
"""How one of those paragraphs names the calendar row it is about."""

DEBT = re.compile(r"([\w.-]+/[\w.-]+)?#(\d+) carries the debt")
"""How it names the issue an adoption of that row waits on.

Section 10 asks an adoption pull request to name the tree that owes the
workflow and the issue that carries the debt, and this is the second of
those two read back off the file. The qualifier is optional because
section 9 makes it so: it requires one of a reference to another
repository, and a debt issue of this tree's own tracker resolves
without one. `carries the debt` is section 10's own phrase, and is
what keeps out the other issues a paragraph cites: an issue carrying a
row's *port* is named where a tree already schedules that row, and is
no reason to excuse an idle one.
"""


def reference(owed: re.Match[str]) -> str:
    """Qualify what `DEBT` read, so that one shape reaches the API.

    :param owed: the match.
    :returns: the reference, this repository filled in where section 10
        wrote it bare.
    """
    repository = owed.group(1) or f"{ORG}/{SELF}"
    return f"{repository}#{owed.group(2)}"


def debts() -> dict[str, str]:
    """Read the debt issue section 10 gives a row it schedules nowhere yet.

    A paragraph naming a debt and no row is refused rather than dropped,
    and so is a row given one twice, for the reason `subjects` refuses a
    bullet it cannot read: a debt this fails to find is a row whose
    exemption stops holding with nothing saying so.

    :returns: each row against the issue its paragraph names, qualified,
        rows whose paragraph names none left out.
    :raises LookupError: where a paragraph names a debt issue and no
        row, or two of them name the same row.
    """
    out: dict[str, str] = {}
    for paragraph in bulleted(ROOT / "README.md", *OWED):
        owed = DEBT.search(paragraph)
        if not owed:
            continue
        row = ROW.match(paragraph)
        if not row:
            msg = f"section 10 gives {reference(owed)} to no row of the calendar"
            raise LookupError(msg)
        if row.group(1) in out:
            msg = f"section 10 gives {row.group(1)} a debt issue twice"
            raise LookupError(msg)
        out[row.group(1)] = reference(owed)
    return out


def triggers(workflow: Path) -> dict[str, Any]:
    """Read the `on:` block of a workflow file.

    YAML 1.1 reads a bare `on` as the boolean it also spells `true`,
    which is why the key is looked for twice: what the file means is the
    same either way, and which one the parser hands back depends on how
    the file happens to quote it.

    :param workflow: the file to read.
    :returns: the trigger block, empty if the file declares none.
    """
    document = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    on = document.get("on", document.get(True, {}))
    return on if isinstance(on, dict) else {}


def schedules(root: Path) -> dict[str, list[str]]:
    """Every scheduled workflow of a tree, against its cron expressions.

    Both suffixes are read because GitHub runs both, and the stem is what
    the calendar names either way: a `links.yml` and a `links.yaml` in one
    tree are two runs of one row, so their crons are answered for
    together. A `timezone:` beside a `cron:` is refused rather than read:
    section 10's calendar means UTC and states no exception, so a
    schedule entry naming a zone is not an instant the calendar can
    compare against.

    :param root: the root of the checkout.
    :returns: each workflow's file stem against the crons it declares.
    :raises AssertionError: where a schedule entry carries a `timezone:`.
    """
    out: dict[str, list[str]] = {}
    for workflow in workflows(root):
        entries = triggers(workflow).get("schedule") or []
        for entry in entries:
            assert "timezone" not in entry, (
                f"{workflow}: a timezone beside a cron is off section 10's calendar"
            )
        crons = [entry["cron"] for entry in entries]
        if crons:
            out.setdefault(workflow.stem, []).extend(crons)
    return out


def test_the_calendar_gives_each_workflow_an_instant_of_its_own() -> None:
    """Two workflows in one repository must not land on the same minute.

    The minute is the repository's, so a day and an hour shared by two
    rows would be two runs of the same tree queued at the same instant --
    which is the one thing the grid exists to avoid.
    """
    slots: dict[tuple[str, str], list[str]] = {}
    for workflow, slot in calendar().items():
        slots.setdefault(slot, []).append(workflow)
    shared = {slot: names for slot, names in slots.items() if len(names) > 1}
    assert not shared, f"section 10 gives one slot to several workflows: {shared}"


def test_the_calendar_gives_each_repository_a_minute_of_its_own() -> None:
    """Two repositories on one minute is the queue the grid is against.

    A slot is shared between trees by design -- a day is a slot rather
    than a census -- so what keeps two of them out of one queue is the
    minute, and two repositories holding the same one collide on every
    workflow they both carry. `00` is in no row for the same reason,
    being the minute everybody else's cron picks.
    """
    minute_of = minutes()
    holders: dict[str, list[str]] = {}
    for repository, minute in minute_of.items():
        holders.setdefault(minute, []).append(repository)
    shared = {minute: names for minute, names in holders.items() if len(names) > 1}
    assert not shared, f"section 10 gives one minute to several trees: {shared}"
    busy = sorted(
        repository for repository, minute in minute_of.items() if int(minute) == 0
    )
    assert not busy, f"repositories on the minute every other cron picks: {busy}"


def test_every_repository_that_schedules_anything_has_a_minute(
    trees: dict[str, Path],
) -> None:
    """A tree with a cron and no row in the minute table is a hole.

    :param trees: the checkouts.
    """
    without = sorted(
        repository
        for repository, root in trees.items()
        if schedules(root) and repository not in minutes()
    )
    assert not without, f"scheduling repositories with no minute: {without}"


def test_a_debt_sentence_is_read_qualified_or_bare() -> None:
    """Either spelling of a debt sentence, and what is not one at all.

    Section 9 asks the qualifier of a reference to another repository,
    so a debt issue of this tree's own is correct prose written bare: a
    bare reference resolves to this repository, and a qualified one
    keeps the repository it names. A sentence citing an issue for
    anything but the debt, and one naming the debt with no issue, are
    read as naming none, which is what leaves the exemption failing
    closed.
    """
    read = {
        "btclib-org/.github#558 carries the debt until that tree schedules": (
            "btclib-org/.github#558"
        ),
        "btclib-org/btclib-node#42 carries the debt until it schedules": (
            "btclib-org/btclib-node#42"
        ),
        "#558 carries the debt until that tree schedules": f"{ORG}/{SELF}#558",
    }
    for sentence, issue in read.items():
        found = DEBT.search(sentence)
        assert found, f"no debt read in {sentence!r}"
        assert reference(found) == issue, f"{sentence!r} names {reference(found)}"
    unread = [
        "btclib-org/btclib-secp256k1#538 carries the port until that tree's",
        "btclib-org/.github#558 is the issue behind this row",
        "an open issue carries the debt until that tree schedules",
    ]
    misread = [sentence for sentence in unread if DEBT.search(sentence)]
    assert not misread, f"read as naming a debt: {misread}"


def test_every_row_of_the_calendar_names_something_that_exists(
    trees: dict[str, Path],
) -> None:
    """A row nothing answers to is the dangling half of the calendar.

    The other tests read the trees and ask the calendar; this reads the
    calendar and asks the trees, which is the direction that catches a
    row for a workflow nobody wrote and a minute for a repository nobody
    has. Both are reported rather than raised. A sentinel whose first
    tree is this repository takes its row in the pull request that gives
    it the workflow, so for those nothing excuses a row added ahead of
    that landing. A sentinel whose first tree is another repository
    cannot land both halves in one pull request -- section 10 says the
    row lands first -- and what carries the row until the schedule
    follows is the open issue its paragraph in *Which trees carry which
    sentinel* names, which is the issue that section says an adoption
    names. So the exemption is read here rather than left to a reader,
    and it expires the day the issue closes: a row nothing schedules,
    with no issue behind it or with a closed one, is the row for a
    workflow nobody wrote that this direction exists to catch.

    :param trees: the checkouts.
    """
    scheduled = {workflow for root in trees.values() for workflow in schedules(root)}
    idle = sorted(workflow for workflow in calendar() if workflow not in scheduled)
    unknown = sorted(repository for repository in minutes() if repository not in trees)
    owed = debts()
    unbounded = [workflow for workflow in idle if workflow not in owed]
    assert not unbounded, (
        "section 10 rows no repository schedules, with no paragraph matching"
        f" `{DEBT.pattern}`: {unbounded}"
    )
    settled = {
        workflow: owed[workflow] for workflow in idle if not still_open(owed[workflow])
    }
    assert not settled, (
        f"section 10 rows no repository schedules, their debt closed: {settled}"
    )
    assert not unknown, f"section 10 minutes for no repository: {unknown}"


def instant(cron: str) -> tuple[int, int, str, str, int] | None:
    """Read a cron expression as the weekly instant it names.

    A field is compared as the number it means and not as the text it is
    written with, `04` and `4` being the same hour; the day of month and
    the month are compared as written, a weekly schedule leaving both
    unrestricted.

    :param cron: the expression, as the workflow spells it.
    :returns: minute, hour, day of month, month, weekday, or None where
        any of the three numeric fields is not a plain number.
    """
    fields = cron.split()
    if len(fields) != FIELDS:
        return None
    numbers = [fields[0], fields[1], fields[4]]
    if not all(field.isdigit() for field in numbers):
        return None
    minute, hour, weekday = (int(field) for field in numbers)
    return minute, hour, fields[2], fields[3], weekday


def expression(slot: tuple[str, str], minute: str) -> str:
    """Write a pair of calendar rows out as the cron they mean.

    The two tables between them fix the minute, the hour and the day of
    the week and leave the day of the month and the month unrestricted,
    which is to say the grid's period is the week: a workflow that wants
    to run on any other has no row here to name it. Rendering the row as
    a cron is what puts that in the failure message, where a monthly
    expression is otherwise reported as the wrong day and nothing says
    the cadence is the disagreement.

    :param slot: the workflow's day and hour, as the table spells them.
    :param minute: the repository's minute, as the table spells it.
    :returns: the expression a workflow in that slot has to carry.
    """
    day, hour = slot
    return f"{int(minute):02d} {int(hour):02d} * * {WEEKDAYS[day]}"


def test_every_cron_is_the_instant_the_calendar_names(
    trees: dict[str, Path],
) -> None:
    """Every `cron:` in the organization is its row, to the minute.

    A row that moves is red here for every tree still on the old
    instant, the row being this file's and each `cron:` its own tree's:
    section 10's *A row that moves is red until the last tree follows
    it* is what that red is, and the issue carrying the ports is what
    bounds it. No `BACKLOG` row can excuse it -- `conftest.py` refuses a
    row for a test that is not asked per repository, and this one takes
    `trees`.

    :param trees: the checkouts.
    """
    rooms = calendar()
    minute_of = minutes()
    wrong: dict[str, str] = {}
    for repository, root in sorted(trees.items()):
        for workflow, crons in schedules(root).items():
            where = f"{repository}/{workflow}"
            if workflow not in rooms:
                wrong[where] = "section 10 names no such workflow"
                continue
            if repository not in minute_of:
                wrong[where] = "section 10 gives this repository no minute"
                continue
            wanted = expression(rooms[workflow], minute_of[repository])
            want = instant(wanted)
            for cron in crons:
                if instant(cron) != want:
                    wrong[where] = f"{cron!r}, where the calendar says {wanted!r}"
    assert not wrong, f"crons that are not on the calendar: {wrong}"


def test_the_record_has_an_entry_per_row_of_the_calendar() -> None:
    """The record's entries are the calendar's rows, in the calendar's order.

    The per-repository test below reads a tree's workflows against the
    record's entries, so a calendar row with no entry would be a
    sentinel asked of nobody, carried or not; this is what says every
    row has one. The order is the record's own claim, "in the order the
    two tables above give the rows and the repositories", and a tree an
    entry names has to be one the minute table gives a minute: a name
    spelt some other way would excuse nothing and fail nothing.
    """
    entries = record()
    assert list(entries) == list(calendar()), (
        f"section 10's record names {list(entries)} where its calendar"
        f" names {list(calendar())}"
    )
    order = list(minutes())
    unknown = {
        sentinel: [tree for tree in trees if tree not in order]
        for sentinel, trees in entries.items()
        if any(tree not in order for tree in trees)
    }
    assert not unknown, f"section 10 entries naming trees with no minute: {unknown}"
    disordered = {
        sentinel: trees
        for sentinel, trees in entries.items()
        if trees != sorted(trees, key=order.index)
    }
    assert not disordered, (
        f"section 10 entries out of the minute table's order: {disordered}"
    )


def test_a_tree_carries_the_sentinels_its_entries_give_it(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Section 10's record, read against one tree in both directions.

    A tree short of a sentinel its entry names and a tree carrying one
    no entry gives it are the pair of findings section 10 states beside
    the record, and one cell reports both. The workflow and the badge
    are one membership there, and the workflow is the half a checkout
    holds; the badge half is a reader's catch, no fixture here holding
    a tree's `README.md`. A workflow the record has no entry for --
    `test`, `lint`, the release path -- is no sentinel and is not asked.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    entries = record()
    carried = {
        workflow.stem
        for workflow in workflows(trees[repository])
        if workflow.stem in entries
    }
    given = {sentinel for sentinel, members in entries.items() if repository in members}
    findings = {
        "sentinels the record gives it and the tree does not carry": sorted(
            given - carried
        ),
        "sentinels the tree carries and no entry gives it": sorted(carried - given),
    }
    findings = {finding: names for finding, names in findings.items() if names}
    assert not findings, f"{repository}: {findings}; " + by_hand(
        repository, "ls .github/workflows/  # against section 10's sentinel record"
    )
