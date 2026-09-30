# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working
with code in this repository.

`README.md` is the standard every btclib-org repository is built and
kept to, and the issue tracker is where a repository's drift from it is
filed and worked off. Read `README.md` before changing it: most of what
a session here wants to add is already in it, with the alternative that
was rejected beside it.

How to work here — what the issue tracker takes, the prose style, and
how a pull request is opened and landed — is `CONTRIBUTING.md`, which is
the same file in every repository of the organization up to its last
section, which is this tree's and holds the commands and the gates.
Repository configuration is `REPOSITORY.md`: read it before changing a
workflow, a branch rule or a setting. Reviewing is `REVIEWING.md`, and
`/review` is that file as a command; read it before reviewing a pull
request and before opening one, since it is what the pull request will be
answered against.

## Architecture

`README.md` is the standard and the product: a change to it is a change
to what every other repository is measured against. `profile/README.md`
is the organization's page, `REPOSITORY.md` is this repository's own
settings read back from the endpoint, `tests/` is the half of section
15's audit a machine can run — its subject the other repositories — and
`.github/scripts/` the scripts this tree's hooks and the reusable
workflows run.

## The primary checkout is the maintainer's

Never work in it: no edit, no `git add`, no commit, no branch switch, no
rebase, no `git stash` — the hooks fix files in place. The one write
allowed there brings it forward, and only while it is on `main` and
`git status --porcelain` prints nothing; where it is not, stop:

```shell
checkout=<checkout>
```

```shell
git -C "${checkout:?}" pull --ff-only
```

Read it only after that, once `git -C <checkout> rev-parse HEAD
origin/main` prints one sha twice. A measurement that has to hold at a
named revision reads `git -C <checkout> show <sha>:<path>` instead.

Every session works in a worktree of its own, from its first edit, named
`wt-<tracker>-<issue>-<repo>-<role>` — `wt-github-255-btclib-writer` for
issue 255 of `btclib-org/.github`'s tracker, worked in `btclib` by a
writer. The environment is created there, with the command `CONTRIBUTING.md`
names under *The environment and the gates*. Every path is written out in
full:

```shell
git worktree add \
  <scratchpad>/wt-<tracker>-<issue>-<repo>-<role> origin/main -b <branch>
```

Removing it is part of finishing:

```shell
git worktree remove --force <scratchpad>/wt-<tracker>-<issue>-<repo>-<role>
```

`refs/stash` and the local `main` are shared by every worktree: never
`git stash`, and move `main` only by the fast-forward above.

## Model

Default model: Sonnet. Opus for a change to what the standard *says* — a
convention two repositories disagree about, a rule whose rejected
alternative has to be weighed — and for a port of one file into every
repository, which looks mechanical and rests on that decision: settle it
in one sentence here before the ports go out. Do not use Fable unless
instructed.

## Non-obvious facts that will otherwise waste a session

- **`pyproject.toml` is not a distribution's.** `package = false`, no
  build backend and no wheel, so of section 3 it declines the metadata
  only an index reads and declares what binds the `[project]` table —
  `authors` and `keywords` — with the reason at the key. Section 14
  names the files kept by the gate's tools that do not look in
  `pyproject.toml` for their configuration. A word this file's own
  prose needs — `CPY`, ruff's copyright rule — is a typo to the spell
  checker until `[tool.typos]` names it, with the reason beside it.
- **There is no coverage: the suite's subject is the other repositories,
  and coverage here would measure the suite itself.** A bare `uv run pytest`
  skips every `integration` test — every alignment question — unless
  `BTCLIB_INTEGRATION=1` is set (`tests/conftest.py`'s `SWITCH`);
  `alignment.yml` has the full command.
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
- **`tests/verbatim_test.py`'s `EXPECTED_DRIFT` takes an entry where the
  copies converge by a landing the branch cannot make** — a port going out
  tree by tree. Where the fix is an edit of the branch's own, make the edit
  instead. An entry takes its path out of the comparison while it stands;
  its docstring says when it is deleted.
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
  own numbers call not worth the hazard. `git grep -lE
  'gh_json|still_open|settings: dict|"gh"|(^|[^_[:alnum:]])gh\('
  tests/*_test.py` names what asks the API for state with no on-disk
  representation. `still_open` is in the pattern because it is the read
  rather than a caller of one: it lives in `tests/__init__.py`, so a file
  reaching the API through it names neither `gh_json` nor a settings dict,
  and a pattern without it answers a confident zero for that file. `"gh"` is
  in the pattern because `pyproject_test.py`'s `dockerfile()` calls `gh`
  directly rather than through `gh_json`, and a pattern without it answers a
  confident zero for that file too. `gh(` is in the pattern because
  `vex_test.py` calls `tests/__init__.py`'s `gh` for the dismissed alerts,
  and a pattern without it answers a confident zero for that file as well;
  a bracket expression bounds it because `\b` in its place answers zero
  under Apple Git's `git grep -E`. `tiers` is not among what the
  command names: `tests/__init__.py`'s `tier()` reads `pyproject.toml`
  and `release.yml` off the checkout, which `tiers_test.py` asks through
  the `tiers` fixture — `conftest.py`'s one-liner over `trees` — rather
  than through `gh_json`.
- **A sibling tree's documentation build reads its `CHANGELOG.md`, so a
  changelog-only diff does not exempt the docs gate.** In every tree with
  a documentation build, `docs/source/changelog_link.md` includes
  `../../CHANGELOG.md`, under `-W`. The assignment stands in a block of
  its own, `${checkout:?}` refusing a paste that set nothing:

  ```shell
  checkout=<checkout>
  ```

  ```shell
  git -C "${checkout:?}" grep -l 'include} \.\./\.\./CHANGELOG\.md' \
    origin/main -- docs/
  ```

  answers where.
- **The alignment suite is what validates a new repository, and a local
  review is not a substitute for running it.** `tests/conftest.py`'s
  `trees` fixture clones every repository shallow and tagless at the tip of
  the default branch, whatever it is named. And for as long as a sibling
  repository exists and is empty, `alignment.yml` is red here on every
  branch of this tree — a cost every session working here pays for the gap
  between `gh repo create` and that sibling's first push.
- **A new repository's rulesets go on only after its first push to
  `main`, never before — section 16 states the reason.** Verify it
  against a landed repository rather than trusting the order alone:
  `gh api repos/<owner>/<repo>/rulesets/<id> --jq .created_at` against
  the root commit's own `commits/<sha>` date. `bitcoin-node-tests` and
  `btclib-wallet` both agree, their rulesets created after their own root
  commit had already landed.
- **The first branch ever pushed to an empty repository becomes its
  `default_branch`, whatever it is named — section 16 states the reason
  the setting is made explicit.** The corollary is what makes a tree
  buildable before it has a `main` at all: a workflow's trigger has only
  to exist on whichever branch is currently default, so
  `gh workflow run <file>.yml --ref <branch>` dispatches it against a
  build branch well before anything has landed.
- **A Dependency Graph job runs only on a push that changes the manifest
  it reads.** Its runs are the `event=dynamic` ones whose title
  carries `Graph Update:`, and in `btclib` the `uv in /.` job follows
  `pyproject.toml` and `uv.lock` while the `pip in /.clusterfuzzlite` job
  follows that directory's `requirements.txt`. So a fix to how the graph
  reads a directory that leaves the manifest alone starts no run at
  landing, the newest run shown is still the failure it fixes, and nothing
  before the next change to that manifest can verify it —
  [the command for the pip job](https://github.com/btclib-org/.github/issues/1436#issuecomment-5899176660).

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
