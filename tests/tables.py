# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Reading a table of README.md as data.

Section 10's calendar is prose a person reads and a rule a machine has
to enforce, and those are the same table rather than two copies of it:
the file is the source, this module is how the suite reads it. A row
added there is checked from the moment it is added, and a row nobody
maintains fails against the trees instead of going quietly stale.
"""

from __future__ import annotations

import re
from pathlib import Path


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


SUBJECT = re.compile(r"^- `([^`]+)` — ")
"""How a bullet of a list this module reads names what it is about.

The backticks and the spaced em dash are the shape, and a bullet written
any other way is one this cannot answer for.
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


def subjects(document: Path, opening: str, closing: str) -> list[str]:
    """Read the backticked subject of every bullet between two lines.

    A bullet's subject is what it is about, and a list whose subjects are
    paths is a list a test can act on. `opening` and `closing` are the
    prose either side of it, so moving the list within its section does
    not need this call changed.

    Every way of reading nothing here is an error rather than an empty
    answer, for the reason `rows` refuses a header it finds twice: a
    caller that gets `[]` compares no files and reports that as agreement.
    So both ends have to be found exactly once and in that order, the
    list between them has to hold a bullet, and every bullet it holds has
    to carry a subject -- a list rewritten into a shape this cannot read
    is the failure, not a run that quietly checks nothing.

    :param document: the markdown file to read.
    :param opening: a substring of the line the list follows.
    :param closing: a substring of the line the list stops at.
    :returns: the subjects, in the order the list gives them.
    :raises LookupError: where either end is not found exactly once, the
        closing line comes first, or a bullet between them has no
        backticked subject.
    """
    lines = document.read_text(encoding="utf-8").splitlines()
    start = sole(document, lines, opening)
    end = sole(document, lines, closing)
    if end < start:
        msg = f"{document.name} holds {closing!r} before {opening!r}"
        raise LookupError(msg)
    out: list[str] = []
    unread: list[str] = []
    for line in lines[start + 1 : end]:
        if not line.startswith("- "):
            continue
        found = SUBJECT.match(line)
        if found:
            out.append(found.group(1))
        else:
            unread.append(line)
    if unread or not out:
        msg = (
            f"{document.name} names {len(out)} subjects between {opening!r}"
            f" and {closing!r}, and these bullets name none: {unread}"
        )
        raise LookupError(msg)
    return out
