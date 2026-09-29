# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The dependency graph on the organization's page is what the trees declare.

`profile/dependencies.dot` is written by hand, and what it draws is a
fact of the other repositories: a dependency one of them adds or drops
leaves the picture wrong with nothing red in either tree. This reads
every tree's `pyproject.toml` and `.gitmodules`, applies the rule the
source's own header states for what is a node and what is an arrow, and
compares the result with the source. Whether the SVG is what that source
renders to is the `check-dependencies` hook's question, not this
module's.

The drawing is the transitive reduction of what is declared, so the
comparison is by what each package installs and not arrow by arrow. A
requirement is a dependent, the group of its `pyproject.toml` that
names it -- `dependencies`, or one extra -- a target and the extras it
asks of the target. What installing a package with an extra installs is
what the requirements reach from that state, where asking a target for
an extra is a requirement of the target's own group of that name. An
arrow drawn between two packages stands for every requirement of one on
the other, the extras being read from the tree and written nowhere on
the drawing. The drawing is right where it draws no arrow the trees do
not declare, draws each in the style its requirements have, installs
from every state what the trees' own requirements install, and draws
no arrow the others already imply.
"""

from __future__ import annotations

import configparser
import re
from collections import defaultdict
from typing import TYPE_CHECKING, Any, NamedTuple

import pytest

from . import ROOT

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

GRAPH = ROOT / "profile" / "dependencies.dot"

BUNDLED = "bundled"
"""The label of a line joining a package to the C library it bundles."""


class Drawing(NamedTuple):
    """What a graph source draws."""

    nodes: frozenset[str]
    """The packages."""

    libraries: frozenset[str]
    """The C libraries, drawn as grey dashed outlines."""

    arrows: dict[tuple[str, str], str]
    """Each arrow, a dependent and its target, against `solid` or `dashed`."""

    bundled: frozenset[tuple[str, str]]
    """Each dotted line, a package and the library it bundles."""


class Requirement(NamedTuple):
    """One requirement of a tree on another tree's package."""

    dependent: str
    group: str
    """`dependencies` as the empty string, an extra as its normalized name."""

    target: str
    asked: frozenset[str]
    """The extras of the target the requirement asks for, normalized."""


type State = tuple[str, str]
"""A package and one of its extras, the empty string being none."""

NOTHING = re.compile(r"\s*")

STATEMENT = re.compile(
    r'\s*(?P<head>"[^"]+"(?:\s*->\s*"[^"]+")?|graph|node|edge)'
    r"(?:\s*\[(?P<attributes>[^\]]*)\])?\s*;"
)
"""A statement of the source: a node or an edge, or defaults for either."""

ATTRIBUTE = re.compile(r'\s*(?P<name>[a-z]+)=(?P<value>"[^"]*"|[A-Za-z0-9.#]+)\s*(,|$)')
"""One `name=value` of an attribute list, the values quoted or bare."""

SIZE = {"width", "height", "fixedsize"}
"""The defaults on `node` that say how big every box is."""

ALLOWED = {
    "graph": {"bgcolor", "outputorder", "pad"},
    "node": {
        "shape",
        "style",
        "color",
        "fillcolor",
        "fontcolor",
        "fontname",
        "fontsize",
        "width",
        "height",
        "fixedsize",
    },
    "edge": {"color", "fontcolor", "fontname", "fontsize", "arrowsize"},
    "package": {"pos"},
    "library": {"pos", "style", "color", "fontcolor"},
    "arrow": {"pos", "style"},
    "line": {"pos", "lp", "style", "label", "arrowhead"},
}
"""What each kind of statement may set, and so what this reads of it."""

REQUIREMENT = re.compile(
    r"^\s*([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)\s*(?:\[([^]]*)\])?"
)
"""The distribution name opening a PEP 508 requirement, and its extras."""


def normalized(name: str) -> str:
    """Spell a distribution or an extra name as PEP 503 and PEP 685 compare it.

    :param name: the name as written.
    :returns: the name lowercased, each run of `-`, `_` and `.` a `-`.
    """
    return re.sub(r"[-_.]+", "-", name).lower()


def attributes(text: str, where: str) -> dict[str, str]:
    """Read one attribute list.

    :param text: what sits between the brackets.
    :param where: the statement, for the error.
    :returns: each name against its value, unquoted.
    :raises ValueError: where the list is not `name=value` pairs.
    """
    found: dict[str, str] = {}
    position = 0
    while text[position:].strip():
        match = ATTRIBUTE.match(text, position)
        if not match:
            msg = f"{where} has an attribute list this does not read: {text!r}"
            raise ValueError(msg)
        found[match["name"]] = match["value"].strip('"')
        position = match.end()
    return found


def statements(path: Path) -> list[tuple[int, str, dict[str, str]]]:
    """Split a graph source into its statements.

    :param path: the `.dot` file.
    :returns: each statement's line, its head and its attributes.
    :raises ValueError: on text that is not a statement this reads.
    """
    text = re.sub(r"//[^\n]*", "", path.read_text(encoding="utf-8"))
    wrapper = re.fullmatch(r"\s*digraph [a-z]+ \{(?P<body>.*)\}\s*", text, re.DOTALL)
    if not wrapper:
        msg = f"{path.name} is not a single `digraph name {{ ... }}`"
        raise ValueError(msg)
    offset = wrapper.start("body")
    body = wrapper["body"]
    out: list[tuple[int, str, dict[str, str]]] = []
    position = 0
    while not NOTHING.fullmatch(body, position):
        match = STATEMENT.match(body, position)
        if not match:
            shown = body[position:].strip().splitlines()[0]
            line = text.count("\n", 0, offset + body.index(shown, position)) + 1
            msg = f"{path.name}:{line} is a line this does not read: {shown!r}"
            raise ValueError(msg)
        line = text.count("\n", 0, offset + match.start("head")) + 1
        where = f"{path.name}:{line}"
        out.append((line, match["head"], attributes(match["attributes"] or "", where)))
        position = match.end()
    return out


POINT = re.compile(r"(-?[0-9.]+),(-?[0-9.]+)")

TOLERANCE = 0.5
"""How far a route's end may sit from the edge of a box, in points: a route
is written in whole points and a box's half-width is not one."""

POINTS_PER_INCH = 72


def on_box(point: str, centre: tuple[float, float], half: tuple[float, float]) -> bool:
    """Say whether a point lies on the outline of a box.

    :param point: `x,y`.
    :param centre: the box's centre.
    :param half: half its width and half its height.
    :returns: whether the point is inside the box and on one of its sides.
    """
    match = POINT.fullmatch(point)
    if not match:
        return False
    dx = abs(float(match[1]) - centre[0])
    dy = abs(float(match[2]) - centre[1])
    inside = dx <= half[0] + TOLERANCE and dy <= half[1] + TOLERANCE
    return inside and (abs(dx - half[0]) <= TOLERANCE or abs(dy - half[1]) <= TOLERANCE)


def route_problem(
    pos: str,
    *,
    arrowhead: bool,
    ends: tuple[tuple[float, float], tuple[float, float]],
    half: tuple[float, float],
) -> str | None:
    """Say what is wrong with where an edge is painted, if anything.

    `neato` with `nop: 2` paints an edge along its `pos` whatever nodes
    its statement names, so the statement says nothing of what is seen:
    the route has to start on the dependent's box and end on the
    target's, and an arrow's `pos` opens with `e,` and the point its
    head lands on.

    :param pos: the edge's `pos`.
    :param arrowhead: whether the edge has one, and so opens with `e,`.
    :param ends: the centres of the dependent and of the target.
    :param half: half the width and half the height of every box.
    :returns: the finding, or `None`.
    """
    words = pos.split()
    tip = None
    if arrowhead:
        if not words or not words[0].startswith("e,"):
            return "an arrow's pos has to open with `e,` and its tip"
        tip = words[0][2:]
        words = words[1:]
    elif words and words[0].startswith("e,"):
        return "a line with no arrowhead has no `e,` in its pos"
    if not words:
        return "a pos has no point"
    if not on_box(words[0], ends[0], half):
        return f"its route starts at {words[0]}, off the dependent's box"
    last = tip if tip is not None else words[-1]
    if not on_box(last, ends[1], half):
        return f"its route ends at {last}, off the target's box"
    return None


class Statements(NamedTuple):
    """The statements of a graph source, sorted by what they draw."""

    nodes: set[str]
    libraries: set[str]
    centres: dict[str, tuple[float, float]]
    size: dict[str, str]
    edges: list[tuple[int, str, str, dict[str, str]]]


def sorted_statements(path: Path) -> Statements:  # noqa: C901
    """Read the defaults and the nodes, and set the edges aside.

    :param path: the `.dot` file.
    :returns: what it holds.
    :raises ValueError: on a statement this does not read.
    """
    nodes: set[str] = set()
    libraries: set[str] = set()
    centres: dict[str, tuple[float, float]] = {}
    size: dict[str, str] = {}
    edges: list[tuple[int, str, str, dict[str, str]]] = []
    for line, head, attrs in statements(path):
        where = f"{path.name}:{line}"
        if head in {"graph", "node", "edge"}:
            unread = sorted(set(attrs) - ALLOWED[head])
            if unread:
                msg = f"{where} sets {unread} on `{head}`, which this does not read"
                raise ValueError(msg)
            if head == "node":
                size = {k: v for k, v in attrs.items() if k in SIZE}
            continue
        names = re.findall(r'"([^"]+)"', head)
        if len(names) == 2:  # noqa: PLR2004
            kind = "line" if attrs.get("style") == "dotted" else "arrow"
            if "pos" not in attrs:
                msg = f"{where} draws an edge with no pos"
                raise ValueError(msg)
            unread = sorted(set(attrs) - ALLOWED[kind])
            if unread:
                msg = f"{where} sets {unread} on an edge, which this does not read"
                raise ValueError(msg)
            edges.append((line, names[0], names[1], attrs))
            continue
        style = attrs.get("style")
        centre = POINT.fullmatch(attrs.get("pos", ""))
        if style not in {None, "rounded,dashed"} or not centre:
            msg = f"{where} draws a node this does not read: {attrs}"
            raise ValueError(msg)
        if names[0] in nodes | libraries:
            msg = f"{where} draws {names[0]} a second time"
            raise ValueError(msg)
        centres[names[0]] = (float(centre[1]), float(centre[2]))
        unread = sorted(set(attrs) - ALLOWED["library" if style else "package"])
        if unread:
            msg = f"{where} sets {unread} on a node, which this does not read"
            raise ValueError(msg)
        (libraries if style else nodes).add(names[0])
    return Statements(nodes, libraries, centres, size, edges)


def drawn(path: Path) -> Drawing:
    """Read the nodes, the arrows and the dotted lines a graph source draws.

    Every statement is one of the shapes `STATEMENT` names and sets only
    what `ALLOWED` lists for its kind, and any other is refused rather
    than skipped -- a subgraph, an unquoted node, a label on a dependency
    arrow, a node with no `pos`, a pair or a node drawn twice -- and an
    edge is painted where its `pos` puts it, so that has to run between
    the boxes of the two nodes it names. Nothing the source draws can then
    be missing from what this compares. A node drawn dashed is a C
    library, and a dotted edge is a bundling and carries the label
    `bundled` and no arrowhead.

    :param path: the `.dot` file.
    :returns: what it draws.
    :raises ValueError: on a statement this does not read.
    """
    nodes, libraries, centres, size, edges = sorted_statements(path)
    if size.get("fixedsize") != "true" or not {"width", "height"} <= set(size):
        msg = f"{path.name} sets no fixed width and height on `node`"
        raise ValueError(msg)
    half = (
        float(size["width"]) * POINTS_PER_INCH / 2,
        float(size["height"]) * POINTS_PER_INCH / 2,
    )
    arrows: dict[tuple[str, str], str] = {}
    bundled: set[tuple[str, str]] = set()
    for line, dependent, target, attrs in edges:
        where = f"{path.name}:{line}"
        if (dependent, target) in arrows or (dependent, target) in bundled:
            msg = f"{where} draws {dependent} -> {target} a second time"
            raise ValueError(msg)
        if not {dependent, target} <= nodes | libraries:
            msg = f"{where} draws an edge to a node that is not drawn"
            raise ValueError(msg)
        style = attrs.get("style", "solid")
        found = route_problem(
            attrs["pos"],
            arrowhead=style != "dotted",
            ends=(centres[dependent], centres[target]),
            half=half,
        )
        if found:
            msg = f"{where} draws {dependent} -> {target} where it is not: {found}"
            raise ValueError(msg)
        if style == "dotted":
            if (
                attrs.get("label") != BUNDLED
                or attrs.get("arrowhead") != "none"
                or "lp" not in attrs
                or dependent not in nodes
                or target not in libraries
            ):
                msg = (
                    f"{where} draws a dotted line that is not a package "
                    f"joined to a library, labelled {BUNDLED!r} with `lp` and "
                    "no arrowhead"
                )
                raise ValueError(msg)
            bundled.add((dependent, target))
        elif style in {"solid", "dashed"} and {dependent, target} <= nodes:
            arrows[dependent, target] = style
        else:
            msg = f"{where} draws an arrow this does not read: {dependent} -> {target}"
            raise ValueError(msg)
    return Drawing(frozenset(nodes), frozenset(libraries), arrows, frozenset(bundled))


def declared(
    pyprojects: dict[str, dict[str, Any]],
) -> tuple[set[str], set[Requirement]]:
    """Derive the packages and the requirements the trees' files declare.

    A package is a tree that builds a distribution, `[build-system]`
    being what says it does. A requirement is one that names such a
    package, from a tree that builds one: a tree that builds none draws
    nothing, whatever it requires.

    :param pyprojects: every tree's parsed file.
    :returns: the packages and the requirements.
    """
    projects: dict[str, dict[str, Any]] = {}
    for repository, document in pyprojects.items():
        name = document.get("project", {}).get("name")
        assert name, f"{repository}'s pyproject.toml names no [project] to draw"
        if "build-system" in document:
            projects[name] = document["project"]
    ours = {normalized(name): name for name in projects}

    def named(group: str, dependent: str, requirements: list[str]) -> set[Requirement]:
        found: set[Requirement] = set()
        for requirement in requirements:
            match = REQUIREMENT.match(requirement)
            assert match, f"{dependent} requires {requirement!r}, which names nothing"
            target = ours.get(normalized(match[1]))
            if target is None or target == dependent:
                continue
            asked = frozenset(
                normalized(e) for e in (match[2] or "").split(",") if e.strip()
            )
            found.add(Requirement(dependent, group, target, asked))
        return found

    requirements: set[Requirement] = set()
    for name, project in projects.items():
        requirements |= named("", name, project.get("dependencies", []))
        for extra, extras in project.get("optional-dependencies", {}).items():
            requirements |= named(normalized(extra), name, extras)
    return set(projects), requirements


def bundled(
    pyprojects: dict[str, dict[str, Any]], gitmodules: dict[str, str]
) -> set[tuple[str, str]]:
    """Derive the C libraries the trees bundle.

    The submodule `X` of a tree that builds a distribution is the library
    `libX`, which is what the source names it.

    :param pyprojects: every tree's parsed file.
    :param gitmodules: the text of each tree's `.gitmodules`, where it has one.
    :returns: each package and the library it bundles.
    """
    found: set[tuple[str, str]] = set()
    for repository, text in gitmodules.items():
        document = pyprojects.get(repository, {})
        if "build-system" not in document:
            continue
        parser = configparser.ConfigParser()
        parser.read_string(text)
        found |= {
            (document["project"]["name"], "lib" + section.split('"')[1])
            for section in parser.sections()
        }
    return found


def installed(requirements: Iterable[Requirement], start: State) -> frozenset[State]:
    """Reach everything installing a package with an extra installs.

    An extra of a package includes the package itself, and a requirement
    asking a target for an extra is a requirement of that target's own
    group of the name.

    :param requirements: what the trees require.
    :param start: the package, and the extra installed with it or none.
    :returns: every package and extra reached, `start` included.
    """
    by_group: dict[State, list[Requirement]] = defaultdict(list)
    for requirement in requirements:
        by_group[requirement.dependent, requirement.group].append(requirement)
    seen = {start}
    pending = [start]
    while pending:
        name, extra = pending.pop()
        reached = [(name, "")] if extra else []
        for requirement in by_group[name, extra]:
            reached.append((requirement.target, ""))
            reached += [(requirement.target, asked) for asked in requirement.asked]
        for state in reached:
            if state not in seen:
                seen.add(state)
                pending.append(state)
    return frozenset(seen)


def starts(packages: Iterable[str], requirements: Iterable[Requirement]) -> set[State]:
    """List every way a package is installed: bare, or with one of its extras.

    :param packages: the packages.
    :param requirements: what the trees require.
    :returns: each package and each extra it has, and each with none.
    """
    return {(name, "") for name in packages} | {
        (r.dependent, r.group) for r in requirements if r.group
    }


def naming_problems(
    packages: set[str], libraries: set[tuple[str, str]], drawing: Drawing
) -> list[str]:
    """Compare the nodes and the dotted lines of a drawing with the trees'.

    :param packages: the packages the trees build.
    :param libraries: the C libraries they bundle, each with its package.
    :param drawing: what the source draws.
    :returns: what is wrong with them, one finding to a string.
    """
    found: list[str] = []
    if drawing.nodes != packages:
        found.append(
            f"drawn and no tree's: {sorted(drawing.nodes - packages)}; "
            f"a tree's and not drawn: {sorted(packages - drawing.nodes)}"
        )
    if drawing.bundled != libraries:
        found.append(
            "bundled and not declared by a .gitmodules: "
            f"{sorted(drawing.bundled - libraries)}; "
            f"declared by one and not drawn: {sorted(libraries - drawing.bundled)}"
        )
    if drawing.libraries != {library for _, library in libraries}:
        found.append(
            f"drawn as a C library and bundled by no tree: {drawing.libraries}"
        )
    return found


def styles(requirements: set[Requirement]) -> dict[tuple[str, str], str]:
    """Say how each pair of packages is drawn, if it is.

    :param requirements: what the trees require of each other.
    :returns: each dependent and target against `solid` where
        `dependencies` names the target, and `dashed` where only an extra does.
    """
    solid = {(r.dependent, r.target) for r in requirements if not r.group}
    return {
        (r.dependent, r.target): "solid"
        if (r.dependent, r.target) in solid
        else "dashed"
        for r in requirements
    }


def reach_problems(
    packages: set[str], requirements: set[Requirement], pairs: set[tuple[str, str]]
) -> list[str]:
    """Compare what the arrows drawn install with what the trees require.

    :param packages: the packages the trees build.
    :param requirements: what they require of each other.
    :param pairs: the arrows drawn, each a dependent and a target.
    :returns: what is wrong with them, one finding to a string.
    """
    every = starts(packages, requirements)

    def reach(kept: set[tuple[str, str]]) -> dict[State, frozenset[State]]:
        those = [r for r in requirements if (r.dependent, r.target) in kept]
        return {state: installed(those, state) for state in every}

    have = reach(pairs)
    want = {state: installed(requirements, state) for state in every}
    found: list[str] = []
    short = sorted(state for state in want if have[state] != want[state])
    if short:
        found.append(
            "the arrows drawn install less than the trees' requirements for: "
            f"{[(s, sorted(want[s] - have[s])) for s in short]}"
        )
    implied = sorted(pair for pair in pairs if reach(pairs - {pair}) == have)
    if implied:
        found.append(f"drawn and implied by the other arrows drawn: {implied}")
    return found


def problems(
    packages: set[str],
    requirements: set[Requirement],
    libraries: set[tuple[str, str]],
    drawing: Drawing,
) -> list[str]:
    """Compare a drawing with what the trees declare.

    :param packages: the packages the trees build.
    :param requirements: what they require of each other.
    :param libraries: the C libraries they bundle, each with its package.
    :param drawing: what the source draws.
    :returns: what is wrong with the drawing, one finding to a string.
    """
    found = naming_problems(packages, libraries, drawing)
    kinds = styles(requirements)
    undeclared = sorted(set(drawing.arrows) - set(kinds))
    if undeclared:
        found.append(f"drawn and declared by no tree: {undeclared}")
    wrong = sorted(
        pair
        for pair, kind in drawing.arrows.items()
        if pair in kinds and kinds[pair] != kind
    )
    if wrong:
        found.append(f"drawn in the style the tree does not declare: {wrong}")
    return found + reach_problems(
        packages, requirements, set(drawing.arrows) & set(kinds)
    )


def test_every_line_of_the_graph_is_read() -> None:
    """The reader above reads the source this tree commits, whole.

    Offline, so that an edit to the source that `drawn` cannot read is
    refused by `lint.yml` rather than by the next `alignment.yml` run.
    """
    drawing = drawn(GRAPH)
    assert drawing.arrows, f"{GRAPH.name} has no arrow this reads"
    assert drawing.bundled, f"{GRAPH.name} has no bundled library this reads"
    ends = {name for pair in drawing.arrows for name in pair}
    assert ends <= drawing.nodes
    assert {library for _, library in drawing.bundled} == drawing.libraries


@pytest.mark.parametrize(
    "line",
    [
        '    {rank=same; "btclib"; "btclib-ecc";}',
        "    btclib_mnemonics;",
        '    "btclib" [pos="0,0"',
        '    "extra" [];',
        '    "extra" [pos="0,0", style=bold];',
        '    "extra" [pos="0,0", color="red"];',
        '    "btclib" -> "btclib-ecc";',
        '    "btclib" -> "btclib-ecc" [pos="0,0", color="red"];',
        '    "btclib" -> "btclib-ecc" [pos="0,0", label="secp256k1"];',
        '    "btclib" -> "btclib-ecc" [pos="0,0", arrowhead=none];',
        '    "btclib" -> "btclib-ecc" [pos="0,0", style=bold];',
        '    "btclib" -> "btclib-ecc" [pos="0,0", style=dotted];',
        '    "btclib" -> "libsecp256k1" [pos="0,0", style=dotted, label="bundled"];',
        '    "btclib" -> "libsecp256k1" [pos="0,0", style=dashed];',
        '    "btclib" -> "elsewhere" [pos="0,0"];',
        "    edge [style=dashed];",
    ],
)
def test_a_line_the_reader_does_not_know_is_refused(tmp_path: Path, line: str) -> None:
    """A statement drawn another way is an error, not a node or edge dropped.

    :param tmp_path: pytest's per-test directory.
    :param line: a line `drawn` has no reading for.
    """
    source = GRAPH.read_text(encoding="utf-8").replace("\n}\n", f"\n{line}\n}}\n")
    (tmp_path / GRAPH.name).write_text(source, encoding="utf-8")
    with pytest.raises(ValueError, match=r"does not read|draws|is not a single"):
        drawn(tmp_path / GRAPH.name)


ECC_POS = 'pos="e,290,342 290,278 290,278 290,335 290,335"'
SECP_POS = 'pos="e,290,442 290,378 290,378 290,435 290,435"'
BUNDLED_POS = 'pos="290,478 290,478 290,542 290,542"'


@pytest.mark.parametrize(
    ("old", "new"),
    [
        (SECP_POS, ECC_POS),
        (SECP_POS, 'pos="290,378 290,378 290,435 290,435"'),
        (SECP_POS, 'pos="e,290,400 290,378 290,378 290,435 290,435"'),
        (SECP_POS, 'pos="e,290,442 290,300 290,300 290,435 290,435"'),
        (BUNDLED_POS, 'pos="e,290,478 290,478 290,542 290,542"'),
        (BUNDLED_POS, 'pos="290,300 290,478 290,542 290,542"'),
        (BUNDLED_POS, 'pos="290,478 290,478 290,542 290,500"'),
    ],
)
def test_an_edge_painted_where_it_is_not_named_is_refused(
    tmp_path: Path, old: str, new: str
) -> None:
    """The route an edge is painted along is read, and has to join its nodes.

    :param tmp_path: pytest's per-test directory.
    :param old: the `pos` of one edge of the committed source.
    :param new: what replaces it.
    """
    source = GRAPH.read_text(encoding="utf-8")
    assert old in source, "the mutation would change nothing"
    (tmp_path / GRAPH.name).write_text(source.replace(old, new), encoding="utf-8")
    with pytest.raises(ValueError, match="where it is not"):
        drawn(tmp_path / GRAPH.name)


@pytest.mark.parametrize(
    "line",
    [
        '    "btclib" -> "btclib-ecc" [style=dashed, ' + ECC_POS + "];",
        '    "btclib" -> "btclib-ecc" [' + ECC_POS + "];",
        '    "btclib-secp256k1" -> "libsecp256k1" [style=dotted, arrowhead=none, '
        'label="bundled", lp="0,0", ' + BUNDLED_POS + "];",
        '    "btclib" [pos="290,260"];',
    ],
)
def test_a_pair_or_a_node_drawn_twice_is_refused(tmp_path: Path, line: str) -> None:
    """Graphviz draws both, so both would have to be compared.

    :param tmp_path: pytest's per-test directory.
    :param line: a second statement for a node or a pair the source has.
    """
    source = GRAPH.read_text(encoding="utf-8").replace("\n}\n", f"\n{line}\n}}\n")
    (tmp_path / GRAPH.name).write_text(source, encoding="utf-8")
    with pytest.raises(ValueError, match="a second time"):
        drawn(tmp_path / GRAPH.name)


def pyproject(
    name: str,
    *,
    dependencies: list[str] | None = None,
    extras: dict[str, list[str]] | None = None,
    build: bool = True,
) -> dict[str, Any]:
    """Build the parsed file of a tree.

    :param name: the `[project]` name.
    :param dependencies: its `dependencies`.
    :param extras: its `optional-dependencies`.
    :param build: whether the tree builds a distribution.
    :returns: the document.
    """
    project: dict[str, Any] = {"name": name}
    if dependencies is not None:
        project["dependencies"] = dependencies
    if extras is not None:
        project["optional-dependencies"] = extras
    return {"project": project, **({"build-system": {}} if build else {})}


def test_a_requirement_carries_the_extras_it_asks_of_its_target() -> None:
    """Asking a target for an extra is part of the requirement."""
    packages, requirements = declared(
        {
            "a": pyproject("a"),
            "b": pyproject(
                "b",
                dependencies=["a[Fast_x]>=1"],
                extras={"X": ["a", "c; python_version<'4'"]},
            ),
            "c": pyproject("c"),
        }
    )
    assert packages == {"a", "b", "c"}
    assert requirements == {
        Requirement("b", "", "a", frozenset({"fast-x"})),
        Requirement("b", "x", "a", frozenset()),
        Requirement("b", "x", "c", frozenset()),
    }


def test_a_tree_that_builds_nothing_draws_nothing() -> None:
    """A tree without `[build-system]` is no node, and has no arrow."""
    packages, requirements = declared(
        {
            "a": pyproject("a"),
            "b": pyproject("b", dependencies=["a"], build=False),
            "c": pyproject("c", dependencies=["b"]),
        }
    )
    assert packages == {"a", "c"}
    assert requirements == set()


def test_a_submodule_is_a_library_of_the_tree_that_builds() -> None:
    """A `.gitmodules` counts for a tree that builds a distribution only."""
    text = '[submodule "secp256k1"]\n\tpath = secp256k1\n\turl = https://x/y.git\n'
    pyprojects = {"a": pyproject("a-pkg"), "b": pyproject("b", build=False)}
    assert bundled(pyprojects, {"a": text, "b": text}) == {("a-pkg", "libsecp256k1")}


def model(
    *, asks: bool = True, wallet: bool = True
) -> tuple[set[str], set[Requirement]]:
    """Declare a small version of the organization's own shape.

    A base, `ecc`, has an extra that installs `native`, and `top`'s own
    extra asks `ecc` for it where `asks` holds and names `native` itself
    where it does not; `wallet` requires `top` and `ecc` both.

    :param asks: whether `top` asks `ecc` for its extra.
    :param wallet: whether the fourth tree is there.
    :returns: what `declared` derives.
    """
    ecc = ["ecc[native]"] if asks else []
    trees = {
        "native": pyproject("native"),
        "ecc": pyproject("ecc", extras={"native": ["native"]}),
        "top": pyproject(
            "top",
            dependencies=["ecc"],
            extras={"native": ["native", *ecc]},
        ),
    }
    if wallet:
        trees["wallet"] = pyproject("wallet", dependencies=["top", "ecc"])
    return declared(trees)


def draw(
    packages: set[str], solid: set[tuple[str, str]], dashed: set[tuple[str, str]]
) -> Drawing:
    """Build a drawing with no library.

    :param packages: the nodes.
    :param solid: the solid arrows.
    :param dashed: the dashed arrows.
    :returns: the drawing.
    """
    arrows = dict.fromkeys(solid, "solid") | dict.fromkeys(dashed, "dashed")
    return Drawing(frozenset(packages), frozenset(), arrows, frozenset())


def test_the_reduction_of_what_is_declared_is_right() -> None:
    """Where `top` asks for `ecc`'s extra, `top -> native` is not drawn."""
    packages, requirements = model()
    reduction = draw(
        packages,
        {("top", "ecc"), ("wallet", "top")},
        {("ecc", "native")},
    )
    assert problems(packages, requirements, set(), reduction) == []


def test_an_arrow_the_others_imply_is_refused() -> None:
    """`wallet -> ecc` is declared, and `wallet -> top -> ecc` installs it."""
    packages, requirements = model()
    redundant = draw(
        packages,
        {("top", "ecc"), ("wallet", "top"), ("wallet", "ecc")},
        {("ecc", "native")},
    )
    assert problems(packages, requirements, set(), redundant) == [
        "drawn and implied by the other arrows drawn: [('wallet', 'ecc')]"
    ]


def test_an_arrow_an_extra_does_not_ask_for_is_not_implied() -> None:
    """Where `top` does not ask `ecc` for the extra, `top -> native` stays."""
    packages, requirements = model(asks=False)
    reduction = draw(
        packages,
        {("top", "ecc"), ("wallet", "top")},
        {("ecc", "native")},
    )
    (finding,) = problems(packages, requirements, set(), reduction)
    assert finding.startswith("the arrows drawn install less")
    assert "('top', 'native')" in finding
    complete = draw(
        packages,
        {("top", "ecc"), ("wallet", "top")},
        {("ecc", "native"), ("top", "native")},
    )
    assert problems(packages, requirements, set(), complete) == []


def test_an_arrow_the_trees_do_not_declare_is_refused() -> None:
    """A drawn arrow no tree requires is named, however the rest reads."""
    packages, requirements = model(wallet=False)
    invented = draw(
        packages,
        {("top", "ecc"), ("native", "top")},
        {("ecc", "native")},
    )
    assert problems(packages, requirements, set(), invented)[0] == (
        "drawn and declared by no tree: [('native', 'top')]"
    )


def test_an_arrow_drawn_in_the_wrong_style_is_refused() -> None:
    """`ecc -> native` is dashed, `native` being only what an extra installs."""
    packages, requirements = model(wallet=False)
    wrong = draw(packages, {("top", "ecc"), ("ecc", "native")}, set())
    assert problems(packages, requirements, set(), wrong) == [
        "drawn in the style the tree does not declare: [('ecc', 'native')]"
    ]


def test_a_bundled_library_is_compared_with_the_gitmodules() -> None:
    """A library bundled and not drawn, or drawn and not bundled, is named."""
    packages, requirements = model(wallet=False)
    base = draw(packages, {("top", "ecc")}, {("ecc", "native")})
    drawing = base._replace(
        libraries=frozenset({"libx"}), bundled=frozenset({("native", "libx")})
    )
    assert problems(packages, requirements, {("native", "libx")}, drawing) == []
    finding = problems(packages, requirements, {("native", "liby")}, drawing)[0]
    assert "declared by one and not drawn: [('native', 'liby')]" in finding


@pytest.mark.integration
def test_the_graph_draws_what_each_pyproject_declares(
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """`profile/dependencies.dot` is what the trees declare, reduced.

    Each tree is read at the tip of its default branch, which is where
    the `trees` fixture clones it, so a repository still living on a
    build branch is drawn as that branch declares it. The submodules
    themselves are left unfetched, and `.gitmodules` is in the clone.

    :param trees: the checkouts.
    :param pyprojects: every tree's parsed file.
    """
    packages, requirements = declared(pyprojects)
    modules = {
        repository: (root / ".gitmodules").read_text(encoding="utf-8")
        for repository, root in trees.items()
        if (root / ".gitmodules").is_file()
    }
    found = problems(packages, requirements, bundled(pyprojects, modules), drawn(GRAPH))
    assert not found, "; ".join(found)
