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

## Commands

uv is the only tool that must be installed.

```shell
uvx pre-commit run --all-files          # the whole gate
uvx pre-commit run markdownlint-cli2    # one hook
uvx pre-commit validate-config .pre-commit-config.yaml
```

That last one is worth running before pushing a change to the hook
config: it catches what a wrong `types_or` tag or a malformed entry
would otherwise turn into a red lint job. `jsonc` is not a tag `identify`
knows, which is why the prettier hook selects by path.

The suite skips itself unless `BTCLIB_INTEGRATION` is set, this being
the one suite in the organization that reaches the network on purpose.
`alignment.yml` carries the command it runs, and what the suite asks is
in `tests/`: it is still being written, so a copy of either here is the
line that goes stale first.

**Check exit codes, not filtered output.** `pre-commit run ... | grep -v
Passed` hides a failure, and `grep` finding nothing exits 1, which is not
the gate's answer to anything.

## What is different here, and will otherwise waste a session

- **`pyproject.toml` is not a distribution's.** `package = false`, no
  build backend and no wheel, so section 3 describes a file this one is
  not. The tools that read a `pyproject.toml` are configured in it, and
  the ones that do not keep files of their own: `.taplo.toml`,
  `.yamllint.yaml`, `.markdownlint.jsonc`. A word this file's own prose
  needs — `CPY`, ruff's copyright rule — is a typo to the spell checker
  until `[tool.typos]` names it, with the reason beside it.
- **The suite's subject is the other repositories, and there is no
  coverage**: what it would measure is a tree that ships nothing, so the
  number would be the suite measuring itself. A claim in this file or in
  `README.md` that no command re-derives is the defect this organization
  writes down most often, and a reader is what catches the ones no test
  reaches.
- **`lint.yml` runs those hooks on every pull request, and its job is
  the required check**, which `REPOSITORY.md` reads back from the
  endpoint. It is the only one, so the hooks are the whole of what a
  merge is gated on. `alignment.yml` is a sentinel and not a gate, for
  the reason its own header gives — an API that is down is nothing a
  pull request introduced — `links.yml` gates nothing, weekly and on a
  change to itself, and `claude-review.yml` gates nothing either. So a
  review may rely on the lint gate rather than running it again,
  `README.md`'s Review section having what the reliance takes.
- **The lint gate is not installed as a git hook.** `pre-commit
  install` writes into the common git directory, which every worktree
  shares: `git -C <worktree> rev-parse --git-path hooks` answers with
  the maintainer's checkout. So a session installing it installs it in
  the tree the section below says never to work in, and in every other
  session's worktree at once. Run the gate by hand before committing.
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

## How a pull request lands

`main` takes a pull request and nothing else: `main-self-merge` requires
an approving review, and the maintainer is a bypass actor in
`pull_request` mode. Squash is the only method.

**The bypass is not automatic — it has to be invoked, and `gh pr merge`
cannot invoke it.** That command refuses client-side, before it asks
GitHub anything:

```text
Pull request is not mergeable: the base branch policy prohibits the merge
```

The merge endpoint applies the bypass server-side, and it is the same
endpoint the merge button asks:

```shell
gh api -X PUT repos/btclib-org/.github/pulls/<n>/merge \
  -f merge_method=squash
```

**Verify what landed rather than trusting the answer**: GitHub composes
the squash commit itself and signs it with its web-flow key, which is a
valid signature and all `main-integrity` asks for — but a landing that
went another way may not be.

```shell
gh api repos/btclib-org/.github/commits/main \
  --jq '.commit.verification | {verified, reason}'
```

`delete_branch_on_merge` is on, so the head branch goes by itself; the
worktree does not, and removing it is still yours to do.

## Model

The default model for this repository is Sonnet. Switch to Opus only for
a change to what the standard *says* — a convention two repositories
disagree about, a rule whose rejected alternative has to be weighed. Use
`/model opus` for the session, then switch back.

Do not use Fable unless explicitly instructed.

## Conventions to match

- **The prose style is `CONTRIBUTING.md`'s "Documentation and comments"
  section, in every sibling repository**: neutral, factual, dry; a
  comment carries the reasoning *including the negative result*; measure
  rather than assert; one fact in one place; no history in the prose.
  It governs this file and the standard alike.
- **Markdown wraps at 80 columns**, tables included (MD013 is on), so
  long commands go in fenced blocks split with `\`.
- **Never state how many of anything a file holds.** A stated count is a
  line every open branch has to edit, and nothing here checks one.
  `README.md`'s section 15 has the commands that answer with today's
  number, whenever one is wanted.
- **A pull request that closes an issue names it in its title, in
  parentheses**; one that closes nothing carries no parentheses. The
  title becomes the landing commit's subject, `squash_merge_commit_title`
  being `COMMIT_OR_PR_TITLE`.
- **An alignment finding names the repositories it is about and the
  command that re-derives it**, and stays open until every one of them
  answers. That is what an issue filed here can do and one filed on a
  single repository cannot.
