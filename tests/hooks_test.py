"""The hooks section 4 says every lint gate runs, read off each gate.

`.pre-commit-config.yaml` is the lint gate, and a hook it does not name
does not run: a hook commented out with a reason beside it is read here
exactly as one never added, which is the point -- section 4 lists these
without a condition, so where a tree declines one the finding is either
the tree's or the section's, and the issue the backlog names is where
that is decided.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from .organization import by_hand, tracked
from .repositories import Tier

pytestmark = pytest.mark.integration

CONFIG = ".pre-commit-config.yaml"

SYNTAX = {
    "check-yaml": ("*.yml", "*.yaml"),
    "check-json": ("*.json", "*.ipynb"),
    "check-toml": ("*.toml",),
    "pretty-format-json": ("*.json", "*.ipynb"),
}
"""Section 4's *syntax* bullet, each hook against the files it reads.

The pathspecs are `identify`'s tags as git sees them -- a notebook is
tagged `json` and a `.jsonc` is tagged nothing -- because the bullet is
conditional on the tree through section 4's *file checking itself*:
`check-hooks-apply` refuses a hook that matches nothing, so a syntax
hook is owed exactly where the tree tracks its file type.
"""

LOCAL = ("toml-comment-width", "decoded-subprocess-encoding")
"""The two of section 4's local hooks that have a subject in any Python tree.

`local-link-prefix` is the third and is compared by `verbatim_test.py`
as part of the file that carries it; mypy is the fourth and is a test
of its own below, section 6 asking for it by name.
"""

MYPY = ("mypy", "mirrors-mypy")
"""The two shapes section 4 gives the mypy hook: local, or the mirror.

The mirror's hook id is `mypy` as well; the repository url is what tells
the two apart, and either answers section 6.
"""


def hooks(repository: str, trees: dict[str, Path]) -> list[dict[str, Any]]:
    """Every hook a repository's lint gate names, in file order.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the hook mappings, each with its repository url under `repo`.
    :raises FileNotFoundError: where the tree has no lint gate at all,
        section 4 naming the file as every repository's.
    """
    path = trees[repository] / CONFIG
    if not path.is_file():
        msg = f"{repository} has no {CONFIG}; " + by_hand(repository, f"ls {CONFIG}")
        raise FileNotFoundError(msg)
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [
        {**hook, "repo": entry["repo"]}
        for entry in parsed.get("repos", [])
        for hook in entry.get("hooks", [])
    ]


def ids(repository: str, trees: dict[str, Path]) -> set[str]:
    """Return the ids of every hook a repository's lint gate names.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :returns: the ids.
    """
    return {hook["id"] for hook in hooks(repository, trees)}


def test_the_syntax_hooks_run(repository: str, trees: dict[str, Path]) -> None:
    """Section 4's *syntax* bullet, wherever the tree has the file type.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    running = ids(repository, trees)
    missing = sorted(
        hook
        for hook, patterns in SYNTAX.items()
        if hook not in running and tracked(trees[repository], *patterns)
    )
    assert not missing, (
        f"syntax hooks the gate does not run over files it tracks: {missing}; "
        + by_hand(
            repository,
            f"grep -nE '^ *- id: ({'|'.join(SYNTAX)})' {CONFIG};"
            " git ls-files '*.json' '*.ipynb' '*.toml' '*.yml' '*.yaml'",
        )
    )


@pytest.mark.tier(Tier.PYTHON)
def test_name_tests_test_runs_at_its_default(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """Sections 4 and 7: `name-tests-test` at its default, `*_test.py`.

    The default is what the hook enforces when given no argument, so an
    argument selecting another pattern is the same finding as the hook
    being absent. Asked only of a tree with a `tests/` directory: the
    hook matches nothing elsewhere, and `check-hooks-apply` would refuse
    it there.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    if not (trees[repository] / "tests").is_dir():
        pytest.skip(f"{repository} has no tests/ directory")
    found = [
        hook for hook in hooks(repository, trees) if hook["id"] == "name-tests-test"
    ]
    command = by_hand(repository, f"grep -n -A1 '^ *- id: name-tests-test' {CONFIG}")
    assert found, "name-tests-test is not in the gate; " + command
    arguments = [argument for hook in found for argument in hook.get("args", [])]
    assert not arguments, (
        f"name-tests-test is given {arguments}, not its default; " + command
    )


@pytest.mark.tier(Tier.PYTHON)
def test_the_local_hooks_run(repository: str, trees: dict[str, Path]) -> None:
    """Section 4's local hooks with a subject in every Python tree.

    `toml-comment-width` has one wherever there is a `pyproject.toml`,
    which is what the tier says there is, and section 3 names it as what
    holds that file's comments to 80 columns.
    `decoded-subprocess-encoding` has one wherever a child process is
    decoded, and a tree that decodes none today is the tree in which the
    first locale-decoded call is refused by nothing. Not spelled as the
    keyword here: the hook is a pygrep over every Python line, a
    docstring's included, and this one is in its own file set.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    missing = sorted(set(LOCAL) - ids(repository, trees))
    assert not missing, f"local hooks the gate does not run: {missing}; " + by_hand(
        repository, f"grep -oE 'id: ({'|'.join(LOCAL)})' {CONFIG}"
    )


@pytest.mark.tier(Tier.PYTHON)
def test_the_gate_runs_mypy(repository: str, trees: dict[str, Path]) -> None:
    """Section 6: configured is not enforced, and the gate runs mypy.

    Either of section 4's two shapes answers. `strict = true` with no
    hook running it is the finding section 15 names on its own: the
    strictness is declared and the code is unchecked.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    runs = [
        hook["id"]
        for hook in hooks(repository, trees)
        if hook["id"] in MYPY or hook["repo"].endswith("/mirrors-mypy")
    ]
    assert runs, "no hook runs mypy; " + by_hand(
        repository, f"grep -n 'mirrors-mypy\\|id: mypy' {CONFIG}"
    )
