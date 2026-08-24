# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What a package directory holds, and what its modules declare.

Section 2 asks the package directory for `py.typed` and an `__init__.py`
that declares `__all__`, of a tree that installs an importable package
and of no tier in particular. Section 7 asks the rest of the surface --
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
    outright, `src/` being that backend's own default and not a layout
    section 2 states, so a tree using it holds no root-level
    `__init__.py` for a scan to find. A backend the standard does not
    configure this way -- `btclib-secp256k1`'s hatchling -- keeps a
    directory of the root carrying an `__init__.py`, `tests/` excepted,
    which is that backend's own default and the shape every such tree
    here uses.

    :param repository: the repository's name.
    :param trees: the checkouts.
    :param pyprojects: each tree's parsed `pyproject.toml`.
    :returns: the directory relative to the checkout, or None where the
        tree installs no importable package.
    :raises LookupError: where more than one directory answers, the
        bullet naming one.
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
        root = settings.get("module-root", "src")
        return Path(root) / name if root else Path(name)
    found = sorted(
        {
            Path(path).parent
            for path in tracked(trees[repository], "*__init__.py")
            if Path(path).parent.parent == Path() and Path(path).parent != Path("tests")
        }
    )
    if len(found) > 1:
        msg = f"{repository} has {found} and section 2 names one; " + by_hand(
            repository, "git ls-files '*__init__.py'"
        )
        raise LookupError(msg)
    return found[0] if found else None


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
