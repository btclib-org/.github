# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The dependency graph on the organization's page is what the trees declare.

`profile/dependencies.dot` is written by hand, and what it draws is a
fact of the other repositories: a dependency one of them adds or drops
leaves the picture wrong with nothing red in either tree. This reads
every tree's `pyproject.toml`, applies the rule the source's own header
states for what is a node and what is an edge, and compares the result
with the source. Whether the SVG is what that source renders to is the
`check-dependencies` hook's question, not this module's.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest

from . import ROOT

if TYPE_CHECKING:
    from pathlib import Path

type Edge = tuple[str, str, str, str]
"""A dependent, its dependency, the extra of the dependent naming it --
empty where `dependencies` does -- and the extras the requirement asks
of the dependency, sorted and joined by a comma."""

GRAPH = ROOT / "profile" / "dependencies.dot"

EDGE = re.compile(
    r'^ *"([^"]+)" -> "([^"]+)"(?: \[(style=dashed, )?label="([^"]+)"\])?;$'
)
"""An edge statement, in the one spelling the source writes each kind."""

LABEL = re.compile(r"^(?P<extra>[a-z0-9-]+)?(?: ?\[(?P<asked>[a-z0-9,-]+)\])?$")
"""An edge's label: the dependent's extra on a dashed edge, then the
extras asked of the dependency in brackets."""

NODE = re.compile(r'^ *"([^"]+)";$')
"""A node statement, which the source writes for a node with no edge."""

SETTING = re.compile(
    r"^ *(//.*|digraph [a-z]+ \{|\}|(graph|node|edge) \[([^;]*\];)?"
    r'|[a-z]+=("[^"]*"|[A-Za-z0-9.]+),|\];)?$'
)
"""A line that draws nothing: a comment, the graph's braces, and the
default attributes the source sets, one to a line or bracketed on the
`graph` line."""

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


def drawn(path: Path) -> tuple[set[str], set[Edge]]:
    """Read the nodes and the edges a graph source draws.

    Every line is one of the two statements or one of the shapes
    `SETTING` names, and any other is refused rather than skipped -- a
    subgraph, an unquoted node, an edge with an attribute this does not
    read -- so that nothing the source draws can be missing from what
    this compares.

    :param path: the `.dot` file.
    :returns: the nodes, those an edge names included, and the edges.
    :raises ValueError: on a line this does not read.
    """
    nodes: set[str] = set()
    edges: set[Edge] = set()
    lines = path.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, start=1):
        edge = EDGE.match(line)
        label = LABEL.match(edge[4] or "") if edge else None
        if edge and label and bool(edge[3]) == bool(label["extra"]):
            edges.add((edge[1], edge[2], label["extra"] or "", label["asked"] or ""))
        elif node := NODE.match(line):
            nodes.add(node[1])
        elif not SETTING.match(line):
            msg = f"{path.name}:{number} is a line this does not read: {line!r}"
            raise ValueError(msg)
    return nodes | {name for edge in edges for name in edge[:2]}, edges


def declared(pyprojects: dict[str, dict[str, Any]]) -> tuple[set[str], set[Edge]]:
    """Derive the nodes and the edges the trees' `pyproject.toml` declare.

    A requirement is an edge where it names a distribution one of the
    trees is: solid from `dependencies`, carrying the extras it asks of
    that distribution, and dashed from an extra only where `dependencies`
    does not already name the same target. A node is a tree that builds a
    distribution, `[build-system]` being what says it does, and every tree
    an edge names.

    :param pyprojects: every tree's parsed file.
    :returns: the nodes and the edges.
    """
    projects: dict[str, dict[str, Any]] = {}
    for repository, document in pyprojects.items():
        name = document.get("project", {}).get("name")
        assert name, f"{repository}'s pyproject.toml names no [project] to draw"
        projects[name] = document
    ours = {normalized(name): name for name in projects}

    def named(requirements: list[str], dependent: str) -> dict[str, str]:
        found: dict[str, set[str]] = {}
        for requirement in requirements:
            match = REQUIREMENT.match(requirement)
            assert match, f"{dependent} requires {requirement!r}, which names nothing"
            target = ours.get(normalized(match[1]))
            if target is None or target == dependent:
                continue
            asked = {normalized(e) for e in (match[2] or "").split(",") if e.strip()}
            found.setdefault(target, set()).update(asked)
        return {target: ",".join(sorted(asked)) for target, asked in found.items()}

    edges: set[Edge] = set()
    for name, document in projects.items():
        project = document["project"]
        runtime = named(project.get("dependencies", []), name)
        edges |= {(name, target, "", asked) for target, asked in runtime.items()}
        for extra, requirements in project.get("optional-dependencies", {}).items():
            edges |= {
                (name, target, normalized(extra), asked)
                for target, asked in named(requirements, name).items()
                if target not in runtime
            }
    built = {name for name, document in projects.items() if "build-system" in document}
    return built | {name for edge in edges for name in edge[:2]}, edges


def test_every_line_of_the_graph_is_read() -> None:
    """The reader above reads the source this tree commits, whole.

    Offline, so that an edit to the source that `drawn` cannot read is
    refused by `lint.yml` rather than by the next `alignment.yml` run.
    """
    nodes, edges = drawn(GRAPH)
    assert edges, f"{GRAPH.name} has no edge this reads"
    assert all(edge[0] in nodes and edge[1] in nodes for edge in edges)


@pytest.mark.parametrize(
    "line",
    [
        '    {rank=same; "btclib"; "btclib-ecc";}',
        "    btclib_mnemonics;",
        '    "btclib" -> "btclib-ecc" [color="red"];',
        '    "btclib" -> "btclib-ecc" [label="secp256k1"];',
        '    "btclib" -> "btclib-ecc" [style=dashed, label="[secp256k1]"];',
    ],
)
def test_a_line_the_reader_does_not_know_is_refused(tmp_path: Path, line: str) -> None:
    """A statement drawn another way is an error, not a node or edge dropped.

    :param tmp_path: pytest's per-test directory.
    :param line: a line `drawn` has no reading for.
    """
    source = GRAPH.read_text(encoding="utf-8").replace("\n}\n", f"\n{line}\n}}\n")
    (tmp_path / GRAPH.name).write_text(source, encoding="utf-8")
    with pytest.raises(ValueError, match="is a line this does not read"):
        drawn(tmp_path / GRAPH.name)


def test_an_edge_carries_the_extras_it_asks_of_its_target() -> None:
    """Asking a target for an extra is part of the edge, and not dropped."""
    pyprojects: dict[str, dict[str, Any]] = {
        "a": {"project": {"name": "a"}, "build-system": {}},
        "b": {
            "project": {
                "name": "b",
                "dependencies": ["a[Fast]>=1"],
                "optional-dependencies": {"x": ["a", "c; python_version<'4'"]},
            },
        },
        "c": {"project": {"name": "c"}, "build-system": {}},
    }
    assert declared(pyprojects) == (
        {"a", "b", "c"},
        {("b", "a", "", "fast"), ("b", "c", "x", "")},
    )


@pytest.mark.integration
def test_the_graph_draws_what_each_pyproject_declares(
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """`profile/dependencies.dot` is what the trees' `pyproject.toml` declare.

    Each tree is read at the tip of its default branch, which is where
    the `trees` fixture clones it, so a repository still living on a
    build branch is drawn as that branch declares it.

    :param pyprojects: every tree's parsed file.
    """
    nodes, edges = declared(pyprojects)
    drawn_nodes, drawn_edges = drawn(GRAPH)
    assert drawn_edges == edges, (
        f"drawn and declared by no tree: {sorted(drawn_edges - edges)}; "
        f"declared and not drawn: {sorted(edges - drawn_edges)}"
    )
    assert drawn_nodes == nodes, (
        f"drawn and no tree's: {sorted(drawn_nodes - nodes)}; "
        f"a tree's and not drawn: {sorted(nodes - drawn_nodes)}"
    )
