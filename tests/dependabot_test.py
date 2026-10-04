# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 11's Dependabot ecosystems, read off each `dependabot.yml`.

The section gives `github-actions` to every tree, workflows for it to
read being every tier's, and makes the others conditional on what the
tree holds: a lock file, a site Gemfile, a submodule, a Dockerfile whose
base images are pinned by digest. So an ecosystem is owed exactly where
its subject is there to be read, which is section 2's rule for a subject
a tree does not hold. Dependabot has a `pre-commit` ecosystem too, and
section 11 says the maintainer keeps pre-commit.ci for hook `rev:` bumps
instead; section 2 lists the file among what `.github/` holds.

The section also states how a declared ecosystem is configured -- grouped,
weekly, a seven-day cooldown, no `target-branch` -- and, for `uv`, what its
group is named. Those are read below too, each against the sentence that
states it.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import by_hand, tracked

if TYPE_CHECKING:
    from pathlib import Path

pytestmark = pytest.mark.integration

CONFIG = ".github/dependabot.yml"

DECLARED = f"sed -n 's/^ *- *package-ecosystem: *//p' {CONFIG}"
"""How a reader takes the ecosystems out of the file in a checkout."""

EVERY_TREE = {"github-actions"}
"""Section 11's ecosystem every tree declares, whatever else it holds."""

WATCHED = {
    "uv": ("uv.lock", "*/uv.lock"),
    "bundler": ("Gemfile", "*/Gemfile"),
    "gitsubmodule": (".gitmodules",),
}
"""Section 11's conditional ecosystems, each against what it watches.

The pathspecs are `git ls-files`'s, so a lock file and a site Gemfile are
found wherever the tree keeps them and a submodule by the file git writes
at the root.
"""

PATHSPECS = " ".join(
    f"'{pattern}'" for patterns in WATCHED.values() for pattern in patterns
)
"""The pathspecs above, as a reader passes them to `git ls-files`."""

DOCKER = "docker"
"""Section 11's ecosystem for a base image a digest pins."""

DOCKERFILES = (":(icase)*dockerfile*", ":(icase)*containerfile*")
"""Where a tree keeps a Dockerfile, as `git ls-files` pathspecs.

The section asks for a Dockerfile a workflow builds, and a workflow
names none in a form this suite reads: ClusterFuzzLite's
`build_fuzzers` action finds `.clusterfuzzlite/Dockerfile` by
convention, so a tracked Dockerfile is taken as built. A pathspec
matches a directory's name too, so `DOCKERFILE` then keeps the files
whose own name is one.
"""

DOCKERFILE = re.compile("dockerfile|containerfile", re.IGNORECASE)
"""The file names dependabot-core's `docker` fetcher takes from a
directory: `DOCKER_REGEXP` in its `docker/lib/dependabot/docker/
file_fetcher.rb`.
"""

LISTED = " ".join(f"'{pattern}'" for pattern in DOCKERFILES)
"""The pathspecs above, as a reader passes them to `git ls-files`."""

HEREDOC = re.compile(r"<<-?([\"']?)(\w+)\1")
"""A heredoc an instruction opens: its quote, and the word that ends it."""

FROM = re.compile(r"FROM\s+(?:--\S+\s+)*(\S+)(?:\s+AS\s+(\S+))?", re.IGNORECASE)
"""A `FROM` instruction: its image, and the stage name it gives, if any."""

RESERVED = "scratch"
"""Docker's reserved empty image, which no digest pins nor needs to."""

DOCKER_DIRECTORIES = (
    f"awk '/package-ecosystem:/ {{d = /docker/}} d && /director/' {CONFIG}"
)
"""How a reader takes the `docker` blocks' directories out of the file."""

NAMED = EVERY_TREE | set(WATCHED) | {DOCKER}
"""Every ecosystem section 11 names, conditional or not."""

UV_GROUP = "dev-tooling"
"""Section 11's name for the `uv` ecosystem's group."""

COOLDOWN_DAYS = 7
"""Section 11's cooldown, in days, before an update is offered."""


def updates(repository: str, trees: dict[str, Path]) -> list[dict[str, Any]]:
    """Return every `updates:` entry a repository's file declares.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the parsed entries, whatever they hold.
    :raises FileNotFoundError: where the tree has no `dependabot.yml`,
        section 2 listing it among what `.github/` holds.
    """
    path = trees[repository] / CONFIG
    if not path.is_file():
        msg = f"{repository} has no {CONFIG}; " + by_hand(repository, DECLARED)
        raise FileNotFoundError(msg)
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    declared: list[dict[str, Any]] = parsed.get("updates", [])
    return declared


def ecosystems(repository: str, trees: dict[str, Path]) -> set[str]:
    """Return every `package-ecosystem` a repository's file declares.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the ecosystems declared, whatever they are.
    :raises FileNotFoundError: where the tree has no `dependabot.yml`,
        section 2 listing it among what `.github/` holds.
    """
    return {entry["package-ecosystem"] for entry in updates(repository, trees)}


def instructions(text: str) -> list[str]:
    """Return a Dockerfile's instructions, one string each.

    A line ending in a backslash continues onto the next, and a line
    opening a heredoc is followed by its body up to the word ending it:
    neither the continuation nor the body is an instruction of its own,
    so a `from` a `RUN` script holds is no `FROM`. Comment lines are
    none either. A file changing its escape character with a parser
    directive is read as though it had not.

    :param text: the file's content.
    :returns: each instruction, its continuation lines joined to it.
    """
    out: list[str] = []
    lines = iter(text.splitlines())
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        instruction = line.rstrip()
        while instruction.endswith("\\"):
            following = next(lines, "")
            if not following.lstrip().startswith("#"):
                instruction = instruction[:-1] + " " + following.rstrip()
        for heredoc in HEREDOC.finditer(instruction):
            for body in lines:
                if body.lstrip("\t") == heredoc.group(2):
                    break
        out.append(instruction.strip())
    return out


def pinned(dockerfile: Path) -> bool:
    """Say whether every base image a Dockerfile names is pinned by digest.

    A `FROM` naming an earlier stage of the same file names no image, and
    `scratch` names the empty one: neither is asked for a digest.

    :param dockerfile: the file to read.
    :returns: whether it has a base image, and each one carries `@sha256:`.
    """
    stages = {RESERVED}
    images = []
    for instruction in instructions(dockerfile.read_text(encoding="utf-8")):
        match = FROM.fullmatch(instruction)
        if match is None:
            continue
        image, stage = match.groups()
        if image.lower() not in stages:
            images.append(image)
        if stage:
            stages.add(stage.lower())
    return bool(images) and all("@sha256:" in image for image in images)


def directory(path: str) -> str:
    """Return the `directory:` Dependabot is given for a tracked file.

    :param path: the file, relative to the root of the tree.
    :returns: its directory, absolute from the root, as the key spells it.
    """
    parent = path.rpartition("/")[0]
    return f"/{parent}"


def test_dependabot_watches_only_the_ecosystems_section_11_names(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Every declared `package-ecosystem` is one the section names.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    unknown = sorted(ecosystems(repository, trees) - NAMED)
    assert not unknown, f"ecosystems section 11 does not name: {unknown}; " + by_hand(
        repository, DECLARED
    )


def test_dependabot_watches_what_section_11_gives_every_tree(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """`github-actions`, the one ecosystem the section makes no tree earn.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    missing = sorted(EVERY_TREE - ecosystems(repository, trees))
    assert not missing, (
        f"ecosystems section 11 gives every tree and this one omits: {missing}; "
        + by_hand(repository, DECLARED)
    )


def test_dependabot_watches_a_conditional_ecosystem_where_its_subject_is_there(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """`uv` where the tree has a lock file, and the other two likewise.

    Both directions, since an ecosystem watching what the tree does not
    have and a subject nothing watches are the same disagreement with
    the section read from either end.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    declared = ecosystems(repository, trees) & set(WATCHED)
    owed = {name for name, patterns in WATCHED.items() if tracked(root, *patterns)}
    assert declared == owed, (
        f"conditional ecosystems declared {sorted(declared)}, and the tree holds"
        f" what {sorted(owed)} watch; "
        + by_hand(repository, f"{DECLARED}; git ls-files {PATHSPECS}")
    )


def test_dependabot_watches_docker_where_a_dockerfile_is_pinned_by_digest(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """A `docker` block where a pinned Dockerfile is, and nowhere else.

    Both directions, as for the other conditional ecosystems, and keyed
    on `directory:` rather than on the ecosystem alone: section 11 puts
    the block where the Dockerfile is, dependabot-core reading that
    directory and none below it.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    root = trees[repository]
    declared = {
        path.rstrip("/") or "/"
        for entry in updates(repository, trees)
        if entry["package-ecosystem"] == DOCKER
        for path in entry.get("directories") or [entry.get("directory", "")]
    }
    owed = {
        directory(path)
        for path in tracked(root, *DOCKERFILES)
        if DOCKERFILE.search(path.rpartition("/")[2]) and pinned(root / path)
    }
    assert declared == owed, (
        f"docker declared for {sorted(declared)}, and Dockerfiles pinned by"
        f" digest are in {sorted(owed)}; "
        + by_hand(
            repository,
            f"{DOCKER_DIRECTORIES}; git ls-files {LISTED} | xargs grep -Hi '^ *FROM'",
        )
    )


def test_dependabot_ecosystems_are_grouped_weekly_with_a_cooldown(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Every ecosystem groups, waits a week, and cools down seven days.

    Section 11: "Each ecosystem groups its updates into one pull
    request... Weekly with a seven-day cooldown... None declares a
    `target-branch`."

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    wrong = []
    for entry in updates(repository, trees):
        ecosystem = entry["package-ecosystem"]
        if not entry.get("groups"):
            wrong.append(f"{ecosystem}: no groups:")
        schedule = entry.get("schedule") or {}
        if schedule.get("interval") != "weekly":
            wrong.append(f"{ecosystem}: interval {schedule.get('interval')!r}")
        if (entry.get("cooldown") or {}).get("default-days") != COOLDOWN_DAYS:
            wrong.append(f"{ecosystem}: cooldown {entry.get('cooldown')!r}")
        if "target-branch" in entry:
            wrong.append(f"{ecosystem}: target-branch {entry['target-branch']!r}")
    assert not wrong, f"{'; '.join(wrong)}; " + by_hand(repository, f"cat {CONFIG}")


def test_dependabot_the_uv_ecosystem_names_its_group_dev_tooling(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """The `uv` ecosystem's group is named `dev-tooling` everywhere.

    Section 11 states the name. A tree with no `uv` ecosystem has
    nothing to check here and passes vacuously; whether it is owed one
    at all is `test_dependabot_watches_a_conditional_ecosystem_where_
    its_subject_is_there`'s question, not this one's.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    wrong = [
        sorted((entry.get("groups") or {}).keys())
        for entry in updates(repository, trees)
        if entry["package-ecosystem"] == "uv"
        and sorted((entry.get("groups") or {}).keys()) != [UV_GROUP]
    ]
    assert not wrong, (
        f"uv ecosystem's group is {wrong}, section 11 names {UV_GROUP!r}; "
        + by_hand(repository, f"cat {CONFIG}")
    )
