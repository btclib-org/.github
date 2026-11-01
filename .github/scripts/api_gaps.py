# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Report the breaks below, which `griffe check` does not compare or can skip.

`griffe check` reads a dataclass field turned into a property as a name
still present, and compares no field list (btclib-org/.github#1934).
Where `@dataclass` writes `__init__`, griffe compares the `__init__` it
generates, so griffe reports a field change that breaks that signature
as well as this script. griffe calls any two return annotations
compatible, so a changed one is no finding either
(btclib-org/.github#1796), and it compares no annotation of a parameter
or an attribute (btclib-org/.github#1946). It keys what it has compared
on the old object's path alone, so it can skip the override a subclass
gains or drops (btclib-org/.github#1943, mkdocstrings/griffe#510). This
script loads the same two versions with griffe's API, and reports these:

- a public dataclass whose fields changed: their names, their order, or
  `init` or `kw_only` of one of them. `dataclasses.fields`, `replace`,
  `asdict`, `astuple` and `__match_args__` all read that list. A class
  that stops being a dataclass is reported too.
- a public function, method or property whose return annotation changed,
  and a public attribute whose annotation changed. To this comparison
  an annotation added, or one that was `None`, is no break. One removed
  from a function or a method, `None` included, is a break `griffe
  check` reports itself; one removed from an attribute or a property,
  which griffe models as an attribute, this script reports.
- a parameter of a public function or method whose annotation changed,
  from `None` as from any other. One added or removed is no break: a
  parameter without an annotation refuses no argument. The signatures
  of an `@overload` and the parameters of a property's setter are
  compared neither here nor by griffe.
- on a pair of two paths, or a later pair of one old object, what
  griffe's own comparison of two functions finds, and an object that
  changed kind. griffe can skip these pairs. A class pair it skips is
  compared for its fields alone, and its members pair in turn. Where
  griffe does reach a pair of two paths, a subclass declared first or a
  function moved to another module, both report it.

griffe also skips pairs, and what griffe alone compares then goes
unreported by either; what this script compares itself is still
reported. griffe skips, for one, a first pair on one path where it first
reaches the object through more aliases on the new side than on the old.
Examples, not a complete list, are a function, a class or a module
re-exported through one more module, and a nested class a subclass gains
in place of its base's.

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
from typing import TYPE_CHECKING, TypeIs, override

import griffe

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

SEARCH_PATHS = (".", "src")
FAILED = 2
FIELDS_CHANGED = "Dataclass fields changed"
RETURNS_CHANGED = griffe.BreakageKind.RETURN_CHANGED_TYPE.value
ATTRIBUTE_CHANGED = griffe.BreakageKind.ATTRIBUTE_CHANGED_TYPE.value
KIND_CHANGED = griffe.BreakageKind.OBJECT_CHANGED_KIND.value
PARAMETER_CHANGED = "Parameter types are incompatible"
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
    seen: set[tuple[str, str]] | None = None,
) -> Iterator[tuple[griffe.Object, griffe.Object]]:
    """Yield each public object of the old version with the new one's.

    The walk is `griffe check`'s: the public members of the old version,
    each paired with the new member of the same name, and the members of
    a module or class paired in turn. A pair reached twice, through a
    re-export or an inherited member, is yielded once. An object paired
    with two others, a method of a base and the override a subclass
    gains, is yielded with each, whatever their kinds. A name gone is
    left to `griffe check`, which misses it on a class or module it skips.
    """
    seen = set() if seen is None else seen
    new_members = new.all_members
    for name, old_member in old.all_members.items():
        if not old_member.is_public or name not in new_members:
            continue
        before, after = _target(old_member), _target(new_members[name])
        if before is None or after is None:
            continue
        pair = (before.path, after.path)
        if pair in seen:
            continue
        seen.add(pair)
        yield before, after
        if before.kind is after.kind and (before.is_module or before.is_class):
            yield from pairs(before, after, seen)


def _shown(found: tuple[Field, ...] | None) -> str:
    """Return a list of fields as a finding prints it."""
    if found is None:
        return "not a dataclass"
    return "(" + ", ".join(str(field) for field in found) + ")"


def _is_property(obj: griffe.Object) -> TypeIs[griffe.Attribute]:
    """Say whether griffe models an object as a property."""
    return isinstance(obj, griffe.Attribute) and "property" in obj.labels


def _annotation(obj: griffe.Object) -> str | griffe.Expr | None:
    """Return what a function returns, or what an attribute is annotated."""
    if isinstance(obj, griffe.Function):
        return obj.returns
    if isinstance(obj, griffe.Attribute):
        return obj.annotation
    return None


def _annotation_changed(
    old: str | griffe.Expr | None,
    new: str | griffe.Expr | None,
    *,
    removed_is_a_change: bool,
) -> bool:
    """Say whether an annotation changed, an added one being no change.

    One removed is a change only where the caller asks, for the reason the
    module docstring gives.
    """
    if old is None or str(old) == "None":
        return False
    if new is None:
        return removed_is_a_change
    return str(old) != str(new)


def _line(obj: griffe.Object, kind: str, change: str = "", parameter: str = "") -> str:
    """Return a finding in the shape of `griffe check -f oneline`."""
    title = obj.canonical_path[len(obj.module.path) + 1 :] or "<module>"
    if parameter:
        title = f"{title}({parameter})"
    where = obj.relative_filepath.as_posix()
    line = f"{where}:{obj.lineno or 0}: {title}: {kind}"
    return f"{line}: {change}" if change else line


def _parameters_changed(old: griffe.Function, new: griffe.Function) -> Iterator[str]:
    """Yield each parameter both functions have, with its annotation changed."""
    for parameter in old.parameters:
        if parameter.name not in new.parameters:
            continue
        was, now = parameter.annotation, new.parameters[parameter.name].annotation
        if was is not None and now is not None and str(was) != str(now):
            yield _line(new, PARAMETER_CHANGED, f"{was} -> {now}", parameter.name)


def _griffe_on_functions(old: griffe.Function, new: griffe.Function) -> Iterator[str]:
    """Yield what griffe finds between two functions, whatever their paths.

    `griffe.find_breaking_changes` compares the members of two objects
    and has no entry for one pair, so each function is put in a module of
    its own that nothing else reads. Its walk drops an old member that is
    not public, and a function can be public only through the alias that
    `pairs` walked, so the old one is held as an alias.
    """
    holders = griffe.Module("old"), griffe.Module("new")
    holders[0].members["function"] = griffe.Alias("function", old, parent=holders[0])
    holders[1].members["function"] = new
    for breakage in griffe.find_breaking_changes(*holders):
        values = breakage.old_value, breakage.new_value
        parameter = next(
            (each.name for each in values if isinstance(each, griffe.Parameter)),
            "",
        )
        yield _line(new, breakage.kind.value, parameter=parameter)


def breaks(
    old: griffe.Object | griffe.Alias, new: griffe.Object | griffe.Alias
) -> Iterator[str]:
    """Yield each break of the kinds the module docstring names.

    A first pair on one path is taken as compared by griffe, which the
    module docstring says is not always so.
    """
    compared: set[str] = set()
    for before, after in pairs(old, new):
        skipped = before.path != after.path or before.path in compared
        compared.add(before.path)
        if before.kind is not after.kind:
            if skipped:
                yield _line(
                    after, KIND_CHANGED, f"{before.kind.value} -> {after.kind.value}"
                )
            continue
        if isinstance(before, griffe.Class) and isinstance(after, griffe.Class):
            was = fields(before)
            now = fields(after)
            if was is not None and now != was:
                yield _line(after, FIELDS_CHANGED, f"{_shown(was)} -> {_shown(now)}")
            continue
        was_annotated, now_annotated = _annotation(before), _annotation(after)
        is_attribute = isinstance(after, griffe.Attribute)
        if _annotation_changed(
            was_annotated, now_annotated, removed_is_a_change=is_attribute
        ):
            kind = (
                ATTRIBUTE_CHANGED
                if is_attribute and not _is_property(after)
                else RETURNS_CHANGED
            )
            yield _line(after, kind, f"{was_annotated} -> {now_annotated}")
        if isinstance(before, griffe.Function) and isinstance(after, griffe.Function):
            yield from _parameters_changed(before, after)
            if skipped:
                yield from _griffe_on_functions(before, after)


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
