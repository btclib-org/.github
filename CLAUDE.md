# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working
with code in this repository.

`README.md` is the standard every btclib-org repository is built and
kept to, `profile/README.md` is the organization's page, and the issue
tracker is where a repository's drift from that standard is filed and
worked off. Read `README.md` before changing it: most of what a session
here wants to add is already in it, with the alternative that was
rejected beside it.

The only Python is `tests/`, and its subject is the organization rather
than this tree: whether the repositories still agree with `README.md`,
which is the half of section 15's audit a machine can run.

How to work here — what the issue tracker takes, the prose style, and
how a pull request is opened and landed — is `CONTRIBUTING.md`, which is
the same file in every repository of the organization up to its last
section, which is this tree's and holds the commands and the gates.
Repository
configuration is
`REPOSITORY.md`: read it before changing a workflow, a branch rule or a
setting. Reviewing is `REVIEWING.md`, and `/review` is that file as a
command; read it before reviewing a pull request and before opening one,
since it is what the pull request will be answered against.

## Architecture

`README.md` is the standard, and it is the product: every other
repository of the organization is built and kept to it, and a change here
is a change to what they are measured against. `profile/README.md` is the
organization's page, `REPOSITORY.md` is this repository's own settings
read back from the endpoint, and `tests/` is the half of section 15's
audit a machine can run — its subject being the other repositories rather
than this tree.

## The primary checkout is the maintainer's

**Never work in it.** No edit, no `git add`, no commit, no branch
switch, no rebase, no `git stash` — the hooks fix files in place. It is a
local reference only, and it stays on `main`.

Reading it is fine, but `git fetch` moves `refs/remotes/origin/main` and
leaves the work tree where it was, so a `grep` or a `Read` against the
checkout answers for whenever it was last brought forward, not for now.
The read that cannot go stale is `git show origin/main:<path>`: it
answers from the ref `git fetch` just moved, never from the tree.

Where the checkout has to be current rather than merely readable, a
fast-forward of a clean `main` brings it up:

```shell
git fetch origin && git merge --ff-only origin/main
```

That writes no commit, switches no branch and runs no hook, so it is on
the permitted side of *never work in it*, not an exception to it. Stop
if the checkout is not on `main` or is not clean: that is no longer
bringing it forward.

**Every session works in a worktree**, its own, from the first edit,
named `wt-<tracker>-<issue>-<repo>-<role>` rather than after the issue
alone, most general part first: an issue filed in this tracker is the
key and the repository is a detail of it — `#255` is one issue owed by
seven repositories, `#177` by two — so the repository is what varies
underneath an issue rather than the other way round, which is why
`repo` comes after `issue`. Naming it that way also sorts every
worktree of one issue together, which is what a port leaves behind.

Each of the four parts earns its place against a different collision,
and none of them is the same collision. `tracker` is the repository
whose issue tracker holds the issue: an issue number is unique only
within one tracker, so `btclib-org/.github#45` and
`btclib-org/btclib#45` are different issues that would otherwise name
the same worktree. `issue` is what prevents the collision that has
actually happened — two worktrees of different work sharing a generic
basename in one repository's own `.git`, keyed on its path's basename,
which is what `wt-review` hit. `repo` prevents a different collision, a
*path* one rather than a `.git` one: two repositories each keep their
own `.git/worktrees/<basename>` and cannot collide there, but the
workers of one session share one scratchpad directory, so a session
carrying one issue into several repositories computes the same target
path for each of them, and `git worktree add` refuses a directory that
already exists — or worse, a second worker reads the first one's tree.
`role` covers the narrower case of a coder and its reviewer holding a
worktree at once, which the ordinary sequence avoids by each removing
its own.

An issue of this tracker worked in `btclib` by a coder names its
worktree `wt-github-255-btclib-coder`. No `uv sync` follows the `cd`,
the gate doing that itself, and the editing, the gates and the commits
all happen in the worktree before the push.

```shell
WT=<scratchpad>/wt-<tracker>-<issue>-<repo>-<role>
git worktree add "$WT" origin/main -b <branch>
cd "$WT"
git push origin HEAD:refs/heads/<branch>
```

`-b <branch>` sits after the path and the commit-ish so that the
placeholder ends the command, which is section 9 of `README.md`'s rule.
With the placeholder ahead of `"$WT"` the `>` closing it takes that path
as its target, and a path with no directory at it is a file the paste
creates.

Removing the worktree is part of finishing, and it stands in a block of
its own: the block above ends in a placeholder, and a shell that
discards that line as a parse error reads the next as a fresh command —
which, in one block, is this line against whatever `$WT` already held.
Standing alone it is a second fence, so `${WT:?}` is what it writes:
with no `$WT` set the expansion fails and the removal does not run.

```shell
git worktree remove --force "${WT:?}"
```

**Never `git stash` in a worktree either: `refs/stash` is shared.** A
worktree isolates files, not refs, so `git stash push` pushes onto the
same stack every other session pops from. Commit to your own branch
instead.

**Do not rewrite `refs/heads/main`, or advance it with work that is not
yours.** Your own branch is what you push, and the pull request is what
moves `main`.

## Model

The default model for this repository is Sonnet. Switch to Opus only for
a change to what the standard *says* — a convention two repositories
disagree about, a rule whose rejected alternative has to be weighed. Use
`/model opus` for the session, then switch back.

**A port of one file into every repository is that case, and reads as
though it were not.** The work looks mechanical — the same edit,
repository by repository — and the decision it rests on is what the
standard says, because trees that each derive the rule for themselves
land different answers and the tracker gets an issue per divergence. What
settles it is one sentence here, written before the ports go out rather
than after; a campaign that starts on Sonnet discovers mid-flight that
it is rewriting a section, with branches already pushed against the
answer it had then.

Do not use Fable unless explicitly instructed.

## Non-obvious facts that will otherwise waste a session

- **`pyproject.toml` is not a distribution's.** `package = false`, no
  build backend and no wheel, so of section 3 it declines the metadata
  only an index reads and declares what binds the `[project]` table —
  `authors` and `keywords` — with the reason at the key. Section 14
  names the files kept by the gate's tools that do not look in
  `pyproject.toml` for their configuration. A word this file's own
  prose needs — `CPY`, ruff's copyright rule — is a typo to the spell
  checker until `[tool.typos]` names it, with the reason beside it.
- **The suite's subject is the other repositories, and there is no
  coverage**: what it would measure is a tree that ships nothing, so the
  number would be the suite measuring itself. What it cannot reach — a
  claim in this file or in `README.md` that no command re-derives — a
  reader catches or nothing does. That fact's operational half:
  `tests/conftest.py` sets `SWITCH = "BTCLIB_INTEGRATION"`, its own
  docstring calling it "the environment variable without which this
  suite skips itself." A bare `uv run pytest` syncs `dev` — uv's default
  group, which `[tool.uv]` overrides nowhere and which reaches `test` —
  collects the suite, skips every test for want of the switch and exits
  0, with nothing measured. *Verifying*, further down this file, says to
  trust the exit code over the filtered output — here the exit code is
  the half that lies, and `BTCLIB_INTEGRATION=1` is what a run needs
  before that trust is earned. `alignment.yml` carries the whole
  command, with the reason for its `--no-default-groups` beside it.
- **A `BACKLOG` row's red is often a sibling's success.** Its rows in
  `tests/__init__.py` are `xfail(strict=True)` and keyed on this
  tracker's issue numbers, while the trees they name move underneath
  them: when another repository lands the fix a row excuses, the cell
  starts passing and the strict xfail turns that success into a failure
  here, with nothing in this tree having changed. That is the mechanism
  working — it is what forces an expired exemption to be noticed rather
  than left to rot — and the question it raises, *is this mine*, is
  answered by two commands: `git diff origin/main..HEAD -- tests/`
  empty says the branch did not cause it, and the same run in a second
  worktree at `origin/main` says it was already red before the branch
  existed. A `git archive` snapshot cannot stand in for that worktree:
  it has no `.git`, and `tests/__init__.py`'s `tracked` runs
  `git ls-files` in the tree under test, so the cells that read a tree
  through it are red there for the method's reason and not the tree's.
- **`profile/README.md` is public in a way no other file here is**: it
  is what github.com/btclib-org renders. Treat a change to it as a change
  to the organization's front page, because it is one.
- **The community health files are inherited, not copied.**
  `CODE_OF_CONDUCT.md`, `SECURITY.md`,
  `.github/PULL_REQUEST_TEMPLATE.md` and `.github/ISSUE_TEMPLATE/` here
  are what GitHub shows for a *public* repository of the organization
  that has none of its own, and section 2 of `README.md` is what says
  which repositories have one. The inheritance is display only: nothing
  is written into those repositories and no hook reads it, so a
  repository that wants the file gated keeps its own. A change here is a
  change to what a reader of every repository inheriting it sees.
- **A branch touching the shared half of `CONTRIBUTING.md` or `REVIEWING.md` —
  the text above `## This repository in particular` — owes
  `tests/verbatim_test.py`'s `EXPECTED_DRIFT` an entry and the issue it names,
  in the same diff.** Not `tests/__init__.py`'s `BACKLOG`, which excuses a
  whole test rather than one path. The precedent is `.gitattributes`:
  `90faad8` added the entry and `6bf5e5c` deleted it once the eighth tree
  converged, its message giving the reason — "a drift filed later still wants
  an entry here and not a row there".
- **A claim about "every tier-2 repository" has to hold of this tree too**,
  section 2 saying its own row is measured the same way as the others. `grep
  -c '^### A version, and no release' CONTRIBUTING.md`, run against every
  tier-2 repository including this one, is the check. `tests/` asks no
  such thing — this tree has no coverage, so a repository that drops the
  heading again is a reader's catch, not a red run.
- **Replacing `tests/conftest.py`'s per-session clone with `--reference`
  against the local checkouts was measured and declined:
  btclib-org/.github#272.** The shrunk clone still contacts the forge for the
  tip, so it removes no network dependency, and its object store is borrowed
  from a checkout that a `git gc` there can break — for a saving the issue's
  own numbers call not worth the hazard. `git grep -lE 'gh_json|settings:
  dict' tests/*_test.py` names `grid_test.py`, `homepage_test.py`,
  `protection_test.py`, `security_test.py`, `settings_test.py`,
  `tags_test.py` and `topics_test.py` — what asks the API for state with
  no on-disk representation. `grid_test.py` asks it for one document and
  only where a calendar row is idle: the state of the issue section 10
  says carries that row's debt. `tiers` is not one of them:
  `tests/__init__.py`'s `tier()` reads `pyproject.toml` and `release.yml` off
  the checkout, which `tiers_test.py` asks through the `tiers` fixture —
  `conftest.py`'s one-liner over `trees` — rather than through `gh_json`.
- **A sibling tree's documentation build reads its `CHANGELOG.md`, so a
  changelog-only diff does not exempt the docs gate.** This tree has no
  `docs/`, but a session driven from this tracker runs the gates of the
  repository it is porting into, and in the five that have a
  documentation build — `btclib`, `btclib-secp256k1`, `btclib-node`,
  `btclib-benchmarks` and `bitcoin-core-rpc` — `docs/source/changelog_link.md`
  pulls `../../CHANGELOG.md` through a MyST `include` and the
  toctree lists it, under `-W`. `-C` puts `<checkout>` ahead of the read
  it names, so it cannot sit last as section 9 asks; the assignment
  stands in a block of its own, its own placeholder ending the line
  being the parse error a shell discards, reading the read below as a
  fresh command against whatever `$checkout` a paste has already set,
  which `${checkout:?}` refuses where a paste has set nothing:

  ```shell
  checkout=<checkout>
  ```

  ```shell
  git -C "${checkout:?}" grep -l 'include} \.\./\.\./CHANGELOG\.md' \
    origin/main -- docs/
  ```

  answers in each of the five and nothing in `.github`, `bbt` or
  `portanode`, which have no `docs/` at all; the same pattern against
  `README.md` answers in all five, which is the control saying the zero
  is an absence rather than a miss. The trap is that *`docs/` is
  unchanged* is a true sentence answering the wrong question: what
  decides is what the tool reads, not which of its inputs moved. Skipping
  the docs gate on that reasoning was caught by a reviewer, not by a run.

## Conventions to match

Section 9 of `README.md` is the prose style, and it governs this file and
the standard alike. It is not re-listed here, that section's own *One
fact in one place* being the reason. `CONTRIBUTING.md`'s *Pull requests*
has what a title does with the issue it closes, and its *The issue
tracker* has what an issue filed here may be about.

What is left to this file is what those cannot say, because it is about a
session rather than about the tree: the worktree rule, the model, the
failure modes in the section that names them, and what this tree is.

## Verifying

Run the command as documented before claiming it works, and read its exit
code rather than its filtered output, for the reason `CONTRIBUTING.md`'s
*This repository in particular* gives. Every claim in this file was
checked against the tree, and the tree changes.
