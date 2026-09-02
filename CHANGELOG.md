# Changelog

What changed in the standard, and why. Nothing here is released — this
repository ships by being read — so the entries are grouped by subject
rather than by version, and the record they make is the one section 15's
audit has no revision to compare against.

## Unreleased

### Section 11 reads what a squash lands too, not only the pull request

- **`closingIssuesReferences` reads the pull request's description, and a
  squash lands a second, separately authored text** (closes #497):
  `dde42cd` (PR 512) put #468 into CLOSED on a subject typed at merge
  time, which the pre-merge read cannot see because that text does not
  exist yet — the pull request's own title and body both read
  `(issue #468)` throughout. Section 11's *What a pull request says it
  is* now asks for the landed commit's own message to be read the same
  way, from its sha, against the per-issue timeline command the section
  already gives; CONTRIBUTING.md's *Landing it* points at that second
  read rather than repeating it.
- **The alternative weighed and declined lands the pull request's title
  as the squash subject verbatim, so there is only one text**: cheaper,
  but a rule about how a person presses the button rather than a check
  anything runs, where comparing the two reads is a check that runs
  regardless of how the button was pressed.
- **A verb in front of a reference that must not close is now a command
  over the branch's own commit text, run before the merge and before the
  description exists to disagree with it**: `f47899a` (PR 491)'s body
  carried `This does not close btclib-org/.github#365`, and
  `closingIssuesReferences` answered empty for it while that issue
  closed anyway, once the identical sentence was the landed commit's
  own text — two reads of the same words, disagreeing. Section 11 gives
  the scan and the expectation it is read against: every hit outside the
  title's own `(closes #N)` parentheses is the finding.

### Section 9 names the rebase hazard `merge=union` hides, and the remedy

- **A rebase across a `merge=union` file can place the rebasing branch's
  own section below one that landed while it waited, and no gate reads
  that order** (closes #486): `git rebase` exits 0, and the fixer that
  restores the blank line between two joined sections says nothing about
  which one comes first, so the diff after the rebase — read, not
  trusted — is what shows the misplacement. The remedy is moving the
  block back before pushing, since nothing already written there is
  rewritten once it lands.

- **Where a new entry belongs inside `## Unreleased` is read from the
  file it lands in** (closes #486), not fixed by section 9 or copied
  from a sibling repository, since the position is not the same
  convention in every repository.

### Section 2 names the scorecard badge and fixes two stale citations

- **`scorecard`'s property asked for "that sentinel's badge" without
  saying which one** (closes #481): every sentinel but `scorecard`
  answers with the workflow-run badge,
  `github.com/<org>/<repo>/actions/workflows/<name>.yml/badge.svg`, and
  `scorecard` does not — it publishes a score rather than a pass or
  fail, at `api.scorecard.dev/projects/github.com/<org>/<repo>/badge`,
  which section 10's `scorecard` subsection already ties to the same
  `publish_results: true` the badge needs. The Read the Docs clause
  three lines above it also drops the three literals it borrowed from
  the workflow badges' own vocabulary, which the paragraph below it is
  written to keep separate.

- **Sections 4 and 15 cited a hand-written licence badge no tree
  carries** (closes #495): both illustrated a rule with
  `bitcoin-core-rpc`'s `[![license: MIT](…)](./LICENSE)`, restored to
  the derived form while btclib-org/.github#490 was being worked. Both
  now point at section 2's own refused form,
  `img.shields.io/badge/license-MIT-blue.svg`, rather than at a tree's
  markdown.

- **The downloads badge linked to a pepy URL that redirects** (closes
  #511): `pepy.tech/project/<name>`, singular, answers `308` and
  redirects to `pepy.tech/projects/<name>`, plural — the same reason
  the Read the Docs host is `app.readthedocs.org` and not
  `readthedocs.org` — and section 2 now names the plural.

### `REPOSITORY.md` states what it covers, and covers the topics

- **The record said it was the whole of the settings outside the tree**
  (issue #468): what it covers is stated instead — the settings section
  16's checklist sets on a new repository, and the ones a section of
  `README.md` states a rule for. The endpoints the answers come from are
  listed by a grep over the file's own `gh api` lines rather than by a
  second list to keep true, and when each was read is the commit that
  wrote it. A file promising a whole API surface is falsified by that
  surface moving, with nothing in the repository having changed.

- **The topics are in this record and in no other file** (issue #468):
  section 3 makes a package's `keywords` its topics, this
  `pyproject.toml` declares none, and `topics_test.py` compares the two
  sides only for a tree whose `pyproject.toml` carries a
  `[build-system]`. What the suite asks of the rest is that a topic
  exists, so a repository restored from a record without them answers
  that floor with nothing.

- **Section 16's checklist sets the topics and reads them back**, which
  is what makes their absence from a copy of `REPOSITORY.md` a defect
  rather than a matter of taste. The copies that record the setting each
  reached it their own way, so the checklist is where the one answer
  belongs.

- **The default branch, GitHub's code-scanning default setup and the
  absence of a Pages site answer a command**, where they were prose or
  nothing. That last call answers `404` here and `built` against
  `btclib-org/btclib`, which is what makes the first an absence rather
  than a permission.

- **The *Features* block had the sibling repositories turning the wiki
  and the projects board off**, and `btclib-benchmarks` is the one that
  does: the loop that answers for the family sits beside the sentence
  now. This repository's answer is the family's, so it is no divergence
  of its own — which matters to the scope above, that block being what a
  call quoted for `has_issues` and `visibility` answers alongside.

- **What the file passes over is named**: fields no call sets, endpoints
  answering empty for a facility nobody reached for, and fields
  `README.md` states no rule about. The price is beside them — a change
  to one of those is found by reading the repository document against
  this file rather than by running a command.

### The organization's page says how often somebody else's vectors are checked

- **`profile/README.md` called the `vendored-vectors` sweep a monthly
  job** (closes #482): each tree carrying that workflow restricts the day
  of the week and leaves the day of the month open, which is a weekly
  schedule, and section 10 holds the rule behind it — *the week is the
  whole of the grid's period*, so a `cron:` on any other cadence is one
  the calendar cannot name.

- **The page states the cadence rather than pointing at section 10 for
  it**, its reader having arrived at github.com/btclib-org with no
  section number to follow. What makes that restatement safe is that the
  period is the grid's and not a row's: a day and an hour move when a row
  moves, where a change to the period rewrites every row at once.
  *Monthly* was a word the page could not have held for the same reason.

- **`portanode`'s entry named macOS and Windows where that tree runs on
  Linux as well.** Its own `README.md` is where the fact lives — *running
  Bitcoin Core (and Electrum) on macOS, Windows and Linux* — and the page
  held a shorter copy of it. Section 9's *One fact in one place* is the
  same diagnosis as the cadence with a different owner.

- **The page names no weekday, no hour and no count of repositories**,
  enumerating them instead, so the cadence above is the whole of what
  section 10 owns here and the correction is one word rather than a
  family of them.

### The aggregate recipe says what runs the job, and what it may judge

- **Section 10 stated the aggregate step's condition and never the
  job's** (closes #479): a job with `needs` and no `if:` is skipped when
  one of those needs fails, so a step that always runs sits inside a job
  the red matrix never reaches and the check a merge waits for reports
  `skipped` rather than the failure. The rule names `!cancelled()` and
  why not `always()`, a run its own concurrency group superseded being
  the case that would reach the job and fail it over a cancellation the
  newer run already speaks for.

- **The sentence naming the listing now names how it is asked for**
  (closes #479): `gh api --paginate`, and `per_page=100` on the query. A
  page is a bound on what comes back and nothing bounds a run's job
  count under it, so the listing can cross that page with nothing in the
  answer saying it did, and both the allowlist and the unfinished count
  are then taken over a subset. `btclib-org/btclib`'s run `33048874272`,
  a `release.yml` run and so not one this shape reads, is a listing of
  this organization's already longer than one default page.

- **The aggregate's own row has no conclusion at the moment the step
  reads it** (closes #479): the allowlist was written over every row of
  the listing while the same section requires exactly one unfinished job
  of the run and names the aggregate as it, so the recipe asked for a
  required check that is red on every run. The allowlist judges each
  finished row, and the unfinished count is what answers for the rest.
  `btclib-benchmarks`' run `33090501622` is where its aggregate printed
  its own row as `unfinished` and `in_progress` before judging the
  listing.

### A wait for something outside the run is a script with a test

- **A trigger added to a wait reaches its first attempt and not what the
  wait is for** (issue #466): the verdict such a step delivers is the
  one it reaches when the wait runs out, and what is waited on belongs
  to a third party, so neither a release nor a rehearsal can arrange for
  it to be late. `documented`'s loop, and the shapes weighed against it
  — a dispatch input naming a version, the same loop pointed at `latest`
  on the docs gate — differ in how often the branch that runs when there
  is nothing to wait for is taken.

- **The lint gate reads the loop and passes it**: `actionlint` runs
  `shellcheck` over a `run:` block, and neither of them reads it against
  the job header, which is where a budget able to outlast
  `timeout-minutes` lives — btclib-org/btclib#1165. Counting against a
  deadline states that budget once, and a test substituting the
  transport and the clock is what drives the loop past it.

- **Section 6 said no test collects `.github/scripts`**: a test whose
  subject is one of those scripts loads it by path, that directory being
  no package. `btclib-secp256k1` tests its wheel-content check that way
  because a run cannot produce the failure on purpose, which is the
  property a wait shares.

### The alignment sweep refuses the run it has no token for

- **A fallback to `GITHUB_TOKEN` made a missing secret read as a
  finding** (issue #477): `ALIGNMENT_TOKEN` is set neither on this
  repository nor on the organization, so every run took the right-hand
  side of `secrets.ALIGNMENT_TOKEN || secrets.GITHUB_TOKEN` and failed
  inside the suite, at the fixture that fetches classic protection. The
  Actions tab shows that red and the red of a run that found drift
  alike, and this sweep is the running half of section 15's audit.

- **A fallback token is what turns a missing secret into a wrong-scope
  failure much later.** `GITHUB_TOKEN` is issued for the repository the
  run is in, and what this sweep asks about is the rest of the
  organization; the workflow's `permissions:` block declares
  `contents: read`, and the Actions-permissions endpoint refuses that
  token in this repository too. No question that needs a credential is
  one the right-hand side answers, and what it bought was an error
  arriving as a traceback per repository rather than as the name of the
  secret. `GH_TOKEN` is `secrets.ALIGNMENT_TOKEN` and nothing else.

- **The refusal is a step of its own, ahead of the checkout**, in the
  shape `claude-review.yml` already uses over its own credential: an
  `::error::` annotation naming the secret, and a non-zero exit. It says
  the run measured nothing, which is what a red sentinel has to say and
  what a token failure inside the suite does not.

- **The header offered the default token as answering most of these**,
  and enumerated what it could not: the fields an endpoint omits for a
  token without push access, and none of the endpoints it refuses
  outright. What survives of that enumeration is the omissions, which a
  read-only `ALIGNMENT_TOKEN` does not see either and whose tests skip
  with the reason.

- **Creating the secret is the maintainer's** — a fine-grained token
  over the organization's repositories, read-only — so the sweep stays
  red until it exists, on one line naming what is missing rather than on
  the questions it could not ask.

### Section 1's group table has a row for `fuzz`

- **`btclib-node` declares `fuzz` and no row described it** (closes
  #476): `fuzz.yml` there runs its harness with `--group fuzz`, which is
  section 10's sentinel doing what section 10 asks of it, and
  `tests/pyproject_test.py::test_every_dependency_group_is_a_row_of_section_1`
  was red on that tree. The table is what the trees are measured against
  rather than a record of what they declare, so the standard is the side
  that moves.

- **What decides whether a tree declares it is where the engine is
  installed from**: the group, where the workflow runs the fuzzer as a
  `uv run` command; the fuzzing service's own image, where the targets
  are compiled inside one. `btclib` hands its targets to ClusterFuzzLite
  and declares no group, its `.clusterfuzzlite/Dockerfile` naming
  `base-builder-python` as what has the engine already.

- **The specifier carries the marker naming the platform the engine
  publishes wheels for.** `uv lock` resolves a specifier without one, so
  the refusal arrives at a developer's `uv sync` off that platform,
  over a group that machine never runs.

### What a repository is, it declares rather than being read off its tier

- **Section 1 read *library* off section 2's tier, and a published
  application is a shape that left no room for** (issue #365):
  `btclib-node` publishes a full node, so the tier made it a library and
  handed it a window its own `pyproject.toml` does not declare. A
  library publishes *and* declares
  `Topic :: Software Development :: Libraries :: Python Modules`, and
  every other repository is an application. The two halves are one
  question asked of the two parties to an import — whether an index
  carries the distribution for somebody else's resolver to reach, and
  what the distribution on it says it is. The record of the decision is
  `btclib-org/btclib-node#507`.

- **The alternatives are beside the rule**: a key of this organization's
  own, which would declare a second time what PyPI already has a field
  for and be read by nothing a user of the package sees; and the tier
  with the exception written in this file rather than in the tree it is
  about, which is a list to keep in step with repositories that move
  without it.

- **The price is stated where the rule is**: a library declining the
  classifier takes the application window and nothing here goes red, an
  application and a library being one shape on disk, so the rule stays a
  reading rather than a test.

- **`test_the_libraries_name_one_interpreter_window` compares the
  population section 1 names** (issue #365): it filtered on the tier, so
  `btclib-node` was among the libraries it held to one window. It
  filters on a `library` helper that reads the tier and the classifier
  together, and no tree's declarations move.

- **What decides which trees hold `interpreters_test.py` is publishing,
  and sections 3 and 15 say so.** An index shows the three declarations
  whatever the distribution on it is, so that population is every tree
  that publishes and the test is named
  `test_every_publisher_holds_the_module_that_reads_its_declarations`
  rather than narrowed to the libraries.

- **Section 15's window command prints a `kind` column** — `library`,
  `application`, or `unreadable` where either call did not answer — so
  the line a reader holds against python.org's window says which of the
  two it is instead of leaving it to be read back off the tier.

- **Section 1 says why the newest interpreter is worth being on**, which
  is the ground the decision was taken on: only `main` accepts a new
  feature, so an interpreter's own speed-ups arrive with a release and
  never with a fix to a branch already out, and a branch reaches
  `security` status years before its end of life.

### The aggregate reads its own run, not the needs context

- **Section 10 asked for a shell loop that always runs, which settles
  when the aggregate's step decides and not what it decides from**
  (closes #464): the needs context reports one result for a whole
  matrix, and btclib-org/btclib#1001 is a run where that result was not
  `failure` while cells were red and the check a merge waits for was
  green. The rule now names the run's own job listing,
  `repos/{repo}/actions/runs/{run_id}/jobs`, the `actions: read` it
  costs the job, and what each rejected reading gets wrong — a boolean
  `if:` that leaves the step skipped, a matrix collapsed to one result,
  and a `for` loop over a join that can be empty.
  `btclib-benchmarks`' `602f51d` is where the mechanism was narrowed
  by experiment rather than by argument: a cell pointed at an action
  SHA that does not exist propagates `failure`, and a download the
  runner abandoned does not.
- **The empty join has no counterpart in the shape now named** (closes
  #464): `for` splits on words and an empty string contributes none, so
  an allowlist over `join(needs.*.result, ' ')` compares nothing and
  exits 0, which is btclib-org/btclib#1454. Reading the listing leaves
  no join to be empty, and the vacuity that shape can have — a listing
  that is not this run's — is refused by requiring the run's one
  unfinished job to be the aggregate itself.
- **`skipped` passes the listing's filter for the reason it passed the
  loop's** (closes #464): a `changes` job that decides a diff touches
  nothing leaves its dependants `skipped`, the API reports that
  conclusion like any other, and a filter naming only `success` would
  fail every run a `changes` job empties, on a check a merge waits
  for.
- **A gate `release.yml` reuses through `workflow_call` has no run of
  its own** (issue #474): the caller's jobs and the called workflow's
  are one listing, every row carrying the caller's `workflow_name`, and
  the publishing jobs are unfinished exactly because they wait on the
  aggregate that would be reading it. Section 10 states the constraint
  and leaves the answer to that issue, so a reused gate keeps what it
  has until the mechanism is run rather than argued.

### A sentinel and its badge are one membership, recorded per tree

- **Section 2 gave a sentinel's badge to a tree that runs that
  sentinel** (closes #490), which is the dependency the wrong way
  round: carrying the badge is why the workflow is there, so the two
  are one membership and a tree drops both together or keeps both.
  Which trees carry which is now section 10's *Which trees carry which
  sentinel*, one entry per calendar row, and section 2's badge row
  reads its sentinels from there rather than stating a rule of its own.

- **The licence badge was every repository's and is now what
  publishing asks for** (closes #490), tier 1's for the reason
  `SECURITY.md` is: the archive leaves github.com. A repository page
  states the licence beside the README of its own accord, so on the
  page the badge sits on it restates what is there, and it earns its
  line on the index page and in an unpacked sdist, where the README
  travels without the repository around it.

- **`scorecard` followed a repository that is public and is not a fork,
  and that is now the bar rather than the key** (closes #490): clearing
  it leaves a tree able to run the sentinel, and the record is what
  says whether it does. A tree the record leaves out gives up the code
  scanning alerts the run files as well as the published score, the
  badge being the reading the row is kept for.

- **Section 15's badge sweep read a row against the tree's properties**
  (closes #490) and reads it against section 2's list and section 10's
  record instead. The calendar sweep beside it gains the reading no
  comparison of instants can make: a line for a tree that workflow's
  entry does not name, whose cron is right and whose row is not the
  tree's.

### A sweep's `paths` filter answers to the clock, not to the count

- **Section 10 made a filtered `pull_request` on a calendar workflow
  conditional on the paths being ones an ordinary branch does not
  touch, and this repository's own `alignment.yml` fails that
  condition** (closes #467): its list names `README.md`, which is this
  tree's product, so it selects nearly every branch here. The condition
  is now the wait one run adds to the checks a pull request already
  has, read off the `gh run list --json createdAt,updatedAt,conclusion`
  pair that stands beside the rule — completed runs only, a `skipped`
  or a `cancelled` one having done none of the work. How often a filter
  fires is the multiplier and not the thing multiplied, so a count of
  the branches it selects decides nothing on its own.

- **Measured that way `alignment.yml` is not the defect the count made
  it look** (closes #467): the sweep takes longer than the lint gate
  and still adds seconds to what a pull request here waits, so a list
  narrow enough to spare a prose branch would buy that branch seconds
  and leave the drift it introduces to wait for Saturday. The trigger
  and the list are unchanged; the workflow's own `paths:` comment now
  says that where a reader counting branches would ask.

### One order for the badge row and the sentinel calendar

- **Section 2 reads `github/v/release` in a pair with the PyPI version
  badge beside it, and the fixed order stated above that sentence
  separated the two** (issue #480). The order is now three groups —
  what the software is, whether it works, and what the OpenSSF makes of
  it — and the pair opens the first, so the section delivers what it
  asks for. Inside the second group the gates come first, in the order a
  commit meets them, no table fixing an order for them; Read the Docs
  joins them there, answering `passing`, `failing` or `unknown` as the
  workflow badges do and building what `docs` builds. The Scorecard
  badge leaves the sentinel run for a line of its own with the OpenSSF
  Best Practices badge, and reads as the last of the sentinels anyway
  because `scorecard` is the calendar's last row.

- **Section 10's calendar rows run family by family** (issue #480): the
  data a tree ships and did not write, the depth its suite is tested to,
  what it does against software it does not ship, what it depends on and
  what it publishes, which test is the authority for each arm of its
  code, the platforms, its own health, and its security. A table whose
  order is not stated is one a new sentinel is appended to, which would
  take the last row out from under section 2's OpenSSF line.
  `deps-latest` keeps Wednesday, which is what leaves section 10's
  closing sentence about Dependabot's Thursday true and every
  `dependabot.yml` in the organization untouched.

- **`alignment` and `links` take Saturday, this tree's own half of the
  move** (issue #480). `alignment.yml`'s `paths:` comment and
  `tests/verbatim_test.py::test_alignment_triggers_on_every_verbatim_file`
  each name the cron a pull request editing a verbatim file would
  otherwise wait for, and each names Saturday now.
  `tests/grid_test.py::test_every_cron_is_the_instant_the_calendar_names`
  names every tree still on its old instant until the ports land, and
  its docstring says so: `BACKLOG` cannot hold a row for it,
  `conftest.py` refusing one for a test that runs once rather than once
  per repository.

### Section 10 states the clock rather than quoting a header

- **The rule *what decides is the clock, not the trigger* rested on a
  quotation from `mutation.yml`'s header that named no tree** (closes
  #469): the copies of that workflow give different reasons for
  withholding the `pull_request` trigger, so a reader who opened the one
  in their own tree found an argument other than the clock with nothing
  to say they held the wrong copy. Section 10 now states the
  discriminator itself — how long one run takes — and gives `links.yml`,
  whose `pull_request` trigger is filtered to its own configuration,
  against a mutation session that runs its test command once per mutant.
  `mutation.yml` points at section 10 for its schedule and calls the
  time not its own to restate, so the quotation ran that citation
  backwards; section 9's *One fact in one place* puts the fact in the
  standard and the pointer in the workflow.

### The review job's fork comment loses its example

- **The header's reason for comparing `full_name` rather than `.fork`
  offered a branch of `btclib-org/bbt` as the case where `.fork` is
  true** (issue #456): `gh api repos/btclib-org/bbt --jq .fork` answers
  `false`. The argument stays and the example goes — what withholds the
  secret is the head repository not being this one, where `.fork` asks
  whether the head repository has a parent, so the two part on a
  repository that is itself a fork, whose own branches are handed the
  secret and which `.fork` would skip. The header reads this
  repository's own `.fork` back, which is what says the two decide
  alike here and that a swap between them would show up in no run. The
  wording is `btclib-org/bbt`'s, landed there as `btclib-org/bbt#8` and
  transcribed rather than re-derived; the remaining sibling copies carry
  the sentence this one had, and each is its own tree's landing.

### The last backlog row expired

- **`btclib-node` landed what the row excused, so the row turned its
  success into a failure** (closes #371): `test_every_test_file_is_named
  _so_pytest_collects_it[btclib-node]` reported `[XPASS(strict)]
  btclib-org/.github#371` once `btclib-node`'s `cfc43d3d` moved
  `tests/helpers.py` into `tests/__init__.py` and dropped the
  `name-tests-test` exclusion. That is the mechanism working — a strict
  expected failure is what forces an expired exemption to be noticed
  rather than left to rot — and the answer is to take the row out, not
  to relax it. `BACKLOG` is now empty, and its docstring says that empty
  is where it is meant to be rather than a state it has not reached:
  nothing here is a place a new failure belongs, a red cell being
  answered in the tree that is red.

### A sentinel is not a pull request's business

- **Section 10 said "what runs weekly does not also gate", and a job
  that runs on a pull request while gating nothing slipped between the
  words** (issue #460): the rule now says a sentinel's own *work* does
  not go on a pull request, and says why *not required* is not the free
  half of it — what a pull request charges is the wait, and a reader
  waits on the list rather than on the subset of it that gates.
  `btclib`'s `fuzz` is the case: a ten-minute exploration on every push
  to every branch, which no rule required, and which the pull request
  that cut a release was merged out from under, three minutes in.
- **What decides is the clock, not the trigger** (issue #460), which
  `mutation.yml`'s own header had already worked out and which an
  earlier draft of this section would have contradicted: written as *a
  sentinel does not run on a pull request at all*, the rule would have
  put calendar workflows of `btclib`'s own out of compliance the day it
  landed — the `paths`-filtered ones, and `integration-bitcoind`, whose
  regtest job is a required check that blocks a merge if it never runs.
  So the rule is what the clock says: the filtered trigger stays, the
  hours-long job stays off a pull request, `workflow_call` and
  `push: branches: [main]` are outside the
  question, and an unfiltered `pull_request` states its reason in the
  header as `codeql` and `integration-bitcoind` do.
- **Section 10's `fuzz` bullet did not say where the regression half
  lives**, so a tree taking the fuzzer had a reason to reach for a
  `pull_request` trigger to get it (issue #460): the bullet now says
  the regression is an ordinary test of the suite, and says where it
  does *not* go — `fuzz/corpus/` is a seed corpus, and `btclib`'s
  `tests/fuzz_corpus_test.py` asks that every seed there is still a
  valid serialization, so a crash input put in it is refused by the
  hardening that fixed the crash. The bullet says what that seed gate is
  worth rather than overstating it: acceptance by one of the entry
  points the harness declares, not by the intended one — the module
  names the harnesses where a narrowed parser passes because a sibling
  still accepts the seed. What is left to the sentinel is the question a
  corpus cannot hold, which is the one it was added for.

### The fork filter comes back, and section 10's fork half loses its example

- **`names()` asked the API for every unarchived repository, forks
  among them** (closes #454): the filter is back —
  `select(.archived == false and .fork == false)` — `btclib-org/bbt`,
  the repository it had been suspended for, being a fork no longer. Its
  docstring keeps the argument for excluding a fork and the half of it
  that does not hold for a fork the organization has taken over, says
  that what the filter asks about is a state rather than the route a
  repository took to it, and carries the command answering that the
  organization holds no fork, so that a line selecting nothing out reads
  as the guard it is. The citation of `btclib-org/bbt#13` goes with the
  tracker that held it, the recreated repository resolving no such
  number and the request it carried being moot.
- **Section 10's `scorecard` bullet named `bbt` as the fork the rule
  excludes** (closes #454): the fork half has no instance in the
  organization, and the bullet says that rather than dropping the
  clause, keeping `ossf/scorecard-action`'s own documented limitation
  as the reason it is a rule at all. `bbt` is inside the rule and owes
  the sentinel, which is btclib-org/bbt's own work to land.
- **The `BACKLOG` row excusing `btclib-node` from section 5's `D`
  selection outlived what it excused** (closes #454): the row is gone,
  `test_d_is_selected_with_the_pep257_convention` passing on every
  repository the suite asks it of, and a strict xfail over a passing
  test being red here.

### Section 7 answers the suite-shape questions

- **A suite that waits on anything outside its own process carries a
  measured per-test timeout** (closes #425), the bound measured against
  its own slowest test on a loaded machine, and the workflow's
  `timeout-minutes` told apart from it: that one names a wedged runner,
  the per-test bound a wedged test. A suite of pure functions does not
  owe one.
- **A tree that owes section 10's fuzzer owes a property layer first**
  (issue #426), keyed on the same property, with hypothesis's profile
  shape stated once — registered in `tests/conftest.py`, the default's
  cost measured, the deep profile opt-in — and a hand-rolled answer
  declared in `tests/README.md`.
- **`tests/functional/` sits beside `integration/`** (issue #427) for a
  suite whose subject is a running process, on terms: `unit/` carries
  the mirror, every directory is in `testpaths`, and the split is
  declared in `tests/README.md`. The two directories are told apart by
  what they need rather than by how long they take.
- **A suite that declines `pytest-randomly` declares it** (issue #428)
  in `tests/README.md` with the reason, weighed against what the plugin
  catches rather than against what it costs — an ordering plugin not
  being that reason by itself.
- **The `_data` underscore is `tests/_data/`'s alone** (closes #441): a
  data directory beside the package or the script takes the name that
  says what it holds, the mark buying nothing where no sibling of it is
  a package.

### Section 8 keeps one copy of the flags and section 10 ungates the sentinels

- **The flags live in `pyproject.toml`, and a job types `pytest` with
  nothing after it** (issue #433), the two job-own arguments named — a
  sentinel's `--no-cov` and a combining job's `COVERAGE_FILE` — so the
  local gate and the CI gate stay one measurement.
- **A sentinel cell that runs the suite passes `--no-cov`**
  (issue #429): the floor is section 8's claim about one interpreter on
  one image, and the day a platform sentinel finds the branch it
  watches for, a cell gating the floor would go red naming the wrong
  claim.
- **Coverage configuration is read from wherever the run starts**
  (issue #443): run from `tests/` a suite reads none of it and passes
  ungated, so a tree with a local floor points such a run at its
  configuration or makes it say it is ungated, measured per tree.

### The standard answers the campaign's decision issues

- **The qualifier does not stand in for the keyword** (closes #413):
  section 9 names `(owner/repo#N)` with no `closes`/`issue` before the
  number as the rejected alternative it is, failing the falsifiability
  the pair exists for exactly as the bare form does; entries already
  landed in that form stay, the append-only rule being why.
- **The verb is checked against the forge's own parse** (closes #421):
  section 11 carries the `closingIssuesReferences` command and reads a
  `closes` missing from its answer, or an `issue` present in it, as
  wrong on the parser's own evidence — a correct title being no
  evidence for the citations beside it. The stable zero is named there
  too (closes #451): one that survives spaced reads is a parse that
  never ran, and an edit resubmitting the body is what re-triggers it.
- **A count that expires inside a landed entry stays there** (closes
  #408): the entry speaks of the day its heading dates, the change that
  moves the population is what gets the new entry, and what the
  no-counts rule forbids is writing the next such sentence; a structure
  the entry itself names is a description the rule does not reach.
- **`CONTRIBUTING.md`'s badge block gets its rule** (closes #445): the
  block's own first line is the admission rule, membership is a
  function of the file's own sections rather than a curation, the
  repository link is the one badge of the *place to go* clause and
  travels with the block, and a tree without a block owes none.
- **A cross-repository sentinel takes its row first** (closes #401):
  section 10 and `tests/grid_test.py`'s docstring say one pull request
  can land both halves only where the first tree is this one; elsewhere
  the row lands with the adoption, the expected red in between is the
  row-existence test, bounded by the issue filed against the tree that
  owes the schedule.
- **Section 12 states the wrapper exemption** (closes #352):
  `btclib-secp256k1` versions by the libsecp256k1 it wraps, the reason
  written in the rule rather than left in that tree's `README.md`
  alone, the exemption re-argued here by any future wrapper, and its
  fourth component told apart from the broken-release one.
- **The badge row admits the OpenSSF Best Practices badge** (issue
  #350): a new property, *registered at bestpractices.dev*, last in the
  fixed order — admitted where REUSE's badge stays refused because its
  render is the questionnaire's live state, the same fact the
  Scorecard's `CII-Best-Practices` check scores.
- **The concurrency ceiling's figure has one home per tree** (issue
  #412): `REPOSITORY.md`'s *Plan-gated settings*, beside the command
  that re-derives it; a workflow header or `CONTRIBUTING.md` states the
  reasoning unnumbered and points there, a date beside the figure being
  no cure. The statements still standing in the trees are that issue's
  worklist.
- **`check_vendored_vectors.py` is owed a scope header, not a
  comparison** (issue #446): section 14 says each copy parses the pin
  file its own tree keeps, so the bytes differ by subject, and what
  every copy owes is the header sentence naming what it parses and
  where it departs from its siblings — owed still where a copy lacks
  one, which is why the issue stays open.

### Section 11 puts the keyword on one line and the subject on one line

- **A subject is one physical line** (closes #403): `%s` joins a
  wrapped subject where the squash does not, so the truncation it hides
  is read off the first line of `%B`, and *Merge method* now says so
  with the command.
- **The keyword and its reference share a physical line, and a block of
  several is written one keyword per line** (closes #420), the shape a
  wrapper cannot split; what catches a loss is counting
  `closingIssuesReferences` against the number intended, the failure
  being stable rather than a lag.
- **A title citing several issues joins them for the reader, and the
  parser binds the verb to the first** (closes #437) — costless where
  the description carries every keyword; a commit that had to close on
  its own subject repeats the verb per reference, and everything
  reaches `main` through a pull request whose description is what
  closes.

### Section 15 marks a failed fetch wherever a filter would swallow it

- **The badge-render command reads its `README.md` through
  `read_or_mark`** (closes #419), so a call that did not answer prints
  `README.md unreadable` where a file carrying no badge prints nothing.
- **What decides which command owes the marker is the filter, not the
  sweep** (closes #419). `gh api` puts a failure's body on stdout and
  exits non-zero, so the settings block at the top of the section
  reports its own failure by printing what it fetched; a `sed` that
  selects lines drops the body and hands on its own exit code, and that
  is a shape a single repository's answer shares with a sweep's row.

### Section 15's pins sweep finds the file wherever section 7 puts it

- **The sweep asks the tree for its `README.md` paths** (issue #434)
  rather than reading `tests/_data/README.md` and falling back to
  `tests/README.md`. Section 7 puts the pins in the data directory and
  that directory beside whatever reads it, which is a script rather than
  the suite in some trees, so a fixed pair of paths opens neither the
  file that holds the pins nor anything that says so. The root
  `README.md` is passed over: it is section 2's, and this one carries
  section 7's block as the shape to write.
- **`pins` names the file the block came from, and `none` where no file
  of the tree carries one** (issue #434). A zero read as a tree with no
  data to vendor, which is equally what a tree whose provenance is
  written some other way leaves; the sweep says it cannot tell those two
  apart and names the reading section 7 asks of `tests/README.md`.

### Section 8 measures a selection against `testpaths`, and reads `--lf` as one

- **A path is a selection only where it leaves a `testpaths` entry out**
  (issue #424). `pytest tests` names what a bare run already collects,
  so a hook reading any path as a subset switches the coverage floor off
  for the run that is the suite; the hooks that read it that way are
  owed their own fix (issue #430). The paths are
  `config.option.file_or_dir`, which is `None` and not `[]` under
  `--help`, so a containment test that iterates it ends `--help` in a
  traceback.
- **`--deselect`, `--ignore`, `--ignore-glob` and `--lf` join `-k` and
  `-m`** (issue #424). Such a run measures the same source with fewer
  tests, so what its report is short of is the tests it did not run: a
  shortfall it reports cannot be told apart from one the tree has, and a
  gate whose red cannot be read teaches whoever runs it to reach for
  `--no-cov`.
- **The narrower reading sits beside it** (issue #424): those flags are
  an iteration's, whose next run is the whole suite, and reading intent
  off all of them makes the hook a second definition of what a real run
  is. What the wider set costs is the run that would have cleared 100
  anyway, a `--lf` with nothing to rerun; an early `-x` is outside the
  set either way.

### Section 9 says the union driver is a checkout's, not the forge's

- **`merge=union` is a checkout's driver, and the forge does not apply
  it** (closes #406). A pull request whose `CHANGELOG.md` or
  `RELEASE_NOTES.md` overlaps its base is reported `CONFLICTING` however
  cleanly `git merge-tree --write-tree` resolves the same pair under the
  driver, and a rebase on a checkout is what clears it. So the driver's
  price is one thing locally, where the same entry edited on two
  branches merges in silence, and another on the forge, which refuses
  the branch until it is rebased. `UNKNOWN` from `gh pr view --json
  mergeable` is the forge still computing the merge rather than an
  answer, and is asked again.

### Section 11's closing keyword fires on the reference beside it

- **The gloss for a mention that must not close drops its ellipsis**
  (closes #414): `<verb> owner/repo#N`, with the verb immediately in
  front of the reference, which is what the rule's own *no verb beside
  it* says and what both of the precedents it rests on show. The wider
  reading — a keyword verb anywhere ahead of the number — condemns a
  shape the parser does not act on, and a sweep written to it reports
  landings that closed nothing.
- **An issue's timeline is what measures the parser** (closes #414).
  `c6c1657` and `214ed5f` each carry a keyword verb further up the
  sentence than the reference and entered their issue's timeline as
  `referenced`, where `592f1bc`, whose verb sits directly in front of
  the number, entered `#81`'s as `closed`. Where the distance is in
  doubt the answer is `closingIssuesReferences` for the pull request in
  hand rather than a wider rule.

### Section 15's multi-field sweeps mark a call that did not answer

- **A sweep reading another repository's file writes `unreadable` into
  the field the call would have filled** (closes #397), where a blank is
  what a repository owing nothing leaves. The interpreter window marks
  its columns one at a time, so a `pin` that answered stands beside a
  `floor` that did not, and `matrix` carries the marker among version
  strings where one workflow of several could not be read; the uv
  floor's `floor=` gains what its `lock=` already had.
- **A sweep that prints a line only where it has something to say prints
  one naming what could not be read** (closes #397), having no field to
  mark: the cron calendar, the Dependabot day and section 2's badge row.
  The badge row belongs with them because a fetch that fails there reads
  as a `README.md` carrying no badge, which is the defect in the shape
  the other two have.
- **The three values are one shell function the sweeps share** (closes
  #397), so a sweep reads a failed call the same way wherever it is
  added.

### Section 11 names the citation a port of `claude-review.yml` adapts

- **The prompt's citation of the standard is a third thing a port
  adapts** (closes #396), and the only one that is not a claim about the
  receiving tree. This repository's copy cites `README.md`, this being
  the tree that holds the rules a finding is written against; everywhere
  else `README.md` is what that repository is to whoever arrives at it,
  so a citation carried over verbatim names the wrong file.
- **A receiving copy names section 11 where section 11 holds the rule
  cited, and the standard with no section number where it does not**
  (closes #396); the subsection form, `section 11's *Review*`, is for
  wherever a subsection does hold the rule. What chooses the shape is
  what holds the rule and never where the sentence sits, since the two
  secret stores a Dependabot-initiated run reads are stated in the
  section's own prose and in *Dependabot and pre-commit.ci*, so a
  citation of them names no subsection wherever it falls. Naming
  section 11 for a rule that sits elsewhere in the standard is precise
  and wrong, that section being *GitHub settings* where a finding about
  the prose cites section 9.
- **Section 14 points at section 11 rather than restating the
  asymmetry** (closes #396). The sentence it replaced had a receiving
  copy naming section 11 where this repository's copy names
  `REVIEWING.md` and `CONTRIBUTING.md`'s last section directly, and a
  receiving copy names those two directly as well.
- **This repository's own `claude-review.yml` cites `README.md` at every
  site** (issue #400). Two of its comments carried a receiving copy's
  form, in the copy that is the standard.
- **The `claude_args` comment names the `gh pr` subcommands the file
  passes** (issue #398) -- `diff`, `review` and `view`.
- **The `mention` job refuses a missing credential in the words of the
  job it guards** (issue #402), that job answering an `@claude` mention
  and reviewing nothing.
- **The comment above that step points at the review job's reason
  instead of restating it** (issue #410), the restatement having
  narrated a measurement made on the review job -- a token found empty
  and a review reported successful -- inside the job that reviews
  nothing. Both strings are `portanode`'s, taken from its blob.

### CLAUDE.md names the docs gate a changelog diff reaches, and the Opus case

- **A sibling tree's documentation build reads its `CHANGELOG.md`, so a
  changelog-only diff does not exempt its docs gate.** `docs/source/changelog_link.md`
  pulls `../../CHANGELOG.md` through a MyST `include` and the
  toctree lists it, under `-W`, in each of the five repositories that
  have a documentation build; the three that do not have no `docs/` at
  all. The bullet carries the `git grep` that answers per tree and the
  `README.md` control that says its zero is an absence. The reasoning it
  refuses — *`docs/` is unchanged, so the docs gate has nothing new to
  read* — is a true sentence answering the wrong question, what the tool
  reads rather than which of its inputs moved.
- **A port of one file into every repository is a change to what the
  standard says**, so section *Model*'s Opus condition covers it. Trees
  each deriving a convention for themselves land different answers and
  file an issue per divergence; one sentence written before the ports go
  out is what settles it, and a campaign that begins on Sonnet finds
  itself rewriting a section with branches already pushed against the
  answer it had then.

### The calendar gains a row for fuzz, the ClusterFuzzLite sentinel

- **`fuzz` takes Monday, 03** (issue #372). `04` and `05` are full on
  every day; `03` is free on every day but Saturday, where `scorecard`
  already holds it. Monday is chosen to land on a different day from
  `scorecard`'s own Saturday.
- **The row does not make `tests/grid_test.py` green** (issue #372). No
  tree yet carries a `fuzz` `schedule:` block; `btclib`'s `fuzz.yml`
  gains one in a follow-up pull request, at this row's instant --
  minute 04, so `4 3 * * 1`.

### Section 10 states the interpreter exception and refuses a schedule's timezone

- **An interpreter axis is a gate cell exactly where its extra cell runs
  in parallel with the ones already in the job and claims no interpreter
  the package does not already claim** (closes #390). `btclib-node`'s
  `test.yml` is the first tree to take the trade, running `3.14` and
  `3.14t` as parallel cells of its `coverage` job; where either
  condition fails, the row belongs in the weekly calendar instead, on
  the same trade that keeps a platform row there.
- **A `timezone:` beside a `cron:` fails `tests/grid_test.py`'s
  `schedules()` outright** (closes #355), rather than being read and
  ignored or converted, so a schedule cannot leave the calendar's UTC by
  declaring one.
- **`grid_test.py`'s docstring pointed a reader at a `BACKLOG` row
  `conftest.py` refuses for a cross-repository test** (closes #348). It
  now says a row takes its place in the pull request that gives the
  first tree the workflow, which is what section 10 already states.

### Section 15 tells a failed call from an answer

- **Section 15's `uv.lock`, `release.yml`, `claude-review.yml` and
  `vendored-vectors.yml` existence checks each folded a failed `gh api`
  call into the same reading a genuine absence gets** (closes #319):
  `--silent`'s failure fed the negative branch either way, so a rate
  limit or a bad token read as `no`, as `none`, or as the file being
  missing, exactly like a repository that genuinely lacks it.
- **Each now captures the call's own stderr and reads `(HTTP 404)` out
  of it** (closes #319), the signal that tells a genuine absence apart
  from every other failure. The private vulnerability reporting sweep
  needed no such capture: that endpoint has no legitimate absence of
  its own, so its `unreadable` already covers every failure. Anything
  else here prints `unreadable` rather than the negative reading.
- **A repository this loop names but the endpoint cannot find still
  answers `(HTTP 404)`** (closes #319), which this shape does not
  close: GitHub's contents API gives a moved path, a stale roster entry
  and a genuinely absent file the same status.
- **The `SECURITY.md` sweep and the vendored-data pins sweep pipe a
  fetch through `base64 -d 2>/dev/null`, where a failed fetch decodes to
  the same blank a genuinely absent file does** (closes #319); both are
  the same defect on the question the issue left open, and both now
  tell the two apart the same way as the boolean sweeps.

### Section 16 points at section 14 instead of naming its files

- **Both of section 16's checklists named the lint-tool configuration
  files section 14 already lists** (closes #388): `.markdownlint.jsonc`,
  `.yamllint.yaml` and `.taplo.toml`, the files kept by the tools whose
  configuration is not in `pyproject.toml`. A file section 14 gains
  later would have reached neither checklist.
- **Both now point at section 14 instead**, in the shape #377 gave
  section 3 (closes #388). `.gitattributes`, `.python-version` and
  `.gitignore` stay named in the new-repository step: section 14 lists
  the first, reads `.python-version` as decided per repository, and
  says nothing at all about `.gitignore`, so none of the three is
  section 14's list to point at instead.

### `typos` is a local hook now, out of reach of `autoupdate`

- **Neither `ci: skip:` nor any per-repository key in pre-commit's own
  config stops `autoupdate` from touching one `repo:` entry** (closes
  #393): `skip:` only excuses a hook from running, and a `repo:` entry
  takes no field of that kind at all. `crate-ci/typos` re-tags a moving
  `v1` alias onto the same commit as each release, `git describe --tags`
  breaks the tie between the two by creation date and names the alias,
  and `autoupdate` proposed it on every run — with `pinned-rev` above
  refusing it on every run in turn, so the pin stayed stuck rather than
  moving.
- **`local` and `meta` are the two `repo:` values `autoupdate` filters
  out before it walks the rest** (closes #393), so the `typos` entry is
  now one. `additional_dependencies: [typos==1.49.0]` carries the
  version pin in place of `rev:`, and `language`, `entry`, `args` and
  `types` are upstream's own hook definition, copied in rather than
  fetched. The other repositories of the organization still pin
  `crate-ci/typos` through `rev:` (issue #399), which section 14 does
  not compare and section 15 has no command for.

### The ack of record is a COMMENT review, and the workflow is inert

- **The verdict has three lines** (issue #340). `ACK <sha>` and `CHANGES
  REQUESTED <sha>` are joined by `NACK <sha>`, Bitcoin's sense of the
  word: the disagreement is with the change itself, so no alteration is
  asked for, where `CHANGES REQUESTED` is a change right in principle
  and wrong as written. `REVIEWING.md` carries the three lines and says
  why a `NACK` and a review that ends without a verdict are not the same
  thing (issue #353).
- **The ack of record is posted as a review of type COMMENT** (issue
  #340), and never as a forge approval or a forge request for changes.
  `can_approve_pull_request_reviews` is false on the organization and on
  this repository, which closes the route a `GITHUB_TOKEN` would take.
  The action posts under a GitHub App's own identity rather than that
  token, so what forbids `--approve` on the route actually taken is the
  prompt; section 11 states both in place of the self-approval refusal,
  which reaches an author and not a workflow.
- **What that leaves unrecovered is the OpenSSF Scorecard's
  `Code-Review` check** (issue #340). A COMMENT review is in
  `pulls/<n>/reviews`, so the forge holds a record of the review the
  standard requires, and it is not an approval. An approving review from
  this workflow would not have recovered the check either: Scorecard's
  own documentation says a review by a bot, one powered by a model
  included, does not count as code review.
- **`claude-review.yml` is present and neither of its jobs runs** (issue
  #340). Both carry `if: vars.CLAUDE_REVIEW_ENABLED == 'true'`, an
  organization variable that does not exist, and an undefined `vars.X`
  is the empty string — so absence is the off state and creating the
  variable is the whole of the activation. The gate is on the job
  because a step-level one leaves the review step's outcome `skipped`,
  which the guard beside it reads as a review that never ran and reports
  as a red check on every pull request.
- **The verification step reads `pulls/<n>/reviews`** (issue #340) and
  matches the three verdict lines. The reviews and the issue comments
  are two stores rather than two views of one, so a review posted with
  `gh pr review` is in the first and in neither of the second.

### The review guard reads the SDK result the action's log leaves out

- **A review that dies inside the action names no cause** (issue #364).
  The log carries a summary of the SDK's result message with the error
  text and `api_error_status` sanitized out of it, where the execution
  file the guard step already names carries that message whole, so the
  guard reads it from there where the review step did not succeed.
- **`show_full_output: true` was the alternative** (issue #364): it
  prints every message including tool results, which the input's own
  description warns against on a public repository. The debug rerun the
  action's log suggests beside it keys on `ACTIONS_STEP_DEBUG` in the
  step's environment, which `gh run rerun --debug` does not put there.
- **This does not make a failing review pass** (issue #364): what the
  guard gains is the name of a failure the log does not carry. Nothing
  in these repositories changed across the moment the runs turned red —
  the action's pin, the model, the SDK and the CLI are the same on
  either side — which is a narrower claim than the cause lying outside
  them, and the field this guard now reads is what tells the two apart.

### The review header's cheapness clause no longer leans on being the only job

- **The header said the review was cheap because it is the only job in
  this repository** (closes #391). It is not: `.github/workflows/`
  holds jobs beyond it, `claude-review.yml` itself among the files
  holding more than one. The header now gives the reason on its own
  terms — it reads a diff of prose, it builds nothing, and it skips a
  draft — instead of through a uniqueness claim.

### Section 3 points at section 14 instead of listing the tool files

- **Section 3 said how many tools keep a configuration file of their
  own, and named yamllint and taplo** (closes #377). `markdownlint-cli2`
  answers that sentence's own criterion — it reads a file found by name
  from the working directory, and `pyproject.toml` is not among the
  names it looks for — so one file that the rule covers was outside the
  sentence stating it.
- **The criterion is discovery, and not whether a tool can read
  `pyproject.toml` at all** (closes #377). `markdownlint-cli2` reads a
  `[tool.markdownlint-cli2]` table where `--config` and `--configPointer`
  point it at one, so what a file of its own buys is the flag pair the
  hook then does not pass.
- **What section 3 keeps is the rule and the reason for it, not the
  enumeration** (closes #377). Section 14 names each such file with what
  it holds, so section 9's *One fact in one place* puts the list there
  and a pointer in section 3, and a file added later is entered where
  the others' contents already are. Raising the count instead would have
  left the same sentence one tool later, which section 9's *Measure,
  don't assert* refuses.
- **`CLAUDE.md`'s `pyproject.toml` bullet points at section 14 too**
  (closes #377), in the shape `REPOSITORY.md` uses for
  `CONTRIBUTING.md`'s *A version, and no release*.

### Section 2's badge row drops the link to the repository

- **The link to the repository is no longer a badge every repository
  carries.** It goes from the property list that decides membership and
  from the fixed order, which now ends on Read the Docs, and it is named
  in what section 2 refuses: a badge row is an audit, and this one
  renders the repository's name because its own URL spells it.
- **What that gives up is the reader who is not on the forge** — a
  `README.md` met as the long description an index renders, or as the
  file an unpacked sdist carries — and that reason had a paragraph of
  its own, which goes with the badge rather than outliving it. Section
  3's `[project.urls]` reaches that reader without a badge: `repository`
  is a `Project-URL` line in the sdist's own `PKG-INFO` and a field the
  index serves.

### `REPOSITORY.md` records the tag ruleset and who squash binds

- **The recorded rulesets were short of one** (closes #376). The call
  that section writes answers `tag-integrity` as well, and it now asks
  for each ruleset's ref condition, which is where `refs/tags/v*` is
  read from rather than asserted. The `pull_request` parameter block the
  second call answers carries `dismissal_restriction` and
  `required_reviewers`.
- **What that ruleset is for on a repository that cuts no release is
  beside it** (closes #376). The paragraph points at `CONTRIBUTING.md`'s
  *A version, and no release* for nothing being tagged, and says the
  rule stands ahead of the tag rather than being created alongside one.
- **The release bullet offered "no tag to protect" as an absence**
  (closes #376). Under a heading saying what is not configured, that
  reads as the reason `refs/tags/v*` is unprotected, where what is
  absent is the tag.
- **The squash constraint was recorded as holding against a flipped
  repository setting, without saying for whom** (closes #375).
  `allowed_merge_methods` is a parameter of the rule the maintainer
  bypasses, so what refuses a merge commit for everybody is
  `main-integrity`'s `required_linear_history`, and rebase-and-merge is
  linear.
- **The bypass was not exercised** (closes #375): offering it a merge
  method the ruleset excludes means flipping `allow_rebase_merge` and
  pressing the button on a live pull request, which is a settings change
  and a landing rather than a call.

### Section 11 says what the `pull_request` bypass suspends

- **The paragraph had the bypass answer nothing beyond the approval**
  (closes #368). What it excuses is the rule of that type, and
  `dismiss_stale_reviews_on_push` — the forge's refusal of a merge whose
  head has moved past its approval — is a parameter of that rule, so the
  refusal reaches every merge except the ones made under the bypass.
  GitHub's description of the mode and of the setting is linked on the
  words that assert it.
- **The `sha` on `CONTRIBUTING.md`'s merge call is named as what stands
  in its place** (closes #368), the pin otherwise reading as a second
  guard over a forge rule that would have refused the moved head anyway.
- **`REPOSITORY.md` quoted the parameter with nothing beside it**
  (closes #368), which reads as a guard this repository's own landings
  have. The block now carries what the bypass does to it and points at
  section 11 for the rest.
- **The bypass was not exercised**: doing so means merging a head nobody
  acked against a live pull request of this organization, which is the
  outcome the paragraph is about. What is measured is the ruleset's own
  shape, read back from the endpoint `REPOSITORY.md` records.

### Section 4 says what `codespell --version` reports

- **The spelling bullet says why that string names no release, and what
  recovers the release from it** (closes #346). The version is
  `setuptools_scm`'s reading of the clone pre-commit builds the hook
  from, which carries no tag to describe, and the string's last field is
  the commit the `rev:` resolved to.
- **Section 15 was the alternative** (closes #346), that being where a
  claim about the repositories sits beside the command re-deriving it.
  What a command there prints is a finding a repository can answer for,
  and no repository can deviate here: the string is decided by how
  pre-commit installs the hook, which is the spelling bullet's subject.

### The calendar gains a row for scorecard, the OpenSSF Scorecard sentinel

- **`scorecard` takes Saturday, 03** (issue #363). `04` and `05` were
  full on every day, so `03` is the next hour the band grows into; `03`
  is free on every day, and Saturday is `ossf/scorecard-action`'s own
  upstream default day.
- **The row does not make `tests/grid_test.py` green** (issue #363).
  `portanode`'s `scorecard.yml` still runs with no `schedule:`, waiting
  on this row before it adds one in a pull request of its own, and
  `btclib-benchmarks`'s own `scorecard.yml` already schedules the
  workflow on `ossf/scorecard-action`'s upstream default cron rather
  than on this row's instant —
  `test_every_cron_is_the_instant_the_calendar_names` was already
  red on that cron before this row existed, naming it a workflow
  section 10 had none for, and stays red after, naming it a cron
  that disagrees with the row now that one exists.

### Section 12's worked answer names no package path

- **`bitcoin-core-rpc`'s worked answer quoted the value of `package`**
  (closes #321), which a move of the package directory falsifies while
  the sentence around it stays true. The answer now names what the flag
  points at — that repository's package directory — and section 15's
  tree command reads the value off the `pyproject.toml` that holds it.
- **Correcting the literal was the alternative** (closes #321), and what
  it buys is a sentence right until the next layout change. The
  paragraph already says its answers are re-derived by section 15's tree
  commands rather than taken on trust, so the value has a place that
  reads it and a copy here is the second statement of one fact.

### The `BACKLOG` row for `btclib-node`'s test-file naming cites an open issue

- **The row excusing
  `test_every_test_file_is_named_so_pytest_collects_it` for
  `btclib-node` cites #371** (closes #367). `conftest.py`'s `cited()`
  writes a row's number into the strict expected failure's reason, so
  that number is where a red cell sends a reader, and a closed issue
  sends them to a record that holds nothing. What the row excuses is
  `btclib-node` keeping its shared test code in `tests/helpers.py` and
  excluding that path from `name-tests-test`, which is what #371
  records.
- **The gap is filed in this tracker rather than in `btclib-node`'s**
  (closes #367). *What this repository is* files an alignment finding
  here, and a row names a tuple of repositories, so an issue belonging
  to one tree could not be cited for a second tree's cell in the same
  row.
- **`BACKLOG`'s docstring names the tracker a row's number is from.**
  What spells a row's number is `conftest.py`'s `cited()`, a file away
  from where a row is written, and the trees this suite measures number
  their own issues in the same range as this one.

### `CONTRIBUTING.md`'s merge command pins the head that lands

- **The command merged whatever sat at the head when it ran**
  (closes #360). *Landing it* now passes the merge endpoint's `sha`,
  the head the checks were read on: checking the ack and merging are
  two calls, and the push that moves the head between them comes out
  of the same round the verdict does. The endpoint is documented to
  refuse a mismatch rather than land it, so a head that moved costs a
  round instead of putting an unreviewed tree on `main`.
- **The argument sits beside the parameter rather than in the issue that
  filed it** (closes #360): the file already anchors a review's exchange
  to a sha, and section 11 already has an ack name one, so an added
  parameter reads as a keystroke until a sentence says which rule it is.
- **The other trees' copies are btclib-org/.github#281's** — the issue
  that tracks a shared half this tree is ahead on, which
  `tests/verbatim_test.py`'s `EXPECTED_DRIFT` already names for this
  path.

### `CONTRIBUTING.md` names the two spellings of an issue citation

- **Its *Pull requests* names `(closes #N)` and `(issue #N)` rather than
  only the section that defines them** (closes #332). The shared half is
  what a contributor of every tree reads, where a pointer reaches
  whoever follows it, and the forms are the half a citation is got wrong
  in. The price is section 9's *One fact in one place*, taken
  deliberately and stated in the sentence that takes it: a change to the
  pair is then an edit here as well as in `README.md`.
- **The other trees' copies are btclib-org/.github#281's** — the issue
  that tracks a shared half this tree is ahead on, which
  `tests/verbatim_test.py`'s `EXPECTED_DRIFT` already names for this
  path.

### Section 2 gives `btclib-node` the tier its tree measures

- **`btclib-node` is tier 1** (closes #351). It holds
  `.github/workflows/release.yml`, which is the file the loop beside
  section 2's table reads to tell a publisher from a Python project that
  publishes nothing, and the row said tier 2.
- **The paragraph keeping `RELEASING.md` out of a tier-2 tree names no
  repository** (closes #351). It listed the trees that state the absence
  of a release under their own `CONTRIBUTING.md`'s *A version, and no
  release*, so a promotion made the list wrong without anything in this
  file being touched; the sentence now says that of a tier-2 repository
  rather than of the trees that were tier 2 when it was written.

### Section 2 states the badges at a `README.md` head

- **Nothing said which badges a `README.md` carries** (issue #338).
  Membership is now a property of the repository: the licence in its
  derived form, the `lint` workflow and a link to the repository in
  every tree; the index badges where the tree publishes; `test` where it
  holds a suite; `docs` and Read the Docs where it builds documentation;
  pre-commit.ci where it is on it; and a badge for each sentinel it
  runs. A curated list has no answer to whether a given tree should
  carry a given badge, which is what let one file open a different way
  in each tree. What it gives up is the head as a summary: a badge per
  sentinel means the row grows with section 10's calendar, and this
  repository, which opens with none, acquires one.
- **The order is fixed, and the sentinels take section 10's calendar
  order** (issue #338): one order to maintain rather than two, at the
  price of a workflow moved to another day moving its badge in every
  `README.md` that carries it.
- **A badge answering with anything but a measurement is a question
  with two answers** (issue #338): the thing it reads has not happened
  yet, which is datable and not a defect, or it should have and did not.
  Which of the two is a reading and not a pattern — each service says so
  in its own words, a workflow badge `no status`, pre-commit.ci and Read
  the Docs `unknown`, the Scorecard `invalid repo path`, shields a
  phrase per family — so section 15's loop prints the status code and
  the message rather than judging, and only a badge not served at all is
  decided by the command.
- **Section 15's first badge loop reads the source and not the alt text**
  (issue #338), the alt text being prose its author chose:
  `bitcoin-core-rpc` writes `license: MIT` over the hand-written badge
  the rule refuses by name, so a loop reading alt text reports a licence
  badge and stops.
- **What is refused, each with its reason** (issue #338): a badge
  asserting a tool rather than measuring one, which renders the same the
  day the tool is removed; the hand-written licence badge, which renders
  `MIT` because its URL says so where the derived form renders it
  because `LICENSE` does; `last-commit`, `commit-activity` and
  `contributors`, which measure activity rather than the tree; a
  coverage badge, which restates what section 8's floor enforces in
  exchange for an upload to a third party; and REUSE compliance, which
  renders `unregistered`; and `img.shields.io/pypi/types`, which reads
  the `Typing :: Typed` classifier rather than the wheel — `urllib3`
  ships `urllib3/py.typed`, declares no such classifier and renders
  `untyped` — so it restates a classifier section 3 already pairs with
  the marker by rule. `wheel` and `implementation` stay: `iniconfig`
  names no `Implementation` classifier and the badge renders `cpython`
  for it, so those two are read off the files a release uploaded.
- **Read the Docs is `app.readthedocs.org`** (issue #338), the other
  spelling answering `307` and redirecting to it.
- **The downloads badge is pepy's** (issue #338), and the reason is not
  that `img.shields.io/pypi/dm` fails to render, since it does: what it
  renders is a month, which falls without anything having happened to
  the tree, where pepy answers with the project's whole life. What that
  gives up is the reading `pypi/dm` is better at.

### Section 2 states what the documentation is built with

- **The `docs` group named "the theme" and never which one** (issue
  #329). It names `furo`, which is built for a reference generated from
  the docstrings of a typed public API with a few pages of prose around
  it. The alternative weighed was `shibuya`, whose announcement bars,
  landing pages and `sphinx-design` components are the reason against
  it here: they are surface these trees would carry and not use, and
  that surface is what choosing `furo` gives up.
- **`sphinx-build -W` does not see a cross-reference that resolves to
  nothing** (issue #324), so a renamed class in a `:class:` role leaves
  the build green and the link dead. Section 2 states `-n` alongside
  `-W`, and section 16's checklist with it.
- **`sphinx.ext.intersphinx` comes before `-n`** (issue #324): sphinx's
  own domain answers for the builtins, so `int` and `bytes` are silent
  without a mapping, but `collections.abc.Sequence`, `pathlib.Path` and
  `os.getcwd` each draw a `reference target not found` with nowhere to
  look — measured on the sphinx the trees pin. Turning `-n` on first
  therefore measures the standard library.
- **`nitpick_ignore` holds only entries whose reason is written beside
  them** (issue #324). Every entry is a reference the build stops
  checking, so a broad `nitpick_ignore_regex` buys a green build by
  giving up the check itself.

### Section 10 says which trees owe which sentinel

- **Mutation testing followed publishing, and the property is holding a
  suite over code the tree ships** (issue #327). A floor at 100 says
  every line ran and nothing about whether an assertion would have
  noticed the line being wrong, so the sentinel is worth most where the
  floor is highest — which reaches `btclib-benchmarks`, that publishes
  nothing. What owes it nothing owes it for one reason: a mutant needs
  code of the tree's own to change, which `bbt` has no suite over and
  `.github` has none of, its suite being over the other repositories.
- **Nothing gave an outside opinion of supply-chain posture** (issue
  #339). `scorecard` is a sentinel a public repository that is not a
  fork owes — `ossf/scorecard-action` does not support a fork, and
  `bbt` is one — and a check scoring below its maximum is an issue against what
  it found rather than a section 14 derogation: this organization aligns
  by adopting the practice, and a derogation would make the outside
  opinion answerable to the thing it measures. What that gives up is the
  case where the check is wrong about this organization, which then
  costs an issue closed on the measurement.
- **Nothing fuzzes a parser of untrusted serialized data** (issue #342).
  `fuzz` follows a tree that parses whatever a stranger sends, which
  reaches `btclib`, `btclib-secp256k1` and `btclib-node` and not
  `bitcoin-core-rpc`, whose peer is an instance its own operator runs. A
  crash it finds is an issue against the parser and never a suppression.
- **A sentinel's calendar row arrives with the workflow** (issues #339
  and #342): `tests/grid_test.py` fails a row nothing in the
  organization schedules, and that direction of the test is the only
  thing anywhere catching a row for a workflow nobody wrote, so spending
  it on a rollout leaves it catching nothing.
- **Section 14 no longer leaves these to the repository** (issues #327,
  #339 and #342): *which optional workflows exist* now reads past those
  section 10 keys on a property of the tree.

### Section 10 says what the calendar's hour is chosen on

- **The calendar gave a workflow an hour and never said on what.** The
  hour is chosen against this organization's own load and not GitHub's:
  what GitHub documents about the delay and the drop it puts at the
  start of an hour, and the remedy it names is a minute, which the
  repository already holds — so an hour picked to miss a published peak
  is picked against nothing. What an hour decides is what the run
  competes with here, a row starting its workflow in every tree that has
  it and each matrix running whole, so the rows sit before the working
  day, where the concurrency ceiling is not owed to a review.
- **The hour is UTC and the band grows downward, so `03` is the next one
  the grid takes**, and the sentinels this section names without a row
  have an hour to arrive in. A `cron:` here names no `timezone:`, and a
  fixed UTC hour falls later in the morning here for as long as the
  clocks are forward, so the late end of the band is what reaches the
  working day first. What that declines is `06`.

### Section 11 makes the ack of record a review

- **The ack of record was posted as a comment, which the forge does not
  record** (issue #340), so a rule this file states was visible in no
  artifact and an outside reader was left concluding nothing here is
  reviewed. It is now a review — `APPROVE` carrying the `ACK <sha>`
  body, `REQUEST_CHANGES` carrying the other. GitHub's refusal of a
  self-approval explains why an *author's* verdict is a comment and had
  been doing duty for why the workflow's was.
- **The rejected alternative is a second human approving every pull
  request** (issue #340), and what this gives up is that a model's
  judgement now sits where a branch rule reads. It is chosen because
  nothing lands while nobody is available.
- **It lands before the ruleset bypass goes** (issue #340), that being
  where the failure mode is found while a missing approval still costs
  nothing.
- **`REVIEWING.md` said a forge approval is not an ack** (issue #340,
  and btclib-org/.github#353 for the copies), giving as the reason a
  refusal that reaches only the author's own. Its shared half now says
  the ack of record is an approving review and points at section 11 for
  whose; `tests/verbatim_test.py`'s `EXPECTED_DRIFT` carries the path
  and the issue until the seven other trees take it.

### `REVIEWING.md` says which artifact carries the verdict

- **The section opened by putting the verdict in a summary comment**
  (closes #361), and the sentence reconciling that with the ack of
  record being a review arrived later in the same section, reading as an
  aside. *The verdict* now names the artifact where it first describes a
  summary: a review that decides whether the pull request lands posts
  that summary to the forge as a review, and every other summary is a
  comment.
- **`APPROVE` and `REQUEST_CHANGES` appeared nowhere in the file**
  (closes #361), so the form section 11 requires of the ack of record
  was missing from the document a reviewer writes a verdict against.
  Each is now paired with the line it carries, and section 11 stays the
  place that says whose verdict is the ack of record and why the forge
  has to hold a review of it rather than a comment.
- **The copies are already recorded as drifted** (issue #353):
  `tests/verbatim_test.py`'s `EXPECTED_DRIFT` names `REVIEWING.md`, so
  this widens the drift that entry excuses instead of owing a second
  one.

### Section 12 states the public-surface check

- **Nothing detected a break in a published package's public surface**
  (issue #326). Section 7's census asserts that `__all__` is declared
  and that what it names exists, never that a release kept what the last
  one gave, and `RELEASE_NOTES.md` is written by hand. `griffe check`
  now runs in the release path, comparing the tag being cut against the
  one before it, and what it reports is either an entry or a reason for
  not being one.
- **The release path and not the merge gate** (issue #326): before 1.0 a
  package breaks its surface deliberately, so a gate reporting every
  break has nothing to say about which are allowed and every run ends in
  a human deciding. It becomes a gate the day a deprecation policy
  supplies the missing half, and the invocation is written to take a
  second reference pair rather than be replaced by one.

### `tests/__init__.py`'s `BACKLOG` row for issue #313 is gone

- **The row excusing `test_the_package_directory_sits_under_src` for
  `btclib` and `bitcoin-core-rpc` outlived both trees' moves** (closes
  #313): `bitcoin-core-rpc` moved its package under `src/`, the last
  tree in the organization that had not, so every cell the row named
  now passes without the strict xfail, and the row is deleted rather
  than narrowed.

### Section 2 states where the package directory sits

- **The package directory sat at the repository root, and no file in
  the organization said why, or said `src/` instead** — issue #313.
  Section 2 now says the package directory sits under `src/`: a package
  at the root is on `sys.path` whenever anything runs from there, so an
  import can resolve to the checkout instead of to the installed
  distribution, which is what section 7's convention tests exist to
  tell apart. The root layout costs one directory less and puts the
  package where a reader of the listing meets it first; that is what
  the rule gives up.
- **Section 3's build-backend bullet says what the rule costs each
  backend** — issue #313: under `uv_build` it is the default, so
  `[tool.uv.build-backend] module-root` overriding it to the root
  disappears rather than changes value; hatchling needs no key at all,
  `src/<name>/__init__.py` already being its own second file-selection
  heuristic.
- **`tests/surface_test.py`'s `package()` located a hatchling package
  only at the repository root, the one layout the rule now leaves
  behind** — issue #313. It now finds one under `src/` too, and a new
  test, `test_the_package_directory_sits_under_src`, fails a tree that
  installs a package outside it, carried as a `BACKLOG` row keyed on
  this issue until each moves.
- **`tests/__init__.py`'s `BACKLOG` row for the package-directory move
  narrows to `btclib` and `bitcoin-core-rpc`** (issue #313):
  `btclib-secp256k1` and `btclib-node` now sit their package under
  `src/`, so their cells in `test_the_package_directory_sits_under_src`
  pass without the strict xfail; `btclib` and `bitcoin-core-rpc` still
  owe the tree the move.

### Section 1 names the uv floor's owners, section 15 its ceiling

- **`[tool.uv] required-version` said the floor was "low enough for
  Dependabot's own bundled uv," with no command beside it and no statement
  of which trees owe it** — issue #312. Section 1 now names the trees that
  owe a floor — every one `uv.lock`'s row binds, tiers 1 and 2 — and says
  the floor sits at the ceiling rather than below it, since the ceiling
  only rises and the failure guarded against is an *older* uv rewriting
  the lock.
- **Section 15 gained the command that measures the ceiling** — issue
  #312: the uv Dependabot's own bundled updater ships, read off
  `dependabot-core`'s `uv/Dockerfile`, beside the loop that reads each
  tree's own declared floor against it.
- **This repository's own `pyproject.toml` gained `required-version =
  ">=0.12.1"`, the ceiling measured today** — issue #312. It held a
  `[tool.uv]` table and commits a `uv.lock`, with no floor declared.
- **`tests/pyproject_test.py`'s check only refused a floor above the
  ceiling, leaving a tree that named none exempt by silence** — issue
  #312. It now fails a tree that commits a `uv.lock` and names no floor at
  all; `bbt` and `btclib-node` are the two, carried as a `BACKLOG` row
  under this issue until both land.
- **Issue #312's `BACKLOG` row narrows to `btclib-node`** — `bbt`'s own
  `required-version` is no longer above what `dependabot-core`'s
  `uv/Dockerfile` bundles, so its cell in
  `test_the_uv_floor_is_not_above_what_dependabot_bundles` passes under
  the strict xfail. The issue stays open: `btclib-node` still owes the
  tree a floor.

### Every fixable hook now fixes, and `CHANGELOG.md`'s derogation is gone

- **A check-only hook reports a defect a machine could have repaired
  instead, and section 4 now states the rule that keeps that from
  happening again: every hook with a fix mode runs with it turned on.**
  `markdownlint-cli2` gains `--fix` and `codespell` gains
  `--write-changes`; `typos` already fixes in place through its own
  upstream default, which `.pre-commit-config.yaml` now says so that an
  `args:` added later for another reason cannot silently turn it off.
  `yamllint` is noted where it is configured as having no fix mode to
  turn on.
- **With `markdownlint-cli2` fixing in place, `CHANGELOG.md`'s directive
  disabling MD022 and MD032 no longer has anything to absorb: a rebase
  that drops the blank line between two joined sections is repaired on
  the next hook run instead of failing a gate with nothing to fix it**
  — issue #190. The two-comment directive at the head of the file is
  gone, the two rules apply to this file again, and section 9 states the
  mechanism the directive used to work around instead of the derogation
  that stood in for it.

### `CHANGELOG.md`'s derogation directive names its condition alone

- **The directive carried two issue pointers — `#33` as the condition
  that gates the removal, and a second naming "the record" — but only
  the condition decides anything** — issue #190. Section 9's *One fact
  in one place* refuses a restated fact as much as an invented one. The
  directive now names `btclib-org/.github#33` alone. The derogation
  itself is unchanged: the two rules stay off for `CHANGELOG.md` until
  that issue's queue is empty.

### Section 7 gains a socket-free bullet, section 15 a vendored-pins audit

- **Section 7's *Convention tests* catalogue named every kind but the one
  two repositories' own docstrings already claim: that a suite reaches
  no socket** — issue #80. The catalogue now carries **the suite opens
  no socket**, so a repository whose transport argument is missing at a
  call site has a stated convention to write a test against, instead of
  a docstring nothing checks.
- **Section 15 had no command reading section 7's vendored-data pins**
  — issue #80. It gains the loop that reads each repository's
  `tests/_data/README.md` or `tests/README.md` against its
  `vendored-vectors.yml`, so a tree pinning an upstream commit with
  nothing rechecking it monthly is a line in the audit rather than a
  reading nobody runs.

### Section 11 names the two closing-keyword forms and their hazard

- **Section 11 said neither form of a closing keyword works across
  repositories; the qualified `owner/repo#N` form does** — issue #304.
  Measured on `btclib-org/btclib-secp256k1#366`'s squash commit,
  `592f1bc`: its message named `btclib-org/.github#81` after a keyword,
  and the issue closed on that merge. That qualified form is also this
  organization's own citation style for another tracker's issue, so the
  sentence disclaiming a keyword is the sentence most likely to carry
  one, as at #81 and #291 — the section now says to name such an issue
  with no keyword verb beside it, negated or not. The manual-link
  paragraph is corrected too: `btclib-org/bitcoin-core-rpc#178` did not
  close `btclib-org/btclib#1160` on merge, that issue having already
  been closed by hand, deliberately, to defuse a race between three
  pull requests carrying the same undisclosed link.

### `btclib-secp256k1`'s two backlog rows for issue #79 are gone

- **`btclib-secp256k1` declares `__all__` in every published module, so
  the two `BACKLOG` rows holding `surface_test.py`'s pair for that tree
  turned red** — issue #79. A row is an `xfail(strict=True)` against a
  tree cloned at its default-branch tip, so it fails the moment the tree
  it names starts passing, which is what it is for. Issue #79 stays open
  for the rest of its record: what section 7's escape clause says, and
  the two trees it has not verified.

### `REPOSITORY.md` points at the release fact instead of restating it

- **`REPOSITORY.md` restated that nothing here is released, once in the
  `tag-integrity` reasoning and once in *What is not configured, and
  why*, instead of pointing at `CONTRIBUTING.md`'s *A version, and no
  release*** — issue #291. Both spots now carry the pointer, in the
  shape `bbt`'s `REPOSITORY.md` already uses.

### `package()` refuses a dotted `module-name` instead of joining it literally

- **`package()` did `Path(root) / name` on a dotted `module-name`, giving
  `src/foo.bar` where `uv_build` builds `src/foo/bar`** — issue #268.
  `uv_build` reads a dot in that key as its other namespace-package
  shape, a module sharing a namespace with a module another distribution
  installs beside it; `package()` now raises `LookupError` naming the
  repository and the key instead of resolving either path. Section 2's
  *the package directory is singular by the rule and not by omission*
  now states this shape too, for the same reason as the sibling list
  shape #264 corrected: a tree here carries its own package, not a leaf
  of a namespace shared with another distribution.

### `CLAUDE.md`'s worktree recipe is `wt-<tracker>-<issue>-<repo>-<role>`

- **The recipe named the worktree after the issue alone, `wt<issue>`, in
  every repository of the organization** — issue #292. A worktree's
  administrative directory lives in the `.git` of the repository
  `git worktree add` was run from, one per repository, so two
  repositories cannot collide there; what the recipe left uncovered was
  a same-repository collision, between two worktrees of different work
  sharing a generic basename, and a *path* collision across
  repositories, since the workers of one session share one scratchpad
  directory and a session carrying one issue into several repositories
  computed the same target path for each. The recipe now names the
  worktree `wt-<tracker>-<issue>-<repo>-<role>`, most general part
  first: `tracker` because an issue number is unique only within one
  tracker, `issue` against the same-repository collision, `repo` against
  the cross-repository path collision, and `role` against a coder and
  its reviewer holding a worktree at once.

### Section 14 says why `claude-review.yml` has no verbatim bullet

- **Section 11 says `claude-review.yml` is in every repository and section 15
  checks only that it exists; section 14 — *Copied verbatim, and decided per
  repository* — carried no entry for the file, unlike `CONTRIBUTING.md` and
  `REVIEWING.md`** — issue #267. Section 14 now says why one is absent:
  `tests/verbatim_test.py`'s comparison needs a copy in this repository the
  others were made from, and this repository's own copy is the workflow's
  origin rather than a receiver of it, so there is none. Whether the
  receiving copies must otherwise agree is left open, for issue #35's
  reusable-workflow consolidation to possibly settle by removing the copies
  rather than by comparing them.

### `tests/pyproject_test.py` gains a check for section 1's uv floor

- **`[tool.uv] required-version` names the oldest uv that may read the
  lock, and a floor above the version `dependabot-core`'s updater
  bundles stops that tree's uv-driven Dependabot updates with no error
  anywhere** — issue #27. `tests/pyproject_test.py` now reads
  `dependabot-core`'s `uv/Dockerfile` through `gh api` and skips, rather
  than failing, where the file cannot be read or is read with no
  `astral-sh/uv:` pin in it.

### The naming bullet states the identifier's grammar and the wheel's escape

- **The naming bullet said an import package takes underscores instead
  of the hyphen, without saying the two rules carry different weight**
  — issue #294. The language's own grammar excludes the hyphen from an
  identifier outright — `name_start` and `name_continue` admit letters,
  digits and `_`, never `-` — where PEP 8's *Package and Module Names*
  only discourages the underscore, as a matter of style, and the bullet
  now states that asymmetry.
- **The naming bullet said nothing about what a distribution name
  becomes in the built artifact** — the same issue. PEP 427's escaping
  rule normalizes any run of `-`, `_` and `.` in a distribution name to
  `_` for the wheel filename and the `.dist-info` directory, so
  `bitcoin-core-rpc` and `bitcoin_core_rpc` already name the same
  wheel; the `#277` paragraph tracking `btclib-secp256k1`'s pending
  rename now points at that rule instead of restating it.

### Section 3 answers `[project].name`'s spelling, both directions

- **Section 3 stated the repository-naming rule but not which spelling
  `name` itself takes** — issue #277. It now states the canonical
  hyphen, `btclib-secp256k1` recorded as the exception until its own
  pull request corrects it — a `BACKLOG` row in `tests/__init__.py`
  excusing it from the new `tests/pyproject_test.py` test that checks
  it.
- **The naming bullet's subject is a distribution, and two trees
  declare `[project].name` while building none** — issue #286. The
  bullet now says so explicitly: `bbt` and `.github` are outside it,
  `.github` unable to take the repository-naming half in any case
  since PEP 503 normalizes `.github` to `-github`, not a distribution
  name.

### `CONTRIBUTING.md` gains this tree's own *A version, and no release*

- **The three other tier-2 repositories keep the fact that nothing is
  released under a `### A version, and no release` heading in
  `CONTRIBUTING.md`'s last section, and this one stated it twice
  instead, in `README.md`'s *What this repository is* and in
  `CLAUDE.md`'s *Architecture*** — issue #276. `CONTRIBUTING.md`'s last
  section now carries the heading, `README.md` points to it in place of
  restating the fact, and `CLAUDE.md` drops its copy.

### Two of section 3's rules get commands that re-derive them

- **`pyproject_test.py` asked only that `license-files` was declared,
  not what it named** — issue #200. Section 3 already states the key
  names `LICENSE` and `AUTHORS.md` and nothing else; the test now
  asserts those two names.
- **Section 3's repository-naming rule had no command in `tests/` that
  re-derived it** — issue #278. A new test compares the distribution's
  `name`, normalized per PEP 503, against the repository.

### `alignment.yml` triggers on the verbatim files, not the list of them

- **`alignment.yml`'s `pull_request` trigger admitted `README.md`, which
  is where section 14's verbatim list lives, but not the files that list
  names** — issue #279. A pull request editing one of them —
  `CONTRIBUTING.md` or `REVIEWING.md`'s shared half, most often — got no
  run of `tests/verbatim_test.py` until the Thursday cron. The `paths:`
  block now names them explicitly, and a new test,
  `test_alignment_triggers_on_every_verbatim_file`, reads the workflow
  and section 14 together and fails where the two disagree, so a path
  added to or dropped from the list is a failure here rather than a
  second copy nobody keeps in step.

### The landing-subject fact is conditional, and CONTRIBUTING.md points at it

- **The landing-subject fact was stated unconditionally, in section 11
  and in `REPOSITORY.md`** — issue #273. *Merge method* already states
  which of the pull request's title and the branch's own commit subject
  lands; *What a pull request says it is* now points at that rule
  instead of asserting the title unconditionally, so the parentheses
  belong on whichever one lands, not only on the title.
  `REPOSITORY.md`'s own sentence now points at *Merge method* too,
  instead of restating its two cases.
- **CONTRIBUTING.md's commit-message paragraph restated the merge
  method three lines under its own explanation of why it does not
  restate section 9** — issue #274. It now links section 11 instead,
  matching the shape *Landing it* already uses for the same fact. The
  edit falls inside the shared half `EXPECTED_DRIFT` in
  `tests/verbatim_test.py` already holds against issue #281, so nothing
  here changes that entry.

### `CLAUDE.md` gains what a session here kept rediscovering

- **`CLAUDE.md` sends a shared-file drift to `EXPECTED_DRIFT`, not `BACKLOG`**
  — `tests/verbatim_test.py` holds the first and excuses one path;
  `tests/__init__.py` holds the second and excuses a whole test.
- **`CLAUDE.md` sends a "every tier-2 repository" claim to be checked against
  this tree too** — issue #276 is open on what it finds here, in
  `CONTRIBUTING.md`'s own `### A version, and no release` section.
- **`CLAUDE.md` records that cloning `tests/conftest.py`'s `trees` fixture by
  `--reference` against the local checkouts was measured and declined** —
  issue #272.

### Two more sections point instead of restating

- **Section 11's merge-method fact has one site** — issue #252.
  *Branch protection and rulesets* keeps squash as `main-self-merge`'s
  own rule, a settings enumeration and not itself in question; *What a
  pull request says it is* restated the fact to reach
  `squash_merge_commit_title`'s consequence, and now points at *Merge
  method* instead.
- **Section 4 points at section 7 for the test-file spelling instead of
  naming it again** — issue #131. The *Python shape* bullet named
  `*_test.py` beside `name-tests-test` at its default; *Layout and
  naming* is where the spelling and the reason for choosing it live, so
  the bullet points there instead. Section 7's *Convention tests*
  paragraph and *Layout and naming* bullet agree with each other, so
  this is the rule's only remaining second site.

### Section 2 drops a dead quote, and section 3 gains a naming rule

- **Section 2 points to `bbt`'s, `btclib-node`'s and
  `btclib-benchmarks`'s own `CONTRIBUTING.md` instead of quoting
  `RELEASING.md`** — issue #159. `btclib-node` and `bbt` no longer
  carry that file, so the paragraph quoted its opening line from a
  page that answers 404; it now names the section each of the three
  keeps the same sentence in. `.github`'s own `CONTRIBUTING.md` has no
  such section, tracked as issue #276.
- **Section 3 states that a repository is named after the distribution
  it publishes, hyphenated, never after the import package** — issue
  #30. The rule was nowhere in the standard.
- **`profile/README.md` links to `btclib-node` under its current
  name** — issue #30. The organization's front page spelled both the
  link text and the URL after the import package, `btclib_node`.

### The calendar gains a row for `btclib-node`'s DNS-seed sentinel

- **`bootstrap-dns` takes Thursday, 05** — issue #201. It is the only
  workflow shape section 10's tables had no row for: a sentinel unique
  to `btclib-node`, resolving each chain's bootstrap DNS seeds against
  the live network, the same slot `py-arm-authority` already holds as a
  row one repository alone answers to. Thursday's `05` was the grid's
  only open cell, `alignment` alone occupying that day, at `04`.
- **`tests/grid_test.py::test_every_row_of_the_calendar_names_something_that_exists`
  fails until `btclib-node` schedules it.** The row and the cron are two
  repositories' changes, and `btclib-node`'s own `bootstrap-dns.yml`
  already runs on `workflow_dispatch` alone, waiting on this row before
  it adds a `schedule:`. The test takes the session fixtures rather than
  a `repository` one, so the backlog's per-repository `xfail` cannot
  excuse it; the row is a real, temporary gap the audit is right to
  report, and `alignment.yml` says of itself why that is a backlog
  entry and not a block.

### Section 3 names the free-threaded classifier and scopes the build fallback

- **The classifiers bullet says what a `3.14t` matrix row is declared
  as** — issue #244. The organization already runs that row in its
  platform sweeps and the bullet named no classifier for it; a `t`
  suffix asks for the same version built without the GIL rather than a
  version of its own, unlike a `pypy` prefix's own implementation, so it
  names the same `X.Y` classifier and not PyPI's `Free Threading`
  maturity classifiers, which a sweep passing is not evidence for.
- **The `uv build` fallback the bullet cites is scoped to the shape it
  relies on** — issue #258. The bullet stated unconditionally what
  section 12 now states by direction: a ceiling below the running uv
  warns and builds with the bundled backend, where a floor above it
  fails outright. Asking for an older backend than the one running is
  always the first shape, so the bullet now says that rather than
  restating both.

### `package()` and the two `py.typed` bullets say what they can reach

- **`package()` refuses a `module-name` list instead of raising
  `TypeError`** — issue #264. `uv_build` allows that key to be a list,
  for a namespace package naming more than one module, and the helper
  joined a `Path` to it; it now raises `LookupError` naming the
  repository and the key. Section 2 now states the package directory is
  singular by the rule rather than by omission, that shape being one
  this file does not allow.
- **Section 2's `py.typed` bullet and section 3's `classifiers` bullet
  say the suite reads a tracked marker, not an installed one** — issue
  #266. `surface_test.py` and `classifiers_test.py` both ask
  `git ls-files`, holding no checkout of the audited trees to build an
  archive from. Measured by building a tree with the marker excluded
  once from the wheel and once from the sdist: `check-sdist` drives no
  wheel at all and passed the sdist that still carried the marker while
  the wheel built beside it did not, so a wheel dropping the marker is
  `check-wheel-contents`'s catch and not this suite's, for a tree that
  publishes; a tree short of tier 1 has no gate over either archive.

### The row for `btclib-node`'s `name-tests-test` argument goes

- **`btclib-node` runs the hook at its default, so its row is deleted**
  — issue #131. `btclib-org/btclib-node@640af71` renamed that tree's
  test modules to `*_test.py` and dropped the argument selecting the
  other pattern, so `test_name_tests_test_runs_at_its_default` asks it
  and is answered. The issue stays open: what it asks for is sections 4
  and 7 saying one thing about test-file naming, which no tree's rename
  settles, and its other row —
  `test_every_test_file_is_named_so_pytest_collects_it` — still records
  a real gap there.

### `btclib-node` closed two filed gaps, so both records go

- **`EXPECTED_DRIFT` no longer names `.gitattributes`** — issue #192.
  The last of the eight trees now carries the standard's comment, so the
  table described copies that agree. The table itself stays. An entry
  there excuses one path and leaves every other verbatim file compared,
  where a backlog row would excuse the whole comparison — which is why a
  drift filed later gets an entry here and not a row there.
- **The backlog row for `btclib_node`'s missing `py.typed` is deleted**
  — issue #239. That package now ships the marker and declares
  `__all__`, so the test asks it and is answered.

### `tests/` and `docs/source/` follow the package, and its locator too

- **Section 2's `tests/` and `docs/source/` bullets are asked of a tree
  that installs an importable package, rather than of a tier** — issue
  #240. Both name a package as their subject already, `tests/` mirroring
  it and `docs/source/` documenting what it ships, so a tree installing
  none owes neither, the same reading issue #193 gave the package
  directory. `.github`'s own `tests/` stays: it is over the organization
  rather than over a package this repository does not hold, which a tier
  being a floor and not a ceiling already allows.
- **`tests/surface_test.py`'s `package()` reads a tree's declared layout
  instead of inferring one from where an `__init__.py` sits** — issue
  #246. `src/` is `uv_build`'s own default and section 2 states no
  layout, so a tree building under that default resolved to no package
  and the assertion skipped silently. The function now reads
  `module-root` and `module-name` off `[tool.uv.build-backend]` for a
  `uv_build` project, and keeps the old root-level scan for a backend
  that defaults there instead, `btclib-secp256k1`'s hatchling among them.
  Verified against both layouts built as fixtures, and against every
  repository's real tree, resolving the same directories and outcomes as
  before the change.

### Section 12's two `build` bullets say what each path actually reads

- **The `pyroma` bullet stops claiming `build` checks `requires` on the
  non-isolated path** — issue #251. `build.util.project_wheel_metadata`
  has no `check_dependencies` call on that branch; the bullet now says
  what decides pyroma's own fallback, which is whether the backend's
  PEP 517 hook raises, not whether the environment satisfies the list.
- **The `check-sdist` bullet's `uv build` warning is scoped to one
  shape of `requires`** — issue #242. A ceiling below the running uv
  warns and builds with the bundled backend anyway; a floor above it
  fails instead, `uv` unable to import a `uv_build` meeting that floor.

### Two records are corrected to name what is still true

- **The derogation's record is now the issue that outlives it** — issue
  #190. #138 asked section 9 to state `merge=union`'s mechanical price
  and closed against the prose that answered it, but the derogation it
  also carried stays live until #33's queue empties, so the head of this
  file was pointing at something closed. #190 is the issue that found
  that, and it closes when the directive goes.
- **`CLAUDE.md`'s primary-checkout paragraph names the read that
  cannot go stale** — issue #248. `git fetch` moves
  `refs/remotes/origin/main` and leaves the work tree where it was, so
  the paragraph told a session enough to read the checkout but not
  enough to read it current. It now says the checkout is a local
  reference kept on `main`, names `git show origin/main:<path>` as the
  read a stale checkout cannot affect, and gives the fast-forward that
  brings the checkout forward without working in it.

### The `Typing :: Typed` pairing with `py.typed` is stated both ways

- **Section 3's `classifiers` bullet states the pairing in both
  directions** — issue #256. It refused the classifier on a tree with
  no marker and said nothing about a tree with the marker and no
  classifier; the marker is PEP 561's promise to a downstream consumer
  that the installed package carries types, and the classifier is that
  same promise on the index page, so the bullet now gives the reason
  the pairing holds bidirectionally.
- **`classifiers_test.py` refuses either half without the other** — the
  same issue. `test_the_typing_classifier_and_the_marker_agree` reuses
  `surface_test.py`'s `package` to skip a tree that installs no
  importable package, and asks the rest against `py.typed` and the
  classifier together.

### `bbt` selects `W`, so the row for it goes

- **The backlog row for `bbt`'s unselected `W` is deleted** — issue
  #176. That tree sets `max-doc-length = 80` and now selects the family
  the key configures, so `test_w_is_selected_with_max_doc_length_at_80`
  asks it and is answered. The row was a strict expected failure, so it
  had to go in the same round the tree changed: an expected failure that
  passes is a red suite, which is what makes the row a record of a gap
  rather than a way of ignoring one.

### Section 11 points instead of restating, at two more sites

- **The port subsection points at section 15 for `--silent`** — issue
  #236. The paragraph gave the same three claims section 15's publishing
  sweep already gives; the subsection is about what a port must adapt,
  and this mechanism is not one of those two things, so it points
  instead, as the other `--silent` sites already do.
- **The two-secret-stores rule is *Dependabot and pre-commit.ci*'s** —
  issue #241. *The workflow, and what a port of it has to adapt* stated
  the same mechanism for the `claude-review.yml` token: that a
  Dependabot-initiated run reads the Dependabot secret store rather than
  the Actions one. It keeps the token's own consequence — a red review
  on every Dependabot pull request while the second store is missing —
  and points at the subsection below for the mechanism.

### The package directory follows the package, and section 16 asks section 7

- **Section 2 asks the package directory of a tree that installs an
  importable package** — issue #193. The bullet was tiers 1 and 2's,
  where a Python project that publishes nothing may install nothing:
  `package = false`, or a build backend given no module to build. Where
  there is no package the bullet has no subject, a floor being over the
  rules whose subject a tree holds.
- **`tests/surface_test.py` asks that bullet of every tree that has a
  package** — `py.typed` in the directory and `__all__` in its
  `__init__.py`, skipped where a tree installs none and carrying no tier
  marker, that being the answer above. The directory is found by the
  `__init__.py` at the root of the tree: found by `py.typed` it would
  report a tree missing that file as an error rather than as the
  finding. `btclib-secp256k1` and `btclib-node` are backlog rows against
  issues #79 and #239.
- **Section 16's migration step points at section 7 for which convention
  tests are owed** — issue #215. It gave the criterion as one test per
  convention the prose states, which is section 7's clause without the
  condition that clause carries, and a migrating tree publishing an
  importable package owes the public-surface test whether its prose
  states the convention or not. The new-repository checklist above it
  leaves the criterion to section 7.

### The `allowed_bots` comment cites a section a port's README has

- **The citation names the standard it means** — issue #184. It ended on
  `README.md`'s section 11, and the `README.md` beside a copy of this
  workflow is that repository's own, with no section 11 in it; section 11
  of the btclib-org repository standard is the same pointer with the
  repository named, and `CONTRIBUTING.md` carries the link to it in every
  tree. The clause excusing the input as deciding nothing in this
  repository goes with it: `.github/dependabot.yml` is in the tree, and
  the runs it opens are what the input admits.

### Section 11 says what `enforce_admins: false` clears

- **The setting clears the required checks and not the review rule
  alone** — issue #185. `strict` is among them, so being up to date with
  `main` is a rebase somebody runs before landing rather than a rule the
  forge holds, and a branch merged behind `main` lands a tree nothing has
  run. `REPOSITORY.md` says that of the `strict` in the protection body
  it records, and points at the section for the rest; the exemption it
  stated a second time under the rulesets points at the same place.

### `REPOSITORY.md` says what Dependabot proposes here

- **The Dependabot paragraph describes the file this tree holds** —
  issue #211. It recorded an absence, and the reasoning under it went
  with it: that the actions these workflows pin, and `uv.lock`, had
  nothing proposing their next revision. `.github/dependabot.yml`
  declares `github-actions` and `uv`, the second because the tree holds
  the lock file section 11 makes that ecosystem conditional on.

### The sdist bullet says what the rule is, not what it was

- **The `check-sdist` bullet states its rule rather than its history** —
  issue #219. It gave the condition the rule once carried and the tool
  that carried it, which section 9's *No history in the prose* leaves to
  this file. The rejected alternative stays, in the form section 9 asks a
  negative result to take: a check conditional on the inclusion being an
  include list is refused because neither direction's failure is loud,
  which the sentences above it establish.

### The interpreter window is compared from here for a tree with no module

- **Section 15 says why `interpreters_test.py` is a library's** — issue
  #206. Section 3 states that a library carries the convention as that
  module and gives no reason for the qualification, so the answer to
  whether an application owes one was written nowhere. A library's
  classifiers are what an index shows whoever is choosing the package,
  where an application's declarations are read by whoever opens the
  repository, and the ends of its window are compared from here instead.
  The other answer weighed is beside it: dropping the classifiers a tree
  publishing nothing shows to no index costs the comparison itself, the
  floor and the matrix being declared either way.
- **The floor is the lowest classifier, asked of every tree that
  declares both.** The two are ends of one window written twice in one
  file, and a tree holding no module of its own compares them nowhere.
  What stays a reading is the classifiers against the interpreters a
  workflow runs: a job naming one outside the window is correct where
  the reason is beside it.
- **A classifier set is a set.** The window each library declares is
  compared sorted, so the same versions written in another order are one
  window rather than two.
- **`.python-version` answers with a version.** A `t` suffix asks for
  that version built without the GIL, which is the version a classifier
  names, so the pin is read without it — and section 15 says the same of
  the column its command prints, where it had said the opposite.

### The blank lines the union driver ate are back

- **`CHANGELOG.md` would pass MD022 and MD032 with the directive at its
  head taken out** — issue #214. Two branches each adding a `###`
  section under `## Unreleased` merge into a heading with no blank line
  above it, and the two rules being off is why the gate reports none of
  them; every heading that lost one has it back. The directive itself
  stays, its removal being issue #190's.

### The two `D` exemptions are a default a tree may decline

- **Section 5 says what declining one means** — issue #208. The bullet
  named `__init__` and the magic methods as exemptions and left open
  whether a tree taking neither is drift. Measured with the pinned ruff:
  `convention = "pep257"` leaves `undocumented-public-init` and
  `undocumented-magic-method` enabled, so the `ignore` entry is the whole
  of each, and a tree without it is asked for the docstring at every such
  site — answering with one, or with a `# noqa` that `RUF100` retires the
  moment the docstring arrives. Both entries are the default and
  declining one is not drift. Requiring them of every tree is the
  rejected alternative: it asks a tree to drop a gate it passes.

### Section 15 stops counting its readings, and section 16 names the switches

- **Section 15 says once what the suite never asks** — issue #203. The
  intro named the readings and counted them, the `tests/README.md`
  paragraph called itself the only one a command cannot compute, and the
  workflow-comments subsection called itself the one audit that is a
  reading. The intro keeps the members and drops the number, and the
  other places say what they are rather than how many there are.
- **The new-repository checklist names every GitHub setting it owes** —
  issue #204. Section 16's first checklist is *How to use this file*'s
  same list without the reasoning, so it carries what section 11 asks —
  secret scanning, its push protection and Dependabot security updates —
  and what section 2 asks of every tier, private vulnerability
  reporting. `tests/security_test.py` asks that setting of every
  repository, so a list omitting it builds a tree the suite fails.
- **The normalizing checklist gains that setting too**, beside the
  scanning switches: a tree brought up to the standard owes it as much
  as a new one.

### Section 15 gives the reason for `--silent` once

- **The `claude-review.yml` sweep points at that reason rather than
  telling the story of a run** — issue #205. It carried an anecdote, a
  count of the repositories the check had missed and a past tense, where
  the publishing sweep two blocks above says in the present what
  `--silent` buys and what `--jq .name` would put on stdout instead. The
  pointer is what stays.

### Section 11's `--silent` paragraph ends at the reason

- **The account of one run goes from it** — issue #232. The paragraph
  gives the mechanism in the present tense — `--silent` sends a 404 to
  stderr, where `--jq .name` puts its body on stdout, a JSON document in
  a column of filenames — and then told what that had cost once. The
  harm is in the clause before it, so the sentence ends there.

### Section 2 says where it states a rule, and its ceiling is asked

- **The root-files table's opening sends a reader to where each reason
  is** — issue #209. It sent them under the table for every row that is
  not every tier's, and only `SECURITY.md`'s reason is there: the
  release documents' is the paragraph above that keeps them out of a
  tier-2 tree, and the two Python files' is the measurement the section
  opens with, whose consequence the sentence now states — a tree with no
  `pyproject.toml` is no Python project and has nothing to lock.
- **`root_files_test.py` reads that paragraph's rule and asks it of a
  tier-2 tree** — issue #218. The table's column says which tiers *owe*
  a row and a tier is a floor, so no cell of it forbids a file:
  `portanode` carries both release documents at tier 3 and contradicts
  neither statement. The rule is read out of the section by the phrase
  that opens it and the bold that closes it, in its own paragraph, and a
  sentence this cannot read is an error rather than a run that asks
  nothing.
- **The two statements are asked of each other.** What the sentence
  keeps out of a tier-2 repository is what the table gives to tier 1
  alone, so a row moved down is reported as the standard contradicting
  itself rather than as every tier-2 tree failing at once.
- **The module says which of its rows are asked for presence twice**,
  `verbatim_test.py` asking the same of the rows section 14 owes of
  every repository.

### The root-files table says what a README is at every tier it binds

- **Section 2's `README.md` row describes the file rather than a
  package** — issue #179. The row gave it as the package's long
  description and the site homepage, and it binds tier 3, which is
  measured by the absence of a `pyproject.toml`; a repository that holds
  no `docs/source` has no site for it to be the homepage of either. What
  an index renders is stated where that tier is argued, in the
  support-line paragraph under the same table.

### Section 16's checklists write the editor and agent configuration

- **`.vscode/` and `.claude/` are on both lists** — issue #174. Section
  2 tracks them, section 13 records that a wrong
  `mypy-type-checker.importStrategy` is silent both ways, and section 14
  owes `.claude/commands/review.md` wherever `REVIEWING.md` is; neither
  checklist named any of them, so a repository worked end to end from
  section 16 finished without them. The settings file follows the step
  that chooses the mypy hook, whose branch its value reads, and the
  review command lands with `REVIEWING.md`. *How to use this file* is
  what makes the omission a gap rather than a saving: the first
  checklist is the sections' own list without the reasoning.

### Section 7's escape clause is stated once and pointed at twice

- **Section 14's *Decided per repository* entry points rather than
  restates** — issue #194. It gave the criterion — the convention tests
  follow the conventions that project's prose states — which is section
  7's clause without the condition that clause now carries, in the place
  a reader goes to find out what is per-repository. The entry names
  section 7's terms instead.
- **Section 15's reading of `tests/README.md` asks section 7 which
  bullets are owed.** The instruction made a finding out of a bullet the
  repository's prose states and the declaration does not claim, which no
  longer reaches a tier-1 tree that neither states the public surface nor
  claims it — btclib-org/bitcoin-core-rpc#235 is that tree. Owed and not
  claimed is the finding, and what is owed is section 7's to say.
- **Section 7 no longer glosses its own clause four lines below it.**
  The paraphrase carried the same gap; the sentence names the clause and
  says where it reaches.

### PEP 639's two keys are read, in every tree that builds an archive

- **`pyproject_test.py` asks section 3 for the licence expression and
  for `license-files`** — issue #173. `license` has to be the SPDX
  string: the deprecated table is what PEP 639 replaced, and it is also
  what passes `classifiers_test.py`, whose refusal of a `License ::`
  classifier beside the expression reads that same key and so asks
  nothing of a tree declaring no string. `license-files` has to be
  declared, and what it may name is section 3's own question — issue
  #200.
- **A tree that names no build backend is skipped with the reason.**
  Section 3's metadata is a distribution's, so a `pyproject.toml` that
  builds none holds no subject for it, which is what section 2 says of
  a rule whose subject a tree does not have.

### Section 5 names the rule behind each of its two ruff keys

- **The width bullet names `W505`** — issue #180. It stated
  `max-doc-length` as the whole of the second width, and the key
  configures a rule that has to be selected: a tree may keep the key and
  leave `W` out, which states a width and enforces none.
  `test_w_is_selected_with_max_doc_length_at_80` already asks a tree for
  both halves, and the section now says what that test reads it as.
- **An `ignore` entry beside a declared convention decides nothing** —
  issue #178. Measured with the pinned ruff, over a class docstring
  shaped to trip both pairs: `convention = "pep257"` alone and the same
  convention beside an `ignore` naming
  `incorrect-blank-line-before-class` and
  `multi-line-summary-second-line` report the same diagnostics, and
  neither prints the incompatibility warning ruff gives where nothing
  has settled the pair. The section says `ignore` names none of them and
  this tree's `pyproject.toml` names neither. What that issue records in
  the other repositories is theirs to answer.
- **The reason beside the two `D` exemptions stops claiming a sibling.**
  It said every sibling ignores the same two, and `btclib-secp256k1`
  ignores neither. The comment names the section that grants the
  exemptions instead, that being where the reason belongs.

### What decides an interpreter range, and the command that reads it

- **Section 1 says what sets the two ends** — issue #83. The section
  gave what `.python-version` and `requires-python` are and not what
  decides their values, which left the rule in the `.python-version`
  comments of the trees that state it. A library covers every
  interpreter still in support, which is python.org's release cycle and
  so moves on a date rather than on a decision; an application takes the
  newest its dependencies allow, and where a dependency holds it below
  the newest release, `.python-version`'s comment names that dependency
  and the condition for raising it. Which of the two a repository is,
  section 2's tier measures.
- **Section 15 gains the command that reads the window off every
  repository** — `requires-python`, the per-version classifiers,
  `.python-version` and the interpreters the platform sweeps run, one
  line each, so a tree out of step is a line out of step.
- **`interpreters_test.py` asks the half no tree can ask of itself** —
  whether the libraries name one window, the window being the release
  cycle's rather than any one of theirs. It asks every Python tree
  besides whether `.python-version` is the newest interpreter its
  classifiers name, that being one end of the window declared in two
  files, and asks every library whether it holds the module section 15
  names as reading its own three declarations against one another.

### Section 2's root files are asked of the tier that owes them

- **`root_files_test.py` reads the table's `tiers` column and asks each
  row of every tree it reaches** — issue #195. The column is what says
  which tiers owe a file, and the only row a test asked of a tree was
  `SECURITY.md`'s, as the file `security_test.py` reads an address out
  of. The tiers nest, so a row is the last tier its cell names and
  `Tier.binds` answers for it as it does for a `tier` marker; a cell
  that is not the tiers from 1 down, and a file the table rows twice,
  are refused rather than read as whatever they parse to.
- **That direction and not the reverse.** A tier is a floor rather than
  a ceiling, so a row that does not reach a repository says nothing
  about a tree that carries the file anyway: `portanode` is tier 3 with
  the release documents its own practice needs, and this repository is
  tier 2 with the `SECURITY.md` GitHub shows for a repository that has
  none of its own. Reading the table in reverse would report both, and
  section 2 states each of them.

### A Dependabot ecosystem is owed where its subject is in the tree

- **Section 11 puts on `uv` the condition section 2 already states for
  it** — issue #175. The section gave `github-actions` and `uv` to every
  tree, where section 2's *a rule whose subject the tree does not hold
  asks nothing of it* names a section 11 ecosystem with no lock file to
  read as its own example. `uv` now sits with `bundler` and
  `gitsubmodule`, declared where the tree holds a `uv.lock`, and
  `github-actions` is what every tree declares, workflows for it to read
  being every tier's.
- **portanode declares `github-actions` alone and is keeping the
  section.** It holds no `pyproject.toml` and no `uv.lock`, so the `uv`
  ecosystem has nothing to read there; `dependabot_test.py` asks `uv`
  against the tree like the other two, and the backlog row that carried
  the disagreement goes with the assertion that made it fail.

### Section 12 says which archives the release variable reaches

- **`SOURCE_DATE_EPOCH` reaches hatchling's archives and not
  `uv_build`'s** — issue #140. Section 12 stated of both backends that a
  commit gives one digest whether the variable is exported or not, which
  is `uv_build`'s answer alone: hatchling writes the exported value into
  the sdist and the wheel, and a constant of its own where nothing
  exports it. Measured by building a project under each backend twice,
  once with the variable unset and once set to an arbitrary second, and
  comparing the archives' digests and member timestamps.
- **A publisher on hatchling that exports the variable for its bill of
  materials moves the digests its attestation vouches for** — issue
  #144. The document's timestamp is the variable, so a tree gaining the
  document exports it, and the bullet above it now says what that
  reaches.

### Section 3 says what `license-files` names

- **The list is `LICENSE` and `AUTHORS.md`, in a file that declares a
  build backend** — issue #200. The section asked for the key and not
  for its contents, so section 14's clause keeping `COPYRIGHT` out was
  the only statement about what the list holds. `LICENSE` alone is
  weighed beside it: the notice names a collective, and `AUTHORS.md` is
  where the archive says its members are listed.
- **The test reading the key says what asserting the two names waits
  on** — btclib-org/btclib-node#235. `pyproject_test.py` asks that
  `license-files` is declared, the section being where what it holds is
  stated.

### The test-file spelling and the public surface each state one rule

- **The test-file spelling is a choice between two patterns pytest
  collects alike** — issue #131. Sections 4 and 7 named
  `name-tests-test`'s default as the rule and gave "a file pytest never
  collects" as the reason, which is the argument against a third
  spelling and not against `test_*.py`. Section 7 now says what picking
  one buys — `local-link-prefix`'s reason, one spelling for a check
  downstream to key on — and section 4 points at it instead of restating
  it.
- **Section 7's *Convention tests* paragraph no longer names a
  `test_`-prefixed suite.** It illustrated the freedom each tree has
  over its module names with a roll-call of the trees; what it gives
  now is the shape that decides it, a package of one module folding
  checks that elsewhere want a module each.
- **The public surface is not a convention a published package may
  decline** — issue #79. Section 7's closing clause let a repository out
  of any bullet its own prose does not state, and a package shipping
  `py.typed` has a public surface whether its prose states one or not: a
  module declaring no `__all__` answers `import *` with the names it
  imported, private modules' included. The bullet gains the condition,
  and states the exception `btclib`'s own census keeps: a module under a
  private name is no part of the surface. The clause keeps its shape.
- **`surface_test.py` asks it of every tree that publishes**, reading
  `__all__` off the checkout rather than importing a package nothing
  here installs. `btclib-secp256k1` is a backlog row against issue #79,
  which stays open for the modules and the census it owes.

### Who owes a verbatim copy is section 14's to say, and the suite asks

- **Each bullet of section 14 opens with one of two spellings of who
  owes a copy** — issue #89. The clause was each bullet's own prose, so
  `tests/verbatim_test.py` could not read it and answered for the copies
  it found alone: a tree short of a file it owes read like a tree the
  file does not apply to. `owed by every repository` is asked of every
  tree by `test_a_repository_carries_the_verbatim_files_owed_of_it`, and
  `owed where` and its condition are left to the reader.
- **`subjects` in `tests/__init__.py` answers with each bullet's clause
  beside its subject**, and refuses a list naming one subject twice,
  which a mapping would otherwise read as one bullet and drop the other.
- **The shared half of a copy ends at one newline** — issue #160. The
  cut is made at a marker opening with a newline of its own, so a copy
  that leaves a blank line before the marker and one that does not
  differed by a byte a diff renders as nothing.
- **The shared `.gitattributes` reasoning says that both `merge=union`
  lines are in every copy** — issue #157. Section 2 gives
  `RELEASE_NOTES.md` to a repository that publishes, and the reasoning
  section 14 makes verbatim spoke of *these two files* to a tree holding
  one; an attribute on a path the tree does not hold matches nothing,
  which is what the comment now says. Sweeping the other copies is issue
  #192, named in `EXPECTED_DRIFT` so that the drift is an expected
  failure rather than a red row.

### Section 4's docstring key, section 12's installer, section 13's mypy

- **`skip-checking-short-docstrings` is decided by the form a docstring's
  contract takes** — issue #114. The setting was each repository's to set
  and to say why, which left the reasons beside it answering two
  different questions. Section 9 asks a docstring for the contract and
  does not ask for a section, so `false` is the answer where a section is
  how a tree's docstrings state it and the default is the answer where
  prose is, pydoclint reading a section and not a sentence. What changing
  the setting would cost stays with the issues tracking it.
- **Section 13 says what the mirror branch leaves the editor reading** —
  issue #82. Under `useBundled` the extension's mypy is not the hook's:
  it is the version the extension ships rather than the one the `rev`
  pins, and it has none of the stub packages `additional_dependencies`
  installs, so an import the hook resolves is unresolved in the editor.
- **Section 12 asks the sdist gate for `--installer=pip`** — issue #145.
  `uv build` builds with the copy of the backend bundled in the running
  uv whenever `build-backend = "uv_build"` — isolation disabled or not,
  and with no `uv_build` in the environment at all — so the
  `additional_dependencies` the section asks for decides nothing on
  `check-sdist`'s default path. Under the pip installer the archive is
  `build --no-isolation`'s, and a hook environment that does not satisfy
  `requires` fails the gate rather than warning, so the backend that
  packs it is one `[build-system]` admits. What that failure does not
  catch is a `requires` widened past the hook's line, which the older
  line still satisfies; the section keeps that as the half issue #145
  leaves open. Section 16's checklist step names the installer beside the
  inclusion table.

### Section 9 says what to cut, and what union costs the gate

- **The habits that lengthen prose without adding to it are named where
  a reader cuts them** — issue #104. The sentence that only introduces
  the next one is decoration, and the negative result a comment carries
  is the rejected alternative and what rejects it rather than a tour of
  the others, which is where the section's demand for the negative
  result stops. The copy in the half of `btclib`'s `CONTRIBUTING.md`
  that is its own is btclib-org/btclib#1300.
- **Section 9 states `merge=union`'s mechanical price beside its
  semantic one** — issue #138. Two branches each adding a `###` section
  under `## Unreleased` produce a file whose second heading sits against
  the bullet above it, which MD022 and MD032 both refuse. What puts the
  line back is reading the file after a rebase: the hook reports without
  fixing, and this file has the two rules off at its head.
- **A package upstream of another does not name the one downstream** —
  issue #81. The organization that publishes a package and where it sits
  in the family are what a consumer chose it for and stay; the prose of
  each repository upstream of `btclib` is a box of that issue of its own,
  and it stays open for them.

### Test data is vendored, and section 7 says what that means

- **Section 7 states the rule and names the two kinds of file** — issue
  #80, which stays open for the boxes that are each repository's. The
  data a test reads is committed beside it and the suite opens no
  socket. A vendored upstream file is a copy of a file in somebody
  else's repository, which a commit and a git blob SHA-1 identify;
  recorded or constructed data is written from a project's source, so
  there is no upstream blob and nothing for a pin to name. A rule
  conflating the two asks for a pin that cannot exist, or lets a copy go
  unchecked among files that cannot be.
- **The pin format is the standard's now, written once**: the fields
  the pinning trees already use, under a heading naming the file, in
  one `README.md` in the `_data` directory. `blob` is the git blob
  SHA-1, which a tree entry already carries and `git hash-object`
  reproduces locally, where a digest of the bytes says only that the
  copy has not changed here.
- **A `_data` directory sits beside whatever reads it**, `tests/_data/`
  where the suite is the only reader, and the underscore is what says
  the directory is not a package.
- **A tree with vendored upstream files runs `vendored-vectors`; one
  with only recorded data says so where the workflow would be**, an
  absent check otherwise reading as an omission.
- **Two rules the vendoring trees keep and this file did not carry.** A
  vector the tree fails is vendored anyway and marked `xfail`, and a
  licence travels with the file it covers.

### The new-repository checklist chooses no mypy hook shape

- **Section 16's `.pre-commit-config.yaml` step points at section 4's
  criterion** — issue #121. Section 4 states the mypy hook as a
  trade-off with two right answers and gives what chooses between them,
  and section 13 keys `mypy-type-checker.importStrategy` off whichever
  shape a repository took; the step named one of the two, so a
  repository built from the checklist had the choice made for it by a
  list that does not say it is choosing. Section 16's normalizing
  checklist names no shape either.

### A Dependabot ecosystem is asked of the tree that would carry it

- **`dependabot_test.py` asks the two halves of section 11's sentence
  nothing asked** — issue #171. Membership in the four ecosystems the
  section names was the whole of the question, leaving the pair the
  section gives every tree, and the condition it puts on the other two,
  measured by nothing. `github-actions` and `uv` are now asked of every
  tree, and `bundler` and `gitsubmodule` are asked in both directions
  against what `git ls-files` finds — a Gemfile at any depth, a
  `.gitmodules` at the root.
- **portanode is a backlog row against issue #175.** It declares
  `github-actions` alone, and whether the tree owes `uv` or the section
  owes `uv` the condition it already states for the other two is what
  that issue decides.
- **A tree with no `.github/dependabot.yml` is an error rather than a
  failed assertion**, the shape `hooks_test.py` uses for a tree with no
  lint gate: a backlog row excuses an assertion, and a file that is gone
  is not one.

### An aggregate job answers to a branch rule, not to a matrix

- **Section 10 states one rule for when a workflow needs an aggregate
  job** — issue #90. Its first sentence asked every matrix workflow for
  one, a later bullet conditioned it on the workflow's answer becoming
  required, and a repository adding a `codeql.yml` chose between the two
  readings in a comment of its own. What the aggregate is for decides
  it: a branch rule can name only a context a pull request produces, so
  a workflow triggered by `push` and `schedule` alone has no name a rule
  could hold, and how many cells it runs changes nothing. The
  conditional reading goes with the sentence that carried it.

- **`REPOSITORY.md` reads the corrected rule.** Its note beside the
  `Lint` context put the aggregate down to a matrix, which is the
  reading section 10 no longer carries; the one job it names is the
  context because the workflow has one job.

### The suite refuses a `License ::` classifier beside the expression

- **`classifiers_test.py` asks the other rule section 3 states about the
  list** — issue #126. Such a classifier is a current entry of PyPI's
  list, so the comparison that module already makes passes it, and the
  build backends this standard keeps put the pair into an archive
  without refusing it. It reads the parsed `classifiers` and not the
  file: in this organization the string occurs in a `pyproject.toml`
  only in the comment explaining the classifier's absence. A failure
  names the repository and the grep that shows those lines in its
  checkout.
- **The expression the classifier duplicates is asked by nothing** —
  issue #173. A tree declaring the classifier and no `license` string is
  short of the expression rather than carrying the pair, which is that
  issue's question and not this test's.

### Section 5's two ruff settings, kept here and asked of every tree

- **`pyproject.toml` declares `max-doc-length` and the pep257
  convention** — issue #163. The section states both for every Python
  tree, and the tree holding the section set neither: W505 is inert
  without the width, ruff having no default doc length, and the `D`
  family runs the whole of what ruff writes under that letter without
  the convention. A docstring in `tests/protection_test.py` that sat
  over the width now fits inside it.
- **`tests/pyproject_test.py` asks both of every repository**, in the
  shape it already asks section 5's `CPY`: the family and the key
  together, since either half alone gates nothing. bbt sets the width
  and selects no `W` — issue #176 — and bbt and btclib-node select no
  `D` — issue #177 — so those cells are rows of the backlog.

### The support line is asked of the repositories that publish

- **Section 2 asks for the support line at tier 1** — issue #98. The
  README is the long description an index renders, so a reader who has
  that page and not the repository has nothing of the organization
  beside it; where nothing is published the README is read on github.com
  under `btclib-org`, and `profile/README.md` is where the organization
  says it. The rule stands beside the loop that checks it, over the
  repositories the tier binds, and the repositories that publish each
  owe a pull request adding the line.
- **This repository's `README.md` ends without the line.** It publishes
  nothing, so `profile/README.md` carries the organization's only copy.

### Section 6's mypy block names only what it buys

- **`show_error_codes` goes from the sample** — issue #170. mypy has no
  such option: `Options` carries `hide_error_codes`, `False` before a
  config file is read, and the key reaches it through the config
  parser's `show_`/`hide_` inversion, so a tree copying the block gets a
  line that reads as a check and is none. The rule stated beside the
  error codes now covers a key already at the value the block would give
  it, with `mypy --help`'s inverse form as what says which those are;
  this repository's own `pyproject.toml` drops the key with the sample.
- **`docs/source/conf.py` is named as outside the scope** — issue #149.
  Sphinx is the `docs` group's and no shape of the mypy hook installs
  it, and `python_version` is one value for a whole table, so asking for
  the file means answering which version to check it at. The exemption
  carries what it costs: every documentation build executes that file,
  and a repository bringing it into scope answers the version question
  first.

### The ack step's comment reads in any tree that carries it

- **`claude-review.yml`'s ack-of-this-head comment cites what every
  copy has** — issue #151. It cited `README.md`'s section 11, which is
  this repository's standard rather than the file beside a copy of the
  workflow, and it names `REVIEWING.md` for where a verdict sits and the
  btclib-org repository standard for the half `REVIEWING.md` does not
  state. The commands in it take `{owner}/{repo}` and a placeholder
  number, so `gh` resolves them against the checkout they are run in.

### A review runs before the push, and one workflow's change gets none

- **Section 11 says a review pass runs locally before the branch is
  pushed, and names what runs it.** `.claude/commands/review.md` with no
  argument reads the branch's diff against `origin/main`; what the pass
  reaches is the class of finding no gate and no pattern does, and what
  it buys is that the forge's round is the last rather than the first —
  issue #45.
- **The exception to the ack of record now stands beside the rule.** A
  pull request adding or editing `claude-review.yml` gets no verdict and
  lands on its gates carrying that change alone — issue #58. The
  consequence was under the subsection on porting the workflow, which
  keeps the mechanism it defers to and points at the rule for what it
  costs.

### The standard names the private channel a `SECURITY.md` promises

- **The advisory form is owed at every tier** — issue #100. Section 2
  gives the file to a publisher and lets the rest inherit this
  repository's, and that policy sends a reporter to the Security tab of
  the repository the defect is in, so the setting behind that tab is
  every repository's whether or not it carries the file. `REPOSITORY.md`
  reads this repository's own back.
- **The reporting address is *security at btclib dot org*, spelled
  out** — issue #109. One mailbox for the organization, because whether
  a mailbox is answered is not something a reporter can check; the
  spelling is what a harvester reading a public file does not lift.
- **Section 15 measures each**, so a `SECURITY.md` written next is
  written against the standard rather than against whichever sibling was
  nearest. The address loop prints the repositories with no file of
  their own rather than answering blank for them, so a blank is a policy
  the pattern found no address in and is not read as agreement.
  `tests/security_test.py` is the running half, and it names the
  sections that decide it.
- **Section 15's calendar is an audit no single tree can answer rather
  than the one.** This block is another, and so is the `claude-review.yml`
  sweep beside it.

### The tree's own comments say what the rule is, in the present tense

- **Two backlog rows are spent and go.** Every tree that runs mypy
  carries section 6's error codes now — issue #165 — and bbt's gate runs
  mypy since btclib-org/bbt#24, so the rows recording those two against
  issues #165 and #112 record nothing. Issue #131's pair against
  btclib-node stays, suspended on the maintainer's decision while
  another session annotates that tree.

- **`dependabot_test.py`'s docstring says what section 11 says now.**
  Section 11 stopped closing the count at three ecosystems in this same
  change, and the module that enforces it went on stating the closed
  count — the exact sentence issue #132 was filed against, left standing
  in the test while the standard was corrected. Section 15 makes a
  module's docstring the statement of which section it reads, so that is
  where a reader sent by the audit is told. It now names the two an
  ecosystem-carrying tree has whatever it holds and the two it earns.
- **An unclosed fence is no block.** `fenced()` promised to raise where a
  section does not hold exactly one, and a fence opened and never closed
  read to the end of the file and came back as one — past the section
  that was asked for. It is discarded instead, and the docstring says
  what a fence has to look like to be read.

- **Comments stop telling the tree's history** — issue #167.
  `.github/dependabot.yml`, `.github/workflows/links.yml`,
  `.pre-commit-config.yaml` and `tests/__init__.py` each carried a clause
  about what this tree used to be, which stays grammatical after it stops
  being true. Section 9's *No history in the prose* puts the
  before in this file, and the present-tense remainder of each comment
  carries the reason on its own.
- **The reason beside `check-toml` names the case the hook catches** —
  issue #166. It said taplo says nothing about what it cannot read: what
  taplo cannot read fails `taplo-format`, and what `check-toml` adds is
  the other class, a key or a table declared twice, which taplo formats
  and passes.

### Section 1's groups, section 6's error codes, section 11's ecosystems

- **`build` and `check` are two rows, and `bindings` is a third.** The
  table said `build` held what inspects a distribution, which is what
  three trees call `check`, while the one tree holding both names uses
  `build` for what compiles wheels. Each row now says what its group
  holds, and the paragraph beside them says why the two names are worth
  keeping apart — issue #129.
- **The `harness`/`test` split is paid for by the tree that asks for
  it.** The section claimed the split kept the workflows the same file
  everywhere; one tree's workflows name the group.
- **Section 6 states the optional error codes, and they are the same
  list in every tree** — issue #165. A code that finds nothing today is
  a ratchet on the line written after it, and a code mypy turns on
  itself is not in the list, naming it stating a check the list does
  not buy. `tests/pyproject_test.py` reads the block as data and asks
  every tree for exactly it.
- **`gitsubmodule` is an ecosystem section 11 names**, conditional on
  the tree having a submodule the way `bundler` is on a site Gemfile,
  with the limit beside it: Dependabot follows upstream's default
  branch, so its pull request says upstream moved and the release bump
  stays by hand. Section 4 stops saying a submodule is beyond
  Dependabot's reach — the local hook and the ecosystem answer
  different halves — issue #132.

### A review reads the prose that stays

- **A suite is run whole, by whoever runs it.** `REVIEWING.md` asked
  for no run at all where the author's gates were on the record; it now
  says what a run has to be — never a module, a `-k`, a `--lf`, a
  deselect or a marker in its place, because what a change breaks is
  found by the test that did not expect it, and a subset is chosen by
  what the author expected. A narrowed or cut-short run is reported as
  no run. The suite is not excepted from the paragraph below it: a
  reviewer relying on an author's run relies on a whole one.
- **Prose is reviewed where a reader of the tree will meet it.**
  `REVIEWING.md` said a commit message was tree prose answering for
  itself; it now says what a review reads for truth is the
  documentation that stays — `README.md`, `CONTRIBUTING.md`, a
  docstring, a comment — and that a commit message or a pull request's
  body, read once at the landing, is a finding only where it decides
  something.
- **A count, a measurement nobody re-derives, and the history of the
  code are findings.** The check every review makes asks for the figure
  to go or for the command that re-derives it to take its place, and
  for a comment or a document that tells what the code used to be to
  stop — section 9's rules, named where the reviewer reads them.

### This tree answers the rows the suite held against it

- **The gate runs `check-toml`, `toml-comment-width` and
  `decoded-subprocess-encoding`.** Section 4 lists the first among the
  syntax hooks and the other two among the local ones, section 3 names
  `toml-comment-width` as what holds a `pyproject.toml`'s comments to 80
  columns, and `.pre-commit-config.yaml` here ran none of the three:
  taplo formatted the toml and passed a key declared twice, the comment
  width was kept by hand, and the suite's own subprocess calls named
  their encoding with nothing refusing the first that would not. The
  cells `tests/hooks_test.py` reported on this repository against issues
  #153 and #134 go from the backlog.

- **`links.yml` no longer passes `--cache`.** No step restored the
  cache file between runs, so the flag decided nothing across them, and
  it would decide nothing with the step added: the run is weekly and the
  cache age passed beside it was a day. Within one run lychee asks each
  URL once whatever the flag says -- `lychee --offline` over this tree's
  markdown reports the unique count beside the total. The cell
  `tests/links_test.py` reported on this repository against issue #111
  goes from the backlog.

- **`CPY` is selected, with `COPYRIGHT` transcribed as its
  `notice-rgx`, and every source file here opens with the notice.**
  `pyproject.toml` left the rule out as one only a package answers for,
  and section 5's rule is about every source file: a suite is source.
  The regex is the one `tests/copyright_test.py` derives, byte for byte
  the siblings', so the test that compares the two now reads this tree
  too. The cell `tests/pyproject_test.py` reported on this repository
  against issue #119 goes from the backlog.

- **`.github/dependabot.yml` exists, watching `github-actions` and
  `uv`, and `check-dependabot` validates it.** The layout bullet of
  section 2 lists the file for a repository that ships a package, and
  this one ships none; but the section also says `.github/` is every
  tier's and holds what the sections the tier binds ask of it, and this
  tree pins actions to commit SHAs and commits a `uv.lock` that nothing
  moved. Weekly on Thursday with the seven-day cooldown, grouped, as
  section 11 asks; the file's header says why no sentinel pre-validates
  what it opens. The gate runs section 4's `check-dependabot` over it,
  since `check-yaml` alone reads the file as yaml and not as what it is.
  The cell `tests/dependabot_test.py` reported on this repository
  against issue #107 goes from the backlog.

- **The suite's shared code is `tests/__init__.py`, and the gate runs
  `name-tests-test` at its default.** `tests/organization.py`,
  `tests/repositories.py` and `tests/tables.py` were the helpers, and
  section 7 puts shared test code in the package `__init__.py` because
  the hook at its default reads every other basename under `tests/` as
  a test module; this tree ran no such hook, which is how they stayed.
  They are one module now, imported as `from . import ...`, with
  each former docstring kept as a part of the package's. What moves
  with them is every name that pointed at one: the backlog is
  `BACKLOG` in `tests/__init__.py`, and section 15, `pyproject.toml`'s
  marker comments and `conftest.py`'s messages say so. The cells
  `tests/hooks_test.py` and `tests/layout_test.py` reported on this
  repository against issue #131 go from the backlog; the spelling
  question that issue holds open is untouched, this tree having been on
  `*_test.py` throughout.

### Section 15's audit runs as the suite, one row per repository

- **Section 15's commands are tests, asked of every repository at
  once.** The suite asked what no single tree could — the calendar, the
  verbatim copies, the rulesets — and left every per-tree command of
  section 15 to a person reading its output: `--frozen`, the action
  pins, the `permissions:` block, the syntax and local hooks,
  `name-tests-test` and the layout it enforces, `strict = true` and the
  hook that runs it, the copyright notice, the dependency groups against
  section 1's table, the project urls, the Dependabot ecosystems, the
  security address and the reporting setting, the newest tag's object
  type, the workflow token, classic protection, and the `links` workflow's
  `--accept` and `--cache`. Each is now a test taking a `repository`
  argument, parametrized over the organization at collection, so a run
  is the matrix issue #38 asked for and a failure names the tree and the
  command that decides it by hand. The commands are the audit issues'
  own — #88, #100, #105, #109, #110, #111, #112, #119, and #128 to #134 —
  and the first run reproduced every finding they record. None is
  resolved here: a red cell on a repository is the audit's answer, not
  the suite's defect.

- **A tier is measured, and a test names the tier it applies down to.**
  `tests/repositories.py` measures section 2's tier off each tree by the
  two files that section names, and a test marked `tier(n)` is skipped
  with the reason on a repository that tier does not bind, so the report
  says which cells were not asked and why. `tests/tiers_test.py` checks
  section 2's table against the measurement in both directions, which is
  the loop that section prints beside it.

- **What the tracker already records runs as a strict expected
  failure.** The backlog in `tests/repositories.py` is one row per
  issue, naming the test and the repositories whose failure that issue
  records, applied at collection, and only an assertion counts as the
  failure expected. A repository that catches up turns its row into a
  failure until the row is deleted, which is what closes the checkbox
  on the issue; a row naming a test no module asks per repository, or a
  repository the API does not list, refuses the collection rather than
  excusing nothing in silence. The alternative, a cell left red until
  its issue closes, would keep every run red for as long as the tracker
  holds a finding, and the first run held one for every row of the
  backlog. `tests/copyright_test.py`'s table of one repository moves
  into it, and its test is asked per repository like the rest;
  `verbatim_test.py` keeps its own, that one being keyed on a path and
  not on a tree.

  A row on a cell the run skips is reported as a failure too, naming
  the row. A repository that stops failing by losing the file the test
  reads, or by moving to a tier the test does not ask, is skipped
  before the assertion, and a skip is neither the expected failure nor
  the pass that would have turned the row red: on this branch before
  the hook, two such rows gave `2 skipped` and exit 0. `conftest.py`
  rewrites that report, and `tests/backlog_test.py` runs the hook on a
  suite of its own to show it does -- the one module whose subject is
  this tree rather than the organization, and the reason `pytester`
  is loaded.

- **A `main` with no classic protection fails the list, and only a
  repository the token cannot read is skipped.** The protection
  endpoint answers 404 to both, and `tests/protection_test.py` took
  both for a token without access and skipped: a repository that moved
  to rulesets alone, which is the very drift #88 is about, would have
  been reported as unreadable. The two are told apart on what `gh`
  wrote -- `Branch not protected` against `Not Found` -- and the first
  is the document with every field off, failing the one assertion the
  backlog excuses. `tests/links_test.py` reads `--accept=<list>` as
  well as `--accept <list>`, the one-word spelling having read as the
  default.

- **The run without the switch reaches nothing.** `BTCLIB_INTEGRATION`
  was read by an autouse fixture, which runs after the session fixtures
  a test asked for: on a snapshot of `main` before this change,
  `pytest --durations=4` without the switch showed the rulesets fixture
  set up in twelve seconds and the trees cloned in seven, and then every
  test skipped. The switch is now read at collection, where a skip is
  decided before any fixture is set up, and the same run takes a
  fraction of a second.

- **Section 15 says what runs and what a person still reads.** Its
  opening no longer says the suite asks only what no single tree can;
  it says that which repositories a question is asked of is section 2's
  tier, that which failures are already filed is the backlog, and that
  two of its audits stay a reading — `tests/README.md` against section
  7, and the workflow comments. `CONTRIBUTING.md`'s last section and
  `alignment.yml`'s header say the same of the suite, and
  `settings_test.py` no longer says classic protection and the workflow
  token stay a person's to run, since they do not. `pyproject.toml`
  registers the `tier` marker, `--strict-markers` being on.

- **Found by the first run and filed, not fixed: #153.** `check-toml` is
  absent from two trees that track toml, which the syntax-hook test
  reports once it asks for a hook only where the tree tracks the file
  type — section 4's own condition, `check-hooks-apply` refusing a hook
  that matches nothing.

### Section 12 states what a publisher owes, in the terms of its backend

- **A published sdist reproduces from its tag, as a property.** Section
  12 stated the reproducible build as setuptools' two mechanisms —
  `SOURCE_DATE_EPOCH` from the tagged commit and a normalization step —
  on a standard whose section 3 keeps no setuptools. It now states what
  the attestation makes every publisher owe, a rebuild of a released tag
  giving the bytes the attestation names, and says what the normalizer
  is in that: not a belt over a backend that already writes fixed member
  metadata but the step that decides the bytes, since it rewrites every
  member's mtime from the backend's constant to the commit's date and
  the digest with it. Issue #140 has the measurement on
  `bitcoin-core-rpc`, member mtimes `0` before the step and the commit's
  second after. So every publisher carries the step, and the alternative
  — each tree weighing whether its backend has made the step inert — is
  named as the reading under which a migration dropped it. The compiled
  case is exempted with its reason beside it: `btclib-secp256k1`'s
  wheels are built by cibuildwheel against a toolchain nothing pins. The
  variable is exported for what reads it, the normalizer and the bill of
  materials, and not for the archives.

- **The bill of materials is owed, not presupposed.** The same bullet
  said the bill of materials was reproducible "for the same reason", of
  publishers of which one produces a document. It is now a bullet
  of its own: every publisher attaches one and the attestation signs it,
  with what makes it reproducible — `SOURCE_DATE_EPOCH` as its timestamp
  and the distribution files' digests under its serial number — beside
  the rule, and the two exemptions that were argued weighed in it. Issue
  #144 is the tracker for the trees that still owe one and is not closed
  by this.

- **`check-sdist` runs wherever an sdist is built.** Section 12 asked for
  it only where the inclusion is an include list, on the reasoning that
  an exclude list's failure is an archive too wide and not silent. That
  conditional was `check-manifest`'s, which read a setuptools include
  list and had nothing without one; `check-sdist` compares the archive
  against what git tracks in both directions and its exit code says
  which way, so the case the conditional exempted is one it answers,
  and nothing else in a release path reads the archive's members. The
  condition leaves sections 4, 12, 15 and 16 together, and the worked
  answer for `btclib-secp256k1` says what the check costs an exclude-list
  tree, the `[tool.check-sdist]` table, rather than that the question is
  not its own.

- **A hook that builds the project builds it with the declared backend.**
  `check-sdist` and `pyroma` build without isolation, so the backend is
  the hook environment's, and `uv build` handed a `requires` its own
  version does not satisfy falls back to the backend it bundles and only
  warns. Section 12 asks the hook to carry `additional_dependencies`
  naming the backend at `[build-system]`'s own specifier, which is what
  has to agree with `requires` — the backend, not the `uv` that drives
  it — and records pinning `uv` on the hook as the alternative. Issue
  #145 measured it on `pyroma`; that a specifier written twice is a
  range that drifts stays open there.

- **Section 3 separates a floor from the boundary it keeps.** The floor's
  reason named a property that arrives in `0.12.0`, `pyproject.toml.orig`
  beside the normalized copy in the sdist, for a floor at `0.12.5`. The
  section now states them as two facts — the boundary, and a floor above
  it being alignment with the `uv` the gate pins — with the measurement
  that locates a boundary: the backend's own `build_sdist` hook at each
  version, and not `uv build` under a pinned `requires`, which answers
  for the backend it bundles. Issue #143 has the table.

### Section 2 says which repositories the standard binds, and how far

- **Three tiers, measured by two files.** A repository is Python where
  it holds a `pyproject.toml` and publishes where it holds
  `release.yml`; tier 1 is both and owes the whole file, tier 2 is the
  first alone and owes everything but section 12 and the two release
  workflows, tier 3 is neither and owes sections 9 and 11 with what
  they name. The tiers nest, a rule with no subject in a tree asks
  nothing of it at any tier, and a tier is a floor: `portanode` cuts a
  signed tag by hand above its tier, and a repository short of its tier
  is a gap unless the reason is written where a reader meets it. Issue
  #37 proposed the three.

- **Every repository has a row, and a loop re-derives the table.** The
  three that publish are tier 1, `btclib-benchmarks`, `btclib-node`,
  `bbt` and this repository are tier 2, `portanode` is tier 3 — the
  loop beside the table is what was run, and a new repository is a row
  in the pull request that creates it, now section 16's first step. The
  root-files table gained a column saying which tiers owe each row, in
  place of the prose that named `SECURITY.md` as the one conditional
  row.

- **A tier-2 repository carries neither `RELEASING.md` nor
  `RELEASE_NOTES.md`.** A release document in a tree that cuts no
  release says only that it does not — `bbt`'s and `btclib-node`'s open
  so — and that is a sentence in `README.md`, not a file; the release
  notes have nothing to be on top of where no version is cut. The
  alternative, carrying both ready because a tier-2 repository could
  release tomorrow, is recorded beside the rule with why it lost: the
  day a release arrives it arrives with `release.yml`, and the files
  with it. This reverses what issue #37's body had ticked as decided,
  and the reason is in section 2 rather than in the issue.

- **This repository keeps the rule it states.** Its `RELEASE_NOTES.md`
  is gone, its `README.md` says it releases nothing, and issue #120,
  which asked it for a `RELEASING.md`, is answered by the tier rather
  than by the file. `SECURITY.md`, which sent a reader to `RELEASING.md`
  for what a release is in a given tree, now says where a tree that
  carries none answers instead. `.gitattributes` keeps its
  `RELEASE_NOTES.md` line: an attribute on a path that is not there is
  inert, and the file stays the same in every tree.

### COPYRIGHT is transcribed into the gate, and the transcription is checked

- **Section 14 says what the file is.** It said one line naming the
  holder, which every header points at instead of repeating; the file is
  three lines, and every source file repeats them, which is what `CPY`
  with an anchored `notice-rgx` enforces. The bullet now says so, and
  that the file is a repository's and not a distribution's: `LICENSE`
  carries the holder for whoever has the archive, so `COPYRIGHT` leaves
  `license-files` — issue #135, where the three packages that ship it
  are measured.

- **`tests/copyright_test.py` compares the regex against the file.**
  `CPY` checks every header against `notice-rgx`, and nothing checked
  `notice-rgx` against the `COPYRIGHT` it was copied from, so a tree
  whose two disagreed passed its own gate. The test derives the regex
  from each repository's `COPYRIGHT` the way section 5 now spells out —
  metacharacters escaped, lines joined by `\n`, anchored with `^` — and
  refuses a declared one that is not it. Measured against the tip of
  every repository: five declare the derived regex byte for byte, and
  `bitcoin-core-rpc` declares the MIT notice in full by a departure its
  own file records, which is issue #119's and not this one's. That
  repository is a row of the backlog in `tests/repositories.py`, a
  strict expected failure naming the issue: the suite stays green on a
  drift already filed, and the day the tree aligns the unexpected pass
  turns red, which is the signal to delete the row.

- **`.gitattributes` is a section 14 file.** Every repository carries
  it and every copy sets the same two files to `merge=union`, and the
  section did not name the path, so `tests/verbatim_test.py` never
  compared the copies: the eight are seven distinct files, differing in
  the comment's wording and in the order of the two lines, and
  `portanode`'s and `btclib`'s add rules for paths only they carry. The
  bullet puts those under `## This repository in particular`, a comment
  to git and the marker the comparison already stops at, so the
  comparison covers the file without a second rule for it — issue #102.
  The path sat in `verbatim_test.py`'s own `EXPECTED_DRIFT` on the same
  terms as above while the seven copies were aligned one pull request
  each; with the last landed the entry is gone and the comparison runs
  red on the next drift.

- **The `ci:` block's verbatim part is named.** Section 14 called the
  block verbatim in part without saying which part: `autofix_prs`,
  `autoupdate_commit_msg` and `autoupdate_schedule` are shared, and
  `skip:` is the repository's own because it can only name hooks that
  repository defines. It also says that no test and no section 15
  command compares the shared part — issue #103.

- **The badge paragraph states the reason and not the repair.** Section
  4's local-link-prefix bullet said what the first version of the hook
  could not reach and what had been cited; section 9 asks for why the
  pattern is as it is, in the present tense. A badge nests a link inside
  a link, and that is now the whole of the paragraph's argument — issue
  #117.

### A review that ran out of time, or that the action refused, says so

- **The budget is the review step's, and running out of it is said.**
  `claude-review.yml` held its fifteen minutes at the job, and a job that
  hits its limit is *cancelled*: nothing after the killed step runs unless
  it asked to run on a cancellation, and nothing here did, so the pull
  request shows a failed check with nothing from this file beside it —
  issue #60 measured two reviews that had read as reviews that found
  something, and the jobs API was what said they had run out of time. The
  limit is now on the step, which *fails* it with the runner's own line
  saying it timed out, and the guard after it runs on any outcome but a
  cancellation and says what that means: no verdict was written, and no
  verdict is no ack, so the row is red without being a finding against the
  tree. The job keeps a larger ceiling for the steps around the review,
  which read the API and post. A review that is going to exceed its budget
  still cannot post what it has, the action being killed rather than
  asked; that half of the issue is not answered here.

- **A review that ends without a verdict line is red, and was measured to
  be.** Issue #56's case — a summary declaring a finding blocking and
  ending on no `ACK` or `CHANGES REQUESTED` line — is what the step landed
  for issue #136 reports as *no verdict*, replayed against the comments
  pull request 53 carried at the time. The message now says that a comment
  whose last line is not a verdict is one of the things it reports, rather
  than only a job that wrote no comment.

- **The reviewer is told to read the title and description again.** The
  review of pull request 67 reported a title that `gh pr view` had been
  answering differently for most of the run: the correction landed after
  the push that fired the event and after the reviewer had started
  reading, by the issue timeline's `renamed` event against the run's own
  log — issue #69 had placed it a second after the push, before the job
  started, which the timeline does not support. Reading the title at job
  start, which the issue proposed, reads it *earlier* than the reviewer
  does and would have answered the old title too; and at the pinned
  revision the action, given a prompt, fetches nothing about the pull
  request and hands the prompt over as written, so what the reviewer reads
  is already the forge's answer at the moment it asks. What closes the
  window is asking again before a finding about the title or description
  is written, and the prompt now says so. An `edited` trigger, the change
  under which a correction re-fires the review, is not taken here: the App
  that appends its summary to a description edits it after opening, and
  what its run would do to the review in flight — a bot actor the action
  refuses, a concurrency group that may or may not cancel for a job
  skipped by its condition — cannot be tested on the branch that proposes
  it, for the reason issue #58 records. Section 11 says what a review
  reads beyond the sha in those terms.

- **Dependabot is named to the action, and the second secret store is in
  the standard.** Issue #77 began as a credential in the wrong store and,
  once the maintainer had added `CLAUDE_CODE_OAUTH_TOKEN` to the
  organization's Dependabot secrets, ended one step later at the action
  refusing a run a bot initiated. The four repositories the issue names
  carry `allowed_bots: "dependabot[bot]"` since 2026-08-23 — not
  `btclib-node`, which configures Dependabot since the day before and is a
  finding against that tree, not this one; this copy carries it too, inert
  here where no `dependabot.yml` opens anything, because this is the file
  the others port. Named rather than `*` for the reason the input's own
  description gives on a public repository. Section 11 reads both stores
  back, and says why a repository that configures Dependabot needs the
  second. Skipping Dependabot's pull requests as a fork is skipped was the
  alternative, and it turns a missing credential into a missing review for
  a class of pull request whose whole value is landing promptly.

- **The command that checks a repository has the workflow answers.**
  Section 11's `gh api … --jq .name` put a 404's body on stdout, so a
  sweep over the organization read as a column of filenames with one JSON
  document in it, and the repository without the workflow survived for as
  long as nobody read the JSON — issue #137, and `bbt` was the repository.
  The line is now `--silent` with the exit code as the answer, the shape
  section 15's publishing sweep already had, and section 15 gains the
  sweep section 11's rule had no command for: one line per repository that
  lacks the file, silence where the rule is kept. Section 15's Dependabot
  calendar loop, which also reads a path a repository may lack, was run
  against one that lacks it: it writes its 404 to stderr and a `null` into
  `base64`, which complains there too — noise, and nothing false on
  stdout.

### The review check reports the verdict, not that the review ran

- **Green means an ack of the head.** `claude-review.yml`'s job was
  green whether the review acked, refused, or wrote nothing at all, so
  the row that reports the ack of record reported only that the action
  had started: the guard the job ended with tests whether an execution
  file was produced, which is a question about the invocation. A step
  past it reads the pull request's comments back, and fails on a
  refusal, on a verdict never written, and on an ack naming a sha the
  head has moved past. Issue #136 has all three measured, the last of
  them on two runs of one sha of pull request 139 that concluded success
  alike, the first having posted nothing and the second the review.

- **The last verdict decides, and the sha is the whole of the
  condition.** A second reading of the same tree can refuse what an
  earlier one acked, so it is the newest verdict that is read rather
  than an ack wherever it sits. It is matched against the head sha and
  not against the run's own clock: an ack belongs to a tree, so a push
  turns a stale ack red with nothing to compare times against, and a
  re-run of an unchanged commit stays green.

- **Section 11 says what a green row means.** It said that a green check
  was not an ack and that the check and the verdict were independent,
  which is what the step above makes false. The paragraph that named the
  guard's blind spot as a failure no copy's comments carried goes with
  it, that reason now being in this copy's comments.

- **The check still gates nothing.** It is not a required check and its
  own header says it must not become one; what the colour buys is a
  reader who sees a refusal in the checks instead of under the fold at
  the foot of a comment. Requiring it is a decision of its own, and the
  workflow's copy in every other repository of the organization is
  where the rule section 11 now states is not yet kept.

### Section 6 states the typing rule, and asks for the gate that runs it

- **The heading is the rule and the table is what applies it.** Section 6
  said what `[tool.mypy]` holds and never that a function carries
  annotations, so it read as a section about a configuration table
  alongside sections 5, 7 and 8, and the rule an author owes was legible
  only to whoever wrote that file. It now opens with the obligation —
  every function declares the types of its parameters and of what it
  returns — and the table follows as how it is enforced, which is the
  shape section 8 already had for coverage. The alternative was a
  section of its own, which renumbers every heading below it and every
  anchor under them, and the cost of that is not only the anchors: every
  repository names sections of this file by number in prose as well —
  in `CONTRIBUTING.md` and `REVIEWING.md`, which section 14 copies
  verbatim into each of them, and in `tests/README.md`, in workflow
  comments, in `pyproject.toml` comments and in the changelogs.
  `grep -rnIE "section (1[0-6]|[6-9])"` over a checkout of each finds
  a reference at 6 or above in every one, `bbt`'s `pyproject.toml` naming
  section 6 itself, where no anchor check reaches a toml comment at all.
  A heading would be a coordinated pull request per repository.

- **Nothing links the old anchor**, which is what made retitling free.
  Measured over a checkout of every repository in the organization
  rather than with code search, which answers 0 for an anchor `bbt` does
  carry because it skips forks: `grep -rhoI '\.github#[0-9]*-[a-z0-9-]*'`
  over all of them names `11-github-settings`,
  `9-prose-comments-and-docstrings`, `8-coverage-at-100` and
  `3-pyprojecttoml-is-the-configuration`, and no other.

- **The setting is not narrowed**, and the reason had to reach the
  honest case as well as the dishonest one. A lower setting, or an
  override switching a strict flag off for the directory that fails it,
  leaves `[tool.mypy]` stating a strictness the tree does not have. The
  bundle enumerated flag by flag does the opposite — it states exactly
  the severity the tree has — and is refused anyway, because what the
  section requires is the strictness and a trajectory toward it is not
  the strictness: `strict = true` tells a reader every function in that
  tree declares its types, where a subset tells them which checks it
  passes and leaves what is annotated to be read tree by tree.

- **A line that genuinely cannot be typed still carries its own
  `# type: ignore[code]`**, and that clause now reads *any of this*
  rather than *one of those*, which had pointed at the optional error
  codes alone. What is actually silenced across the organization is not
  those at all — `arg-type`, `assignment`, `list-item`,
  `no-untyped-call`, `no-any-return` — where among the optional ones
  only `redundant-expr` appears, so the narrow wording was wrong about
  nearly every site it governed. It is bounded to a check and never the
  annotation itself, so the heading above cannot be met by a bare
  signature behind `# type: ignore[no-untyped-def]`; no site in the
  organization silences that code today.

- **A configured severity that nothing runs is not this rule met.** A
  `pyproject.toml` can carry `strict = true` with no mypy hook in the
  lint gate, which holds every line of the section while nothing has
  ever type checked the tree. The clause went to section 6 and not to
  section 4, where the hook list is: section 4 already asks the gate for
  a mypy hook, and what was missing is not that the hook exists but that
  the declaration alone does not meet this rule — which is a statement
  about the rule, and belongs where whoever is held to it reads it.
  Section 4 keeps the hook and its shapes, and section 6 points there
  rather than restating them.

- **The audit follows.** Section 15's tree block gains
  `grep -n 'id: mypy' .pre-commit-config.yaml` beside the
  `strict = true` grep, and the sentence that names the pair of answers
  as the finding; section 16's normalizing step asks for the hook
  alongside the table, the new-repository checklist having named it
  already.

- **Measured, not asserted.** `uvx mypy` over an unannotated `def`
  reveals it as `Any` in and `Any` out, says nothing about a body that
  reads an attribute no object has, hands its caller `Any`, and exits 0;
  `uvx mypy --strict` over the same file exits 1 with `no-untyped-def`,
  `no-untyped-call` and `no-any-return`. That run is what the opening
  paragraph's widest claim rests on.

### One code of conduct, and a security policy where a package carries it

- **`CODE_OF_CONDUCT.md` is kept in this repository and nowhere else.**
  The file is a pointer to the PSF code of conduct: one policy for the
  organization rather than anything a tree has to say about itself, so a
  copy per repository is a copy of a pointer. GitHub shows this one for
  any public repository of the organization carrying none of its own,
  which section 2 says is display only, and display is the whole of what
  the file was doing in each tree. Section 16's first step no longer
  writes one into a new repository.

- **Section 14 no longer lists it**, and `tests/verbatim_test.py`
  therefore no longer compares it: the list's subject is a path that two
  or more trees carry, and a comparison of one copy has no state in which
  it fails. What the entry bought is had another way — the organization
  advertises a single policy because there is a single file, not because
  the copies were checked to be the same one. The repositories that still
  carry one drop it in pull requests of their own, and each may land on
  its own schedule now that nothing compares them.

- **`SECURITY.md` is owed by a repository that publishes and inherited
  everywhere else**, which makes it section 2's conditional row. What
  decides it is that the sdist carries the file, so a reader who has the
  archive and not github.com still reads the policy, and what such a file
  says — what belongs to that project, what its distributions attest to,
  what it is known not to do — is that tree's own. Which repositories
  those are is a measurement, and section 15 gains the command that
  takes it rather than this entry keeping a second copy of one. It
  answers `btclib`, `btclib-secp256k1` and `bitcoin-core-rpc` today. The
  `bbt` that PyPI serves under that name is a different project — this
  organization's sets `version = "0"` and says in `pyproject.toml` that
  there is no upload — which is why that command reads a distribution's
  project urls rather than its status code.

- **This repository carries the `SECURITY.md` the rest inherit.** It
  holds what is true wherever it is displayed — that an issue is public
  from the moment it is filed, the advisory route and the address beside
  it, that a defect belongs to the project whose code decides the wrong
  thing, and that a report goes wherever the reporter found it because
  routing one is the maintainers' job. What it cannot hold is the half a
  policy exists for: which flaws are that tree's, and what it is known
  not to do. That half is why a publishing repository keeps its own.

- **`MANIFEST.in` leaves section 2's table.** Which file declares the
  sdist's include list is the build backend's to say, which section 12
  settles and section 15's audit reads back, so the row was a third place
  for one fact. Nothing about a tree changes, and the row's departure
  asserts nothing about one: whether a given repository tracks a
  `MANIFEST.in` is answered by `git ls-files MANIFEST.in` in it, not by
  its backend.

### The support line names the organization

- **Every `README.md` ends by crediting the btclib organization and its
  projects**, where the line named `btclib` alone. That is the library's
  name, and section 2 asks for the line from a node, a benchmark suite
  and a course as well, where naming the library would credit the
  support to one of the things being supported. That section asks for it
  identical everywhere — this repository's own `README.md` and the
  organization profile included — and the wording is what makes that
  argument hold for a repository that is not the library.

- **Whether the line is owed at all is issue #98, and this does not
  settle it.** That issue's point is the choice between section 2 going
  on asking for the line and section 2 ceasing to ask, and it names
  `bbt` and `portanode` as repositories a support claim right for
  `btclib` may be wrong for. What changes here is how the line reads
  where section 2 asks for it; were that issue to decide the section
  should stop asking, the specimen goes and this wording goes with it.
  The copies that move are the specimen, the line this repository's own
  `README.md` carries and the one on the organization profile.

### A pure-Python project builds with `uv_build`

- **Section 3 states the backend.** `uv_build` where the project is pure
  Python, and what decides the exception is what a project compiles:
  `btclib-secp256k1` builds a vendored C library through cffi and cmake,
  which hatchling answers with a build hook and a pure-Python backend
  does not answer at all. What the move buys is where the sdist's
  inclusion is then declared — glob patterns in
  `[tool.uv.build-backend]`, beside the rest of the configuration,
  rather than in a file of its own with a language of its own. The
  requirement carries a ceiling at the next minor, uv bumping its minor
  for a breaking change and releasing the backend with itself, where the
  same section refuses an upper bound to a sibling dependency: what
  differs is that a bound on a build requirement narrows what an
  isolated build resolves for itself rather than what a published
  artifact accepts.

- **`MANIFEST.in` and `check-manifest` leave the standard with
  setuptools.** That hook gates a tree against a setuptools include list
  and has no subject without one. `check-sdist` takes its place: it
  builds the archive and compares it against what git tracks, and keys a
  backend plugin on the `[build-system]` string, so the include list is
  read from whichever table the declared backend reads and the
  exclusions are not written twice. Sections 4, 12, 15 and 16 name it
  where they named the tool that is leaving.

- **Section 12's example named a repository that had neither.** It said
  `btclib` owes the sdist half because "its `MANIFEST.in` is an include
  list": `btclib` builds with `uv_build` and tracks no `MANIFEST.in`,
  which the tree endpoint answers with an empty list:

  ```shell
  gh api 'repos/btclib-org/btclib/git/trees/main?recursive=1' \
    --jq '[.tree[].path | select(. == "MANIFEST.in")]'
  ```

  The paragraph's rule — which table declares the inclusion is the
  backend's — was sound, and the example was left behind by the backend
  move. The question under it is answered rather than dropped with the
  tool: a glob include list drops a tracked file as silently as a
  manifest does, and `check-sdist` in `btclib`'s gate is what catches
  it.

- **The PEP 639 floor is the backend's own, not `setuptools>=77`.** That
  constant was one backend's, and the projects not on that backend
  already declared something else: `btclib-secp256k1` writes
  `hatchling>=1.27`, where an older hatchling rejects the SPDX string
  and `license-files` outright, and `btclib` a `uv_build` floor chosen
  by what its sdist carries. A repository following the old sentence
  literally onto either backend wrote a requirement its build does not
  use.

- **Nothing local refuses the deprecated classifier beside the
  expression.** One file carrying `license = "MIT"`, `license-files` and
  a `License ::` classifier at once, built under each backend: the run
  is issue #113's, whose body carries the probe script and whose comment
  carries what it printed, and this change re-derived neither.
  `setuptools>=77` fails the build, `hatchling>=1.27` builds with no
  diagnostic at all, `uv_build` builds with a warning, and both archives
  that build carry `License-Expression: MIT` and the deprecated
  `Classifier:` line together, `twine check` passing both.

  What this change did re-derive is the half a command answers here: the
  `trove-classifiers` comparison passes the classifier too, asking
  whether a string is a classifier at all, and this one is a current
  entry of that list rather than a deprecated one:

  ```shell
  uvx --with trove-classifiers python -c \
    'from trove_classifiers import deprecated_classifiers as d
  print("License :: OSI Approved :: MIT License" in d)'
  ```

  So the backend that enforced the rule is the one leaving the standard,
  and section 3 says the rule stands on being read. Whether PyPI's
  upload endpoint refuses such an archive is still unmeasured: asking it
  means publishing a version.

### The calendar names the workflows that exist

- **Section 10's rows follow the file names the organization now uses.**
  `tests/grid_test.py` keys the calendar on a workflow's file stem, and
  the alignment that landed across the organization renamed the scheduled
  ones so that a prefix groups a family and a name says its own subject:
  `os-ubuntu`, `os-macos`, `os-windows`, `deps-latest`, `pypi-install`,
  `integration-bitcoind`, `integration-hwi`, `py-arm-authority`. Until the
  rows followed, the test failed in both directions at once — rows no
  repository schedules, and workflows no row names. No cron moved: each
  fires in the slot its old name held.

- **`portanode` and `bbt` have a minute.** Neither schedules anything
  today, so the reservations buy nothing yet; what they avoid is the
  other way `tests/grid_test.py` fails —
  `test_every_repository_that_schedules_anything_has_a_minute`, which a
  first cron landing in either tree would answer, where the rows above
  answer `test_every_cron_is_the_instant_the_calendar_names`. Issue #97
  names both: the rows because a rename left them behind, the minutes
  because `portanode` was never on that table at all.

- **`verbatim_test.py` passes.** Every path section 14 owes is one file
  across every tree that owes it, which
  `BTCLIB_INTEGRATION=1 uv run pytest tests/` answers for whole.

### The shared yamllint configuration runs the default set

- **`.yamllint.yaml` extends `default` here too.** The copy this
  repository keeps is the one section 14 compares the others against, and
  it was the copy that had never been fixed: it listed two rules and
  extended nothing, which runs those two alone and leaves indentation,
  trailing whitespace and duplicate keys unchecked under a gate that
  passes because a check nobody runs cannot fail. The repositories that
  already carried the fixed file are what this takes it from, verbatim;
  `gh api repos/btclib-org/{}/contents/.yamllint.yaml --jq .size` names
  them. Every yaml file in this repository, and in every sibling that
  copies it, is now linted against the whole default set rather than
  against two rules of it.

- **`document-start` gates rather than reports.** The default set carries
  the rule at warning, and the hook runs `yamllint` without `--strict`,
  where a warning exits 0: the convention every file already follows was
  never enforced by anything. It is an error now, which no tracked yaml
  file in the organization currently trips.

### The repository that owns the standard carries what it names

- **`REVIEWING.md` and `.claude/commands/review.md` are section 14
  entries.** Where the standard had reached, the copies were one file
  but for their H1 and the section whose title says it is not generic:
  that was the measurement this change rests on, taken before
  `btclib-org/btclib-benchmarks#159` moved one of them mid-branch. What
  the entry can still say without a claim that ages is what the shape
  became — the per-tree half is now that file's own last section, and
  `.claude/commands/review.md` follows it for the same reason, staying a
  file of its own rather than folding into `CLAUDE.md`, which every
  session loads including the one that wrote the diff.

- **A review need not deliver a verdict.** The ack of record is what a
  landing reads and ends in `ACK <sha>` or `CHANGES REQUESTED <sha>`. A
  reading that says what it found and stops is a review too: requiring a
  verdict of every reading prices each thing worth saying at a judgement
  on the whole change.

- **Two rules a reviewer had and the standard did not.** That a cited
  fact exists is not that the citation is honest, and a search for the
  cited term cannot tell the two apart. And a review says what it did
  *not* check — a command it could not run, an issue it could not read —
  because a review that answered whether a diff closes its issues against
  the pull request's own account of them is reasoning in a circle nobody
  reading the last line would see.

- **`CONTRIBUTING.md` and `REVIEWING.md` are one file up to their last
  section**, which is the tree's own and holds the commands, the gates
  and what a review of that tree checks beyond the generic. A human
  should not open an agent's file to learn how to run a gate, and
  section 2 calls `CONTRIBUTING.md` *"how to work"*.

- **Some of the files section 2 names and this repository lacked**:
  `COPYRIGHT`, `AUTHORS.md`, `CONTRIBUTING.md`, `REVIEWING.md`,
  `CHANGELOG.md`, `RELEASE_NOTES.md` and `.gitattributes`. Others it
  still lacks — `SECURITY.md` and `RELEASING.md` among them — and what a
  repository that publishes nothing owes of that table is not settled
  here. `CODE_OF_CONDUCT.md` and `LICENSE`
  take the text the siblings have yet to adopt, so both leave this
  repository out of group until they do; `LICENSE` also loses its year
  range, `COPYRIGHT` naming the holder without one, so the two disagreed
  the first January nobody remembered.

- **`AUTHORS.md` points at this repository's own contributors.** Section
  14 said the file was kept for the organization rather than per package;
  that holds today only because one graph happens to be a superset of the
  others, which nothing re-derives.

- **A shared file may answer for the tree it is in.** `CONTRIBUTING.md`
  and `REVIEWING.md` carry `## This repository in particular` as their
  last heading, and `tests/verbatim_test.py` compares what precedes it
  where a file carries one and the whole file where it does not. Without
  that rule those two would have been declared byte-identical while
  differing by construction, so the sentinel would have reported them
  drifted for ever — an alarm with no state in which it closes.

- **Section 9 states the rule for a cross-repository reference.** A bare
  `#123` resolves inside the repository it is written in. The rule was
  written in a per-tree section of `REVIEWING.md` and would have been
  lost when that section left.

### `CONTRIBUTING.md` names the landing queue

- **A repository with more than one pull request open lands one at a
  time** — issue #34. Rebasing every waiting pull request after each
  landing queues this repository's whole check matrix again, against the
  organization's ceiling on concurrent jobs, spending it on runs the next
  landing invalidates anyway; *The landing queue* now states the rule
  this cost taught, distinct from *One subject, opened as soon as it is
  written*, which governs when a finished pull request is opened rather
  than which of several already open ones reaches `main` next.
- **`EXPECTED_DRIFT` names `CONTRIBUTING.md`** — issue #281. The new
  subsection is `.github`'s alone until the other seven repositories
  carry it too, which section 14's own comparison would otherwise report
  as this organization's only verbatim-file drift.

### The `D`-family backlog row names `btclib-node` alone

- **`tests/__init__.py`'s `BACKLOG` row for issue #177 records the
  strict xfail against `btclib-node`** — `bbt` selects `D` with the
  `pep257` convention (btclib-org/bbt#45), and issue #177 stays open on
  `btclib-node`'s own instance of the family.

### Section 5's ruff `select` is `["ALL"]`, not a hand-picked list

- **A hand-picked `select` list is a thing that rots: nothing forces a second
  edit here the day ruff ships a family nobody has looked at.** `select =
  ["ALL"]` replaces it, and every exclusion now lives in `ignore` with the
  reason beside it, of one of three kinds: a rule the formatter conflicts with,
  cited from ruff's own `docs/formatter.md` rather than argued here; a rule this
  tree declines on its own merits — `TD` is the new entry of that kind, and
  section 5's argument is that it disagrees with `FIX` rather than duplicating
  it; and a finding real enough to act on, closed at its own site instead of
  silenced — typing-only imports moved under `if TYPE_CHECKING:`, two
  implicit-concatenation literals parenthesized, and `ANN401` and `ARG001` each
  answered with a `# noqa` and its own reason.
- **`tests/pyproject_test.py`'s checks for `CPY`, `W` and `D` read
  `select` for the family's own code; `ruff_selects()` now also reads
  `"ALL"` as every family selected**, so this repository's own tree —
  read from the working copy `trees` uses for `.github`, not fetched —
  keeps passing them under the new shape.
- **Section 14's "decided per repository" line named the `select`
  list's project-specific additions; it now names `ignore`'s own
  entries**, the shape a tree's own choice actually varies under
  `ALL`.

### The uv-floor backlog row is gone, and issue #312 with it

- **`tests/__init__.py`'s `BACKLOG` row for the uv-floor test is
  deleted** — closing issue #312: every repository committing a
  `uv.lock` names a floor at or below what `dependabot-core`'s bundled
  uv reads, so `test_the_uv_floor_is_not_above_what_dependabot_bundles`
  needs no strict xfail to excuse anyone.

### Section 14 states the default, and section 9 the CHANGELOG citation

- **Section 14 named what a repository copies verbatim and what it
  decides for itself, and said nothing about a convention that fits
  neither list.** It now states the default: one answer for every tree,
  with a differing convention filed here as a defect rather than kept as
  a choice; and what earns a place on the per-repository list is a
  reason true of that repository, not that the trees already differ.
- **`CHANGELOG.md` entries answering an issue have spelled the relation
  between the entry and the issue several different ways across the
  repositories, and section 9 named none of them** (closes #331): it now
  states the citation as `(closes #N)` where the change closes the
  issue, `(issue #N)` where it does not, qualified `owner/repo#N` across
  repositories — checkable against the landing commit's own subject,
  which the bare `(#N)` form some repositories use is not, GitHub
  numbering issues and pull requests in one sequence. The entries
  already landed keep whichever form they used.

### CLAUDE.md names the suite's switch, and the backlog's sibling-red

- **`CLAUDE.md`'s *Non-obvious facts* named the suite's subject and its
  missing coverage, and said nothing about how a run measures anything**
  (closes #343): the bullet now states `tests/conftest.py`'s
  `BTCLIB_INTEGRATION` switch, and that `uv run pytest` written the
  ordinary way exits 0 with everything skipped — the case *Verifying*'s
  own advice, to trust the exit code over the filtered output, does not
  cover.
- **The same section said nothing about a `BACKLOG` row turning red
  once a sibling repository lands the fix the row excuses** (closes
  #343): a new bullet names the strict-xfail mechanism and the two
  commands that tell a session's own branch apart from it —
  `git diff origin/main..HEAD -- tests/` empty, and the same run against
  a `git archive origin/main` snapshot.

### Section 9 puts a new entry at the end of the open section

- **Where a new `CHANGELOG.md` or `RELEASE_NOTES.md` entry belongs
  inside the section that has not shipped was each tree's own to read
  off its file** (closes #514): it is now the end of that section, after
  the entries already there and above the heading of the latest released
  version. What decides it is the `merge=union` driver rather than how
  the section reads — it places the side arriving second below the side
  already there, so appending leaves the entries in the order they
  landed in, where inserting at the top leaves a rebasing branch's entry
  under a neighbour it was not written for, its text unchanged and its
  diff an addition with no deletion counted.
- **Both alternatives are written down as rejected** (closes #514):
  newest first reads as a timeline to a person and buys nothing else,
  the order inside a section that has not shipped carrying no
  information and the release that closes it giving it a version
  heading; and section 14's *decided per repository* list takes a reason
  of a kind that a tree mixed by accident does not have.
- **The rebase bullet beside it now asks whether the branch's own block
  is still at the end of the open section** (closes #514), the diff
  being what says so, since no gate reads the order two `###` sections
  sit in.

### A name of the organization is spelled one way in a requirement

- **Nothing asked whether a requirement naming a distribution of the
  organization spells it the way that distribution names itself**
  (closes #335): PEP 503 folds runs of `-`, `_` and `.` before a
  resolver matches, so either spelling resolves and installs the same
  distribution, and the tree carrying the odd one passes its own gate.
  `tests/names_test.py` asks every tree for one spelling, in the
  requirement tables its `pyproject.toml` declares and in what it writes
  down elsewhere.
- **The position is read and never the spelling** (closes #335): the
  underscore is what the import package is called, and what PEP 427
  escapes the name to for a wheel or an sdist filename, so a test
  reading the spelling reports both and carries a list of exceptions
  instead of a rule. A name is a requirement where a table declares it
  as one, or where a version specifier or an extras bracket follows it,
  and an import package is written in neither position. What no
  position tells apart from prose is a bare name on an installer's
  command line.
- **What the second test reads is what a reader or a resolver meets**
  (closes #335): the files a tree tracks, less `CHANGELOG.md` and
  `RELEASE_NOTES.md`, which section 9 says nothing already written in is
  rewritten, and less its Python, where a requirement is a string the
  program uses rather than one a reader copies out.
- **A backlog row records the one tree that spells it two ways** (issue
  #524): `btclib-secp256k1` writes its own name with an underscore in
  requirements its `README.md` and `RELEASING.md` give a reader, and the
  row is a strict expected failure until those lines move.
- **Section 3 says a requirement naming the distribution takes the
  canonical spelling too** (closes #335), beside the bullet saying
  `[project].name` does.

### Section 12 states the sdist property, and the mechanism is the tree's

- **The release rule was written as the step a publisher runs: it named
  the normalization script and required every publisher to carry it**
  (issue #140): what the standard states is now the property — a
  published sdist reproduces from the tag it was released from, its
  released bytes being the output of the pipeline the repository
  declares — with the steps between the tag and the archive named in
  that repository's own `RELEASING.md`, the reason beside each, so
  replacing one of them is a change to that file rather than to the
  standard.
- **The compiled wheel was exempted from the property without the reason
  the exemption needs** (issue #140): the index attests every file the
  publish job uploads, so `btclib-secp256k1`'s wheels carry an
  attestation the property is not stated of, and a verifier who rebuilds
  one and gets other bytes has nothing telling them whether the
  difference is a defect. Both alternatives are written down as
  rejected: saying nothing about the wheels, and pinning the image, the
  compiler and the linker so that they reproduce too, which is declined
  on cost and filed as btclib-org/btclib-secp256k1#439.
- **The sentence saying that nothing re-derives the property on a
  released tag pointed at the issue that states it** (issue #140): it
  names btclib-org/.github#523, the weekly sentinel split out to carry
  that half.

### Section 12 has the release pull request open the next cycle's sections

- **Between a release pull request landing and the next cycle opening,
  `main` carried no work-in-progress section in `CHANGELOG.md` or
  `RELEASE_NOTES.md`, so a branch open across that window had nowhere
  correct to put its entry** (closes #522): section 12 now has the
  release pull request retitle the section of both files to the version
  being tagged and open an empty work-in-progress section above them,
  which leaves the topmost `##` heading of either file a
  work-in-progress heading at every commit of the default branch.
- **The merge freeze is written down beside it as the rejected
  alternative**: `bitcoin-core-rpc`, `btclib-node` and
  `btclib-secp256k1` each write the step "in a pull request of its own
  and before anything else lands", which is a rule about how a
  person sequences merges on the day several branches are in flight,
  where opening the section in the release pull request leaves no window
  to sequence around. Bringing each publishing tree's `RELEASING.md` to
  the standard is #528.
- **The version bump does not travel with the retitle**: the tag is
  checked to say what `pyproject.toml` declares, so a pull request that
  released and bumped to the next generic version at once would cut its
  tag on a tree declaring a version that tag does not name. The
  objection that the release would then publish the new empty section as
  its notes does not hold — `awk '$0 ~ "^## " tag "( |$)"'` in each
  publishing tree's `release.yml` lifts the tag's own section.

### The one backlog row is gone, its exemption having expired by being fixed

- **`tests/__init__.py`'s `BACKLOG` is empty again** (issue #524):
  `btclib-secp256k1` spelled its own name with an underscore in three
  requirements a reader copies, the row excused the cell that measures
  it, and the row is what forced the expiry to be noticed. That tree
  hyphenated all three in `d82416c` and the strict expected failure then
  reported the success as a failure —
  `XPASS(strict) btclib-org/.github#524` — which is the mechanism
  working rather than a regression: a cell that starts passing under a
  strict row turns green into red here until somebody deletes the row.
- **The docstring's second paragraph said the opposite of the design**
  (issue #524): *Empty is where this is meant to arrive rather than a
  state it keeps* predicates both halves of *empty*, so it read as
  saying that empty is not a state the backlog holds — where the
  paragraph's whole point is that empty is the state it returns to. It
  now says *where this returns rather than where it always is*, which is
  the contrast the sentence was reaching for. The tuple emptying is what
  made the sentence worth reading closely.

### A releasing tree's `homepage` is its own documentation site

- **Which trees provide documentation, and whether documenting commits a
  tree to releasing, were unstated** (issue #533): section 2 now says
  that a tree releasing a Python package provides documentation and that
  the converse does not follow. A release carries a URL no later pull
  request can correct, and building `docs/source/` says nothing about
  publishing, so a tree that keeps that directory and subscribes no
  service to it is complete rather than short of a release.
- **Section 3 sends a releasing tree's two `homepage` surfaces to that
  site** (issue #533): `[project.urls] homepage`, which an index serves,
  and the repository's `.homepage`, which is the *About* link on its
  page. The read for each sits beside the rule, half the pair being a
  setting no file in the tree holds. A project's home is what documents
  it and not a project page, a sibling's or its own. The condition is
  the rule's, not the section's: section 3 binds tier 2 as well, and a
  tree that releases nothing publishes no URL that outlives a
  correction, so it is asked nothing here whatever it declares.
- **The alternative is written down as rejected** (issue #533): where the
  two surfaces disagree, moving the setting to whatever `pyproject.toml`
  declares is the cheaper edit, and it settles the disagreement by
  consecrating it — a tree whose declared home is another project's page
  keeps it.
- **`documentation` stays, naming that same URL** (issue #533): an index
  page then shows two links to one page, which is what it costs, against
  a field indexes and tools read for documentation specifically.
- **Section 16's new-repository checklist sets the `homepage` beside the
  topics** (issue #533), the two settings a `pyproject.toml` field
  decides.

### Section 11 admits `(issue #N)` in a landed subject

- **A pull request that advances an issue it does not close names it
  `(issue #N)`, on whichever of the title and the commit subject lands**
  (closes #529): the token was reserved for a `CHANGELOG.md` entry, and
  the reason section 11 gives for parentheses at all — the number
  reaching `git log` and staying reachable from a checkout with no forge
  in front of it — holds unchanged for a branch answering half an issue,
  which the reservation left with no number to reach.
- **One token holds one meaning wherever the standard writes it** (closes
  #529): *cites an issue the change does not close*, in a changelog entry
  and in a subject alike, where the reservation made it a meaning in one
  file and a prohibition in another.
- **The rejected alternative is beside the rule** (closes #529):
  reserving the token for `CHANGELOG.md` alone keeps parentheses on a
  subject always meaning a close, and costs the number that a branch
  answering half an issue would otherwise leave in `git log`.
- **What closes is unchanged** (closes #529): the description closes and
  never the title, `closingIssuesReferences` is the read that says what
  it closed, and a pull request that neither closes nor advances an issue
  carries no parentheses.
- **`CONTRIBUTING.md`'s copy of the two spellings says the same thing**
  (closes #529), the shared half naming `(issue #N)` as the citation of
  an issue the change advances rather than as a changelog's alone.

### Section 10's `os-ubuntu` and `os-windows` entries name `btclib-node`

- **`btclib-node`'s `origin/main` carries `os-ubuntu.yml` and
  `os-windows.yml` and both badges, and *Which trees carry which
  sentinel*'s two entries named neither** (closes #527):
  btclib-org/btclib-node#599 landed both on the decisions
  btclib-org/btclib-node#528 and btclib-org/btclib-node#430 recorded,
  so the tree carried what no entry gave it — the finding section 10
  names beside the record, read from the same side as #492.
- **Each entry gains `btclib-node` where the repository table orders
  it**, after `btclib-benchmarks`, matching the `os-macos` entry beside
  them that already carries it there.

### The lint gate runs actionlint and zizmor over the workflows

- **`.pre-commit-config.yaml` adds `actionlint-py` and `zizmor-pre-commit`,
  both at the revisions `btclib` already pins** (closes #503): section
  4's workflows bullet asks every tree's lint gate for both hooks at zero
  findings, and this repository's own gate ran neither. `uvx pre-commit
  run --all-files` passes both hooks against this repository's own
  workflows, with no finding from either to fix.

### `.github/dependabot.yml`'s header names what it pins without counting it

- **The header states what Dependabot moves and what pre-commit.ci moves
  instead, and drops the "two of the three" opening** (closes #438): the
  `typos` hook's `additional_dependencies` pin was a fourth thing the
  count left out, and section 9's *Measure, don't assert* forbids a
  stated total that nothing checks. The comment still names every pin
  and what moves it, with no arithmetic for a future pin to fall outside
  of.

### `links.yml` checks a link's fragment, so a renamed heading goes red

- **`lychee` checks a fragment only when asked, and the workflow did not
  ask** (closes #506): a heading rename that changes `README.md`'s anchor
  left `REPOSITORY.md`'s reference definitions pointing at the old one
  with nothing red anywhere, GitHub serving the page and dropping the
  fragment rather than 404ing on it.
- **The `lychee-action` step now passes `--include-fragments`**: proved
  first against a copy of the tree with one heading renamed, red only
  with the flag and green without it on the same input; run again on the
  tree as it stands, where it found no broken anchor to fix. When it goes
  red is this workflow's own cadence and unchanged here: weekly, on
  demand, and on a pull request only when `links.yml` itself moves -- so a
  rename that lands elsewhere is caught by the next Saturday's run rather
  than by the pull request that made it.
- **The flag also reaches a remote URL's fragment, which is not this
  tree's to keep resolving**: measured online against every `#fragment`
  this tree currently links to, on `github.com` and `docs.github.com`,
  and none turned red — a fragment check reads the page the plain link
  check already fetched, so it asks no third party a question it was not
  already asking.

### The `bbt` and `bitcoin-core-rpc` entries say what is there

- **`profile/README.md`'s `bbt` entry named slides among what the
  repository holds; `bbt` carries no slide file at any extension, and
  its own `README.md` sends a reader to the course page instead**
  (closes #501): the entry drops the word, the course page staying
  linked in the `btclib` paragraph above.
- **The `bitcoin-core-rpc` entry called the package one source file; the
  client is a package of modules**, its own `CHANGELOG.md` recording the
  split into a package (btclib-org/bitcoin-core-rpc#292). The entry now
  says what the tree holds rather than what it held before the split.
- **The same entry offered vendoring as a supported way to use it, and
  that stopped being true in the same landing** (closes #544): `grep -in
  vendor` answers nothing in `bitcoin-core-rpc`'s `README.md`,
  `CONTRIBUTING.md`, `CLAUDE.md` or `SECURITY.md`, and its changelog says
  of the split that "vendoring a single file is no longer what the shape
  is for". What survived is the standard-library-only constraint, which
  is what the sentence now gives a reader a reason for.

### Section 11 says what a `REPOSITORY.md` covers, and the suite asks it

- **The file covers the settings the standard asks about** (issue #551):
  the ones section 16's checklist sets on a new repository and the ones
  a section of `README.md` states a rule for, together with whatever a
  call quoted for one of those answers alongside it, and it says what
  falls outside that scope. What section 11 rejects is the copy saying
  `this file is the whole of them`, a claim no command checks: which
  fields of the repository document are settings rather than URLs,
  counts and derived state is a reading.
- **`tests/scope_test.py` asks every repository whether its copy makes
  the rejected claim**, reading the claim out of section 11 rather than
  carrying one of its own, and folding the whitespace of both sides: the
  sentence wraps at the margin in copies a line-based `grep` then
  answers `0` for. A copy still making it is a strict expected failure
  keyed on the issue, so its row is deleted by the branch that narrows
  its wording.

### Section 3 says who `[project].authors` names

- **Nothing said who `authors` names, and `btclib-node`'s own published
  sdist disagreed with itself over it**: `LICENSE`, `AUTHORS.md` and
  every source header named the collective while `Author-email` named an
  individual (btclib-org/btclib-node#598) — three mechanisms the
  standard already fixes against a field it said nothing about
  (closes #534).
- **`authors` now names what the MIT notice names, in every file that
  declares a `[project]` table, whether or not that file builds
  anything**: `bbt` and `.github` are declaring trees that build
  nothing, so the alternative — scoping the rule to a file that names a
  build backend, the way `license-files` is scoped — was weighed and
  declined, for the reason section 3 now gives beside the rule.
- **`tests/pyproject_test.py` asks it of every declaring tree, derived
  from `COPYRIGHT` and not transcribed**: the name is `COPYRIGHT`'s
  first line, read by a new helper beside the one
  `tests/copyright_test.py` already carries for `notice-rgx`, and the
  address is asked only of the declaring trees agreeing among
  themselves — no literal names it, `COPYRIGHT` carrying none.
- **A tree that declares a name and no address fails rather than
  dropping out of the comparison, and a comparison with nothing in it
  fails too**: a suite that skips what it cannot read answers the same
  green whether the trees agree or none of them says anything, and the
  second is the state the check exists to refuse.

### Section 2 gives the organization site its row

- **`btclib-org.github.io` is a repository of the organization and
  section 2's table gave it no row** (issue #553): the suite asks the
  forge which repositories there are rather than reading the table, so
  `tiers_test.py::test_section_2_gives_every_repository_a_row` failed on
  the tree the table left out. The row is tier 3, the tree holding no
  `pyproject.toml`, which is where the measurement of a tier stops.
- **The vehicle for the organization site is a repository of its own,
  with this one rejected** (issue #530): the paragraph beside the table
  says which tree serves the site and cites the decision, so a reader
  meets the row as the site's rather than as a name GitHub reserves.

### Three trees have landed the scope port and leave the backlog row

- **`bbt`, `bitcoin-core-rpc` and `btclib-secp256k1` no longer claim
  their `REPOSITORY.md` is the whole of what is set outside the tree**
  (issue #551): each landed the port, so
  `test_the_settings_file_does_not_claim_to_be_the_whole_of_them` passes
  for all three, and the row being `xfail(strict=True)` turns each pass
  into a failure until the name comes out. The exemption expires the
  moment the fix lands, which is the mechanism working rather than the
  suite complaining — `btclib`, `btclib-node` and `portanode` still owe
  the port and stay.

### A value's role, the free-threading classifier, two documentation properties

- **A value the standard owns is cited where an entry uses it and named
  where the entry decides it** (closes #485): section 9 draws the rule
  on the value's role rather than on its presence, so an entry recording
  a `cron:` moved onto section 10's calendar points at that section,
  while an entry deciding a calendar row states the instant it chose.
  Ownership tells the two apart: the calendar is this repository's, so a
  weekday and an hour beside a citation of section 10 is a decision here
  and a copy in any other tree. The rejected alternative is a flat
  refusal to restate an owned value, which would forbid the entries
  deciding a row from stating the row. A copy already landed stays, the
  next entry being the remedy append-only leaves.
- **A `Free Threading` classifier is declared where the merge gate
  exercises the free-threaded build** (closes #563): a gate refuses the
  landing that breaks that build, where a sweep runs beside a landing
  and blocks nothing, so section 3 keys the classifier on the gate
  rather than refusing it on a sweep's strength. Section 3's claim that
  section 7's closing rule makes the convention a test rather than a
  hope holds of the conventions beside it and not of this one:
  `interpreters_test.py` compares a classifier that names one version
  against the floor, the classifiers and the matrix, and `Free Threading`
  names no version, so it sits outside that comparison exactly as the
  `Implementation` classifier does. Section 3 now says what would
  enforce it, the biconditional that gates `Implementation`, with the
  gate's own matrix as its second side.
- **Building documentation and being served by Read the Docs are two
  properties** (issue #338): section 2's membership list welded them,
  and a tree that builds `docs/` and subscribes no service to it is
  complete by that section's own *The documentation*, so under one
  property its absent Read the Docs badge reads as a badge it owes. The
  fixed order is unchanged, Read the Docs staying immediately after
  `docs`, so no tree's badge row moves. What the split gives up is
  *published documentation* read off the `docs` badge alone.

### What a tree gates, the environments it declares, and where badges are read

- **A tree gates the code it holds against the failure that code has**
  (issue #301): section 8 opens with that rule, so the coverage floor is
  what a package that installs is measured by rather than the whole of
  what the section says — course material is measured by whether it
  still runs on the dependencies pinned today, and a suite whose subject
  is outside its own tree is itself the gate. The title stays
  `Coverage at 100%`: this tree's own `REPOSITORY.md` reaches the
  section by that anchor and `links.yml` passes `--include-fragments`,
  so a retitle is red here.
- **A repository declares `pypi` and `testpypi` where it publishes and
  no environment besides** (closes #575): section 11 gives the endpoint
  that finds anything else, and names `github-pages` as GitHub's own,
  created by enabling Pages — so it is outside the rule and outside
  `REPOSITORY.md`, which would otherwise read back a value nobody here
  can set. The alternatives rejected are saying nothing, which after the
  scope port has each copy's silence assert that whatever is there is
  fine, and recording whatever a repository holds, which legitimises a
  stray environment by writing it down.
- **`deps-oldest` is `deps-latest`'s mirror, on Thursday at `03`**
  (issue #323): `uv lock --resolution lowest-direct` on the oldest
  interpreter alone, which verifies the claim a floor makes to whoever
  installs — `requires-python` and the dependency specifiers, in the one
  cell that holds both. The row is owed by the trees that build a
  distribution, and section 10 has the row land before the workflows do,
  so `test_every_row_of_the_calendar_names_something_that_exists` is red
  until the first tree schedules it. Verifying at release time instead
  is the rejected alternative: it reaches only the trees that publish,
  and it puts the red at the moment a release is cut.
- **Which trees owe the OpenSSF Best Practices badge is section 10's
  `scorecard` entry** (issue #350): `CII-Best-Practices` is the check
  that reads the questionnaire, so the trees the sentinel runs in are
  the trees to register, and registering one that runs no Scorecard is
  attestation work nothing reads. Section 2's badge bullet is keyed on
  that entry rather than on holding the registration, and section 10
  names btclib-org/.github#350 as what carries the registrations
  outstanding. What it costs is a second home per tree for facts this
  file already states, so a change to any of them owes a pass over the
  questionnaires.
- **The `test` badge is keyed on the workflow rather than on holding a
  suite** (issue #500): a tree that runs its suite inside another
  workflow carries no `test` badge, and what goes red when the suite
  falls is the badge of the workflow that ran it — this repository being
  that tree, its suite running inside `alignment.yml`. Splitting the
  property as *builds documentation* and *served by Read the Docs* are
  split is the rejected alternative: there the two badges answer for a
  build and a subscription, where here they would be one workflow's
  status under two names.
- **`.readthedocs.yaml` is in every tree that builds `docs/`, so the
  tree cannot be read for the *served by Read the Docs* property**:
  section 2 says the membership is read from each tree's own
  `REPOSITORY.md`, a subscription being a setting outside the tree
  rather than a membership the organization decides, and
  `btclib-benchmarks` is where that absence reads as a decision.

### Section 2 drops `--keep-going` and says what `exclude_patterns` names

- **Section 16's checklist no longer asks for `sphinx-build
  --keep-going`, and section 2 says why it is not passed** (issue #347):
  in the sphinx `uv.lock` resolves the flag is declared with
  `help=argparse.SUPPRESS` and the application records it as unused, so
  it is missing from `--help` while the parser still accepts it. An
  unrecognized argument is refused where this one builds, so a run that
  passes it reads exactly like a run that does not.
- **`-W` on its own reports a warning raised while reading and one
  raised while writing from the same run, then fails at the end of it**
  (issue #347), which is what the flag's name asks for. Keeping it with
  a comment naming what it buys is recorded as the rejected alternative,
  there being nothing for that comment to say; each tree's own
  `docs.yml`, `CONTRIBUTING.md` and `.readthedocs.yaml` still pass it,
  which is the rest of that issue.
- **`exclude_patterns` is a rule rather than `sphinx-quickstart`
  residue** (issue #418): it names what the tree writes under
  `docs/source/` and is empty where nothing does. Sphinx reads a file as
  a document only where its name ends in one of `source_suffix`'s
  suffixes with something left over to be the document's name, so
  `Thumbs.db` and `.DS_Store` are not candidates under the `.md` and
  `.rst` these trees declare; `_build` is live only for a build
  directory written inside the source directory, and these trees build
  beside `docs/source/` rather than under it.

### Section 1's `dev` row says which groups `dev` has to reach

- **The row read `every group above`, and *above* names this table's own
  rows rather than what a tree declares** (closes #498): two trees read
  it as the groups a developer runs by hand and each left out one they
  declare — `btclib-node`'s `fuzz` (btclib-org/btclib-node#646) and
  `btclib-secp256k1`'s `check` and `mutation`
  (btclib-org/btclib-secp256k1#451), both since reached from their own
  `dev`. The row now names the tree's declarations, and the paragraph
  below the table adds that they are counted transitively, so a
  `harness` reached through `test` is not read as absent.
- **The alternative weighed and declined has the row mean every group a
  developer runs by hand**, which is what the two trees read into it: it
  saves an install, and it costs a second rule — about which groups
  count — applied by each tree to itself. The one case that made it
  attractive is already answered two paragraphs above, where an engine
  publishing no source archive for the developer's platform carries the
  marker naming its own.

### Three lines of prose agree with their mechanism

- **Section 15's uv ceiling is read with the markers `read_or_mark`
  gives** (closes #440): the line piped `gh api` into a `grep -oE`, so a
  call that failed and a `Dockerfile` whose image line stopped matching
  both left stdout blank and both exited 1. The read prints `ceiling=`
  with the value, `absent` or `unreadable`, and the prose beside it says
  which is asked again and which is `dependabot-core` moving what the
  block rests on. The alternative, a second argument to `read_or_mark`
  naming another repository, is declined beside it.
- **`CLAUDE.md` names a worktree at `origin/main` as the baseline for a
  red that may not be the branch's** (closes #442): a `git archive`
  snapshot has no `.git`, and `tests/__init__.py`'s `tracked` runs
  `git ls-files` in the tree under test, so the snapshot is red where
  `origin/main` is not.
- **Section 3's `license-files` bullet no longer spells the collective's
  name** (closes #557): the literal was a copy no command compared, where
  `COPYRIGHT` is the file the suite derives the name from. The sentence
  names the collective by reference; the alternative makes `README.md` a
  source `tests/` reads, and the `authors` bullet beside it has why the
  trees, and not this file, are the authority.

### Two verbatim files say what the standard says, and the queue points home

- **`.gitattributes` states the union price as section 9 does** (issue
  #423): the driver is a checkout's and the forge does not apply it, so
  a pull request whose changelog or release notes overlap its base is
  reported `CONFLICTING` however cleanly the pair merges locally, and a
  rebase on a checkout is what clears it. Every other tree is owed the
  same file, so `tests/verbatim_test.py`'s `EXPECTED_DRIFT` names the
  path against that issue until the copies agree.
- **`.markdownlint.jsonc` points at section 14 for who carries it**
  (issue #316), in place of naming the trees: an enumeration is a count,
  and the one it replaces named a part of the trees carrying the file.
  `EXPECTED_DRIFT` names the path against that issue on the same
  ground.
- **`CONTRIBUTING.md`'s *The landing queue* points at `REPOSITORY.md`'s
  *Plan-gated settings* for the ceiling's figure** (issue #412), which
  section 10 names as its one home per tree; the sentence stays
  unnumbered. The path's `EXPECTED_DRIFT` entry already names
  btclib-org/.github#281, one entry excusing the whole of a path's
  drift, so the port carries this with the rest.

### Section 14 decides `.gitignore` per repository

- **What a tree ignores is what its own build and tools write**
  (issue #39): a package that compiles an extension ignores the object
  files and the shared library it links, a tree whose `dist` job writes
  a bill of materials ignores the directory it lands in, and a tree that
  installs nothing has no build output to name. Section 14 classified
  the file neither way while section 16's first checklist had a new
  repository copy it; that checklist now has `.python-version` and
  `.gitignore` written for the tree rather than copied, both being
  decided per repository.
- **The rejected alternative is a verbatim `.gitignore` owed by every
  repository**, holding the union of what any tree writes: it would be a
  bullet `tests/verbatim_test.py` compares, and it would grow with every
  repository added while telling a reader of one tree nothing about
  which of its entries that tree needs.
- **The header sentence a `check_vendored_vectors.py` copy owes names
  the siblings of that name** (issue #446), the singular it carried
  having presumed exactly one other copy.

### `dev` reaches every group here, and the uv floor sits at the ceiling

- **`pyproject.toml` declared `test` and `lint` and no `dev`** (closes
  #552): section 1's row makes `dev` every group the tree declares and
  the default of `uv sync`, and section 2 measures this tree's own row
  the way it measures the others. `dev` now includes both groups, so
  one sync installs what any command here runs.
- **The `--no-default-groups` call sites keep the flag**, `alignment.yml`'s
  pytest step and the mypy hook: each installs the groups it names,
  unmoved by what `dev` includes, and the hook's command is the one
  section 4 spells out. The alternative weighed and declined drops the
  flag now that `dev` covers the same groups: it saves a word, and makes
  each environment follow `dev` wherever it goes next.
- **`CLAUDE.md` said a bare `uv run pytest` exits 0 with everything
  skipped, and in a worktree with no `.venv` it failed to spawn pytest**
  (closes #545): nothing installed the `test` group. With `dev` as uv's
  default the run syncs, collects and skips, and the bullet now says so,
  `BTCLIB_INTEGRATION=1` being what a measuring run still needs.
- **`[tool.uv] required-version` rises to the ceiling Dependabot's
  bundled uv sets** (issue #448), `0.12.5` by section 15's command at
  the writing; the sibling floors the issue names are their own trees'.

### A reused gate declines to aggregate, on an input its caller passes

- **A gate `release.yml` reuses through `workflow_call` skips its
  aggregate, on a boolean `workflow_call` input the calling job passes**
  (issue #474): section 10 named the constraint and left the mechanism
  open, and the mechanism is an input because nothing else in a called
  run says it is one — `github.event_name` is the caller's event, which
  the `changes` job of the workflow `btclib-org/btclib`'s dispatched run
  `32458459305` called printed as `workflow_dispatch`, and
  `github.workflow` is the caller's name. What gates the release in that
  run is the caller's own `needs:` on the calling job, which the
  publishing jobs already name: `bitcoin-core-rpc`'s run `33236701141`
  is a release whose called platform workflows had failing cells and
  whose every publishing job reports `skipped`.
- **Running the aggregate anyway is the alternative refused first**
  (issue #474): the listing it would read is the caller's, and the
  caller's publishing jobs are unfinished exactly because they wait on
  the aggregate, so the one unfinished row the shape requires can never
  be the aggregate itself. Reading `needs.*.result` where the listing is
  not the workflow's own is refused for the reason section 10 already
  gives, btclib-org/btclib#1001.
- **What runs the mechanism is the first port and not this entry**
  (issue #474): the tree that proves it is one whose `release.yml` calls
  a `test.yml` carrying an aggregate, `bitcoin-core-rpc`, and the two
  observations are `test: every job passed` reported on that tree's own
  pull request and skipped in a release run.

### A workflow that cancels nothing omits `closed`, and lychee checks anchors

- **The `closed` type is there for the cancellation, and a workflow
  whose group sets `cancel-in-progress: false` cancels nothing**
  (closes #513): section 10 now says such a workflow omits the type and
  says beside its trigger that it does, which is how
  `bitcoin-core-rpc`'s and `btclib-node`'s `pypi-install.yml` read it.
  The alternative weighed and declined keeps the list flat and leaves
  the job's `github.event.action != 'closed'` to absorb the event: a run
  scheduled for every close in order to decline its own work, with the
  reason the type is inert stated nowhere the trigger block shows.
- **`--include-fragments` is every `links.yml`'s and not this
  repository's alone** (issue #583): the anchors a renamed heading here
  breaks are cited in the trees that link to it, so the run that would
  notice is theirs, and `tests/links_test.py` now asks each tree's
  lychee step for the flag. The alternative weighed and declined has a
  tree check the anchors of its own headings only, which cannot see who
  links into them. A tree that does not pass the flag yet carries a
  backlog row against the issue, so its cell is a strict expected
  failure until the port lands.

### Section 11 draws the perimeter a `REPOSITORY.md` records

- **A copy records a setting a behaviour of the standard rests on, not
  only one a section states a rule for** (issue #566): `allow_auto_merge`
  is inside by that limb, *Merge method*'s landing being auto-merge
  pressing the only enabled button, and section 16's checklist turns it
  on with the squash-only setting it already names. The rejected
  alternative leaves the setting to each repository as a convenience, and
  what it costs is a section describing a landing path the tree no longer
  offers with no command anywhere to catch it.
- **`has_wiki` and `has_projects` are outside it, and a copy neither
  reads them back nor explains an answer to them** (issue #550): the
  standard states no rule about either and says so beside the perimeter,
  which is the one place a copy has to read to know. The rejected
  alternative records each with a sentence saying no rule is stated, so
  that a reader sees the answer and is told it is nobody's divergence;
  what it costs is a file growing with GitHub's API rather than with the
  standard, in a wording each copy invents for itself.
- **`has_issues` is inside** (issue #550): `CONTRIBUTING.md` sends an
  issue about one repository alone to that repository's own tracker and
  section 16's checklist gives every repository an `ISSUE_TEMPLATE/`, so
  a behaviour the standard describes rests on the setting.
- **A copy reads `.visibility` back, and records nothing for `.fork`**
  (issue #584): the sentinel's run rests on the repository being public,
  which is the limb above, where nothing sets `.fork` — a repository
  arrives as one or it does not. The rejected alternative keeps both
  halves of section 10's bar out of every copy on the ground that the bar
  is section 10's to state, and what it costs is the flip: the sentinel's
  row and its badge stand while the run stops producing a score, and the
  file a reader restores the repository from says nothing.
- **A copy does not claim that nothing it records has another form in the
  tree** (issue #571): the topics are section 3's `keywords`, a releasing
  tree's `.homepage` is the `[project.urls]` field of that name, and a
  Pages custom domain has the root `CNAME` carrying the same value, so in
  a tree holding one of those the record is a second copy read back for
  comparison. The rejected alternative is the blanket clause,
  one sentence shorter and refuted in such a tree's own file two sections
  further down.
- **A copy carries all three limbs of the scope sentence in the
  standard's own words** (issue #582): `README.md` written into the
  second names a sibling's own file, and a bare `it` there reaches for
  section 16's checklist. The rejected alternative leaves the wording to
  each copy, and what it costs is a reading per tree of a claim they are
  all making once.
- **This repository's own `REPOSITORY.md` takes the same answers**: it
  already reads `allow_auto_merge` and `.visibility` back and now states
  the first, drops the wiki and the projects board along with the
  comparison against the siblings, and takes the scope sentence's
  wording. The reason recorded beside `.visibility` is this repository's
  own — the community health files it supplies are shown while it is
  public — the sentinel section 10's bar is about not being one it
  carries.

### Section 11's Read the Docs connection is the App, not a webhook

- **What connects a repository to Read the Docs is the organization-wide
  `read-the-docs-community` GitHub App at `repository_selection: all`**
  (issue #564): `gh api orgs/btclib-org/installations` names it, and
  `gh api repos/btclib-org/<repo>/hooks --jq length` answers `0` in
  every repository of the organization, so what a `REPOSITORY.md`
  records is the installation and an empty hook list rather than a
  webhook. A hook found on a repository is stale and is deleted rather
  than repaired; btclib-org/bitcoin-core-rpc#291 records one that was.
- **The per-repository webhook is the rejected alternative, and the
  secret is why**: Read the Docs issues it on the project's own
  integration page and GitHub returns it masked, so nothing read back
  from the repository says whether a hook still carries the right one.
  The status code the section named for a hand-added hook goes with the
  rule it belonged to, rather than becoming the ground a rule stands on:
  no command here re-derives it.
- **`latest`, `stable` and the tag automation rule are read back from
  the project's public API** (issue #564), which answers without a
  token: `latest` comes back as a branch and `stable` as a tag whose
  `ref` is the highest release tag, beside the tags the rule has
  activated. The rule itself the API does not expose —
  `automation-rules/` answers 404 where an endpoint needing a token
  answers 401 — so the rule is recorded through its result.

### Section 10 calendars the rebuild and homepage sentinels

- **A tree that publishes an attestation has a row that re-derives it**
  (issue #523): `sdist-rebuild` takes Sunday 03, at the head of the
  security rows the calendar ends with, and its entry names `btclib`,
  `btclib-secp256k1` and `bitcoin-core-rpc`. What it compares against is
  the digests the published attestation carries rather than the ones the
  index serves, and the compiled wheel stays outside the property
  section 12 states. Section 10 has the row land here first, so
  `test_every_row_of_the_calendar_names_something_that_exists` names it
  until the first of the three schedules the workflow.
- **The page github.com/btclib-org serves is generated from a file in
  this tree, and the sentinel that watches for drift between them has a
  row and a minute** (issue #558) (issue #553): `homepage` takes
  Saturday 03, and `btclib-org.github.io` the minute after `bbt`'s,
  which is `links`'s minute in that tree too — a sentinel its entry
  gives it and it does not carry, btclib-org/btclib-org.github.io#1.
  The `repository_dispatch` that would send the exact signal wants a
  credential with write access to that tree, which nothing here holds,
  and asking the question from this suite instead answers red on `main`
  here for a drift another repository owns. Until the site schedules the
  workflow, `test_every_row_of_the_calendar_names_something_that_exists`
  names `homepage` beside `sdist-rebuild`.
- **`pypi-install`'s entry names `btclib-node`** (issue #85): that tree
  schedules the workflow on the row's day and hour and on its own
  minute, which section 10 reads as the entry's gap and not the tree's.
  What that issue stays open for is `os-windows`, whose entry names
  `btclib-node` where that tree carries no windows workflow.

### Section 12 says what a release run's `needs:` and its post-publish check are

- **A job named in `needs:` that is not a gate is opted back in by the
  dependent's own `always()`, and the widening does not propagate**
  (issue #484): each dependent states it for itself, with the explicit
  `needs.<job>.result == 'success'` beside it, because a bare `needs:`
  reads back through the listed job's own chain. The audit lands beside
  it: a release run is read job by job for `skipped` rather than for
  red, a skipped job carrying no step and leaving a release that never
  finished reading as one that did. `always()` on the non-gating job
  itself and dropping it from `needs:` are the rejected alternatives,
  the first changing nothing a dependent reads and the second costing
  the ordering the listing buys. The publishers whose guards do not
  carry the shape yet are that issue's other half.
- **The post-publish check is a job of the release run calling the
  reusable install workflow, and never a step appended to a publish
  job** (closes #488): a publish job's runner carries what its image
  ships and nothing the tree chose, so an appended step provisions its
  own toolchain or fails on the missing `uv` at `127` or on an
  interpreter `requires-python` does not admit, and placement decides
  whether the failure is legible — a failing job is red beside a publish
  job that stayed green, where a failing step turns the publish job
  itself red and takes the attestation and the GitHub release down as
  skips with it. Inlining the check because the
  index has nothing to read before a first release is the rejected
  alternative: the release's own call runs after its upload and waits
  for the version its tag names, so what has nothing to read is the
  schedule.

### The suite asks whether a releasing tree's homepage is its documentation

- **A releasing tree's `.homepage`, its `[project.urls] homepage` and its
  `[project.urls] documentation` are read against each other** (closes
  #535): section 3 sends both surfaces that carry the name to the
  documentation the tree provides and has `documentation` name that
  same URL, and no gate in the tree the rule binds compares them.
  `tests/homepage_test.py` asks each tier-1 tree that the three are one
  string, the way `topics_test.py` asks `keywords` and `.topics`, and
  `CLAUDE.md`'s list of the files that ask the API names it.
  Compared as written rather than with the trailing slash normalized:
  the rule is that the surfaces agree, and a slash one carries and
  another lacks is that disagreement. Which URL it is — the tree's own
  site rather than a sibling's, or on which host — is not asked,
  section 3 naming no host and no shape for the site.

### Section 7 keys the property layer, and section 10 loses an example

- **A tree owes section 7's property layer because bytes an adversary
  chose reach its parser, not because section 10's record gives it the
  fuzzer** (issue #426): the two cost differently — a property layer is
  code in the suite that runs with everything else, where a fuzzer is a
  scheduled runner with a harness and a corpus — so keying the cheap one
  on membership in the expensive one lets a tree obtain the first only
  by being given the second. Keying it on the record is the rejected
  alternative.
- **`btclib-secp256k1` has the property and no entry, and the reason
  stands beside the absence** (issue #342): whether a target there may
  reach the vendored C library at all — which would be fuzzing
  upstream's work rather than these bindings — decides what the sentinel
  would be run for, and that is undecided, so an entry taken now
  schedules a weekly run against a target nobody has agreed is this
  project's to write. The membership record is untouched: giving `fuzz`
  a fourth tree is a decision to take on its own evidence rather than
  one to arrive at by making two sentences agree.
- **Section 10 states what a sentinel's own work costs a pull request
  rather than instancing it** (closes #471): what a pull request charges
  is the wait, and a sentinel's length is what makes its work worth
  anything, so a trigger firing `fuzz` on a pull request charges the
  whole of a sentinel's run for a verdict no merge waits on. The
  rejected alternative is a replacement example: `fuzz.yml` runs on the
  calendar and on a dispatch in both trees the record names, so an
  example of a sentinel charging a pull request for its own work would
  come out of history, which section 9 keeps in two files of its own.

### Section 3 reaches a tree that ships nothing, and every written name

- **`keywords` turns on the `[project]` table and not on the index**
  (closes #465): a tree that uploads nothing declares the list all the
  same, so that the topics github.com shows have something in the tree
  to be read against, and `tests/topics_test.py` selects on that table
  where it selected on `[build-system]`. The rejected alternative keys
  the rule on publishing, which is how the topics of a tree with no
  upload came to answer to no list at all. This `pyproject.toml`
  declares its own topics as keywords, and section 16's checklist keys
  the absence it already described on there being no `pyproject.toml`
  rather than on a file that declares no `keywords`.
- **A distribution name written for somebody to copy out is spelled
  canonically wherever it is written** (issue #581), not only in a
  requirement: a flag's value, an install target, a deployment
  environment's `url:`, the message on a release tag. Position is all
  `tests/names_test.py` can read and these sites have none, so the rule
  is stated and named a reader's catch rather than left to be answered a
  line at a time per tree.
- **A PyPI page is linked as `https://pypi.org/project/<name>/`**, the
  form `https://pypi.org/p/<name>` redirects to: the site serves either
  spelling of the name and redirects neither, so the spelling shown is
  the writer's and the rule above reaches it. The short form is the
  rejected alternative, saving the characters and costing the redirect.
- **This tree declines of section 3 the metadata only an index reads,
  and no more** (closes #602): its `CLAUDE.md` and section 2's row said
  section 3 describes a file this `pyproject.toml` is not, which read as
  the whole of it while `authors` and now `keywords` bind the tree; each
  now names the half declined.

### Section 11 separates the two closing parsers, and what a force-push costs

- **Two parsers read a closing keyword, and a newline is where they
  part** (closes #519): the one answering `closingIssuesReferences`
  reads the pull request's description and requires a physical line, and
  the one that closes on a push reads the message that landed and
  crosses the newline. Section 11 states them apart, each with the
  measurement it rests on and the day it was read.
- **A `closed` event's commit id says which of the two closed the
  issue** (closes #519): it carries a sha where the push did and null
  where the description did, so `825c74e2` closing an issue its message
  reaches only across a newline is the measurement of the second parser,
  and a null beside it is uninformative rather than contrary. The pair
  of controls is a description with no keyword whose issue closed on its
  commit, and a commit with no keyword whose issue closed on its
  description.
- **The keyword scan over a branch's own commit text keeps `\s`**
  (closes #519): the parser that text will meet is the one that reads a
  landed message, so a separator narrowed to a space or a tab would miss
  the shape the scan exists to catch. The rule to write one keyword per
  line stays, being what the description parser requires and what a wrap
  at eighty columns silently breaks.
- **What a force-push costs is the review attached to the sha it
  replaces, and section 11 gives the read that answers whether there is
  one** (closes #570): `pulls/<n>/reviews` is the endpoint that answers,
  and `pulls/<n>/comments` is the one that reads as an absence, counting
  inline comments alone. An amend and a correction as its own commit
  both move the head, so what the rule reaches is the push rather than
  what carries the correction; a reading taken before a pull request
  exists is attached to nothing and cannot be orphaned.
- **The rejected alternative opens the pull request only once a reading
  has cleared the sha**, so that no push ever follows a review. It needs
  no read at all, and what it costs is being a rule about what a session
  remembers per branch — where a bot submits against the head within
  seconds of a pull request opening, leaving no window to work inside.

### The suite asks a `REPOSITORY.md` for the section on what it passes over

- **A copy says what falls outside its scope under
  `## What this file passes over`, and `tests/scope_test.py` asks every
  repository for that heading** (issue #565): whether the section is
  there is what a string finds, where what it says about the perimeter
  stays a reading. Section 11 names the heading as the form the second
  obligation takes, with the reader's check as the rejected alternative
  beside it, and the test reads the heading off that sentence as its
  sibling reads the claim. `portanode`'s copy has no such section and is
  a strict expected failure keyed on the issue, its row expiring with
  the port that gives the copy the section.

### This tree's head carries the row section 2 owes it, and its suite declares itself

- **`README.md` opens with the badge row section 2 reads off this tree**
  (closes #357): pre-commit.ci and `lint`, then `links` and `alignment`
  in section 10's calendar order, in the form every other repository's
  head takes. No `test` badge, the suite running inside `alignment.yml`
  and section 2 giving a suite's badge to the workflow that runs it; no
  licence badge, that being tier 1's; no Scorecard badge, the record not
  naming this tree. Whether a workflow badge carries `?branch=main` is
  #579's question, and it reaches this row as it reaches every other.
- **`tests/README.md` declares which of section 7's conventions this
  suite tests, and what of that section has no subject here** (closes
  #357): none of the bullets, this tree shipping no package for one to
  walk, and one sentence beside each rule of the section the suite takes
  or declines, with the reason.
- **`pytest-randomly` joins the `test` group** (issue #428), section 7's
  default taken rather than declined: what it guards here is the session
  fixtures every test reads after one fetch, where a test that mutated
  what it read would pass or fail by order and nothing else in the suite
  would notice. The rejected alternative declares the decline in
  `tests/README.md` on the ground that the fetched answers are read once
  and never changed -- which nothing enforces, and which the shuffle is
  what would notice the day it stops being true.

### Section 2 puts `?branch=main` on every workflow-status badge

- **A workflow-status badge answers for `main` or answers `no status`**
  (issue #579): unqualified, it falls back to another branch's run where
  `main` has none, so section 2 qualifies every one of them and names
  the `workflow_dispatch` run from `main` that gives a new sentinel's
  badge its first reading. The rejected alternatives, a qualifier keyed
  on whether the workflow has run on `main` and the unqualified badge,
  are beside the rule; the badge rows are ported behind it.

### The ported verbatim files agree everywhere, so their drift entries go

- **`EXPECTED_DRIFT` no longer names `.gitattributes`** (closes #423):
  every tree's header states the union price as section 9 does, the
  forge not applying the driver, and the copies agree byte for byte.
- **`EXPECTED_DRIFT` no longer names `.markdownlint.jsonc`** (closes
  #316): every tree's header points at section 14 for who carries the
  file, in place of naming trees, and the copies agree byte for byte.
- **`EXPECTED_DRIFT` no longer names `CONTRIBUTING.md`** (closes #281):
  every tree carries the shared half as this one has it, and
  `tests/verbatim_test.py`'s own cut of it hashes the same in each.

### The suite reads section 10's sentinel record in both directions

- **Section 10's *Which trees carry which sentinel* is read as data and
  asked of every tree** (closes #494): `tests/grid_test.py` reads each
  entry's trees off the record — `subjects` in `tests/__init__.py`
  reading a bullet whole where it wraps, which the entries do — and
  compares them with the workflows a checkout holds, one cell per
  repository, short and unnamed alike; a second test holds the record to
  one entry per calendar row, in the order section 10 says. What a tree
  is short of is that tree's, as section 10 says beside the record, so
  the red cells are `BACKLOG` rows keyed on the issues carrying them:
  `deps-oldest` (issue #323), `sdist-rebuild` (issue #523), the site's
  `links` (issue #597), and `os-windows` in `btclib-node` (issue #618),
  where the tree dropped the sentinel for a gate cell and the record has
  not said whether it follows. The badge half stays a reader's catch:
  the badge is section 2's, and no fixture holds a tree's `README.md`.

### This tree's badge row carries the qualifier section 2 asks of it

- **Every workflow-status badge at the head of `README.md` carries
  `?branch=main`** (issue #579): `lint`, `links` and `alignment` answer
  for `main` or answer `no status`, where the unqualified badge falls
  back to another branch's run when `main` has none.

### The record answers for the ceiling, the credential and CodeQL

- **`REPOSITORY.md` has a *Plan-gated settings* section, which is where
  section 10 puts the ceiling's figure** (issue #569, issue #412):
  `gh api orgs/btclib-org --jq .plan.name` and GitHub's limits table sit
  beside the number, `CONTRIBUTING.md`'s *The landing queue* already
  points at that heading by name, and the plan-gated secret-scanning
  pair is pointed at the section that reads it back rather than
  restated. The plan and the credential are the file's first
  organization-scoped calls, so the command at the head that enumerates
  its endpoints matches `orgs/btclib-org` as well as this repository's
  own paths, and prints them all.
- **The credential `claude-review.yml` spends leaves *A facility nobody
  reached for*** (closes #572): the empty Actions and Dependabot
  repository stores record section 11's decision that the token is an
  organization secret at `visibility=all`, so they take a bullet of
  their own with the organization's two stores read back beside them,
  and the facilities nobody has reached for keep the general one.
  `bbt`'s copy, the other the issue names, already reads that way.
- **The *Topics* section reads the tree's own `keywords` back against
  the setting** (closes #593, issue #571): section 3 turns the rule on
  the `[project]` table rather than on whether anything is published,
  `topics_test.py`'s `keyworded` selects on that table, and this
  `pyproject.toml` declares the names — so the section carries the
  `diff` that holds the two lists together, the head of the file says
  the topics have a second form in the tree as the ported copies do, and
  what the record is still the only home of is that the names are set on
  the repository at all.
- **The CodeQL bullet states what section 10's record decides** (closes
  #590): the `codeql` entry does not name this tree, and a tree an entry
  does not name is asked nothing by that row, so the analysis is off by
  a decision taken once for the organization — in place of a reason that
  narrated the file and a question left open with nothing behind it.

### The backlog row for the fragment flag is gone

- **`tests/__init__.py`'s `BACKLOG` row for
  `test_lychee_checks_a_link_into_a_heading` is deleted rather than
  narrowed** (issue #583): every tree the row named passes
  `--include-fragments` to lychee, so each cell passes without the
  strict expected failure, which turns that success into a failure here.
  The issue is closed by the last of those ports, in
  `btclib-org/portanode`, so this landing cites it without closing it.

### The open section is a list of entries, and a number in one has a place

- **A `###` names one entry, never a theme several entries share**
  (issue #567). Section 9 asked for an entry "in the group it belongs
  to" and for the end of the open section, and a section carrying themes
  has those in two different places; grouping by theme is written down
  as the rejected alternative, on the ground that nothing in the file
  says what the themes are and that the append point the placement and
  rebase bullets are read against becomes the theme's rather than the
  section's. An open section already carrying theme headings takes its
  next entry after them, with nothing above it moving. Section 2's row
  for the file names the entry rather than the group. Bringing the trees
  to the rule is btclib-org/.github#586, so this cites the issue without
  closing it.
- **A citation goes in the bullet making the claim, not on the heading
  above it** (issue #547). An entry's bullets cite separately, so a
  citation on the heading answers for the entry while the bullets under
  it name issues of their own and nothing says how the two sets relate.
  The heading citation is the rejected alternative, and what it buys is
  a section whose numbers a reader collects from the headings alone. The
  tree that cites on the heading is the other half of
  btclib-org/.github#586, so this cites the issue without closing it.
- **An issue an entry names without acting on it is written into the
  sentence, not into the parentheses** (closes #538). The parentheses
  say what the entry did about an issue and there is nothing to say of
  one it did nothing about, so a reference put there bare is the shape
  *The qualifier does not stand in for the keyword* already refuses; in
  the sentence it sheds the keyword and not the qualifier, and says what
  the issue is to the entry.
- **Section 15 audits none of it, and the reason for that is the landed
  entries rather than the two shapes being indistinguishable**: a
  pointer inside parentheses with nothing before the number is what
  *Nothing already written is rewritten* keeps, so a pattern over the
  file matches one of those as readily as a citation.

### The .gitattributes comment names the driver's sides and one anchor

- **`union` keeps `ours` first and then `theirs`, and the base's own
  lines stay where they are** (issue #520): the comment said the added
  lines were kept "in the order base-then-ours", which names no order
  between the two sides — the fact the position of an entry turns on. A
  scratch repository with `CHANGELOG.md merge=union` and two branches
  each writing an entry answers with the `ours` line above the `theirs`
  line, in a merge and in a rebase alike and wherever the base's own
  line sits. Which side is which is the operation's: the branch checked
  out when merging, the upstream when rebasing.
- **The premise is an entry arriving at one anchor, not a bullet
  appended to one of a few groups** (issue #643): a `###` names one
  entry, so the open section is the list of its entries and there are no
  groups to append to, and what the driver resolves is two branches
  writing an entry at the one place section 9 sends it.
- **`tests/verbatim_test.py`'s `EXPECTED_DRIFT` names `.gitattributes`
  against btclib-org/.github#646** (issue #520, issue #643): a comment
  section 14 owes verbatim makes this tree's edit a drift the comparison
  reports, and an entry there excuses that path while every other
  verbatim file stays compared — where a `BACKLOG` row would excuse the
  whole test. Carrying the comment to the repositories that lag is what
  closes both issues, which is why this landing cites them without
  closing either.

### The organization page names the site tree and links btclib's documentation

- **The word *btclib* opening `profile/README.md` links the library's
  published documentation** (closes #637): `btclib.org` is served by
  `btclib-org.github.io`, whose `index.md` is that file's bytes under
  front matter, so on that surface the word linked the page carrying it.
  The library's repository was the other candidate, and the file already
  links it under *The libraries*; the documentation is what a reader
  following that word in that sentence is after, and it is right
  whichever repository holds the domain.
- **`btclib-org.github.io` is an entry in the same file's *Around them*,
  with the domain written and not linked** (closes #559): against naming
  it, a reader of the organization's page is looking for what to use and
  a repository whose whole content is that page is not it — but the list
  carries `.github` on those same terms, so what decides an entry there
  is not whether a reader would use the repository. What the entry says
  is where the page is served, which nothing else on the page says once
  the link above is the library's documentation; linking the domain
  would put back on the served copy the self-reference the bullet above
  removes.
- **The `.github` entry writes the standard's scope instead of pointing
  at it** (closes #559): it said the standard is what *the repositories
  above* are built and kept to, which enumerated the list while that
  entry was last and stopped doing so the moment one sat below it —
  section 2 giving that repository a row, and saying its row is measured
  like the others. Naming the scope leaves the sentence true wherever
  the entry sits.

### Section 7 states how a fuzzer stands to the property layer, once

- **Section 7's *Property tests* carries the statement and section 10's
  `fuzz` bullet points at it rather than restating it** (closes #594):
  the two copies claimed different things — section 7's that a fuzzer
  presupposes the property layer, section 10's that neither substitutes
  for the other — which is section 9's *One fact in one place* failing
  rather than being risked. The surviving sentence carries both claims,
  since keeping only one resolves the duplication by losing half a fact.
- **Section 7 is the copy that stays, because the distinction is what
  the property layer is specified against** (closes #594): a reader of
  the `fuzz` bullet arrives asking whether the tree owes the sentinel,
  which that bullet's keying property answers, where a reader of section
  7 arrives deciding whether to write the layer at all. The `fuzz` bullet
  keeps its own examples — a length prefix larger than the buffer, a
  truncated multibyte sequence, a varint that overflows, a recursion
  depth that exhausts the stack — those being about the sentinel rather
  than about the ordering of the two layers.
- **The pointer names *Property tests* and speaks for that layer alone**
  (closes #594): section 10's sentence took in section 7's convention
  tests beside the property tests, a widening the surviving sentence
  does not make.

### The suite asserts its own convention declaration, and tests the changelog

- **`tests/README.md`'s declaration of which of section 7's conventions
  this repository tests is asserted by a test in the same suite**
  (closes #615): `conventions_test.py` asks that the declaration's table
  and its *Not tested here* line account for each of section 7's
  conventions once, that a module named there is a file, and that the
  file holds a test.
- **Section 7's conventions are read off `README.md` rather than
  transcribed into the suite** (closes #615): a sibling suite holds a
  copy because its standard is in another repository, and here the
  standard and the declaration are the same commit, so a copy would be
  the one that goes stale — a bullet added to section 7 would land with
  nothing to notice that neither half of the declaration accounts for
  it.
- **`subjects` takes the pattern by which a list names its subjects**
  (closes #615): section 7 emphasises its bullet leads where the lists
  this suite already reads quote theirs as code, so the shape is the
  caller's to pass and there is one reader of a bulleted list rather
  than two.
- **`CHANGELOG.md` states no count of itself, and a test says so**
  (closes #616): `changelog_test.py` reads a history file for a count of
  its own entries or bullets, and tells that from a count of something
  else by whether a possessive in front of the count gives what it
  counts an owner. Section 11 says a count is not reachable by a
  pattern, which is a rule about counts of anything; a count of the
  file's own parts is narrower and is reachable. `merge=union` is why
  the rule wants a test rather than a reading: the same paragraph edited
  on two branches merges without a conflict.

### Section 7 points at section 10's `fuzz` entry for the keying property

- **Section 7's *Property tests* names the property its layer is keyed
  on and no longer glosses it** (closes #650): the gloss was a second
  statement of the criterion, and the two were already apart in their
  words — section 7's *its parser* against section 10's *the parser* —
  where section 9's *One fact in one place* asks for one statement and a
  pointer. Section 10's is the statement that keeps the discrimination,
  that the property is not merely input the tree does not produce.
- **What tells a restatement from a pointer's own apposition is whether
  the clause carries the criterion**: section 1's `fuzz` group and
  section 14's *Decided per repository* each name what section 10 keys
  the sentinel on without stating it, so neither can come to disagree
  with the entry; section 7's gloss carried the criterion itself.
- **The pointer names the `fuzz` entry rather than the section**, the
  gloss having been what spared the reader the jump: what is left has to
  land where the property is stated rather than at a section's head.

### The alignment suite bounds a hung test, and `addopts` says what it waits on

- **The suite carries section 7's per-test timeout** (closes #617): a
  hang is the one failure a suite cannot report on itself, and without a
  bound what a reader gets is `alignment.yml` cancelled at its
  `timeout-minutes`, naming the job and no test. `pyproject.toml`'s
  comment at `timeout` is the measurement the number was taken from, and
  `tests/README.md` declares the bullet as taken rather than as the gap.
- **The bound covers a test's setup as well as its body**: the clone of
  every repository and the repository document of each are session
  fixtures', which pytest-timeout charges to whichever test triggered
  them, so `timeout_func_only` would time the bodies alone and leave a
  stalled clone unbounded. `session_timeout` is no answer either, being
  read between tests rather than able to interrupt one.
- **`addopts`' reason for declining `-n auto` no longer rests on every
  test here waiting on the network** (closes #652): a module whose
  subject is this tree waits on nothing outside its own process, and
  what carries the conclusion is that a test asking about another
  repository waits on the fetching, which is where the wall clock goes.

### A paste of section 15's metadata block reaches nothing that writes

- **The block's lines chain with `&&`** (closes #619): the first holds
  bare placeholders, which the shell reads as redirections and refuses
  — a redirection error and not a parse error, so unchained the lines
  below it run, and the last of them runs `uv build --sdist`, which
  writes into a `dist/` of the directory it runs in. Chained, a paste
  made before the placeholders are filled runs no command at all, in
  `zsh`, `bash` and `sh` alike. What the block asks is unchanged: the
  repository's topics against `pyproject.toml`'s `keywords`, and
  `twine check` on the sdist's metadata.
- **Section 9 carries the rule** (closes #619), governing every document
  here rather than section 15 alone, and it turns on what follows a
  placeholder on its own line. A word after it leaves `>` a target, so
  the line fails at run time and a trailing `&&` short-circuits the rest
  — a guard resting on the reader's directory rather than on the line,
  since a file of the placeholder's own name sitting there lets the `<`
  succeed and the line run. A placeholder ending the line leaves `>`
  nothing to open, and an interactive shell discards that line together
  with its `&&` and reads the next as a fresh command, so the chain
  never forms and a write below it runs. The chain guards the first
  case, and the second is left the fence of its own for the writing line
  that the first rejects.

### `REPOSITORY.md`'s Topics section states the `[project]`-table trigger once

- **`## Topics` states the `[project]`-table trigger once, in the
  sentence naming `topics_test.py`'s `keyworded` and this repository's
  own inclusion** (closes #671): the section stated the same fact
  twice — that the rule turns on the `[project]` table and not on
  whether anything is published — section 9's *One fact in one place*
  failing rather than being risked.
- **The surviving sentence is the one tying the trigger to the test
  that enforces it on this repository, not the one paraphrasing
  section 3 on its own** (closes #671): the sibling copies are written
  from this section rather than the other way round, so what is kept
  here is what they carry, and the sentence kept already pairs the test
  with this repository, where the other restated section 3's own wording
  with nothing tying it to either.

### A paste of the blocks named here reaches nothing that writes

- **The placeholder ends the command in section 2's tier loop and in
  section 11's blocks that read `closingIssuesReferences`** (closes #621):
  a word after it leaves the `>` closing the placeholder a target, so a
  paste made from a directory holding a file of the placeholder's own
  name creates one named for that word. Ending the line, the placeholder
  leaves `>` nothing to open and the command does not parse, in `zsh`,
  `bash` and `sh` alike; what `zsh` then reads as fresh commands is the
  tier loop's body, which only reads. `gh` takes the positional after
  its flags and the GraphQL variables after the query, so what the
  blocks ask is unchanged. What a paste of another block still writes
  here is measured the same way and left where it is filed (issue #675).
- **`git worktree remove --force "$WT"` stands in a block of its own**
  (closes #664): the line above it ends in a placeholder, and a shell
  that discards that line as a parse error reads the next as a fresh
  command, so a paste of one block removes whatever `$WT` a session that
  has already been through it still holds. Its own block is the one
  CLAUDE.md's reader pastes deliberately.

### `.gitattributes`'s copies agree, so `EXPECTED_DRIFT` no longer names it

- **`tests/verbatim_test.py`'s `EXPECTED_DRIFT` no longer names
  `.gitattributes`** (closes #646, closes #520, closes #643): every
  repository section 14 owes the file to now carries
  `btclib-org/.github`'s comment verbatim, naming the union driver's
  `ours`-then-`theirs` order and the anchor rather than the order the
  driver does not produce or the changelog groups section 9 no longer
  has. The table itself stays, `REVIEWING.md`'s entry standing against
  issue #353.

### Section 10 says when a platform row leaves a tree's entry

- **The `os-windows` entry no longer names `btclib-node`** (closes #618,
  closes btclib-org/btclib-node#735): that tree gates a `windows-latest`
  cell on the suite passing instead of carrying the sentinel beside it,
  so the record follows the tree and the tree owes no workflow back.
- **The ground is a gate cell asking the whole of what that tree's
  sentinel asked** (closes #618): the converse *What runs weekly does
  not also gate* denies is a hole in a matrix, and a sentinel covered
  whole leaves none. The cell earns its place before a review on the
  parallel-job trade section 10 already states for an interpreter axis,
  and gates on the suite passing rather than on the coverage floor.
  Where that trade does not hold, or where the cell is narrower than
  the sentinel's matrix, the sentinel keeps its whole matrix on the
  calendar and the entry keeps the tree -- a hole is what the paragraph
  above refuses, so a partial cell buys nothing.
- **`tests/__init__.py`'s `BACKLOG` row keyed on the issue goes**
  (closes #618): a row says the answer is written down and waiting, and
  this entry is the answer.
- **Two more rows go with it, both excusing a cell that now passes.**
  A row is a strict expected failure precisely so that a tree catching
  up is reported rather than quietly excused, so a row outliving its
  cell turns the suite red from the other side. `btclib-node` leaves
  the `deps-oldest` row, having become the first tree to schedule that
  sentinel, which is btclib-org/btclib-node#739's own landing; the
  `links` row goes whole, the site carrying `links.yml` now
  (closes #656). Only the first of those two is forced by the entry
  above it: with the `os-windows` row gone, the `deps-oldest` row was
  the last thing excusing
  `test_a_tree_carries_the_sentinels_its_entries_give_it[btclib-node]`,
  and leaving it would have turned a passing cell red. The `links` row
  was already red on `main` on its own account and is fixed here
  because it was in front of us.

### Section 10's worked examples follow the trees they name

- **The interpreter-axis example reads `btclib-node`'s `test.yml` as it
  stands** (closes #666): `3.14t` runs in a `free-threaded` job of its
  own beside the `coverage` job at `3.14` rather than as a second cell
  of the `coverage` job, and `test-passed` does not name that job, so
  the paragraph no longer states that both cells are required by one
  aggregate. btclib-org/btclib-node#746 is what it points at for why
  the job reports rather than gates.
- **The criterion the example illustrates is untouched** (closes #666):
  what it weighs is the slot a cell occupies before a review, which the
  cell costs whether or not a merge waits for it, so whether the cell
  reports or gates does not move the axis onto the weekly calendar.
- **The `deps-oldest` bullet says what btclib-org/.github#323 still
  carries** (closes #683): the trees of the entry still short of the
  workflow, `btclib-node` carrying `deps-oldest.yml` with a `schedule:`
  and no longer being one of them.

### Section 14 places `tests/conventions_test.py`

- **The module is per repository by subject, and outside the compared
  list** (closes #674): each copy reads the declaration its own tree
  keeps, its rows and the `tests/` root it resolves a declared module
  against are that tree's, and `btclib-node` keeps its copy at
  `tests/unit/conventions_test.py`. What the copies hold in common is a
  job — read the declaration section 7 asks for and assert every
  convention it names has a module holding a test for it — so each owes
  a header sentence about this module: what it reads, and which of its
  departures are decided. A defect in the parsing that job needs
  otherwise sits in every copy with nothing red anywhere.
- **The rejected alternative is a bullet in *The same file in every
  repository*** (closes #674): no two copies are byte-equal and that
  comparison is by path, so the bullet would report the copies as drift
  on the day it landed and could not reach `btclib-node`'s at all.

### The `docs/` read and `README.md`'s boundary and commit blocks write nothing

- **`CLAUDE.md`'s `docs/` read and `README.md`'s `uv_build` boundary
  check each move their placeholder into an assignment of its own**
  (issue #675): `-C` and `--with` put it ahead of the command that
  takes it, so it cannot sit last inside that command the way section
  2's tier loop puts `<org>`; the assignment stands in its own block
  instead, what section 9 already leaves for a placeholder that ends
  its line, and the read or the boundary check below it runs against
  whatever the assignment has already set.
- **`README.md`'s pinned-commit block moves `--jq` ahead of the
  endpoint it reads** (issue #675): `<rev>` then sits last the way
  section 2's tier loop already puts `<org>`.
- The fourth block the same sweep still finds sits inside the
  `merge=union` bullet, which #629 is open against and #661 owes a
  consolidation afterward; it is left there rather than edited by a
  second branch at once.

### Section 10 says what its own prose means

- **The `sdist-rebuild` bullet no longer counts the trees of its own
  entry** (closes #686): "the first of the three" stated a total,
  which section 9's *Measure, don't assert* forbids; "the first of
  them" bounds the same debt without one.
- **The interpreter-axis criterion's lead sentence names a second job
  as readily as a second matrix cell** (closes #692): no gate workflow
  in the organization runs its interpreter axis inside one job's own
  `strategy:`, so "the cells already gating the review" replaces "the
  ones already in the job", matching the wording the criterion's own
  failure clause already uses.

### The BACKLOG row keyed on ISS 551 narrows to its lagging tree

- **`tests/__init__.py`'s row for
  `test_the_settings_file_does_not_claim_to_be_the_whole_of_them` names
  `portanode` alone** (closes #693): neither `btclib`'s nor
  `btclib-node`'s `REPOSITORY.md` carries `this file is the whole of
  them` any longer, so the row's strict `xfail` was turning each tree's
  own passing cell into `XPASS(strict)`. `portanode` is still the one
  copy the claim is found in.

### `REPOSITORY.md` answers for the review switch and for `is_template`

- **The file reads both variable stores back for
  `vars.CLAUDE_REVIEW_ENABLED`, the switch `claude-review.yml` guards
  its jobs with** (issue #682): the repository's store because a
  variable set here would take precedence over one of the same name set
  on the organization, and the organization's for the empty name list
  section 11 reads as the off state — with a `total_count` beside it, a
  store that prints nothing at all when it answers needing one to show
  the call reached it. The repository's `actions/variables` zero records
  a decision now, so *A facility nobody reached for* no longer names
  Actions variables among the empty answers that record none.
- **`is_template` is named among the fields of the repository document
  the file passes over** (issue #691): it is in that document, in none
  of the `--jq` objects there, and `README.md` asks nothing of it, which
  is the class that block enumerates; a field of that class it does not
  name is silent in both places at once, and reads as one nobody looked
  at rather than as one weighed and left out.

### Section 9 holds a wrap to what `shellcheck` reads a comment line as

- **A sentence wrapped so that `shellcheck` is the first word of a
  comment line writes a directive rather than prose** (issue #689): the
  same sentence with the word pulled up onto the line above is green, so
  what fails is the wrapping and not the prose. Where the rest of the
  line does not parse as a directive, the file is `SC1072` and the gate
  is red; where it does — `# shellcheck disable=SC2086` arriving whole
  on its own line — the run exits 0 and an unquoted `echo $x` beside it
  goes unreported, which the same script with the word pulled up
  reports. Both outcomes reproduce through `actionlint` over a
  workflow's `run:` block, which is how the lint gate here reads a
  comment.
- **The rule is about the wrapping alone, because both outcomes are
  defects**: what the rest of the line parses as decides which of the two
  a wrapped sentence produces, and where it parses as a directive
  `shellcheck`'s ordinary scope decides whether the finding beside it
  goes quiet — file-wide where the line precedes every command, and
  otherwise over the command or compound it immediately precedes, so a
  statement standing between the two is the difference. A line that
  parses as no directive is red wherever it sits. Neither outcome is one
  to aim for, so there is no boundary the rule has to name.

### *Merge method*'s rule gains the instance that got past it

- **A wrapped commit subject lands truncated by the squash, and the
  usual read cannot see it** (closes #701): `git show -s --format=%s`
  joins a multi-line subject paragraph into one, so the read a coder
  and a reviewer both run shows the sentence they intended while the
  squash lands only the first physical line. *Merge method* already
  stated the rule and the `%B`-based read that sees it, and states it
  once still: what it gains is the worked instance it had none of,
  this repository's own `79fb1df`, whose remainder is on `main` as the
  body's first line with both closing citations in it.
- **The rule is not restated where a reader went looking for it**
  (closes #701). *What a pull request says it is* already pointed at
  *Merge method* for which of the title and the subject lands; the
  same sentence now says that rule also decides whether the citation
  survives the landing. A second statement of the mechanism was
  written first and dropped in review: section 9 has the second place
  point at the first, not repeat it.
- **Prose alone did not catch it: the rule is an ancestor of the
  instance it is cited against, not a reaction to it** (closes #701):
  `fc2412a` added *Merge method*'s paragraph, and `79fb1df` landed on a
  tree that already carried it, so a documented, correct, manual read
  is not what stopped the truncation from recurring. Whether an
  automated check belongs in this repository is left to a separate
  issue rather than decided here.

### A placeholder standing as a whole argument is unquoted

- **`REVIEWING.md`'s blocks for filing collateral quoted their
  placeholders, so a paste of them reached `gh` rather than failing**
  (closes #587): the quotes make `<` and `>` ordinary text, leaving a
  valid `gh issue create` whose title and body are the placeholders
  themselves and a `gh issue list` whose search term is one. Unquoted,
  the placeholder ends the line, `>` has no target, and the shell
  refuses the block and writes nothing — `zsh`, `bash` and `sh` alike.
- **Section 9 carries the rule** (closes #587), governing every document
  here rather than `REVIEWING.md` alone, and it says what tempts the
  quotes back: quoting is what an argument holding spaces otherwise asks
  for, so the absence wants a sentence beside it. Section 15's
  `git log -S <phrase>` comes under the rule.
- **The condition the shell's `<` succeeds under is stated once, in the
  bullet whose claim rests on it** (closes #661): a file of the
  placeholder's own name sitting in the reader's directory is what
  leaves a block's guard resting on the reader rather than on the line,
  and the rule above points at that bullet for what a bare placeholder
  fails with rather than stating the condition beside its own claim.
- **The rule stops at a placeholder standing as a whole argument**
  (closes #587): a placeholder inside a larger string is quoted for what
  sits beside it — `"repos/<org>/$r/contents/$1"` for the variable — and
  a quote another language needs is that language's, so a wider rule
  would make a violation of every one of them in the tree that states
  it. What that leaves is a command a paste still runs, and the rule
  claims no protection for it.

### Section 10 says which job an aggregate's `needs` may leave out

- **The opening sentence names what `needs` collects: every job whose own result
  is a claim about the pull request** (closes #685): a job built to conclude
  successfully whatever it finds -- a `continue-on-error` step reported rather
  than left to redden the run -- makes no such claim, and a paragraph beside
  the opening sentence states the ground and its self-terminating condition.
  `btclib-node`'s `free-threaded` job, already out of `test-passed`'s own
  `needs:` on exactly this ground, is the instance the paragraph cites.

### `scope_test.py`'s by-hand command asks the assertion's question

- **A claim wrapping onto an indented line is found by the assertion and
  missed by the command the failure names** (closes #620): the test folds
  every run of whitespace to one space, where translating newlines alone
  leaves the indent beside the space it writes, so a reader taking the
  command to the checkout reads that the finding is not there. `tr -s
  '[:space:]' ' '` squeezes the run instead, which is the fold the test
  makes.
- **The command counts occurrences rather than lines** (closes #620): a
  folded file is one line, so a count of lines answers the same for a
  copy carrying the claim twice as for one carrying it once. `grep -oF`
  asks for the claim as a string, which is what the assertion asks.
- **Restating the test's own regex in a `python3 -c` is the alternative
  declined** (closes #620): it is provably the same fold, and it is no
  longer a shell command a reader can eyeball, where two filters are
  checkable against the fold by running both against a copy that wraps.

### A failing `gh` call says what `gh` said, and the first fetch is bounded

- **A `gh api` that comes back non-zero names what the tool wrote to
  standard error** (closes #663): `CalledProcessError` carries the exit
  status alone into pytest's report, so a 404, a revoked token and a
  secondary rate limit arrive there as one sentence. `tests/__init__.py`
  raises `Refused` instead — a `CalledProcessError` still, so that
  `protection_test.py` goes on telling one refusal from another by
  `stderr` — whose message names the command as a line the reader can
  take to a terminal, the way `by_hand` names one.
- **The alternative declined is an assertion carrying `stderr`**
  (closes #663): the backlog's rows are strict expected failures keyed
  on `AssertionError`, so a refused call raised that way is reported as
  the finding the row already records, in a run that exits 0, whether
  the assertion came from a test's body or from a fixture that test
  asked for. Any other exception is the failure or the error it is.
- **The run's first fetch carries a bound of its own**
  (closes #667): `conftest.py` parametrizes the per-repository tests
  over the names the API answers with, before an item exists, and
  pytest-timeout installs its bound in `pytest_runtest_protocol` — so
  `pyproject.toml`'s `timeout` reaches every wait but that one, and an
  unbounded first fetch ends the run with `alignment.yml` cancelled at
  its `timeout-minutes`, naming the job and no test. `TIMEOUT` sits
  under the per-test bound, so a hang inside a test is reported as the
  command that hung and not as the test that was being asked, and far
  over what a call here takes, so that a slow answer is not turned into
  a finding about the organization.
- **One helper runs every command whose output this suite reads**:
  `git grep -n 'subprocess.run' tests/` answers with `output` and with
  `conftest.py`'s clone, which is not one of them — it captures
  nothing, so git's own stderr reaches the report already, and it runs
  inside an item, where the per-test bound covers it.

### The organization's default new-issue page is this tree's own

- **`.github/ISSUE_TEMPLATE/` holds `bug_report.yml`,
  `feature_request.yml`, `question.yml` and `config.yml`** (issue #632):
  section 2 gives `.github/` to every tier, section 16's checklist names
  the directory in it, and section 11 cites that checklist as why
  `has_issues` is a setting a copy records. GitHub serves an
  organization's `.github` templates to every public repository of it
  that keeps none of its own, so one directory is both this tracker's
  forms and the new-issue page of a repository that has not written its
  own.
- **The forms ask what is answerable in a tree whose subject they do not
  know** (issue #632): what happens, how to reproduce it, and against
  which release or commit. A question only one subject answers — which
  chain, which BIP, which script — is what a repository asks in a form it
  keeps itself, and is what a default served to several cannot ask.
- **Where an issue belongs is a link and not a second statement of the
  rule** (issue #632): `CONTRIBUTING.md`'s *The issue tracker* already
  says that what the standard decides, or what no single tree can answer,
  is filed in `btclib-org/.github`, and that file is the same in every
  repository these forms reach.
- **The security entry names the policy rather than an advisory form**
  (issue #632): a `contact_links` url is absolute, the schema admitting
  only `^https?://`, so an advisory form written here sends every
  reporter to one repository's Security tab, where `SECURITY.md` asks
  for the tab of the repository the defect is in.
- **Blank issues are off** (issue #632): discussions are not enabled
  here, so a question has a form of its own, and with that written there
  is nothing a blank box is the only home for.
- **`CLAUDE.md`'s list of the community health files inherited from here
  carries the directory** (issue #632), which `README.md`'s own bullet
  on them already classes with the rest: a session editing a form has to
  meet the sentence saying what it is changing for a reader of every
  repository that inherits it.

### Section 9 says where a placeholder goes, and what each guard rests on

- **A bare placeholder goes at the end of its command** (closes #673):
  there the `>` closing it has no target and the line is a parse error,
  so it writes nothing whatever the reader's directory holds, where a
  word after the placeholder gives `>` that word as a target and a
  directory holding a file of the placeholder's own name turns the line
  into a write. That instruction was written at the blocks obeying it,
  which is a convention a later editor undoes by tidying one block's
  arguments; the blocks now point at section 9 for the reason instead of
  at section 2's tier loop.
- **The fence of its own for a writing line rests on the reader taking
  the one fence** (closes #678): github.com gives each fence its own
  copy button, and a drag across the rendered passage is one paste that
  the fences do not interrupt. Section 9 states that condition beside
  the remedy, as it already stated the reader's directory beside the
  `&&` chain's.
- **What discriminates is the feed and the paste, not a script against a
  pty** (closes #672): `zsh` reading a block from stdin discards the
  parse error and carries on to the write at `rc=0`, where `-c` and a
  file abort, so a harness built on `cat block | zsh` reads as the
  aborting case and is the other one; and `zsh` takes a bracketed paste
  as a single buffer and abandons all of it, where `bash` and `sh`
  submit it a line at a time and reach the write with the markers
  present or absent.
- **The rejected shape keeps the bullet those three are against and adds
  one apiece**: that bullet carried where a placeholder goes and what
  the guards below it rest on at once, which is why the layout came to
  be written at the blocks, so it is split by subject rather than
  extended.
