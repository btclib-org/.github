"""Every scheduled run in the organization is on section 10's calendar.

The calendar is two tables: a workflow owns a day and an hour, a
repository owns the minute. Between them they name an instant for every
`cron:` in the organization, and this is what says so -- a row that
drifts from the trees, or a tree that drifts from the rows, fails here
rather than being noticed the week a notification arrives on the wrong
day.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from .organization import ROOT
from .tables import name, rows

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
    together.

    :param root: the root of the checkout.
    :returns: each workflow's file stem against the crons it declares.
    """
    here = root / ".github" / "workflows"
    files = sorted(path for suffix in ("*.yml", "*.yaml") for path in here.glob(suffix))
    out: dict[str, list[str]] = {}
    for workflow in files:
        entries = triggers(workflow).get("schedule") or []
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


def test_every_row_of_the_calendar_names_something_that_exists(
    trees: dict[str, Path],
) -> None:
    """A row nothing answers to is the dangling half of the calendar.

    The other tests read the trees and ask the calendar; this reads the
    calendar and asks the trees, which is the direction that catches a
    row for a workflow nobody wrote and a minute for a repository nobody
    has. Both are reported rather than raised: a row added ahead of the
    workflow it schedules is a backlog entry until the rollout reaches
    the last tree, and this suite gates nothing.

    :param trees: the checkouts.
    """
    scheduled = {workflow for root in trees.values() for workflow in schedules(root)}
    idle = sorted(workflow for workflow in calendar() if workflow not in scheduled)
    unknown = sorted(repository for repository in minutes() if repository not in trees)
    assert not idle, f"section 10 rows no repository schedules: {idle}"
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
