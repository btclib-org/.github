# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Refuse a public API finding that RELEASE_NOTES.md does not name.

`griffe check -f oneline` prints one finding per line,
`path:line: object: explanation`, on standard error. Each finding is
reduced to a key and compared with the keys of the backticked spans of
one section of the notes: the section of the tag being released, or the
first one under the file's title where there is no tag, which is the
section open for the release to come.

A finding of a module, printed `<module>`, has the module's dotted path
as its key, taken from the path griffe printed. Any other finding has
the name of its object up to the first `(` or `.`, so
`ScriptError.__init__(code)` is `ScriptError`. A span has that name as
well, and the whole of what precedes its first `(` besides, so
`btclib.hwi` names the module and `ScriptError` names the class.

A span may qualify an object by the modules it is imported from, the way
a caller spells it: `tx_builder.build_psbt`, `fetch.ElectrumFetcher`. A
component of such a span names the finding with that key when every
component before it is a component of the finding's module, in the same
order, so `fetch.ElectrumFetcher` names `ElectrumFetcher.timeout` of
`btclib_wallet.fetch.electrum`, which `btclib_wallet.fetch` re-exports.
What qualifies an object of another package, `threading.TIMEOUT_MAX`,
names nothing of this one's, and neither does a module finding, which
the span naming its dotted path alone covers.

Nothing is asked of where in the section a name stands: not every tree
keeps a breaking-changes subsection. A finding that is no break, a
widening, stays refused until the section names its object all the same.

    uv run --no-project --python 3.15 \
        .github/scripts/check_public_api.py "$package" findings.txt \
        RELEASE_NOTES.md --tag "$tag"
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

_FINDING = re.compile(r"(?P<path>.+?):(?P<line>\d+): (?P<obj>\S+): (?P<why>.*)")
_FENCE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
_SPAN = re.compile(r"`([^`]+)`")
_MODULE = "<module>"


@dataclass(frozen=True)
class Finding:
    """One line of griffe's output, or a line that is not one."""

    text: str
    name: str
    key: str
    path: str = ""
    line: str = ""
    why: str = ""
    module: str = ""


def _head(name: str) -> str:
    """Return the name up to its first `(` or `.`."""
    return re.split(r"[.(]", name, maxsplit=1)[0]


def _dotted(path: str, package: str) -> str:
    """Return the dotted path of the module a file holds."""
    parts = PurePosixPath(path).with_suffix("").parts
    if package in parts:
        parts = parts[parts.index(package) :]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def findings(output: str, package: str) -> list[Finding]:
    """Read griffe's `oneline` output, a line it cannot read being a finding."""
    found = []
    for raw in output.splitlines():
        text = raw.strip()
        if not text:
            continue
        match = _FINDING.fullmatch(text)
        if match is None:
            found.append(Finding(text=text, name=text, key=text))
            continue
        path, obj = match["path"], match["obj"]
        module = ""
        if obj == _MODULE:
            name = key = _dotted(path, package)
        else:
            name, key, module = obj, _head(obj), _dotted(path, package)
        found.append(
            Finding(text, name, key, path, match["line"], match["why"], module)
        )
    return found


def section(notes: str, tag: str | None) -> str | None:
    """Return the section of the notes for the tag, or None where it has none.

    Without a tag, the first `## ` heading. With one, the heading that is
    the tag followed by a space or by nothing, as the job lifting the
    release notes reads it, so `## v2026.9.29` and
    `## v2026.9.29 (patch)` are the tag's and `## v2026.9.290` is not.
    """
    heading = (
        re.compile(r"## ") if not tag else re.compile(rf"## {re.escape(tag)}( |$)")
    )
    lines = notes.splitlines()
    start = next((n for n, line in enumerate(lines) if heading.match(line)), None)
    if start is None:
        return None
    body = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def _spans(text: str) -> list[str]:
    """Return the backticked spans of a section, each on one line.

    Fenced blocks are dropped first, their fences being no span, and a
    span may wrap across a line of the notes.
    """
    return [" ".join(span.split()) for span in _SPAN.findall(_FENCE.sub("", text))]


def named(text: str) -> set[str]:
    """Return the keys of the backticked spans of a section."""
    keys: set[str] = set()
    for name in _spans(text):
        keys.update({_head(name), name.split("(")[0]})
    return keys


def qualified(text: str) -> set[tuple[tuple[str, ...], str]]:
    """Return each name a span qualifies, with the components before it."""
    pairs: set[tuple[tuple[str, ...], str]] = set()
    for name in _spans(text):
        parts = name.split("(")[0].split(".")
        pairs.update((tuple(parts[:n]), parts[n]) for n in range(1, len(parts)))
    return pairs


def covered(
    finding: Finding, keys: set[str], pairs: set[tuple[tuple[str, ...], str]]
) -> bool:
    """Return whether a span of the section names the finding's object."""
    if finding.key in keys:
        return True
    if not finding.module:
        return False
    for qualifiers, name in pairs:
        components = iter(finding.module.split("."))
        if name == finding.key and all(q in components for q in qualifiers):
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    """Print each finding as covered or not, and refuse the uncovered ones."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", help="the package griffe walked")
    parser.add_argument("findings", help="griffe's `-f oneline` output")
    parser.add_argument("notes", help="RELEASE_NOTES.md")
    parser.add_argument("--tag", help="the tag being released, absent on a rehearsal")
    args = parser.parse_args(argv)

    with Path(args.findings).open(encoding="utf-8") as stream:
        found = findings(stream.read(), args.package)
    if not found:
        print("no findings")
        return 0

    with Path(args.notes).open(encoding="utf-8") as stream:
        body = section(stream.read(), args.tag)
    if body is None:
        where = f"for {args.tag}" if args.tag else "under the title"
        print(f"::error::{args.notes} has no section {where}")
        return 1

    keys, pairs = named(body), qualified(body)
    missing = []
    for finding in found:
        if covered(finding, keys, pairs):
            print(f"covered   {finding.text}")
            continue
        print(f"uncovered {finding.text}")
        if finding.path:
            message = f"{finding.name}: {finding.why}; not named in the notes"
            message = message.replace("%", "%25").replace("\n", "%0A")
            print(f"::error file={finding.path},line={finding.line}::{message}")
        if finding.name not in missing:
            missing.append(finding.name)
    if missing:
        print(
            f"::error::the section of {args.notes} does not name: " + ", ".join(missing)
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
