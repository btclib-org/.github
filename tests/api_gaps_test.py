# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Tests for `.github/scripts/api_gaps.py` and the breaks it reports.

Each case writes two versions of a package `pkg` under `src/` and runs
the script's `main` on them, `griffe.load_git` replaced by a load of the
old directory with the options the script passes it: the walk, the
comparison and the exit code are the script's own, and only the git
worktree is not made. A pair shaped like btclib-org/btclib#2759, a
dataclass field turned into a property, and one shaped like
btclib-org/base58-bech32#26, a function returning one more value, are
asked first, beside griffe's own answer on the same pair.
"""

from __future__ import annotations

import importlib.util
import itertools
import re
import subprocess
import sys
import tomllib
from textwrap import dedent
from typing import TYPE_CHECKING

import griffe
import pytest
import yaml

from . import ROOT

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

_SCRIPT = ROOT / ".github" / "scripts" / "api_gaps.py"
_WORKFLOWS = ROOT / ".github" / "workflows"


def _load(name: str) -> ModuleType:
    """Load a script by path, `.github/scripts` being no package."""
    spec = importlib.util.spec_from_file_location(
        name, ROOT / ".github" / "scripts" / f"{name}.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


script = _load("api_gaps")

WITNESS_BEFORE = '''
    """A package."""

    from __future__ import annotations

    from dataclasses import dataclass

    __all__ = ["Witness"]


    @dataclass(frozen=True)
    class Witness:
        """A witness stack."""

        stack: tuple[bytes, ...]

        def __init__(self, stack: list[bytes] | None = None) -> None:
            object.__setattr__(self, "stack", tuple(stack or ()))
'''

WITNESS_AFTER = '''
    """A package."""

    from __future__ import annotations

    from dataclasses import dataclass

    __all__ = ["Witness"]


    @dataclass(frozen=True)
    class Witness:
        """A witness stack."""

        _serialized: bytes

        def __init__(self, stack: list[bytes] | None = None) -> None:
            object.__setattr__(self, "_serialized", b"".join(stack or ()))

        @property
        def stack(self) -> tuple[bytes, ...]:
            """The stack."""
            return (self._serialized,)
'''

DECODE_BEFORE = '''
    """A package."""

    __all__ = ["bech32_decode"]


    def bech32_decode(bech: str) -> tuple[str, list[int]]:
        """Decode."""
        return bech, []
'''

DECODE_AFTER = '''
    """A package."""

    __all__ = ["bech32_decode"]


    def bech32_decode(bech: str) -> tuple[str, list[int], int]:
        """Decode, and say which checksum it was."""
        return bech, [], 1
'''


def _write(root: Path, source: str) -> None:
    """Write a version of `pkg` under `root/src`."""
    package = root / "src" / "pkg"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(dedent(source), encoding="utf-8")


class Pair:
    """Two versions of `pkg`, and the script run on them."""

    def __init__(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        self._runs = itertools.count()
        self._tmp = tmp_path
        self._monkeypatch = monkeypatch
        self._capsys = capsys
        self.root = tmp_path

    def load_git(
        self,
        package: str,
        *,
        ref: str,
        repo: str,
        search_paths: list[str],
        **options: bool | None,
    ) -> griffe.Object | griffe.Alias:
        """Load the old version as the script asks git for it."""
        assert (ref, repo) == ("base", ".")
        paths = [self.root / "old" / path for path in search_paths]
        return griffe.load(package, search_paths=paths, **options)  # type: ignore[arg-type]

    def run(self) -> tuple[int, list[str]]:
        """Run the script in the new version; return its exit code and lines."""
        self._monkeypatch.setattr(script.griffe, "load_git", self.load_git)
        self._monkeypatch.chdir(self.root / "new")
        code = script.main(["pkg", "base"])
        return code, self._capsys.readouterr().out.splitlines()

    def compare(self, before: str, after: str) -> tuple[int, list[str]]:
        """Write two versions of `__init__.py`, and run the script on them."""
        self.root = self._tmp / str(next(self._runs))
        _write(self.root / "old", before)
        _write(self.root / "new", after)
        return self.run()

    def griffe(self) -> list[str]:
        """Return what griffe's own comparison finds on the last pair."""
        old, new = (
            griffe.load("pkg", search_paths=[self.root / side / "src"])
            for side in ("old", "new")
        )
        return [str(breakage) for breakage in griffe.find_breaking_changes(old, new)]


@pytest.fixture
def pair(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> Pair:
    """Return a pair of versions to compare."""
    return Pair(tmp_path, monkeypatch, capsys)


def test_a_field_turned_into_a_property_is_a_break(
    pair: Pair,
) -> None:
    """The shape of btclib-org/btclib#2759, which griffe reads as no break."""
    found = pair.compare(WITNESS_BEFORE, WITNESS_AFTER)

    assert found == (
        1,
        [
            (
                "src/pkg/__init__.py:11: Witness: "
                "Dataclass fields changed: (stack) -> (_serialized)"
            )
        ],
    )
    assert pair.griffe() == []


def test_a_function_returning_one_more_value_is_a_break(
    pair: Pair,
) -> None:
    """The shape of btclib-org/base58-bech32#26, which griffe reads as none."""
    found = pair.compare(DECODE_BEFORE, DECODE_AFTER)

    assert found == (
        1,
        [
            (
                "src/pkg/__init__.py:7: bech32_decode: Return types are incompatible: "
                "tuple[str, list[int]] -> tuple[str, list[int], int]"
            )
        ],
    )
    assert pair.griffe() == []


@pytest.mark.parametrize("source", [WITNESS_AFTER, DECODE_AFTER])
def test_a_version_against_itself_is_no_break(
    pair: Pair,
    source: str,
) -> None:
    """The same API on both sides, a docstring and a body aside."""
    after = source.replace('"""The stack."""', '"""The elements."""').replace(
        "return bech, [], 1", "return bech, [], 2"
    )
    assert after != source

    assert pair.compare(source, after) == (0, [])


POINT = '''
    import dataclasses
    from dataclasses import dataclass, field

    @dataclass
    class Point:
        """A point."""

        {body}
'''


def _point(*lines: str) -> str:
    """Return a module holding the dataclass `Point` with these lines."""
    return POINT.replace("{body}", "\n        ".join(lines))


@pytest.mark.parametrize(
    ("before", "after", "change"),
    [
        (("x: int", "y: int"), ("y: int", "x: int"), "(x, y) -> (y, x)"),
        (("x: int", "y: int"), ("x: int",), "(x, y) -> (x)"),
        (("x: int",), ("x: int", "y: int = 0"), "(x) -> (x, y)"),
        (
            ("x: int", "y: int = 0"),
            ("x: int", "y: int = field(default=0, init=False)"),
            "(x, y) -> (x, y (init=False))",
        ),
        (
            ("x: int", "y: int = 0"),
            ("x: int", "y: int = dataclasses.field(default=0, kw_only=True)"),
            "(x, y) -> (x, y (kw_only))",
        ),
        (
            ("x: int", "y: int = 0"),
            ("_: dataclasses.KW_ONLY", "x: int", "y: int = 0"),
            "(x, y) -> (x (kw_only), y (kw_only))",
        ),
        (
            ("x: int", "y: int = field(default=0, init=False)"),
            (
                "x: int",
                "y: int = field(default=0, init=False)",
                "def __init__(self, x: int) -> None:",
                "    self.x = x",
                "    self.y = 0",
                "    self.z: int = 0",
            ),
            None,
        ),
    ],
)
def test_a_change_of_the_fields_is_a_break(
    pair: Pair,
    before: tuple[str, ...],
    after: tuple[str, ...],
    change: str | None,
) -> None:
    """Names, order, `init` and `kw_only`: what `dataclasses.fields` lists.

    An `__init__` assigning the fields changes none of them, and adds none.
    """
    code, lines = pair.compare(_point(*before), _point(*after))

    changes = [line.split(": ", 3)[-1] for line in lines]
    assert (code, changes) == ((1, [change]) if change else (0, []))


def test_a_dataclass_that_stops_being_one_is_a_break(
    pair: Pair,
) -> None:
    """`dataclasses.fields` raises on a class that is no dataclass."""
    before = _point("x: int")
    after = before.replace("    @dataclass\n", "")

    code, lines = pair.compare(before, after)

    assert (code, lines) == (
        1,
        [
            (
                "src/pkg/__init__.py:5: Point: "
                "Dataclass fields changed: (x) -> not a dataclass"
            )
        ],
    )


@pytest.mark.parametrize(
    "line",
    [
        "z: ClassVar[int] = 1",
        "z: 'ClassVar[int]' = 1",
        "z: InitVar[int] = 1",
        (
            "z: InitVar[int] = 1\n        def __init__(self, x: int) -> None:\n"
            "            self.x = x"
        ),
        "_: KW_ONLY",
        "@property\n        def z(self) -> int:\n            return 1",
        (
            "def __init__(self, x: int) -> None:\n            self.x = x\n"
            "            self.z: int = 1"
        ),
    ],
)
def test_what_is_no_field_changes_no_field(
    pair: Pair,
    line: str,
) -> None:
    """None of these is in `dataclasses.fields`.

    A class variable, an init-only variable, the marker, a property, a
    name set in `__init__`.
    """
    imports = "from typing import ClassVar\nfrom dataclasses import InitVar, KW_ONLY\n"
    before = imports + dedent(_point("x: int"))
    after = imports + dedent(_point("x: int", line))

    assert pair.compare(before, after) == (0, [])


def test_a_class_that_is_no_dataclass_has_no_fields_to_change(
    pair: Pair,
) -> None:
    """Annotations of a plain class, and becoming a dataclass, break nothing."""
    before = '''
        class Plain:
            """Plain."""

            x: int
    '''
    after = '''
        from dataclasses import dataclass

        @dataclass
        class Plain:
            """Plain."""

            y: int
    '''

    assert pair.compare(before, after) == (0, [])


def test_a_private_dataclass_is_not_compared(
    pair: Pair,
) -> None:
    """The walk is griffe's: a name that is not public is not walked."""
    before = _point("x: int").replace("class Point", "class _Point")
    after = _point("y: int").replace("class Point", "class _Point")

    assert pair.compare(before, after) == (0, [])


def test_the_fields_of_a_base_come_first(
    pair: Pair,
) -> None:
    """A field declared again keeps its place, as `dataclasses` orders it."""
    before = '''
        from dataclasses import dataclass

        @dataclass
        class Base:
            """Base."""

            a: int
            b: int

        @dataclass
        class Child(Base):
            """Child."""

            c: int
    '''
    after = before.replace(
        "            c: int", "            c: int\n            a: int"
    )

    assert pair.compare(before, after) == (0, [])

    changed = before.replace("class Child(Base)", "class Child")
    _, lines = pair.compare(before, changed)
    assert [line.split(": ", 3)[-1] for line in lines] == ["(a, b, c) -> (c)"]


NESTED = """
from dataclasses import dataclass


class Outer:
    \"\"\"Outer.\"\"\"

    @dataclass
    class Inner:
        \"\"\"Inner, whose docstring has a line at column 0:

column 0.
        \"\"\"

        x: int
"""


def test_a_nested_dataclass_is_read_from_its_module(pair: Pair) -> None:
    """A class source with a line at column 0 cannot be parsed on its own."""
    _, lines = pair.compare(NESTED, NESTED.replace("x: int", "y: int"))

    assert lines == [
        "src/pkg/__init__.py:8: Outer.Inner: Dataclass fields changed: (x) -> (y)"
    ]


def test_a_dataclass_of_an_unresolved_base_keeps_its_own_fields(
    pair: Pair,
) -> None:
    """A base outside the package leaves the class's own fields compared."""
    before = "from elsewhere import Base\n" + dedent(_point("x: int")).replace(
        "class Point", "class Point(Base)"
    )
    after = before.replace("x: int", "y: int")

    _, lines = pair.compare(before, after)

    assert [line.split(": ", 3)[-1] for line in lines] == ["(x) -> (y)"]


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("def f(x):", "def f(x) -> int:"),
        ("def f(x) -> None:", "def f(x) -> int:"),
        ("def f(x) -> dict[str,int]:", "def f(x) -> dict[str, int]:"),
    ],
)
def test_a_return_annotation_gained_is_no_break(
    pair: Pair,
    before: str,
    after: str,
) -> None:
    """Added, gaining a value, or written with other spacing."""
    body = "\n    return 1\n"

    assert pair.compare(before + body, after + body) == (
        0,
        [],
    )


def test_a_change_of_spelling_alone_is_reported(
    pair: Pair,
) -> None:
    """The annotations are compared as griffe renders them, not as types."""
    before = "from typing import Optional\n\ndef f(x) -> Optional[int]:\n    return 1\n"
    after = before.replace("Optional[int]", "int | None")

    _, lines = pair.compare(before, after)

    assert [line.split(": ", 3)[-1] for line in lines] == [
        "Optional[int] -> int | None"
    ]


def test_a_return_annotation_removed_is_left_to_griffe(
    pair: Pair,
) -> None:
    """Griffe reports it, so this script does not report it twice."""
    body = "\n    return 1\n"

    found = pair.compare("def f(x) -> int:" + body, "def f(x):" + body)

    assert found == (0, [])
    assert pair.griffe() == ["Return types are incompatible"]


def test_a_method_and_a_property_are_named_by_their_class(
    pair: Pair,
) -> None:
    """The object is the path within its module, as griffe prints it."""
    before = '''
        class Key:
            """A key."""

            def serialize(self) -> bytes:
                return b""

            @property
            def size(self) -> int:
                return 0
    '''
    after = before.replace("-> bytes", "-> str").replace("-> int", "-> float")

    code, lines = pair.compare(before, after)

    assert code == 1
    assert sorted(line.split(": ", 2)[1] for line in lines) == [
        "Key.serialize",
        "Key.size",
    ]


def test_a_re_exported_object_is_reported_once(
    pair: Pair,
) -> None:
    """Reached through its module and through the package, it is one object."""
    for side, returns in (("old", "int"), ("new", "str")):
        package = pair.root / side / "src" / "pkg"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text(
            'from pkg.codec import f\n\n__all__ = ["f"]\n', encoding="utf-8"
        )
        (package / "codec.py").write_text(
            f'__all__ = ["f"]\n\ndef f() -> {returns}:\n    return 1\n',
            encoding="utf-8",
        )

    assert pair.run() == (
        1,
        ["src/pkg/codec.py:3: f: Return types are incompatible: int -> str"],
    )


def test_a_failed_comparison_exits_2_with_its_traceback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A git error, or a package absent, is told from a finding."""

    def fail(*_: object, **__: object) -> None:
        message = "fatal: invalid reference: base"
        raise griffe.GitError(message)

    monkeypatch.setattr(script.griffe, "load_git", fail)

    assert script.main(["pkg", "base"]) == script.FAILED
    out, err = capsys.readouterr()
    assert out == ""
    assert "invalid reference: base" in err


def test_run_as_a_program_outside_a_repository_it_exits_2(tmp_path: Path) -> None:
    """The workflows run it by path, and read its exit code."""
    ran = subprocess.run(
        [sys.executable, str(_SCRIPT), "pkg", "HEAD^1"],
        capture_output=True,
        check=False,
        cwd=tmp_path,
        encoding="utf-8",
    )

    assert (ran.returncode, ran.stdout) == (script.FAILED, "")
    assert "Traceback" in ran.stderr


def test_a_field_prints_its_flags() -> None:
    """A field at the defaults prints its name alone."""
    assert str(script.Field("x")) == "x"
    flagged = script.Field("x", init=False, kw_only=True)
    assert str(flagged) == "x (init=False, kw_only)"


def test_a_finding_is_read_as_griffe_s_by_both_readers(
    pair: Pair,
) -> None:
    """The label's classifier and the release check read a finding.

    The first calls it a break, and the second keys it by its class, as a
    span of the notes would name it.
    """
    _, lines = pair.compare(WITNESS_BEFORE, WITNESS_AFTER)
    output = "\n".join(lines) + "\n"

    assert _load("api_break").classify(1, output) == "true"
    [finding] = _load("check_public_api").findings(output, "pkg")
    assert (finding.key, finding.module) == ("Witness", "pkg")


def _locked(name: str) -> str:
    """Return the version `uv.lock` holds for a package."""
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    version: str = next(p["version"] for p in lock["package"] if p["name"] == name)
    return version


def test_the_tests_load_the_griffe_the_workflows_run() -> None:
    """Every pin in both workflows, the test group's, and the lock agree."""
    pins = {
        pin
        for name in ("reusable-api-break.yml", "reusable-public-api.yml")
        for pin in re.findall(
            r"griffe==([\d.]+)", (_WORKFLOWS / name).read_text(encoding="utf-8")
        )
    }
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert pins == {_locked("griffe")}
    assert f"griffe=={_locked('griffe')}" in pyproject["dependency-groups"]["test"]


@pytest.mark.parametrize(
    ("name", "job", "base"),
    [
        ("reusable-api-break.yml", "api-break", "HEAD^1"),
        ("reusable-public-api.yml", "public-api", '"$PREVIOUS_TAG"'),
    ],
)
def test_both_workflows_add_the_findings_to_griffe_s(
    name: str, job: str, base: str
) -> None:
    """Both run the script after griffe, against the same base.

    Its standard output alone is added, and its exit code is taken where
    it is the higher.
    """
    parsed = yaml.safe_load((_WORKFLOWS / name).read_text(encoding="utf-8"))
    run = next(
        " ".join(step["run"].replace("\\\n", " ").split())
        for step in parsed["jobs"][job]["steps"]
        if "api_gaps.py" in step.get("run", "")
    )

    assert (
        "uv run --quiet --no-project --python 3.15 --with griffe==2.2.0 "
        f'standard/.github/scripts/api_gaps.py "$PACKAGE" {base} '
        '>> "$findings" || gaps=$? '
        'if [ "$gaps" -gt "$status" ]; then status=$gaps; fi'
    ) in run
    assert f"-a {base}" in run
