# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Where a package directory sits, and what it and its modules declare.

Section 2 asks the package directory to sit under `src/`, to hold
`py.typed`, and to hold an `__init__.py` that declares `__all__`, of a
tree that installs an importable package and of no tier in particular.
Section 7 asks the rest of the surface --
`__all__` in every module -- of a package that publishes, taking that
bullet out of its escape clause there: `py.typed` promises the types are
supported, and which names are public is the other half of that promise.
What is asked here is the standard's side of it, that the modules
declare `__all__` at all. The census section 7 asks for beside it walks
an installed package and belongs to the suite of the tree that ships it.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from . import Tier, by_hand, tracked

pytestmark = pytest.mark.integration

TYPED = "py.typed"
"""The marker file section 2 asks the package directory to hold."""

DECLARED = re.compile(r"^__all__\s*(?::[^=]+)?=", re.MULTILINE)
"""A module-level `__all__`, read rather than imported.

Nothing installs the trees this suite clones, so a module importing a
compiled extension could not be imported to be asked for the attribute.
An assignment at the left margin is what the declaration looks like,
its annotated form included.
"""


def is_public(path: str) -> bool:
    """Say whether a module's dotted name is public at every part.

    `__init__` names the package rather than a module of its own, so
    the directory holding it is what decides that part.

    :param path: the module's path, relative to the checkout.
    :returns: whether no part of the dotted name is private.
    """
    parts = (*Path(path).parts[:-1], Path(path).stem)
    return not any(part.startswith("_") for part in parts if part != "__init__")


def package(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> Path | None:
    """Return the package directory of a tree, where it installs one.

    Read off what the tree's own `pyproject.toml` declares rather than
    inferred from where an `__init__.py` happens to sit: under
    `uv_build`, `module-root` and `module-name` say the directory
    outright, `src/` being that backend's own default and section 2's
    own rule alike. A backend the standard does not configure this way
    -- hatchling -- names no directory of its own, so it is found by a
    scan tried at the root first and under `src/` second, the order
    hatchling's own file-selection heuristic tries them in; `tests/` is
    excepted from either.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :param pyprojects: each tree's parsed `pyproject.toml`.
    :returns: the directory relative to the checkout, or None where the
        tree installs no importable package.
    :raises LookupError: where more than one directory answers, the
        bullet naming one -- `module-name` as a list or with a dot
        included, both being `uv_build`'s own namespace-package shapes,
        which section 2 does not allow.
    """
    config = pyprojects.get(repository, {})
    uv = config.get("tool", {}).get("uv", {})
    if uv.get("package") is False:
        return None
    if config.get("build-system", {}).get("build-backend") == "uv_build":
        settings = uv.get("build-backend", {})
        default = config.get("project", {}).get("name", repository).replace("-", "_")
        name = settings.get("module-name", default)
        if name == []:
            return None
        if isinstance(name, list):
            msg = (
                f"{repository} sets module-name to {name}, and section 2"
                " names the package directory rather than several; "
                + by_hand(repository, "grep -n module-name pyproject.toml")
            )
            raise LookupError(msg)
        if "." in name:
            msg = (
                f"{repository} sets module-name to {name}, and section 2"
                " names one tree's own package rather than a module"
                " sharing a namespace with another; "
                + by_hand(repository, "grep -n module-name pyproject.toml")
            )
            raise LookupError(msg)
        root = settings.get("module-root", "src")
        return Path(root) / name if root else Path(name)
    found = sorted(
        {
            Path(path).parent
            for path in tracked(trees[repository], "*__init__.py")
            if Path(path).parent != Path("tests")
            and Path(path).parent.parent in (Path(), Path("src"))
        }
    )
    if len(found) > 1:
        msg = f"{repository} has {found} and section 2 names one; " + by_hand(
            repository, "git ls-files '*__init__.py'"
        )
        raise LookupError(msg)
    return found[0] if found else None


def test_package_refuses_a_module_name_list() -> None:
    """`module-name` as a list is uv_build's namespace-package shape.

    No repository in the organization declares it, so this is a
    synthetic `pyproject.toml` rather than one read off a tree: what is
    asked is that `package()` names the repository and the key rather
    than joining a `Path` to a `list` and raising `TypeError`.
    """
    pyprojects = {
        "a-namespace-package": {
            "build-system": {"build-backend": "uv_build"},
            "tool": {"uv": {"build-backend": {"module-name": ["foo", "bar"]}}},
        }
    }
    with pytest.raises(LookupError, match="module-name"):
        package("a-namespace-package", {}, pyprojects)


def test_package_refuses_a_dotted_module_name() -> None:
    """A dot in `module-name` is `uv_build`'s namespace-package shape.

    No repository in the organization declares one, so this is a
    synthetic `pyproject.toml` rather than one read off a tree:
    `uv_build` reads `module-name = "foo.bar"` as the module `bar` in
    the shared namespace `foo`, built at `src/foo/bar`, not the literal
    `Path("src") / "foo.bar"` a plain join would produce. What is asked
    is that `package()` names the repository and the key rather than
    resolving either path.
    """
    pyprojects = {
        "a-namespace-package": {
            "build-system": {"build-backend": "uv_build"},
            "tool": {"uv": {"build-backend": {"module-name": "foo.bar"}}},
        }
    }
    with pytest.raises(LookupError, match="module-name"):
        package("a-namespace-package", {}, pyprojects)


def test_the_package_directory_is_typed_and_declares_its_surface(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 2: `py.typed` and an `__init__.py` that declares `__all__`.

    Asked of every tree and skipped where there is no package, that
    being the condition the bullet carries rather than a tier.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: each tree's parsed `pyproject.toml`.
    """
    root = trees[repository]
    directory = package(repository, trees, pyprojects)
    if directory is None:
        pytest.skip(f"{repository} installs no importable package")
    command = by_hand(
        repository,
        f"git ls-files '{directory}/{TYPED}';"
        f" grep -n '^__all__' {directory}/__init__.py",
    )
    assert tracked(root, f"{directory}/{TYPED}"), (
        f"{directory} holds no {TYPED}; " + command
    )
    declaration = (root / directory / "__init__.py").read_text(encoding="utf-8")
    assert DECLARED.search(declaration), (
        f"{directory}/__init__.py declares no __all__; " + command
    )


def test_the_package_directory_sits_under_src(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 2: the package directory sits under `src/`.

    Asked of every tree and skipped where there is no package, the same
    condition the bullet above carries.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: each tree's parsed `pyproject.toml`.
    """
    directory = package(repository, trees, pyprojects)
    if directory is None:
        pytest.skip(f"{repository} installs no importable package")
    assert directory.parts[0] == "src", f"{directory} is not under src/; " + by_hand(
        repository, "git ls-files '*__init__.py'"
    )


@pytest.mark.tier(Tier.PUBLISHER)
def test_every_published_module_declares_its_public_surface(
    repository: str,
    trees: dict[str, Path],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 7: `__all__` in every public module of a published package.

    A module under a private name is no part of the surface and is not
    asked, which is the exception the bullet states and the one
    `btclib`'s own census keeps.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    :param pyprojects: each tree's parsed `pyproject.toml`.
    """
    root = trees[repository]
    directory = package(repository, trees, pyprojects)
    assert directory is not None, (
        f"{repository} publishes a package and the tree holds none; "
        + by_hand(repository, "git ls-files '*__init__.py'")
    )
    silent = sorted(
        path
        for path in tracked(root, f"{directory}/*.py")
        if is_public(path)
        and not DECLARED.search((root / path).read_text(encoding="utf-8"))
    )
    assert not silent, (
        f"public modules of a published package declaring no __all__: {silent}; "
        + by_hand(
            repository,
            f"git ls-files '{directory}/*.py'"
            r" | grep -vE '/_[^_]' | xargs grep -L '^__all__'",
        )
    )
