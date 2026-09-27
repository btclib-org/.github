# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for `dependabot_test.py`'s Dockerfile reader, on files built here.

That module asks section 11 whether a `docker` block sits where a
Dockerfile pinned by digest is, and the organization's Dockerfiles are
too plain to show that the reader tells the cases apart: none holds a
heredoc, a continued `RUN` or a `scratch` stage. These build the inputs
a line-by-line reading gets wrong instead.

Nothing here reaches the network, so no `integration` marker: `conftest.py`
skips only the marked tests without the switch, and these run regardless
of it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .dependabot_test import DOCKERFILE, instructions, pinned

if TYPE_CHECKING:
    from pathlib import Path

DIGEST = "python@sha256:" + "0" * 64
"""A base image pinned by digest."""


def dockerfile(tmp_path: Path, text: str) -> Path:
    """Write a Dockerfile and return its path.

    :param tmp_path: pytest's per-test temporary directory.
    :param text: the file's content.
    :returns: the file written.
    """
    path = tmp_path / "Dockerfile"
    path.write_text(text, encoding="utf-8")
    return path


def test_a_heredoc_body_is_no_instruction(tmp_path: Path) -> None:
    """A `from` a `RUN` heredoc holds leaves a pinned file pinned."""
    text = f"FROM {DIGEST}\nRUN python3 - <<PY\nfrom os import path\nPY\n"
    assert pinned(dockerfile(tmp_path, text))


def test_a_tab_stripped_heredoc_ends_at_its_indented_word() -> None:
    """`<<-` ends at the word with its leading tabs removed."""
    text = f"FROM {DIGEST}\nRUN cat <<-'EOF'\n\tfrom os import path\n\tEOF\n"
    assert instructions(text) == [f"FROM {DIGEST}", "RUN cat <<-'EOF'"]


def test_a_continuation_line_is_no_instruction(tmp_path: Path) -> None:
    """A continued `RUN` whose next line begins with `from` is one `RUN`."""
    text = f"FROM {DIGEST}\nRUN echo \\\n  from os import path\n"
    assert pinned(dockerfile(tmp_path, text))


def test_a_comment_inside_a_continuation_does_not_end_it() -> None:
    """A comment line between continued lines is dropped, not an end."""
    text = "RUN a \\\n# note\n  b\n"
    assert [" ".join(line.split()) for line in instructions(text)] == ["RUN a b"]


def test_scratch_is_asked_for_no_digest(tmp_path: Path) -> None:
    """`FROM scratch` beside a pinned image leaves the file pinned."""
    text = f"FROM {DIGEST} AS build\nFROM scratch\nCOPY --from=build / /\n"
    assert pinned(dockerfile(tmp_path, text))


def test_an_earlier_stage_is_asked_for_no_digest(tmp_path: Path) -> None:
    """A `FROM` naming a stage of the same file names no image."""
    text = f"FROM {DIGEST} AS base\nFROM base\n"
    assert pinned(dockerfile(tmp_path, text))


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("FROM python:3.12\n", id="a tag"),
        pytest.param(f"FROM {DIGEST}\nFROM python\n", id="one of two"),
        pytest.param("FROM --platform=linux/amd64 python\n", id="a flag"),
        pytest.param("FROM scratch\n", id="no base image"),
        pytest.param("# FROM x@sha256:0\n", id="a comment"),
    ],
)
def test_a_file_short_of_a_digest_is_not_pinned(tmp_path: Path, text: str) -> None:
    """Every base image carries a digest, and there is at least one.

    :param tmp_path: pytest's per-test temporary directory.
    :param text: the file's content.
    """
    assert not pinned(dockerfile(tmp_path, text))


@pytest.mark.parametrize(
    ("name", "taken"),
    [
        ("Dockerfile", True),
        ("Containerfile", True),
        ("Dockerfile.fuzz", True),
        ("fuzz.dockerfile", True),
        (".dockerignore", False),
        ("docker-compose.yml", False),
    ],
)
def test_a_file_name_is_taken_as_dependabot_core_takes_it(
    name: str,
    taken: bool,  # noqa: FBT001
) -> None:
    """The name filter is dependabot-core's own, case folded.

    :param name: a file's name.
    :param taken: whether dependabot-core's fetcher reads it.
    """
    assert (DOCKERFILE.search(name) is not None) is taken
