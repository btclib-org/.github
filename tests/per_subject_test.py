# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Where the copies of section 14's per-subject files are, against the prose.

Section 14 keeps two files out of *The same file in every repository*
because each copy's subject is its own tree's: the bytes differ by
design, so a comparison by path reads every copy as drift. What is left
for a command to decide is the location, and each paragraph states one --
the path it opens with, and beside it the tree that keeps its copy
somewhere else. `verbatim_test.py` asks the location question of the
compared list and, by construction, of nothing outside it: `verbatim()`
reads that list, and these two paragraphs are outside it by the sentence
that put them there.

What each paragraph says after its subject is a clause of the same
spellings that list's bullets carry, and `verbatim_test.py` reads it off
this module's reading rather than walking the prose a second time: who
owes a copy is one question, asked wherever section 14 answers it.

The silence section 14 gives as the reason those paragraphs exist is what
this closes for them -- a copy at a path the standard does not give
reported on the day it lands rather than on the day somebody greps the
trees.

What that costs is the prose of those paragraphs becoming a parser's
input, so a rewording a reader would pass over turns a run here red. The
cost is taken loudly: `per_subject` raises on a paragraph carrying the
phrase whose subject it cannot read, rather than passing it over, a
paragraph nothing asks about being the state this module is against.
"""

from __future__ import annotations

import re
import shlex
from pathlib import Path

import pytest

from . import ROOT, by_hand, output, tracked

pytestmark = pytest.mark.integration

STANDARD = ROOT / "README.md"
"""The file section 14 is in, read for its paragraphs rather than copied."""

PARAGRAPHS = re.compile(r"\n\s*\n")
"""What a blank line splits the standard's prose on."""

WRAPPED = re.compile(r"\s+")
"""What eighty columns leaves between two words of one sentence.

A paragraph is folded on it before anything is matched, so a clause the
margin broke in two is read as the sentence it is.
"""

PHRASE = "per repository by subject"
"""How section 14 says a file is outside the compared list by its subject.

Every paragraph carrying it is read for a subject, and one that carries
it and opens with none is an error rather than a paragraph passed over.

The copula is `OPENING`'s and not this one's, so that a paragraph saying
it another way -- *is decided per repository by subject*, which is the
neighbouring `.gitignore` sentence's *is decided per repository* carried
over -- is selected here and refused there, rather than stopping being
read at all. Selecting on the whole opening would make that rewording a
paragraph nothing asks about, which is the state this module is against.
"""

OPENING = re.compile(r"^`([^`]+)` is per repository by subject, (.+)$")
"""How such a paragraph names the file, and what it says after that.

The subject opens the paragraph, which is where a reader looks for it and
so where this reads it. What follows the phrase is the clause: who owes a
copy, in one of the two spellings section 14 gives its bullets, and then
the rest of the paragraph -- the same answer `subjects` in
`tests/__init__.py` gives for a bullet, read by `verbatim_test.py`'s
`owed` the same way. A paragraph carrying the phrase and saying nothing
after it is unread here rather than read as owing nothing of anybody.
"""

QUOTED_NOT_A_COPY = ("README.md", ".github/workflows/vendored-vectors.yml")
"""Paths these paragraphs quote that are a copy of no subject of theirs.

One is what this repository's copy of `tests/conventions_test.py` reads
section 7's list of conventions off, and the other is the workflow whose
presence the vendored-pin condition is observed by. Every repository
carries the first, and each tree owing the script carries the second, so
an extraction taking every backticked token would find one of them
wherever it looked and report no tree as short of anything. They are what
`declared` is held against; where the prose stops quoting one, the
control wants another token and not deleting.
"""

BACKTICKED = re.compile(r"`([^`]+)`")
"""Every inline-code token of a paragraph, read by that control alone."""

ELSEWHERE = re.compile(r"`([^`]+)` keeps its copy at `([^`]+)`")
"""How such a paragraph names a tree that keeps its copy somewhere else.

The repository, then the path. A departure worded some other way is
unread here, and `test_a_per_subject_copy_sits_where_section_14_puts_it`
reports it as a copy at a path the standard does not give: a red row
naming the tree, rather than a question nothing asks.
"""


def per_subject(document: Path = STANDARD) -> dict[str, str]:
    """Read section 14's per-subject paragraphs, each subject against the rest.

    Every way of reading nothing is an error rather than an empty answer,
    for the reason `subjects` in `tests/__init__.py` refuses a list it
    cannot read: a caller handed `{}` asks nothing of any tree and reads
    the silence as agreement.

    :param document: the file to read, this tree's `README.md` unless a
        control names another.
    :returns: each subject path against what its paragraph says after the
        phrase, which is the clause `owed` reads and the sentences
        `departures` reads.
    :raises LookupError: where the document holds no such paragraph, one
        this reads no subject and clause off, or two naming one subject.
    """
    read: list[tuple[str, str]] = []
    unread: list[str] = []
    for block in PARAGRAPHS.split(document.read_text(encoding="utf-8")):
        paragraph = WRAPPED.sub(" ", block).strip()
        if PHRASE not in paragraph:
            continue
        found = OPENING.match(paragraph)
        if found is None:
            unread.append(paragraph)
        else:
            read.append((found.group(1), found.group(2)))
    out = dict(read)
    if unread or not out or len(out) != len(read):
        msg = (
            f"{document.name}: {len(read)} paragraphs carry {PHRASE!r} with"
            f" a subject and a clause of their own, {len(out)} distinct"
            f" among them, and these carry it with no subject and clause:"
            f" {unread}"
        )
        raise LookupError(msg)
    return out


def departures(clause: str) -> dict[str, str]:
    """Read the trees a paragraph sends elsewhere, by the path each is sent to.

    :param clause: what the paragraph says after its subject.
    :returns: each repository against the path it keeps its copy at.
    """
    return dict(ELSEWHERE.findall(clause))


def declared(subject: str, clause: str) -> list[str]:
    """Every path a per-subject paragraph gives a copy of its subject.

    The path it opens with, and the one behind each departure it states.
    No other backticked token is read, `QUOTED_NOT_A_COPY` being what
    that costs to get wrong: a paragraph quotes a workflow, a repository
    name and this tree's own `README.md` too, and a rule taking every one
    of them would answer that a tree carrying anything the prose mentions
    carries a copy.

    :param subject: the path the paragraph opens with.
    :param clause: what it says after that.
    :returns: the paths, the subject's own first.
    """
    return [subject, *departures(clause).values()]


def carried(root: Path, names: list[str]) -> list[str]:
    """List every copy under a name a paragraph gives, wherever it is.

    By those names and not by the paths section 14 gives them: the
    question is where the copies are, and a search of the declared paths
    alone cannot see one anywhere else. Every name the paragraph gives,
    because a departure stated as a name of its own is a name copies of
    that subject sit under, and a search of the subject's name answers
    nothing for the tree keeping one. Tracked rather than walked, so a
    checkout's own environment is not read as part of it.

    What this search and the departure test divide is the direction.
    `test_a_per_subject_copy_sits_where_section_14_puts_it` takes the
    copies this finds and asks whether each is where the standard puts
    it; `test_a_tree_section_14_sends_elsewhere_keeps_its_copy_there`
    takes each departure the standard states and asks whether a copy is
    at it, and reads no copy list at all -- `tracked` at the declared
    path is the whole of it. A departure a tree no longer makes is red in
    both, and a copy at a path no paragraph names is red in the first
    alone. The other reader of this is
    `test_a_per_subject_path_is_one_some_repository_carries`, which asks
    the widened question of the organization rather than of a tree: a
    subject carried everywhere under a departure's name only resolves
    through that name here instead of reading as a path nobody keeps.

    :param root: the root of the checkout.
    :param names: the paths the paragraph gives, `declared`'s answer.
    :returns: the paths, relative to the root, in git's order.
    """
    wanted = {Path(path).name for path in names}
    return [
        path
        for path in tracked(root, *(f"*{name}" for name in sorted(wanted)))
        if Path(path).name in wanted
    ]


def listing(paragraphs: dict[str, str]) -> str:
    """Give the command that lists a tree's copies of these files.

    The pathspecs are the ones `carried` passes, so what a reader runs is
    what the test ran.

    :param paragraphs: what `per_subject` read.
    :returns: the `git ls-files` a reader runs in a checkout.
    """
    wanted = {
        Path(path).name
        for subject, clause in paragraphs.items()
        for path in declared(subject, clause)
    }
    pathspecs = " ".join(shlex.quote(f"*{name}") for name in sorted(wanted))
    return f"git ls-files -- {pathspecs}"


def test_a_per_subject_copy_sits_where_section_14_puts_it(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """A copy of one of these files is where its paragraph puts it, or absent.

    A tree carrying none is no finding here: the section says these files
    are per repository by subject and never that a tree owes one. A copy
    somewhere the paragraph does not put it is the finding -- one that
    moved, one a tree took at a path of its own, and one whose departure
    the paragraph states in words `ELSEWHERE` does not read.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    subjects = per_subject()
    root = trees[repository]
    astray: dict[str, list[str]] = {}
    for subject, clause in subjects.items():
        here = departures(clause).get(repository, subject)
        copies = carried(root, declared(subject, clause))
        found = [path for path in copies if path != here]
        if found:
            astray[here] = found
    assert not astray, (
        "section 14 gives each of these subjects one path in this tree, and"
        f" the copies here are at others: {astray}; "
        + by_hand(repository, listing(subjects))
    )


def test_a_per_subject_path_is_one_some_repository_carries(
    trees: dict[str, Path],
) -> None:
    """A subject no tree carries anywhere is a paragraph that has gone stale.

    `verbatim_test.py`'s `test_section_14_names_files` asks this of the
    compared list. Asking it here is also what keeps the test above from
    passing on a path that moved out from under the paragraph: that one
    reports a copy somewhere the standard does not put it, and a subject
    the trees no longer answer to has no copy anywhere for it to report.

    :param trees: the checkouts.
    """
    unknown = [
        subject
        for subject, clause in per_subject().items()
        if not any(carried(root, declared(subject, clause)) for root in trees.values())
    ]
    assert not unknown, (
        f"section 14 names these per repository by subject, and no"
        f" repository carries a file of that name: {unknown}"
    )


def test_a_tree_section_14_sends_elsewhere_keeps_its_copy_there(
    trees: dict[str, Path],
) -> None:
    """A departure the standard states is one the tree still makes.

    A clause left behind by a copy that moved back to the path its
    paragraph opens with excuses that tree from the default with nothing
    to excuse, and the test above passes it: that one asks where a tree's
    copies are, and a tree at the path the clause gives is a tree at the
    path the standard gives. The two degenerate the opposite ways round --
    this has nothing to ask where no paragraph names a departure, and that
    is the state in which a clause going unread reddens the test above.

    :param trees: the checkouts.
    :raises LookupError: where a clause names a repository the
        organization does not have.
    """
    stale: dict[str, str] = {}
    for subject, clause in per_subject().items():
        for repository, path in departures(clause).items():
            if repository not in trees:
                msg = (
                    f"section 14 sends {repository} elsewhere for {subject},"
                    " and the organization has no repository of that name"
                )
                raise LookupError(msg)
            if not tracked(trees[repository], path):
                stale[f"{repository} {subject}"] = path
    assert not stale, (
        "section 14 says each of these trees keeps its copy at the path"
        f" beside it, and none is there: {stale}"
    )


def planted(tmp_path: Path, paragraphs: list[str]) -> Path:
    """Write paragraphs for `per_subject` to read.

    :param tmp_path: where to write them.
    :param paragraphs: the prose, one paragraph each.
    :returns: the file, holding those paragraphs and nothing else.
    """
    document = tmp_path / "README.md"
    document.write_text("\n\n".join(paragraphs) + "\n", encoding="utf-8")
    return document


def test_an_unread_paragraph_a_missing_one_and_a_repeated_one_each_raise(
    tmp_path: Path,
) -> None:
    """The three ways the reader would answer for prose it did not read.

    The standard's own subjects are written back out first and have to
    read as themselves, so that what the probes measure is the shape and
    not the planting. Each probe reaches a refusal of its own, named in
    the message it is matched on: a paragraph carrying the phrase whose
    subject is unreadable, which is the rewording this module costs; a
    document with no such paragraph, which asks nothing of any tree and
    would read as agreement; and one subject in two paragraphs, which a
    mapping takes as one and drops the other.

    :param tmp_path: where the copies are planted.
    """
    live = per_subject()
    paragraphs = [
        f"`{subject}` is {PHRASE}, {clause}" for subject, clause in live.items()
    ]
    assert per_subject(planted(tmp_path, paragraphs)) == live
    first, *rest = paragraphs
    unread = [first.replace("`", "", 2), *rest]
    assert unread != paragraphs
    # the paragraphs carry apostrophes, so `repr` quotes one of them
    # with `"` and a pattern naming the opening quote matches neither
    with pytest.raises(LookupError, match=r"no subject and clause: \["):
        per_subject(planted(tmp_path, unread))
    clauseless = [f"`{subject}` is {PHRASE}." for subject in live]
    with pytest.raises(LookupError, match=r"no subject and clause: \["):
        per_subject(planted(tmp_path, clauseless))
    with pytest.raises(LookupError, match="0 paragraphs carry"):
        per_subject(planted(tmp_path, ["Nothing here names a subject."]))
    with pytest.raises(LookupError, match=r"2 paragraphs carry.*1 distinct"):
        per_subject(planted(tmp_path, [first, first]))


def test_the_paths_a_paragraph_names_are_not_its_backticked_tokens() -> None:
    """`declared` reads the subject and each departure, and nothing else.

    Both paragraphs are dense with inline code that is no copy of
    anything, and the failure of a rule taking all of it is silent: the
    tokens in `QUOTED_NOT_A_COPY` are carried by the trees that would
    then read as satisfied.
    """
    quoted: set[str] = set()
    named: set[str] = set()
    for subject, clause in per_subject().items():
        quoted |= set(BACKTICKED.findall(clause))
        named |= set(declared(subject, clause))
    for token in QUOTED_NOT_A_COPY:
        assert token in quoted, (
            f"section 14's per-subject prose no longer quotes {token!r}:"
            " the control wants a token it does quote, not deleting"
        )
        assert token not in named, (
            f"{token!r} is read as a path a copy of a subject sits at:"
            " the extraction is taking backticked tokens that are none"
        )


def sown(tmp_path: Path, paths: list[str]) -> Path:
    """Build a tree tracking some files, for `carried` to search.

    :param tmp_path: where to build it.
    :param paths: the files it tracks, relative to its own root.
    :returns: the root of the tree.
    """
    root = tmp_path / "sown"
    root.mkdir()
    for path in paths:
        (root / path).parent.mkdir(parents=True, exist_ok=True)
        (root / path).write_text("", encoding="utf-8")
    output("git", "-C", str(root), "init", "--quiet")
    output("git", "-C", str(root), "add", "--", *paths)
    return root


def test_every_name_a_paragraph_gives_is_searched_and_a_near_miss_is_not(
    tmp_path: Path,
) -> None:
    """`carried` searches the tree, by each whole name, and by no other.

    Its pathspec is a wildcard, and what decides whether a copy one
    directory deeper is seen at all is whether that wildcard crosses a
    `/`: git's does. One that did not would answer that every tree
    carries nothing, which is
    `test_a_per_subject_copy_sits_where_section_14_puts_it` green having
    asked nothing -- and section 14 names a departure exactly one
    directory deeper, so that is the live case rather than a contrived
    one. A departure under a name of its own is the other live case,
    `btclib-node`'s `.github/scripts/check_vendored_pin.py`, and a
    search of the subject's name answers with nothing for that tree. The
    near miss is a file whose name merely ends with a searched one,
    which the pathspec admits and the name decides against. The paths
    here are the control's own and none of the standard's: what is
    measured is the search, not what section 14 says.

    :param tmp_path: where the tree is built.
    """
    root = sown(
        tmp_path,
        ["probe.py", "under/one/probe.py", "here/not_probe.py", "by_another_name.py"],
    )
    assert carried(root, ["here/probe.py"]) == ["probe.py", "under/one/probe.py"]
    assert carried(root, ["here/probe.py", "gone/by_another_name.py"]) == [
        "by_another_name.py",
        "probe.py",
        "under/one/probe.py",
    ]
