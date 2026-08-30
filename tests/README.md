# Tests

This file exists for section 7 of the [organization standard][std],
which asks each repository to declare which of its conventions the suite
turns into a red test rather than leave it to be read off a directory
listing, and to declare, with the reason, what of that section a suite
declines. The standard is this tree's own `README.md`, and the suite's
subject is whether the other repositories still agree with it:
`__init__.py`'s docstring says what it asks and how, and `alignment.yml`
is the job that runs it.

## Convention tests

Section 7 lists the conventions a suite can turn into a red test, and
says a repository needs the ones its own prose states rather than all of
them. That escape clause is right and it costs something: an absent
convention test reads exactly like a convention this repository does not
have, and a `grep` over `tests/` cannot tell the two apart.

So which of them this repository tests is **declared here**.

| convention | module |
| --- | --- |
| the changelog | `changelog_test.py` |

Not tested here: the public surface; the copyright header; the
documentation; the import graph; the build system; the calling
convention; input validation; the suite opens no socket.

Most of these walk code a tree ships, and this tree ships none:
`package = false` in `pyproject.toml`, no `src/`, no build backend and
no `docs/`. Modules here ask the standard's side of some of the same
questions of the *other* repositories -- `surface_test.py` whether a
published package's modules declare `__all__`, `copyright_test.py`
whether a tree's `notice-rgx` transcribes its `COPYRIGHT` -- and that is
the suite's subject rather than a convention test over itself: the
census section 7 asks for belongs to the suite of the tree that ships
the package, which is what `surface_test.py`'s docstring says.

**The changelog** is the bullet with a subject here, `CHANGELOG.md`
being a file this tree keeps rather than a package it ships.

**The suite opens no socket** is the bullet this suite does not keep,
rather than one it leaves untested: every test that reaches GitHub
carries the `integration` marker, and `__init__.py`'s docstring is where
the reason is.

Section 7 asks a test in the same suite to assert this declaration, and
`conventions_test.py` is it. It reads section 7's conventions off
`../README.md` rather than keeping a copy of them, and asks that the
table and the *Not tested here* line account for each of them once.

## What of section 7 this suite takes, and what has no subject here

- **`pytest-randomly` is installed and needs no flag**, section 7's
  default. What it guards here is the session fixtures: every repository
  document, every clone and every tier is fetched once and read by every
  test after, so a test that mutated what it read -- a key popped from
  the shared `dict`, a list sorted in place -- would pass or fail by what
  ran before it, and nothing else in this suite would notice. Declining
  it on the ground that the fetched answers are read once and never
  changed was weighed and refused: nothing enforces that, and the
  shuffle is what notices the day it stops being true. `-p no:randomly`
  puts the collection order back to reproduce a failure against it, and
  the seed a run prints reproduces the shuffle.
- **The suite is integration but for the modules whose subject is this
  tree**, and it sits in `tests/` rather than under `tests/integration/`
  because there is nothing beside it to keep apart. Every test that
  reaches GitHub carries the `integration` marker; `BTCLIB_INTEGRATION`
  is the switch, and `conftest.py` skips the run without it at
  collection, naming the switch in the skip. `alignment.yml` sets it,
  and refuses the run before the checkout where the token it needs is
  absent rather than letting the suite skip.
- **No functional layer**: `tests/functional/` is for a suite that
  starts what the repository ships, and this tree ships nothing to start.
- **No property layer**: section 7 keys it on a parser between the tree
  and an adversary, and says a suite whose subject is a measurement does
  not owe it. Every question here is a reading of a tree or of an API
  answer against `README.md`.
- **Nothing is vendored, and the suite fetches by design.** Section 7
  says a test never reaches the network and every test here that asks
  about another repository does, for the reason `__init__.py`'s docstring
  gives: what it measures is agreement with the standard, and the
  standard is here. So there is no `tests/_data/`, no pins file and no
  `vendored-vectors` workflow.
- **No per-test timeout**, where section 7 asks one of a suite that
  waits on anything outside its own process: every test here that asks
  about another repository waits on GitHub, and `alignment.yml`'s
  `timeout-minutes` bounds the job rather than the test.
  btclib-org/.github#617 is that gap.
- **No `slow` marker.** The markers registered are `integration`, `tier`
  and `backlog`, each with its reason at the key in `pyproject.toml`.
- **No `--cov` and no `-n auto`**, the comment at `addopts` in
  `pyproject.toml` giving the reason for each: coverage would be the
  suite measuring itself, this tree shipping no code of its own, and a
  test that asks about another repository waits on the network rather
  than on a core.
- **Layout**: `tests/` mirrors a package, and there is none. The modules
  sit flat, each docstring naming what it reads, and the shared code is
  in `__init__.py` for the reason its docstring gives.
- **The suite writes nothing into the checkout**: the clones go under
  pytest's own temporary directory, and so does the suite
  `backlog_test.py` runs through `pytester`.

[std]: https://github.com/btclib-org/.github/blob/main/README.md
