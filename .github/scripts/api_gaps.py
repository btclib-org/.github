# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Report breaks of the kinds below, which `griffe check` does not compare.

`griffe check` reads a dataclass field turned into a property as a name
still present, and compares no field list (btclib-org/.github#1934).
Where `@dataclass` writes `__init__`, griffe reports a renamed `init`
field, or a positional one that moved, as a change of `__init__`'s
parameters, so that change is reported twice. griffe calls any two
return annotations compatible, so a changed one is no finding either
(btclib-org/.github#1796). This script loads the same two versions with
griffe's API, and reports these:

- a public dataclass whose fields changed: their names, their order, or
  `init` or `kw_only` of one of them. `dataclasses.fields`, `replace`,
  `asdict`, `astuple` and `__match_args__` all read that list. A class
  that stops being a dataclass is reported too.
- a public function, method or property whose return annotation changed.
  An annotation added, or one that was `None`, is no break; one removed
  is a break `griffe check` reports itself.

The annotations are compared as griffe renders them, so a change of
spelling alone, `Optional[int]` to `int | None`, is reported as well.

Each finding is one line in the shape of `griffe check -f oneline`,
`path:line: object: explanation`, so that `api_break.py` and
`check_public_api.py` read it as one of griffe's. The base is a git
reference; the current version is the working tree, which is the tag a
release workflow checks out. The exit code is 1 with findings, 0
without, and 2 where the comparison failed, its traceback on standard
error.

    uv run --quiet --no-project --python 3.15 --with griffe==2.2.0 \
        .github/scripts/api_gaps.py "$package" "$base" >> findings.txt
"""

from __future__ import annotations

import argparse
import ast
import functools
import sys
import traceback
from dataclasses import dataclass
from typing import TYPE_CHECKING, override

import griffe

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

SEARCH_PATHS = (".", "src")
FAILED = 2
FIELDS_CHANGED = "Dataclass fields changed"
RETURNS_CHANGED = griffe.BreakageKind.RETURN_CHANGED_TYPE.value
_DATACLASS = "dataclasses.dataclass"
_FIELD = "dataclasses.field"
_KW_ONLY = "dataclasses.KW_ONLY"
_NO_FIELD = {"dataclasses.InitVar", "typing.ClassVar", "typing_extensions.ClassVar"}
_UNRESOLVED = (griffe.AliasResolutionError, griffe.CyclicAliasError)


@dataclass(frozen=True)
class Field:
    """One field of a dataclass, as `dataclasses.fields` lists it."""

    name: str
    init: bool = True
    kw_only: bool = False

    @override
    def __str__(self) -> str:
        flags = [
            flag
            for flag, on in (("init=False", not self.init), ("kw_only", self.kw_only))
            if on
        ]
        return f"{self.name} ({', '.join(flags)})" if flags else self.name


def _named(cls: griffe.Class, node: ast.expr | None) -> str:
    """Return the dotted path a name, a subscript or a call names.

    The first name is resolved in the module of the class, which is the
    scope a class body reads, so `field` imported from `dataclasses` is
    `dataclasses.field`. A string, a quoted annotation, is parsed first.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        try:
            node = ast.parse(node.value, mode="eval").body
        except SyntaxError:
            return ""
    while isinstance(node, ast.Subscript | ast.Call):
        node = node.value if isinstance(node, ast.Subscript) else node.func
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return ""
    try:
        first = cls.module.resolve(node.id)
    except griffe.NameResolutionError:
        first = node.id
    return ".".join([first, *reversed(parts)])


def _flag(call: ast.expr | None, keyword: str) -> object:
    """Return the constant a call passes for a keyword, or None."""
    if isinstance(call, ast.Call):
        for argument in call.keywords:
            if argument.arg == keyword and isinstance(argument.value, ast.Constant):
                return argument.value.value
    return None


@functools.cache
def _tree(source: str) -> ast.Module:
    """Return a module's syntax tree, parsed once for all its classes."""
    return ast.parse(source)


def _class_node(cls: griffe.Class) -> ast.ClassDef:
    """Return the definition of a class, found in its module's tree.

    The module is parsed rather than the class's own lines, which do not
    parse alone where the class is nested and a line of it, in a
    docstring, starts at column 0. griffe numbers a class from its first
    decorator.
    """
    for node in ast.walk(_tree(cls.module.source)):
        if not isinstance(node, ast.ClassDef) or node.name != cls.name:
            continue
        first = min([node.lineno, *(each.lineno for each in node.decorator_list)])
        if first == cls.lineno:
            return node
    message = f"{cls.path}: no class at line {cls.lineno} of its module"
    raise LookupError(message)


def _own_fields(cls: griffe.Class) -> list[Field] | None:
    """Return the fields a class declares, None where it is no dataclass.

    They are read from the class body and not from griffe's members,
    which an assignment in `__init__` overwrites. An annotated name of
    the body is a field, unless it is a `ClassVar`, an `InitVar` or the
    `KW_ONLY` marker.
    """
    node = _class_node(cls)
    decorator = next(
        (each for each in node.decorator_list if _named(cls, each) == _DATACLASS),
        None,
    )
    if decorator is None:
        return None
    kw_only = _flag(decorator, "kw_only") is True
    fields = []
    for statement in node.body:
        if not isinstance(statement, ast.AnnAssign):
            continue
        if not isinstance(statement.target, ast.Name):
            continue
        kind = _named(cls, statement.annotation)
        if kind == _KW_ONLY:
            kw_only = True
            continue
        if kind in _NO_FIELD:
            continue
        value = statement.value
        call = value if _named(cls, value) == _FIELD else None
        fields.append(
            Field(
                statement.target.id,
                init=_flag(call, "init") is not False,
                kw_only=kw_only or _flag(call, "kw_only") is True,
            )
        )
    return fields


def fields(cls: griffe.Class) -> tuple[Field, ...] | None:
    """Return the fields of a dataclass, None where the class is none.

    The fields of each dataclass among its bases come first, from the
    last base of the method resolution order, and a field declared again
    keeps the place it was first given, as `dataclasses` orders them.
    """
    try:
        chain = [*reversed(cls.mro()), cls]
    except (ValueError, *_UNRESOLVED):
        chain = [cls]
    merged: dict[str, Field] | None = None
    for each in chain:
        own = _own_fields(each)
        if own is None:
            continue
        merged = {} if merged is None else merged
        merged.update((field.name, field) for field in own)
    return None if merged is None else tuple(merged.values())


def _target(member: griffe.Object | griffe.Alias) -> griffe.Object | None:
    """Return the object a member is, its alias resolved, or None."""
    if not isinstance(member, griffe.Alias):
        return member
    try:
        return member.final_target
    except _UNRESOLVED:
        return None


def pairs(
    old: griffe.Object | griffe.Alias,
    new: griffe.Object | griffe.Alias,
    seen: set[str] | None = None,
) -> Iterator[tuple[griffe.Object, griffe.Object]]:
    """Yield each public object of the old version with the new one's.

    The walk is `griffe check`'s: the public members of the old version,
    each paired with the new member of the same name, and the members of
    a module or class paired in turn. An object reached twice, through a
    re-export or an inherited member, is yielded once. A name gone, or
    an object that changed kind, is `griffe check`'s to report.
    """
    seen = set() if seen is None else seen
    new_members = new.all_members
    for name, old_member in old.all_members.items():
        if not old_member.is_public or name not in new_members:
            continue
        before, after = _target(old_member), _target(new_members[name])
        if before is None or after is None or before.path in seen:
            continue
        seen.add(before.path)
        if before.kind is not after.kind:
            continue
        yield before, after
        if before.is_module or before.is_class:
            yield from pairs(before, after, seen)


def _shown(found: tuple[Field, ...] | None) -> str:
    """Return a list of fields as a finding prints it."""
    if found is None:
        return "not a dataclass"
    return "(" + ", ".join(str(field) for field in found) + ")"


def _returns(obj: griffe.Object) -> str | griffe.Expr | None:
    """Return what a function or a property is annotated to return."""
    if isinstance(obj, griffe.Function):
        return obj.returns
    if isinstance(obj, griffe.Attribute) and "property" in obj.labels:
        return obj.annotation
    return None


def _returns_changed(
    old: str | griffe.Expr | None, new: str | griffe.Expr | None
) -> bool:
    """Say whether a return annotation changed, an added one being no change."""
    if old is None or new is None:
        return False
    return str(old) not in {"None", str(new)}


def _line(obj: griffe.Object, kind: str, old: str, new: str) -> str:
    """Return a finding in the shape of `griffe check -f oneline`."""
    title = obj.canonical_path[len(obj.module.path) + 1 :] or "<module>"
    where = obj.relative_filepath.as_posix()
    return f"{where}:{obj.lineno or 0}: {title}: {kind}: {old} -> {new}"


def breaks(
    old: griffe.Object | griffe.Alias, new: griffe.Object | griffe.Alias
) -> Iterator[str]:
    """Yield each break of the kinds the module docstring names."""
    for before, after in pairs(old, new):
        if isinstance(before, griffe.Class) and isinstance(after, griffe.Class):
            was = fields(before)
            now = fields(after)
            if was is not None and now != was:
                yield _line(after, FIELDS_CHANGED, _shown(was), _shown(now))
            continue
        was_returning, now_returning = _returns(before), _returns(after)
        if _returns_changed(was_returning, now_returning):
            yield _line(after, RETURNS_CHANGED, str(was_returning), str(now_returning))


def load(
    package: str, against: str
) -> tuple[griffe.Object | griffe.Alias, griffe.Object | griffe.Alias]:
    """Load the package at a git reference and in the working tree.

    The options are the ones `griffe check -s . -s src -X` loads with.
    """
    old = griffe.load_git(
        package,
        ref=against,
        repo=".",
        search_paths=list(SEARCH_PATHS),
        allow_inspection=False,
        resolve_aliases=True,
        resolve_external=None,
    )
    new = griffe.load(
        package,
        try_relative_path=True,
        search_paths=list(SEARCH_PATHS),
        allow_inspection=False,
        resolve_aliases=True,
        resolve_external=None,
    )
    return old, new


def main(argv: Sequence[str] | None = None) -> int:
    """Print each finding, and exit as `griffe check` does on one.

    :param argv: the arguments, `sys.argv[1:]` where none are given.
    :returns: 1 with findings, 0 without, 2 where the comparison failed.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", help="the package griffe walks")
    parser.add_argument("against", help="the git reference of the base")
    args = parser.parse_args(argv)
    try:
        old, new = load(args.package, args.against)
        found = list(breaks(old, new))
    # whatever fails, griffe's own exceptions or a git one, is told apart
    # from a finding by its exit code, which a caller reads
    except Exception:  # noqa: BLE001
        traceback.print_exc(file=sys.stderr)
        return FAILED
    for line in found:
        print(line)
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
