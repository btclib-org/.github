# Repository configuration

What is set on this repository, as the `gh api` call that reads it back
and the answer that call gives today. A setting recorded as prose alone
is one nobody can check; recorded this way, a drift is one command away
from being seen.

[Section 11 of the standard][s11] says every repository writes its
settings down here, and until now this was the repository with nowhere to
read its own back — the one holding the standard being the one exempt
from it.

The rules and the settings live *outside* the tree, so this file is the
whole of them: nothing below is recoverable by reading the repository.

**Where a setting has a reason, the reason is in `README.md` and this
file links to it.** Two copies of an argument are two things to keep
true, and the standard is in this repository, so the link is one a reader
can follow rather than a section number to go looking for. What is here
instead is the answer this repository gives — including where that is not
the answer the sibling repositories give.

## Required checks on main

```shell
gh api repos/btclib-org/.github/branches/main/protection \
  --jq '.required_status_checks | {strict, checks: [.checks[].context]}'
# {"strict":true,"checks":["Lint"]}
```

The rulesets below enforce the signatures and the review, and [classic
protection is where the required checks go][s16]. It was created once
`lint.yml` had produced its context, which is the order that call
requires; the command that created it is kept at the foot of this section
because a `PUT` there sets every field and a reader restoring the
protection needs the whole object rather than the answer above.

| Check | Produced by |
| --- | --- |
| `Lint` | `lint.yml`'s only job |

`lint.yml` has one job, so that job is the context and there is no
[aggregate job][s10-check] here to name. The name is not the sibling
repositories' `Lint and type-check`, though the hook config it runs
carries a mypy hook as theirs do: a context is keyed by name alone and
bound outside the tree, so changing one is not something a pull request
can do. The direction that would matter is the other one, a name
promising a check nobody runs.

**`links.yml` is not a required check and must not become one.** It asks
whether somebody else's server answered, which is a question a merge
cannot depend on; its own header carries the reasoning.
`claude-review.yml` is not one either, and [says so itself][s11-review].

A check context cannot be bound before a workflow has produced it, which
is why `lint.yml` landed before the rule did. The call that created the
protection carries the whole object — every field of it, since a `PUT`
sets what it is given and clears what it is not, so this is also what
restores it:

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

`enforce_admins: false` is not a relaxation but what makes a solo merge
possible at all, the ruleset bypass reaching only the ruleset's own rule;
[section 11 pairs the two settings][s11-branch].

The `checks` array and a JSON body on stdin, never `contexts` and never
`-f`, and a later change to the list is a `PATCH` of
`/required_status_checks` rather than a partial `PUT` — [section 11
records what each of those does instead][s11-branch], every one of them
silently. `15368` is the Actions app, and a check bound to it cannot be
reported by anything else.

## Branch protection and the rulesets

`main` is the only branch, and everything reaches it through a pull
request. Rules [aggregate rather than replace each other][s11-branch], so
what holds is what the call below answers **together with** the classic
protection two headings up: that one requires a review, a linear history,
resolved conversations and the `Lint` check, and refuses a force push or a
deletion, and it exempts an administrator where these rulesets do not.
Where the two overlap, the stricter answer is the one that applies:

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

The `bypass` field is what the first call above is read for. It answers
`["pull_request"]`, and [that mode against `always` is the whole of the
design][s11-branch]; `always` in that field would mean a direct push to
`main` had become possible for its holder, which is the drift this
command exists to catch.

There is no `tag-integrity` ruleset, and no `refs/tags/v*` for one to
target. What it buys the sibling repositories is [a signed release
tag][s11-sigs], and nothing here is released, so there is no tag for the
rule to hold.

## Signed commits

```shell
gh api repos/btclib-org/.github/commits/main \
  --jq '.commit.verification | {verified, reason}'
# {"reason":"valid","verified":true}
```

`required_signatures` refuses an unsigned commit at the push rather than
noticing it afterwards, and with an empty bypass list it refuses one from
everybody. What the call answers is the signature on the squash GitHub
composed at the merge button, made with its own web-flow key rather than
the maintainer's, and that satisfies the rule: [it asks for a valid
signature and not for a particular signer][s11-sigs].

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

[Squash is the only method the standard enables][s11-merge], and the
`main-self-merge` ruleset above names it too, so the constraint holds
even if this repository setting is flipped back.

`COMMIT_OR_PR_TITLE` with `COMMIT_MESSAGES` is what makes [a pull
request's title the landing commit's subject][s11-title] and the branch's
own messages its body.

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
where they live *only*, for the reason [`README.md`](./README.md)'s
*What this repository is* gives: a finding about several repositories
filed on one of them is invisible from the others.

Public matters more here than elsewhere. This repository supplies the
community health files GitHub shows for any public repository of the
organization that has none of its own, and it does that only while it is
public and named `.github`.

The wiki and the projects board are on, where the sibling repositories
turn both off. The standard states no rule about either, so this is a
divergence rather than a decision, and closing it is a settings change
with no diff to review.

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

`can_approve_pull_request_reviews` is false, and [the standard says why
that matters as much as the token][s11-tokens].

**What this call cannot say is whether that value is this repository's
own or the organization's**, [there being no endpoint that
answers][s11-tokens]. Nobody has recorded an override here, which is
weaker than knowing there is none — so whoever moves the organization
default reads this repository back afterwards rather than assuming it
moved.

## Secret scanning and Dependabot

```shell
gh api repos/btclib-org/.github --jq '.security_and_analysis'
# {"dependabot_security_updates":{"status":"enabled"},
#  "secret_scanning":{"status":"enabled"},
#  "secret_scanning_non_provider_patterns":{"status":"disabled"},
#  "secret_scanning_push_protection":{"status":"enabled"},
#  "secret_scanning_validity_checks":{"status":"disabled"}}
```

[The standard asks for secret scanning, its push protection and
Dependabot security updates][s11-tokens], and the call answers `enabled`
to each. What runs before any of them is the `detect-private-key` hook,
on the author's own machine.

What answers `disabled` is [plan-gated rather than declined][s11-tokens],
so this call reports the setting and not the request.

There is no `.github/dependabot.yml`, where [the standard asks for the
`github-actions` ecosystem at least][s11-bots]: the actions these
workflows pin have nothing proposing their next SHA, and `uv.lock` has
nothing proposing its next resolution. The pre-commit
revisions do have pre-commit.ci's weekly autoupdate, per the `ci:` block
of `.pre-commit-config.yaml`. The missing file is a gap rather than a
choice.

## Private vulnerability reporting

```shell
gh api repos/btclib-org/.github/private-vulnerability-reporting
# {"enabled":true}
```

On, [as the standard asks of every tier][s2-root].

## What is not configured, and why

- **No publishing, and no release workflow.** Nothing here is installed
  or downloaded; what this repository ships, it ships by being read on
  github.com. So there is no `pypi` environment, no OIDC trusted
  publisher, and no tag to protect.
- **No CodeQL.** The reason recorded here was that there is no code, and
  `tests/` is code. What stands in its place is narrower: that suite is
  neither installed nor imported by anything, and what it reads is this
  organization's own API answers. Whether that is enough to leave the
  analysis off is open rather than settled.
- **No Pages and no Read the Docs.** The rendered form of this repository
  is the organization profile GitHub builds from `profile/README.md`,
  which is not a site anything deploys.
- **A suite, and no coverage.** [Section 8's ratchet][s8] is a claim
  about a package's own code and this tree ships none, so what the number
  would measure is the suite measuring itself. What the suite does
  measure is [the audit the standard carries][s15], for the questions
  whose answer is in no single tree — and this file is the rest of that
  audit, pointed at the repository the commands came from.

[s2-root]: ./README.md#root-files
[s8]: ./README.md#8-coverage-at-100
[s10-check]: ./README.md#the-aggregate-job-and-the-required-check
[s11-bots]: ./README.md#dependabot-and-pre-commitci
[s11-branch]: ./README.md#branch-protection-and-rulesets
[s11-merge]: ./README.md#merge-method
[s11-review]: ./README.md#review
[s11-sigs]: ./README.md#signatures
[s11-title]: ./README.md#what-a-pull-request-says-it-is
[s11-tokens]: ./README.md#tokens-publishing-scanning
[s11]: ./README.md#11-github-settings
[s15]: ./README.md#15-auditing-a-repository-against-this-file
[s16]: ./README.md#16-checklists
