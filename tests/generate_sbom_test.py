# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for the bill-of-materials writer of `.github/scripts`.

The script reads the metadata of a wheel or of an sdist and the bytes of
the distribution files, and, from the tree it is run in, the gitlinks of
its submodules and `.github/vex.toml`. No clock, no network: the archives
here are synthetic and carry the metadata each test is about, and the
file a test describes only needs to have content, its digest being what
is read.

Two properties are worth more than the field-by-field assertions, and are
what the release pipeline depends on. The document validates against the
CycloneDX 1.6 JSON schema, checked once against the published schema and
its two `$ref` files -- not asserted here, that would need the schema
vendored and a validator installed for one test. The one rule of it a
test does assert is that the references are distinct, a dependency
declared across several marker-separated lines being the shape that
reaches it: that assertion is a comparison over the document the script
already returns, where the rest of the schema is not. And it is
reproducible:
`test_the_document_is_the_same_bytes_twice` is the one that fails if a
clock or a `uuid4` ever reaches it, which would leave a rebuilt release
differing from the published one in the one field nobody could check.

`git` is stubbed where a test needs the one line `git ls-tree` prints for
a gitlink, and run for real where it needs a repository.

The script is loaded by path, `.github/scripts` being no package.
"""

from __future__ import annotations

import gzip
import importlib.util
import io
import json
import runpy
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, NamedTuple

import pytest

if TYPE_CHECKING:
    from types import ModuleType

_SCRIPT = Path(__file__).parents[1] / ".github" / "scripts" / "generate_sbom.py"

# resolved once, for the reason generate_sbom.py's own `_GIT` is: a bare
# "git" in a subprocess list is a partial executable path
_GIT = shutil.which("git") or "git"

# an instant in August 2026, as SOURCE_DATE_EPOCH carries one: seconds
_EPOCH = 1786407122
_SHA256_HEX = 64
# the exit status of a command line argparse refuses
_USAGE = 2
_PINNED = "6e2c8bc4ecdc6e71dbe7a368f360d8d453ce435d"
_ZKP_PINNED = "8f9ab5f2b2d4e036b299932dda151cb6dd75e60e"
_GITMODULES = """[submodule "secp256k1"]
\tpath = secp256k1
\turl = https://github.com/bitcoin-core/secp256k1.git
[submodule "secp256k1-zkp"]
\tpath = secp256k1-zkp
\turl = https://github.com/fametrano/secp256k1-zkp.git
"""
_METADATA = """Metadata-Version: 2.4
Name: example-dist
Version: 2026.9
Summary: An example distribution
License-Expression: MIT
Project-URL: homepage, https://example-dist.readthedocs.io/
Requires-Python: >=3.10
"""


_MEMBERS = ("example_dist-2026.9.dist-info/METADATA",)


@pytest.fixture
def script() -> ModuleType:
    """Return the script, imported by path."""
    spec = importlib.util.spec_from_file_location("generate_sbom", _SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_dist(
    directory: Path,
    *,
    requirements: tuple[str, ...] = (),
    metadata: str = _METADATA,
    members: tuple[str, ...] = _MEMBERS,
    version: str = "2026.9",
) -> tuple[Path, Path]:
    """Write a wheel carrying this metadata, and an sdist beside it.

    Named with the underscore PEP 427 gives a dash in the distribution
    name, which is what `uv build` writes.
    """
    text = metadata + "".join(f"Requires-Dist: {r}\n" for r in requirements)
    wheel = directory / f"example_dist-{version}-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        for member in members:
            archive.writestr(member, text)
    sdist = directory / f"example_dist-{version}.tar.gz"
    sdist.write_bytes(b"an sdist, read for its digest alone")
    return wheel, sdist


def sbom(
    script: ModuleType,
    directory: Path,
    *,
    requirements: tuple[str, ...] = (),
    metadata: str = _METADATA,
    members: tuple[str, ...] = _MEMBERS,
) -> dict[str, Any]:
    """Return the document for a dist directory written on the spot.

    `directory` doubles as the repository root the submodule scan reads:
    a fresh `tmp_path` carries no `.gitmodules` unless a test writes one
    with `make_submodule_repo` first, which is the no-op every other test
    here relies on without saying so.
    """
    wheel, sdist = write_dist(
        directory, requirements=requirements, metadata=metadata, members=members
    )
    document: dict[str, Any] = script.build_sbom(sdist, _EPOCH, directory, wheel)
    return document


def write_sdist(
    directory: Path,
    *,
    metadata: str = _METADATA,
    stem: str = "example_dist-2026.9",
    member: str | None = "PKG-INFO",
    as_directory: bool = False,
) -> Path:
    """Write an sdist carrying this PKG-INFO, and return it.

    `stem` is the top-level directory inside the archive, whose depth is
    what tells the distribution's own PKG-INFO from a vendored one.
    `member` is the name to give it, `None` leaving the archive with none,
    and `as_directory` makes it a directory, which `extractfile` answers
    `None` for.
    """
    path = directory / "example_dist-2026.9.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        if member is not None:
            info = tarfile.TarInfo(f"{stem}/{member}")
            content = metadata.encode()
            if as_directory:
                info.type = tarfile.DIRTYPE
                archive.addfile(info)
            else:
                info.size = len(content)
                archive.addfile(info, io.BytesIO(content))
    return path


def sdist_sbom(script: ModuleType, directory: Path, metadata: str) -> dict[str, Any]:
    """Return the document for an sdist alone, written in `directory`."""
    document: dict[str, Any] = script.build_sbom(
        write_sdist(directory, metadata=metadata), _EPOCH, directory
    )
    return document


class _Call(NamedTuple):
    """One call of the stubbed `git`."""

    args: list[str]
    cwd: Path | None


def stub_git(monkeypatch: pytest.MonkeyPatch, answers: dict[str, str]) -> list[_Call]:
    """Answer `git ls-tree` from a mapping of path to stdout.

    Returns the arguments and working directory of every call, in order.
    """
    calls: list[_Call] = []

    class _Result:
        def __init__(self, stdout: str) -> None:
            self.stdout = stdout

    def fake_run(
        args: list[str], cwd: Path | None = None, **_options: object
    ) -> _Result:
        calls.append(_Call(args, cwd))
        return _Result(answers[args[-1]])

    monkeypatch.setattr(subprocess, "run", fake_run)
    return calls


def make_submodule_repo(
    root: Path,
    *,
    url: str = "https://github.com/bitcoin-core/secp256k1.git",
    sha: str = "6e2c8bc4ecdc6e71dbe7a368f360d8d453ce435d",
    path: str = "secp256k1",
    commit_gitlink: bool = True,
) -> Path:
    """Turn `root` into a git repository declaring one submodule.

    `.gitmodules` and the gitlink are independent facts in git's own
    model -- the file can be edited without the tree changing what it
    pins -- so both are written by hand rather than through `git
    submodule add`, which would need to reach the url it clones.
    """
    subprocess.run([_GIT, "init", "-q"], cwd=root, check=True)
    (root / ".gitmodules").write_text(
        f'[submodule "{path}"]\n\tpath = {path}\n\turl = {url}\n', encoding="utf-8"
    )
    subprocess.run([_GIT, "add", ".gitmodules"], cwd=root, check=True)
    if commit_gitlink:
        subprocess.run(
            [_GIT, "update-index", "--add", "--cacheinfo", f"160000,{sha},{path}"],
            cwd=root,
            check=True,
        )
    subprocess.run(
        [
            _GIT,
            "-c",
            "user.email=test@example.org",
            "-c",
            "user.name=test",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "-m",
            "vendor a submodule",
        ],
        cwd=root,
        check=True,
    )
    return root


def test_the_document_describes_the_distribution(
    script: ModuleType, tmp_path: Path
) -> None:
    """The root component is at the version the wheel declares."""
    document = sbom(script, tmp_path)

    assert document["bomFormat"] == "CycloneDX"
    assert document["specVersion"] == "1.6"
    assert document["metadata"]["timestamp"] == "2026-08-11T00:12:02Z"
    component = document["metadata"]["component"]
    assert component["name"] == "example-dist"
    assert component["version"] == "2026.9"
    assert component["purl"] == "pkg:pypi/example-dist@2026.9"
    assert component["licenses"] == [{"expression": "MIT"}]
    assert component["description"] == "An example distribution"
    assert component["properties"] == [
        {"name": "btclib:requires-python", "value": ">=3.10"}
    ]
    # no component-level hash, the component being two files
    assert "hashes" not in component


def test_the_two_files_are_named_with_their_digests(
    script: ModuleType, tmp_path: Path
) -> None:
    """One externalReference per distribution file, carrying its SHA-256."""
    document = sbom(script, tmp_path)

    references = document["metadata"]["component"]["externalReferences"]
    distributions = [
        r for r in references if r["url"].startswith("example_dist-2026.9")
    ]
    assert [r["url"] for r in distributions] == [
        "example_dist-2026.9-py3-none-any.whl",
        "example_dist-2026.9.tar.gz",
    ]
    for reference in distributions:
        (digest,) = reference["hashes"]
        assert digest["alg"] == "SHA-256"
        assert len(digest["content"]) == _SHA256_HEX


def test_a_project_url_becomes_a_reference_of_its_kind(
    script: ModuleType, tmp_path: Path
) -> None:
    """The labels of `[project.urls]` map onto CycloneDX's own vocabulary."""
    metadata = _METADATA + "Project-URL: repository, https://github.com/o/r\n"
    document = sbom(script, tmp_path, metadata=metadata)

    references = document["metadata"]["component"]["externalReferences"]
    assert {
        "type": "website",
        "url": "https://example-dist.readthedocs.io/",
        "comment": "homepage",
    } in references
    assert {
        "type": "vcs",
        "url": "https://github.com/o/r",
        "comment": "repository",
    } in references


def test_a_label_with_no_mapping_is_recorded_as_other(
    script: ModuleType, tmp_path: Path
) -> None:
    """A url is never dropped for want of a word for what it is."""
    metadata = _METADATA + "Project-URL: pull_requests, https://example.org/pulls\n"
    document = sbom(script, tmp_path, metadata=metadata)

    references = document["metadata"]["component"]["externalReferences"]
    assert {
        "type": "other",
        "url": "https://example.org/pulls",
        "comment": "pull_requests",
    } in references


def test_a_pinned_requirement_carries_its_version(
    script: ModuleType, tmp_path: Path
) -> None:
    """`==` is the one specifier that names a version rather than a range."""
    document = sbom(script, tmp_path, requirements=("btclib_secp256k1==0.8.0",))

    (component,) = document["components"]
    assert component["name"] == "btclib-secp256k1"
    assert component["version"] == "0.8.0"
    assert component["purl"] == "pkg:pypi/btclib-secp256k1@0.8.0"
    assert component["scope"] == "required"
    assert component["properties"] == [
        {"name": "btclib:requires-dist", "value": "btclib_secp256k1==0.8.0"}
    ]


def test_a_floor_carries_no_version(script: ModuleType, tmp_path: Path) -> None:
    """A range is not a version, and what the wheel declares is a range.

    Which is the shape every release carries: RELEASING.md replaces each
    direct reference with a `>=` floor before the tag, and what an
    installer then resolves is not a fact about these files.
    """
    document = sbom(script, tmp_path, requirements=("btclib_secp256k1>=0.8.0",))

    (component,) = document["components"]
    assert "version" not in component
    assert component["purl"] == "pkg:pypi/btclib-secp256k1"
    assert component["properties"] == [
        {"name": "btclib:requires-dist", "value": "btclib_secp256k1>=0.8.0"}
    ]


def test_a_direct_reference_carries_its_vcs_url(
    script: ModuleType, tmp_path: Path
) -> None:
    """Between releases each sibling is a `git+https://...@main` reference."""
    url = "git+https://github.com/btclib-org/btclib-secp256k1.git@main"
    document = sbom(script, tmp_path, requirements=(f"btclib_secp256k1 @ {url}",))

    (component,) = document["components"]
    assert component["externalReferences"] == [{"type": "vcs", "url": url}]
    # percent-encoded, the `+` and the `@` of the url being the two
    # characters that would otherwise end a purl qualifier
    assert component["purl"] == (
        "pkg:pypi/btclib-secp256k1?vcs_url=git%2Bhttps%3A%2F%2Fgithub.com"
        "%2Fbtclib-org%2Fbtclib-secp256k1.git%40main"
    )


def test_an_extra_makes_a_requirement_optional(
    script: ModuleType, tmp_path: Path
) -> None:
    """A dependency the wheel asks for only when an extra is asked for."""
    requirement = 'coverage>=7; extra == "test"'
    document = sbom(script, tmp_path, requirements=(requirement,))

    (component,) = document["components"]
    assert component["scope"] == "optional"


def test_a_marker_that_is_not_an_extra_leaves_it_required(
    script: ModuleType, tmp_path: Path
) -> None:
    """An interpreter version says where a dependency installs, not whether."""
    document = sbom(script, tmp_path, requirements=('tomli; python_version < "3.11"',))

    (component,) = document["components"]
    assert component["scope"] == "required"


def test_the_extras_of_a_requirement_are_recorded(
    script: ModuleType, tmp_path: Path
) -> None:
    """A name with extras keeps them, the purl having no field for them."""
    document = sbom(script, tmp_path, requirements=("requests[socks]>=2",))

    (component,) = document["components"]
    assert {"name": "btclib:extras", "value": "socks"} in component["properties"]


def test_a_dependency_split_by_marker_is_one_component(
    script: ModuleType, tmp_path: Path
) -> None:
    """One component per dependency, whatever it takes to declare it.

    Widening a floor across interpreter versions is several
    `Requires-Dist` lines differing only by marker, and each of them
    reads as the same package url.
    """
    requirements = (
        'cffi>=1.17; python_version >= "3.13"',
        'cffi>=1.16; python_version == "3.12"',
        'cffi>=1.15; python_version < "3.12"',
    )
    document = sbom(script, tmp_path, requirements=requirements)

    (component,) = document["components"]
    assert component["name"] == "cffi"
    assert component["purl"] == "pkg:pypi/cffi"
    # every line kept, in the order the metadata declares them: the
    # component is a reading of them all and checkable against them
    assert component["properties"] == [
        {"name": "btclib:requires-dist", "value": requirement}
        for requirement in requirements
    ]


def test_a_submodule_pinned_to_a_commit_is_a_component(
    script: ModuleType, tmp_path: Path
) -> None:
    """A vendored submodule is a component `Requires-Dist` never carries."""
    make_submodule_repo(tmp_path)
    document = sbom(script, tmp_path)

    (component,) = document["components"]
    sha = "6e2c8bc4ecdc6e71dbe7a368f360d8d453ce435d"
    assert component["type"] == "library"
    assert component["name"] == "secp256k1"
    assert component["purl"] == f"pkg:github/bitcoin-core/secp256k1@{sha}"
    assert component["bom-ref"] == component["purl"]
    assert component["version"] == sha
    assert component["scope"] == "required"
    assert component["externalReferences"] == [
        {"type": "vcs", "url": "https://github.com/bitcoin-core/secp256k1.git"}
    ]
    assert component["properties"] == [
        {"name": "btclib:submodule-path", "value": "secp256k1"}
    ]


def test_a_submodule_ssh_url_is_read_too(script: ModuleType, tmp_path: Path) -> None:
    """The form `git submodule add` writes for a private remote."""
    make_submodule_repo(tmp_path, url="git@github.com:bitcoin-core/secp256k1.git")
    document = sbom(script, tmp_path)

    (component,) = document["components"]
    assert component["name"] == "secp256k1"
    assert component["purl"].startswith("pkg:github/bitcoin-core/secp256k1@")


def test_a_submodule_url_that_is_not_github_stops_it(
    script: ModuleType, tmp_path: Path
) -> None:
    """Refused rather than guessed at, an unreadable url's own rule."""
    make_submodule_repo(tmp_path, url="https://gitlab.com/o/r.git")

    with pytest.raises(SystemExit, match="cannot read the submodule url"):
        sbom(script, tmp_path)


def test_a_submodule_without_a_gitlink_stops_it(
    script: ModuleType, tmp_path: Path
) -> None:
    """A path `.gitmodules` names but the tree does not pin is not skipped."""
    make_submodule_repo(tmp_path, commit_gitlink=False)

    with pytest.raises(SystemExit, match="is not a pinned submodule"):
        sbom(script, tmp_path)


def test_a_tree_declaring_no_submodule_contributes_no_component(
    script: ModuleType, tmp_path: Path
) -> None:
    """The scan is a no-op where there is no `.gitmodules` to read."""
    assert script.submodule_components(tmp_path) == []


def test_a_submodule_component_sorts_beside_requires_dist_components(
    script: ModuleType, tmp_path: Path
) -> None:
    """One `components` list, sorted by `bom-ref` across both sources."""
    make_submodule_repo(tmp_path)
    document = sbom(script, tmp_path, requirements=("btclib_secp256k1>=0.8.0",))

    refs = [c["bom-ref"] for c in document["components"]]
    assert refs == sorted(refs)
    names = {c["name"] for c in document["components"]}
    assert names == {"secp256k1", "btclib-secp256k1"}


def test_the_dependency_graph_names_a_submodule_component(
    script: ModuleType, tmp_path: Path
) -> None:
    """A submodule component is a dependency the root depends on too."""
    make_submodule_repo(tmp_path)
    document = sbom(script, tmp_path)

    (component,) = document["components"]
    root, *leaves = document["dependencies"]
    assert component["bom-ref"] in root["dependsOn"]
    assert leaves == [{"ref": component["bom-ref"], "dependsOn": []}]


def test_the_references_of_a_document_are_distinct(
    script: ModuleType, tmp_path: Path
) -> None:
    """`bom-ref` identifies a component, so CycloneDX 1.6 asks it be unique.

    Nothing here runs the schema, and a dependency split by marker is the
    shape that reaches this rule of it -- in the graph as well as in the
    components, `dependencies` being keyed by the same reference.
    """
    document = sbom(
        script,
        tmp_path,
        requirements=(
            'cffi>=1.17; python_version >= "3.13"',
            'cffi>=1.15; python_version < "3.13"',
            "btclib_secp256k1>=0.8.0",
        ),
    )

    references = [document["metadata"]["component"]["bom-ref"]]
    references += [c["bom-ref"] for c in document["components"]]
    assert len(set(references)) == len(references)
    root, *leaves = document["dependencies"]
    graph = [root["ref"], *(leaf["ref"] for leaf in leaves)]
    assert len(set(graph)) == len(graph)
    assert len(set(root["dependsOn"])) == len(root["dependsOn"])


def test_a_version_the_lines_disagree_about_is_left_out(
    script: ModuleType, tmp_path: Path
) -> None:
    """A pin under a marker names a version for one environment.

    Which is not what the wheel pins, so the document names none.
    """
    document = sbom(
        script,
        tmp_path,
        requirements=(
            'tomli==2.0.1; python_version < "3.11"',
            'tomli==2.2.1; python_version >= "3.11"',
        ),
    )

    (component,) = document["components"]
    assert "version" not in component
    assert component["purl"] == "pkg:pypi/tomli"


def test_a_version_the_lines_agree_on_is_kept(
    script: ModuleType, tmp_path: Path
) -> None:
    """Lines that pin the same version pin it for the distribution."""
    document = sbom(
        script,
        tmp_path,
        requirements=(
            'tomli==2.2.1; python_version < "3.11"',
            'tomli==2.2.1; python_version >= "3.11"',
        ),
    )

    (component,) = document["components"]
    assert component["version"] == "2.2.1"
    assert component["purl"] == "pkg:pypi/tomli@2.2.1"


def test_a_line_outside_an_extra_makes_the_dependency_required(
    script: ModuleType, tmp_path: Path
) -> None:
    """Optional only where every line naming it is under an extra."""
    document = sbom(
        script,
        tmp_path,
        requirements=('coverage>=7; extra == "test"', 'coverage>=7; os_name == "nt"'),
    )

    (component,) = document["components"]
    assert component["scope"] == "required"


def test_the_dependency_graph_names_every_component(
    script: ModuleType, tmp_path: Path
) -> None:
    """The root depends on each, and each on nothing: one level, declared."""
    document = sbom(
        script,
        tmp_path,
        requirements=("requests==1.0", "btclib_secp256k1==2.0"),
    )

    refs = [component["bom-ref"] for component in document["components"]]
    root, *leaves = document["dependencies"]
    assert root == {"ref": "pkg:pypi/example-dist@2026.9", "dependsOn": refs}
    assert leaves == [{"ref": ref, "dependsOn": []} for ref in refs]


def test_the_components_are_sorted(script: ModuleType, tmp_path: Path) -> None:
    """Sorted by reference, so the metadata's own order cannot move them."""
    document = sbom(
        script, tmp_path, requirements=("zope.interface==7.0", "attrs==25.0")
    )

    assert [c["name"] for c in document["components"]] == ["attrs", "zope-interface"]


def test_a_requirement_the_script_cannot_read_stops_it(
    script: ModuleType, tmp_path: Path
) -> None:
    """Refused rather than guessed at.

    A dependency the document omits in silence is the one failure a bill of
    materials must not have.
    """
    with pytest.raises(SystemExit, match="cannot read the requirement"):
        sbom(script, tmp_path, requirements=("== 1.0",))


@pytest.mark.parametrize(
    ("members", "expected"),
    [
        ((), "carries 0 dist-info/METADATA members"),
        (
            ("a-1.dist-info/METADATA", "b-2.dist-info/METADATA"),
            "carries 2 dist-info/METADATA members",
        ),
    ],
)
def test_a_wheel_without_exactly_one_metadata_stops_it(
    script: ModuleType, tmp_path: Path, members: tuple[str, ...], expected: str
) -> None:
    """One wheel is one distribution, and its metadata is one member."""
    with pytest.raises(SystemExit, match=expected):
        sbom(script, tmp_path, members=members)


def test_metadata_with_no_name_stops_it(script: ModuleType, tmp_path: Path) -> None:
    """A wheel whose metadata is missing the two fields that identify it."""
    with pytest.raises(SystemExit, match="declares no Name or no Version"):
        sbom(script, tmp_path, metadata="Metadata-Version: 2.4\n")


def test_metadata_with_no_summary_or_licence_omits_them(
    script: ModuleType, tmp_path: Path
) -> None:
    """Every optional field is optional, rather than reported as empty."""
    metadata = "Metadata-Version: 2.4\nName: example-dist\nVersion: 2026.9\n"
    document = sbom(script, tmp_path, metadata=metadata)

    component = document["metadata"]["component"]
    assert "description" not in component
    assert "licenses" not in component
    assert "properties" not in component


def write_vex(root: Path, *entries: str) -> None:
    """Write the tree's not-affected list from these table bodies."""
    (root / ".github").mkdir(exist_ok=True)
    text = "".join(f"[[not_affected]]\n{entry}\n" for entry in entries)
    (root / ".github" / "vex.toml").write_text(text, encoding="utf-8")


_FINDING = """id = "GHSA-xxxx-xxxx-xxxx"
source = "GitHub Advisories"
component = "Some_Dep"
justification = "code_not_reachable"
detail = "The vulnerable parser is never called."
"""


def test_main_says_how_to_be_called_when_it_is_not(
    script: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    """Two directories, no more and no fewer."""
    with pytest.raises(SystemExit) as excinfo:
        script.main(["prog", "dist"])

    assert excinfo.value.code == _USAGE
    assert "usage: prog [-h] [--sdist-only]" in capsys.readouterr().err


def test_main_refuses_to_run_without_source_date_epoch(
    script: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No default of "now", for normalize_sdist.py's reason.

    A default makes the document differ from the released one, and whoever
    found that out is the one person who could not fix it.
    """
    monkeypatch.delenv("SOURCE_DATE_EPOCH", raising=False)

    assert script.main(["prog", str(tmp_path), str(tmp_path)]) == 1
    assert "SOURCE_DATE_EPOCH is not set" in capsys.readouterr().err


@pytest.mark.parametrize("pattern", ["*.whl", "*.tar.gz"])
def test_main_refuses_a_dist_directory_that_is_not_one_pair(
    script: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    pattern: str,
) -> None:
    """A stale artifact beside the fresh one is not silently skipped over."""
    monkeypatch.setenv("SOURCE_DATE_EPOCH", str(_EPOCH))
    write_dist(tmp_path)
    write_dist(tmp_path, version="2026.8")
    (
        tmp_path
        / (
            "example_dist-2026.8"
            f"{'.tar.gz' if pattern == '*.whl' else '-py3-none-any.whl'}"
        )
    ).unlink()

    with pytest.raises(SystemExit, match=f"expected one {pattern.replace('*', '.')}"):
        script.main(["prog", str(tmp_path), str(tmp_path / "sbom")])


def test_main_refuses_a_dist_directory_holding_no_wheel(
    script: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing wheel is an error and not a quiet sdist-only document.

    Which document is written is the caller's to say with `--sdist-only`.
    """
    monkeypatch.setenv("SOURCE_DATE_EPOCH", str(_EPOCH))
    monkeypatch.chdir(tmp_path)
    write_sdist(tmp_path)

    with pytest.raises(SystemExit, match=r"expected one \*\.whl, found none"):
        script.main(["prog", str(tmp_path), str(tmp_path / "sbom")])


def test_main_names_the_file_after_the_sdist(
    script: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The caller passes a directory and needs to know no version.

    Which in a rehearsal it does not: the build patches a
    `.dev<run*100+attempt>` into the version before building, so the name
    the workflow would have to construct is not the one in pyproject.toml.
    """
    monkeypatch.setenv("SOURCE_DATE_EPOCH", str(_EPOCH))
    monkeypatch.chdir(tmp_path)
    wheel, _ = write_dist(tmp_path, version="2026.9.dev7")
    # a stem of its own, so that a name taken from the wheel is a failure
    wheel.rename(tmp_path / "example_dist-0-py3-none-any.whl")
    output = tmp_path / "sbom"

    assert script.main(["prog", str(tmp_path), str(output)]) == 0

    written = output / "example_dist-2026.9.dev7.cdx.json"
    assert f"wrote {written}" in capsys.readouterr().out
    text = written.read_text(encoding="utf-8")
    assert json.loads(text)["specVersion"] == "1.6"
    assert text.endswith("}\n")


def test_the_document_is_the_same_bytes_twice(
    script: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The reproducibility the release assets and their attestation want.

    Everything here is derived: the timestamp from `SOURCE_DATE_EPOCH`,
    the serial number from the purl and the digests. A clock or a `uuid4`
    reaching either is what this fails on.
    """
    monkeypatch.setenv("SOURCE_DATE_EPOCH", str(_EPOCH))
    monkeypatch.chdir(tmp_path)
    write_dist(tmp_path, requirements=("btclib_secp256k1>=0.8.0",))

    first, second = (tmp_path / "one", tmp_path / "two")
    assert script.main(["prog", str(tmp_path), str(first)]) == 0
    assert script.main(["prog", str(tmp_path), str(second)]) == 0

    name = "example_dist-2026.9.cdx.json"
    assert (first / name).read_bytes() == (second / name).read_bytes()


def test_the_tree_is_the_working_directory(
    script: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The script may be fetched from anywhere: the tree is where it runs.

    `_SCRIPT` sits in a tree of its own, so a document carrying the
    findings of `tmp_path` could not have read them from there.
    """
    monkeypatch.setenv("SOURCE_DATE_EPOCH", str(_EPOCH))
    tree, dist = tmp_path / "tree", tmp_path / "dist"
    tree.mkdir()
    dist.mkdir()
    write_dist(dist, requirements=("some-dep>=1",))
    write_vex(tree, _FINDING)
    monkeypatch.chdir(tree)

    assert script.main(["prog", str(dist), str(tmp_path / "sbom")]) == 0

    text = (tmp_path / "sbom" / "example_dist-2026.9.cdx.json").read_text(
        encoding="utf-8"
    )
    assert json.loads(text)["vulnerabilities"][0]["id"] == "GHSA-xxxx-xxxx-xxxx"


def test_the_main_guard_runs_the_script_as___main__(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Run `if __name__ == "__main__":` without a subprocess.

    `runpy.run_path` executes the file fresh with `__name__` set to
    `"__main__"` in this interpreter.
    """
    monkeypatch.setenv("SOURCE_DATE_EPOCH", str(_EPOCH))
    monkeypatch.chdir(tmp_path)
    write_dist(tmp_path)
    monkeypatch.setattr(sys, "argv", ["prog", str(tmp_path), str(tmp_path / "sbom")])

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(_SCRIPT), run_name="__main__")

    assert excinfo.value.code == 0


def test_the_sdist_alone_is_described_from_its_own_metadata(
    script: ModuleType, tmp_path: Path
) -> None:
    """One file, one digest, and the PKG-INFO the archive carries."""
    sdist = write_sdist(tmp_path)

    document = script.build_sbom(sdist, _EPOCH, tmp_path)

    root = document["metadata"]["component"]
    assert root["purl"] == "pkg:pypi/example-dist@2026.9"
    assert root["licenses"] == [{"expression": "MIT"}]
    assert root["description"] == "An example distribution"
    (archive, *urls) = root["externalReferences"]
    assert archive == {
        "type": "distribution",
        "url": sdist.name,
        "hashes": [{"alg": "SHA-256", "content": script.file_hash(sdist)}],
    }
    assert [entry["comment"] for entry in urls] == ["homepage"]
    assert document["metadata"]["timestamp"] == "2026-08-11T00:12:02Z"


def test_main_with_sdist_only_describes_the_sdist_beside_a_wheel(
    script: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A wheel in the directory is left out of a document that says so."""
    monkeypatch.setenv("SOURCE_DATE_EPOCH", str(_EPOCH))
    monkeypatch.chdir(tmp_path)
    write_dist(tmp_path)
    sdist = write_sdist(tmp_path)
    output = tmp_path / "sbom"

    assert script.main(["prog", "--sdist-only", str(tmp_path), str(output)]) == 0

    document = json.loads(
        (output / "example_dist-2026.9.cdx.json").read_text(encoding="utf-8")
    )
    root = document["metadata"]["component"]
    distributions = [
        entry["url"]
        for entry in root["externalReferences"]
        if entry["type"] == "distribution"
    ]
    assert distributions == [sdist.name]
    assert document == script.build_sbom(sdist, _EPOCH, tmp_path)


def test_the_serial_number_is_the_digests_and_not_the_clock(
    script: ModuleType, tmp_path: Path
) -> None:
    """A rebuild of a tag writes this file too, which is what signs it."""
    sdist = write_sdist(tmp_path)

    first = script.build_sbom(sdist, _EPOCH, tmp_path)
    later = script.build_sbom(sdist, _EPOCH + 86_400, tmp_path)

    assert first["serialNumber"] == later["serialNumber"]
    assert first["metadata"]["timestamp"] != later["metadata"]["timestamp"]

    # the same archive rewritten: one byte of content, and the serial
    # number is another document
    with gzip.open(sdist, "ab") as appended:
        appended.write(b"\n")
    assert (
        script.build_sbom(sdist, _EPOCH, tmp_path)["serialNumber"]
        != (first["serialNumber"])
    )


def test_the_wheel_is_part_of_the_serial_number(
    script: ModuleType, tmp_path: Path
) -> None:
    """A document naming two files is not the document naming one."""
    wheel, _ = write_dist(tmp_path)
    sdist = write_sdist(tmp_path)

    both = script.build_sbom(sdist, _EPOCH, tmp_path, wheel)
    alone = script.build_sbom(sdist, _EPOCH, tmp_path)

    assert both["serialNumber"] != alone["serialNumber"]


def test_an_sdist_with_no_pkg_info_stops_it(script: ModuleType, tmp_path: Path) -> None:
    """Reading the metadata out of the archive is what makes it describable."""
    sdist = write_sdist(tmp_path, member=None)

    with pytest.raises(SystemExit, match="carries 0 PKG-INFO members"):
        script.sdist_metadata(sdist)


def test_a_vendored_pkg_info_is_not_the_distributions(
    script: ModuleType, tmp_path: Path
) -> None:
    """Depth is what tells them apart, a vendored tree carrying its own."""
    path = tmp_path / "example_dist-2026.9.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        for name in ("pkg/PKG-INFO", "pkg/vendored/PKG-INFO"):
            content = _METADATA.encode()
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))

    assert script.sdist_metadata(path)["Name"] == "example-dist"


def test_a_pkg_info_that_is_not_a_file_stops_it(
    script: ModuleType, tmp_path: Path
) -> None:
    """A member of that name with nothing to read is named, not skipped."""
    sdist = write_sdist(tmp_path, as_directory=True)

    with pytest.raises(SystemExit, match="is not a regular file"):
        script.sdist_metadata(sdist)


def test_an_sdist_declaring_no_version_stops_it(
    script: ModuleType, tmp_path: Path
) -> None:
    """A document with no version is worse than no document."""
    with pytest.raises(SystemExit, match="declares no Name or no Version"):
        sdist_sbom(script, tmp_path, "Metadata-Version: 2.5\nName: x\n")


def test_every_submodule_is_a_component_at_the_commit_it_is_pinned_to(
    script: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The pin `Requires-Dist` cannot state is what the gitlink states."""
    calls = stub_git(
        monkeypatch,
        {
            "secp256k1": f"160000 commit {_PINNED}\tsecp256k1\n",
            "secp256k1-zkp": f"160000 commit {_ZKP_PINNED}\tsecp256k1-zkp\n",
        },
    )
    (tmp_path / ".gitmodules").write_text(_GITMODULES, encoding="utf-8")

    components = script.submodule_components(tmp_path)

    assert [entry["purl"] for entry in components] == [
        f"pkg:github/bitcoin-core/secp256k1@{_PINNED}",
        f"pkg:github/fametrano/secp256k1-zkp@{_ZKP_PINNED}",
    ]
    assert components[1]["properties"] == [
        {"name": "btclib:submodule-path", "value": "secp256k1-zkp"}
    ]
    assert [call.args[1:] for call in calls] == [
        ["ls-tree", "HEAD", "--", "secp256k1"],
        ["ls-tree", "HEAD", "--", "secp256k1-zkp"],
    ]
    assert {call.cwd for call in calls} == {tmp_path}


def test_the_pin_is_read_from_the_tree_and_not_from_a_checkout(
    script: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`git ls-tree HEAD` answers for a submodule nobody initialized."""
    stub_git(monkeypatch, {"secp256k1": f"160000 commit {_PINNED}\tsecp256k1\n"})
    (tmp_path / ".gitmodules").write_text(
        '[submodule "secp256k1"]\n'
        "\tpath = secp256k1\n"
        "\turl = git@github.com:bitcoin-core/secp256k1\n",
        encoding="utf-8",
    )

    (component,) = script.submodule_components(tmp_path)

    assert component["version"] == _PINNED
    assert not (tmp_path / "secp256k1").exists()


_WHEEL_METADATA = _METADATA + "Requires-Dist: cffi>=1.6\n"
_BOTH_PINNED = {
    "secp256k1": f"160000 commit {_PINNED}\tsecp256k1\n",
    "secp256k1-zkp": f"160000 commit {_ZKP_PINNED}\tsecp256k1-zkp\n",
}


def test_a_wheel_names_the_libraries_its_build_compiled_and_no_other(
    script: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unflagged build compiles `secp256k1` alone, and says so."""
    stub_git(monkeypatch, _BOTH_PINNED)
    (tmp_path / ".gitmodules").write_text(_GITMODULES, encoding="utf-8")
    metadata = script.message_from_string(_WHEEL_METADATA)

    document = script.build_wheel_sbom(metadata, tmp_path, ["secp256k1"], "static")

    refs = [f"pkg:github/bitcoin-core/secp256k1@{_PINNED}", "pkg:pypi/cffi"]
    assert [entry["bom-ref"] for entry in document["components"]] == refs
    root = document["metadata"]["component"]
    assert root["purl"] == "pkg:pypi/example-dist@2026.9"
    assert root["properties"] == [
        {"name": "btclib:requires-python", "value": ">=3.10"},
        {"name": "btclib:linkage", "value": "static"},
    ]
    assert document["dependencies"][0]["dependsOn"] == refs

    flagged = script.build_wheel_sbom(
        metadata, tmp_path, ["secp256k1", "secp256k1-zkp"], "static"
    )
    assert f"pkg:github/fametrano/secp256k1-zkp@{_ZKP_PINNED}" in [
        entry["bom-ref"] for entry in flagged["components"]
    ]
    assert flagged["serialNumber"] != document["serialNumber"]


def test_a_wheel_document_has_no_clock_and_no_digest_of_its_archive(
    script: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """What differs between two builds of one commit is not in it."""
    stub_git(monkeypatch, _BOTH_PINNED)
    (tmp_path / ".gitmodules").write_text(_GITMODULES, encoding="utf-8")
    write_vex(tmp_path, _FINDING.replace("Some_Dep", "secp256k1-zkp"))
    metadata = script.message_from_string(_WHEEL_METADATA)

    static = script.build_wheel_sbom(metadata, tmp_path, ["secp256k1"], "static")
    dynamic = script.build_wheel_sbom(metadata, tmp_path, ["secp256k1"], "dynamic")

    assert "timestamp" not in static["metadata"]
    # the findings name a library this wheel did not compile, which is why
    # they are not carried, and why reading them would stop the build
    assert "vulnerabilities" not in static
    assert static == script.build_wheel_sbom(
        metadata, tmp_path, ["secp256k1"], "static"
    )
    assert static["serialNumber"] != dynamic["serialNumber"]


def test_a_compiled_path_no_gitmodules_entry_declares_is_refused(
    script: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A library the document cannot pin is one it would omit in silence."""
    stub_git(monkeypatch, _BOTH_PINNED)
    (tmp_path / ".gitmodules").write_text(_GITMODULES, encoding="utf-8")

    with pytest.raises(SystemExit, match=r"\['vendored'\] compiled"):
        script.build_wheel_sbom(
            script.message_from_string(_WHEEL_METADATA),
            tmp_path,
            ["secp256k1", "vendored"],
            "static",
        )


def test_a_wheel_metadata_declaring_no_version_is_refused(
    script: ModuleType, tmp_path: Path
) -> None:
    """The message names the wheel's metadata rather than an archive."""
    metadata = script.message_from_string("Metadata-Version: 2.5\nName: x\n")

    with pytest.raises(SystemExit, match="the wheel's METADATA declares no Name"):
        script.build_wheel_sbom(metadata, tmp_path, [], "static")


def test_the_wheel_document_is_written_under_the_wheels_own_name(
    script: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The distribution field of a wheel's file name, PEP 427's escaping."""
    stub_git(monkeypatch, _BOTH_PINNED)
    (tmp_path / ".gitmodules").write_text(_GITMODULES, encoding="utf-8")

    output = script.write_wheel_sbom(
        _WHEEL_METADATA, tmp_path, ["secp256k1"], "dynamic", tmp_path / "out"
    )

    assert output == tmp_path / "out" / "example_dist.cdx.json"
    text = output.read_text(encoding="utf-8")
    assert text.endswith("}\n")
    expected = script.build_wheel_sbom(
        script.message_from_string(_WHEEL_METADATA),
        tmp_path,
        ["secp256k1"],
        "dynamic",
    )
    assert json.loads(text) == expected


def test_a_tree_with_no_list_states_no_vulnerabilities(
    script: ModuleType, tmp_path: Path
) -> None:
    """No file leaves the key out, not an empty array."""
    assert "vulnerabilities" not in sbom(script, tmp_path)


def test_a_finding_reaches_the_document_against_its_component(
    script: ModuleType, tmp_path: Path
) -> None:
    """The finding names the dependency by its `bom-ref` and says why."""
    write_vex(tmp_path, _FINDING)
    document = sbom(script, tmp_path, requirements=("some-dep>=1",))

    assert document["vulnerabilities"] == [
        {
            "id": "GHSA-xxxx-xxxx-xxxx",
            "source": {"name": "GitHub Advisories"},
            "affects": [{"ref": "pkg:pypi/some-dep"}],
            "analysis": {
                "state": "not_affected",
                "justification": "code_not_reachable",
                "detail": "The vulnerable parser is never called.",
            },
        }
    ]


def test_a_finding_may_name_the_distribution_itself(
    script: ModuleType, tmp_path: Path
) -> None:
    """The root component is a component too, its own code being a subject."""
    root = sbom(script, tmp_path)["metadata"]["component"]
    write_vex(tmp_path, _FINDING.replace("Some_Dep", root["name"]))
    document = sbom(script, tmp_path)

    (finding,) = document["vulnerabilities"]
    assert finding["affects"] == [{"ref": root["bom-ref"]}]


def test_a_finding_for_a_component_the_document_lacks_is_refused(
    script: ModuleType, tmp_path: Path
) -> None:
    """A finding that answers nothing is an error, not a silent omission."""
    write_vex(tmp_path, _FINDING)
    with pytest.raises(SystemExit, match="some-dep, which this document"):
        sbom(script, tmp_path)


@pytest.mark.parametrize(
    "entry",
    [
        _FINDING.replace("code_not_reachable", "not_reachable"),
        _FINDING.replace('detail = "The vulnerable parser is never called."\n', ""),
        _FINDING + 'severity = "low"\n',
        _FINDING.replace("The vulnerable parser is never called.", ""),
    ],
    ids=["justification", "missing key", "extra key", "empty value"],
)
def test_a_malformed_finding_is_refused(
    script: ModuleType, tmp_path: Path, entry: str
) -> None:
    """A finding is stated whole or not at all."""
    write_vex(tmp_path, entry)
    with pytest.raises(SystemExit):
        sbom(script, tmp_path, requirements=("some-dep>=1",))


def test_a_finding_may_name_a_vendored_submodule(
    script: ModuleType, tmp_path: Path
) -> None:
    """A submodule is a component under its upstream repository's name."""
    make_submodule_repo(tmp_path)
    write_vex(tmp_path, _FINDING.replace("Some_Dep", "secp256k1"))
    document = sbom(script, tmp_path)

    (finding,) = document["vulnerabilities"]
    assert finding["affects"] == [
        {"ref": f"pkg:github/bitcoin-core/secp256k1@{_PINNED}"}
    ]


def test_a_name_the_document_carries_twice_is_refused(
    script: ModuleType, tmp_path: Path
) -> None:
    """A dependency and a submodule of one name make an entry ambiguous."""
    make_submodule_repo(tmp_path)
    write_vex(tmp_path, _FINDING.replace("Some_Dep", "secp256k1"))
    with pytest.raises(SystemExit, match="secp256k1, which the document carries"):
        sbom(script, tmp_path, requirements=("secp256k1>=1",))


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("", "holds no `\\[\\[not_affected\\]\\]` entry"),
        ("not_affected = [1]\n", "must be a list of"),
        ("[not_affected]\nid = 'a'\n", "must be a list of"),
        ("not_affected = [\n", "does not parse"),
    ],
    ids=["empty file", "list of integers", "single table", "unparsable"],
)
def test_a_list_the_rule_does_not_allow_is_refused_cleanly(
    script: ModuleType, tmp_path: Path, text: str, message: str
) -> None:
    """Each shape of a bad file stops the run with a message."""
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "vex.toml").write_text(text, encoding="utf-8")
    with pytest.raises(SystemExit, match=message):
        sbom(script, tmp_path)


def test_a_submodule_named_in_another_spelling_is_still_reached(
    script: ModuleType, tmp_path: Path
) -> None:
    """An entry may name a submodule in its PEP 503 spelling."""
    make_submodule_repo(tmp_path, url="https://github.com/o/Secp_Lib.git")
    write_vex(tmp_path, _FINDING.replace("Some_Dep", "secp-lib"))
    document = sbom(script, tmp_path)

    (finding,) = document["vulnerabilities"]
    assert finding["affects"] == [
        {"ref": "pkg:github/o/Secp_Lib@6e2c8bc4ecdc6e71dbe7a368f360d8d453ce435d"}
    ]
