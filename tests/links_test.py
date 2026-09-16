# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The `links` workflow asks lychee a question its flags let it answer.

`links.yml` gates nothing, so its whole value is that a red run means a
destination has moved: a flag that makes a live host read as dead, or
that promises a cache no step keeps, costs an investigation and buys
nothing, and a question the arguments never ask leaves a move
unreported. The flags are read from the action's `args:` rather than
grepped, the arguments being one folded string the grep would have to
reassemble.
"""

from __future__ import annotations

import re
import shlex
from fnmatch import fnmatchcase
from typing import TYPE_CHECKING, Any, NamedTuple

import pytest

from . import ORG, ROOT, SELF, by_hand, tracked
from .workflows_test import document, steps

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

ACTION = "lycheeverse/lychee-action"

REUSABLE = "reusable-links.yml"
"""The workflow of this repository holding the lychee job a tree calls."""

LOCAL = f"./.github/workflows/{REUSABLE}"
"""A call to `REUSABLE` by path, which runs the calling tree's own copy."""

REMOTE = f"{ORG}/{SELF}/.github/workflows/{REUSABLE}@main"
"""A call to this repository's `REUSABLE`, at section 10's `@main`."""

TARGETS = "${{ inputs.targets }}"
"""Where `REUSABLE`'s `args:` takes the caller's paths."""

SUCCESS = set(range(100, 104)) | set(range(200, 300))
"""lychee's own default for `--accept`: `100..=103,200..=299`.

Read back with `lychee --help | sed -n '/--accept/,/default/p' | tail -1`.
The flag replaces the range rather than adding to it, so a list that
names fewer turns every other success into an error.
"""

RANGE = re.compile(r"^(\d+)(?:\.\.=(\d+))?$")
"""One entry of an `--accept` list: a code, or an inclusive range."""


class Call(NamedTuple):
    """What a repository's `links.yml` runs, and the paths it runs it over."""

    step: dict[str, Any]
    """The lychee step, its `args:` holding the caller's paths."""

    workflow: Path
    """The file the step is written in."""

    owner: str
    """The repository that file is in."""

    targets: str
    """The caller's `targets:` input, empty where the call is direct."""


def lychee(
    repository: str,
    trees: dict[str, Path],
) -> Call:
    """Find the lychee step of a repository's `links.yml`, with its file.

    Skipped where there is no `links.yml`: section 10's record gives the
    workflow to every repository, so a tree without one is a gap in that
    tree, reported by `grid_test.py` against the record rather than asked
    here. An error where the file exists and no step calls the action,
    since the file is then not what its name says.

    A job calling `REUSABLE` runs that file's steps, so they are read
    from the tree the call names -- the calling tree's own for `LOCAL`,
    this repository's for `REMOTE` -- with the job's `targets` put where
    `args:` takes them: the step returned is the one the call runs.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the call, its fields as `Call` names them.
    :raises LookupError: where `links.yml` calls the action no times or
        more than once, or calls `REUSABLE` without `targets` or where
        the tree the call names has no such file.
    """
    workflow = trees[repository] / ".github" / "workflows" / "links.yml"
    if not workflow.is_file():
        pytest.skip(f"{repository} has no links.yml")
    found: list[Call] = []
    for job in (document(workflow).get("jobs") or {}).values():
        if not isinstance(job, dict):
            continue
        owner = {LOCAL: repository, REMOTE: SELF}.get(job.get("uses", ""))
        if owner is None:
            found.extend(
                Call(step, workflow, repository, "")
                for step in job.get("steps") or []
                if step.get("uses", "").startswith(ACTION)
            )
            continue
        targets = (job.get("with") or {}).get("targets")
        if targets is None:
            msg = f"{repository}/links.yml calls {REUSABLE} without targets"
            raise LookupError(msg)
        called = trees[owner] / ".github" / "workflows" / REUSABLE
        if not called.is_file():
            msg = f"{repository}/links.yml calls {REUSABLE}, and {owner} has none"
            raise LookupError(msg)
        for step in steps(called):
            if step.get("uses", "").startswith(ACTION):
                given = dict(step.get("with") or {})
                given["args"] = str(given.get("args", "")).replace(
                    TARGETS, str(targets)
                )
                found.append(Call({**step, "with": given}, called, owner, str(targets)))
    if len(found) != 1:
        msg = f"{repository}/links.yml calls {ACTION} {len(found)} times"
        raise LookupError(msg)
    return found[0]


def relative(workflow: Path) -> str:
    """Name a workflow file the way a command in its checkout does.

    :param workflow: the file `lychee` returned.
    :returns: its path from the root of the tree holding it.
    """
    return f".github/workflows/{workflow.name}"


def test_a_call_is_read_from_the_tree_it_names(tmp_path: Path) -> None:
    """A call by path reads the caller's own copy, and `@main` this one's.

    A sibling calling `LOCAL` runs a file its own runner checks out, so
    this repository's copy answering for it would pass a tree whose run
    fails. Planted trees: this repository's with `REUSABLE`, a sibling
    without it, and the sibling's `links.yml` calling each way in turn.

    :param tmp_path: where the trees are planted.
    """
    here = tmp_path / SELF / ".github" / "workflows"
    here.mkdir(parents=True)
    source = ROOT / ".github" / "workflows" / REUSABLE
    (here / REUSABLE).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    sibling = tmp_path / "sibling" / ".github" / "workflows"
    sibling.mkdir(parents=True)
    trees = {SELF: tmp_path / SELF, "sibling": tmp_path / "sibling"}
    call = "jobs:\n  links:\n    uses: {}\n    with:\n      targets: docs\n"
    (sibling / "links.yml").write_text(call.format(REMOTE), encoding="utf-8")
    read = lychee("sibling", trees)
    assert (read.owner, read.workflow, read.targets, arguments(read.step)[-1]) == (
        SELF,
        here / REUSABLE,
        "docs",
        "docs",
    )
    (sibling / "links.yml").write_text(call.format(LOCAL), encoding="utf-8")
    with pytest.raises(LookupError, match="sibling has none"):
        lychee("sibling", trees)


def arguments(step: dict[str, Any]) -> list[str]:
    """Split the action's `args:` input into words.

    :param step: the lychee step.
    :returns: the words, empty where the input is not given.
    """
    return str(step.get("with", {}).get("args", "")).split()


def accepted(words: list[str]) -> set[int]:
    """Read the status codes an argument list makes lychee accept.

    Both spellings clap takes, `--accept <list>` and `--accept=<list>`:
    a list the second way is one word, and reading only the first would
    take it for the default and pass a list that drops half of it.

    :param words: the action's arguments.
    :returns: the codes, lychee's default where `--accept` is not passed.
    :raises ValueError: where an entry is neither a code nor a range.
    """
    given = None
    for index, word in enumerate(words):
        if word == "--accept":
            given = words[index + 1]
        elif word.startswith("--accept="):
            given = word.removeprefix("--accept=")
    if given is None:
        return set(SUCCESS)
    out: set[int] = set()
    for entry in given.split(","):
        found = RANGE.match(entry)
        if not found:
            msg = f"--accept entry {entry!r} is neither a code nor a range"
            raise ValueError(msg)
        low = int(found.group(1))
        high = int(found.group(2) or low)
        out.update(range(low, high + 1))
    return out


def ranges(codes: list[int]) -> list[str]:
    """Write a sorted list of codes the way `--accept` spells them.

    :param codes: the codes, sorted.
    :returns: each run of consecutive codes as `low..=high`, or alone.
    """
    out: list[str] = []
    start = previous = None
    for code in [*codes, None]:
        if start is not None and previous is not None and code != previous + 1:
            out.append(str(start) if start == previous else f"{start}..={previous}")
            start = None
        if start is None:
            start = code
        previous = code
    return out


def test_lychee_accepts_every_success_code(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """An `--accept` list covers what lychee would accept unasked.

    A list may add to the default -- `429` is the one worth adding, a
    rate limit being an answer from a host that is alive -- and may not
    take from it: a host that starts answering `204` to a HEAD turns a
    live link into a reported dead one, without anybody touching the
    tree.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    call = lychee(repository, trees)
    lost = sorted(SUCCESS - accepted(arguments(call.step)))
    assert not lost, (
        f"success codes --accept turns into errors: {ranges(lost)}; "
        + by_hand(call.owner, f"grep -o -- '--accept [^ ]*' {relative(call.workflow)}")
    )


def test_lychee_checks_a_link_into_a_heading(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """`--include-fragments` is passed, so an anchor is a link too.

    A fragment is checked only when asked for, and the forge serves the
    page whether or not the fragment names a heading on it -- so a
    heading renamed in one tree breaks the links into it with nothing
    red in that tree. The run that would notice is the one over the
    file holding the link, which is why every tree passes the flag and
    not only the tree whose headings are cited most.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    call = lychee(repository, trees)
    assert "--include-fragments" in arguments(call.step), (
        "lychee checks a fragment only when asked, and a link into "
        "another tree's heading is checked by this tree's run alone; "
        + by_hand(call.owner, f"grep -c include-fragments {relative(call.workflow)}")
    )


def test_a_lychee_cache_is_kept_between_runs(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """`--cache` is passed only where a step keeps `.lycheecache`.

    A workflow run starts from a fresh workspace, so a cache lychee
    writes at the end of one run is read by the next only if a step
    restores it; without one the flag decides nothing, and a comment
    crediting it with absorbing a throttling host describes a mechanism
    that is not there.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    call = lychee(repository, trees)
    if "--cache" not in arguments(call.step):
        return
    kept = any(
        other.get("uses", "").startswith("actions/cache")
        for other in steps(call.workflow)
    )
    assert kept, (
        "--cache is passed and no step restores or saves .lycheecache; "
        + by_hand(
            call.owner,
            f"grep -c 'actions/cache\\|lycheecache' {relative(call.workflow)}",
        )
    )


def reached(term: str, path: str) -> bool:
    """Say whether a `targets:` term makes lychee read a file.

    lychee's walker skips a hidden directory unless a term names it
    literally: `.github/**/*.md` answers and needs no `--hidden`, where
    `.git*/**/*.md` and `[.]github/**/*.md` answer nothing until
    `--hidden` is passed. So a string built of `*` and `**` alone leaves
    `.github/` and `.claude/` outside it whatever it spells, and
    `links.yml` passes no `--hidden`. Read back with
    `lychee --dump-inputs --offline '<term>'` in a tree holding one.

    This reads lychee 0.24.2, which is the version a run uses:
    `lychee-action`'s `lycheeVersion` input defaults to it and
    `reusable-links.yml` pins the action at a commit, so what the
    walker does moves only when that pin moves.

    :param term: one path term of a `targets:` string.
    :param path: a path from the root of a tree, as git spells it.
    :returns: whether lychee reads that file when handed that term.
    """
    return _matches(term.split("/"), path.split("/"))


def _matches(term: list[str], path: list[str]) -> bool:
    """Match a path's components against a term's segments.

    `**` stands for any run of components and `*` for part of one, and
    neither crosses a component whose name begins with a dot: that one
    is matched by a segment equal to it and by nothing else.

    :param term: the term's segments.
    :param path: the path's components.
    :returns: whether the segments match the components.
    """
    if not term:
        return not path
    head, rest = term[0], term[1:]
    if head == "**":
        for across in range(len(path) + 1):
            if across and path[across - 1].startswith("."):
                return False
            if _matches(rest, path[across:]):
                return True
        return False
    if not path:
        return False
    first = path[0]
    named = first == head if first.startswith(".") else fnmatchcase(first, head)
    return named and _matches(rest, path[1:])


def outside(targets: str, paths: list[str]) -> list[str]:
    """List the paths no term of a `targets:` string reaches.

    The string is quoted as for a shell and is split as one. A term
    holding `://` is a URL lychee fetches rather than a tree it walks,
    and `btclib-org.github.io` hands it the organization's own site.

    :param targets: a `links.yml` call's `targets:` input.
    :param paths: the paths to ask about.
    :returns: the paths outside every term, in the order given.
    """
    terms = [term for term in shlex.split(targets) if "://" not in term]
    return [path for path in paths if not any(reached(term, path) for term in terms)]


def test_a_term_reaches_a_hidden_directory_only_by_naming_it() -> None:
    """The walker's own rule, which decides what a `targets:` string owes.

    A wildcard stops at a dot wherever the dot is -- at the root, and
    under a directory a term has already named -- so the two files every
    repository keeps out of sight of `**`, its pull request template and
    its review command, are reached by a term that spells the directory
    and by no other.
    """
    hidden = ".github/PULL_REQUEST_TEMPLATE.md"
    assert not reached("**/*.md", hidden)
    assert not reached(".git*/**/*.md", hidden)
    assert not reached("[.]github/**/*.md", hidden)
    assert reached(".github/**/*.md", hidden)
    assert reached(".github/*.md", hidden)
    assert not reached("docs/**/*.md", "docs/.draft/x.md")
    assert reached("docs/.draft/*.md", "docs/.draft/x.md")
    assert reached("**/*.md", "README.md")
    assert reached("**/*.md", "profile/README.md")


def test_outside_is_red_on_a_string_that_names_no_hidden_directory() -> None:
    """The pair a live cell needs: the same files, two strings, two answers.

    A string of visible globs passes a tree whose markdown is all
    visible and says nothing about one whose markdown is not, so the
    reading it disagrees with is the one to show it red on.
    """
    paths = [
        "README.md",
        "profile/README.md",
        "tests/README.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".claude/commands/review.md",
    ]
    assert outside('"*.md" "profile/*.md" ".claude/commands/*.md"', paths) == [
        "tests/README.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
    ]
    assert outside('"**/*.md" ".github/**/*.md" ".claude/**/*.md"', paths) == []
    assert outside('"*.md" https://btclib.org/', paths) == paths[1:]


def test_lychee_reads_every_markdown_file_a_tree_tracks(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """A tree's `targets:` reaches every `*.md` that tree tracks.

    The string is the claim that these are the files whose links are
    checked, so a tracked file outside it is one this workflow never
    reads and a dead destination in it is found by whoever follows the
    link. Markdown is what this asks about because it is what every
    repository holds; the `rst` a tree tracks is the cell below, asked
    separately so that a tree owing one term is not excused the others.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    call = lychee(repository, trees)
    missed = outside(call.targets, tracked(trees[repository], "*.md"))
    assert not missed, (
        f"tracked markdown no term of targets reaches: {missed}; "
        + by_hand(repository, f"lychee --dump-inputs --offline {call.targets}")
    )


def test_a_docs_term_reaches_the_directory_it_names_and_below_it() -> None:
    """`**` stands for no component as well as for several.

    The term section 10 gives for a tree's documentation source reaches
    `docs/README.rst` beside `docs/source/index.rst`, which is what the
    walker answers: `lychee --dump-inputs --offline 'docs/**/*.rst'` in
    a tree holding both names both.
    """
    assert reached("docs/**/*.rst", "docs/source/index.rst")
    assert reached("docs/**/*.rst", "docs/README.rst")
    assert not reached("docs/**/*.rst", "README.rst")


def test_lychee_reads_every_rst_file_a_tree_tracks(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """A tree's `targets:` reaches every `*.rst` that tree tracks.

    Section 10's rejected alternative here is the documentation build's
    own `sphinx-build -n -W`: it fails on a cross-reference that does not
    resolve and fetches no URL, so what a term adds is the external link,
    in a file such as `docs/README.rst` that `docs/source/` reaches
    through no `toctree` and no `include`. A tree tracking no `rst` is
    asked nothing, there being no file for a term to cover.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    call = lychee(repository, trees)
    missed = outside(call.targets, tracked(trees[repository], "*.rst"))
    assert not missed, (
        f"tracked documentation source no term of targets reaches: {missed}; "
        + by_hand(repository, f"lychee --dump-inputs --offline {call.targets}")
    )


FENCE = re.compile(r"^```.*?^```\n?", re.DOTALL | re.MULTILINE)
"""A fenced code block, so its own `#` comments are not read as headings.

README.md's own comment lines inside its `toml` example are exactly
this shape: not stripped, they read as headings GitHub never renders,
and `anchors()` would answer ids no heading gives.
"""

HEADING = re.compile(r"^#{1,6} (.+)$", re.MULTILINE)
"""One heading of a markdown file, its own text after the `#`s."""

ROOT_LINK = re.compile(rf"github\.com/{re.escape(ORG)}/{re.escape(SELF)}#([\w-]+)")
"""A link into this repository by anchor, the root shape lychee cannot
check once its step holds a token (btclib-org/.github#630): the API
answers that the repository exists, and lychee takes that for the
anchor. This asks the same question offline, against this file's own
headings.
"""


def slug(heading: str) -> str:
    """Render a heading's text the way GitHub's own anchor does.

    Lowercase, spaces to hyphens, everything but a word character, a
    space or a hyphen already in the heading dropped -- which is what
    strips a heading's backticks along with its punctuation, GitHub
    slugging the rendered text rather than the markdown that produced
    it.

    :param heading: the heading's text, markdown and all.
    :returns: the anchor GitHub renders for it.
    """
    return re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "", heading.lower()).strip())


def anchors(markdown: str) -> set[str]:
    """Read every heading of a file as the anchors GitHub gives them.

    A repeated slug is suffixed `-1`, `-2` and so on, in heading order,
    which is GitHub's own rule for a duplicate; README.md repeats none
    today, but a link resolving is a claim about GitHub's rendering and
    not only about this file's headings being distinct.

    :param markdown: the file's text.
    :returns: every anchor the file answers to.
    """
    seen: dict[str, int] = {}
    out: set[str] = set()
    for heading in HEADING.findall(FENCE.sub("", markdown)):
        base = slug(heading)
        count = seen.get(base, 0)
        seen[base] = count + 1
        out.add(base if count == 0 else f"{base}-{count}")
    return out


def test_slug_matches_three_headings_already_linked_by_anchor() -> None:
    """GitHub's own rendering, read off three anchors already in the tree.

    `tests/__init__.py`'s own docstring mentions `./README.md#8-coverage-at-100`
    as an example anchor rather than a link, `SECURITY.md` links
    `#2-the-tree` and `CODE_OF_CONDUCT.md` links
    `#14-copied-verbatim-and-decided-per-repository` -- three anchors
    already resolving on GitHub, against the headings they name.
    """
    known = {
        "8. Coverage at 100%": "8-coverage-at-100",
        "2. The tree": "2-the-tree",
        "14. Copied verbatim, and decided per repository": (
            "14-copied-verbatim-and-decided-per-repository"
        ),
    }
    wrong = {
        heading: slug(heading)
        for heading, want in known.items()
        if slug(heading) != want
    }
    assert not wrong, f"slug disagrees with a known anchor {known}: {wrong}"


def test_a_root_link_into_this_files_heading_resolves(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """A `github.com/<org>/.github#<fragment>` link names a real heading.

    This is the shape *A `github.com/<owner>/<repo>#heading` link is
    unchecked by this flag* in section 10 names as the one lychee cannot
    check once its step holds a token, so the check is made here,
    offline, against this file's own headings rather than against the
    forge.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    targets = anchors((trees[SELF] / "README.md").read_text(encoding="utf-8"))
    root = trees[repository]
    broken = sorted(
        f"{path}: #{fragment}"
        for path in tracked(root, "*.md")
        for fragment in ROOT_LINK.findall((root / path).read_text(encoding="utf-8"))
        if fragment not in targets
    )
    assert not broken, (
        f"links no heading of README.md answers to: {broken}; "
        + by_hand(repository, f"grep -rn 'github.com/{ORG}/{SELF}#' -- '*.md'")
    )
