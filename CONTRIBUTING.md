# Contributing

`README.md` in this repository is the
[btclib-org repository standard](./README.md): what every repository of
the organization is built and kept to, each rule with the alternative it
was decided against. A sibling's `CONTRIBUTING.md` links out to it; this
one is written inside it, so where a rule below is the standard's, the
section number is given rather than the rule restated.

Read `README.md` before changing it. Most of what a session here wants to
add is already in it, with the rejected alternative beside it.

## The environment

uv is the only thing that has to be installed; it fetches interpreters
and tools itself. There is a project here, and nothing installs it:
`package = false`, its only Python being one test suite.

## The gates

```shell
uvx pre-commit run --all-files          # the whole gate
uvx pre-commit run markdownlint-cli2    # one hook
uvx pre-commit validate-config .pre-commit-config.yaml
```

`uvx` and not the `uv run` a sibling's lint job uses, and `lint.yml` runs
this same command: a workflow invoking pre-commit some other way is the
second declaration section 4 refuses, one version behind the author's or
ahead of it. The last one is worth running before pushing a change to the
hook config — it catches what a wrong `types_or` tag or a malformed entry
would otherwise turn into a red lint job.

**Check exit codes, not filtered output.** `pre-commit run ... | grep -v
Passed` hides a failure, and `grep` finding nothing exits 1, which is not
the gate's answer to anything.

**The gate is not installed as a git hook.** `pre-commit install` writes
into the common git directory, which every worktree of this repository
shares: `git -C <worktree> rev-parse --git-path hooks` answers with the
maintainer's checkout. So one session installing it installs it for every
other. Run the gate by hand before committing.

The suite is a second thing and not a gate. It asks the organization what
no single repository can ask itself, it reaches GitHub to do so, and it
skips itself unless `BTCLIB_INTEGRATION` is set. `alignment.yml` carries
the command it runs; a copy of that command here would be the line that
goes stale first.

## What gates a merge, and what only reports

`lint.yml`'s job is the required check and is the whole of what a merge
is gated on; `REPOSITORY.md` reads the rule back from the endpoint rather
than restating it.

Everything else reports. `alignment.yml` is a sentinel: what it finds is
drift that happened days ago in a repository nobody is working in, and an
API that is down is nothing a pull request introduced. `links.yml` asks
whether somebody else's server answered. `claude-review.yml` writes the
review and its own header says it must not become a required check —
requiring it would make a review a gate to satisfy rather than a reading
to answer.

## The issue tracker

**An issue belongs here when closing it means touching more than one
repository, or when its subject is the standard itself.** An issue about
one repository's own files, workflows or settings belongs in that
repository, even when the defect was found while working on the standard.

**An alignment finding names the repositories it is about and the command
that re-derives it**, and stays open until every one of them answers.
That is what an issue filed here can do and one filed on a single
repository cannot.

A finding noticed while doing something else is filed, not carried: a
pull request that answers two questions cannot be accepted for either.

## Documentation and comments

The house style of btclib-org, in one line: a comment says *why*, never
*how it got here*. Present-tense reasoning, **including the negative
result** — what was tried, what it measured, why it was not taken — is
what makes a file reviewable. History belongs in `CHANGELOG.md`.

**Measure rather than assert.** A claim that no command re-derives is the
defect this organization writes down most often, and section 15 carries
the commands that answer with today's number. Where a claim is worth
making, the command that re-derives it goes beside it.

**Never state how many of anything a file holds.** A stated count is a
line every open branch has to edit, and nothing here checks one. It is
also what `merge=union` keeps both of, silently, when two branches edit
it.

**One fact in one place.** A rule stated in two files is two things to
keep true, and the second wording is the one that goes stale. Point at
the file that owns the fact.

Markdown wraps at 80 columns, tables included — MD013 is on — so a long
command goes in a fenced block split with `\`. A line holding nothing but
an unbreakable URL is exempt.

A bare `#123` resolves only inside the repository it is written in, so a
reference to another one is `owner/repo#123`. The exemption is mechanical:
a pull request's closing keyword is read by the forge and takes the
forge's own reference.

## Pull requests

`main` is the only branch and takes a pull request and nothing else, a
direct push being refused for everyone. Run the gate locally first: CI
runs exactly it, so a red run there is a local run that was not done.

A pull request answers one subject. **One that closes an issue names it
in its title, in parentheses; one that closes nothing carries no
parentheses** — the title becomes the landing commit's subject,
`squash_merge_commit_title` being `COMMIT_OR_PR_TITLE`. The body carries
the forge's closing keyword for what it closes.

`CHANGELOG.md` gets an entry for anything a reader would notice.

**A correction is a commit of its own, never an amend.** A force-push
replaces the commits a review is attached to; the one force-push that
stays right is a rebase carrying no new work.

### The review

`REVIEWING.md` is the standard a review is written against, and is this
file's other half. Section 11 of the standard says which review is the
one a landing reads: the **ack of record**, a comment whose last line
names the sha it acks. A reading that delivers no verdict is a review
too, and `REVIEWING.md` says why.

### Landing it

The rule is one approving review, and the maintainer is a bypass actor in
`pull_request` mode. **The bypass is not automatic — it has to be
invoked, and `gh pr merge` cannot invoke it**, refusing client-side
before it asks GitHub anything:

```text
Pull request is not mergeable: the base branch policy prohibits the merge
```

The merge endpoint applies the bypass server-side, and it is the same
endpoint the merge button asks. Squash is the only method:

```shell
gh api -X PUT repos/btclib-org/.github/pulls/<n>/merge \
  -f merge_method=squash
```

**Verify what landed rather than trusting the answer.** GitHub composes
the squash commit itself and signs it with its web-flow key, which is a
valid signature and all `main-integrity` asks for — a landing that went
another way may not be:

```shell
gh api repos/btclib-org/.github/commits/main \
  --jq '.commit.verification | {verified, reason}'
```

`delete_branch_on_merge` is on, so the head branch goes by itself. What
is still yours is bringing every checkout sitting on `main` up to date,
that being where the next session starts from.
