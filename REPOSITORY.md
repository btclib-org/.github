# Repository configuration

What is set on this repository, as the `gh api` call that reads it back
and the answer that call gives today. A setting recorded as prose alone
is one nobody can check; recorded this way, a drift is one command away
from being seen.

[Section 11 of the standard][s11] says every repository writes its
settings down here, and until now this was the repository with nowhere to
read its own back — the one holding the standard being the one exempt
from it.

The rules and the settings live *outside* the tree: nothing below is
recoverable by reading the repository. What is recorded is the settings
the standard asks about — the ones [section 16's checklist][s16] sets on
a new repository, and the ones a section of `README.md` states a rule
for — together with whatever a call quoted for one of those answers
alongside it. That is this file's scope, and *What this file passes over*
at the foot says what falls outside it.

The endpoints these answers come from are the file's own `gh api` lines,
listed rather than restated in a second place that would have to be kept
true:

```shell
grep -o 'repos/btclib-org/\.github[a-z/-]*' REPOSITORY.md | sort -u
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

The wiki and the projects board are on, and that is not this
repository's divergence: `btclib-benchmarks` is the sibling that turns
both off.

```shell
for r in btclib btclib-node btclib-secp256k1 bbt portanode \
         bitcoin-core-rpc btclib-benchmarks; do
  gh api "repos/btclib-org/$r" \
    --jq '[.name, (.has_wiki | tostring), (.has_projects | tostring)]
          | @tsv'
done
# btclib-benchmarks answers false twice, and every other name true twice
```

The standard states no rule about either, so no answer to them is a
decision here, and settling it in one direction is a settings change with
no diff to review.

## Topics

```shell
gh api repos/btclib-org/.github --jq '.topics'
# ["bitcoin","btclib","github-organization","repository-standard"]
```

[Section 3 makes a package's `keywords` its topics][s3], and this
`pyproject.toml` declares none — it is not a distribution's, so there is
no list in the tree for these names to be compared against.
`topics_test.py` compares the two sides for a repository whose
`pyproject.toml` carries a `[build-system]`, which this one does not, and
asks of the rest only that a topic exists at all. So the names live here
and nowhere else: a repository restored from a record that passed over
them has no topics, which is the one thing the suite does ask.

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

## What is not configured, and why

- **No publishing, and no release workflow.** `CONTRIBUTING.md`'s *A
  version, and no release* is the whole of that answer. There is no
  `pypi` environment, no OIDC trusted publisher and nothing tagged:
  `gh api repos/btclib-org/.github/environments --jq .total_count`
  answers `0`.
- **No CodeQL**, and GitHub's default setup off with it:
  `gh api repos/btclib-org/.github/code-scanning/default-setup --jq .state`
  answers `not-configured`. The reason recorded here was that there is no
  code, and `tests/` is code. What stands in its place is narrower: that
  suite is neither installed nor imported by anything, and what it reads
  is this organization's own API answers. Whether that is enough to leave
  the analysis off is open rather than settled.
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

**A facility nobody reached for.** Actions secrets and variables,
Dependabot secrets, self-hosted runners, webhooks, deploy keys, autolinks
and custom property values each answer empty here, and an empty answer
records no decision. Whichever of them is used one day arrives with the
section that uses it.

**A field the standard states no rule about, and no call above
answers alongside one it does.** `allow_forking`, `allow_update_branch`,
`has_discussions`, `has_downloads` and `web_commit_signoff_required` are
in the repository document and in none of the `--jq` objects here, and
`README.md` asks nothing of them: `grep -c allow_update_branch README.md`
answers `0` where `grep -c 'default branch' README.md` does not, which is
what makes that zero an absence. Recording a field on no rule grows this
file with GitHub's API rather than with the standard.

The price is that a change to any of those is invisible here, and finding
one means reading the repository document against this file rather than
running a command.

[s2-root]: ./README.md#root-files
[s3]: ./README.md#3-pyprojecttoml-is-the-configuration
[s8]: ./README.md#8-coverage-at-100
[s10-check]: ./README.md#the-aggregate-job-and-the-required-check
[s11-bots]: ./README.md#dependabot-and-pre-commitci
[s11-branch]: ./README.md#branch-protection-and-rulesets
[s11-merge]: ./README.md#merge-method
[s11-review]: ./README.md#review
[s11-sigs]: ./README.md#signatures
[s11-tokens]: ./README.md#tokens-publishing-scanning
[s11]: ./README.md#11-github-settings
[s15]: ./README.md#15-auditing-a-repository-against-this-file
[s16]: ./README.md#16-checklists
