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

**An issue belongs to a repository when closing it means touching that
repository and no other.** One that spans repositories, or whose subject
is the standard itself, is filed in
[btclib-org/.github](https://github.com/btclib-org/.github/issues): a
difference between two repositories belongs to neither of them, and filed
once per repository it is copies that do not know about each other.

**An issue says how it was measured**, and a finding names the command
that re-derives it. A finding about several repositories names each of
them, and stays open until every one answers.

A finding noticed while doing something else is filed, not carried: a
pull request that answers two questions cannot be accepted for either.
Look for the issue already open before filing another.

## Documentation and comments

The house style of btclib-org, in one line: a comment says *why*, never
*how it got here*. Present-tense reasoning, **including the negative
result** — what was tried, what it measured, why it was not taken — is
what makes a file reviewable. History belongs in `CHANGELOG.md`.

**Measure rather than assert.** A claim that no command re-derives is the
defect this organization writes down most often. Where a claim is worth
making, the command that re-derives it goes beside it.

**Never state how many of anything a file holds.** A stated count is a
line every open branch has to edit, and nothing checks one. It is also
what `merge=union` keeps both of, in silence, when two branches edit it.

**One fact in one place.** A rule stated in two files is two things to
keep true, and the second wording is the one that goes stale. Point at
the file that owns the fact rather than restating it.

Markdown wraps at 80 columns, tables included — MD013 is on — so a long
command goes in a fenced block split with `\`. A line holding nothing but
an unbreakable URL is exempt.

**A reference to another repository is qualified.** A bare `#123`
resolves inside the repository it is written in, so a cross-repository
reference is `owner/repo#123` or it points somewhere else in silence. The
one exemption is mechanical: a pull request's closing keyword is read by
the forge, so it takes the forge's own form.

## Pull requests

`main` is the only branch and takes a pull request and nothing else, a
direct push being refused for everyone. Run the gates locally first — the
section above says which they are — because CI runs exactly them, so a
red run there is a local run that was not done.

`REVIEWING.md` is the standard a review is written against, and is this
file's other half. Read before opening a pull request, it is what the
pull request will be answered against.

`CHANGELOG.md` gets an entry for anything a reader would notice, and the
release notes move only for something a user has to *act* on, in the
repositories that publish.

### One subject, opened as soon as it is written

A pull request answers one question. Issues that share a subject are one
pull request, closing each of them; issues that do not are one pull
request each, however small either of them is.

**One that closes an issue names it in its title, in parentheses; one
that closes nothing carries no parentheses.** The title becomes the
landing commit's subject, `squash_merge_commit_title` being
`COMMIT_OR_PR_TITLE`. The body carries the forge's closing keyword.

It is opened the moment it is written and verified — not held for the
previous one to be reviewed or to land, and not batched with the next. A
batch arrives as one reviewing job with several subjects, which is the
shape that costs the most to read; a finished pull request held back is
review that could have started and did not.

Working this way stacks branches, which is fine and costs one rule: a
child whose base was amended is moved with the old base named,

```shell
git rebase --onto <new-base> <old-base-sha> <child>
```

because a plain rebase replays the base's old commit inside the child,
and the forge then shows the base's old text as additions with nothing
red anywhere. Read the child's diff afterwards rather than trusting the
rebase, and retarget each child onto `main` as its parent lands.

**A correction is a commit of its own, never an amend.** A force-push
replaces the commits a review is attached to; the one force-push that
stays right is a rebase carrying no new work.

### The review

A review is given promptly and on local evidence. It does not wait for
CI, does not report a check as a finding, and does not discuss a run at
all: whether CI is green is the author's business, once, at landing time.

The exchange is anchored to a sha rather than to a branch, a branch being
free to move under a review:

- the author hands off by naming the sha pushed and the evidence run
  against it, then leaves that head alone;
- the reviewer answers with findings — where, what is wrong, how they
  know it, and whether each is blocking;
- the author accepts what is reasonable, declines the rest with a reason
  in the thread, and pushes the answer without waiting for CI;
- the reviewer resolves the threads they opened, that being what says a
  finding is closed, and re-reviews the delta rather than the branch.

**What ends the loop is the ack of record**, a comment whose last line
names the sha it acks, and the author does not supply their own. A
reading that says what it found and delivers no verdict is a review too
and ends nothing; `REVIEWING.md` has both, and why they are not the same
thing. A disagreement that survives a second exchange goes to the
maintainer instead of into a third round.

### Landing it

CI is read once, and this is where. Rebase onto `main`'s tip, push that
head so the checks run on the tree that will land, and only then wait for
them: checks read before a rebase describe a tree nobody is landing. A
rebase that moved nothing but the base leaves the ack standing; one that
resolved a conflict does not, that resolution being a change no reviewer
has seen.

Then squash, which is the only method the rule accepts. The forge
composes the commit and signs it with its own key, and that is what the
rule asks for: a valid signature, not a particular signer's.

**The maintainer's bypass is not automatic — it has to be invoked, and
`gh pr merge` cannot invoke it**, refusing client-side before it asks
GitHub anything:

```text
Pull request is not mergeable: the base branch policy prohibits the merge
```

The merge endpoint applies it server-side, and it is the same endpoint
the merge button asks:

```shell
gh api -X PUT repos/{owner}/{repo}/pulls/<n>/merge \
  -f merge_method=squash
```

**Verify what landed rather than trusting the answer:**

```shell
gh api repos/{owner}/{repo}/commits/main \
  --jq '.commit.verification | {verified, reason}'
```

`delete_branch_on_merge` is on, so the head branch goes by itself. What
is still yours is bringing every checkout sitting on `main` up to date,
that being where the next session starts from and a stale one being where
a branch gets built on a base that has moved. `REPOSITORY.md` carries the
settings and why they are what they are.
