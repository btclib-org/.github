# Repository configuration

What is set on this repository, as the `gh api` call that reads it back
and the answer that call gives today. A setting recorded as prose alone
is one nobody can check; recorded this way, a drift is one command away
from being seen.

`README.md` section 11 says every repository writes its settings down
here, and until now this was the repository with nowhere to read its own
back — the one holding the standard being the one exempt from it.

The rules and the settings live *outside* the tree, so this file is the
whole of them: nothing below is recoverable by reading the repository.

## Required checks on main

```shell
gh api repos/btclib-org/.github/branches/main/protection \
  --jq '.required_status_checks | {strict, checks: [.checks[].context]}'
# gh: Branch not protected (HTTP 404)
```

There is no classic protection here, so nothing waits on a check. The
rulesets below enforce the signatures and the review; classic protection
is where the required checks live, per section 16 step 12, and it is what
this repository has yet to grow. `lint.yml` is what a rule will name:

| Check | Produced by |
| --- | --- |
| `Lint` | `lint.yml`'s only job |

`lint.yml` has one job, so that job is the context — section 10's rule
that a workflow whose whole answer becomes required needs an aggregate
applies to a matrix, and there is none here. A context is keyed by name
alone, and the name is not the sibling repositories' `Lint and
type-check`: there is no Python in this tree and no mypy hook in
`.pre-commit-config.yaml`, so that name would promise a check nobody
runs.

**`links.yml` is not a required check and must not become one.** It asks
whether somebody else's server answered, which is a question a merge
cannot depend on; its own header carries the reasoning.
`claude-review.yml` is not one either, for the reason section 11 gives:
requiring it would make a reading into a gate.

A check context cannot be bound before a workflow has produced it, so
`lint.yml` runs first and the rule follows. Creating the protection is
one call, and it carries the whole object because there is none to patch
— every field of it, since a `PUT` sets what it is given and clears what
it is not:

```shell
gh api -X PUT repos/btclib-org/.github/branches/main/protection \
  --input - <<'JSON'
{"required_status_checks": {"strict": true,
   "checks": [{"context": "Lint", "app_id": 15368}]},
 "enforce_admins": false,
 "required_pull_request_reviews": {"dismiss_stale_reviews": true,
   "required_approving_review_count": 1},
 "restrictions": null,
 "required_linear_history": true,
 "allow_force_pushes": false,
 "allow_deletions": false,
 "required_conversation_resolution": true}
JSON
```

`enforce_admins` is false and has to be: it is what clears the *classic*
review requirement for the maintainer, the ruleset bypass reaching only
the ruleset's own rule, and turning it on would deadlock every solo
merge.

The `checks` array and a JSON body on stdin, never `contexts` and never
`-f`: `contexts` has no field for an app, so sending it replaces a bound
list with an unbound one and says nothing, and `-f` sends `app_id` as a
string, which the endpoint refuses. `15368` is the Actions app, and a
check bound to it cannot be reported by anything else. Once the object
exists, a later change to the list is a `PATCH` of
`/required_status_checks` — a partial `PUT` of the whole object would
drop the reviews with it.

## Branch protection and the rulesets

`main` is the only branch, and everything reaches it through a pull
request. With no classic protection, the rulesets are the whole of what
holds — rules aggregate across rulesets and classic protection, the most
restrictive combination winning wherever they overlap, so adding the
required check above changes nothing below:

```shell
gh api repos/btclib-org/.github/rulesets --jq '.[].id' \
  | xargs -I{} gh api repos/btclib-org/.github/rulesets/{} \
    --jq '{name, target, enforcement, rules: [.rules[].type],
           bypass: [.bypass_actors[]?.bypass_mode]}'
# {"bypass":[],"enforcement":"active","name":"main-integrity",
#  "rules":["required_signatures","required_linear_history",
#           "non_fast_forward","deletion"],"target":"branch"}
# {"bypass":["pull_request"],"enforcement":"active",
#  "name":"main-self-merge","rules":["pull_request"],"target":"branch"}
```

- `main-integrity` — required signatures, required linear history, no
  force pushes, no deletions — with **no bypass actor at all**, which is
  what makes every one of those true of an administrator too.
- `main-self-merge` — a pull request, an approving review, stale reviews
  dismissed on push, conversations resolved, and `squash` as the only
  merge method it accepts — bypassed by the maintainer in
  **`pull_request` mode**.

```shell
gh api repos/btclib-org/.github/rulesets --jq '.[].id' \
  | xargs -I{} gh api repos/btclib-org/.github/rulesets/{} \
    --jq '.rules[] | select(.type=="pull_request") | .parameters'
# {"allowed_merge_methods":["squash"],
#  "dismiss_stale_reviews_on_push":true,"require_code_owner_review":false,
#  "require_extra_approval_for_unattributed_changes":true,
#  "require_last_push_approval":false,"required_approving_review_count":1,
#  "required_review_thread_resolution":true}
```

**The bypass mode is the whole of the design.** `pull_request` excuses
its holder from the review rule *while merging a pull request* and at no
other time, which answers the one thing a solo-maintainer repository
cannot do — produce somebody else's approval — and answers nothing
further. A direct push to `main` is refused for everyone, the holder
included. `always` would permit that push and would buy nothing, the
signature rule asking for a valid signature rather than for a particular
signer.

There is no `tag-integrity` ruleset, and no `refs/tags/v*` for one to
target. What that ruleset buys the sibling repositories is a signed
release tag, otherwise the unattested link in a chain that is signed
everywhere else; nothing here is released, so there is no such link and
nothing for the rule to hold.

## Signed commits

```shell
gh api repos/btclib-org/.github/commits/main \
  --jq '.commit.verification | {verified, reason}'
# {"reason":"valid","verified":true}
```

`required_signatures` refuses an unsigned commit at the push rather than
noticing it afterwards, and with an empty bypass list it refuses one from
everybody. It asks for a valid signature and not for a particular signer,
so what lands from the merge button — a squash GitHub composes and signs
with its own web-flow key — satisfies it exactly as the maintainer's own
key does.

What no rule covers is a commit before it is pushed:
`git log -1 --format='%G? %GS'`, an `N` being a defect to fix rather than
to explain.

## Merge methods

```shell
gh api repos/btclib-org/.github \
  --jq '{squash: .allow_squash_merge, merge: .allow_merge_commit,
         rebase: .allow_rebase_merge, auto: .allow_auto_merge,
         delete_on_merge: .delete_branch_on_merge,
         title: .squash_merge_commit_title,
         message: .squash_merge_commit_message}'
# {"auto":true,"delete_on_merge":true,"merge":false,
#  "message":"COMMIT_MESSAGES","rebase":false,"squash":true,
#  "title":"COMMIT_OR_PR_TITLE"}
```

Squash only: one pull request is one commit on `main`, which
`required_linear_history` already implies and this makes unambiguous in
the dropdown GitHub preselects from whatever was used last. The ruleset
names the same method, so the constraint holds even if this setting is
flipped.

`COMMIT_OR_PR_TITLE` is why a pull request that closes an issue names it
in its title: that title becomes the landing commit's subject, so the
number reaches `git log` and stays reachable from a checkout with no
forge in front of it. `COMMIT_MESSAGES` puts the branch's own commit
messages in the body rather than the pull request's description.

`delete_branch_on_merge` fires on its own, every landing here being a
merged pull request, so a branch still standing is one that was closed
rather than merged.

## Features

```shell
gh api repos/btclib-org/.github \
  --jq '{wiki: .has_wiki, projects: .has_projects, issues: .has_issues,
         visibility: .visibility}'
# {"issues":true,"projects":true,"visibility":"public","wiki":true}
```

Issues are where this organization's cross-repository findings live, and
where they live *only*: a finding about several repositories filed on one
of them is invisible from the others.

Public matters more here than elsewhere. This repository supplies the
community health files GitHub shows for any public repository of the
organization that has none of its own, and it does that only while it is
public and named `.github`.

The wiki and the projects board are on, where the sibling repositories
turn both off — a wiki being a second place for documentation to go
stale, and this repository being documentation. That is a divergence
rather than a decision, and closing it is a settings change with no diff
to review.

## Token permissions

```shell
gh api repos/btclib-org/.github/actions/permissions/workflow
# {"default_workflow_permissions":"read",
#  "can_approve_pull_request_reviews":false}
```

`read`, which is what every workflow here needs: `lint.yml` and
`links.yml` read the tree, and `claude-review.yml`'s jobs elevate
themselves to `pull-requests: write` to post a comment and to
`id-token: write` for the OIDC token the action mints at startup. Nothing
publishes, attests or writes to the repository's contents.

`can_approve_pull_request_reviews` is false, and it matters as much as
the token: a run that can approve a pull request is a way around the one
rule that says somebody other than the author approves.

**What this call cannot say is whether that value is this repository's
own or the organization's.** The endpoint takes `read` or `write` and has
neither `null` nor `inherit`, and no endpoint reports which repositories
carry an override; a repository that sets its own stops following the
default with nothing to say that it has. Nobody has recorded an override
here, which is weaker than knowing there is none — so whoever moves the
organization default reads this repository back afterwards rather than
assuming it moved.

## Secret scanning and Dependabot

```shell
gh api repos/btclib-org/.github --jq '.security_and_analysis'
# {"dependabot_security_updates":{"status":"enabled"},
#  "secret_scanning":{"status":"enabled"},
#  "secret_scanning_non_provider_patterns":{"status":"disabled"},
#  "secret_scanning_push_protection":{"status":"enabled"},
#  "secret_scanning_validity_checks":{"status":"disabled"}}
```

All free on a public repository and all off by default; push protection
is the one that refuses the push rather than reporting it afterwards. The
`detect-private-key` hook is what runs before any of them, on the
author's own machine.

What answers `disabled` above is plan-gated rather than declined, and the
API answers a `PATCH` of one with 200 while leaving it off — so what that
call reports is the setting and not the request.

There is no `.github/dependabot.yml`: the actions pinned in the workflows
here have nothing proposing their next SHA, and the pre-commit revisions
have pre-commit.ci's weekly autoupdate instead. That is a gap rather than
a choice.

## What is not configured, and why

- **No publishing, and no release workflow.** Nothing here is installed
  or downloaded; what this repository ships, it ships by being read on
  github.com. So there is no `pypi` environment, no OIDC trusted
  publisher, and no tag to protect.
- **No CodeQL.** It analyses code for vulnerabilities, and there is none
  here: `README.md`, `profile/README.md` and configuration.
- **No Pages and no Read the Docs.** The rendered form of this repository
  is the organization profile GitHub builds from `profile/README.md`,
  which is not a site anything deploys.
- **No test suite, so no coverage.** What replaces one is section 15 of
  `README.md`: the standard is measured against the repositories with the
  commands recorded there rather than asserted, and this file is that
  measurement pointed at this repository.
