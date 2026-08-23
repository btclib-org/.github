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

Nothing here is installed, imported or released. What this repository
ships, it ships by being read.

## The primary checkout is the maintainer's

**Never work in it.** No edit, no `git add`, no commit, no branch
switch, no rebase, no `git stash` — the hooks fix files in place. Reading
it is fine, and so is `git fetch`, which writes refs and leaves the work
tree alone.

**Every session works in a worktree**, its own, from the first edit:

```shell
WT=<scratchpad>/wt<issue>
git worktree add -b <branch> "$WT" origin/main
cd "$WT"                              # no uv sync: the gate does it
# edit, gate and commit here, then
git push origin HEAD:refs/heads/<branch>
git worktree remove --force "$WT"     # removing it is part of finishing
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

Do not use Fable unless explicitly instructed.

## Non-obvious facts that will otherwise waste a session

- **`pyproject.toml` is not a distribution's.** `package = false`, no
  build backend and no wheel, so section 3 describes a file this one is
  not. The tools that read a `pyproject.toml` are configured in it, and
  the ones that do not keep files of their own: `.taplo.toml`,
  `.yamllint.yaml`, `.markdownlint.jsonc`. A word this file's own prose
  needs — `CPY`, ruff's copyright rule — is a typo to the spell checker
  until `[tool.typos]` names it, with the reason beside it.
- **The suite's subject is the other repositories, and there is no
  coverage**: what it would measure is a tree that ships nothing, so the
  number would be the suite measuring itself. What it cannot reach — a
  claim in this file or in `README.md` that no command re-derives — a
  reader catches or nothing does.
- **`profile/README.md` is public in a way no other file here is**: it
  is what github.com/btclib-org renders. Treat a change to it as a change
  to the organization's front page, because it is one.
- **The community health files are inherited, not copied.**
  `CODE_OF_CONDUCT.md` and `PULL_REQUEST_TEMPLATE.md` here are what
  GitHub shows for a *public* repository of the organization that has
  none of its own. Nothing is written into those repositories, no hook
  reads it, and a repository that wants the file gated keeps its own —
  so a change here changes what a reader sees on repositories nobody is
  looking at.

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
