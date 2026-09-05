# Repository configuration

What is set on this repository, as the `gh api` call that reads it back
and the answer that call gives today. A setting recorded as prose alone
is one nobody can check; recorded this way, a drift is one command away
from being seen.

[Section 11 of the standard][s11] says every repository writes its
settings down here, this one included: the repository that holds the
standard is not exempt from it.

The rules and the settings live *outside* the tree. What is recorded is
the settings the standard asks about — the ones [section 16's
checklist][s16] sets on a new repository, the ones a section of the
standard states a rule for, and the ones a behaviour it describes rests
on — together with whatever a call quoted for one of those answers
alongside it. That is this file's scope, and *What this file passes over*
at the foot says what falls outside it.

The topics have a second form in the tree, `pyproject.toml`'s
`keywords`, so they are read back here for comparison rather than as the
only place the answer lives, which is what *Topics* says of them.
Nothing else here is recoverable by reading the tree.

The endpoints these answers come from are the file's own `gh api` lines,
listed rather than restated in a second place that would have to be kept
true. The pattern reaches both scopes: a setting the organization decides
once is read back here too, where a section below rests on it.

```shell
grep -oE '(repos/btclib-org/\.github|orgs/btclib-org)[a-z/-]*' \
  REPOSITORY.md | sort -u
```

When each answer was read is the commit that wrote it: `git blame
REPOSITORY.md`.

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
possible at all, the ruleset bypass reaching only the ruleset's own rule.
It exempts an administrator from the required checks as well as from the
review, so the `strict` above is not what makes the landing tree current;
[section 11 pairs the two settings and has what does][s11-branch].

The `checks` array and a JSON body on stdin, never `contexts` and never
`-f`, and a later change to the list is a `PATCH` of
`/required_status_checks` rather than a partial `PUT` — [section 11
records what each of those does instead][s11-branch], every one of them
silently. `15368` is the Actions app, and a check bound to it cannot be
reported by anything else.

## Branch protection and the rulesets

`main` is the repository's default branch and its only one:

```shell
gh api repos/btclib-org/.github --jq '.default_branch'
# main
```

Everything reaches it through a pull request. Rules [aggregate rather
than replace each other][s11-branch], so what holds on `main` is what the
call below answers for that target **together with** the classic
protection two headings up: that one requires a review, a linear history,
resolved conversations and the `Lint` check, and refuses a force push or
a deletion — under the exemption above, which these rulesets do not
carry. Where the two overlap, the stricter answer is the one that
applies:

```shell
gh api repos/btclib-org/.github/rulesets --jq '.[].id' \
  | xargs -I{} gh api repos/btclib-org/.github/rulesets/{} \
    --jq '{name, target, enforcement, refs: .conditions.ref_name.include,
           rules: [.rules[].type],
           bypass: [.bypass_actors[]?.bypass_mode]}'
# {"bypass":[],"enforcement":"active","name":"main-integrity",
#  "refs":["refs/heads/main"],
#  "rules":["required_signatures","required_linear_history",
#           "non_fast_forward","deletion"],"target":"branch"}
# {"bypass":["pull_request"],"enforcement":"active",
#  "name":"main-self-merge","refs":["refs/heads/main"],
#  "rules":["pull_request"],"target":"branch"}
# {"bypass":[],"enforcement":"active","name":"tag-integrity",
#  "refs":["refs/tags/v*"],"rules":["required_signatures"],"target":"tag"}
```

- `main-integrity` — required signatures, required linear history, no
  force pushes, no deletions — with **no bypass actor at all**, which is
  what makes every one of those true of an administrator too.
- `main-self-merge` — a pull request, an approving review, stale reviews
  dismissed on push, conversations resolved, and `squash` as the only
  merge method it accepts — bypassed by the maintainer in
  **`pull_request` mode**.
- `tag-integrity` — required signatures and nothing else, over
  `refs/tags/v*` rather than over a branch, with **no bypass actor**.

```shell
gh api repos/btclib-org/.github/rulesets --jq '.[].id' \
  | xargs -I{} gh api repos/btclib-org/.github/rulesets/{} \
    --jq '.rules[] | select(.type=="pull_request") | .parameters'
# {"allowed_merge_methods":["squash"],
#  "dismiss_stale_reviews_on_push":true,
#  "dismissal_restriction":{"allowed_actors":[],"enabled":false},
#  "require_code_owner_review":false,
#  "require_extra_approval_for_unattributed_changes":true,
#  "require_last_push_approval":false,"required_approving_review_count":1,
#  "required_review_thread_resolution":true,"required_reviewers":[]}
```

The bypass reaches that whole block and not the approving review alone,
and every landing here is made by the account it names:
`dismiss_stale_reviews_on_push` is on and reaches none of them.
[Section 11 has what stands in for it][s11-branch].

`main-self-merge`'s `bypass` is one of the fields the first call above
is read for. It answers `["pull_request"]`, and [that mode against
`always` is the whole of the design][s11-branch]; `always` in that field
would mean a direct push to `main` had become possible for its holder,
which is a drift the call is there to catch.

`tag-integrity` matches no ref: `CONTRIBUTING.md`'s *A version, and no
release* is where nothing being tagged is measured. What the rule buys
is [a signed release tag][s11-sigs], and it stands ahead of that tag
rather than being created alongside one, so a `v*` pushed to this
repository meets it.

## Signed commits

```shell
gh api repos/btclib-org/.github/commits/main \
  --jq '.commit.verification | {verified, reason}'
# {"reason":"valid","verified":true}
```

`required_signatures` is a rule of `main-integrity`, so what it refuses
is a push writing an unsigned commit to `refs/heads/main`, at the push
rather than in a check reported afterwards, and with no bypass actor it
refuses one from everybody. Nothing above reaches a branch other than
that one.

What the call answers is the signature on the squash GitHub composed at
the merge button, made with its own web-flow key rather than the
maintainer's, and that satisfies the rule: [it asks for a valid signature
and not for a particular signer][s11-sigs]. The section below reads back
squash as the only merge method, so that commit is also the only one the
rule ever sees: a branch's own are never written to `main`.

So what no rule covers is every commit but that one, pushed or not, and a
verified `main` is not evidence that any of them is signed.
`git log --format='%G? %GS' origin/main..` is what answers for a branch's
own, an `N` being a defect to fix rather than to explain.

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

[Squash is the only method the standard enables][s11-merge], and
`allowed_merge_methods` above holds it for every account the
`main-self-merge` bypass does not cover. For the maintainer, who is
covered, what stands against this setting being flipped back is
`main-integrity`'s `required_linear_history`: no bypass actor, and a
merge commit refused for everybody. Rebase-and-merge is linear, so that
rule does not reach it, and [the reason it is not enabled is section
11's][s11-merge].

Whether a bypass holder is offered a merge method `allowed_merge_methods`
excludes is not read back here: measuring it means flipping
`allow_rebase_merge` and pressing the button on a live pull request,
which is a settings change and a landing rather than a call.

`COMMIT_OR_PR_TITLE` with `COMMIT_MESSAGES` is the pair
[Merge method][s11-merge] asks for, and which of the two titles lands is
that subsection's rule.

Auto-merge is on, and [the landing that subsection describes rests on
it][s11-merge].

`delete_branch_on_merge` fires on its own, every landing here being a
merged pull request, so a branch still standing is one that was closed
rather than merged.

## Features

```shell
gh api repos/btclib-org/.github \
  --jq '{issues: .has_issues, visibility: .visibility}'
# {"issues":true,"visibility":"public"}
```

Issues are where this organization's cross-repository findings live, and
where they live *only*, for the reason [`README.md`](./README.md)'s
*What this repository is* gives: a finding about several repositories
filed on one of them is invisible from the others.

Public matters more here than elsewhere. This repository supplies the
community health files GitHub shows for any public repository of the
organization that has none of its own, and it does that only while it is
public and named `.github`.

## Topics

```shell
gh api repos/btclib-org/.github --jq '.topics'
# ["bitcoin","btclib","github-organization","repository-standard"]
```

[Section 3 makes a package's `keywords` its topics][s3].
`pyproject.toml` here declares the same names, so the two lists are one
list spelled twice, and this is the command that holds them together: it
prints the difference and exits nonzero on one.

```shell
diff <(gh api repos/btclib-org/.github --jq '.topics[]' | sort) \
     <(sed -n '/^keywords = \[/,/^]/s/^ *"\(.*\)",$/\1/p' pyproject.toml \
       | sort)
```

Both sides are sorted because [the order is maintained on one side and
compared on neither][s3]: `pyproject.toml` declares the names in the
order that section keeps, and the call answers in an order of GitHub's
own. `topics_test.py`'s `keyworded` selects the trees this comparison is
asked of on the `[project]` table's presence, so this one is among them.

What the record is still the only home of is that the names are set on
the repository at all: nothing in the tree pushes them there, so a
repository restored from `pyproject.toml` alone has the keywords and no
topics until somebody sets them.

## Token permissions

```shell
gh api repos/btclib-org/.github/actions/permissions/workflow
# {"default_workflow_permissions":"read",
#  "can_approve_pull_request_reviews":false}
```

`read`, which is what every workflow here needs: `lint.yml` and
`links.yml` read the tree, and `claude-review.yml`'s jobs elevate
themselves to `pull-requests: write` to write on a pull request and to
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

Version bumps are the other half of what Dependabot does here, and they
are a file rather than a setting: `.github/dependabot.yml` declares
`github-actions`, which [the standard gives every tree][s11-bots], and
`uv`, which it gives a tree holding what that ecosystem reads — this one
holds `uv.lock`. The pre-commit hook revisions have no Dependabot
ecosystem, and are pre-commit.ci's weekly autoupdate instead, per the
`ci:` block of `.pre-commit-config.yaml`.

## Private vulnerability reporting

```shell
gh api repos/btclib-org/.github/private-vulnerability-reporting
# {"enabled":true}
```

On, [as the standard asks of every tier][s2-root].

## Plan-gated settings

The ceiling on concurrent jobs is a number the plan decides rather than
anything this repository configures, and [section 10 of the standard
makes this section its one home in the tree][s10-set], beside the command
that re-derives it:

```shell
gh api orgs/btclib-org --jq .plan.name
# free
```

[GitHub's own table](https://docs.github.com/en/actions/reference/limits)
turns that answer into a number, twenty concurrent jobs on the free plan,
shared across every repository of the organization. `lint.yml` and
`claude-review.yml` are what a pull request here starts, with
`alignment.yml` and `links.yml` added where the paths their triggers name
are touched. `CONTRIBUTING.md`'s *The landing queue* is what points here
for the figure.

The two secret-scanning settings that answer `disabled` under *Secret
scanning and Dependabot* above are the other plan-gated pair, and that
section is where they are read back.

## What is not configured, and why

- **No publishing, and no release workflow.** `CONTRIBUTING.md`'s *A
  version, and no release* is the whole of that answer. There is no
  `pypi` environment, no OIDC trusted publisher and nothing tagged:
  `gh api repos/btclib-org/.github/environments --jq .total_count`
  answers `0`.
- **No CodeQL**, and GitHub's default setup off with it:
  `gh api repos/btclib-org/.github/code-scanning/default-setup --jq .state`
  answers `not-configured`. [Section 10's `codeql` entry does not name
  this tree][s10-carries], and a tree an entry does not name is asked
  nothing by that row, so what is off here is off by a decision taken
  once for the organization rather than by one this repository reached
  on its own. What would turn the analysis on is that entry, and this
  bullet is the setting that follows from it.
- **No Pages and no Read the Docs.** The rendered form of this repository
  is the organization profile GitHub builds from `profile/README.md`,
  which is not a site anything deploys.
  `gh api repos/btclib-org/.github/pages` answers `404`, and the same
  call against `btclib-org/btclib` answers `built` — the pair is what
  makes the first an absence rather than a permission.
- **A suite, and no coverage.** [Section 8's ratchet][s8] is a claim
  about a package's own code and this tree ships none, so what the number
  would measure is the suite measuring itself. What the suite does
  measure is [the audit the standard carries][s15], for the questions
  whose answer is in no single tree — and this file is the rest of that
  audit, pointed at the repository the commands came from.

## What this file passes over

The API answers for more than this repository decides, and what is left
out is left out by the scope above rather than by oversight.

**What no call sets.** `gh api repos/btclib-org/.github` answers with the
repository document, most of which is URLs, counts and derived state. The
fields of it that are settings are the ones the sections above quote.

**A credential this repository spends and does not hold.**
`claude-review.yml` reads `secrets.CLAUDE_CODE_OAUTH_TOKEN`, and both
secret stores here answer empty for it:

```shell
gh api repos/btclib-org/.github/actions/secrets --jq .total_count
gh api repos/btclib-org/.github/dependabot/secrets --jq .total_count
# 0, both
gh api orgs/btclib-org/actions/secrets \
  --jq '.secrets[] | [.name, .visibility]'
gh api orgs/btclib-org/dependabot/secrets \
  --jq '.secrets[] | [.name, .visibility]'
# ["CLAUDE_CODE_OAUTH_TOKEN","all"], both
```

Those two zeros record a decision, and it is [the standard's][s11-review]:
the token is an organization secret at `visibility=all`, in both stores,
so a repository adopting the workflow configures nothing for it, and a
copy of it in a store here would be that decision undone.

**A switch this repository does not set.** `claude-review.yml` guards
its jobs with `vars.CLAUDE_REVIEW_ENABLED`, and neither variable store
holds it:

```shell
gh api repos/btclib-org/.github/actions/variables --jq .total_count
# 0
gh api orgs/btclib-org/actions/variables --jq '.variables[].name'
# (nothing)
gh api orgs/btclib-org/actions/variables --jq .total_count
# 0
```

The organization secret above answering with a name is what makes these
zeros absences rather than an endpoint that answers empty for everyone.
The variable store prints nothing at all when it answers, so its own
`total_count` of `0` is what shows the call reached it: one that does not
reach it prints an error and exits non-zero. [Section 11 reads that empty
name list as the switch's off state][s11-review]. Both stores are read
because a variable set here would take precedence over one of the same
name set on the organization, so the organization's answer alone would
not show the switch off for this tree.

**A facility nobody reached for.** Self-hosted runners, webhooks, deploy
keys, autolinks and custom property values each answer empty here, and an
empty answer records no decision. Whichever of them is used one day
arrives with the section that uses it.

**A field the standard states no rule about, and no call above
answers alongside one it does.** `allow_forking`, `allow_update_branch`,
`has_discussions`, `has_downloads`, `is_template` and
`web_commit_signoff_required` are in the repository document and in none
of the `--jq` objects here, and `README.md` asks nothing of them:
`grep -c allow_update_branch README.md` answers `0` where
`grep -c 'default branch' README.md` does not, which is what makes that
zero an absence. Recording a field on no rule grows this file with
GitHub's API rather than with the standard.

The price is that a change to any of those is invisible here, and finding
one means reading the repository document against this file rather than
running a command.

[s2-root]: ./README.md#root-files
[s3]: ./README.md#3-pyprojecttoml-is-the-configuration
[s8]: ./README.md#8-coverage-at-100
[s10-check]: ./README.md#the-aggregate-job-and-the-required-check
[s10-carries]: ./README.md#which-trees-carry-which-sentinel
[s10-set]: ./README.md#the-set-and-its-cadence
[s11-bots]: ./README.md#dependabot-and-pre-commitci
[s11-branch]: ./README.md#branch-protection-and-rulesets
[s11-merge]: ./README.md#merge-method
[s11-review]: ./README.md#review
[s11-sigs]: ./README.md#signatures
[s11-tokens]: ./README.md#tokens-publishing-scanning
[s11]: ./README.md#11-github-settings
[s15]: ./README.md#15-auditing-a-repository-against-this-file
[s16]: ./README.md#16-checklists
