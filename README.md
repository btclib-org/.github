# The btclib-org repository standard

<!-- The badges are what the reader decides with, one property of the
tree per badge, in the groups section 2 below fixes and in its order:
the gates first -- pre-commit.ci, then the lint workflow -- and the
sentinels after them in the order section 10's calendar schedules them,
the day and the hour each one owns being that section's and not
restated here. Which sentinels this tree carries is section 10's
record: `links` is every repository's and `alignment` is this tree's,
and the record gives it no other, so there is no Scorecard badge and
no `scorecard.yml` behind it. There is no `test` badge either, this
tree's suite running inside `alignment.yml` and section 2 giving a
suite's badge to the workflow that runs it; and nothing keyed on
publishing or on a documentation build, this tree doing neither. One
badge per line keeps a change to one line and every line inside MD013,
whose 80 columns bind only where a space follows them. -->
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/btclib-org/.github/main.svg)](https://results.pre-commit.ci/latest/github/btclib-org/.github/main)
[![lint workflow status](https://github.com/btclib-org/.github/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/btclib-org/.github/actions/workflows/lint.yml?query=branch%3Amain)
[![links workflow status](https://github.com/btclib-org/.github/actions/workflows/links.yml/badge.svg?branch=main)](https://github.com/btclib-org/.github/actions/workflows/links.yml?query=branch%3Amain)
[![alignment workflow status](https://github.com/btclib-org/.github/actions/workflows/alignment.yml/badge.svg?branch=main)](https://github.com/btclib-org/.github/actions/workflows/alignment.yml?query=branch%3Amain)

**This repository keeps the standards the btclib-org projects have in
common: it states them, and it is where they are kept true.** The
statement is this file. Keeping it true is the issue tracker beside it,
which is where a repository's drift from the standard is filed and
worked off — because a divergence between two repositories belongs to
neither of them, and an issue opened on one is an issue the other never
sees.

So the work has two directions and both land here. A repository that has
fallen behind the standard is an issue against the repository, tracked
here. A repository that has gone *ahead* of it — a practice worth having
everywhere, arrived at in one place — is an issue against this file, and
the standard changes.

**And not only drift: the ongoing maintenance that crosses repositories
is tracked here too**, whether or not the standard has anything to say
about it. A badge to remove from every README, an action that changed
its inputs, a tool that deprecated a flag four `pyproject.toml`s pass, a
convention worth adopting everywhere at once — each is one piece of work
that lands as one pull request per repository, and what it needs is a
single place to be planned from, watched, and closed once every one of
them has answered. That is the same argument as above, and it is what
makes this a project rather than a document.

What follows is that standard: what every repository in the organization
is configured to do, as far as its tier in section 2 binds it, and why.
It is written to be read twice: once when a repository is created, so
that the shape is right from the first commit, and once when an existing
one is normalized, so that the gap is a list rather than an impression.

The reference implementations are `btclib`, `btclib-secp256k1`,
`bitcoin-core-rpc` and `btclib-benchmarks`. Where they agree, this file
states the rule. Where they differ, it says which part of the difference
is a decision and which is only the age of the repository.

Nothing here is recoverable from a single tree: the branch rules, the
environments and the repository settings live on GitHub, and the tooling
decisions live in files whose reasoning is the comment above them. Both
halves are below.

## What this repository is

`btclib-org/.github`, which GitHub reads for two things and which this
file is the third of:

- **`profile/README.md`** is the organization's page,
  [github.com/btclib-org](https://github.com/btclib-org).
- **Default community health files** — a `CODE_OF_CONDUCT.md`,
  `SECURITY.md`, `SUPPORT.md`, `FUNDING.yml`, or issue and pull request
  templates placed here are shown for any *public* repository of the
  organization that has none of its own. The inheritance is display
  only: an inherited file is in no tree, so no hook reads it, no sdist
  carries it, and a repository that wants the file gated keeps its own.
  `CODE_OF_CONDUCT.md` is kept here and nowhere else: it points at the
  PSF code of conduct, which is one policy for the organization rather
  than anything a tree says about itself, so a copy per repository is a
  copy of a pointer. `SECURITY.md` is kept here *and* in each repository
  that publishes, the table below saying when and why, and section 15
  the command that answers which.
- **This file** is inherited by nothing and is the point: one statement
  of the standard, linked from each repository's `CONTRIBUTING.md`,
  rather than a copy per repository for the copies to drift apart in.
- **The issue tracker** is the maintenance. An alignment finding names
  the repositories it is about and the command that re-derives it, and
  stays open until every one of them answers — which is the thing an
  issue filed on a single repository cannot do, its checkboxes being
  invisible from the others.

Nothing here is released: this repository ships by being read, and
`CONTRIBUTING.md`'s *A version, and no release* is what the placeholder
version in `pyproject.toml` is for.

**A finding that spans repositories is filed here, and only here.** Not
here *as well*: the same divergence written up once per repository is
what this rule exists to stop. It costs twice — a defect acquires
several numbers and no owner, so closing one leaves the others open
against something that no longer exists; and the copies cannot see each
other, which is how the same defect was filed twice ninety minutes apart
by two passes over one file, neither noticing the other.

The shape is one issue naming the repositories it is about, with a
checkbox per repository and the command that re-derives the finding, and
it closes when the last box is ticked. A per-repository issue is for
work that is genuinely that repository's alone; where one is opened for
a repository's share of a cross-repository finding, it links to the
issue here rather than restating it, and closes when that repository's
pull request lands.

**A decision taken here that removes an artifact owes a sweep of every
tree for what asserts it.** A tag, a release page, a setting: what a
tree says about the thing is false from the moment the decision lands,
and that tree did not change to make it so, so no diff there is the
occasion to re-read the sentence. The landing that removes the artifact
is the one place where somebody has the fact in view as it stops being
true, which is what makes the sweep the deciding issue's rather than the
stale tree's.

The sweep goes in the deciding diff where what asserts the artifact is
in a tree that diff already touches, and otherwise in an issue filed
with the deciding one, in the shape above. The rejected alternative
leaves it to section 15's read-backs, which are run against the tree
that did not change — by hand in an audit, or by the suite on its
schedule — so they answer whenever that next comes round rather than at
the landing. Each of them answers for a section of this file too, so a
sentence about the artifact is compared with nothing unless a section
names it. No command checks that a decision did this, which puts it
among section 15's readings rather than its comparisons.

Branch rules, rulesets and repository settings are *not* inherited from
here either. On an organization plan without organization-wide rulesets
they are applied per repository, which section 15 is how to verify.

## How to use this file

- **A new repository** — work down the sections in order. Section 16's
  first checklist is the same list without the reasoning, for when the
  reasoning has already been read once.
- **An existing repository** — section 16's second checklist is ordered
  by what a gap costs, wherever dependency leaves that order free. Its
  opening paragraph is where that order is argued, and each step that
  waits on another says there what it waits for.
- **A rule with no reason beside it is not this file's rule.** Every
  setting below was decided against an alternative, and the alternative
  is what stops the next reader from undoing it.

## 1. Toolchain and environment

### uv is the only prerequisite

`uv` fetches interpreters, linters and packaging tools itself, so a
contributor installs one thing and CI installs nothing. The commands are
the environment with all groups, the suite gated at 100%, and the whole
lint gate:

```shell
uv sync
uv run pytest
uv run pre-commit run --all-files
```

Every documented command is a `uv run` command, and every workflow step
runs the same command verbatim. `CONTRIBUTING.md`'s last section carries
the commands a developer runs, so a workflow change that leaves one of
them behind makes that file wrong rather than merely stale. A workflow
whose command lives only in the workflow says so where it is written,
rather than being copied into prose that nothing re-runs.

**`--locked`, never `--frozen`.** `--locked` fails when `uv.lock` and
`pyproject.toml` disagree; `--frozen` takes the lock as it finds it and
runs a gate against an environment nobody declared.

### `.python-version` and `requires-python`

The two point at opposite ends on purpose:

- `.python-version` is the **newest** interpreter the matrix covers. It
  is what a bare `uv run` uses, so a local run measures what the
  coverage job measures.
- `requires-python` is the **oldest** supported. ruff infers its target
  from it; `[tool.mypy] python_version` restates it, because mypy
  otherwise targets whatever runs it and a typing construct missing from
  the floor becomes invisible.

`.python-version` takes a whole-line comment only: a trailing comment on
the version line makes uv ignore the file and fall back to a default
interpreter.

**What sets the two ends is what the repository is.** A library is
imported by code its authors never see and an application is run by its
own users, and the interpreters each of them covers follow from that.

**A library publishes and declares the classifier
`Topic :: Software Development :: Libraries :: Python Modules`. Every
other repository is an application.** The two halves are one question
asked of the two parties to an import: section 2's tier is whether an
index carries the distribution for somebody else's resolver to reach,
and the classifier is what the distribution on it says it is.
Publishing alone is the rejected proxy and `btclib-node` is what it
reads wrong: a full node is a program its users run, and publishing it
is how they install it. Rejected with it is a key of this
organization's own, which would declare a second time what PyPI already
has a field for and would be read by nothing a user of the package
sees, and a tier carrying the exception here rather than in the tree it
is about, which is a list to keep in step with repositories that move
without it.

The price is that a library declining the classifier takes the
application window and nothing goes red. No command here refuses that
and none can, the two being one shape on disk, so the rule above stays a
reading rather than a test.

A **library covers every interpreter still in support**: the floor is
the oldest Python that has not reached end of life, `.python-version` is
the newest released, and the classifiers name every version between them
while the platform sweeps run each. Neither end is a choice, and the
[Python release cycle](https://devguide.python.org/versions/) — whose
table carries the end-of-life date of every branch — is what moves both.
It moves them in the same month, one version reaching end of life as the
next is released, so a library's window changes on a date rather than on
a decision. The libraries name one window between them, since it is
python.org's window and not each tree's: a library whose floor is not
the others' is out of step with the cycle rather than with them, and
section 15's command is what reads it.

An **application takes the newest interpreter its dependencies allow**.
It is not there to be imported, so covering an older one buys
compatibility for nobody: `.python-version` is the newest version every
dependency publishes for, and `requires-python` is the oldest the tree
itself means to run on, which is that same version where it means to run on one
interpreter alone. The newest is also the one worth being on, and the
release cycle above carries both halves of why: only `main` accepts a
new feature, so an interpreter's own speed-ups arrive with a release and
never with a fix to a branch already out, and a branch reaches
`security` status years before its end of life and takes security fixes
alone from then on. Where a dependency holds `.python-version` below the
newest release, that file's comment names the dependency and the
condition for raising it — a ceiling with no reason beside it is one the
next reader cannot tell from a preference, and it outlives the
dependency that set it.

### Dependency groups

Groups rather than extras, because uv has no default extra: an extra
alone would leave `uv sync` resolving a project without it.

| group | what it holds |
| --- | --- |
| `harness` | the test runner and its plugins, nothing else |
| `test` | `harness` plus whatever the suite delegates to |
| `lint` | mypy, pre-commit, ruff |
| `bindings` | an optional native dependency that is also an extra |
| `build` | what builds a distribution, cibuildwheel included |
| `check` | what inspects a distribution before it is published |
| `docs` | sphinx and `furo` |
| `mutation` | the mutation runner |
| `fuzz` | the fuzzing engine |
| `dev` | every group the tree declares, and the default of `uv sync` |

The `harness`/`test` split is what lets a job ask for the suite *without*
the optional native dependency, since uv's `--no-group` suppresses a
group that was selected and not one another group includes. A project
with no such dependency keeps the two names or not as its own workflows
ask: the split is paid for by the tree whose `test.yml` asks for
`--group harness`.

`build` and `check` are two names because one tree holds both and they
mean different things there: `--only-group build` compiles wheels,
`--only-group check` reads them without compiling anything. A tree with
no build step of its own still names its inspection tools `check`, so
the command means the same thing everywhere.

`fuzz` is `mutation`'s shape: a scheduled workflow's group rather than a
gate's. A tree declares it where that workflow runs the fuzzer as a
`uv run` command, and not where the targets are compiled inside the
fuzzing service's own image, which has the engine installed already —
`btclib` hands its targets to ClusterFuzzLite and declares no such
group. Section 10 keys the sentinel on what a tree parses and leaves the
harness to the tree; the group follows that choice rather than making
it.

An engine that publishes wheels for the platform it fuzzes on and no
source archive is specified with the marker naming that platform.
`uv lock` resolves without one, so what a missing marker costs is a
developer's `uv sync` off that platform, refused over a group that
machine never runs.

`dev` reaches every group *the tree itself declares*, transitively
through `include-group`, rather than every row of this table: the table
names the groups, and each tree declares the subset it has. What the
rule buys is that one sync is enough to run anything the tree runs, so
a group left out of `dev` is found by a gate failing on a machine that
had already synced.

A group no developer runs by hand — a scheduled workflow's `mutation`,
say — is not an exception to it. What such an exception saves is an
install; what it costs is a second rule, about which groups count,
applied by each tree to itself. And the hazard it would be reached for,
a sync refused over a group that machine never runs, is the marker
paragraph's above, and answered there.

Where a package is both an extra and a group, the specifier is written
twice and a test refuses the day the two disagree.

### `uv.lock`

Committed, and the only thing that moves it is Dependabot's uv ecosystem
and the `uv-lock` hook. The dependency groups declare no versions: the
whole drift of ruff, mypy, pytest and sphinx lives in the lock file, so
one pull request a week carries all of it, pre-validated by the
`deps-latest` workflow.

`[tool.uv] required-version` names the oldest uv that may read the
lock. Every tree the root-files table above binds to `uv.lock` — tiers
1 and 2 — carries it. The floor is set at the ceiling rather than
below it: the newest uv that Dependabot's own bundled updater still
reads, since that updater runs `uv lock` with exactly the uv it ships
and refuses rather than upgrading itself, so a floor above the ceiling
would silently stop every lock update it attempts, security ones
included. Raising the floor as the ceiling moves is always safe: the
failure guarded against is an *older* uv rewriting the lock, and the
ceiling only rises. Section 15 carries the command that measures it.
`setup-uv` given no version input reads that key, so CI needs no
second pin.

## 2. The tree

### Which repositories, and how far

This file is written for a Python package that publishes, and the
organization holds repositories that are not one. How far it binds a
repository is that repository's **tier**, and a tier is measured rather
than declared, by two files:

- a repository **is Python** where it holds a `pyproject.toml`;
- it **publishes** where it holds `.github/workflows/release.yml`,
  which is section 12's machine.

The tiers nest: tier 2 owes what tier 3 owes and more, and tier 1 owes
what tier 2 owes and more.

- **Tier 3 — any repository, whatever it is written in.** Sections 9,
  11 and 14: the prose; the settings, together with what they name — a
  required check, which is section 4's gate over the file types the tree
  holds, and the review workflow whose verdict is the ack of record —
  and the files every repository carries the same. Of the root-files
  table below, the rows marked for it.
- **Tier 2 — a Python project that publishes nothing.** Everything but
  section 12 and the two workflows that exist for a release, `release`
  and `pypi-install`, the second reading what the first put on the
  index.
- **Tier 1 — a Python package that publishes.** The whole file.

A rule whose subject the tree does not hold asks nothing of it, at any
tier: section 14 says so of `.taplo.toml` and a tree with no `toml`, and
it is the same sentence for a section 11 ecosystem with no lock file to
read. What the tier adds to that sentence is the difference between a
rule with no subject here and a rule with a subject that is declined,
which is the difference an alignment finding has to state.

**A tier is a floor, not a ceiling.** Above it, a repository carries
what its own practice needs: `portanode` carries the `RELEASING.md`
that says how a release is cut by hand, which its tier does not ask
for. Below it, a repository short of what its tier binds is a gap,
filed here. A gap with the reason beside it, where a reader meets the
repository — its `CLAUDE.md` or its `REPOSITORY.md` — is a decision
rather than a gap; a sentence that declines a rule and gives no reason
is a gap with a sentence in front of it, this file's own *a rule with
no reason beside it* read from the other side.

| repository | tier |
| --- | --- |
| `btclib` | 1 |
| `btclib-secp256k1` | 1 |
| `bitcoin-core-rpc` | 1 |
| `btclib-node` | 1 |
| `btclib-benchmarks` | 2 |
| `.github` | 2 |
| `bbt` | 2 |
| `portanode` | 3 |
| `btclib-org.github.io` | 3 |

The table is a claim, and the loop below is what checks it, in either
direction — a row the loop contradicts is the finding, and so is a
repository the loop names and the table does not. A new repository is a
row here in the pull request that creates it, section 16's first step.

`<org>` sits last for the reason section 9 gives.

```shell
for r in $(gh repo list --json name --jq '.[].name' <org>); do
  t=3
  gh api "repos/<org>/$r/contents/pyproject.toml" --silent \
    2>/dev/null && t=2
  [ "$t" = 2 ] && gh api \
    "repos/<org>/$r/contents/.github/workflows/release.yml" --silent \
    2>/dev/null && t=1
  printf '%s\t%s\n' "$r" "$t"
done
```

`.github` is this repository, and its row is measured like the others:
a `pyproject.toml`, a suite, and no `release.yml`. What it declines of
tier 2 — there is no coverage here, and of section 3 the metadata only
an index reads — its `CLAUDE.md` says, with the reason.

`btclib-org.github.io` is the organization site, served by Pages from
the root of its `main`, and btclib-org/.github#530 is where that vehicle
was decided and this repository rejected as the alternative. Its row is
measured like the others too: no `pyproject.toml`, which is tier 3.

**A tier-2 repository carries neither `RELEASING.md` nor `RELEASE_NOTES.md`.**
What the first would say is that there is no release — which every such tree
states under its own `CONTRIBUTING.md`'s *A version, and no release* — and a
file whose content is its own absence is one sentence in `README.md`, not a
file: the file's being there tells every reader who has not opened it that
there is a procedure here, and `SECURITY.md`, which sends a reader to it for
what a release is in a given tree, sends them instead to a line the `README.md`
can hold. The second is what a user has to act on *at a release*, on top of the
changelog, so where no release is cut it has nothing to be on top of;
`CHANGELOG.md` stays, a change being noticed whether or not a version names it.
The alternative weighed was carrying both ready, on the ground that a tier-2
repository could release tomorrow. What that buys is a procedure nobody runs,
kept in step with section 12 by nobody; and the day a release arrives it
arrives with `release.yml`, which is the day the repository is tier 1 and the
two files come with it.

### Root files

Each is one fact in one place, and the last column is which tiers owe
the row. Where a row is not every tier's, the reason is beside whatever
decides the tier — `SECURITY.md`'s under the table, the two release
documents' in the paragraph above that keeps them out of a tier-2 tree,
and `pyproject.toml`'s and `uv.lock`'s in the measurement this section
opens with, a tree with no `pyproject.toml` being no Python project and
having nothing to lock:

| file | what it is | tiers |
| --- | --- | --- |
| `README.md` | what the repository is, to whoever arrives at it | 1, 2, 3 |
| `LICENSE` | MIT, referred to by SPDX from `pyproject.toml` | 1, 2, 3 |
| `COPYRIGHT` | the three-line notice every source file opens with | 1, 2, 3 |
| `AUTHORS.md` | a pointer to the contributor graph, not a list | 1, 2, 3 |
| `SECURITY.md` | reporting, supported versions, known limitations | 1 |
| `CONTRIBUTING.md` | how to work; its last section is this tree's | 1, 2, 3 |
| `REVIEWING.md` | the standard a review is written against | 1, 2, 3 |
| `REPOSITORY.md` | the settings that live outside the tree | 1, 2, 3 |
| `RELEASING.md` | how a release is cut, and how one is recovered | 1 |
| `CHANGELOG.md` | every user-visible change, one entry each | 1, 2, 3 |
| `RELEASE_NOTES.md` | what a user has to *act* on, on top of it | 1 |
| `CLAUDE.md` | what a session needs and no human document holds | 1, 2, 3 |
| `pyproject.toml` | the project and every tool's configuration | 1, 2 |
| `uv.lock` | the pinned resolution | 1, 2 |

**`SECURITY.md` is tier 1's row**, and what it turns on is that the
repository publishes. The sdist carries the file, so a reader who has
the archive and not github.com reads the policy from it, and a published
package's own provenance — what its distributions attest to, and which
of them is supported — is not something a file shared with every other
repository can state. Where nothing is published there is no archive,
and GitHub shows this repository's copy. What that costs is worth
knowing: an inherited policy cannot name the flaws that are that tree's,
or the project a report about it should go to instead, so a tree
with either to say says it in its `README.md` and its issue tracker.

**The private channel that row promises is a setting as well as a
file.** *Report a vulnerability* on a repository's Security tab does not
wait on somebody remembering to read a mailbox, where the address beside
it does. The file is tier 1's and the setting is every tier's, because
the policy sends a reporter to the Security tab of the repository the
defect is in, and that repository need not be one carrying a policy of
its own; where the form is off, the policy offers a route the repository
does not have.

**The address kept beside the form** is *security at btclib dot org*,
spelled out rather than written as a `mailto:` or with an `@`. Beside,
because an address needs neither an account nor a repository setting to
work; spelled out, because that is the form a harvester reading a public
file does not lift, and a reporter reads either. One address for the
organization rather than one per file, because whether a mailbox is
answered is not something a reporter can check: a report sent to one
that is not answered is the failure they never learn about. It names
the subject rather than a team, so who answers a report can change
without the policy changing.

**The badges at a `README.md`'s head are never curated.** A curated
list has no answer to *should this tree carry that badge*, so two trees
curate differently and neither of them is wrong, which is how one file
comes to open a different way in each tree. Where a property of the
repository decides a badge the answer is read off the tree, and where
none does the membership is written down — one place either way, and
neither of them the tree's own taste.

What that gives up is the head as a summary. A badge per sentinel means
the row grows with section 10's calendar rather than staying the handful
a reader takes in at once, so the tree running the most sentinels
carries the longest row and the tree running the fewest carries a row
all the same. That is the trade and it is deliberate: a
row long enough to be an audit is worth more here than a row short
enough to be decoration, because the rule below is what makes it an
audit. A tree that wants the shorter row drops a sentinel, its badge
going with it.

Which badge a tree carries, and what decides it:

- **every repository** — the `lint` workflow;
- **publishes** — from the index, the version, the downloads, the
  development status, the supported Python versions, `wheel` and
  `implementation`; and from the forge, `github/v/release` and the
  licence, derived from the repository's own `LICENSE` by
  `img.shields.io/github/license/<org>/<repo>`;
- **holds a `test` workflow** — its badge;
- **on pre-commit.ci** — its badge;
- **builds documentation** — the `docs` workflow;
- **served by Read the Docs** — the Read the Docs badge at
  `app.readthedocs.org`;
- **named by section 10's `scorecard` entry** — the OpenSSF Best
  Practices badge, `www.bestpractices.dev/projects/<id>/badge`;
- **a sentinel section 10's record names the tree in** — that
  sentinel's badge.

**The suite's badge is the `test` workflow's**, and the property is
that workflow rather than holding a suite: a tree that runs its suite
somewhere else carries no `test` badge, and what goes red when the suite
falls is the badge of the workflow that ran it. This repository is that
tree, its suite running inside `alignment.yml`. Splitting the property
as *builds documentation* and *served by Read the Docs* are split is the
rejected alternative: there the two badges answer for a build and a
subscription, where a `test` badge pointing at `alignment.yml` and the
`alignment` badge beside it would be one workflow's status under two
names, and a reader seeing them differ would be reading two measurements
where there is one.

**Building documentation and being served by Read the Docs are two
properties**, the second not implied by the first: a tree that builds
`docs/` and subscribes no service to it is complete rather than short of
anything, which is what *The documentation* below says. Under one
property covering both, that tree's absent Read the Docs badge and a
badge a tree owes and does not carry read the same, and only the second
is a finding. What the split gives up is *published documentation* read
off the `docs` badge alone: the pair answers it instead, and the order
below keeps the two adjacent, so a tree holding both carries them
together.

Which trees the second names is read from each tree's own
`REPOSITORY.md`. `.readthedocs.yaml` is in every tree that builds
`docs/`, so the tree cannot be read for the property, and a subscription
is a setting outside the tree rather than a membership the organization
decides — which is section 11's file and not a record here.
`btclib-benchmarks` is where that reads as a decision: it builds
`docs/`, subscribes no service, and says so under its *What is not
configured, and why*.

**The licence badge is tier 1's for the reason `SECURITY.md` is**: the
archive leaves github.com. A repository page states the licence beside
the README of its own accord, which
`gh api repos/<org>/<repo> --jq .license.spdx_id` is the source of, so
on the page the badge sits on it restates what is already there, and it
earns its line where the README travels — the long description an index
renders, and the copy an unpacked sdist carries. What that gives up is
a tier-2 tree's row saying what the licence is; the sidebar beside it
says so, and the row is worth more for the questions no sidebar
answers.

**A sentinel's badge is recorded rather than derived**, because the
sentinel is: section 10's *Which trees carry which sentinel* is the one
record, and the badge and the workflow are one membership rather than
two. Carrying the badge is why the workflow is there rather than the
other way round, so a tree drops both together or keeps both.

**That badge is the workflow-run one for every sentinel but
`scorecard`** —
`github.com/<org>/<repo>/actions/workflows/<name>.yml/badge.svg`,
answering whether the run passed. `scorecard` publishes a score rather
than a pass or fail, and the property asks for that score:
`api.scorecard.dev/projects/github.com/<org>/<repo>/badge`, which
section 10's `scorecard` subsection already ties to the same
`publish_results: true` the published score itself needs. A
workflow-run badge there would answer whether the sentinel ran and not
what it found, where what it found is the reason section 10 gives for
running it at all.

**Every workflow-status badge carries `?branch=main`** on that URL, the
gates' and the sentinels' alike. The row is an audit of `main`, and an
unqualified badge is not always `main`'s: where the workflow has no run
on `main` it renders another branch's, a deleted branch's included, and
nothing in the render says so — the fallback is
[GitHub's own](https://docs.github.com/en/actions/how-tos/monitoring-and-troubleshooting-workflows/monitoring-workflows/adding-a-workflow-status-badge).
The qualified badge answers for `main` or answers `no status`, which
*A badge that answers with anything but a measurement* below reads as
a question: datable while the first `main` run is still ahead, a defect
once its day has passed. Section 10's *`workflow_dispatch` on
everything* is what gets a workflow its first `main` run before its
day, so a tree that lands the badge dispatches the workflow from `main`
rather than leaving it at `no status` until the schedule comes round.
The rejected alternatives are the unqualified badge, whose fallback
reports what the row does not audit, and a qualifier omitted where the
workflow has no `main` run yet, which is a row re-derived per workflow
and out of date the day the first run lands. The pre-commit.ci badge,
`results.pre-commit.ci/badge/github/<org>/<repo>/main.svg`, is outside
the rule, being the service's own and not a workflow-status badge: its
branch is in its path.

**A workflow-status badge's link carries `?query=branch%3Amain`**, the
same filter in the spelling the runs page takes: the image's
`?branch=main` is ignored there, and a page ignoring it renders as the
unfiltered one. A badge line is one claim, so the page the reader
arrives on lists the runs the image answers for. An unqualified link
lists every branch's, and a feature branch's red run at the top of that
list says nothing about `main` — the confusion the qualifier above
removes, arriving one click later. The rejected alternative is the
unqualified link, which is how a reader reaches the pull request run
that broke something and which the filter hides. It is rejected because
that is a different question from the one the row answers, and because
the filtered page carries a *Clear filters* control beside the filter it
applied: the whole history stays one click from a reader who wants it,
where a run of another branch read as the audit's is an error nothing
announces.

**The order is fixed**, and it is three groups: what the software is,
whether it works, and what the OpenSSF makes of it.

The first opens with the release identity as a pair, the version beside
`github/v/release`; then what the project is, the development status and
the licence; then the rest of what the index carries, the downloads, the
supported Python versions, `implementation` and `wheel`.

The second is the gates and then the sentinels: pre-commit.ci, `lint`,
`test`, `docs`, Read the Docs, then the sentinels in the order section
10's calendar gives them. The calendar fixes the sentinels' order and
nothing fixes the gates', so this list is where the gates' order is
decided rather than read off something else. Read the Docs is among them
because it answers with a state of the build as the workflow badges
around it do and builds what `docs` builds.

The third is the Scorecard badge and then the OpenSSF Best Practices
badge, on a line of their own. `scorecard` is the calendar's last row,
so the sentinels end where that line begins and the Scorecard's badge
reads as the last of them without being among them.

A tree skips what it does not own and keeps the rest in that order, so a
reader comparing two `README.md` files compares like with like instead
of hunting. Taking the sentinels' order from the calendar is one order
to maintain rather than two, and what it costs is that a workflow moved
to another day moves its badge in every `README.md` that carries it.
That identity is over the sentinels alone: `lint`, `test` and `docs`
have no row in section 10's calendar, so a reader who looks there for
one is reading the wrong table rather than an incomplete one.

`img.shields.io/pypi/wheel` and `img.shields.io/pypi/implementation`
are read off the files a release uploaded rather than off anything the
project declares: `iniconfig` names no `Implementation` classifier and
the second renders `cpython` for it anyway. `github/v/release` is read
in a **pair** with the PyPI version badge, which the order above puts
beside it: where the two disagree, a release reached the forge and not
the index.

**A badge that answers with anything but a measurement is a question
with two answers**, and which one is the point: either the thing it
reads has not happened yet — a workflow short of its first scheduled
run, a project not yet built — which is datable and not a defect, or it
should have happened and did not, which is. That is what keeps the row
an audit rather than decoration, and it is what catches a workflow
renamed out from under a badge still pointing at the old file.

Reading it is a reading and not a pattern, because each service says so
in its own words and changes them without telling anybody: a GitHub
workflow badge answers `no status`, pre-commit.ci and Read the Docs
`unknown`, the Scorecard `invalid repo path`, and shields a phrase per
family — `repo not found`, `package or version not found`, `no releases
or repo not found`. A pattern written from that list passes the day a
service rewords its own failure, and passes silently, which is the one
way this rule can fail without anybody noticing. What a command settles
is the narrower half: a badge not served at all, which is what a renamed
workflow and a deleted project both answer with. Section 15 has both.

What is refused, and the reason is nearly the same one each time:

- **a badge that asserts a tool rather than measuring one** —
  `linted with ruff`, `code style: black` and the rest. The string is
  written into the URL, so it renders the same the day the tool is
  removed;
- **`img.shields.io/badge/license-MIT-blue`**, which is that defect in
  small: it renders `license MIT` because the URL says so, where the
  derived form renders it because `LICENSE` does. The derived form
  replaces it rather than sitting beside it, two badges of one fact
  being two things to keep true;
- **`last-commit`, `commit-activity` and `contributors`** — derived, and
  the objection is not that: they measure activity rather than the tree,
  so a quiet month on a finished library reads as decay;
- **a coverage badge** — section 8's floor already refuses a fall, so
  the badge would restate what a gate enforces in exchange for an upload
  to a third party;
- **REUSE compliance** — it renders `reuse unregistered`, which is a
  registration with that service and not a property of the tree;
- **`img.shields.io/pypi/types`**, which looks like the one badge
  reading the **shipped artifact** and is not: it reads the
  `Typing :: Typed` classifier. `urllib3` ships `urllib3/py.typed` in
  its wheel, declares no such classifier, and the badge renders
  `untyped`. So it restates section 3's classifier, which section 3
  already pairs with `py.typed` by rule, and a badge restating a rule
  the tree gates is the objection made of a coverage badge two entries
  up. What that gives up is a reader of the index page seeing the
  typing promise at a glance, which the classifier list on that same
  page carries anyway;
- **a link to the repository** — it renders the repository's name
  because the URL says so, and the row is an audit, so the item that
  measures nothing is the one that does not belong in it. What that
  gives up is the reader who meets this file as the long description an
  index renders or as the `README.md` an unpacked sdist carries, where
  the repository is not one click away: section 3's `[project.urls]`
  reaches that reader instead, `repository` being a `Project-URL` line
  in the sdist's own `PKG-INFO` and a field the index serves.

The Read the Docs host is `app.readthedocs.org` and not `readthedocs.org`
because the second answers `307` and redirects to the first: one spelling
because two are two things to keep true, and that one because it is where
the other lands, a redirect being something its owner can retire.

The Best Practices badge is admitted where REUSE's is refused, and the
line between them is what the render measures. For a registered project
the badge answers with the questionnaire's live state — in progress with
its percentage, passing, silver, gold — a state that moves when an
answer stops being true, and it is the same state the Scorecard's
`CII-Best-Practices` check scores, so the row and the `scorecard`
sentinel read one fact from two sides. REUSE's stays refused for the
reason its own bullet above gives, which this render escapes: the
questionnaire's state is a measurement, where `reuse unregistered` is
not. Registration is the maintainer's attestation and not a pull
request. Which trees it reaches is section 10's `scorecard` entry, that
sentinel's `CII-Best-Practices` check being what reads the
questionnaire, so a tree the entry does not name has a row complete
without the badge.

The downloads badge is pepy's rather than `img.shields.io/pypi/dm`, and
both of them render: the first answers with the project's whole life and
the second with the last month, so the second is a figure that falls
without anything having happened to the tree. What that gives up is the
reading `pypi/dm` is better at, whether the package is being taken up
now.

**The badge links to `pepy.tech/projects/<name>`, plural, and not
`pepy.tech/project/<name>`**: the singular answers `308` and redirects
to the plural, the same reason the Read the Docs host above is
`app.readthedocs.org` and not `readthedocs.org` — a redirect being
something its owner can retire.

**`CONTRIBUTING.md`'s badge block is inside this rule's reach, and it is
not the row.** Some trees open *This repository in particular* with a
block of toolchain badges, and the block's first line is its own
admission rule: each badge names a choice the sections below explain, or
a place to go, and the README keeps the ones that can turn red. That
sentence is the rule, stated where the block is, and it is what makes
the block a function rather than a curation: a badge belongs there
because a section of that same file explains the choice it names, so two
trees' blocks differ exactly where their toolchains do and nowhere else.
The repository link, refused from the row above as the item that
measures nothing, is admitted here as the one badge of the *place to go*
clause — `CONTRIBUTING.md` travels in the sdist and renders where the
repository is not one click away — so a tree that carries the block
carries it. The block itself is not owed: a tree without one has nothing
to explain away, its sections carrying the same choices unbadged. What
is refused is only a block without its sentence, which is a curated list
wearing the shape of a rule.

**A publishing repository's `README.md` ends with the line naming who
supports the work**, under a thematic break:

```markdown
---

The btclib organization and its projects are actively supported by
[DGI](https://dgi.io) and [CheckSig](https://checksig.com).
```

It is tier 1's for the reason `SECURITY.md` is: the archive leaves
github.com. The README is the long description an index renders, so a
reader who has that page and not the repository meets the project with
no organization beside it, and should not have to work out whether it is
somebody's weekend project. Where nothing is published the README is
read on github.com under `btclib-org`, and `profile/README.md` — the
page the owner link reaches — is where the organization says it, once
and for all of them. The alternative weighed was every tier: what that
buys below tier 1 is a second copy of a sentence a reader is one click
from, and what it costs is a claim whose subject is the organization
kept true in every tree separately. This repository publishes nothing,
so `profile/README.md` is its only copy.

Identical wherever it appears, and identical on purpose: reworded per
repository it would be several claims to keep true instead of one, and
the `links` workflow is what notices if either URL stops resolving. It
is the organization the line names, not `btclib`: that is one package's
name, and the siblings that publish beside it would otherwise credit the
support to one of the things being supported.

The rule is a claim about the repositories, and the loop is what checks
it:

```shell
for r in <every repository that publishes>; do
  printf '%s\t' "$r"
  gh api "repos/<org>/$r/contents/README.md" --jq .content \
    | base64 -d | grep -c 'actively supported'
done
```

`1` from each is the answer; a `0` is a repository short of what its
tier binds, filed here.

Dotfiles, each owed by the tiers that owe the section reading it:
`.pre-commit-config.yaml`, `.python-version`, `.gitattributes`,
`.gitignore`, `.markdownlint.jsonc`, `.taplo.toml`, `.yamllint.yaml`,
`.readthedocs.yaml`, `.secrets.baseline`, and `.vscode/` and `.claude/`,
both tracked.

### Directories

- the package directory, under `src/`, holding `py.typed` and a
  `__init__.py` that declares `__all__`;
- `tests/`, mirroring the package;
- `docs/source/`, hand-written, with a test that every shipped module is
  documented;
- `.github/` — `workflows/`, `dependabot.yml`, `ISSUE_TEMPLATE/`,
  `PULL_REQUEST_TEMPLATE.md`, `scripts/` and `mutation/`.

`.github/` is every tier's, and holds what the sections the tier binds
ask of it. The other three name a package as their subject rather than a
tier — the package directory *is* the package, `tests/` mirrors it, and
`docs/source/` documents what it ships — so a tree installing none owes
none of the three: tier 1 is a package by what that tier is, and a
project that publishes nothing may install nothing — `package = false`,
or a build backend given no module to build. Where there is no package a
bullet has no subject: a floor is over the rules whose subject a tree
holds, and does not supply one.

**`PULL_REQUEST_TEMPLATE.md` sits under `.github/`.** GitHub reads the
file from `.github/`, from the root or from `docs/`, in that order — in
a repository's own tree, and in this one for a repository that carries
none of its own — so where it goes is this file's to say and not the
forge's, and a copy under `.github/` is the one served whatever else a
tree holds. It goes there because it is the forge's input rather than a
document a reader opens, which is what `dependabot.yml` and
`ISSUE_TEMPLATE/` beside it in the bullet above are as well. What that
costs is the reader who would have met the template in the repository
listing, the same trade this section makes for the package directory
under `src/`.

The rejected alternative is the file wherever GitHub reads one, which
leaves two trees of one organization differing in shape for nothing and
cannot be read back off the forge:
`repos/<org>/<repo>/community/profile` answers
`files.pull_request_template.url` with this repository's copy for a tree
that has none of its own, so that endpoint cannot tell a repository
carrying no template from one carrying its own.

**The package directory sits under `src/`.** A package at the
repository root is on `sys.path` whenever anything runs from that
root, so an import can resolve to the checkout instead of to the
installed distribution, and section 7's convention tests exist to tell
those two apart. Under `src/` the checkout root holds no importable
package, so the suite tests what was built or fails outright, and the
two cannot be silently confused. The root layout costs one directory
less and puts the package where a reader of the repository listing
meets it first; that is what this gives up.

**The package directory is singular by the rule and not by omission.**
`uv_build` lets a project name more than one module in `module-name`, a
namespace package sharing a distribution between them, and that is a
shape this file does not state: one tree here is one distribution
carrying one package, and a project wanting several stays several
repositories or several `module-name`s of its own rather than one tree
answering to two directories. The same key also reads a dot as that
backend's other namespace-package shape -- `module-name = "foo.bar"`
builds the module `bar` under the shared namespace `foo`, at
`src/foo/bar`, rather than naming this tree's own package -- and that is
a shape this file does not state either, for the same reason: the
package a tree here carries is its own, not a leaf sharing a namespace
with a module another distribution installs beside it.
`tests/surface_test.py`'s `package()` reads the key rather than
resolving it, so a tree declaring either shape meets a message naming
the repository and the key instead of a directory this file never
promised it one.

A tree without a package may still keep `tests/` above the floor:
`.github`'s own suite is over the organization rather than over a
package this repository does not hold, and a tier is free to carry more
than it is asked for.

### The documentation

**A tree that releases a Python package provides documentation; a tree
that documents need not release.** A release carries a URL no later pull
request can correct, for the reason section 11's *Pages and Read the
Docs* gives, so what a published version points a reader at has to
exist. The converse does not follow: building this directory says
nothing about publishing, so a tree that keeps it and subscribes no
service to it is complete rather than short of a release. The badge rule
above reads *builds documentation* off a tree as a property, and this is
where a releasing tree owes it — a state recorded rather than work asked
of anybody, and the next tree kept from arriving without it.

What `docs/source/` holds is a few hand-written pages around a reference
sphinx generates from the docstrings of a typed public API, one set per
tree and none of them large.

**The theme is `furo`**, declared in the `docs` group and named in
`docs/source/conf.py`. It is built for that shape: the content first,
the navigation in the left sidebar and the page's own contents in the
right, light and dark from one setting. It is also what the part of the
Python ecosystem these projects sit in reads as ordinary — `pip`, which
it was written for, `black`, `urllib3`, `attrs` and the Python
developer's guide. The alternative weighed was `shibuya`, which
Emscripten, Sentry's Python libraries and Authlib use: it is the better
theme for a product site, and its announcement bars, landing pages and
`sphinx-design` components are what decides against it here, being
surface these trees would carry and not use. That surface is what
choosing `furo` gives up, so a tree that later wants a landing page
changes theme rather than extending this one. `sphinx_rtd_theme` is
where a Read the Docs project starts by default, which is a reason to
find it in a tree and not a reason to keep it.

Whether sphinx stays the generator is open and not decided here: a tree
that left it would take its theme with it, so nothing above turns on the
answer.

**The build runs `-n` as well as `-W`.** `-W` turns a warning into an
error and never sees a cross-reference that resolves to nothing: a
renamed class in a `:class:` role, a parameter type no longer in the
tree, a moved function is not a warning at all, so the build is green
and the link goes nowhere. For documentation generated from the
docstrings of a typed public API that is the documentation half of
running mypy without `strict` — the tool is there, the flag that makes
it strict is not, and the gap is invisible because the gate passes. `-n`
is what makes an unresolved reference a warning for `-W` to refuse.

**`sphinx.ext.intersphinx` comes first**, with a mapping for python and
for whatever else the annotations reach. Without an inventory to resolve
against, a name from outside the tree resolves to nothing and is
reported as the tree's own broken link: sphinx's own domain answers for
the builtins, so `int` and `bytes` are silent, but
`collections.abc.Sequence`, `pathlib.Path` and `os.getcwd` each draw a
`reference target not found` with nowhere to look. Turning `-n` on
before the mapping exists therefore measures the standard library rather
than the documentation, and fills `nitpick_ignore` with entries whose
reason is that sphinx was not told where python's objects live.

**`nitpick_ignore` holds only entries whose reason is written beside
them**, an entry being a reference that genuinely cannot resolve rather
than one nothing was pointed at. What `-n` costs is paid there and
nowhere else: every entry is a reference the build stops checking, so a
broad `nitpick_ignore_regex` buys a green build by giving up the check
itself. That is the same trade section 5 makes over `ignore` and section
8 over `exclude_also`, and it is why the first run of `-n` is triage
rather than a pass.

**`--keep-going` is not passed.** In the sphinx `uv.lock` resolves, the
flag is declared with `help=argparse.SUPPRESS` and the application
records it as unused, so it is missing from `--help` and accepted by the
parser at once: an unrecognized argument is refused, and this one
builds. `-W` on its own reports every warning a build raises and fails
at the end of it — a warning raised while reading and one raised while
writing arrive from the same run — so what the flag's name asks for is
what the build does without it. Keeping it with a comment naming what it
buys is the alternative, and there is nothing for that comment to say.

**`exclude_patterns` names what the tree writes under `docs/source/`,
and is empty where nothing does.** `sphinx-quickstart` seeds it with
`_build`, `Thumbs.db` and `.DS_Store`. Sphinx reads a file as a document
only where its name ends in one of `source_suffix`'s suffixes and
something is left over to be the document's name, so under the `.md` and
`.rst` these trees declare neither of the last two is a candidate to
exclude at all. `_build` is a live entry only for a build directory
written inside the source directory, a page under one being read and
then failing `-W` for belonging to no toctree; a tree whose build goes
beside `docs/source/` has nothing there to name. Carrying the stock list
anyway is the alternative, rejected because it reads as a statement
about the tree's layout while naming paths that layout does not produce.

## 3. `pyproject.toml` is the configuration

One file holds the project metadata and every tool that can be
configured in it. Where a tool the lint gate runs looks for its
configuration by name from the working directory and `pyproject.toml` is
not among the names, it keeps a file of its own: the tool finds that
file, so the hook passes no path, and a file has the room for reasoning
that a hook argument has not. Section 14 names each of those files and
what it holds.

- **The build backend is `uv_build` where the project is pure Python.**
  What the choice buys is where the sdist's inclusion is then declared:
  glob patterns in `[tool.uv.build-backend]`, in this file and beside
  the rest of the configuration, rather than in a file of its own with
  an include and exclude language of its own. One backend across the
  ordinary case is also one such language to learn rather than one per
  project. What makes a project the exception is what it compiles:
  `btclib-secp256k1` builds a vendored C library through cffi and cmake,
  which hatchling answers with a build hook and a pure-Python backend
  does not answer at all.

    Section 2's `src/` rule matches each backend's own default, so
    neither needs a key that states it. `uv_build` already looks under
    `src/` unless `[tool.uv.build-backend] module-root` overrides it, so
    that key disappears under the rule rather than changing value.
    Hatchling names no directory at all: `<name>/__init__.py` at the
    root is its first file-selection heuristic and `src/<name>/__init__.py`
    its second, so the rule is answered by which heuristic matches
    rather than by a setting.

    `requires` names that backend with a floor and, under `uv_build`, a
    **ceiling at the next minor**, where the bullet below refuses an
    upper bound to a sibling dependency. What differs is what the bound
    costs: on a runtime dependency it makes a published artifact refuse
    a version somebody already has, where on a build requirement it only
    narrows what an isolated build resolves for itself, and that build
    resolves whatever the bound allows. What it buys is that uv bumps
    its minor for a breaking change and releases this backend with
    itself, so an unbounded requirement lets a published sdist build
    under a backend nobody checked it against, with no release of this
    project in between. Each bound carries the reason that chose it, and
    PEP 639 below is one such reason.

    The floor is the boundary of the property it keeps, and the comment
    gives the measurement that found it. Under `uv_build` the sdist's
    own `pyproject.toml` is a normalized copy of the file with the
    verbatim one kept beside it as `pyproject.toml.orig` from `0.12.0`;
    below that the sdist carries the verbatim file and no `.orig`.

    The rejected alternative is a floor above that boundary, aligned
    with the `uv` the gate pins through `uv-pre-commit` or with the
    sibling the number was copied from, as an equality or as a bound the
    floor stays under. It excludes backends that keep the property, and
    nothing checks the number it lands on: under section 12's
    `--installer=pip` the archive `check-sdist` compares against git is
    packed by a backend `additional_dependencies` resolves from
    `[build-system]`'s own range, which satisfies the floor by
    construction. What does read the floor is `uv build`, and section 1
    is where that costs: `[tool.uv] required-version` names the oldest
    uv a tree admits, pre-commit.ci moves a hook rev on each
    repository's own weekly schedule with nothing moving that key, and
    on a uv the key admits but the floor excludes, uv looks past the
    copy bundled in it for a `uv_build` meeting the floor instead, which
    section 12 has too. `0.12.0` is below what `required-version`
    names — section 15's sweep prints that key per tree — so a floor at
    the boundary cannot contradict section 1.

    The boundary is measured by calling the backend's own hook at each
    version. `--with` puts `<version>` ahead of the command it
    measures, so it cannot sit last as section 9 asks; the assignment
    stands in a block of its own, for the reason section 9's bullet
    gives, and the block below it writes `${version:?}`, unset being
    what an unfilled paste of that block alone supplies:

    ```shell
    version=<version>
    ```

    ```shell
    uv run --no-project --with uv_build=="${version:?}" python -c \
      "import uv_build; print(uv_build.build_sdist('<outdir>'))"
    ```

    and not with `uv build` under a pinned `requires`: asking for a
    backend older than the one running is always section 12's
    ceiling-below case, where `uv build` falls back to the backend it
    bundles and only warns, so it answers for that copy and not for the
    pin, and the same command on a machine with another `uv` answers
    differently. btclib-org/.github#143 has the table, the boundary read
    off the last `0.11` release and the first `0.12`.
- **The version is declared once**, in `[project]`. The package reads it
  back with `importlib.metadata`; the sphinx `conf.py` parses this file,
  metadata not being available to an uninstalled build. Two declarations
  are two things a release has to compare.
- **The name in `[project]` is the distribution's, and the repository
  is named after it, hyphenated, never after the import package.** PEP
  503 normalizes runs of `-`, `_` and `.` in a distribution name to a
  single `-`, so the hyphen is the canonical spelling; an import
  package is a Python identifier and takes underscores instead, so the
  two are spelled differently on purpose. The two rules do not carry
  the same weight: the language's own grammar has no hyphen in an
  identifier at all — `name_start` and `name_continue` admit letters,
  digits and `_`, never `-` — where PEP 8's *Package and Module Names*
  only discourages the underscore, as a matter of style. `bitcoin-core-rpc`
  declares `name = "bitcoin-core-rpc"` and imports as `bitcoin_core_rpc`;
  the repository takes the first spelling, not the second. The built
  artifact escapes both the same way regardless: PEP 427's escaping
  rule normalizes any run of `-`, `_` and `.` in a distribution name to
  `_` for the wheel filename and the `.dist-info` directory, so
  `bitcoin-core-rpc` and `bitcoin_core_rpc` would both name the same
  `bitcoin_core_rpc-<version>` wheel.

    **`name` itself takes that same canonical spelling.** Folding the
    family together is right for asking whether a distribution and its
    repository agree, and says nothing about which member of the
    family the `[project]` table may pick for itself; this states that
    it picks the hyphen too. `btclib-secp256k1` declares
    `name = "btclib-secp256k1"`, the same hyphen the other four
    publishers write. The wheel and the `.dist-info` directory read
    `btclib_secp256k1-<version>` either way: the escaping rule above
    already folds both spellings to the one string.

    **A requirement naming the distribution takes that spelling too**,
    wherever it is written: a table a resolver parses, a command in a
    document, a block somebody is meant to copy. The normalization above
    is what hides the other spelling — it resolves and installs the same
    distribution, and no gate reports it — so what the written form
    decides is what a reader copies out and types.
    `tests/names_test.py` asks this of every tree, reading the position
    rather than the spelling: a name is a requirement where a table
    declares it as one, or where a version specifier or an extras
    bracket follows it, and an import package is written in neither
    place.

    **Every other place a person writes the name for somebody to copy
    out takes it too**: a flag's value, an install target, a deployment
    environment's `url:`, the message on a release tag. The reason is
    the one above and it does not turn on the position — what the
    written form decides is what a reader copies and types — so the rule
    reaches wherever the thing named is the distribution rather than the
    import package. Position is all `tests/names_test.py` can read, and
    these sites have none, so this half is a reader's catch.

    **A PyPI page is linked as `https://pypi.org/project/<name>/`**, the
    form `https://pypi.org/p/<name>` redirects to, and it spells the
    name canonically like any other written form: the site serves
    `/project/btclib_secp256k1/` and `/project/btclib-secp256k1/` alike
    and redirects neither, so which spelling a reader is shown is the
    writer's. The rejected alternative is the short form, which saves
    the characters and costs everybody who follows it the redirect. A
    URL that settles its own spelling is outside the rule rather than an
    exception to it: `/simple/` redirects to the hyphen PEP 503 folds
    the name to, and asks nothing of whoever writes the link.

    **The bullet has no subject where a tree builds no distribution.**
    `bbt` and `.github` both declare `package = false` and a
    `[project].name` of their own — `bbt` after the repository,
    `.github` after what its suite does — and neither reading is
    wrong, because neither key names a distribution. `.github` could
    not take the repository-naming half even if it tried: PEP 503
    normalizes `.github` to `-github`, which is not a distribution
    name. A `package = false` tree's `name`, where it declares one, is
    its own choice.
- **PEP 639 licensing**: `license = "MIT"` as an SPDX string and
  `license-files`, not the deprecated table and not a `License ::`
  classifier. The floor that carries them is the backend's own:
  `btclib-secp256k1` writes `hatchling>=1.27` because an older hatchling
  rejects both halves above outright, where `uv_build`'s floor is set by
  what its sdist carries and says that instead. A constant copied from
  another project is a requirement the build does not use.

    **`license-files` names `LICENSE` and `AUTHORS.md`, and nothing
    else**, in a file that declares a build backend: where nothing is
    built the key would name files into an archive that does not exist.
    The MIT notice names a collective, and `AUTHORS.md` is where the
    archive says its members are listed — section 14 has what the file
    is, the vendored attribution it carries included, and why
    `COPYRIGHT` is not named beside it. The alternative is `LICENSE`
    alone: what it saves is shipping a file whose text is a pointer to
    github.com, which a reader who has the archive and not the site
    cannot follow, and what it costs is an archive that names the
    collective and never says where its members are listed.

    **Nothing local refuses the classifier beside the expression**,
    which is why this is a rule rather than something a build catches.
    One file carrying both, built under each backend — the probe and
    what it printed are btclib-org/.github#113's — leaves `uv_build`
    warning, hatchling saying nothing at all, and both archives carrying
    `License-Expression: MIT` and the deprecated `Classifier:` line
    together. `setuptools>=77` is what fails the build, and it is not a
    backend this standard keeps. `twine check` passes both archives, and
    so does the `trove-classifiers` comparison the `classifiers` bullet
    names, which asks whether a string is a classifier at all: this one
    is a current entry of that list and not a deprecated one. Whether
    PyPI's upload endpoint refuses the pair is unmeasured, asking it
    meaning publishing a version.
- **`authors` names what the MIT notice names**, in every file that
  declares a `[project]` table, whether or not that file builds
  anything. The collective is already fixed three times over — by
  `COPYRIGHT`, by `LICENSE`, and by the header ruff's `CPY` holds every
  source file to — so a per-tree literal here is a fourth statement of
  one fact, and the one a package index prints as the package's author.
  `btclib-node` published an sdist whose `LICENSE`, `AUTHORS.md` and
  every source header named the collective while `Author-email` named an
  individual: three to one, and the one on the page
  (btclib-org/btclib-node#598).

    The alternative is the scoping the bullet above uses — `license-files`
    reaching only a file that declares a build backend — and what it
    leaves is why it is not taken here. `bbt` and `.github` build
    nothing, so the harm cannot reach them; but neither can the check,
    and an unread key is where a tree drifts unobserved until somebody
    gives it a backend. Declaring it costs each of them one line, and
    what it buys is that the answer is the same wherever a reader opens
    the file.

    **The address is fixed by the trees agreeing, not by a literal
    here.** `COPYRIGHT` carries the name and nothing carries the
    address, so spelling the address out in this file would put the one
    copy no command checks in the one document a tree cannot re-derive
    it from — and the day it moved, every `pyproject.toml` would be
    updated, the suite would stay green, and this sentence would go
    stale with nothing reading it. What section 15's suite asks instead
    is that the name be `COPYRIGHT`'s, transcribed the way `notice-rgx`
    already is, and that every declaring tree answer the same address as
    every other, an address none of them declares failing the same as
    two that disagree. The trees are each other's authority: one changed
    alone is a drift the suite names, and all of them changed together
    is a decision rather than an accident.
- **`keywords` are the GitHub topics**, the same names in the same
  lowercase spelling. The keywords carry an order and the topics do not:
  PyPI shows keywords as given, so they are ordered by relevance, while
  `gh api repos/<org>/<repo> --jq '.topics'` answers alphabetically
  whatever was set. So the order is maintained on one side and compared
  on neither, and what it decides is which name is left out when GitHub's
  twenty are full — past twenty the topics are the first twenty
  keywords, which is the one place the two may differ at all.

    Both name what the tree holds. A keyword nothing in the tree answers
    to is a claim made to whoever searched and not kept; something the
    tree holds that no keyword names is why somebody did not find it.
    Neither is visible from inside the file, so both are read against
    the tree rather than against the list they were copied from.

    **The rule turns on the `[project]` table and not on the index.** A
    tree that uploads nothing declares the list all the same, so that
    the topics github.com shows have something in the tree to be read
    against. The rejected alternative keys the rule on publishing, the
    bullets around this one each being about metadata an index serves,
    and what it costs is that reading: such a tree's topics then answer
    to no list, and drift from what it holds with nothing red. A
    repository with no `pyproject.toml` has no table and so no key to
    write, and section 16's checklist is where its topics are recorded
    instead.
- **`classifiers` are present**, and each is a claim about this tree
  rather than a line taken from a sibling's: `Typing :: Typed` and
  `py.typed` ship together or neither ships, the marker being PEP 561's
  promise to a downstream consumer that the installed package carries
  types and the classifier that same promise on the index page, so one
  without the other is a package whose two statements of one fact
  disagree; an `Operating System` only where the package is built for it
  and `OS Independent` only where nothing is compiled, and one
  `Programming Language :: Python :: X.Y` per interpreter the matrix
  runs. A `t` suffix in the matrix names that same `X.Y`, free-threading
  being a build of one version and not a version of its own — unlike a
  `pypy` prefix, a different implementation with a classifier of its own
  under `Implementation`. PyPI's own `Free Threading` classifiers are a
  maturity level an author claims for the code, and one is declared
  where the merge gate exercises the free-threaded build: a gate refuses
  the landing that breaks that build, where a sweep runs beside a
  landing and blocks nothing. The rejected alternative is a green sweep,
  which says the build passed somewhere and leaves the claim resting on
  a run nothing waits for. These are conventions this section states, so
  section 7's closing rule makes them tests rather than hopes: a tree
  that publishes carries `interpreters_test.py`, which reads the floor,
  the classifiers and the matrix and refuses a disagreement, section 15
  saying why publishing is what decides that and not section 1's
  library. That comparison is over a classifier naming one version, and
  `Free Threading` names none, so it reaches the free-threading
  convention no more than it reaches the `Implementation` classifier
  beside it — which is gated instead by a biconditional, the classifier
  present exactly where what it claims is run. The free-threading
  convention takes that same shape, and its second side is the gate's
  own matrix rather than every file CI holds, a sweep naming an
  interpreter as readily as the gate does. Nothing local refuses a
  classifier that is not a classifier at all — `twine check` reads the
  long description and not this list, and a build accepts whatever the
  file says; PyPI's upload endpoint is what rejects one, at the point
  where a version is already being consumed.
  `trove-classifiers` is the same list as a package, and comparing
  against it is the check that can run before then.

    Both halves of that pairing, and section 2's own `py.typed` bullet
    before it, are a promise about an installed package, and `.github`'s
    own suite reads a tracked one instead: `surface_test.py` and
    `classifiers_test.py` ask `git ls-files`, holding no checkout of the
    trees it audits to build an archive from. What verifies the promise
    where a tree publishes is section 12's `check-sdist` and
    `check-wheel-contents` — measured by building a tree with the marker
    excluded once from the wheel and once from the sdist:
    `check-sdist` drives no wheel at all, and passes an sdist that still
    carries the marker while the wheel built alongside it does not, so
    that half is `check-wheel-contents`'s, once
    `[tool.check-wheel-contents]` names the package. A tree short of
    tier 1 owes the marker with no gate over whether a build carries it,
    this suite included.
- **`[project.urls]`** carries homepage, documentation, download,
  changelog, repository, issues and pull requests.

    **A releasing tree's `homepage` is its own documentation site, in
    both surfaces that carry the name**: this field, which an index
    serves with the package, and the repository's `.homepage`, which is
    the *About* link on its page. A project's home is what documents it
    and not a project page, a sibling's or its own, and section 2's rule
    that a releasing tree provides documentation is what says there is
    one to name. A tree that releases nothing publishes no URL that
    outlives a correction, so this asks it nothing. The
    two are read apart, half of the pair being a setting no file in the
    tree holds:

    ```shell
    gh api repos/<org>/<repo> --jq '.homepage'
    sed -n '/^\[project.urls\]/,/^\[/p' pyproject.toml
    ```

    Where they disagree, the alternative weighed was to move the setting
    to whatever `pyproject.toml` declares. It is the cheaper edit, and it
    consecrates the state rather than correcting it: a tree whose
    declared home is another project's page keeps it, where the rule
    sends both surfaces to the documentation the tree itself provides.

    **`documentation` names that same URL, and stays.** What it costs is
    an index page showing two links to one page; what it buys is the
    field indexes and tools read for documentation specifically, which
    `homepage` does not stand in for.
- **No upper bound on a sibling dependency.** Two projects developed
  together coordinate a break at release time, which is what a ceiling
  substitutes for when they cannot; a ceiling would cost a release per
  upstream minor and make a published artifact refuse a version it works
  with.
- **Every comment carries the reason and the negative result**, held to
  80 columns by the `toml-comment-width` hook.

## 4. The lint gate is `.pre-commit-config.yaml`

**The lint workflow runs this very file.** There is never a second list
of the same tools in a workflow: what CI enforces is exactly what a
commit enforces, and a hook cannot be gated by pre-commit.ci alone.

**Every hook that has a fix mode runs with it turned on.** A check-only
hook reports a defect a machine already knows how to repair and spends a
human round reading a finding a flag would have applied; a fixer instead
leaves the correction already made, in the tree, for whoever committed to
read before the commit lands — a pre-commit hook that fixes a file fails
the run rather than applying itself unseen. A hook stays check-only where
it has none to turn on: a validator has nothing to rewrite, and neither
does a rule with no mechanical repair for what it finds.

### The `ci:` block

```yaml
ci:
  autofix_prs: false
  autoupdate_commit_msg: "Update the pinned pre-commit hook revisions"
  autoupdate_schedule: weekly
  skip: [mypy]
```

`autofix_prs: false` because a bot committing to a branch is at odds with
a setup where no workflow token can write; a failing hook is fixed by its
author. `skip: [mypy]` because that hook shells out to uv, which
pre-commit.ci does not have — the lint workflow covers it. No
`autoupdate_branch`: the default branch is the only branch.

### What the hooks cover

- **the file checking itself** — `meta`'s `check-hooks-apply` and
  `check-useless-excludes`, so a pattern that has stopped matching is a
  failure rather than a rule that quietly stopped running; and a local
  `pinned-rev` pygrep hook refusing a `rev:` that names a bare major or a
  prerelease, both of which `autoupdate` offers as readily as a release.
- **hygiene** — `trailing-whitespace`, `end-of-file-fixer`,
  `mixed-line-ending --fix=lf`, `check-case-conflict`,
  `fix-byte-order-marker`, `check-merge-conflict`,
  `check-vcs-permalinks`, `check-added-large-files`, and
  `check-shebang-scripts-are-executable` wherever the repository has
  scripts.
- **submodules** — the rule is *pinned*, not *forbidden*.
  `forbid-submodules` where there are none, a submodule being the one
  dependency that sits in neither the lock file nor an sdist; where one
  is legitimate, a local hook refusing an unpinned or moved submodule
  takes its place, and section 11's `gitsubmodule` ecosystem says when
  upstream moved.
- **syntax** — `check-yaml`, `check-json`, `check-toml`,
  `pretty-format-json`.
- **Python shape** — `debug-statements`, `check-docstring-first`, and
  `name-tests-test` at its default, the spelling section 7 states.
- **secrets** — `detect-private-key` and `detect-secrets` against a
  committed `.secrets.baseline`. A baseline rather than an exclusion: an
  excluded file is unwatched, where a baseline entry is a finding
  somebody has read. The two entropy plugins stay off where the vectors
  are hex strings, a new one being what a legitimate addition looks like.
  Not gitleaks: every one of its hook ids passes `--staged`, so under
  `--all-files` it scans nothing and passes.
- **spelling** — `codespell` and `typos`, both configured in
  `pyproject.toml`, both skipping vendored vectors: a typo inside an
  upstream vector is part of the vector. `typos` is a `local` hook,
  pinned through `additional_dependencies` rather than `rev:`; the
  comment beside the entry in `.pre-commit-config.yaml` says why.

    **`codespell --version` answers `0.1.dev1+g<sha>` and not the
    release its `rev:` names.** pre-commit fetches the pinned ref by
    name, shallowly, and checks out `FETCH_HEAD`; the other strategy in
    `pre_commit/store.py` fetches `--tags` and is reached only where
    that one raises. Each half of that fetch sets a field of the string
    `setuptools_scm` computes at install time. The clone holds no tag to
    describe, so `0.1.dev` stands where the release number would be; the
    number after `dev` is the clone's own commit count, which the depth
    holds at one — a full-history fetch of the same ref is equally
    tagless and puts the whole history's count there instead. What
    follows the `g` is the commit the `rev:` resolved to, abbreviated,
    and this names it in full, `<rev>` last for the reason section 9
    gives:

    ```shell
    gh api --jq .sha repos/codespell-project/codespell/commits/<rev>
    ```

    The commits endpoint and not `git/ref/tags`, so that the command
    holds whichever way the pinned repository tags: an annotated tag
    resolves to the tag object there and to the commit here.

    `typos --version` answers its release: a `local` hook's
    `additional_dependencies` installs straight from the index, with no
    upstream clone in the loop for a tag to be missing from.
- **prose and markup** — `markdownlint-cli2`, `prettier` (yaml and
  jsonc), `taplo-format`, `yamllint`.
- **schemas** — `check-dependabot`, `check-readthedocs`,
  `check-github-issue-config` and `check-github-issue-forms`, because a
  typo in any of those files is not an error to the service that reads
  it: it silently does nothing. `dependabot.yml`'s evidence is a pull
  request that never arrives; an issue form's is the *New issue* page,
  where the reader is a person and not a run. The issue pair selects
  narrowly, both hooks carrying `types: [yaml]`: `config.yml` under that
  spelling for the first, the directory's yaml that is neither
  `config.yml` nor `config.yaml` for the second, a markdown template for
  neither. `check-hooks-apply` above fails a hook that matches no file,
  so each goes where `ISSUE_TEMPLATE/` holds what it selects.
- **workflows** — `actionlint` and `zizmor`, both at zero findings, both
  required to stay there. actionlint via its Python packaging, the
  upstream hook's only non-docker id needing a go toolchain everywhere.
- **Python** — `ruff-check --fix` and `ruff-format`.
- **docstrings against signatures** — `pydoclint` over the package. The
  `D` family checks that a docstring *exists*; this checks that it
  describes the parameters and the return the signature declares, which
  is the half that goes wrong silently when a signature changes.
  `skip-checking-short-docstrings` is **each repository's to set, and
  what decides it is the form a docstring's contract takes there**. Left
  at its default, a docstring carrying sections is held against the
  signature and one carrying none is taken at its word, its length making
  no difference to that; set `false`, a docstring owes an `Args` and a
  `Returns` section for whatever the signature declares. Section 9 asks a
  docstring for the contract and does not ask for a section, so the
  answer is `false` where a section is how that tree's docstrings say
  what the call takes and returns, and the default where they say it in
  prose — a paragraph naming each parameter, or a summary that already
  states the return. pydoclint reads a section and not a sentence, so
  `false` over prose asks for the same fact a second time, which section
  9's *One fact in one place* refuses. Prose that leaves a parameter
  unmentioned is a docstring that does not state the contract, which
  section 9 asks for whatever this key says, and no value of the key
  finds it: the default holds nothing against a docstring carrying no
  section, and `false` reports the prose that names every parameter and
  the prose that names none alike. What a repository writes beside the
  key is which of the two its docstrings are; what changing the setting
  would cost belongs to the issues tracking it — btclib-org/btclib#1178,
  btclib-org/btclib-benchmarks#128 and btclib-org/bitcoin-core-rpc#172 —
  cost being a reason to defer a decision rather than one that decides
  it. Where the answer goes is section 3's rule and not a new one:
  `[tool.pydoclint]` in `pyproject.toml`. What is *not* offered is
  `false` for the public API and the default elsewhere: pydoclint has no
  such split, so it would take two invocations over two file lists plus a
  rule about which files are public that nothing checks.
- **types** — a mypy hook, below.
- **packaging** — `uv-lock`, `pyroma`, and `check-sdist` wherever an
  sdist is built, which is section 12's condition rather than a second
  one.

### The local hooks

- **mypy** — a trade-off with two right answers rather than a rule.
  Either way `--ignore-missing-imports` is off: it turns an unresolved
  or misspelled import into `Any`, which is the opposite of strict, and
  `mirrors-mypy` supplies it by default.

    - **A local hook**, `language: system`, running
      `uv run --locked --no-default-groups --group lint --group test
      mypy <package> tests .github/scripts` with
      `pass_filenames: false`. The gate then checks against the
      project's own locked environment: one declaration of what the
      dependencies are, and the real ones behind the types. Its price is
      `skip: [mypy]` in the `ci:` block, `uv` being absent on
      pre-commit.ci.
    - **`mirrors-mypy` with pinned `additional_dependencies`**, where
      the type check needs a small, stable set that can be pinned by
      hand and kept in step with `uv.lock`. Its price is that second
      declaration; what it buys is the type gate running on
      pre-commit.ci too.

    The criterion is which price is smaller: a project whose types rest
    on its own package wants the first, one whose types rest on a
    handful of stub packages can afford the second.

    **What the `skip:` then costs** is answered where that key is:
    the lint workflow covers the hook. What is left to say here is what
    pre-commit.ci is still kept for — the pull request that bumps the
    revisions pinned in this file — and that a local hook has no
    revision to bump, `uv.lock` moving its mypy instead, on Dependabot's
    own day.

    **Under the mirror, two declarations have to stay equal**, and
    nothing makes them: the hook's `rev` against the mypy `uv.lock`
    resolves, and each `additional_dependencies` pin against the same
    package there. The second declaration is the price named above; that
    it is unchecked is the part worth knowing before choosing it.
- **`toml-comment-width`** — pygrep, 80 columns on a toml comment, a
  trailing unbreakable link exempt.
- **`decoded-subprocess-encoding`** — pygrep refusing `text=True` and
  `universal_newlines=True`: a decoded child process takes the locale's
  encoding, which is the same defect ruff's `unspecified-encoding`
  catches one layer in, and no linter here has an opinion on the keyword.
- **`local-link-prefix`** — pygrep refusing a markdown link whose
  destination is local and does not begin `./`. In every repository of
  the organization, this one included: the rule is the organization's
  and not the publishing repositories', because one spelling is what
  lets a check downstream key on one pattern, and a standard whose own
  tree does not keep it is a standard with a counter-example at the top
  of it.

    What it buys where documentation is built: `docs.yml` greps the
    built html for `href="#./`, which is what MyST renders in place of a
    link the `RootFileLinks` transform in `docs/source/conf.py` cannot
    resolve — an anchor to an id no page has, and a dead link `-W` sees
    nothing wrong with once a suppression is added back. MyST renders
    the destination verbatim, so what that grep can match is decided by
    how the link was written, upstream of the workflow entirely.

    **The prefix is the rule, and not the extension**, because
    btclib-org/btclib#1175's table settles it: `DOES_NOT_EXIST.txt`,
    `sub/DOES_NOT_EXIST.md`, `DOES_NOT_EXIST` and
    `../DOES_NOT_EXIST.md` each reach that fallback and each is missed
    by the union of both greps a repository ran, so an `.md`-scoped
    rule leaves every one of them writable. A prefix refuses all four
    where they are written.

    **A badge nests a link inside a link**, and
    `[![license: MIT](…)](./LICENSE)` is the
    shape: the image is the link text, so a link text written `[^]]*`
    stops at the `]` closing the alt text and reads the image `src` in
    place of the badge's own href. Link text is therefore
    `(?:[^]]|\]\([^)]*\))*`, a character that is not `]` or a whole
    `](…)` group, which steps over the image and still checks the `src`
    by backtracking. Measured: a badge href renders exactly what a
    plain href renders, so every row of the table above can be written
    as a badge destination.

    Measured in each publishing repository, with an unresolvable
    link written each way: `./page.md`, `./page.md#anchor`,
    `./page.txt`, `./sub/page.md` and an extensionless `./page` each
    render `#./` followed by the destination, so one pattern sees every
    one; the same destinations written without the `./` render the
    destination alone, which no single pattern reaches without also
    matching the autodoc anchors those pages carry.

    **`../` is refused with the rest, and it is the row that most needs
    a reason beside it.** `RootFileLinks` *deliberately declines* to
    resolve a target that normalizes to something starting `..`, on the
    reasoning that nothing above the repository root is a document that
    build can answer for. So `../page.md` reaches MyST's fallback by
    design rather than through a gap in the transform, renders
    `href="#../page.md"`, and is matched by neither surviving grep —
    and the grep should not be widened to reach it, because a link
    climbing out of the root has nothing to resolve to in the first
    place. Refusing it at source is the only place that shape can be
    caught at all.

    The pattern's first branch asks for a whole `[text](destination)`
    whose `[` is not preceded by a backtick, so prose can quote the
    refused shape in a code span and grep output carrying no `[` is not
    matched. Its second branch reads a link reference definition,
    `[label]: page.md`, which carries no `(` and renders the same
    fallback; it is anchored at the start of the line, because a
    reference *use* followed by a colon is ordinary prose and an
    unanchored pattern reports it — measured, in
    `btclib-benchmarks`'s changelog. pygrep is line based and cannot
    see a fenced block, so an example of the refused shape inside one
    fails the hook; the code span is the way round it, and this file is
    written accordingly.
- **`no-hyphen-at-end-of-line`** — pygrep refusing a markdown line that
  ends inside a word, at that word's own hyphen. Markdown joins two
  source lines with a space, so a word wrapped there renders with the
  hyphen *and then a space* inside it. The source looks correct, which
  is why reading a diff does not find one; the instance that produced
  this rule was found by scanning rendered `<code>` spans in built html
  across the organization, which is the only gate here that reads output
  rather than source, and there is no such gate.

    Nothing else covers it. markdownlint has no rule for it, the width
    rules read a line rather than what two lines become, and
    `sphinx-build -W` is not asked whether a token means anything. It
    matters most where the token is a command or an identifier, because
    a reader copies what the page shows.

    **What it cannot see**, stated so the rule is not mistaken for the
    class: a code span whose content breaks at a `/` or a `.` renders
    with the same intruding space and has no hyphen to match. Reading
    the built html is what catches that, and this hook is not it.

    Measured before it was proposed: every repository of the
    organization was clean under `git grep -n -E '[A-Za-z0-9]-$' --
    '*.md'` once `btclib-secp256k1`'s three were fixed, so the rule
    costs nothing today and exists to keep the next one from being
    written.
- **`unquoted-placeholder`** — pygrep refusing a placeholder that stands
  as a whole argument and carries quotes. Section 9 is the rule and what
  the quoting costs: quotes make the angle brackets ordinary text, so a
  paste made before the placeholder is filled in reaches the tool with
  the placeholder as its value rather than failing at the shell. In
  every repository of the organization, this one included: the rule is
  section 9's and binds them alike, and the paste it guards against is
  made by a reader of whichever tree they have open.

    **`CHANGELOG.md` and `RELEASE_NOTES.md` are outside it**, by
    `exclude: ^(CHANGELOG|RELEASE_NOTES)\.md$`. Section 9 makes both
    append-only, so the refused shape in an entry that has landed has no
    repair and the tree carrying the hook over it no green state to
    reach — what is left to such a tree is a `SKIP=` on every run, or no
    hook at all. What the exclusion gives up is a file a reader pastes
    from like any other prose, so what holds the rule there is somebody
    reading the entry before it lands.

    The narrower exclusion, keyed on the entries written before the
    rule, is the alternative declined for being unavailable rather than
    unwanted: `exclude:` selects files and pygrep reads whole ones.
    Leaving the scope to each tree is the other, and what it costs is
    what this bullet opens by asking for — the same entry in every
    repository, rather than each deciding which of its own files the
    rule reaches. `RELEASE_NOTES.md` is named in a tree that carries
    none because `check-useless-excludes` asks an exclusion to match
    some file the hook selects rather than each name in it, and section
    2's table gives `CHANGELOG.md` to every tier.

    **What separates an exempt quote from a refused one is a property of
    the line, not of the fence around it.** Section 9 exempts a quote
    another language needs, which a reader tells apart by the fence a
    line sits in. A pattern cannot: Python's `re` takes a look-behind
    only at a fixed width, so a pygrep matching across lines has to
    consume the file from its start, and it then names the first line
    and prints everything up to the match — a verdict carrying no
    location. Both exemptions are read off the line instead. No shell
    puts a space around an assignment's `=`, `x = y` being the command
    `x` run with two arguments, so a spaced one belongs to another
    language and its value is that language's to quote; and a quote
    nested inside a quote of the other kind is a nested program's.

    **What it cannot see** is three things, each of them the price of
    reading one line at a time, and two of them over-reports rather than
    misses. An array written one element to a line: no element line
    carries the assignment that exempts a value, so the elements are
    reported and the rule does not reach them. A program in another
    language written across two lines: the quote that makes the
    placeholder that language's sits on the line above, so what section
    9 exempts by name is reported. And a placeholder that shares its
    line with an earlier quote of its own kind, an apostrophe in the
    prose or a second argument alike: the pattern crosses a quoted run
    of the *other* kind to reach a placeholder and stops at one of the
    same, so that line goes unreported.

    Widening for either of the first two wants a match that spans lines,
    which costs what is measured above: pygrep matching at once names the
    file's first line and prints everything up to the match.

    **What a reader meeting the second of those does** — the report
    being right about the line and wrong about the rule — is rewrite the
    line rather than waive the hook. The value the reader supplies goes
    into an assignment block above the fence and the program carries
    `${name:?}`, which is what section 9's *The fence a split leaves
    below is live* already asks of the lower fence and the shape
    section 3's `uv_build` read is written in. Reflowing the program
    onto one line is the other answer available and it is declined:
    what decides whether it fits is 80 columns rather than the reading,
    and a program too long for one line has nowhere left to go.

    Measured before it was proposed: this tree is clean under the hook
    and no other repository of the organization is, so unlike the two
    hooks above it costs each tree a pass over its own prose before that
    tree can carry it.

## 5. ruff

```toml
[tool.ruff.lint]
preview = true
explicit-preview-rules = true
```

The pair is what lets a rule be named in `ignore` — itself a preview
feature — without turning on everything ruff is still designing. A
preview rule then runs only where `extend-select` names it exactly.

- **`select = ["ALL"]`.** Every rule family ruff ships, present ones and
  a release's future ones alike, rather than a hand-picked list: a list
  is a thing that rots, since nothing forces a second edit here the day
  ruff ships a family nobody has looked at yet. `ALL` takes a new family
  in on the pull request that bumps ruff's own pinned rev instead, which
  is the day somebody is already looking at what changed. The rejected
  alternative is the hand-picked list this key held before: each family
  named and commented here, and each later addition remembered by
  whoever next opened this file rather than arriving on its own.
- **`ignore` holds three kinds of entry, told apart by what its comment
  argues.** A rule the formatter conflicts with, cited from ruff's own
  `docs/formatter.md` and not argued here, since the list is the
  vendor's and does not change with this tree. A rule this tree declines
  on its own merits, argued in the comment beside it —
  `undocumented-magic-method` and `undocumented-public-init` below are
  two, and `TD`'s own rules further down are a third. And a finding that
  is real and is simply not in `ignore` at all: fixed, or answered with a
  `# noqa` and a reason at its own site, which `RUF100` retires the day
  nothing needs it.
- **`ignore` names rules, never codes.** The reason sits in the comment
  and the rule sits in the entry, with nothing to look up between them.
- **`FIX` runs and `TD` is in `ignore`.** Unfinished work belongs in an
  issue, where it can be searched, assigned and closed; a marker in a
  comment is a backlog nobody queries, sitting beside code that reads as
  finished. `FIX` refuses four of them — `TODO`, `FIXME`, `XXX` and
  `HACK` — wherever one opens a comment, on its own line or after code.
  `TD` disciplines the format of the first three and is not even a
  superset of what `FIX` refuses — `HACK` draws no `TD` diagnostic at
  all — and where the two do overlap they disagree rather than agree:
  `TD001` steers a refused `FIXME` toward `TODO`, which `FIX002` refuses
  just as hard. A repository that finishes what it starts keeps the
  refusal, and `TD`'s own rules in `ignore` are where `ALL` is told so.
  The rejected alternative is ignoring `FIX` and keeping `TD003`
  instead, so a marker stands provided it carries a link to an issue —
  the mainstream choice, and a real argument in an organization whose
  mechanism is the issue tracker. Rejected because `TD003` checks that
  the link exists and never that the issue behind it is still open, so
  a marker outlives the issue it cites in silence, and section 15's
  audit does not enter a comment inside a `.py` file to catch it.
  What `FIX` does not read bounds what selecting it buys: a marker
  inside a docstring or a string literal is invisible to it, as is a
  mid-sentence mention that opens no comment, and a `TODO.md` at the
  root is the same defect in a file ruff never opens.
- **Docstrings are gated**: the `D` family with `convention = "pep257"`, every
  public module, class, method and function carrying one. `__init__` and the
  magic methods are the two exemptions pep257 itself does not ask for, and the
  `ignore` entry is the whole of each: the convention leaves
  `undocumented-public-init` and `undocumented-magic-method` enabled, so a tree
  naming neither is asked for a docstring at every such site. A magic method is
  documented by the data model it implements, so a docstring on `__repr__`
  saying it returns `repr(self)` is the restatement section 9's *One fact in one
  place* argues against. `undocumented-public-init` is declined for a different
  reason: the rule checks that a docstring exists, never that it says anything,
  and the cheapest line that satisfies it restates what the constructor's own
  annotations and strict mypy already carry. PEP 257 places the constructor's
  documentation in `__init__`'s own docstring, so declining the rule declines
  that presence check, not the documentation — an argument's meaning, a raised
  exception, an invariant the constructor establishes still has nowhere else to
  go. Both entries are the default, and declining one is not drift: the rule is
  then answered with a docstring, or with a `# noqa` that `RUF100` retires as
  soon as one arrives. Requiring them of every tree was the alternative,
  rejected because it asks a tree to drop a gate it passes. The convention is
  also what settles the pairs ruff calls incompatible, so `ignore` does not name
  the half it disables: beside a declared convention that entry changes no
  diagnostic and silences no warning. The warning ruff prints over such a pair
  appears only where nothing has settled it.
- **Code and prose have separate widths, and both are enforced**:
  `ruff-format` reflows code to 88, and
  `[tool.ruff.lint.pycodestyle] max-doc-length = 80` holds the
  docstrings and whole-line comments — prose the formatter never
  reflows — to the width markdown is already held to. A comment ending
  in a URL is exempt on a condition, and one following code on its line
  is outside the key: section 9 states both, with the reason — as it
  states what a tree keeping `line-too-long` reports such a comment at,
  the same table naming that width. `W505` is the rule that reads the
  key and is inert without it, ruff having no default doc length: a
  tree naming no `max-doc-length` states a width and enforces none,
  `select` aside.
- **`max-complexity = 10`**, ruff's default, with a `# noqa` and a reason
  at each site over it rather than a global bound at the tree's worst.
  `RUF100` then fails the noqa as unused the moment a refactor brings the
  function under the line, so the list can only shrink.
- **The copyright notice is a ruff rule**, `CPY` with a `notice-rgx`
  that is `COPYRIGHT` transcribed: each line with its regex
  metacharacters escaped, the lines joined by `\n`, the whole anchored
  with `^`, so that a source file opens with the file's text and not
  with a line resembling it. The rule rather than the copyright-notice
  hook, which checks only staged files unless given `--enforce-all` and
  so checks nothing under `--all-files`.

    **ruff reads the regex and never the file**, so the transcription is
    a copy that can drift from its source with every gate green: `CPY`
    checks the headers against the regex, and nothing in the tree checks
    the regex against `COPYRIGHT`. `tests/copyright_test.py` of this
    repository does, deriving the regex from each tree's `COPYRIGHT` and
    refusing one that is not it byte for byte — one spelling rather than
    any regex that matches, so that the copies are comparable and a
    drifted one names its own difference.
- **`per-file-ignores`** covers `__init__.py` re-exports and the test
  tree's `assert`, non-cryptographic `random` and the pytest-style rules
  a test legitimately trips. The `D` rules are **not** among them: a
  public test function states what it verifies.

## 6. The code is typed, and mypy is strict

**Every function declares the types of its parameters and of what it
returns**, and `strict = true` is what refuses one that does not. The
obligation and the setting are one rule and not two: without it an
unannotated `def` is not the absence of a claim but the widest one —
mypy takes every parameter and the return as `Any`, leaves the body
unchecked, and hands each caller back `Any` — so a bare signature
loosens the code around it and not only itself.

```toml
[tool.mypy]
strict = true
warn_unreachable = true
python_version = "<the requires-python floor>"
show_column_numbers = true
enable_error_code = [
    "deprecated",
    "exhaustive-match",
    "explicit-override",
    "ignore-without-code",
    "mutable-override",
    "possibly-undefined",
    "redundant-expr",
    "redundant-self",
    "truthy-bool",
    "truthy-iterable",
    "unimported-reveal",
    "unused-awaitable",
]
```

**The setting is not narrowed.** Not a lower one while the annotations
are caught up on, and not an override switching a strict flag off for
the directory that fails it: either leaves `[tool.mypy]` stating a
strictness the tree does not have, which is the one thing a reader of
that table takes from it. Nor is the same bundle enumerated flag by
flag in its place: that table is honest — it states exactly the severity
the tree has, rather than overstating it — and it is still not this
rule, because what is required is the strictness and a trajectory
toward it is not the strictness. `strict = true` tells a reader that
every function in the tree declares its types; a subset of the flags
tells them which checks it passes, and leaves what is annotated to be
read tree by tree. Where a single line genuinely cannot be typed the
answer is at that line and never in this table, the
`# type: ignore[code]` below being it.

**Configured is not enforced, and this section asks for both.** The
rule is met where the lint gate runs mypy over the tree, so a
`[tool.mypy]` no hook reads sets a severity rather than applying one —
a repository can hold every line above and have nothing that has ever
type checked it. Which hook runs it, and the shapes it comes in, is
section 4's, and this points there rather than restating them.

`strict = true` is the floor, not the ceiling, and the codes above are
the ceiling: **the same list in every tree**, not a survey each one
runs for itself, because a code that finds nothing today is a ratchet —
what it catches is the line written after the survey, and a tree that
skipped it finds out later than the others. Among them
`ignore-without-code`, so a `type: ignore` names the rule it silences and
a blanket one cannot creep in; `deprecated`, which is the early warning
`filterwarnings = ["error"]` buys at runtime; and `redundant-expr`,
`possibly-undefined` and `warn_unreachable`, each of which finds the
runtime guard whose static type promises more than an untrusted source
can. A code mypy enables on its own under the version the lock pins is
not in the list, and a key already at the value the block would give it
is not in the block: naming either states a check it does not buy.
`mypy --help` writes the flag that changes a default and gives the
default direction as its inverse, so a setting reachable only as an
inverse — `--show-error-codes`, under `--hide-error-codes` — is one
mypy has already.

A site that needs any of this relaxed — a check, never the annotation
itself — carries its own `# type: ignore[code]`, never a second global
exemption.

**Scope is the package, the tests and `.github/scripts`.** A test whose
subject is a script under `.github/scripts` loads it by path, that
directory being no package, so the type check is what reads a script
before it runs whether or not one was written for it.

**`docs/source/conf.py` is outside it.** Sphinx is the `docs` group's
and no shape of section 4's mypy hook installs it, so what that file
imports is unresolved in the hook's environment, which strict mode
reports rather than reading as `Any`; and `python_version` is one value
for the whole table — mypy takes no per-module version — so the file
would be checked at the floor the library declares and never runs on.
Every documentation build executes `conf.py`, so a defect in it reaches
the published site with the gate green: a repository that brings the
file into scope answers the version question first, and that answer is
its own.

One run, at the floor. A second pass at the newest interpreter would
check the same code where no source is conditional on the version.

## 7. Tests

### Layout and naming

- `tests/` mirrors the package, directory for directory — or
  `tests/unit/` does, where the suite splits by kind under *Functional
  tests* below.
- **`*_test.py`**, enforced by `name-tests-test` at its default. What
  the hook is for is the file named neither way: pytest's `python_files`
  collects `test_*.py` and `*_test.py` alike, and a file named outside
  both is not a red test but no test, nothing but the report's count
  moving. Between the two, one is the organization's, for
  `local-link-prefix`'s reason — one spelling is what lets a check
  downstream key on one pattern — and the hook's default is which.
- Shared test code lives in a package `__init__.py` — vector loaders,
  helpers — never in a module whose name says "test" and holds none.
- `tests/_data/` holds the data the suite reads, under the rule below.

### pytest configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --cov --durations=8 --strict-config --strict-markers"
# and, where the suite is long enough for the pool to pay for itself,
# "-n auto --dist worksteal" in the same string
xfail_strict = true
filterwarnings = ["error"]
markers = [...]
```

- **`--strict-config` and `--strict-markers`**: a typo in this table, or
  a marker nobody registered, is an error. That is what turns a
  misspelled `skipif` into a failure instead of a test that silently
  stops skipping.
- **`filterwarnings = ["error"]`, with no blanket ignore.** A deprecation
  warning is the early form of a break; on a spread from the floor to the
  newest interpreter there is time to act on it only if it is not silent.
  An ignore added here names the warning and says what would let it go.
- **`xfail_strict`**: a test expected to fail that passes is a fixed bug
  still marked broken.
- **`--cov` in addopts, and never as the last token.** `--cov` takes an
  optional value, so last it swallows the first path the command line
  gives — a whole-suite run measuring nothing, reporting zero, against a
  threshold of 100.
- **`-n auto --dist worksteal`** where the suite is long enough for the
  pool to pay, measured on CI rather than on a laptop; `worksteal` where
  the cost is lopsided, since `load` hands the queue out in chunks and a
  worker that draws several slow cases finishes long after the others. A
  short suite removes the flag, and the criterion is the length of a CI
  cell rather than the count of its tests.
- **`pytest-randomly` is installed and needs no flag.** It shuffles and
  prints the seed, which guards the one thing a green suite cannot tell
  you about itself: whether a test passes because of what ran before it.
  `-p no:randomly` puts the file order back when a failure has to be
  reproduced. A suite that declines the shuffle declares it in
  `tests/README.md`, with the reason, weighed against what the plugin
  catches rather than against what it costs — and an ordering plugin is
  not that reason by itself: a sequence two tests need can live inside
  one test, where a plugin-imposed order makes the dependence invisible
  at the call site.
- **A suite that waits on anything outside its own process carries a
  measured per-test timeout.** A hang is the one failure a suite cannot
  report on itself: the run stops rather than fails, and what a reader
  gets is a cancelled job at the workflow's `timeout-minutes`, naming
  the job rather than the test — that bound is a wedged runner's, and a
  per-test bound is what names a wedged test. So a suite that starts a
  process, opens a socket or waits on a deadline sets pytest-timeout's
  `timeout`, the bound measured against its own slowest test on a loaded
  machine and the measurement written beside the number, the number
  itself never being portable: what travels is the rule and the way it
  was measured. A suite of pure functions does not owe one — a limit
  nothing approaches costs a plugin and a number to keep true, and buys
  nothing.
- **No `slow` marker unless a measurement earns one.** A plain run is the
  run that has looked at everything, and the file a `-m "not slow"` loop
  would skip is usually the one worth keeping.
- **The suite writes nothing**, and runs from a read-only checkout and
  from an unpacked sdist.

### Anything generated is checked against its source

A committed artifact that something else derives — a serialized form, a
rendered page, a table — is re-derived by the gate and compared, so a
change to it is a failure rather than something to notice in a diff.
Regeneration is opt-in and the failure message names the command:

```shell
BTCLIB_REGENERATE_GOLDEN=1 uv run pytest
```

Where the comparison is a test, this is a golden file: a module compares
`to_dict()` against the json committed beside it. Where it is a page or
a document, it is a hook with a `--check` flag instead — and that hook is
worth writing `language: python`, stdlib-only and `always_run: true`, so
it runs on pre-commit.ci as well, where `uv` is absent. `always_run`
rather than a `files:` pattern, because an artifact goes stale from an
edit to any of its inputs, and a pattern narrow enough to name them all
is a pattern that stops matching one day.

### Test data is vendored, never fetched

Every file a test reads is committed beside it. A suite that fetches its
input has a verdict that depends on somebody else's uptime, and one that
cannot run offline cannot run in a sandbox either — so the data is in the
tree.

**Two kinds of file, and only one of them can be pinned.** A *vendored
upstream file* is a copy of a file that exists in somebody else's
repository: a commit and a git blob SHA-1 identify the original, so
whether the copy still matches it is a question with an answer.
*Recorded or constructed data* is written from a project's source rather
than copied from it — a reply built the way the code that sends it builds
one, values transcribed from a specification that publishes no file — so
there is no upstream blob and nothing for a pin to name, and the entry
says instead which source it was written from and how a reader
reproduces it. A rule conflating the two asks a repository for a pin that
cannot exist, or lets a copy go unchecked among files that cannot be.
What the tree derives from its own code is neither, and the subsection
above has it.

**A data directory beside whatever reads it**, which is `tests/_data/`
where the suite is the only reader and a directory beside the package or
the script where it is not. The underscore is `tests/_data/`'s alone. It
says the directory is not a package — it holds no `__init__.py`, nothing
imports it, and the way in is a path built from `__file__`, the mark the
language already puts on a private module, applied where it is literally
true — and that reason does its work inside `tests/`, where a sibling of
`tests/__init__.py` would otherwise read as importable. At the repository
root nothing is a package, so the mark buys nothing there and the
directory takes the name that says what it holds, the way in built from
`__file__` either way.

**The pins are one `README.md` in that directory**, covering every
`_data` directory the suite reads rather than one file per directory,
with an entry per file headed by its path:

```text
repo    <owner/repo>
path    <the path in that repository>
commit  <the commit pinned to>  <its date>
blob    <the git blob SHA-1 compared>
pulled  <the date this content entered this tree>
behind  <revisions of that path since the pin>
```

`blob` is the git blob SHA-1 rather than a digest of the bytes, because
it is what a tree entry already carries: nothing has to be downloaded to
compare against, `git hash-object` reproduces it locally, and a digest
answers whether the copy changed here and never whether upstream moved.
`pulled` is the date the current content entered this tree, which
`git log --follow --diff-filter=A` answers and nobody's memory does;
`behind` counts upstream revisions of the path since the pin, which is
staleness rather than a defect, taking a newer revision being a decision.
Under the block a verdict says how the copy stands to that blob —
identical, identical but for what a fixer in the gate rewrote, or
transcribed where the upstream is prose and there is no blob to compare
at all. A fixer that would rewrite those bytes for nothing is excluded
from the directory, a reformat voiding the pin and the verdict together.

**A repository with vendored upstream files runs `vendored-vectors`**,
which re-checks every pin on section 10's schedule and opens an issue on
drift rather than refreshing anything. One whose data is all recorded
says so where the workflow would be, an absent check otherwise reading
as an omission.

A vector the tree fails is vendored anyway and marked `xfail`, never left
out — an absent vector hides the defect it would have shown, and
`xfail_strict` turns the marker red the day the defect is fixed. A
licence travels with what it covers: where upstream ships one beside the
file, the copy takes it too, under a name that cannot be read as
licensing the directory around it.

### A capability the platform may refuse is asked for inside a guard

The call that asks for it sits in a `try`, and the refusal becomes a
`pytest.skip` naming what refused, which this section's `-ra` reports.
Creating a symlink is the case the family carries: on Windows an account
without `SeCreateSymbolicLinkPrivilege` gets an `OSError` from
`os.symlink` rather than a link, which CPython records in
`Lib/tarfile.py` where it names the exceptions that call may raise. What
the guard is for is a contributor's own machine and not a runner — a
runner holding the privilege runs the case either way, so its green cell
answers for the gate rather than for that machine. The `except` runs
only where the refusal happened, which is not the machine the floor is
measured on, so it carries section 8's `pragma: no cover` with the
inline half that section asks for, and the fuller reason is the
docstring the case already opens with. Leaving the call bare is the
rejected alternative, on the ground that no runner has refused it; what
it costs is a red suite on the one machine that cannot run the case at
all, naming a privilege where the case is about something else.

### Integration tests

`tests/integration/` is whatever needs something the repository does not
ship — a node, a device, an emulator. Each test skips itself without the
environment switch that asks for it, the switch is named in the skip
message, and the directory is omitted from the coverage ratchet: a body
that skips itself would be an uncovered line at every commit rather than
a defect. What covers them is an unattended job, and that job fails if
its tests skipped rather than ran.

### Functional tests

`tests/functional/` sits beside `integration/` where a suite's subject
is a running process rather than a module: a test that starts what the
repository ships and drives it over a port has no module to sit beside,
so the mirror has no place for it. The terms keep the concession from
becoming a place to put anything. `tests/unit/` then carries the mirror,
and nothing moves out of it to escape a rule; every directory is in
`testpaths`, so a bare run is still the whole suite; and the split is
declared in `tests/README.md` with its reason, this section's own rule
for a convention only prose states. The two directories are told apart
by what they need rather than by how long they take: `integration/`
needs something the repository does not ship, `functional/` needs
nothing it does not — it starts the thing itself. The rejected
alternative is flattening, which moves the record of which tests hold a
port into a marker or a naming convention, the same fact kept where a
`testpaths` entry cannot see it.

### Property tests

A tree that has the property section 10's `fuzz` entry keys on owes a
property layer, whether or not that section's record gives it the
sentinel. The rejected alternative keys the layer on the record instead,
and what it costs is a tree getting the cheap half only by being given
the expensive one: a property layer is code in the suite that runs with
everything else, where a fuzzer is a scheduled runner with a harness and
a corpus. The two answer different questions and neither substitutes for
the other: a property test answers *does this hold over the domain I
described*, a fuzzer answers *what is in the domain I did not describe*
— and the second presupposes the first, a fuzzer extending no described
domain having nothing to contradict. hypothesis is the named shape, its
profiles registered once in `tests/conftest.py` rather than repeated on
every `@given`:

```python
settings.register_profile("default", deadline=None, max_examples=500)
settings.register_profile("thorough", deadline=None, max_examples=2_000)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "default"))
```

`deadline=None`, because a per-example time limit is a timing flake on
whichever cell of the matrix is slowest; the default example count set
where a measurement of its cost on the whole suite says it is
affordable; and the deep profile opt-in, because the search that finds a
latent defect is not a search to run at every commit — and what it finds
graduates into a vector test rather than staying in a search that may
not repeat it. A tree that answers the property with hand-rolled
properties over the same domain declares that in `tests/README.md`,
where the reader meets it. A suite whose subject is a measurement rather
than a parser does not owe the layer: generated inputs to a timing are
the shape the tool is worst at.

### Convention tests

The distinguishing feature of the suite, and the part an older repository
is most likely to lack. A convention that only prose states is a
convention that drifts; each of these turns one into a red test, and none
of them carries an exemption list that is allowed to grow:

- **the public surface** — `__all__` is declared by every module and
  package at every depth, a module under a private name excepted as no
  part of that surface, and a census walks the tree rather than listing
  it, so a new public name fails until it is exported or recorded. A
  module declaring none answers `import *` with every name it does not
  underscore, the ones it imported included, so what a caller may rely
  on is settled by an import list. Where the package is published this
  is not a bullet the clause below excuses: `py.typed` says the types
  are supported, and which names are public is the other half of that
  sentence;
- **the copyright header** — `LICENSE`, `__copyright__` and the project
  metadata checked *together*, each having drifted alone before;
- **the documentation** — every shipped module appears in the sphinx
  pages, hand-written pages inviting exactly that drift;
- **the import graph** — every module importable first, with nothing else
  in `sys.modules`, which is the only way a one-directional cycle shows
  up;
- **the changelog** — neither history file may state a count of itself,
  a number nothing derives being right or wrong invisibly;
- **the build system** — nothing but the declared backend runs while a
  distribution is built;
- **the calling convention** — keyword-only parameters stay keyword-only,
  private functions carry no default, and a name's prefix promises what
  the call answers;
- **input validation** — every public function refuses what it does not
  declare, driven by a walk over the public surface rather than by a
  hand-written list;
- **the suite opens no socket** — every construction that could reach the
  network carries the argument that keeps it hermetic, driven by a walk
  over the call sites rather than a fixed list of them, so a
  construction that forgot the argument is what turns red instead of a
  test that passes offline and fails the day it is not.

A new repository does not need all of these. It needs the ones its own
conventions state in prose, and the rule that a convention worth stating
is worth a test — the public surface excepted, which a repository
publishing an importable package has whether its prose states it or not.

**Which of them a repository implements is declared, not inferred.**
`tests/README.md` names each bullet above that this repository tests and
the module that tests it, and a test in the same suite asserts that
declaration is true — the rule one paragraph up, applied to this section
itself, and it is forced rather than chosen. The suites do not agree on
names and are right not to: a package of many modules wants a module per
bullet, where a package that is one module folds several of these checks
into the one file that is about it, which is the honest shape for it.
And this section's own escape clause, wherever it reaches, makes an
*absent* convention test indistinguishable from a convention the
repository does not have. A declaration is what tells those two apart; a
`grep` over `tests/` cannot, which is why the audit below reads the
declarations.

**A convention test moves with the code it walks.** These tests walk a
package: a module carved out into a repository of its own stops being
walked the moment it leaves, and the receiving tree either takes the
test or drops the convention with nothing red anywhere. So when code
moves between repositories, the convention tests that covered it are
part of what moves, and both `tests/README.md` files change in the same
pair of pull requests. What must *not* be aligned is where those tests
live or what they are called — only which conventions are tested, and
that each tree says which.

## 8. Coverage at 100%

**A tree gates the code it holds against the failure that code has**, and
the coverage floor below is one such gate rather than the whole rule. A
package that installs is measured by that floor. Course material is
measured by whether it still runs on the dependencies pinned today: what
breaks a demonstration script is a release underneath it renaming what it
imports, and a floor over code nothing executes measures nothing. A suite
whose subject is outside its own tree is itself the gate rather than
something with one — `.github`'s suite runs against the other
repositories, so a floor here would be the instrument measuring itself.

Which of them applies is read off what the tree installs. A tree that
installs no package owes no floor, that rule having no subject there,
which is section 2's sentence for a rule whose subject a tree does not
hold; what it owes instead is the gate its own material's failure asks
for, in the workflow a reader already goes to for what runs that
material. That is a different axis from section 2's rule that the
package directory, `tests/` and `docs/source/` name a package as their
subject: that one says which directories a tree owes, this one what
gates the code it does hold.

```toml
[tool.coverage.run]
source = ["<package>", "tests"]
omit = ["*/site-packages/*", "tests/integration/*"]
branch = true

[tool.coverage.report]
show_missing = true
skip_covered = true
precision = 2
exclude_also = [...]
fail_under = 100.0
```

- **The tests are measured too.** A test nothing runs is dead code with
  the authority of a test.
- **`branch = true`.** The interesting miss is a wrapper's guard clause,
  and statement coverage alone calls a half-tested `if` fully covered:
  the line ran, one of its two ways out never did. The gate is 100% of
  statements *and* branches, and the second half is where a refusal
  nobody exercised shows up.
- **`exclude_also` where the unreachable thing is one shape repeated.**
  A failure no input can provoke — a `raise RuntimeError` behind a call
  that cannot fail — is excluded once, by pattern, rather than carrying
  a `pragma: no cover` at every site. What is left is a number only
  untested code can lower. A pattern that would also exclude something a
  test can reach is not one of these: for a one-off, the pragma is still
  the answer, in the shape *What it costs is paid at the site* below
  gives it.
- **`source` is named, never left to `--cov` alone.** Unnamed, it measures
  every file the run imports, which reaches a script a test imports by
  path — uncovered, because nothing runs its `main()` but a subprocess.
  A local gate stricter than the CI one it exists to reproduce is the
  worse of the two directions.
- **100 is not the same rule with the bar raised.** coverage special-cases
  the value: nothing short of an exact 100.00% passes, where 99.99 passed
  everything above 99.985%. It also makes the report agree with the exit
  code, which a threshold inside the rounding step does not — a run can
  print `FAIL` and exit zero.
- **What it costs is paid at the site**: a line no ordinary run reaches is
  covered by patching what stands in the way, or carries a
  `pragma: no cover` with its reason. Neither is a build left red.

  **The reason goes on the pragma's own line, after ` -- `** — the dash
  a comment writes, an em dash being this file's own. What the position
  buys is that

  ```shell
  git grep -nE 'pragma: no cover$' -- '*.py'
  ```

  answers empty in a tree that keeps the rule, so every line it names is
  a site short of the inline half — a defect under this rule whether or
  not a reason for it is written somewhere else. ` - ` is the rejected
  alternative, and what it costs is a hyphen where a dash was meant, and
  a check written for one spelling answering a confident zero for a tree
  that writes the other, which is what

  ```shell
  git grep -nE 'pragma: no cover - [^-]' -- '*.py'
  ```

  is for.

  **A reason too long for the line goes above it as well, the inline
  half naming the case.** `btclib-node`'s `[tool.coverage.report]`
  comment is where the family already writes this, and it is what keeps
  the grep above a gate rather than a census. The fuller reason is the
  comment over the line, or the docstring the file or the function
  already opens with where one reason covers every pragma under it —
  written once there rather than copied per line, while each line goes
  on carrying the case it is.

  Letting the fuller reason **replace** the inline half is the rejected
  alternative, and what it costs is the gate: a conforming tree would
  then answer the grep non-empty, so the command would name its
  conforming sites and its reasonless ones together and telling them
  apart would be a reading. Section 14's *decided per repository* list
  was the other alternative, and it is declined: that list takes a
  reason true of the repository, and how much a reason has to say is a
  property of the line being excluded rather than of the tree holding
  it.
- **Measured on one interpreter**, the one `.python-version` pins, which
  is enough at 100 only because no source branches on the version — a
  percentage below 100 could not promise that, the statement count moving
  between versions.
- **The flags live in `pyproject.toml`, and a job types `pytest` with
  nothing after it.** `addopts` carries the coverage flags,
  `[tool.coverage.report]` the floor and the report options, and a copy
  typed into a workflow is a copy a maintainer never runs, so the local
  gate and the CI gate stop being the same measurement with nothing
  turning red. Two arguments are a job's own rather than second copies:
  the `--no-cov` a platform sentinel passes, and the `COVERAGE_FILE` of
  a job that combines runs.
- **The configuration is read from wherever the run starts.** coverage
  looks for its configuration in the directory the process started in,
  so a suite run from `tests/` finds no `source`, no `branch = true`
  and no `fail_under`: it measures a different set of files and exits 0
  whatever the number is. A tree with a local floor either points the
  run at its configuration from wherever it starts, or makes such a run
  say it is ungated rather than letting it pass as the gate — and
  which of the two a tree does is measured on that tree, the pair of
  runs from the root and from `tests/` being the measurement.
- **A selective run is reported and not gated.** `fail_under` applies to
  every report coverage writes, so `pytest tests/foo` would fail on the
  tree's coverage rather than its own. A `conftest.py` hook drops the
  threshold when the invocation asks for something other than the whole
  suite — paths, `-k`, `-m`, `--deselect`, `--ignore`, `--ignore-glob`,
  `--lf` — and never overrules an explicit `--cov-fail-under`. A path is
  a selection only where it leaves a `testpaths` entry out, rather than
  wherever one is named: `pytest tests` is what a bare run already
  collects, so a hook reading any path as a subset switches the floor
  off for the run that is the suite. The paths are
  `config.option.file_or_dir`, which is `None` and not `[]` under
  `--help` — the parse being abandoned before the positional is
  consumed — so a containment test that iterates it ends `--help` in a
  traceback. Setting the threshold means writing to
  `config.known_args_namespace`: pytest-cov reads that copy and never
  `config.option`, so the obvious spelling fails silently.

  A run that leaves tests out measures the same source with fewer tests,
  so what its report is short of is the tests it did not run: a
  shortfall it reports cannot be told apart from one the tree has, and a
  gate whose red cannot be read is what teaches whoever runs it to reach
  for `--no-cov`.
  The narrower reading — paths, `-k` and `-m` alone — is rejected: it
  holds the rest to be the flags of an iteration whose next run is the
  whole suite, and reading intent off all of them to make the hook a
  second definition of what a real run is. What the wider set costs is
  the occasion where such a run would have cleared 100 anyway — a `--lf`
  that finds nothing to rerun and so is the whole suite, a `--deselect`
  of one arm of a parametrization the others cover — and the next bare
  run measures the tree again. An early `-x` is outside the set either
  way: what cuts that run short is a failure and not what the invocation
  asked for.
- **Where an optional native dependency splits the code**, coverage is
  measured twice — with it and without — and the *union* is gated at 100
  beside the delegated run's own gate, not instead of it, so a line
  covered only by the fallback run cannot pass in silence. The two runs
  name their data files with `COVERAGE_FILE`, or they overwrite each
  other in the job that combines them.
- No coveralls, no third-party upload, no secret: a local threshold
  enforced on every run instead of on pull requests only.

## 9. Prose, comments and docstrings

Nothing checks prose the way the suite checks code, so every line of it
is one a later change can falsify in silence. That is what its length is
weighed against, and what lengthens it without adding to it is deleted on
sight rather than weighed.

- **Tone: neutral, factual, dry.** Explanatory detail is wanted;
  decoration is not, and the sentence that only introduces the next one
  is decoration.
- **A docstring states the contract** — what the call takes, what it
  returns or raises, and the rule the behaviour comes from. Not a
  restatement of the name.
- **A comment carries the reasoning, including the negative result** —
  why the code is as it is, and why *not* the obvious alternative. The
  second half is what stops the next reader from "fixing" a deliberate
  choice, and it is what makes a configuration file reviewable rather
  than merely readable. The negative result is the rejected alternative
  and what rejects it, and the tour of the others is not part of it.
- **Cite the authority.** Where behaviour comes from a standard, name it;
  where the project deviates, say so and say why.
- **Measure, don't assert.** A number in prose comes from a command, and
  the command belongs beside it. Never state a count that nothing checks,
  and never state how many of anything a file holds: a stated total is a
  line every open branch has to edit, and two branches moving it to the
  same wrong number merge without a conflict.
- **A measurement's quantifier is not the sentence's.** The bullet above
  is satisfied by a command that ran and a number that is right, and a
  sentence saying *every*, *the only*, *none* or *always* where the
  command asked about one instance claims more than the command beside
  it answers. So the reading is two questions in order: what the
  measurement covers, and what the sentence it licensed claims. Where
  the second is the wider, either the measurement widens or the sentence
  narrows, a universal owing a hunted counterexample.
  `btclib-org/btclib`'s `40e75d87` is the narrow form: its entry holds a
  chaininfo reply, a block hash and a header each `to the size their
  endpoint answers rather than to something wider`, and the same bullet
  says what makes the narrower claim measurable — `A reply one octet
  over the limit is refused with that limit in the message, and the
  recorded answer inside it is accepted`, a check on each side of the
  bound. The reader-side form is the one with a
  shape on the page: a sentence about a mechanism names the command that
  would falsify it. A quantifier too wide is invisible in prose and a
  missing command name is not, so the second is how a reader finds the
  first.
- **A control the same fault silences is not a control.** *Measure,
  don't assert* and the bullet above ask that a number come from a
  command and that the sentence claim no more than the command answered;
  neither asks whether the command measured anything. An apparatus fails
  symmetrically where whatever silences the check silences the control
  with it — a pattern that matches nothing, a revision the shell
  mangled, a status read off the wrong process — and a control that
  differs from the check only in what it looks for is the one that fails
  that way, so the two agree and the agreement is what convinces. Name a
  control by the perturbation it applies rather than by the property it
  is hoped to prove, and put it where the answer already in hand is
  impossible: a revision that cannot hold the file, a file that cannot
  hold the string. Zero is not the tell. `git show` handed a mangled
  revision writes its complaint to stderr, so a count of its stdout is
  the zero a real absence gives and a count of the streams merged is a
  small plausible number. The rejected alternative writes this into each
  repository's `CLAUDE.md`, among the failure modes a session meets
  there; what it costs is a copy per repository of one fact, and the
  reader it reaches is whoever works in a tree rather than whoever
  writes the sentence a measurement is for.
- **The guard goes into the instrument, not into the reader's
  recognition.** A rule applied where it is recognised is not applied at
  the site nobody looked at, so what survives is the form written
  unconditionally. A control runs unchained, `grep -c` exiting 1 on a
  count of zero so that `check && control` prints one number where two
  were due and never reaches the second. A parameter expansion a `:`
  follows is braced: `zsh` takes the character after an unbraced
  `$name:` as a modifier where it is one and consumes the pair, so
  `"$sha:AUTHORS.md"` asks `git` for a revision that does not exist
  where `"${sha}:AUTHORS.md"` asks for the file, and `:a`, `:A` and `:P`
  resolve what is left against the working directory. The trigger is
  literal text, which makes a path arriving in a variable immune by
  mechanism rather than by care. A status is read from the command
  rather than from a pipeline, `$?` after `cmd | head` being `head`'s.
  The rejected alternative writes down which characters bite; what it
  costs is a lookup at every use site, and the site that gets no lookup
  is the one the rule was for.
- **A reference derived from what it tests is not a reference.** A
  reconstruction is evidence while its inputs are independent of the
  subject, and one built out of the tip it is meant to check carries
  whatever damaged that tip, so the comparison exits 0 and reads exactly
  as a clean one does. The block comes from the blob before the
  operation, or the two sides come from different commits.
- **A placeholder standing as a whole argument is unquoted**, so that a
  paste made before it is filled in fails at the shell rather than
  reaching the tool. Quoting is what an argument holding spaces
  otherwise asks for, and it makes `<` and `>` ordinary text: the
  command runs, and the tool takes the placeholder as the value. What a
  bare one fails with is the bullet below, and what that failure leaves
  unguarded is the one after that. A placeholder *inside* a larger
  string is not this: `"repos/<org>/$r/contents/$1"` is quoted for the
  variable beside it, and unquoting it would be wrong shell rather than
  a guard. Nor is a quote another language needs — a `python -c`
  program's string, a TOML value. Nor is a `<...>` whose spelling is not
  a placeholder at all — an element name the command is looking for,
  `<title>` in a badge SVG being the instance. Such a token is a
  literal, and the unquoting repair is not available to it: what it
  takes instead is the exemption above, on purpose — inside a larger
  string carrying the neighbouring literal text the match needs,
  `grep -oE '<title>[^<]*</title>'` rather than `grep '<title>'` alone,
  the form section 15's own badge-render loop already writes. What
  decides is the token's neighbourhood, not its spelling: the same
  token is a genuine placeholder standing alone as a flag's whole
  argument elsewhere, where unquoting is exactly the right repair. The
  rejected alternative is a list of literals the rule exempts by name;
  what it costs is a ruling per line, on a page where nothing
  distinguishes a literal from a value — the larger-string form is
  visible in the fence itself, and it is the same test a reader already
  applies to `"repos/<org>/$r/contents/$1"`.
- **A bare placeholder goes at the end of its command**, where the `>`
  closing it has no target and the line is a parse error before it is a
  command. `<` and `>` are the shell's redirection operators, so a paste
  made before the placeholder is filled in is a pair of redirections
  wherever the placeholder sits; what the position decides is whether
  the line can run at all. Where a word follows the placeholder, `>`
  takes the word as its target and the line fails at run time on the `<`
  — `no such file or directory: org` — except in a reader's directory
  holding the placeholder's own name, where the `<` succeeds, the line
  runs, and the `>` writes one named for the word that follows. What
  decides is the direction of the open and not what the name holds: POSIX
  gives `open(2)` an `EISDIR` only where the flags ask to write or to
  execute, so the `<` opens for reading and succeeds on a directory as
  readily as on a file, and the `read(2)` that would fail is one the shell
  never performs. The rejected alternative names the two objects — a file
  or a directory — in place of the rule; what it costs is the `>` side,
  where a directory is what the open fails on, so the pair would read as
  taken back where the bullet reaches `/` rather than following from what
  is said here.
  A placeholder inside a path puts that word at the root of the filesystem:
  `orgs/<org>/installations` gives the `>` the target `/installations`, so
  the paste writes nothing in the directory the reader is standing in and a
  sweep that lists that directory reports the block as clean. A sweep of
  `/` reports the same on macOS, where `/` is read-only: the open of a name
  not already there answers `EROFS`, and the `>` creates nothing. That
  errno is the platform's answer measured rather than its page's: macOS's
  own `open(2)` gives `EROFS` for a file that resides on a read-only file
  system and is to be modified, and a name that is not there resides
  nowhere. The rejected alternative explains the reader's clean directory
  by the write having landed at the root; what it costs is a reader hunting
  at `/` for a file this platform does not write. `/` alone is not that
  case — the open fails, and one command's redirections are performed in
  order, so the `>` after it in `repos/<org>/<repo>` is never reached and
  that command writes nothing. What the open fails with on macOS is not the
  `EISDIR` above: a `>` asks to create as well as to write, and at `/` the
  errno names the create rather than the direction. macOS answers `EEXIST`,
  which its own `open(2)` gives only for `O_CREAT` with `O_EXCL`; a `>`
  sets `O_CREAT` alone, so the platform departs from its own page. `/.`
  names the same directory and answers `EISDIR`, so the answer belongs to
  the spelling and not to the directory it names. Neither errno decides
  anything here, the open failing under both. The rejected alternative
  leaves the general reason a directory gets; what it costs is a reader
  carrying the `EISDIR` above down onto the one target this sentence is
  about.
  A redirection that fails is the one command's rather than the line's,
  so the other side of a pipeline runs whatever it did:
  `git show v<version>:pyproject.toml | grep '^version'` reaches the
  `grep`. At the end of the line there is nothing for `>` to open, so
  the line writes nothing whatever the directory holds. Where the
  command's own shape refuses the position — `--with <version>` precedes
  what it measures, and an endpoint's path continues past `<org>` — the
  placeholder's line is a block of its own, with nothing under it for a
  paste that stops at the fence to reach; what that stopping rests on is
  the bullet below.
- **A line that writes goes in a fence of its own**, the parse error
  guarding only the line it sits on: an interactive shell answers it by
  discarding that line together with its trailing `&&` and reading the
  next as a fresh command, so the chain never forms and a write below it
  runs. The run-time failure is the one a trailing `&&` short-circuits,
  and that guard rests on the reader's directory rather than on the
  line. The fence rests on something of the reader's too — on their
  taking the one fence, which github.com affords by giving each its own
  copy button. A drag across the rendered passage is one paste instead,
  and what a shell makes of one paste is the bullet below.
- **What any of that is measured with is a paste into a terminal, and
  the shell decides how much of one paste is a command.** `zsh` takes a
  bracketed paste — what a terminal emulator wraps one in — as a single
  buffer and abandons all of it on the parse error, where `bash` and
  `sh` submit it a line at a time and reach the write with the markers
  present or absent. Feeding the block to a shell as a script measures
  something else, and not the same something for every shell: `zsh`
  reading it from stdin discards the parse error and carries on as an
  interactive shell does, where `-c` and a file abort. So a harness
  built on `cat block | zsh` reads as the aborting case and is the
  other one.
- **A fence with nothing in it that fails at the parse is live**,
  whether a split left it below another or nothing split it at all. A
  paste of it alone is a command and it runs with every value the reader
  was to set empty. A placeholder in it settles nothing: section 3's
  `uv_build` read carries `<outdir>` inside a `python -c` program's
  string, which the unquoting bullet above exempts, so what stops that
  line is its `${version:?}` rather than the placeholder. Where no split
  has left such a fence, the guard is what splits it: a placeholder that
  bullet exempts is text the line sends to the tool rather than a stop,
  so section 12's job listing, whose run id is quoted for the query
  string beside it, puts that id in an assignment block of its own above
  the fence and reads it from there. The fence writes each of those
  values as `${name:?}` and joins its lines with `&&`, and reads one of
  them at or above its first line that writes, a guard below that line
  arriving too late. Neither is the guard by itself: an interactive
  shell's `${name:?}` abandons the one command it stands in, so a line
  under it that reads nothing of the reader's runs anyway, and a chain
  with nothing failing in it runs to its end. Chained, a `${name:?}`
  failure is the run-time one the fence bullet above says a trailing
  `&&` short-circuits. Prose beside the fence says what `:?` is doing
  there, since a reader who is not told deletes it. Leaving such a line
  alone because the endpoint it names only reads is the rejected
  alternative: what a call does at the far end is not on the page, so
  that test is a ruling per line where the parse is something the fence
  shows.
- **A trailing `#` comment goes above the fence, as prose.** `zsh`
  leaves `INTERACTIVE_COMMENTS` unset, so an interactive one takes `#`
  as an ordinary word and what follows it as arguments to the command on
  that line. A chain whose `&&` is followed by a comment has its
  right-hand side on that same line, so it is complete where the file
  shows it continuing, and the lines under it start a chain of their
  own. An apostrophe in the comment opens a quote instead. A later
  apostrophe closes it, and the command runs with the lines between the
  two as a single argument, the lines past the second running as they
  were written. With none to close it the buffer ends unterminated, and
  neither that command nor the lines below it run. That stop is not a
  guard: nothing puts the apostrophe there for it, and the next
  rewording of the comment takes it away. The prose above the fence has
  the room a line beside a command does not. The same mechanism reaches
  a whole-line comment too: `#` is an ordinary word to an interactive
  `zsh` wherever it opens the line, not only where it follows `&&`, so
  an apostrophe among that line's own words opens the same unterminated
  quote and kills the fence beneath it. A backtick in such a comment is
  a command substitution to the same shell, and a paste attempts to run
  it. A whole-line `#` comment inside a fence carries neither an
  apostrophe nor a backtick, and one that needs either goes above the
  fence as prose beside the rest. What decides is not the first
  character being `#` — a word the shell fails to find and moves past —
  but what the rest of the line hands it, and that stop is no more a
  guard than the trailing case's: nothing puts the plain words there for
  it, and the next rewording can add the apostrophe. The rejected
  alternative moves every whole-line comment above the fence, as the
  trailing one goes; what it costs is every fence in the organization
  that carries one, for a shape that is harmless while it keeps to plain
  words, and a comment on a line of its own is where a reader finds why
  a flag is there. No gate reads this — a heading and a comment both
  begin with `#`, so a line-based hook cannot tell them apart — and that
  absence is a fence-aware runner's, not this bullet's.
- **One fact in one place.** Two files stating the same thing become two
  files disagreeing about it; the second points at the first.
- **A package upstream of another does not name the one downstream.**
  What a consumer of it reads has to stand on its own: the organization
  that publishes it and where it sits in the family are context, and
  everything else about a dependent is a cross-reference to a project
  that reader does not have.
- **A reference to another repository is qualified.** A bare `#123`
  resolves inside the repository it is written in, so a cross-repository
  reference is `owner/repo#123` or it points somewhere else in silence.
  The one exemption is mechanical: a pull request's closing keyword is
  read by the forge, so it takes the forge's own form.
- **No history in the prose.** Comments say why the code is as it is, in
  the present tense. History has two files of its own.
- **80 columns everywhere prose lives** — markdown by MD013, tables
  included; a Python docstring and a whole-line comment by ruff's
  `max-doc-length`; a toml comment by a pygrep hook. Code is 88, the
  width `ruff format` produces, and what reports a line past it is
  `line-too-long`, a rule each tree keeps or ignores; yaml is 100,
  because an action pinned to a commit SHA with its tag in a trailing
  comment is past 80 before anything else is said.

    **A Python comment following code on its line is outside the
    number**, and nothing holds it to that width: `max-doc-length`
    reaches a docstring and a whole-line comment and stops there, and
    `ruff format` does not rewrap one. What such a comment may use is
    whatever the code leaves, and a reason that will not fit goes into
    the comment above the line — for a `pragma: no cover`, above the
    inline half section 8 keeps rather than replaces.

    A gate is the rejected alternative rather than a missing one, and
    what it would buy is the number holding without anybody reading for
    it. What overflows is typically a `type: ignore`, a `noqa` or a
    pragma's inline half: the first two are a tool's own spelling and
    the third names which case the line is, so the only thing left to
    shorten is the code the comment sits after. And a line-oriented
    pattern reads a `#` inside a string as a comment, which no spelling
    of such a pattern fixes.

    **What holds a Python line to 88 is not the formatter alone.**
    `ruff format` counts a trailing comment in the line's width and
    splits the code to fit it where a split fits; where none does —
    the statement admitting no split, or the comment leaving nothing
    to split into — the line stays past 88, and that is the line left
    over. A tree keeping `line-too-long` reports it at the width
    `max-line-length` names, falling back to `line-length` — 88, the
    width this section already fixes — where that key is unset, and
    with no fix ruff can apply; a tree naming the rule in section 5's
    `ignore` measures it nowhere. Fixing the
    choice for every tree is the rejected alternative: what a line has
    to spare differs with the code on it, and section 5's `ignore` is
    already where a rule declined on its own merits is argued.

    `line-too-long` does not report every over-long line. Which lines it
    passes over and which pragmas it recognises are ruff's and move with
    ruff, so neither list is here; what is stated is what this
    standard's own decisions rest on. A line whose last word contains
    `://` is passed over where everything ahead of that word fits the
    width, which is the condition section 5 leaves here rather than
    wording it a second time. A pragma ruff recognises need not end the
    line: from it the rest goes unmeasured, so the width a finding
    names is the one ahead of it. That much is `preview`'s, which
    section 5 sets: without it the whole line is reported. A comment
    opening with such a pragma is passed over whichever way `preview`
    is set, by an exemption that is not this one. Each of these holds
    under `max-doc-length` too, at its own width. What section 8 needs
    is that `pragma: no cover` is outside the set ruff recognises, an
    inline half being measured like any other trailing comment.
- **A comment whose first word is `shellcheck` is a directive, so where a
  sentence wraps decides whether one gets written.** A wrap that puts the
  word there does so by accident, and what follows it on that line
  decides which failure it is: what the tool cannot parse as a directive
  is a parse error — `SC1072`, and a red gate — while a line that does
  read as a valid directive can be honoured, the run exiting 0 with a
  real finding suppressed by a sentence that was never about it. The
  second is the one the rule is for: a gate that passes having measured
  less than it appears to leaves nothing to notice. Any comment
  `shellcheck` reads is in scope, including the `run:` block section 10
  has `actionlint` hand it. Wrap so the word does not begin a line — the
  same sentence with it pulled up onto the line above is prose again.

### `CHANGELOG.md` and `RELEASE_NOTES.md`

- The changelog gets an entry for anything a user would notice. The
  release notes are what a user has to *act* on.
- **One fact each**: the breaking-changes list lives in the release
  notes and the detail behind it in the changelog, so neither restates
  the other.
- **Both are `merge=union` in `.gitattributes`.** Two branches each
  appending an entry at the same anchor conflict on the insertion point,
  which is a conflict with nothing to decide; union keeps both sides'
  added lines, on rebases included. Its price is that on a checkout the
  two files never conflict at all, so the *same* entry edited on two
  branches merges in silence — which is the second reason neither file
  states a count.
- **The driver is a checkout's, and the forge does not apply it**, so
  the price has a second half no local command predicts. A pull request
  whose `CHANGELOG.md` or `RELEASE_NOTES.md` overlaps its base is
  reported `CONFLICTING` however cleanly the same pair merges under the
  driver:

  ```shell
  git merge-tree --write-tree origin/main <branch>
  gh pr view --json mergeable --jq .mergeable <n>
  ```

  `UNKNOWN` from the second is the forge computing the merge rather than
  an answer, so it is asked again. A rebase on a checkout is what clears
  a `CONFLICTING`, and the driver applies during that rebase — so the
  silence above is a rebase's, and what the merge button lands never had
  the driver applied to it at all.
- **Union drops the blank line between two sections it joins.** Two
  branches each adding a `###` section under `## Unreleased` produce a
  file whose second heading sits against the bullet above it, which
  MD022 and MD032 both refuse. Section 4's autofix rule has
  `markdownlint-cli2` write the line back on the next hook run, rather
  than only reporting it missing.
- **A `###` names one entry, never a theme several entries share.** So
  the open section is the list of its entries, and the end of it is one
  place. Grouping by theme is the rejected alternative: nothing here
  says what the themes are, so each tree names its own set and an entry
  belonging to two of them has to pick one, and the append point becomes
  the theme's rather than the section's — which is the anchor the two
  bullets below are read against. Where an open section already carries
  theme headings, the next entry goes after them, at the end of the
  section, and nothing above it moves.
- **A new entry goes at the end of the open section**, after the entries
  already there and immediately above the heading of the latest released
  version — at the end of the file where the tree has released nothing.
  The union driver decides that rather than how the section reads: it
  joins two branches that appended at one anchor by placing the side
  arriving second below the side already there, so the entries end up in
  the order they landed in.
- **A rebase's result is read, because nothing else reads it.** `git
  rebase` exits 0, there is no conflict marker, and no gate reads the
  order two `###` sections sit in — only whether the blank line between
  them survived, which the union bullet above covers. The diff is what
  says the branch's own block is still at the end of the open section:

  ```shell
  git diff origin/main..HEAD -- CHANGELOG.md
  ```

  A block sitting anywhere else is moved back before pushing — *Nothing
  already written is rewritten* below is what turns leaving it there
  into a standing misplacement once it lands.
- **Newest first is the rejected alternative, and under it that same
  driver is silently wrong.** A branch that inserted at the top of the
  section comes back from its rebase sitting under a neighbour it was
  not written for, its text byte for byte what its author wrote and only
  the position changed: the diff reports an addition and counts no
  deletion. What newest first buys is a section a person reads as a
  timeline, and that is all it buys — the entries of a section that has
  not shipped are a set of changes rather than a sequence, and the
  release that closes the section gives it a version heading, after
  which their order answers nothing.
- **Putting the position on section 14's *decided per repository* list
  was the other alternative, and it is declined.** A tree whose entries
  land in both places has no reason of the kind that list takes, so an
  entry for it would record an accident as a decision.
- **An entry making several claims has a list for a body, and one making
  a single claim may have a paragraph.** What a list does is keep claims
  apart, and an entry making one has nothing to keep it apart from, so
  the marker is available to it rather than owed. The rejected
  alternative is a list whatever the entry holds: what it buys is one
  shape for every body, so that a reader looking for an entry's citation
  looks in the same place each time, and what it costs is a list of one
  standing for a separation the entry does not make.
- **An entry answering an issue that the change closes cites it `(closes
  #N)`.** An entry answering an issue the change does not close — a fix
  that leaves a mechanism unexplained, one half of a bundle — cites it
  `(issue #N)`. Across repositories the qualified `owner/repo#N` sits
  inside the same parentheses, the qualifier rule above reaching a
  changelog citation exactly as it reaches any other cross-repository
  reference.
- **The citation sits in the text making the claim — the bullet of a
  list body, the paragraph of a paragraph body — and not on the heading
  above it.** An entry's bullets are separate facts and cite separately,
  so a citation gathered onto the heading answers for the entry as a
  whole while the bullets under it name issues of their own, and nothing
  says how the two sets relate. A paragraph body makes one claim and
  raises no such pairing; what keeps its citation off the heading is
  what a heading is, *A `###` names one entry* above making it the
  entry's name where a citation says what the entry did about an issue.
  The rejected alternative is the heading citation, and what it buys is
  a section whose issue numbers a reader collects by scanning the
  headings alone.
- **The reason the pair has two spellings rather than one** is that it
  is then checkable against the landing commit's own subject, written at
  a different moment and the half that gets re-read before merging. One
  spelling for both cases makes an entry inherited from a superseded
  branch unfalsifiable, and such an entry has already told a reader an
  issue was open on the day it closed.
- **The rejected alternative is the bare `(#N)`**, which some
  repositories use: GitHub numbers issues and pull requests in one
  sequence, so `(#N)` does not say which it names — and a squash lands
  with the pull request's own number appended to the commit subject
  already, so the bare form in an entry reads as that number instead.
- **The qualifier does not stand in for the keyword.** `(owner/repo#N)`
  with nothing before the number says which object it names and not what
  the entry did about it, so it fails the falsifiability above exactly
  as the bare form does while reading as more careful; the
  cross-repository citations are `(closes owner/repo#N)` and
  `(issue owner/repo#N)`, keyword and qualifier together. Entries
  already landed in the keywordless form stay as they are, the bullet
  below being why.
- **An issue the entry names without acting on it is written into the
  sentence, not into the parentheses.** The parentheses say what the
  entry did about an issue, and there is nothing to say of one it did
  nothing about, so a reference put there bare is the shape the bullet
  above refuses and reads as a citation with its keyword dropped. What
  the move sheds is the keyword and the parentheses, never the qualifier
  *A reference to another repository is qualified* above requires, and
  the sentence says what the issue is to the entry — where a decision
  lives, which issue covers the other half.
- **Nothing already written is rewritten.** Both files are append-only
  in practice and `merge=union` in fact; the rule binds what is written
  next, not the entries that predate it. What the next entry owes one
  still sitting in the open section is *An entry in the open section is
  a live claim* below.
- **A count that expires inside a landed entry stays there.** An entry
  speaks of its own day — the one its release heading dates, or the day
  it landed where a changelog releases nothing — so a sentence that
  counted a moving population — trees yet to take a rule, repositories
  short of a file — was true when it landed and is not corrected when
  the population moves; the change that moves the population is what
  gets the new entry, and the reader is served by that entry rather than
  by a rewrite the bullet above already refuses. What the no-counts rule
  of this section forbids is writing the next such sentence: a new entry
  counts nothing that moves underneath it. A structure the entry itself
  names — `build` and `check` are two rows, and it lists the two — is a
  description rather than a count, and the rule does not reach it. That
  day is what a reader dates the count against, and a release heading is
  what announces it: an entry the open section still holds has the day
  and not the heading, so it is met as current rather than as a record.
  *An entry in the open section is a live claim* below is that case.
- **An entry in the open section is a live claim.** *Nothing already
  written is rewritten* and *A count that expires inside a landed entry
  stays there* above are about an entry a reader meets as a record: the
  release heading over it says which day the entries beneath it speak
  of. The open section carries no such heading, so its entries are met
  as what the tree holds now, and the release that closes the section
  ships them whole — and where a tree releases nothing, as this one
  does, that section is the whole file and no heading ever arrives. So a
  later entry in that same section bearing on an earlier one leaves the
  file making two claims at once, with nothing saying which the tree
  holds. What is owed is a sentence in the new entry saying what it does
  to the earlier one, and the append stays an append.
  `btclib-org/btclib`'s `babf6fd8` puts a bullet under one the open
  section already held and says `It leaves the entry above where it
  was`, giving the reason that entry's rule survives — while the same
  commit rewrites the prompt that entry's own last paragraph calls
  unchanged, which is what makes it a claim borne on rather than a
  neighbour — and `git show --numstat` reports no deletion on
  `CHANGELOG.md`. So this is not an exception to either bullet above; it
  is what they cost.
- **The form of an entry moves; what an entry claims does not.** That is
  the boundary, and `btclib-org/btclib`'s `49176251` is where it sits:
  it edits the open section — 105 insertions against 84 deletions on
  `CHANGELOG.md`, and no other file — turning paragraphs sitting bare
  under a `###` into bullets split at a bold lead-in, of which the
  citation moving into the bullet that makes the claim is one
  consequence. No sentence changes its truth value across those
  deletions, and that is established rather than asserted: normalizing
  both sides — every citation removed wherever it sat, emphasis and
  list markers stripped, sentence punctuation dropped — and comparing
  the word sequences of the whole file leaves one clause reordered in
  the `btclib.minikey` entry, carrying the same facts, and the commit's
  own new entry. A session that finds that commit and stops there reads
  the open section as editable, and one that finds *Nothing already
  written is rewritten* above and stops there reads it as frozen. The
  deletions are what `git show --numstat` reports: `grep -c '^-[^-]'`
  over the same diff answers 76, being blind to a deleted blank line,
  which is a `-` with no second character; to a deleted markdown bullet,
  which gives `-- **`; and to a wrapped line opening on the house `--`,
  which gives `---`. Every one of those shapes undercounts, and a diff
  holding nothing else answers 0 and reads as the pure append it is not,
  which is why a boundary is argued from `--numstat` and not from a
  pattern.
- **No command in section 15 audits this.** Entries already landed put a
  pointer inside parentheses with nothing before the number, and
  *Nothing already written is rewritten* above keeps them there, so a
  pattern over the file matches one of those as readily as a citation.
  Telling the two apart is a reading, the way this file already treats a
  claim no command re-derives.
- **A value the standard owns is named where the entry decides it and
  cited where the entry uses it.** The entry giving a sentinel its day
  and hour states the instant, that being what it decided, and it ages
  into truth: the decision belongs to that instant whatever the calendar
  says later. The entry moving a `cron:` onto that instant
  cites the section and copies nothing out of it, a copy there ageing
  into a falsehood *Nothing already written is rewritten* above refuses
  to correct. So what decides how an entry is written is the value's
  role in it rather than its presence.

    **Ownership tells the two roles apart.** Section 10's calendar is
    this repository's, so a weekday and an hour beside a citation of
    that section here is the entry that decided them, and the same pair
    in another tree's changelog is a copy of what this one says.

    The rejected alternative is a flat refusal to restate any value the
    standard owns. It is the shorter rule, and it forbids an entry that
    decides a calendar row from stating the row, which is the whole of
    what such an entry records.

    **A copy already landed stays**, for the reason *A count that
    expires inside a landed entry stays there* above gives: the change
    that moves the value is what gets the next entry, and that entry is
    what serves the reader. So both files are records rather than
    references, and a schedule, a floor or a setting is read from the
    section that owns it.

## 10. Workflows

### What every workflow does

- **Every action is pinned to a commit SHA**, with the tag in a trailing
  comment. A tag is a name its owner can move, and these run in a job
  that can read the workflow token.
- **`permissions: contents: read` at the workflow level**, and one
  elevation per job where a job needs more: the job that writes a release
  holds no OIDC token, and the job that signs writes no release.
- **`timeout-minutes` on every job**, set far above what the work needs:
  what it bounds is a hung job holding a runner.
- **`checkout` passes `persist-credentials: false`.**
- **Concurrency groups are named literally** —
  `group: test-${{ github.head_ref || github.ref }}` — never through
  `github.workflow`, which in a called workflow is the *caller's* name,
  so two called workflows would share a group and cancel each other.
  `head_ref` falls back to `ref` so a push run gets its own group, and a
  pull request always groups by its own branch.
- **Triggers**: `push: branches: [main]` and `pull_request`. A push
  trigger on every branch would run the workflow twice for an open pull
  request, into two groups that do not cancel each other; `main` keeps
  its own trigger because a merge creates a commit the pull request never
  tested, and because a cache is readable only from the branch that wrote
  it and from the default branch.
- **`pull_request` types** are `[opened, reopened, synchronize,
  ready_for_review, closed]`. `ready_for_review` because a readied pull
  request would otherwise wait for its next push; `closed` so the merge
  lands in the pull request's own concurrency group and cancels the run
  still holding it. Draft and closed pull requests decline the work in an
  `if`.
- **A workflow whose concurrency group sets `cancel-in-progress: false`
  omits `closed`, and says beside its trigger that it does.** The type
  is there for the cancellation, so where nothing is cancelled a closed
  event supersedes no run and starts one: the `if` above then declines
  that run in every job, which is a workflow scheduled in order to do
  nothing. Such a workflow's `if` guards the draft alone, the event it
  would otherwise decline being one it no longer receives. The rejected
  alternative keeps the list flat and leaves the `if` to absorb the
  event, which reads the same in every tree and costs a run per close,
  with the reason the type is inert stated nowhere the trigger block
  shows.
- **`paths-ignore` only on `push`.** The same list on `pull_request`
  would produce no run at all for a prose-only diff, and a required check
  that produces no run blocks the merge instead of passing it.
- **`workflow_dispatch` on everything**, including the gates: a branch
  whose pull request is not open yet has no other way to ask.
- **`workflow_call`** where the release workflow reuses the gate.
- Every step is a `uv` command with `--locked`.
- **A step that waits for something outside the run is a script under
  `.github/scripts` with a test, not a loop in a `run:` block.** What
  such a step exists for is the verdict it reaches when the wait runs
  out, and no trigger produces that verdict: what is waited on is
  somebody else's work, so neither a release nor a rehearsal can arrange
  for it to be late. A trigger added to reach the loop reaches its first
  attempt instead, which is the branch a wait takes when there is
  nothing to wait for. The lint gate reads the loop and passes it,
  `actionlint` running `shellcheck` over the `run:` block and neither of
  them reading it against the job header — so what stays unread until
  the day the wait is needed is the budget, and a loop able to outlast
  its own `timeout-minutes` is killed inside itself, the run carrying
  the runner's message where the step was written to name the page to go
  and read (btclib-org/btclib#1165). The wait therefore counts against a
  deadline rather than against attempts, which states the budget once
  instead of leaving it a product to be multiplied out, and its test
  substitutes the transport and the clock to drive the loop past that
  deadline. `btclib`'s `wait_for_hwi_device.py` is a wait in that shape,
  and `btclib-secp256k1`'s `verify_wheel_contents.py` is tested that way
  for the reason a wait shares: a run cannot produce the failure on
  purpose, so what the test gives the script is synthetic, and for a
  wait that is the clock.

### The set, and its cadence

A gate runs on a pull request and on a push:

| workflow | what it varies |
| --- | --- |
| `test` | — |
| `lint` | — |
| `docs` | — |
| `release` | a tag, calling the others before it publishes |

**One image and one interpreter.** `ubuntu-latest` and the version in
`.python-version`, and nothing a gate runs varies further. The reason is
one number, the ceiling the plan puts on an organization's concurrent
jobs: at that ceiling a pull request's wall clock is the wait for a slot
rather than the work, so a second image before a review buys a rarer
answer at the price of every review. Everything else answers weekly and
before a release instead — a regression sitting on `main` for at most a
week, against every review paying for it.

**The ceiling's figure has one home per tree, and it is not a workflow
header.** The number is the plan's, so `REPOSITORY.md`'s *Plan-gated
settings* is where it lives, beside the command that re-derives it and
GitHub's own table. Prose that needs the reasoning — a workflow header,
`CONTRIBUTING.md` — states it as this section does, ceiling unnumbered,
and points there for the figure. A date beside the number is not the
cure: the date says when it was true and nothing says it still is,
where the command answers for the day it is run. This section names no
number for the same reason.

**An interpreter axis is a gate cell rather than a sentinel row exactly
where the extra cell runs in parallel with the cells already gating the
review, so the ceiling absorbs it without lengthening the wait, and
where what it claims is the same pinned interpreter run a second time
rather than a version the package newly claims to support.** `btclib-node`'s
`test.yml` carries `3.14t` on this ground, in a `free-threaded` job of
its own beside the `coverage` job at `3.14`: the two run as parallel
jobs rather than in sequence, and `3.14t` is `.python-version`'s own
interpreter with the GIL off rather than a second interpreter the
package claims to support. That job reports rather than gates,
`test-passed` there leaving it out of `needs:` for the reason
btclib-org/btclib-node#746 records; what the criterion weighs is the
slot a cell occupies before a review, which it costs either way. Where
either condition fails — the cells run in sequence, or the second cell
is a version the package does not already claim — the row belongs in
the weekly calendar instead, on the same trade that keeps a platform
row there.

**What runs weekly does not also gate**, so nothing is asked twice at
the price a gate charges. The converse does not hold: a sentinel runs
its matrix whole, the cells a gate already covered included, because a
matrix with a hole in it is one nobody can read the shape of, and the
hole would be re-derived from the gate every time somebody asked what
ran. A sentinel cell that runs the suite passes `--no-cov` for the same
reason read from the other side: the floor is section 8's claim about
one interpreter on one image, and a sentinel exists to ask whether the
platform changes the answer — so the day it finds the `sys.platform`
branch it watches for, the coverage number on that image is
legitimately not 100, and a cell that gated the floor would go red
naming the floor where the finding is the platform's.

**A sentinel's own work is not a pull request's business either, and
*not required* is not the free half of that.** The rule above reads as
though the cost were the gate's, so a job that runs on a pull request
while gating nothing looks to have escaped it: it has not, because what
a pull request charges is the wait, and a reader waits on the list
rather than on the subset of it that gates. `fuzz` is where the trade is
starkest: the exploration is the whole of the work and its length is
what makes it worth anything, so a trigger firing it on a pull request
charges that pull request the wait of a sentinel's full run for a
verdict no merge waits on.

**What decides is the clock, not the trigger** — provided the clock
stays the thing the expensive work answers to, which is what a filter
preserves and an unfiltered trigger destroys. The clock is how long one
run takes: `links.yml` makes one pass over the tree's links and carries
a `pull_request` trigger on its own configuration, where a mutation
session runs its test command once per mutant. So a `pull_request`
trigger on a calendar workflow is not forbidden. It is `paths`-filtered
to the workflow's own configuration and to what that configuration
reads, and what then runs is the whole sweep rather than some cheaper
check of it: the filter bounds how *often* a pull request pays for the
sweep, not what the sweep is. How rare the paths are is that multiplier
rather than the thing multiplied, so counting the branches a filter
selects settles nothing on its own: what a narrower list buys back is
the wait one run adds to the checks a pull request already has, which
the durations answer and the count does not.

```shell
gh run list --repo <owner>/<repo> --workflow <name>.yml \
  --json createdAt,updatedAt,conclusion
```

Run it for the gate's workflow too, and count only the runs that
completed: `skipped` and `cancelled` did none of the work, and
averaging them in reports a fraction of the real cost. A sentinel too
new to have runs to read is where the pair has no answer yet, and
`workflow_dispatch` below is what gets it one. What the pair answers is
how much the sweep *adds* to the wait rather than which check is
longest — a sweep that outlasts the gate adds nothing to a pull request
some slower check is still holding. Where the addition is seconds, a
filter selecting every branch costs a pull request seconds and
narrowing it recovers seconds; where one run is minutes or hours, the
same filter preserves no clock and the paths are wrong. This
repository's own `alignment.yml` is the seconds case — its list names
`README.md`, which is this tree's product, so nearly every branch here
selects it, and what a selected branch waits for it is short enough
that the alternative on offer, waiting for Saturday, is the worse
trade.
Where even a filtered sweep is too much to hang off a pull request, as
an hours-long session is, the calendar is the whole of it. Two triggers
are outside the question entirely — `workflow_call`, where the release
workflow reuses a sentinel as a gate, which this section asks for
elsewhere, and `push: branches: [main]`, where a merge commit is a
census no pull request took. An unfiltered `pull_request` needs a reason
of its own, stated in the header, and the organization has two such
reasons: `integration-bitcoind`, whose regtest job is a required check
and where a required check that never runs blocks a merge, and `codeql`,
whose result the OpenSSF Scorecard reads off a merged pull request's own
commits.

The half a pull request does owe is the deterministic one: an artifact
committed to the tree and replayed by the suite costs milliseconds and
no container, where the sentinel's question — what is in the domain
nobody has described yet — is one an hour once a week answers better
than ten minutes on every push. That is also why shortening the arm is
not the answer, and the alternative is named rather than left to be
guessed at: a minute of fresh exploration per pull request is still the
sentinel's work, done where it is worth least and waited on by somebody.
`workflow_dispatch` is what runs a sentinel by hand before a release
rather than waiting for its day.

Two tables make the calendar, and they are the calendar — the workflow
owns a day and an hour, the repository owns the minute:

| workflow | day | hour |
| --- | --- | --- |
| `vendored-vectors` | Monday | 03 |
| `bootstrap-dns` | Monday | 04 |
| `mutation` | Monday | 05 |
| `fuzz` | Tuesday | 04 |
| `integration-bitcoind` | Tuesday | 05 |
| `integration-hwi` | Wednesday | 03 |
| `deps-latest` | Wednesday | 04 |
| `pypi-install` | Wednesday | 05 |
| `deps-oldest` | Thursday | 03 |
| `py-arm-authority` | Thursday | 04 |
| `os-macos` | Thursday | 05 |
| `os-ubuntu` | Friday | 04 |
| `os-windows` | Friday | 05 |
| `homepage` | Saturday | 03 |
| `links` | Saturday | 04 |
| `alignment` | Saturday | 05 |
| `wheel-reproducibility` | Sunday | 02 |
| `sdist-rebuild` | Sunday | 03 |
| `codeql` | Sunday | 04 |
| `scorecard` | Sunday | 05 |

| repository | minute |
| --- | --- |
| `btclib` | 04 |
| `btclib-secp256k1` | 08 |
| `bitcoin-core-rpc` | 12 |
| `btclib-benchmarks` | 16 |
| `btclib-node` | 20 |
| `.github` | 24 |
| `portanode` | 28 |
| `bbt` | 32 |
| `btclib-org.github.io` | 36 |

**The rows are in the order of what they ask about**, family by family:
the data a tree ships and did not write, the depth its suite is tested
to, what it does against software it does not ship, what it depends on
and what it publishes, which test is the authority for each arm of its
code, the platforms, its own health, and its security. A new sentinel
takes the slot its family already holds rather than the end of the
table, and `scorecard` is why that is a rule rather than a tidiness:
section 2 puts the Scorecard badge at the head of the OpenSSF line
because `scorecard` is the last row, so a sentinel appended past it
takes that reason away. The table's order is that order too: the day
and the hour place the row among the families as well as fixing when
it runs. So a slot standing free between two rows of another family
does not seat a row beside its own, and where the band offers none
that does, it grows downward.

**The week is the whole of the grid's period**, so every row is a weekly
run, and a `cron:` repeating on any other cadence is one the calendar has
no way to name. A workflow that would rather run monthly runs weekly
instead: what the rarer schedule buys is a few runs nobody was waiting
for, against an instant two tables state and a test checks.

**The weekday is the same in every repository**, so a failure
notification names the workflow by the day it arrived, and one calendar
is one thing to remember rather than one per tree. The minute is the
repository's because GitHub queues same-minute schedules across every
repository that asked for one, and a long enough queue drops a run
outright; minute `:00` is in no row for the same reason, being the
minute everybody else's cron picks.

**The hour is chosen against this organization's own load, not
GitHub's.** The queue the minute answers is the one GitHub documents,
and GitHub documents it at the start of an hour: the remedy its note on
`schedule` gives against the delay and the drop is a minute — "schedule
your workflow to run at a different time of the hour" — and it names no
hour of the day at all. An hour picked to miss a published peak is
therefore picked against nothing. What an hour does decide is what the
run competes with here: a row starts its workflow in every tree that has
it, each running its matrix whole, so the rows sit in the hours before
the working day, where the ceiling above is not being spent on a pull
request somebody is waiting for and a failure is waiting to be read
rather than arriving in the middle of one.

**The hour is UTC, and the band grows downward.** A `cron:` here names
no `timezone:`, which is what leaves it UTC, and a fixed UTC hour falls
later in the morning here for as long as the clocks are forward. The
band's late end is what reaches the working day first, so the hour the
band gains is the one below its earliest rather than the one above its
latest. **A `timezone:` beside a `cron:` fails
`tests/grid_test.py` outright**, rather than being converted before the
calendar is compared, so a schedule cannot leave UTC by declaring one.

A day is a slot rather than a census: it says when that workflow runs
where a repository has it, not that every repository does, and *Which
trees carry which sentinel* below is which repositories those are.

Dependabot is in neither table and runs Thursday, that being the day
`deps-latest` reports on the upgrade before the pull request arrives —
it states its own schedule in `dependabot.yml`, in a different shape,
and picks its own minute.

`tests/grid_test.py` of this repository reads both tables and every
`cron:` of every repository, in both directions: a schedule no row names
fails there, and so does a row nothing in the organization answers to,
which is what keeps a row here from being a claim nobody checks. The
commands a human runs instead are in section 15.

`deps-latest` is the sentinel that makes a Dependabot pull request a diff
whose result is already known: it upgrades everything the resolver
touches, runs the suite, the lint gate and the packaging checks, and
commits nothing.

`deps-oldest` is its mirror, and what it verifies is the claim a floor
makes to whoever installs: `uv lock --resolution lowest-direct` where
`deps-latest` runs `uv lock --upgrade`, on the oldest interpreter alone.
`lowest-direct` and not `lowest`, which takes the transitive
dependencies to their minima as well and resolves environments that do
not install, a red saying nothing about the tree. One cell, because a
floor is two claims — `requires-python` and the dependency specifiers —
and the cell holding both at once is what verifies them together, the
rest of the matrix being `deps-latest`'s and `test`'s. What it finds is
an issue against the floor it found, a floor raised because it was wrong
being the point of the run.

Verifying at release time instead — a `lowest-direct` step in
`release.yml` — is the rejected alternative. It reaches only the trees
that publish, where a tree that releases nothing declares floors too,
and it puts the red at the moment a release is being cut, over a drift
that happened months earlier and has nothing to do with the release.

`links` runs lychee with `--include-fragments`, so a link into a
heading is checked as an anchor and not only as a page. A tree cites
another tree's headings by anchor — this file's sections most of all,
which the `CONTRIBUTING.md` of every repository links into — and the
forge serves a page whose fragment resolves to nothing rather than
answering 404, so a heading renamed here breaks those links with
nothing red in the tree that renamed it. The run that would notice is
therefore the linking tree's, which is why the flag belongs in every
`links.yml` and not in this repository's alone; `tests/links_test.py`
asks each tree's lychee step for it. The rejected alternative has a
tree check only the anchors of its own headings, which measures the
file a rename lands in and never the links pointing at it.

**A sentinel's row arrives with the workflow, and one pull request can
do both only where the first tree is this one.** `tests/grid_test.py`
reads the calendar against the trees in both directions, so a row naming
a workflow nothing in the organization schedules fails there exactly as
a `cron:` no row names does. A sentinel whose first tree is this
repository takes its row in the pull request that gives it the
workflow — one repository, one landing, neither test red. A sentinel
whose first tree is another repository cannot: the row is this tree's
`README.md` and the schedule is that tree's workflow, always two pull
requests, and one of them lands first. The order is the row first — the
adoption is this file's own change, and the receiving tree's workflow
comment then cites a row that exists from the moment it lands — and what
carries the row in between is the debt issue its paragraph of *Which
trees carry which sentinel* below names. That reference is what
`test_every_row_of_the_calendar_names_something_that_exists` reads,
asking GitHub whether the issue is open, so the exemption expires when
the issue closes rather than when a reader thinks to look.
The other order keeps that test green by turning
`test_every_cron_is_the_instant_the_calendar_names` red instead, and
asks a tree to schedule against a calendar that does not yet name it.
What stays refused is a row written the day the rule is, which reads as
the calendar being a plan rather than a description: an adoption pull
request names the tree that owes the workflow and the issue that
carries the debt, where a plan names nobody — and that direction of the
test is the only thing anywhere that catches a row for a workflow
nobody wrote, so spending it on a rollout with no debtor leaves it
catching nothing.

**A row that moves is red until the last tree follows it.** The row is
this file's and each `cron:` is its own tree's, so a slot changed here
and a schedule changed there are separate landings, and in between
`test_every_cron_is_the_instant_the_calendar_names` names every tree
still on the old instant. That list is the port's work rather than a
defect of the trees on it, and it is bounded by the issue carrying the
ports — a reader's check, where the debt issue an adoption names is one
the run reads.

### Which trees carry which sentinel

Section 14 leaves *which optional workflows exist* to each repository,
and these are not left there: what a tree owes is decided once and
ported, a repository deciding for itself whether its own parser is
fuzzed being a repository deciding what the organization's exposure is.

This is the record: one entry per calendar row, naming the trees that
carry that sentinel, in the order the two tables above give the rows and
the repositories. A tree an entry names runs the workflow and shows its
badge, section 2's row reading its sentinels from here rather than
stating a rule of its own; a tree an entry does not name is asked
nothing by that row.

- `vendored-vectors` — `btclib`, `btclib-secp256k1`,
  `btclib-benchmarks`, `btclib-node`;
- `bootstrap-dns` — `btclib-node`;
- `mutation` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`,
  `btclib-benchmarks`, `btclib-node`;
- `fuzz` — `btclib`, `btclib-node`;
- `integration-bitcoind` — `btclib`, `bitcoin-core-rpc`, `btclib-node`;
- `integration-hwi` — `btclib`;
- `deps-latest` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`,
  `btclib-benchmarks`, `btclib-node`;
- `pypi-install` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`,
  `btclib-node`;
- `deps-oldest` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`,
  `btclib-benchmarks`, `btclib-node`;
- `py-arm-authority` — `btclib`;
- `os-macos` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`,
  `btclib-benchmarks`, `btclib-node`;
- `os-ubuntu` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`,
  `btclib-benchmarks`, `btclib-node`;
- `os-windows` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`;
- `homepage` — `btclib-org.github.io`;
- `links` — every repository;
- `alignment` — `.github`;
- `wheel-reproducibility` — `btclib-secp256k1`;
- `sdist-rebuild` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`;
- `codeql` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`,
  `btclib-benchmarks`, `btclib-node`;
- `scorecard` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`,
  `btclib-node`.

**An entry is what was decided, not what a tree happens to hold**,
which is what separates it from the tier table of section 2: a tier is
read off the tree by the two files that section names, where carrying a
sentinel is a decision somebody took. So a tree short of what its entry
names is a gap in that tree and not a correction owed here, and a tree
that carries what no entry gives it is the same finding read from the
other side — a workflow whose row does not name the tree, and a badge
with no row behind it. `tests/grid_test.py` reads the workflow half of
both against every tree, a red cell there bounded by the issue a
`BACKLOG` row of `tests/__init__.py` names.

Where a property of the tree decides membership it is stated below, so
that the answer for a new repository is read off the tree rather than
argued; where none does, the entry above is the whole of it. A tree that
owes a sentinel it does not carry is a debt with an issue behind it, and
its entry gains the tree when the workflow and the badge land together.

- **`mutation` follows a suite over code the tree ships.** A coverage
  floor at 100 says every line and branch ran and says nothing about
  whether any assertion would have noticed the line being wrong — a
  module imported and never asserted about reaches 100% of itself — so
  the sentinel is worth most exactly where the floor is highest and
  coverage has stopped saying anything new. Publishing is the wrong
  property to key it on: `btclib-benchmarks` publishes nothing, holds a
  suite and holds `fail_under = 100.0`, which is the tree where the
  measurement has the most to say rather than the least. What owes it
  nothing owes it for one reason rather than several: a mutant needs
  code of the tree's own to change. `bbt` holds no suite at all, its material
  being course notebooks and scripts, and gains the sentinel the day it
  gains a suite over that material, which is btclib-org/.github#301's
  question. `.github`'s suite is over the other repositories rather than
  over anything this tree ships, so a mutant here would land in the
  measuring instrument and the number would be the suite reporting on
  itself.
- **`scorecard` asks a repository that is public and is not a fork**,
  and that is the bar rather than the key: clearing it leaves a tree
  able to run the sentinel, and the entry above is what says whether it
  does. Public is what the OpenSSF Scorecard reads at all, and
  `ossf/scorecard-action`'s own README says running it on a fork is not
  supported — so `gh api repos/<org>/<repo> --jq .fork` is the second
  half of the bar, and no repository of the organization answers
  `true` to it: that half is a rule with no instance, kept for the tree
  that arrives as a fork rather than describing one that is here. A tree
  the entry leaves out gives up the alerts the run files as well as the
  score, `security-events: write` below being that half; the badge is
  what the row is kept for, and a reading nobody displays is not worth
  the run. What the sentinel buys is an opinion of the tree's
  supply-chain posture formed outside the organization: this file is a
  standard the organization holds itself to and every command in section
  15 asks a question somebody here chose, where a score computed by a
  third party is the one reading that can find what nobody thought to
  ask for. **A check scoring below
  its maximum is an issue against what it found**, never a sentence in
  section 14 saying why this organization scores it that way — it
  aligns by adopting the practice rather than by explaining the score,
  and a derogation would make the outside opinion answerable to the
  thing it measures. What that gives up is the case where a check is
  simply wrong about this organization, which then costs an issue closed
  on the measurement rather than a paragraph nobody revisits.

    The badge and the published score want `publish_results: true`, and
    the job wants `id-token: write` for the transparency-log entry,
    `security-events: write` to file what it finds as code scanning
    alerts, and `actions: read` with `contents: read` — the
    elevation-per-job rule above, applied to a workflow that writes
    nothing to the tree.

    **Its triggers are the action's and not this section's**, which is
    the one exception to *`workflow_dispatch` on everything* above: that
    README names `push` and `schedule` on the default branch as
    supported and calls `workflow_dispatch` experimental, so a tree
    following this section there would be asking for a trigger its
    action does not stand behind. The same README reads repository rules
    with the workflow's own `GITHUB_TOKEN` and wants an administrative
    one where a repository's protection is the classic kind instead;
    every repository here carries a ruleset set *and* classic
    protection, section 16's checklist asking for both, so which of the
    two the score rests on is a question a port answers and this
    sentence does not.

    **The trees this entry names owe a registration at
    bestpractices.dev**, the questionnaire answered, and section 2's row
    carries the badge that renders its live state. `CII-Best-Practices`
    is the check that reads that registration, so the trees the sentinel
    runs in are the trees to register: registering one that runs no
    Scorecard is attestation work nothing reads. Registering is an
    account action rather than a pull request, and
    btclib-org/.github#350 is where the registrations outstanding are
    carried. What that costs is a second home, one per tree, for facts
    this file already states — how a vulnerability is reported, how a
    release is cut, what gates a change — so a change to any of them
    owes a pass over the questionnaires, and nothing says so. That is
    section 9's *One fact in one place* losing deliberately to being
    legible from outside the organization.
- **`fuzz` follows a tree that parses whatever a stranger sends.** Not
  merely input the tree does not produce: the property is that nobody
  stands between the parser and an adversary who chooses the bytes.
  `btclib` and `btclib-secp256k1` read transactions, scripts, PSBTs,
  signatures and extended keys off the wire, and `btclib-node` speaks
  the peer-to-peer protocol, where the sender is by definition a
  stranger. `bitcoin-core-rpc` reads a Bitcoin Core instance its own
  operator runs, so the party on the other side is chosen rather than
  arbitrary and the property does not reach it; that is a weaker threat
  model and it is the reason, not an omission. `btclib-secp256k1` has
  the property and no entry, and the property does not settle this one
  on its own: whether a target there is allowed to reach the vendored C
  library at all — which would be fuzzing upstream's work rather than
  these bindings — decides what the sentinel would be run for, and
  btclib-org/.github#342 is where that is decided. An entry taken before
  that answer schedules a weekly run against a target nobody has agreed
  is this project's to write. Section 7's *Property tests* has how a
  fuzzer and the property layer stand to each other. What a fuzzer turns
  up is a length prefix larger than the buffer, a truncated multibyte
  sequence, a varint that overflows, a recursion depth that exhausts the
  stack — found by the sentinel rather than by somebody else. A crash
  the sentinel finds is an issue against the parser and never a
  suppression, that being the whole of what it was run for.
  The regression that crash becomes is the suite's and not the
  sentinel's: an ordinary test, naming the input and what the parser is
  now expected to do with it — which is usually to refuse it in the
  tree's own exception rather than to accept it.
  `fuzz/corpus/` is not that place, and a tree must not be told to put
  it there. That directory is a *seed* corpus in the term's ordinary
  sense — inputs committed beside a target so the fuzzer starts from
  valid structures rather than from noise — and the gate over it,
  `btclib`'s `tests/fuzz_corpus_test.py`, asks the opposite question:
  that every seed is *still a valid serialization of what it parses*. A
  crash input added there inverts that gate, because the hardening that
  fixes the crash is exactly what makes the seed refused, and the only
  way back to green would be to delete the regression. What the seed
  gate does guarantee is acceptance by *one of* the entry points the
  harness declares rather than by the intended one, and the module says
  so itself, naming the harnesses where a parser narrowed to refuse its
  own seed passes because a sibling still accepts it. That is a check on
  the seeds — it keeps the fuzzer's starting point honest as the parsers
  move under it — and what frees the sentinel from carrying a regression
  suite is the ordinary test above rather than this gate.
  What fills the workflow is the tree's — which entry points are targets
  and which harness runs them, `atheris` under ClusterFuzzLite in
  Actions or under OSS-Fuzz. What is fixed here is the name the calendar
  keys on and which trees owe one.
- **`deps-oldest` follows a tree that builds a distribution.** Its
  `requires-python` and its dependency specifiers are a claim made to
  whoever installs it, and that claim is what the resolution checks; a
  tree that installs nothing makes none, so `bbt` and this repository
  are outside the row whatever their `pyproject.toml` declares. It is
  the same set `deps-latest` names, the two rows asking one question in
  opposite directions: whether the code survives the newest releases,
  and whether the oldest ones it declares install at all.
  btclib-org/.github#323 carries the debt for the trees of the entry
  still short of the workflow.
- **`sdist-rebuild` follows a tree that publishes an attestation.** The
  attestation vouches for bytes, so a released tag either rebuilds to
  the sdist that was signed or it vouches for something no rebuild
  answers for: section 12 states that property, and each tree's
  `RELEASING.md` names the steps a rebuild replays. What the sentinel
  compares against is the digests the attestation carries,
  `gh attestation verify` over the rebuilt file passing only where the
  two agree; reading the index's own digests for the release instead is
  the rejected alternative, those saying what PyPI holds rather than
  what was signed. Cutting the comparison into the release is the
  other, and there it is a build against itself in the same job on the
  same image: what moves between a release and the day somebody
  verifies is a backend, a runner image or a toolchain, which is the
  interval a weekly run covers and a release-time step has not reached.
  The compiled wheel is outside the property for the reason section 12
  gives, so the row is the sdist's rather than every file a rebuild
  produces with one tree's exemption written into it. A rebuild that
  disagrees is an issue against the tree it ran in.
  btclib-org/.github#523 carries the debt until the first of them
  schedules the workflow.
- **`wheel-reproducibility` follows a tree that ships a compiled
  wheel.** Section 12 puts the compiled wheels outside the property
  `sdist-rebuild` re-derives, and this row is what asks how far that
  stands. A wheel with nothing compiled in it is the checkout's own
  files under the member metadata the backend fixes, which is the
  ground `sdist-rebuild` already stands on. The sentinel builds one
  interpreter's wheel twice on one image and diffs the two archives
  member by member, then diffs the wheels two images of one platform
  built, the second image being chosen to differ in the toolchain it
  carries. What it answers for is narrower than what section 12
  exempts. btclib-org/btclib-secp256k1#524 is where the property is
  being reached for, on the platform section 12 names a pin for, and the
  workflow this row schedules asks two builds in one directory and two
  environments alike: a platform whose wheels disagree is an issue
  against what the run names rather than a line here.
  btclib-org/btclib-secp256k1#538 carries the port until that tree's
  `cron:` is the instant above and its badge is in the row.
- **`homepage` follows a tree serving a page generated from another
  tree's file.** `btclib-org.github.io`'s `index.md` is derived from
  `profile/README.md` here, and what the sentinel asks is whether the
  served copy still says what that file says. The drift it watches for
  arrives from a landing in this tree rather than from anything the
  serving tree does, so no pull request there is the occasion to ask.
  Sending a `repository_dispatch` from here when `profile/README.md`
  lands is the rejected alternative: it is the exact signal rather than
  a poll, and it wants a credential with write access to that tree,
  which nothing here holds. Asking it from this suite is the other, and
  what it costs is a red on `main` here for a drift another repository
  owns. The minute this row gives that tree is `links`'s there too,
  which it does not carry yet: btclib-org/btclib-org.github.io#1.
  btclib-org/.github#558 carries the debt until that tree schedules the
  workflow.
- **A platform row leaves a tree's entry where a gate cell asks the
  whole of what that tree's sentinel asked.** *What runs weekly does not
  also gate* above denies its own converse over a hole in a matrix, and
  a sentinel the gate covers whole leaves none. That cell gates on the
  suite passing and not on the coverage floor, for the reason the same
  paragraph gives a sentinel cell its `--no-cov`, and its place before a
  review is the trade *An interpreter axis is a gate cell rather than a
  sentinel row* above names. Where that trade does not hold, or where
  the cell is narrower than the sentinel's matrix — one of its images,
  one of its interpreters — the sentinel keeps its whole matrix on the
  calendar and the entry keeps the tree. `btclib-node` is out of the
  `os-windows` entry on this ground, its `test.yml` gating a
  `windows-latest` cell at the interpreter `.python-version` pins.

### The aggregate job, and the required check

A workflow whose answer gates a pull request ends in a job that `needs` every
other job in it whose own result is a claim about the pull request, and is
named with its workflow — `test: every job passed` — because a check context is
keyed by name alone and two workflows with a job of the same name produce one
ambiguous check.

**A job engineered to conclude successfully whatever it finds makes no such
claim, and stays out of `needs` for exactly as long as that holds.** A step
tolerated with `continue-on-error: true`, reported by a step of its own
rather than left to redden the run, is what gives such a job that shape:
its green then says nothing about what the job is named for, so folding it
into `needs` would make the aggregate cite a job whose passing is not
evidence of anything. The exception is not a standing shape — it holds only
while the job cannot make the claim it is named for, and it ends the day it
can. `btclib-node`'s `free-threaded` job is out of `test-passed`'s own
`needs:` on exactly this ground: its sync step is tolerated because the
wheel it depends on does not publish, and it rejoins `needs` the day that
changes (btclib-org/btclib-node#746).

**A matrix is not what asks for one.** A branch rule can name only a
context a pull request produces, so a workflow triggered by `push` and
`schedule` alone is one no rule can require, however many cells it runs,
and an aggregate there is a name nothing can hold. Where such a workflow
is to gate, the trigger and the aggregate arrive in the same pull
request, and the rule follows them.

- **Never name a matrix cell in the branch rule.** The rule lives outside
  the repository, so a context that stops being produced blocks every
  merge with nothing in the tree to explain why.
- **The job carries an `if:` of its own: a job with `needs` and no `if:`
  is skipped when one of those needs fails**, which is the outcome the
  aggregate exists to report. The check then reports `skipped`, which is
  silence about the failure rather than a report of it, and no step of
  that job runs however unconditional the step is. The condition is
  `!cancelled()`, beside the draft and closed conditions *What every
  workflow does* gives above. `always()` is the wrong widening: a run its
  own concurrency group superseded reaches the job and fails it, making a
  red required check of a cancellation the newer run already speaks for.
  `!cancelled()` skips the job on that run instead, and a job cancelled
  on its own — the run not being cancelled — still reaches the step.
- **What the aggregate reads is its own run's job listing, asked of the
  API rather than of `needs`** —
  `repos/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}/jobs`, each
  finished row's `conclusion`, in a step that fails on anything but
  `success` and `skipped`. The aggregate's own row is not one of them:
  its `conclusion` is `null` while the step is reading, and what judges
  that row is the unfinished count below. The job elevates to
  `actions: read` above the workflow's `contents: read` and hands
  `github.token` to the call. What that buys is a source reporting what
  the needs context does not.
- **The listing is asked for in full** — `gh api --paginate`, with
  `per_page=100` on the query so that the pages are few. A page is a
  bound on what comes back and nothing bounds a run's job count under
  it, a matrix being what expands that count and the matrix being what
  an aggregate exists for. Rows past the page are missing from the
  answer with nothing in the answer saying so, so the allowlist above
  and the count below are taken over a subset.
- **A matrix reports one result to `needs` and one row per cell to the
  listing.** btclib-org/btclib#1001 is a run whose cells died in *Set up
  job* downloading a pinned action, codeload answering 429 and the
  runner giving up, where `needs.<job>.result` was not `failure`.
  `btclib-benchmarks`' `602f51d` narrows the mechanism by experiment
  rather than by argument: a cell pointed at an action SHA that does not
  exist propagates `failure` normally, and the abandoned download does
  not.
- **A boolean `if:` over `needs` decides nothing when it is false.** The
  step is skipped, a skipped step leaves its job successful, and the job
  branch protection names is green over a red matrix — which is what
  btclib-org/btclib#1001 is a recorded run of.
- **A shell allowlist over `join(needs.*.result, ' ')` is vacuous on an
  empty join.** `for` splits on words and an empty string contributes
  none, so the loop compares nothing and exits 0; it is sharpest where
  the aggregate has a single `needs`, and it is btclib-org/btclib#1454.
- **What answers that vacuity here is a count of the run's unfinished
  jobs, and the count is the aggregate itself alone.** A listing with
  nothing unfinished is not a listing of the run the step is running in,
  and one with something else unfinished is a run this job does not
  `needs` the whole of. The count is what says so rather than a name,
  a name being what a rename moves. The empty join has no counterpart
  in this shape, there being no join.
- **The listing's unit is the run and not the workflow.** A gate
  `release.yml` reuses through `workflow_call` has no listing of its
  own: the caller's jobs and the called workflow's are one run, every
  row of it carries the caller's `workflow_name`, and the publishing
  jobs are unfinished exactly because they wait on this one, so the
  count above can never be the aggregate alone.
- **The aggregate declines the reused run, on an input the caller
  passes.** The reusable workflow declares a `workflow_call` input
  `reused`, `type: boolean` with `default: false`; the calling job in
  `release.yml` passes it `true` in its `with:` block; and the aggregate
  carries `!inputs.reused` in the `if:` beside the conditions above. A
  run that is not a call leaves the input unset, so the aggregate runs
  wherever the listing is the workflow's own — which is where branch
  protection reads it, a release being a tag push or a dispatch that no
  rule waits on. What gates the release instead is the caller's own
  `needs:` on the calling job: `bitcoin-core-rpc`'s `release.yml` run
  `33236701141` had failing cells in the platform workflows it called,
  and every publishing job of it reports `skipped`.
- **The input carries the signal because nothing else in a called run
  states it.** `github.event_name` is the caller's event —
  `btclib-org/btclib`'s run `32458459305` was dispatched, and the
  `changes` job of the workflow it called printed `workflow_dispatch` —
  as `github.workflow` is the caller's name, which is why *What every
  workflow does* above names a concurrency group literally; and no field
  of a job row names the file that wrote it. Detecting reuse without the
  input is therefore an inference over the caller's own values. The
  other rejected alternative reads `needs.*.result` where the listing is
  not the workflow's own, which reinstates btclib-org/btclib#1001.
- `skipped` is legitimate on purpose: when the run was superseded by its
  concurrency group, and when a `changes` job decided the diff touches
  nothing those jobs read. The listing reports it as a conclusion like
  any other, so a filter naming only `success` fails the check a merge
  waits for on every run a `changes` job empties.
- **A `changes` job** is the cheapest job in the workflow and decides
  whether the rest runs. It answers `true` on every trigger that has no
  base to diff against, and the files it counts as prose are narrower
  than they look: the README is the package's long description, the docs
  are read by tests, and the history files are parsed by the suite.
- Where a single job is what gates, **that job is the context**.
- **Renaming a required check cannot be done in a pull request**: the
  branch stops producing the old name while the rule still waits for it.
  The rule moves first, against the branch, and the pull request follows.

## 11. GitHub settings

These live outside the tree. `REPOSITORY.md` is where each repository
writes down its own, with the command that reads it back.

**What that file covers is the settings this standard asks about** — the
ones section 16's checklist sets on a new repository, the ones a section
of the standard states a rule for, and the ones a behaviour it describes
rests on — together with whatever a call quoted for one of those answers
alongside it. It says what falls outside that scope too, so a setting it
is silent about reads as a decision rather than as an omission.

**A copy carries all three limbs in the standard's own words** rather
than wording them for itself. Two spellings are what that forecloses:
`README.md` written into the second limb names a sibling's own file, and
a bare `it` there reaches for section 16's checklist, where the third
limb's `it` is this standard. The rejected alternative leaves the wording
to each copy, and what it costs is a reading per tree of a claim they are
all making once.

The claim rejected is `this file is the whole of them`, which no command
checks: the repository document answers with fields this file states no
rule about, and telling those apart from the settings a repository
decides is a reading. What the narrower claim gives up is the promise
that a reader holding the file holds everything; what it buys is a
perimeter this file fixes rather than the endpoint, which is what a copy
can be held to.

**The section headed `## What this file passes over` is where a copy
says what falls outside that scope.** Whether the section is there is
what a command asks; whether it is honest about the perimeter is a
reading, as the wider claim above is. The rejected alternative leaves
the second obligation to a reader's check with nothing to run, and what
it costs is a copy that deletes the rejected claim and says nothing of
what it leaves out reading as converged.

**A copy does not claim that nothing it records has another form in the
tree.** The topics are section 3's `keywords`, a releasing tree's
`.homepage` is the `[project.urls]` field of that name, and a Pages
custom domain has the root `CNAME` carrying the same value — so where a
tree holds one of those, the record is a second copy read back for
comparison rather than the only place the answer lives, which is what
that copy's own section on it says. The rejected alternative is the
blanket clause `nothing here is recoverable by reading the code`, one
sentence shorter and refuted in such a tree's own file two sections
further down.

**`has_wiki` and `has_projects` are outside the perimeter**: this
standard states no rule about either, and a copy neither reads them back
nor explains an answer to them. The rejected alternative records each
with a sentence saying no rule is stated, so that a reader sees the
answer and is told it is nobody's divergence; what it costs is a file
growing with GitHub's API rather than with this standard, in a wording
each copy invents for itself.

**`has_issues` is not with them.** `CONTRIBUTING.md` sends an issue about
one repository alone to that repository's own tracker, and section 16's
checklist gives every repository an `ISSUE_TEMPLATE/`, so a behaviour
this standard describes rests on the setting and a copy records it.

**Section 10's `scorecard` bar splits on that same test.** Public is what the
sentinel reads at all, so a behaviour this standard describes rests on
`.visibility` and a copy reads it back, which puts a flip to private one
command from being seen. Nothing sets `.fork`: a repository arrives as a fork
or it does not, so no limb reaches it and section 10 states that half of the
bar once. The rejected alternative keeps both halves out of every copy, on the
ground that the bar is section 10's to state; what it costs is the flip, after
which the sentinel's row and its badge stand while the run stops producing a
score, and the file a reader restores the repository from says nothing.

### Signatures

**Every commit reaching a protected branch carries a valid signature**,
enforced by a `required_signatures` ruleset rule. It does not have to be
one particular signer: the maintainer's key, GitHub's web-flow key on a
button-driven merge, and a bot's key are all valid, which is what makes
the merge buttons usable.

Tags too: a release tag is signed, and a `tag-integrity` ruleset over
`refs/tags/v*` requires it — that tag being otherwise the one unattested
link in a fully signed chain.

### Branch protection and rulesets

`main` is the only branch. Everything reaches it through a pull request,
the bots' included, none of which names a target branch.

Classic protection carries the required checks with `strict`, one
approving review, `dismiss_stale_reviews`, linear history, no force
pushes, no deletions, `required_conversation_resolution`, and
`enforce_admins` **off**.

Three rulesets sit beside it, additive — rules aggregate across rulesets
and classic protection, taking the most restrictive combination:

- **`main-integrity`** — required signatures, linear history, no force
  pushes, no deletions. **No bypass actor, for anyone, ever.**
- **`main-self-merge`** — require a pull request, one approving review,
  dismissal of stale reviews, conversation resolution, and `squash` as
  the only merge method it accepts. Bypass: the maintainer, in
  **`pull_request` mode**.
- **`tag-integrity`**, target `tag`, `refs/tags/v*` — required
  signatures and nothing else, so the recovery path that deletes and
  re-tags a failed release still works.

**The bypass mode is the whole of the design.** `pull_request` excuses
its holder *while merging a pull request* and at no other time, which
answers the one thing a solo-maintainer repository cannot do — produce
someone else's approval. A direct push to `main` is refused for everyone.
The other mode, `always`, would permit a direct push, and what it would
buy is worth nothing once the rule is read as asking for a valid
signature rather than for a particular signer.

**What it excuses is the rule, not the approval count.** Its holder [can
then choose to bypass any branch protections and merge that pull
request](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository#granting-bypass-permissions-for-your-branch-or-tag-ruleset),
and the guard against merging a head an approval no longer covers is a
parameter of that same rule: `dismiss_stale_reviews_on_push`, [the
approval dismissed once a push changes the diff it was
given](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets#require-a-pull-request-before-merging).
So the dismissal binds every merge except the ones this organization
makes, and the `sha` on `CONTRIBUTING.md`'s merge call is not a second
belt over a forge rule that would have refused the moved head anyway.

Two settings hold the door, not one: the classic review requirement is
cleared for the maintainer by `enforce_admins: false` *plus* admin, and
turning `enforce_admins` on would deadlock every solo merge. That setting
clears the whole of classic protection for that account rather than its
review rule alone, `strict` included, so being up to date with `main` is
a rebase somebody runs and not a rule the forge holds. A branch merged
behind `main` lands a tree nothing has run: the branch is green against
the base it was gated on, `main` is green against its own tip, and the
squash produces neither.

When patching required checks, use the `checks` array and a JSON body on
stdin: `contexts` has no field for an app, so sending it silently
replaces a bound list with an unbound one, and `-f` sends `app_id` as a
string, which the endpoint refuses. `PATCH` the sub-endpoint; a partial
`PUT` of the whole protection object drops the reviews and the
signatures.

### Merge method

**Squash is the only button enabled**, and auto-merge presses it once the
review and the checks are in. One change is one commit on `main`. A merge
commit is refused by linear history already; rebase-and-merge is the one
deliberately removed, since it replays a branch's review steps onto
`main`.

**`allow_auto_merge` is on**, and a copy reads it back with the other
merge settings: the sentence above rests on the setting rather than
describing it. Off, auto-merge is not offered, every landing waits on
somebody pressing *Squash and merge* at the moment the last check goes
green, and nothing turns red. The rejected alternative leaves it to each
repository as a convenience rather than a setting of this standard's,
and what that costs is a section describing a landing path the tree no
longer offers, with no command anywhere to catch it.

One method is also one entry in a dropdown that GitHub preselects from
whatever was used last — and the dialog that switches auto-merge on
carries the same dropdown, hours before anything merges.

`squash_merge_commit_title` and `squash_merge_commit_message` are set so
that a single-commit branch lands under its own subject and a longer one
under the pull request's title, with the branch's commit messages as the
body — never the pull request's description.

**A subject is one physical line.** `%s` joins a wrapped subject up to
the first blank line where the squash does not, so `git log --oneline`
and every read through `%s` show a whole sentence the landing will cut —
a wrapped subject lands truncated at its first line, the citation it
carried left behind in the body, and nothing turns red. The read that
does not conceal the wrap is the first line of `%B`:

```shell
git show -s --format=%B <sha> | head -1
```

`79fb1df` is where that happened here. `git show -s --format=%s 190d5bd`
reads the whole subject the branch carried, `(closes #686) (closes #692)`
and all; the first line of the same commit's `%B` is the fragment the
squash landed. The rest of the subject is on `main` as the body's own
first line, `what they mean (closes #686) (closes #692)` sitting where a
paragraph belongs, in a message nothing rewrites. The issues closed
anyway, GitHub having parsed them from the pull request title, so
nothing went red and the only signal was the sentence stopping mid-clause.

`delete_branch_on_merge` is on.

### What a pull request says it is

**A pull request that closes an issue names it in its title, in
parentheses**: `Say when github-release runs instead of relying on no if
(closes #1142)`. Which of the title and the branch's own commit subject
lands is *Merge method*'s rule, so the parentheses belong on whichever
one that is — not only on the title; whether they survive the landing at
all is that same rule, a subject that wraps taking its citation off the
subject with it. Either way the number reaches `git log` and stays
reachable from a checkout with no forge in front of it.

**A pull request that advances an issue it does not close names it the
same way, `(issue #N)`**, and for the same reason, which reaches further
here: without the citation the subject carries no number at all, so from
a checkout with no forge the connection is not weakened but lost. The
token holds one meaning wherever the standard writes it — section 9's
`CHANGELOG.md` citation and this one both name an issue the change does
not close — and which of the two a change carries is decided by what is
true of it. Neither is the closing mechanism: the description is, and
the paragraphs below have the read that says what it closed.

**The rejected alternative reserves `(issue #N)` for `CHANGELOG.md`
alone**, so that parentheses on a subject always mean a close. What it
costs is the number: a branch answering half an issue then lands with
nothing in `git log` pointing at what it answered.

A pull request that neither closes nor advances an issue carries no
parentheses, and adding some because the shape looks right is how a
wrong number gets in. Nothing already landed is rewritten, a title and a
landed commit subject included: section 9's *Nothing already written is
rewritten* is this same rule, read from the title's side of it.

**A title citing several issues joins them for the reader, and the
parser binds the verb to the first.** `(closes #319, #388)` is, to the
parser, a keyword on the adjacent number and a bare mention of the
rest — which costs nothing where the description carries every keyword,
the check below having counted them, and the landed subject's own
keyword then meets issues already closed. That safety is the
description's, not the subject's: a commit that had to close on its own
subject would repeat the verb for each reference — `(closes #319)
(closes #388)`, adjacency being the test — and everything here reaches
`main` through a pull request whose description is what closes.

**The verb is checked against the forge's own parse, not against
intent.** `closingIssuesReferences` is what GitHub actually read out of
the description, and *what a pull request closes is read before it is
merged*, below, has the command — one read answering both questions.
A title or an entry carrying `closes` for a number missing from that
answer, or `issue` for one present in it, is wrong on the parser's own
evidence — landed pull requests have carried the second defect, closing
their issue while citing it `(issue #N)` in the changelog, the release
notes and the title at once, and one of them got the title right while
both prose files beside it stayed wrong, so a correct title is not
evidence for the citations it travels with. The answer can lag the
create by a moment; a zero that survives repeated reads spaced apart is
not lag but a parse that never ran, and an edit that resubmits the body
is what re-triggers it.

The title is not the closing mechanism. `Closes #N` in the
*description* is what GitHub acts on, and both are wanted: the
description closes the issue, the title records which one. The bare
`#N` form is repository-local: written in another repository it names
that repository's own issue N, not this one's. The qualified
`owner/repo#N` form closes across repositories exactly as `#N` closes
within one — measured on `btclib-org/btclib-secp256k1#366`'s squash
commit, `592f1bc`, whose message named `btclib-org/.github#81` after a
keyword: the issue closed on that merge, its timeline crediting the
commit rather than a Development-panel link.

That qualified form is also section 9's own citation style for another
tracker's issue, so an ordinary cross-repository mention already
carries what a keyword needs to fire — and GitHub does not parse
negation, so the sentence declaring that a keyword closes nothing is
the sentence most likely to hold one: the commit above read `No keyword
closes btclib-org/.github#81 here`, and a same-repository pull request
body read `I close #291 by hand once the last lands` — each put a
keyword verb directly in front of the number it meant to spare. So a
mention that must not close names the issue with no verb immediately in
front of it, negated or not — `tracking issue: owner/repo#N`, never
`<verb> owner/repo#N` — and a cross-repository task keeps its tracking
issue open this way until every one of its pull requests has landed, and
somebody closes it by hand.

**Adjacency is the test, and an issue's timeline is what measures it.**
A verb the number does not immediately follow does not fire the parser:
`btclib-org/.github`'s `c6c1657` reads `none is resolved here; what it
found beyond them is #153`, and its `214ed5f` reads `Which of these
fixes survives a future hand-copy, per #39`, and each entered its
issue's timeline as `referenced` where `592f1bc` above entered
`btclib-org/.github#81`'s as `closed`. Both are unconfounded, which is
what a citation here has to be: `#153` stayed open four hours past
`c6c1657` and was closed by a different landing, and `#39` is open
still — where a commit whose own pull request closes the issue through
its body records `referenced` whether the keyword bound or not, and
proves neither. In both, a newline separates the verb from the number —
and that a newline alone breaks the binding, in a keyword meant to fire,
is btclib-org/.github#420's subject.

**Two parsers read a closing keyword, and a newline is where they part.**
One answers `closingIssuesReferences` and reads the pull request's
description; the other closes on a push and reads the message that
landed. A physical line is what the first requires, and #420's
measurement is of that one. It is not reproducible, the pull request it
was taken on having been corrected before it merged, and what stands in
its place is a pair of negations, read on 2026-08-30:
`btclib-org/.github#510` says `does not close #466` on one line, its
only mention of that issue, and `closingIssuesReferences` names it;
`btclib-org/bitcoin-core-rpc#182` says the same negation at the end of
a line with `btclib-org/btclib#1157` beginning the next, and the same
read answers empty. The two differ in the reference form as well as in
the newline, and the sweep below is what controls for that: its
adjacent hits carry the bare and the qualified form alike and are
parsed alike, so the newline is what is left between the pair. The most
recent pull requests of every repository in the organization are asked
the same question:

```shell
gh pr list --repo <org>/<repo> --state all --limit 200 \
  --json number,body,closingIssuesReferences
```

— the verbs reaching a reference on one line being the positive control,
without which the absence of the others measures nothing.

**The second parser crosses the newline, and a `closed` event's commit
id is what says so.** That field carries a sha where the push closed the
issue and null where the description did:
`btclib-org/btclib-secp256k1#366` names `btclib-org/.github#81` with no
verb anywhere in its description and `closingIssuesReferences` empty,
and the close of #81 carries `592f1bc`; `btclib-org/.github#504`'s
squash message carries no keyword at all, its description closes #477,
and that close carries no sha. So `btclib-org/btclib`'s `825c74e2` is
the measurement of the second parser on a newline: it writes `closes` at
the end of a line and `btclib-org/.github#402`, its only occurrence, at
the start of the next, and the close of #402 names that sha. Where both
parsers could fire, the event records whichever did, so a null there
says nothing against it.

**So the keyword and its reference share a physical line, and a block of
several is written one keyword per line.** That is the description
parser's requirement stated where a wrapper can break it rather than a
second rule: this section asks each issue for its own verb and section 9
wraps prose at eighty columns, and a body that follows both as one long
line loses precisely the keywords the wrap splits, every one of them
individually well-formed, the text reading correctly to a person and
only the API answering short. One keyword per line is the shape a wrapper cannot
split, and no formatter is let reflow the block. What catches a loss is
counting the registrations against the number intended. `<n>` sits last
for the reason section 9 gives:

```shell
gh pr view --json closingIssuesReferences \
  --jq '.closingIssuesReferences | length' <n>
```

The failure is stable, so asking twice answers only the indexing lag —
a five where eight were meant reads exactly like a correct answer for a
smaller set, and only the count knows what was meant.

**What is not measured here is a gap on one line**, a verb and a number
with only text between them; no commit in this tracker isolates it, and
not for one reason — a same-line instance closes at that same merge
through its pull request's body, or lands against an issue closed hours
earlier by something else, or names a pull request or another tree's
number. Read the rule as adjacency and write to it, rather than as a
licence to put a verb on the same line as a number it must not close:

```shell
gh api repos/<org>/<repo>/issues/<n>/timeline --paginate \
  --jq '.[] | select(.commit_id != null) | {event, commit_id}'
```

So a rule forbidding a keyword verb anywhere ahead of a reference
forbids a shape the forge does not act on, and a sweep written to it
reports landings that closed nothing. What covers the doubt is the
`closingIssuesReferences` read below rather than a wider rule, it being
an answer about the pull request in front of you.

**A manual link carries no form to get right and no keyword to omit**,
which is what makes it the sharper trap: made by hand in the
Development panel, it closes its issue on merge regardless of
repository, and it appears in no diff, no commit message and no
description, so every surface a reviewer reads can say the opposite of
what merging will do. `btclib-org/bitcoin-core-rpc#178` carried exactly
such a link to `btclib-org/btclib#1160`, confirmed by
`closingIssuesReferences`, while its own body said in as many words
that it did not close that issue. Merging #178 did not close #1160
either: the issue had already been closed by hand, deliberately, once a
maintainer found the same undisclosed link on two more pull requests
racing it. What kept the sentence from being false is a person noticing
in time, not the mechanism — the link would have closed #1160 on merge
had #178 landed first.

So **what a pull request closes is read before it is merged**, from the
one place that answers. The variables follow the query, which puts `<n>`
last for the reason section 9 gives:

```shell
gh api graphql -f query='
query($owner:String!,$name:String!,$num:Int!){
  repository(owner:$owner,name:$name){
    pullRequest(number:$num){
      closingIssuesReferences(first:10){
        nodes{number repository{nameWithOwner}}}}}}' \
  -F owner=<org> -F name=<repo> -F num=<n>
```

An issue there that the description does not name is the finding, and a
cross-repository one is the finding this rule exists for: a tracking
issue closed on the first of three repositories leaves the other two
answering to nothing.

**That read describes the pull request, not what a squash will land.**
`closingIssuesReferences` reads the description as it stands when the
call runs, and a squash lands a second, separately authored text — the
commit message composed at merge time, in a field the description never
populates. `dde42cd` (PR 512) is the gap made concrete: the pull
request's title read `(issue #468)`, its body's first line said why —
one of three *Done when* items, the others sibling copies — and
`closingIssuesReferences` answered empty for #468. Landing it, the
maintainer typed `(closes #468)` into the squash subject, a text the
description-based read never sees, and #468 came back CLOSED on it:

```shell
gh api "repos/btclib-org/.github/issues/468/timeline?per_page=100" \
  --jq '[.[] | select(.event=="closed" or .event=="reopened") |
         {event, at: (.created_at | fromdateiso8601)}] | (.[1].at - .[0].at)'
# 38
```

— reopened by hand thirty-eight seconds later, the number the command
above prints rather than one read off the page. Nothing in the pull
request was wrong, and `closingIssuesReferences` answered correctly for
the object it reads; the squash subject is a different document,
written after that read, and no pre-merge check reaches a document that
does not exist yet.

**So the read is taken twice: `closingIssuesReferences` before the
merge, as above, and, for every reference the landed commit's own
message names, the per-issue timeline read given above, after it.** A
`closed` event naming the just-landed sha for a reference the first read
did not name is the finding — #468's shape, caught before it costs a
reopen rather than after.

**The alternative weighed and declined takes the pull request's title as
the squash subject verbatim, rather than composing one, so there is only
one text to disagree with itself.** It is cheaper and removes the
divergence instead of detecting it, but it is a rule about how a person
presses the button, the weaker kind this file already carries one of —
the negation paragraph above — and #468 is what that kind looks like
once broken. Comparing the two reads is a check that runs regardless of
how the button was pressed, which is why it is the one kept.

**The negation paragraph above is checked directly, against the
branch's own commit subjects and bodies, because the forge's two reads
of the same words can disagree.** `f47899a` (PR 491)'s body carried
`This does not close btclib-org/.github#365`; `closingIssuesReferences`
answered empty for it while the pull request stood open, and the issue
still closed once the identical sentence was the landed commit's own
text. Counting that answer against the number you mean to close,
above, is what already reaches a different mechanism —
`btclib-org/portanode#238` quoted another commit's `(closes #188)` in
its own body, and the same read answered three where two were meant, a
surplus the count would have shown had it been read rather than only
printed. Neither reading closes the gap `f47899a` opened, because the
pull request's own description held the same words the push later
acted on differently. What reaches that gap is a read that never asks
the forge at all:

```shell
git log <base>..<branch> --format='%H%x00%B%x00' | python3 -c '
import re, sys
verb = re.compile(r"(?i)\b(close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+"
                   r"((?:[\w.-]+/[\w.-]+)?#[0-9]+)")
fields = sys.stdin.read().split("\x00")
for sha, body in zip(fields[0::2], fields[1::2]):
    for m in verb.finditer(body):
        print(sha[:9], m.group(0))
'
```

run over the branch before it is opened, against the same expectation:
every hit outside the title's own `(closes #N)` parentheses is the
finding, and a number the title carries that the scan does not find is
a closing keyword the title declares that the branch's own words never
state. Its separator is `\s`, which crosses a newline, because the
parser this text will meet is the one that reads a landed message: a
space or a tab would miss the shape `825c74e2` closed an issue with,
which is the shape this scan exists to catch.

### Review

A pull request needs an approving review from somebody other than its
author. GitHub refuses a self-approval, which is why an *author's* own
verdict is a comment and can be nothing else.

**What a landing reads is the ack of record**: a verdict whose last line
is `ACK <sha>`, `CHANGES REQUESTED <sha>` or `NACK <sha>`, naming a sha
because an ack belongs to a tree and not to a branch. `CHANGES
REQUESTED` is the change being right in principle and wrong as written,
and what answers it is another push. `NACK` is Bitcoin's sense of the
word: the disagreement is with the change itself, so no alteration is
asked for and none would earn an ack, and what answers it is an argument
or a closed pull request. A review that delivers no verdict is a reading
and not an unfinished review; `REVIEWING.md` states that distinction,
and why, for whoever reviews.

**The ack of record is posted as a review of type COMMENT**, whichever
of the three it carries — `gh pr review --comment` — and never as a
forge approval or a forge request for changes:

```shell
gh api orgs/<org>/actions/permissions/workflow \
  --jq .can_approve_pull_request_reviews
gh api repos/<org>/<repo>/pulls/<n>/reviews --jq '.[].user.login'
```

The first answers `false`, which closes the route a `GITHUB_TOKEN`
would take, and *Tokens, publishing, scanning* below has why it is set
that way. The second answers `claude[bot]` — a GitHub App's identity,
not `github-actions[bot]` — so that setting is not what governs the
credential in play. What forbids `--approve` here is the prompt saying
never to, `Bash(gh pr:*)` in `claude_args` permitting it otherwise: a
rule of this file held by a sentence in a prompt, and worth naming as
that rather than as a setting. The self-approval refusal above is not
the reason either — it reaches an author, and the workflow does not run
as one.

`--request-changes` is available and goes unused, one shape for the
three keeping the answer in one place: the verdict is the body's last
line, which is what the job's own verification step reads, and a review
type saying something for one verdict of the three would be a second
place for the answer to live and to disagree.

**What the forge then holds is a record of the review and not an
approval.** That second call lists a COMMENT review as it lists any
other, so the rule this file states is visible in an artifact rather
than only here. It does not buy the OpenSSF Scorecard's `Code-Review`
check: that check credits an approval on the forge or a merger
different from the committer, and its own documentation says that a
review by a bot, one powered by a model included, does not count as
code review — so the approval this workflow does not have would not
have satisfied it either. What it asks for is a second person who
understands the change, in its own words, and no workflow is one.

**btclib-org/.github#341 holds the removal of the ruleset's
`bypass_actors`.** The bypass is what lets a merge happen with no
approving review on the pull request, and the workflow's verdict is not
one, so removing it puts a person's approval on the critical path of
every merge. What that buys is the rule enforced by the forge rather
than by whoever is landing, and what it costs is that nothing lands
while nobody is available. That is the trade the issue decides.

**The ack of record is `claude-review.yml`'s**, and an author's own is
not one. A comment from the account that opened the pull request is a
statement that its gates were run — worth having, and not a reading. The
distinction is the whole of why the review requirement exists: an author
verifying their own work cannot find what they did not think to look
for, which is the class of defect a second reader exists to catch. What
triggers the workflow is `opened`, `reopened`, `synchronize` and
`ready_for_review`, and a comment naming `@claude` — that last is how a
head that moved after the review gets a fresh one, since the ack does
not follow the branch.

**The workflow is present and neither of its jobs runs.** Each carries
`if: vars.CLAUDE_REVIEW_ENABLED == 'true'`, an organization variable:

```shell
gh api orgs/<org>/actions/variables --jq '.variables[].name'
```

It names nothing, and an undefined `vars.X` is the empty string, so the
absence is the off state and creating it with that value is the whole of
what a tree carrying the gate needs to start reviewing. Nothing else has
to be written that day, which is why the file is kept current rather than
deleted from a tree and written into it a second time. A tree whose gate
is off carries no ack of record, and what a landing reads there is
whatever reading a person made. The switch is the organization's rather
than each repository's because one setting is one thing to remember: a
variable per tree is one that can be set in some and forgotten in others,
with nothing saying which.

**A pull request that adds or edits `claude-review.yml` gets no ack**,
that being the exception the rule above has, until the change is on
`main`; what refuses it is in the workflow's own header, below. That is
not something to work around — it is the honest shape of "no review
happened" — and such a pull request lands on its gates and on a
description saying so. It carries that change alone, since anything
travelling with it lands unreviewed too. The refusal is keyed on that
file, so a pull request touching another workflow is reviewed like any
other.

**A green check is an ack of the head, and nothing weaker.** The job's
last step reads back what was posted and refuses to report anything
else: a refusal, a verdict never written, and an ack naming a sha the
branch has moved past are a red row each. What the row cannot say is
what the review found, which is the comment's to say and is read
whatever the colour.

It is deliberately **not a required check**, and its own header says it
must not become one. Requiring it would make a review a gate to be
satisfied rather than a reading to be answered, and would hand the merge
button to whatever the workflow happened to say. What it is instead is
the thing a human landing the pull request reads before pressing. That
is a different mechanism from the review it posts: a required check is
a context a branch rule names and nothing else can supply, where the
approval a `pull_request` rule counts is satisfied by whoever reviews.

`REVIEWING.md` is the standard: a diff is acked when
it leaves the tree better than it found it, a matter of taste is not a
finding, and work the diff never set out to do becomes an issue rather
than a comment. Every finding is labelled blocking, non-blocking, nit or
question.

**A review pass runs locally against the branch before it is pushed**,
and `.claude/commands/review.md` with no argument is what runs it: the
diff of the current branch against `origin/main`, read against
`REVIEWING.md` as the workflow reads a pull request. It posts nothing,
replaces no round on the forge and is not the ack of record; what it buys
is that the forge's round is the last rather than the first. What it
reaches is what the gates do not — a count nothing re-derives, a bare
cross-repository reference, a paragraph a change elsewhere falsified —
and the count is not reachable by a pattern either, a number being a
defect for what it counts rather than for the string it is. The
distinction the ack of record rests on holds here too: a pass run from
the session that wrote the diff re-performs the author's reading.

**A gate already run on this sha is relied on, and the run is named.**
Where the required checks run beside the review on that commit, or an
author hands over a branch they gated themselves and said so, the review
says whose run it is rather than repeating it; where no such run is on
the record it runs them, and a gate that fails is the strongest finding
available. The sha is the whole of the condition, so a rebase voids it —
the branch was gated and then the tree moved under the gate — and naming
the run is what lets a reader tell a gate relied on from one nobody
looked at.

**What a diff decides with is run, not read.** Where a diff adds
something that decides an outcome by matching or computing — a regex, a
pattern in a hook, a grep, a script, a query — the review executes it,
against the shapes the diff's own prose claims to cover and the shapes
the tree actually holds, and the finding quotes what it printed.
Reading it again is not a second check: the author read it and believed
it. A claim the prose makes about the tree takes the same treatment,
"every link here is already `./`-prefixed" being one `git grep`'s worth
of evidence and the reason a change is offered as safe. None of it is a
run of the gates — those run beside the review on the same sha, or are
the author's to run before pushing — because what the diff adds has
been run against nothing until a review runs it. Where what is at hand
cannot run it — a script or a query wanting an interpreter, where a
pattern against the tree needs only a grep and is the usual case — the
summary says so in those words, that it was not run: a hand trace is
the author's reading performed a second time, and it can carry a
finding but not an ack.

**What a force-push costs is the review attached to the sha it
replaces**, a bot's included, and whether there is one is read before the
push rather than remembered:

```shell
gh pr list --repo <org>/<repo> --state open --head <branch> --json number
gh api repos/<org>/<repo>/pulls/<n>/reviews \
  --jq '.[] | "\(.user.login) \(.state) \(.commit_id[0:8])"'
```

`reviews` is the endpoint that answers, and `pulls/<n>/comments` is the
one that reads as an absence: it counts inline review comments, so a
review carrying none answers zero there and one here. The first command
finding no pull request is the rule's own limit — a reading taken before
one exists is attached to nothing, and no push can orphan it.

**A pull request that exists leaves no window.** `sourcery-ai[bot]`
submits against the head within seconds of one opening — `created_at` on
the pull request against `submitted_at` on the review, read on
2026-08-30 — so a push following the open has no interval in which
nothing is attached yet. That is not the same as every pull request
carrying one, which is why what decides is the read and not the timing.
What carries the correction does not reach this either: an amend and a
commit of its own both move the head, and a review describes the sha it
names rather than the branch. What the read buys is that a review left
pinned to the replaced sha is known to be stale rather than taken for a
reading of the head, and *A green check is an ack of the head* above is
what shows it. The one force-push that stays right is a rebase carrying
no new work.

**The rejected alternative is an ordering rule**: open the pull request
only once a reading has cleared the sha, so that no push ever follows a
review. It needs no read at all, and what it costs is being a rule about
what a session remembers per branch — the weaker kind, for the reason
*What a pull request says it is* gives above — where a session holding
several branches at once has nothing telling it which of them is already
open. The commands above are that same rule as a check that runs.

#### The workflow, and what a port of it has to adapt

`claude-review.yml` is in every repository this file governs, and the
credential is not a repository's to hold:

```shell
gh api repos/<org>/<repo>/contents/.github/workflows/claude-review.yml \
  --silent 2>/dev/null && echo claude-review.yml
gh api orgs/<org>/actions/secrets --jq '.secrets[] | "\(.name) \(.visibility)"'
gh api orgs/<org>/dependabot/secrets \
  --jq '.secrets[] | "\(.name) \(.visibility)"'
```

The first answers with the name or with nothing, and `--silent` is for
the reason section 15's publishing sweep gives.

The token is an **organization** secret at `visibility=all`, so a
repository adopting the workflow configures nothing for it. That is worth
stating because the answer *nothing* is invisible from a repository's own
settings page, and it is the first question a port asks. It is in both
stores for the reason *Dependabot and pre-commit.ci* gives below, and a
repository that configures Dependabot gets a red review on every pull
request Dependabot opens while the second is missing.

**Two of the three things a port must adapt** are claims about the
receiving tree rather than settings. The prompt names `REVIEWING.md`, and
it tells the reviewer that the gates are running beside it on this sha —
so a repository without that file, or without those workflows, needs a
prompt that says something true instead of inheriting a claim about files
it does not have. Copying the workflow faithfully into a tree that has
neither is the same defect as copying any other shared file that
describes one tree, committed by the act of spreading it.

**The third is a citation**, and it is not about the receiving tree at
all. The prompt cites the rules a finding is written against, and this
repository's copy cites `README.md`, this being the tree that holds them;
everywhere else that file is section 2's — what the repository is, to
whoever arrives at it — so a citation carried over verbatim names the
wrong file. A receiving copy cites this standard instead, in one of
these shapes:

- `section 11 of the organization's standard`, where the rule cited is in
  this section and no one subsection of it holds the rule, and wherever
  the sentence is the one that names the standard;
- `section 11's *Review*`, or whichever subsection does hold the rule
  cited;
- `the organization's standard`, with no section number, where the rule
  cited is not in this section.

**What chooses the shape is what holds the rule, never where the
sentence sits.** A copy that shortens to the subsection form after its
first citation is precise and wrong the moment it cites a rule that
subsection does not hold: the two secret stores a Dependabot-initiated
run reads are stated in this section's own prose and in *Dependabot and
pre-commit.ci*, so a citation of them names no subsection at all, wherever
in the file it falls. What a copy does owe its own reader is that the
standard is named in full somewhere in it, since `section 11` alone does
not say which document it is a section of — that, and not the order,
is what a copy citing only subsections fails.

The last shape is the one worth stating, since naming section 11 there
would be precise and wrong. This section is *GitHub settings*, where a
finding about the prose cites section 9 and a finding about a rule
stated without the reason that chose it cites *How to use this file*; a
citation of the wrong place sends a reader further astray for being
precise than a vague one does.

**Why the job has the shape it has** is in the workflow's own header, in
every copy of it: why a missing credential had to be made loud, why the
action's refusal to run under an edited copy arrives as a green skip and
what makes that red, why the fork condition is a fact about secrets
rather than a policy, and why `id-token: write` is required for
something other than what it looks like. That file is where each was
written by whoever was bitten by it, and repeating them here would make
this the second place either can be wrong. What that refusal costs a
landing is above, with the rule it excepts.

**A review reads more than the sha.** The tree it judges is the
commit's; the title and description it judges are what the forge
answered when the reviewer asked, and a correction to either lands
seconds behind the push that fired the run — behind the reviewer's first
read, on the pull request that measured it — so the prompt here has the
reviewer ask again before a finding about them. A correction landing
after that read is invisible to it, and with no `edited` trigger nothing
re-fires, so such a finding cannot clear itself except through a further
push or a `close`/`reopen`.

### Tokens, publishing, scanning

- **The default `GITHUB_TOKEN` is read-only repository-wide**; a job
  needing more declares it, and a caller's `permissions:` block replaces
  the callee's default outright rather than adding to it. This is a
  *setting* and not a property of the workflows, and it is inherited
  from an organization default that ships as `write` — so a new
  repository is writable until somebody says otherwise, and the
  workflow-level `permissions:` block is the braces and not the belt:

    ```shell
    gh api -X PUT orgs/<org>/actions/permissions/workflow \
      -f default_workflow_permissions=read \
      -F can_approve_pull_request_reviews=false
    ```

    `can_approve_pull_request_reviews` matters as much as the token: a
    run that can approve a pull request is a way around the one rule
    that says somebody other than the author approves.

    **The inheritance is one-way, and its absence is unreadable.** A
    repository that sets its own value stops following the organization
    default and there is no way back: the endpoint takes `read` or
    `write` and has neither `null` nor `inherit`, and no endpoint
    reports which repositories carry an override. The only way to find
    one is to move the organization default and see which repositories
    do *not* move — and that survey is blind to any repository already
    holding the new value, which is therefore untested rather than
    known good. So a repository that pins its own is recorded in its
    `REPOSITORY.md`, that file being the one place the fact can live,
    and whoever moves the organization default moves those with it.
- **Secret scanning, its push protection and Dependabot security updates
  are on.** All three are free on a public repository and off by
  default; push protection is the one that refuses the push rather than
  reporting it afterwards.
- **Publishing waits for an approval**: `pypi` and `testpypi` are
  environments requiring a review, and `pypi` is restricted to `v*` tags.
  Trusted publishing via OIDC, so no long-lived token exists.
- **A repository declares `pypi` and `testpypi` where it publishes, and
  no environment besides.** Each of the two is named by a job of the
  release workflow and carries the review the bullet above asks for; an
  environment no workflow names and no protection rule gates does
  nothing the setting exists for, and the endpoint is where it is
  found:

    ```shell
    gh api repos/<org>/<repo>/environments \
      --jq '.environments[] | "\(.name) \(.protection_rules | length)"'
    ```

    **`github-pages` is GitHub's**, created by enabling Pages rather
    than by the repository, and its protection rule is GitHub's too, so
    it is outside the rule above and outside `REPOSITORY.md`: reading it
    back would record a value nobody here can set. Serving Pages is what
    gives a tree the environment, so that answer is read off the
    repository rather than written down.

    Two alternatives are rejected. **Saying nothing** leaves every other
    environment outside the perimeter a `REPOSITORY.md` claims, where
    that file's silence reads as a decision, so each copy would assert
    that whatever is there is fine. **Recording whatever a repository
    holds** writes a stray environment down rather than finding it,
    which is what legitimises it.
- **Code scanning**: the analysis runs from a workflow, and GitHub's
  default setup is *off* — the two cannot both be on, and while the
  setting is on the workflow runs, the analysis completes, and the upload
  is refused. Turning it off has an order that never leaves `main`
  unmergeable: drop the context from the rule, disable the setting,
  re-run, merge.
- **Secret scanning's non-provider patterns and validity checks are
  plan-gated**, and the API answers a `PATCH` with 200 while leaving them
  disabled. The `detect-secrets` hook is the compensating control.

### Dependabot and pre-commit.ci

`github-actions` everywhere — the required check and the review workflow
are every tier's, so every tree has workflows for it to read — and three
more where the tree has what they watch: `uv` where a `uv.lock` exists,
`bundler` where a site Gemfile does, `gitsubmodule` where a submodule
does. The three are conditional by section 2's rule for a subject the
tree does not hold, so a tree with no lock file and no `uv` entry is
keeping this section rather than departing from it. Pre-commit hook
revisions have no Dependabot ecosystem — pre-commit.ci updates them
weekly instead, except a hook whose `repo:` is `local`: `autoupdate`
skips that value entirely, so a version pinned inside one, such as
`.github`'s own `typos`, moves by hand alone.

`gitsubmodule` follows upstream's *default branch*, so its pull request
says that upstream moved and is not the bump: a release pins the tagged
commit by hand. It answers the half the local hook does not — the hook
refuses an unpinned or moved pointer, and says nothing about upstream.

Each ecosystem groups its updates into one pull request, since every pull
request runs the whole matrix. Weekly with a seven-day cooldown: a
compromised release is usually yanked within days, and the sentinel
workflow has already exercised the drift, so each pull request is a small
diff whose result is known. None declares a `target-branch`: without one
the default branch is the target, and a `target-branch` naming a branch
that is not there is not an error anywhere — it is a repository where
nothing is ever proposed.

**A Dependabot pull request reads a different secret store.** GitHub
hands a `pull_request` run whose actor is `dependabot[bot]` the
Dependabot secrets rather than the Actions secrets, so a secret held only
in the second resolves to the empty string on exactly those runs. A
workflow that needs one there needs it registered in both, under the same
name; a workflow that fails loudly on an empty secret is what turns the
omission from a silent pass into a red check.

An action may refuse a bot besides. The review action does, unless the
bot is named in `allowed_bots` — name the one that opens pull requests
here rather than passing `*`, which on a public repository lets any App
permitted to comment start a run carrying a prompt it wrote.

### Pages and Read the Docs

Where a repository serves a site from its own root, the source, the
build type and the CNAME are settings rather than files, and a workflow
builds the same site so that a failure is a red check rather than a page
served broken. Read the Docs' `latest` follows the default branch,
`stable` is the highest release tag, and an automation rule activates
each new tag. The project's public API answers for each of those
without a token:

```shell
p=https://app.readthedocs.org/api/v3/projects/<slug>
curl -s "$p/"
curl -s "$p/versions/?active=true"
```

The first answers with `default_branch` and with `repository.url`, which
says which repository the slug serves. The second comes back with
`latest` as a branch and `stable` as a tag whose `ref` is the highest
release tag, beside the tags the rule has activated — the rule's result
rather than the rule itself, which that API does not expose:
`automation-rules/` answers 404 where an endpoint needing a token
answers 401.

**What connects a repository to Read the Docs is the organization-wide
`read-the-docs-community` GitHub App, not a per-repository webhook**, so
what a repository records on the GitHub side is the installation and an
empty hook list. Both names stand in a block of their own, the
endpoints' paths continuing past them being the position section 9
refuses:

```shell
org=<org>
repo=<repo>
```

```shell
gh api "orgs/${org:?}/installations" \
  --jq '.installations[] | select(.app_slug == "read-the-docs-community")
        | [.app_slug, .repository_selection]'
gh api "repos/${org:?}/${repo:?}/hooks" --jq length
```

`repository_selection: all` is what makes one installation the
connection for every repository at once rather than a setting each tree
carries its own copy of. A hook the second command finds is stale and is
deleted rather than repaired, the App already doing the whole of what it
was for; btclib-org/bitcoin-core-rpc#291 records one that was found and
removed.

The per-repository webhook is the rejected alternative, and the secret
is why: Read the Docs issues it on the project's own integration page
and GitHub returns it masked, so nothing read back from the repository
says whether a hook still carries the right one, and one that has
stopped delivering sits `active: true` while the App carries the build
regardless.

The **slug** is what serves the site, and it is not the project's name:
renaming the project leaves the slug where it was, so a repository
renamed while its documentation was not is a URL that 404s over a build
that succeeds. Renaming the slug is a dashboard action of its own, and
the old one stops answering rather than redirecting.

Get that URL right before a release rather than after, because
`pyproject.toml`'s `documentation` reaches where no pull request does:
the metadata of every version already on the index, and the body of every
release that quotes it. A wrong one is superseded by the next release and
corrected in none of the ones that shipped.

## 12. Releasing

- **Calendar versioning, `YYYY.M.D`.** Between releases the declared
  version is `YYYY.M`, month only, so a checkout of `main` reports itself
  as work in progress. A fourth component exists only for a release that
  shipped broken and cannot be reuploaded. No release candidates: there
  is no pre-release, only a version not yet tagged, and a check refuses
  anything that is not digits and dots. The one exemption is a wrapper
  whose version names the upstream it wraps: `btclib-secp256k1` releases
  `M.N.P` for the libsecp256k1 `vM.N.P` inside it, its own `README.md`
  stating the scheme, because a wrapper dated by its own calendar makes
  a caller read a changelog to answer *which upstream is this*. The
  exemption is this section's rather than an entry on section 14's
  *decided per repository* list, so a future wrapper re-argues it here
  instead of inheriting an answer nobody is asked for — and its fourth
  component means a rewrap of the same upstream, not the broken-release
  meaning above, the two schemes never sharing a tree.
- **A rehearsal on TestPyPI** uses `.dev<run number>`, patched in by the
  workflow rather than typed, so it is unique per run and sorts below the
  release it rehearses.
- **The tag is signed**, is checked to be an ancestor of `main`, and is
  checked to say what `pyproject.toml` says.
- **The release pull request closes the cycle's sections and opens the
  next.** It retitles the work-in-progress section of `CHANGELOG.md` and
  of `RELEASE_NOTES.md` to the version being tagged, and opens an empty
  work-in-progress section above them in the same pull request, so the
  topmost `##` heading of either file on the default branch is a
  work-in-progress heading at every commit and a branch landing across a
  release day has an open section to append to. Opening the next cycle
  in a pull request of its own, ahead of anything else landing, is the
  rejected alternative: the window it leaves is one pull request wide,
  and the merge freeze that covers it is a rule about how a person
  sequences merges on the day several branches are in flight, enforced
  by nothing, where retitling and opening together leaves no window to
  sequence around. The next generic version does not travel with the
  retitle: the tag is checked to say what `pyproject.toml` says, above,
  so a pull request that released and bumped at once would cut its tag
  on a tree declaring a version that tag does not name, and the version
  bump stays in the pull request that sets it. The empty section is
  not what a release publishes: the notes are lifted from the section
  whose heading is the tag's own, which is the one just retitled.
- **A published sdist reproduces from its tag.** The attestation every
  publisher attaches vouches for bytes, so a release rebuilt from the
  commit its tag names — by running what the release ran — gives those
  bytes back, or the attestation vouches for something no rebuild can
  check. What the release ran is the repository's to state and this
  file's to require: `RELEASING.md` names the steps between the tag and
  the archive with the reason beside each, so replacing one of them is a
  change to that file and not to this one, where a rule naming the
  script of the day would date itself the day it is replaced. Section
  3's backends already differ underneath it — `uv_build` ignores
  `SOURCE_DATE_EPOCH` and writes fixed member metadata into both
  archives, where hatchling reads the variable and writes a constant of
  its own without it — and what either publisher owes is the same. The
  released bytes are that pipeline's output rather than the backend's: a
  normalization step run after the build replaces the member metadata
  the backend wrote, so the digest the attestation signs is the step's,
  and not a belt over a backend that fixes that metadata on its own. On
  `bitcoin-core-rpc` the step moves every member's mtime from `0` to the
  tagged commit's second and the digest with it, btclib-org/.github#140
  having the figures, so a publisher that runs such a step and one that
  does not attest different bytes of the same tree rather than making
  one guarantee in two styles. Leaving each publisher to weigh whether
  its backend has made the step redundant is the rejected alternative,
  that being the reading under which a migration drops it as inert and
  moves what the attestation vouches for. `SOURCE_DATE_EPOCH` itself is
  exported from the tagged commit for what reads it — the normalizer,
  and the bill of materials below — and under `uv_build` for nothing
  else, its archives being the same bytes either way. Under hatchling
  the variable reaches the archives too, so exporting it for the bill of
  materials moves the digests the attestation vouches for. The compiled
  wheels are outside the property and are named rather than passed over.
  `btclib-secp256k1` publishes two builders' wheels and `release.yml`
  downloads them under one artifact pattern, so the index attests every
  one beside the sdist, PEP 740 covering every file the publish job
  uploads, and a verifier who rebuilds one and gets other bytes has
  nothing to tell them whether that is a defect. One tool does not
  rebuild both: cibuildwheel builds the `cp3XX` and `pp3XX` wheels
  against a compiler and a toolchain nothing pins, where the
  `py3-none-*` wheels are cffi ABI-mode builds `python -m build` writes
  on the runner, and cibuildwheel run against one of those produces a
  file of another name rather than other bytes. What is measured is
  narrower than what either builder writes: `wheel-reproducibility.yml`
  builds one interpreter's wheel twice in one image and diffs the
  archives, and whether a wheel of another ABI tag reproduces is
  measured on no trigger — the published `py3-none-*` ones being
  btclib-org/btclib-secp256k1#540. Saying nothing about the wheels is
  the rejected alternative for that reason, an attestation
  reading as one guarantee over every file it covers. Pinning the
  environment so they reproduce across two of them is the other, and in
  the tree that compiles them it is one measurement across the platforms
  rather than one decision: a digest on the container the Linux build
  compiles inside states that environment to anybody who can pull it,
  which is btclib-org/btclib-secp256k1#524, where Xcode and the MSVC
  toolset are chosen from what a runner image already carries, so the
  same pin on macOS and Windows states nothing to a verifier who was
  never on the machine and is declined rather than pending —
  btclib-org/btclib-secp256k1#554. Nothing yet re-derives the property
  on a released tag — the command that rebuilds one and verifies it
  against the attestation is one a person runs — and that half is
  btclib-org/.github#523's.
- **A bill of materials is published beside the distribution files**,
  by every publisher, and the attestation signs it with them. One answer
  rather than an answer and its exemptions, for the reason every
  publisher signs: a consumer reading the organization's releases should
  not have to learn which of them describes itself and why. What makes
  it reproducible is the variable the bullet above exports for it: its
  timestamp is `SOURCE_DATE_EPOCH` and its serial number derives from
  the distribution files' digests, so a rebuild of a released tag writes
  the same document and the attestation verifies it exactly as it does
  the archives. The exemption that carried weight was
  `btclib-secp256k1`'s — a document naming only
  `cffi` where the package's content is a C library at a pinned commit
  invites a reader to trust a silence — and it is an argument about the
  generator, which btclib-org/btclib#1280 has describe what a
  distribution contains rather than what it declares, not one against
  the document. `bitcoin-core-rpc`'s was weaker: `components: []` is
  true rather than misleading, and a signed statement a consumer can
  read is not the assertion inside a run that consumer never sees.
  btclib-org/.github#144 carries the trees that still owe one.
- **What is published is inspected first** — `twine check --strict`,
  `check-wheel-contents` and `pyroma --min 10` on the files the release
  will publish; then the wheel is installed from an empty directory and
  smoke-tested, so the import finds the wheel and not the source tree.
  Those read a distribution's *metadata*, and an unconfigured
  `check-wheel-contents` reads the wheel's own `RECORD`, which is the
  wheel's account of itself: none of them asks what the tree the wheel
  was built from has. A `py.typed` dropped by a `package-data` typo gives
  a wheel that installs, imports, type checks as `Any`, and passes all of
  the above.
- **So the wheel is diffed against the package tree it claims to carry**,
  in both directions, and where that tree is the whole of the wheel's
  library the diff is `[tool.check-wheel-contents]` naming it — a line of
  configuration rather than a check to write, test and keep in step with
  a page. Where the wheel is *not* one package tree, that flag has no
  wording for it: a compiled artifact at the wheel's own root is reported
  as a file outside the package whether or not it is the one the build
  intends, and the repository owes a script saying what the flag cannot,
  its allowlist stated in prose and compared against the script's
  constants by a test, in both directions, so neither is free to drift.
  Some other check implying the same diff does not stand in for the flag
  where the flag applies: that is the same assertion bought with code to
  maintain, and it moves what the `dist` job knows about the artifact
  into a chain that holds only while every link runs.
- **The sdist is diffed against what git tracks**, in both directions, by
  `check-sdist` in the gate of every repository that builds one. It
  builds the archive and compares it against the index, and its exit code
  says which way the two differ: a tracked file the archive dropped, or a
  member git does not track. The first is an include list's failure — a
  tracked file nobody added to `source-include` — and it is silent. The
  second is an exclude list's, and it is not loud either: an archive too
  wide is noticed by whoever reads the archive, and nothing else in a
  release path does, `twine check`, `check-wheel-contents` and `pyroma`
  each reading a distribution's account of itself, so a local build
  artifact or a vendored tree mid-update reaches the index with nothing
  asking. Both directions being quiet is why the check is not conditional
  on the inclusion being an include list, and what it costs an
  exclude-list tree is a `[tool.check-sdist]` table naming the tracked
  files its archive leaves out on purpose. Which table declares the
  inclusion is the backend's: `uv_build` reads `[tool.uv.build-backend]`
  and hatchling `[tool.hatch.build.targets.sdist]`, neither reads the
  other's, and a table the declared backend does not read is
  configuration that looks like a rule and governs nothing. So
  `check-sdist` keys a plugin on `[build-system]` and reads that
  backend's own exclusions, which is what leaves `[tool.check-sdist]`
  holding only what no pattern of the backend's accounts for. Past that,
  an allowlist for the sdist — which members may sit at the archive's
  root, that every member is a regular file or a directory where a tar
  can carry a symlink or a device node, that no directory holds another
  distribution's metadata — is the escalation a repository takes when its
  archive carries more than the package.
- **A hook that builds the project builds it with the backend
  `[build-system]` admits**, and what that takes differs between the two
  hooks, because only one of them builds through PEP 517 at all. Both
  build without isolation, pre-commit.ci being unable to create the
  isolated environment.

    `pyroma` reads the metadata through
    `build.util.project_wheel_metadata`, and its non-isolated path never
    reads `requires` at all: there is no `check_dependencies` call on
    that branch, so it returns metadata once the backend's own PEP 517
    hook does, whatever else the list names. What falls back to an
    isolated build is pyroma's own wrapper, on a `BuildException` from
    that first attempt — so the hook carries `additional_dependencies`
    naming the backend at `[build-system]`'s own specifier: that keeps
    the backend importable, which is what the first, requires-blind
    attempt needs in order not to raise, and the fallback — a virtual
    environment pre-commit.ci cannot create — is never asked for.
    btclib-org/.github#145 has the run.

    `check-sdist` drives `uv build`, and that is not PEP 517 for this
    backend: given `build-backend = "uv_build"` it builds with the copy
    bundled in the running uv, whether or not isolation is disabled and
    whether or not the environment holds a `uv_build` at all. Where
    `requires` excludes that uv with a ceiling below it, it warns and
    builds with the bundled copy anyway; where the exclusion is a floor
    above it, uv looks past its own copy for a `uv_build` meeting that
    floor instead and the build fails when none does — `import uv_build`
    raising `ModuleNotFoundError` under `--no-build-isolation`, the shape
    this hook takes. Either way naming the backend there decides
    nothing, the target environment's own `uv_build` being what neither
    branch consults, and what packs the archive the gate compares
    against git is the hook environment's `uv`, which the manifest
    installs unpinned. `args: [--inject-junk, --installer=pip]`
    is what brings the hook under the rule: check-sdist then builds
    through `build --no-isolation`, which does read the environment, so
    the backend `additional_dependencies` names is the one that packs
    the archive. `--inject-junk` is repeated because `args:` replaces
    the manifest's list rather than adding to it, and uv's own
    `--force-pep517` is out of reach, check-sdist writing that command
    line itself.

    **What the failure keeps is the hook environment inside `requires`**,
    which is the whole of what this bullet asks: `build --no-isolation`
    refuses an environment that does not satisfy it — `ERROR Missing
    dependencies` — so the backend that packs the archive is one
    `[build-system]` admits or there is no archive. It does not keep the
    two specifiers equal, and nothing does: a specifier written in two
    files is still a range that drifts when the ceiling is raised in one
    of them, and a `requires` widened past the hook's line leaves that
    line satisfying it and green. That half btclib-org/.github#145 leaves
    open, there being no bot to close it — section 10 has why hook
    revisions have no Dependabot ecosystem, and what bumps a `rev` leaves
    an `additional_dependencies` specifier where it is. Pinning `uv` on
    the hook is the alternative, and it is what the default path would
    need, the driver being the backend there; it is refused because it
    leaves even the first half silent, a `uv` pinned outside `requires`
    warning where the `pip` installer refuses.
- **A release is checked against the last one for a break in the public
  surface**, by `griffe check` in the release path, comparing the tag
  being cut against the tag before it. Section 7's public-surface census
  asserts that `__all__` is declared and that what it names exists,
  which answers *is this module's surface stated* and never *did this
  release take something the last one gave*; `RELEASE_NOTES.md` is where
  a caller is told to act and is written by hand, so nothing in the tree
  can tell that an entry is missing. `griffe check` walks the public API
  of two git references and reports what broke, each finding named by
  the kind of break it is — a public object removed, a parameter's
  default or kind changed, a parameter added as required, a return or
  attribute type no longer compatible, a public name now pointing at a
  different kind of thing — and it exits non-zero having found any. It
  loads each reference from a git worktree of its own rather than from
  an installed distribution, so a pure-Python tree needs nothing built;
  and it is the loader `mkdocstrings` reads a Python API with, which is
  what makes it a maintained tool rather than a script somebody wrote
  once — it is a dependency taken on for this and nothing else here, and
  that is the cost. What it reports is either a
  `RELEASE_NOTES.md` entry or a reason for not being one, written where
  the release is being written.

    **The release path and not the merge gate**, which is the choice
    worth stating because the second is the one that reads as stricter.
    A gate comparing the branch against the last release makes a
    caller-visible break a decision taken in the pull request that makes
    it, and before 1.0 a package breaks its surface deliberately: a gate
    that reports every such break has nothing to say about which of them
    are allowed, so every run ends in a human deciding — which is the
    release path's answer arriving earlier and more often rather than a
    stricter check. It becomes a gate the day btclib-org/btclib#651
    settles a deprecation policy and not before, that policy being the
    missing half — the question stops being *did the surface change* and
    becomes *did it change without the release of warning the policy
    owes*, which a command can answer on its own. So the release path's
    invocation is written to take a second reference pair rather than to
    be replaced by one.

- **A job named in `needs:` that is not a gate takes `always()` in the
  dependent's own guard**, beside an explicit `needs.<job>.result ==
  'success'` for each listed job that is one. The public-surface check
  above is such a job: it exits non-zero on any break, which is what a
  cycle before 1.0 is expected to produce, and `needs:` alone refuses to
  start a job whose listed dependency failed or was skipped. Listing it
  orders the reading before the upload, and the guard is what says the
  reading's result decides nothing. `always()` here and not the
  `!cancelled()` section 10 gives an aggregate: what that section weighs
  `always()` against is a superseded run turning a required check red,
  and a release workflow, triggered by a tag push and a dispatch,
  produces no required check.
- **The widening does not propagate, so each dependent states it for
  itself.** A bare `needs:` reads back through the listed job's own
  `needs:` chain, so a job two hops from the non-gating one is skipped
  although the dependency it names succeeded — which is how a
  post-publish check comes to be skipped by a job it does not name.
  Putting `always()` on the non-gating job itself is the rejected
  alternative and moves nothing: what a dependent reads is that job's
  result, and a job that ran and failed stops it exactly as a skipped one
  does. Dropping it from `needs:` is the other, and it costs the
  ordering: the surface is then read beside the upload rather than before
  it, which is a reading arriving too late to bear on the release it was
  written for.
- **A release run is audited job by job for `skipped`, not for red.** A
  failed job is loud; a skipped one carries no step, starts and completes
  in the same second, and gives a reader looking for a failure nothing to
  look at, so a release whose post-publish check never ran reads as a
  release that finished. What answers is the run's own job listing — the
  endpoint section 10's aggregate reads from inside its run, asked here
  of a run that has ended. The run id is quoted for the query string
  beside it, so the assignment stands in a block of its own, for the
  reason section 9's bullet gives, and the block below it writes
  `${run:?}`, unset being what an unfilled paste of that block alone
  supplies:

    ```shell
    run=<id>
    ```

    ```shell
    gh api --paginate \
      "repos/{owner}/{repo}/actions/runs/${run:?}/jobs?per_page=100" \
      --jq '.jobs[] | [.conclusion, (.steps|length), .name] | @tsv'
    ```

    read against the jobs the release was expected to hold. Auditing for
    red alone is the rejected alternative, and it is what a reader does
    unprompted: it finds whatever went wrong and says nothing about what
    the failure took with it.
- **The smoke test runs again in the release job, without constraints**,
  after the upload rather than before: installing a dependency executes
  its code, and a compromised one must not reach a `dist/` still to be
  handed on.
- **A scheduled workflow installs from the index** and asks whether the
  published artifact *works*, not whether it installs — an import runs
  `__init__.py` alone, where a data file missing from the wheel is opened
  only at the first call that needs it.
- **That workflow is where the post-publish check lives, called by the
  release as a job of its own, and never a step appended to a publish
  job.** A publish job downloads the distribution files and hands them to
  `pypa/gh-action-pypi-publish`, so nothing in it provisions a toolchain:
  what the runner carries is whatever its image ships and nothing the
  tree chose — no `uv`, and an interpreter at the image's version rather
  than at the one `requires-python` asks for. A step appended there
  provisions its own or fails in one of two ways: on the command's name
  where what it calls is `uv`, `127` being the shell's answer to a
  command that is not there, and on the interpreter's version where it
  is not — or, where `requires-python` admits the image's version, it
  passes on an interpreter the tree did not choose, which says nothing.
  Neither failure names the runner as its cause. The reusable workflow
  provisions its own toolchain, so nobody placing the check there has
  to know either.
- **Placement also decides whether the failure is legible.** Both
  placements run after the upload, so either can only report an act
  already irreversible — a filename on the index is not retractable. A
  job that fails is a row of its own in the listing above, red beside a
  publish job that stayed green; a step that fails turns the publish job
  itself red, and every job guarded on that job's `success` skips with
  it — the attestation and the GitHub release among them — leaving a
  release published, unattested and unannounced behind one red job that
  names none of it.
- **The check reads the index for the version the tag names**, so a first
  release is no different from any other: the call passes the tag, the
  wait holds until the index serves that version, and it fails on its
  deadline rather than let the matrix install the version the tag
  replaces. Inlining the check because the index has nothing to read
  before a first release is the rejected alternative, and what it answers
  is a different run: the release's own call runs after its upload, and
  what has nothing to read is the schedule, which passes no version,
  waits for nothing and installs whatever the index serves at the time. A
  rehearsal has no such job either — the check reads the release index,
  and what a rehearsal exercises is the publish step rather than what an
  index then serves.

Worked answers, each named for the property of its distribution that
decides it rather than as a shape to copy, and each re-derived by section
15's tree commands rather than taken on trust. `bitcoin-core-rpc` points
`package` at its package directory and stops there — measured against a
wheel built with `py.typed` stripped and `RECORD` edited to match, which
installs and imports cleanly and which the unconfigured tool passes —
because a single-module package with no data directory has no member that
the flag and the sdist check between them leave unpinned.
`btclib-secp256k1` has no package to name: every wheel it ships carries a
compiled artifact at the wheel's own root, so it keeps `ignore = ["W003",
"W009"]` for the top-level member that is not a mistake, and its script
asks what the flag has no wording for — which artifact a wheel of that
tag must carry, and that it is not the zero-byte one a half-finished
build step leaves behind. Its sdist target is an exclude list, so what
`check-sdist` costs it is the `[tool.check-sdist]` table naming the
tracked files its archive leaves out on purpose, and what the check buys
it is the case a check conditional on an include list would exempt: a
file git does not track reaching the index through an archive nothing
else reads, the vendored library's tree included, since the check lists a
submodule's files with git's own. `btclib`'s `source-include` is a glob
include list and its archive carries the suite and the vendored vectors,
so what the same check catches there is the silent half — a tracked file
the list never named — and which files may sit at the root and what kind
of member the tar holds are the questions nothing it runs otherwise asks.

## 13. Editor and agent configuration

`.vscode/settings.json` and `.vscode/extensions.json` are tracked and
hold no preference. Every recommended extension is a tool the lint gate
already runs, and the settings put the fixing ones on save: what the
editor fixes is what the hook would have fixed, so nothing reaches
`git commit` for the first time there. An extension with no hook behind
it is a second opinion nothing enforces, and the reflex installs that
would fight a hook are listed as `unwantedRecommendations`. Anything
machine-local belongs in the editor's own user settings.

**`mypy-type-checker.importStrategy` follows section 4's branch**, and
getting it wrong is silent both ways. With the local hook it is
`fromEnvironment`: the mypy the extension bundles is a different version
from the locked one, and an `enable_error_code` name it does not know is
dropped with a warning no extension surfaces. With the mirror it is
`useBundled`, there being no project mypy to point at — `fromEnvironment`
against a `.venv` without one reports nothing at all rather than failing.
That branch leaves the editor reading a different mypy from the hook's:
the bundled one is not the version the `rev` pins either, and it has none
of the stub packages `additional_dependencies` installs, so an import the
hook resolves is unresolved there.

The exception is a package that is a **compiled extension**, and it goes
the other way: the mirror's isolated environment has no built extension,
so the import does not resolve there and the editor cannot use that
environment whatever the hook does. It reads the project's instead, which
`uv sync` built the extension into — so `fromEnvironment` under the
mirror, and the version equality section 4 asks for is what makes the two
the same mypy rather than merely both present.

`CLAUDE.md` carries what an agent cannot read off the tree — the
non-obvious failure modes, and the rule that a session never works in the
maintainer's own checkout — a worktree per session, and never `git stash`
in one, `refs/stash` being shared across worktrees. `.claude/` is tracked
beside it, with the same argument as `.vscode/`.

## 14. Copied verbatim, and decided per repository

**The same file in every repository**, and deliberately so — prose and
configuration move between them, and a paragraph that lints in one has to
lint in the others. Each bullet opens with its subject, the path, and
then with who owes a copy: `owed by every repository`, or `owed where`
and the condition. The first is what `tests/verbatim_test.py` of this
repository asks of every tree, so that one short of a copy is a finding
rather than a tree the comparison passes over; the second is prose, and
a tree the condition does not reach is absent and correctly so. The
paths are what that test compares:

- `.markdownlint.jsonc` — owed by every repository; no rule disabled.
  What it names is a style where markdownlint's default is "consistent",
  which asks each file to agree with itself and therefore lets two files
  disagree.
- `.yamllint.yaml` — owed by every repository; the default set, extended
  rather than listed, with `line-length` raised to 100 and two rules
  disabled, and `document-start` raised from the default's warning to an
  error because the hook runs no `--strict` and a warning exits 0.
  Extending is what makes it a rule set at all: yamllint enables
  no rule a configuration does not name, so a file that lists rules and
  extends nothing runs those alone and leaves indentation, trailing
  whitespace and duplicate keys off under a gate that still passes. The two
  disabled rules carry the reason beside them, `comments` because dependabot
  writes the spacing it objects to and `truthy` because the `on:` a workflow
  opens with is the spelling GitHub Actions requires.
- `.taplo.toml` — owed where the tree holds a `toml`; four-space indent,
  `reorder_keys` left false because the order of a table is an argument,
  `array_auto_collapse` false so that adding an entry is a one-line
  diff.
- `COPYRIGHT` — owed by every repository: the notice every source file
  opens with, three lines naming the holder and pointing at `LICENSE`,
  and the source the `notice-rgx` of section 5 is transcribed from. A
  repository file and not a distributed one, so it is not in
  `license-files`: `LICENSE` carries the holder for whoever has the
  archive, and a header's source text is read by the gate and by nobody
  who installs the package.
- `LICENSE` — owed by every repository: MIT, the holder named and no year
  range. A range is a line nobody updates, and `COPYRIGHT` states the
  holder without one, so the two would disagree the first January nobody
  remembered.
- `.claude/commands/review.md` — owed where `REVIEWING.md` is: it is the
  invocation and not a second copy of the standard, and it stays a
  file of its own rather than folding into `CLAUDE.md`, which is read by
  every session including the one that wrote the diff.

**Verbatim in part**, the file around it being the repository's own and
so nothing a comparison by path can do: the `ci:` block of
`.pre-commit-config.yaml`, the mypy strictness block, the ruff width and
complexity settings, the pytest strictness flags, and `fail_under = 100`.
Of the `ci:` block, `autofix_prs`, `autoupdate_commit_msg` and
`autoupdate_schedule` are the shared part, with the values section 4
gives; `skip:` is the repository's own, because it names hooks of that
file that pre-commit.ci cannot run, and a hook the repository does not
define has no place in it. `tests/verbatim_test.py` compares none of
these, its subject being a path: what holds a part equal across the
copies is that each was written from this file, and that a command of
section 15 greps for it, which none does for the `ci:` block.

Whole files are here too, and these say in themselves where the
comparison stops:

- `CONTRIBUTING.md` — owed by every repository, and the same file in each
  **up to `## This repository in particular`**. Under that heading are
  the commands and the gates of that tree, because a human should not
  open an agent's file to learn how to run one — which is what holding
  them in `CLAUDE.md` asked.
- `REVIEWING.md` — owed by every repository, and the same file in each
  up to the same heading, a review that means one thing in one tree and
  another in the next being no standard. Under it is what a review of
  that tree checks beyond the generic.
- `.gitattributes` — owed by every repository: the two `merge=union`
  entries, the reasoning beside them, and section 9 as where the rule is
  stated. The attributes a tree needs for files only it carries —
  `portanode`'s binaries and line endings — go under the same heading,
  which is a comment to git and the marker to the comparison, so that a
  rule for one repository's paths is not a copy for every other to drift
  from.

`tests/verbatim_test.py` compares what precedes that heading where a file
carries one, and the whole file where it does not, each ending at a
single newline — so the marker is the declaration, the blank line a copy
puts before it is a spelling rather than content, and there is no second
list of exceptions to keep in step.

`AUTHORS.md` is owed by every repository and differs in two ways that
are the repository's own. It points at **that repository's** contributor
graph: a single shared pointer would be accurate only while one graph
stays a superset of the others, and would leave the first person to
contribute somewhere else uncredited in silence. And a tree that vendors
somebody else's work attributes it here, which is what the file is for —
`btclib-secp256k1` says that the vendored libsecp256k1 is not its work,
carries its own licence and its own authors, and is only ever read from.

It is named in prose and not as a bullet deliberately: a file meant to
differ per repository can never satisfy a byte comparison, so listing it
above would buy an assert with no state in which it closes.

`CODE_OF_CONDUCT.md` is out of the list for the opposite reason: there is
one copy of it, in this repository, and a comparison needs two. What the
bullet was for is had another way — the organization advertises a single
policy because there is a single file, rather than because every copy of
it agrees with this one.

`claude-review.yml` is owed by every repository section 11 governs, and section
15's existence loop is what checks that — not this list. `CONTRIBUTING.md` and
`REVIEWING.md` earn a bullet because this repository's own copy of each is a
receiver exactly like every other tree's, which is what
`tests/verbatim_test.py`'s comparison assumes. `claude-review.yml` has no such
copy here: this repository is the standard the workflow reviews, so its prompt
and a receiving copy's differ by the adaptation section 11's *The workflow, and
what a port of it has to adapt* states. A bullet here would put this
repository's own copy in the comparison too, and it
would fail forever rather than the way `EXPECTED_DRIFT` expects: that table
records a copy a fix converges, not one that cannot by design.

Whether the receiving copies must otherwise read alike is open, not decided
here: `btclib-org/.github#267` raised it, with a drift that has no named
adaptation behind it — a boilerplate cross-reference worded three ways, and one
tree missing the qualifier section 9 requires — and `btclib-org/.github#35`'s
reusable-workflow consolidation could make the question moot by removing the
copies rather than by comparing them. No command in this repository checks it
either way.

A per-file exception belongs in that file's own
`markdownlint-configure-file` comment, not in the shared config read by
files that never trip the rule it relaxes.

**The default is one answer for every tree.** A convention that differs
between two repositories and appears on neither of section 14's two
lists is a defect, not a choice either tree gets to keep: it is filed in
this repository's issue tracker, by *What this repository is*'s shape
for a cross-repository finding, and which answer is right is decided
once, here, and ported.

**Getting onto the per-repository list below takes a reason of one
kind**: something true of that repository that makes the shared answer
wrong — its Python floor, the shape of its distribution, what it ships,
what its tests are about. Every entry on the list carries one. *This
tree already does it differently* is not such a reason: precedent by
accretion is exactly how a standard stops being one, and it is how the
`CHANGELOG.md` citation forms section 9 now settles came to diverge in
the first place.

**Decided per repository**: `requires-python` and `.python-version`; the
matrix breadth; which optional workflows exist past those section 10
keys on a property of the tree; the ruff `ignore` list's
entries a tree declines on its own merits and its `per-file-ignores`; what
a publishing repository checks about its package contents past section
12's floor —
the sdist allowlist, and the script a wheel that is not one package tree
needs — which follows the shape of that project's own distribution and
is settled by measuring it, not by copying what a sibling does; the
convention tests, which each project chooses on section 7's terms; and
the `[tool.uv.sources]` table, which exists only while a dependency is
not on the index and goes the day it is.

`.gitignore` is decided per repository and so outside the compared list
above: what a tree ignores is what its own build and tools write. A
package that compiles an extension ignores the object files and the
shared library it links; a tree whose `dist` job writes a bill of
materials ignores the directory it lands in; a tree that installs
nothing has no build output to name at all. The rejected alternative is
one file copied into every tree, holding the union of what any of them
writes: it grows with every repository added, and a reader of one tree
cannot tell from it which entries that tree needs.

`.github/scripts/check_vendored_vectors.py` is per repository by
subject, and deliberately outside the compared list above: each copy
parses the pin file its own tree keeps, so the bytes differ wherever
the subjects do, which no comparison by path can read as anything but
drift. What every copy owes instead is a header sentence naming what it
parses and where it departs from the siblings of the same name —
`btclib-node`'s workflow already carries one — so a reader holding two
copies knows which difference was decided. Its failure mode is why the
sentence is owed: an entry shape the script does not match is skipped,
the run is green, and the issue it would have opened never opens — so a
fix that is not about one tree's entry shape, a `gh` call or a field
spelling, is carried to every copy in the same campaign, the header
being what says which parts those are.

`tests/conventions_test.py` is per repository by subject too, and outside
the compared list for the same reason: each copy reads the declaration
its own tree keeps, so its rows are that tree's, and so is the `tests/`
root it resolves a declared module against — `btclib-node` keeps its copy
at `tests/unit/conventions_test.py`, a different path and not only
different bytes. What the copies hold in common is a job rather than a
text: read the declaration section 7 asks for and assert that every
convention it names has a module holding a test for it. The header
sentence a copy owes is about this module and not about how its tree
names convention tests: what it reads, and which of its departures are
decided rather than accidental. This repository's copy reads section 7's
list of conventions off `README.md` rather than transcribing it — which a
sibling cannot, the standard being in another repository — and says so.
The failure mode is why the sentence is owed: a defect in the parsing
that shared job needs sits in every copy carrying it and turns nothing
red anywhere, so a fix that is not about one tree's rows or its root is
carried to every copy in the same campaign, which is what
`btclib-org/.github#651` records. A bullet in the compared list above is
the rejected alternative: no two copies are byte-equal and that
comparison is by path, so the bullet would report the copies as drift on
the day it landed and could not reach `btclib-node`'s at all.

## 15. Auditing a repository against this file

Alignment is measured, not remembered. Each command below answers for
one section above.

**Much of it runs on its own.** `tests/` of this repository is a suite
that asks every repository the questions below, one test per question
and one row per repository, so that a run is the matrix and a failure
names the tree and the command that decides it by hand. It asks them
here and not in each tree's own convention tests because what is
measured is agreement with this file, which no tree holds a copy of: a
test there answers for that repository's reading of a rule, and the
rule has moved since. Which section each module reads is that module's
own docstring, and there is no second copy of the list here to keep in
step with it. Which repositories a question is asked of is section 2's
tier, measured off each tree as that section measures it, and a tree the
tier does not bind is skipped with the reason. Which failures the
tracker already records is the backlog in `tests/__init__.py`: those run
as strict expected failures naming the issue, so a repository that
catches up is reported until its row is deleted. `alignment.yml` runs it
weekly.

The commands below are the same questions for the tree in front of you,
and the questions the suite does not ask yet or cannot. Which it asks is
each module's docstring; what it never will is a reading rather than a
comparison — `tests/README.md` against section 7, and the workflow
comments, below. A repository answers for itself where it can —
`interpreters_test.py`, `conventions_test.py`, the hook-pin tests — and
this file is where the rest is written down.

Section 3 states the convention that the classifiers name the
interpreters a tree runs, and says a tree that publishes carries it as
`interpreters_test.py`; this file is what carries it for a tree that
does not: a published tree's classifiers are what an index shows whoever
is choosing the package, where an unpublished tree's declarations are
read by whoever opens the repository. Publishing and not section 1's
library is what decides that, an index showing the three declarations
whatever the distribution on it is. So the ends of an unpublished tree's
window are compared here rather than by a module of its own. The other
answer weighed was dropping the classifiers such a tree shows to no
index, and what that costs is the comparison itself — the floor and the
matrix are declared either way, and nothing would be left to read them
against. What no command here compares is the classifiers
against the interpreters a workflow runs, which stays a reading: a job
naming one outside the window is correct where the reason is beside it,
and no command here can read a reason.

The settings, which is where the defects have actually been:

```shell
R=<org>/<repo>
gh api repos/$R --jq '{allow_squash_merge, allow_merge_commit,
  allow_rebase_merge, delete_branch_on_merge, security_and_analysis}'
gh api repos/$R/actions/permissions/workflow
gh api repos/$R/rulesets --jq '.[].id' | xargs -I{} \
  gh api repos/$R/rulesets/{} --jq '{name, target,
    rules: [.rules[].type], bypass: [.bypass_actors[]?.bypass_mode]}'
gh api repos/$R/branches/main/protection \
  --jq '{sigs: .required_signatures.enabled,
         checks: [.required_status_checks.checks[]?.context]}'
```

What the answer has to say: squash the only method, signatures required
with an **empty** bypass list, the self-merge bypass in `pull_request`
mode and never `always`, and a token that is `read`.

The tree:

```shell
grep -n 'strict = true\|fail_under = 100\|branch = true\|"FIX"\|"TD"' \
    pyproject.toml
grep -n 'id: mypy' .pre-commit-config.yaml
git ls-files 'TODO*' '**/TODO*'
grep -hoE 'uses: [^ ]+' .github/workflows/*.yml | grep -v '@[0-9a-f]\{40\}'
grep -L '^permissions:' .github/workflows/*.yml
grep -rn -- '--frozen' .github/workflows/
grep -rn 'merge=union' .gitattributes
git ls-files '*package-content-policy*' '*_contents*'
sed -nE '/^\[build-system\]/,/^\[/{/^\[/!p;}' pyproject.toml
grep -n 'check-sdist' .pre-commit-config.yaml
sed -nE '/^\[tool\.check-wheel-contents\]/,/^\[/{/^[a-z]/p;}' pyproject.toml
sed -nE '/^\[.*(targets\.sdist|uv\.build-backend)\]/,/^\[/{/^[a-z]/p;}' \
    pyproject.toml
uv run pre-commit run --all-files
cat tests/README.md
```

The metadata an index shows, which no command in the tree can compare
because half of it is a repository setting. The lines chain because the
last of them writes, which is section 9's rule:

```shell
gh api repos/<org>/<repo> --jq '.topics | join(", ")' &&
sed -n '/^keywords = \[/,/^\]/p' pyproject.toml &&
uv build --sdist && uvx twine check dist/*.tar.gz
```

The first two have to name the same things, up to GitHub's twenty — as
sets and not as sequences, the first command answering alphabetically
whatever was set, where the second echoes an order somebody chose. The
third checks less than its name suggests — section 3 says what it does
and does not read — so the classifiers are asked about separately, and
before a release rather than during one:

```shell
uvx --with trove-classifiers python -c '
import pathlib, tomllib
from trove_classifiers import classifiers
declared = tomllib.loads(
    pathlib.Path("pyproject.toml").read_text()
)["project"]["classifiers"]
print([c for c in declared if c not in classifiers])'
```

An empty list is the answer. A string in it is one PyPI would refuse on
upload, at the point where a version is already being consumed.

`gh api` puts a failure's body on stdout and exits non-zero, so a
command that filters nothing out of what it fetched reports its own
failure, which is what the settings block above does. Where a `sed`
reads the fetch instead, or a capture parses it as content, both signals
are lost and a call that failed is one blank with a repository that owes
nothing — a sweep's row and a single repository's answer alike. The
reading is written once. `read_or_mark` takes the path in `$r`'s tree as
`$1` and sets `$content` and `$ok`; `list_or_mark` names `$r`'s
workflows and sets `$names` and `$ok`:

```shell
read_or_mark() {
  if e=$(gh api "repos/<org>/$r/contents/$1" --jq .content 2>/dev/null)
  then content=$(printf '%s' "$e" | base64 -d); ok=found
  elif gh api "repos/<org>/$r/contents/$1" --jq .content 2>&1 1>/dev/null \
      | grep -q '(HTTP 404)'; then content=; ok=absent
  else content=; ok=unreadable
  fi
}
list_or_mark() {
  if names=$(gh api "repos/<org>/$r/contents/.github/workflows" \
      --jq '.[].name' 2>/dev/null); then ok=found
  elif gh api "repos/<org>/$r/contents/.github/workflows" 2>&1 1>/dev/null \
      | grep -q '(HTTP 404)'; then names=; ok=absent
  else names=; ok=unreadable
  fi
}
```

`found` is a file that answered, `absent` the `(HTTP 404)` a repository
without that path gives, and `unreadable` anything else — a call that
did not answer, which is no reading to act on until it is asked again. A
sweep whose line has fields writes the marker into the field the call
would have filled; one that prints a line only where it has something to
say prints a line naming what could not be read, having no field to
write into. The `--silent` existence checks reach the same three values
by exit code, there being no content to decode.

Section 1's interpreter window, declared once in `requires-python`,
again in the classifiers, again in `.python-version` and a fourth time
in the matrix the platform sweeps run:

```shell
for r in <every repository>; do
  read_or_mark pyproject.toml
  floor=$(printf '%s' "$content" |
    sed -nE 's/^requires-python = ">=(3\.[0-9]+)"/\1/p')
  classifiers=$(printf '%s' "$content" |
    sed -nE 's/^ +"Programming Language :: Python :: (3\.[0-9]+)",$/\1/p' |
    paste -sd, -)
  case $content in
    *'Topic :: Software Development :: Libraries :: Python Modules'*)
      declares=library ;;
    *) declares=application ;;
  esac
  if [ "$ok" = unreadable ]; then
    floor=unreadable; classifiers=unreadable; declares=unreadable
  fi
  read_or_mark .python-version
  pin=$(printf '%s' "$content" | grep -v '^#')
  [ "$ok" = unreadable ] && pin=unreadable
  list_or_mark
  if [ "$ok" = unreadable ]; then matrix=unreadable; publishes=unreadable
  else
    printf '%s\n' "$names" | grep -qx release.yml \
      && publishes=yes || publishes=no
    matrix=$(printf '%s\n' "$names" | while read -r f; do
      [ -n "$f" ] || continue
      read_or_mark ".github/workflows/$f"
      if [ "$ok" = found ]; then
        printf '%s' "$content" |
          sed -nE 's/^ +- "(3\.[0-9]+t?|pypy3\.[0-9]+)"$/\1/p'
      else echo unreadable; fi
    done | sort -u | paste -sd, -)
  fi
  case $declares:$publishes in
    unreadable:*|*:unreadable) kind=unreadable ;;
    library:yes) kind=library ;;
    *) kind=application ;;
  esac
  printf '%s\t%s\tfloor %s\tclassifiers %s\tpin %s\tmatrix %s\n' \
    "$r" "$kind" "$floor" "$classifiers" "$pin" "$matrix"
done
```

One line per repository. Where a line carries classifiers, the floor is
the lowest of them, the pin is the highest, and the matrix runs every
one. The `library` lines are the same window as each other, that window
being python.org's; an `application` line is read against the comment in
its own `.python-version` instead, which is where section 1 puts the
dependency that set the ceiling. Which of the two a line is, section 1
decides and this reads: `release.yml` among the workflow names, and the
library classifier anywhere in the file rather than among the
per-version ones the `classifiers` column keeps. A `kind` of
`unreadable` is either call not answering, and neither half is guessed
from the other.

The matrix column is empty where no workflow names a list of them,
which is a tree whose workflows name no interpreter at all and a tree
that runs a single one as a key: either way the pin is what runs. A
column reading `unreadable` is the call and not the declaration, and
`matrix` carries the marker among version strings where one workflow of
several could not be read.
Section 3 has what a `t` suffix and a `pypy` prefix each name a
classifier as; this command reads the first as its own `X.Y` and drops
the second, there being no version string for an implementation to
match. Reading the matrix against the classifiers is this command's
work: what the suite compares them with is the floor and the pin, and
no workflow.

Section 1's uv floor, and the ceiling it is set at:

```shell
if d=$(gh api repos/dependabot/dependabot-core/contents/uv/Dockerfile \
    -H 'Accept: application/vnd.github.raw' 2>/dev/null)
then ceiling=$(printf '%s' "$d" | grep -oE 'ghcr\.io/astral-sh/uv:[0-9.]+')
elif gh api repos/dependabot/dependabot-core/contents/uv/Dockerfile \
    2>&1 1>/dev/null | grep -q '(HTTP 404)'; then ceiling=absent
else ceiling=unreadable
fi
printf 'ceiling=%s\n' "$ceiling"
for r in <every repository>; do
  read_or_mark pyproject.toml
  req=$(printf '%s' "$content" \
    | sed -nE 's/^required-version = "(.*)"/\1/p')
  [ "$ok" = unreadable ] && req=unreadable
  e=$(gh api "repos/<org>/$r/contents/uv.lock" --silent 2>&1) && lock=yes \
    || { printf '%s' "$e" | grep -q '(HTTP 404)' && lock=no \
         || lock=unreadable; }
  printf '%s\tlock=%s\tfloor=%s\n' "$r" "$lock" "$req"
done
```

`ceiling=` is the uv Dependabot's own bundled updater ships, above
which it refuses to re-lock rather than upgrading itself. It is read
outside the organization, where `read_or_mark` builds no path, so the
reading is spelled out with the helper's markers: `absent` is the
`Dockerfile` gone from that path and an empty value is its image line
no longer matching the pattern — either is `dependabot-core` moving
what this block rests on, and is acted on the day it prints — where
`unreadable` is the call not answering, and is asked again. The
alternative gives `read_or_mark` a second argument naming another
repository; what it costs is every call inside the organization
carrying a default for the one outside it.

`lock=yes` names a tree that owes the floor; `floor=` empty beside it is
the finding, a tree committing a lock with nothing capping the uv that
reads it. `lock=no` owes no floor, so an empty `floor=` beside it is
silent rather than a finding, whatever the ceiling is that day. A `floor=`
that is not `ceiling=` is a finding on either side of it, section 1's
sentence being that the floor is set at the ceiling rather than below
it. Below the ceiling, the tree still admits a uv older than the one
its lock updates are written with. Above it, the refusal `ceiling=`
names has already stopped that tree's uv updates. `lock=unreadable` is
neither: the call itself failed, told apart from a genuine `no` by the
`(HTTP 404)` `--silent` would otherwise swallow, and `floor=` beside it
answers nothing until the sweep is run again. `floor=unreadable` says it
of the other call, which fails independently of this one: an empty
`floor=` is the finding above, where `floor=unreadable` is nothing at
all until the `pyproject.toml` fetch answers.

Which repositories publish, which is what section 2's first tier turns
on and so what decides whether a `SECURITY.md` is owed or inherited:

```shell
for r in <every repository>; do
  e=$(gh api "repos/<org>/$r/contents/.github/workflows/release.yml" \
    --silent 2>&1) && w=release.yml \
    || { printf '%s' "$e" | grep -q '(HTTP 404)' && w=none \
         || w=unreadable; }
  printf '%s\trelease=%s\n' "$r" "$w"
done
```

The index's path continues past the name, which is the position section
9 refuses, so it stands in a block of its own:

```shell
name=<name>
```

```shell
curl -s "https://pypi.org/pypi/${name:?}/json" | python3 -c 'import json, sys
d = json.load(sys.stdin).get("info")
if d is None:
    print("absent from the index")
else:
    u = [v for v in (d.get("project_urls") or {}).values()
         if "github.com/<org>/" in v]
    print(u[0] if u else "on the index, another project")'
```

Both halves are the question, and neither answers alone. The first is
asked by the exit code: `--silent` prints nothing on success and sends
the failure to stderr, where `--jq .name` would put a 404's *body* on
stdout and `|| echo none` would append to it. That stderr is now
captured rather than let through: a `(HTTP 404)` in it is `release.yml`
genuinely absent, and anything else is the call itself failing —
`w=unreadable`, told apart from a real `none` rather than folded into
it. The second reads the project urls rather than the status code,
because a name this
organization does not publish may be served by somebody else's project
of the same name — so the discriminator is a link back to the
organization and not a `200`. `<name>` is what `pyproject.toml`
declares, which is not always the repository's.

`(HTTP 404)` is what a genuinely absent `release.yml` answers with, and
also what a repository this loop names but the endpoint cannot find
answers with — a stale roster reads as `none` rather than
`unreadable`, a gap this shape does not close.

The private channel section 2 owes, which is a setting in every
repository and an address in the files that carry the policy:

```shell
for r in <every repository>; do
  printf '%-20s ' "$r"
  enabled=$(gh api "repos/<org>/$r/private-vulnerability-reporting" \
    --jq .enabled 2>/dev/null) || enabled=unreadable
  echo "$enabled"
done

one='security at btclib dot org'
any='[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
for r in <every repository>; do
  printf '%-20s ' "$r"
  read_or_mark SECURITY.md
  [ "$ok" = absent ] && { echo 'no SECURITY.md'; continue; }
  [ "$ok" = unreadable ] && { echo 'unreadable'; continue; }
  printf '%s\n' "$content" | grep -o -i -E "$one|$any" \
    | sort -u | tr '\n' ' '
  echo
done
```

`true` from every repository is the answer to the first, a `false` being
a policy that links a form the reporters of that repository do not have,
and *unreadable* an endpoint that answered neither — captured rather
than let through, an error body on stdout being what the publishing
sweep above uses `--silent` against.

The second answers one line per repository.
*security at btclib dot org* is a repository carrying a policy and
giving the address; *no SECURITY.md* is one inheriting this
repository's, read beside the publishing sweep since at tier 1 that is
the missing file; a blank line is a policy the pattern found no address
in — another spelled-out mailbox, or none at all — and printing the
missing file rather than leaving it blank is what tells a blank from a
policy that is not there. An `@` form is the finding wherever it prints,
that being the spelling the address is written to avoid. The grep reads
no further: a pattern taking any spelled-out address would report the
one `btclib-secp256k1` gives for the C library it binds, which is
upstream's and correctly there. *unreadable* is the call itself
failing, the same `(HTTP 404)` capture the publishing sweep uses telling
it apart from a genuine `no SECURITY.md`.

Section 2's badge rule, whose subject is the head of a file no tree can
read for another, and section 10's record beside it. The first loop is
membership and order, one line per badge and none at all for a
`README.md` that carries no badge:

```shell
for r in <every repository>; do
  read_or_mark README.md
  if [ "$ok" = found ]; then
    printf '%s' "$content" \
      | sed -nE "s|^\[!\[[^]]*\]\(([^)]*)\).*|$r\t\1|p"
  else printf '%s\t(%s)\n' "$r" "$ok"; fi
done
```

A repository whose `README.md` did not answer takes the second column
instead of a badge source: `(unreadable)` is the call, and `(absent)`
the file, which section 2's *Root files* owes at every tier. The
parentheses are what no source has, so neither reads as one.

The badge's **source** and not its alt text, which is prose its author
chose: a badge can write `license: MIT` over section 2's refused
`img.shields.io/badge/license-MIT-blue.svg`, and a loop reading the alt
text reports a licence badge and stops.
Read the sources against section 2's list and section 10's record, in
the order they arrive: a badge neither gives the tree, one they give it
and the row does not carry, and a row out of order are each a finding,
and no command tells them apart from each other.

The second asks what each badge renders, which is what a reader of the
rendered file sees and a reader of its source cannot:

```shell
r=<repo>
read_or_mark README.md
if [ "$ok" != found ]; then echo "README.md $ok"
else printf '%s' "$content" \
  | sed -nE 's|^\[!\[[^]]*\]\(([^)]*)\).*|\1|p' \
  | while read -r src; do
      body=$(curl -sL -w '\n%{http_code}' "$src")
      says=$(printf '%s' "$body" | tr -d '\n' \
        | grep -oE '<title>[^<]*</title>' | sed -E 's|</?title>||g')
      printf '%s\t%s\t%s\n' "$(printf '%s' "$body" | tail -1)" \
        "${says:-(no title)}" "$src"
    done
fi
```

One line per badge, and it prints rather than judging: anything but
`200` is the finding a command can decide, and the message beside it is
the reading the rule above asks for. Read the Docs and pepy carry no
`<title>` and print `(no title)`, so those two are read from the
rendered image or from the page they link to. Where the `README.md`
itself did not answer, the marker takes the whole line, there being no
badge for it to sit beside.

Section 11's rule that `claude-review.yml` is in every repository, which
no single tree can answer for the others and nothing in `tests/` asks:

```shell
for r in <every repository>; do
  e=$(gh api "repos/<org>/$r/contents/.github/workflows/claude-review.yml" \
    --silent 2>&1) && continue
  printf '%s' "$e" | grep -q '(HTTP 404)' \
    && echo "$r has no claude-review.yml" \
    || echo "$r: claude-review.yml unreadable"
done
```

Silent where the rule is kept, one line naming a repository missing it,
and a differently worded line where the call itself failed rather than
answered — `--silent` for the reason the publishing sweep gives.

The calendar of section 10, across the organization, an audit no single
tree can answer:

```shell
for r in <every repository>; do
  list_or_mark
  [ "$ok" = found ] || { echo "$r workflows $ok"; continue; }
  printf '%s\n' "$names" | while read -r f; do
    [ -n "$f" ] || continue
    read_or_mark ".github/workflows/$f"
    if [ "$ok" = found ]; then
      printf '%s' "$content" | sed -n "s/^ *- cron: /$r $f /p"
    else echo "$r $f $ok"; fi
  done
done | sort -k2
```

Sorted by workflow, so a file running on a different day from its
namesake in another tree is one line out of place. A minute shared by two
repositories at the same day and hour is the other finding, for the
reason section 10 gives beside the table. A line for a tree that
workflow's entry in section 10's record does not name is the third, and
the one no comparison of instants can show: the cron is right and the
row is not the tree's.

A repository with no schedule prints nothing, so the marker takes a line
of its own rather than a field, and it sorts under the name of what did
not answer: a workflow's, or `workflows` for the listing, whose `absent`
is a repository with no `.github/workflows` at all.

That loop reads `cron:` and reaches no further, so the calendar's
Dependabot row is not in it: that schedule is an `interval` and a `day`
in `.github/dependabot.yml`, a different shape in a different file, and
it takes a second command.

```shell
for r in <every repository>; do
  read_or_mark .github/dependabot.yml
  [ "$ok" = found ] || { echo "$r dependabot $ok"; continue; }
  printf '%s' "$content" | sed -n "s/^ *day: /$r dependabot /p" | sort -u
done
```

One line per repository where every ecosystem agrees, more than one
where they do not — which is itself the finding, an ecosystem opening on
a day the sentinel before it does not precede. `absent` in place of the
day is a repository with no `.github/dependabot.yml`, which section 2's
*Directories* owes, and `unreadable` is the call.

`strict = true` in `pyproject.toml` with no `id: mypy` in
`.pre-commit-config.yaml` is section 6's finding and a finding on its
own: the strictness is configured and nothing runs it, which is the half
of that section a tool table cannot answer for.

An action not pinned to forty hex digits, a workflow with no
`permissions:` block, and a `--frozen` anywhere are each a finding on
their own. Check exit codes, not filtered output.

`tests/README.md` is section 7's answer, and no command computes it —
that section says why. Read it against section 7's list and that
section's rule for which bullets a repository owes: a bullet owed and
not claimed is the finding, and a bullet claimed is answered by the test
in that repository that asserts the claim. Across the organization the
same command run in each tree is the matrix, and there is no shorter way
to it.

Section 7's vendored-data pins, which sit in the data directory and so
wherever that directory sits: the sweep asks the tree for its
`README.md` paths rather than naming any, a tree whose data sits beside
the script that reads it having no path a fixed list would hold. The
root `README.md` is passed over, being section 2's rather than a data
directory's, and this one carrying section 7's block as the shape to
write, which no count tells from a pin:

```shell
for r in <every repository>; do
  if paths=$(gh api "repos/<org>/$r/git/trees/HEAD?recursive=1" \
      --jq '.tree[] | select(.path | endswith("/README.md")) | .path' \
      2>/dev/null)
  then pins=$(printf '%s\n' "$paths" | while read -r p; do
      [ -n "$p" ] || continue
      read_or_mark "$p"
      if [ "$ok" = found ]; then
        n=$(printf '%s' "$content" | grep -c '^commit  ')
        [ "$n" -gt 0 ] && echo "$p=$n"
      else echo "$p=$ok"; fi
    done | paste -sd, -)
  else pins=unreadable
  fi
  e=$(gh api "repos/<org>/$r/contents/.github/workflows/vendored-vectors.yml" \
    --silent 2>&1) && wf=yes \
    || { printf '%s' "$e" | grep -q '(HTTP 404)' && wf=no || wf=unreadable; }
  printf '%s\tpins=%s\tworkflow=%s\n' "$r" "${pins:-none}" "$wf"
done
```

A path with a count beside it is a file carrying the block, which
section 7 asks a tree for one of; the loop names a path only where the
count is above zero. A path with `workflow=no` is section 7's finding: a
tree pinning an upstream commit with nothing rechecking it on section
10's schedule. The reverse — a workflow present where no path answers —
is the same finding read from the other side.

`pins=none` is no `README.md` of the tree carrying the block, which is a
tree with nothing to vendor and equally a tree whose provenance is
written some other way; this command does not tell those two apart, and
what does is the reading section 7 asks of `tests/README.md` above.
`pins=unreadable` is the tree listing failing, `unreadable` beside a
path is that file's own fetch, and `workflow=unreadable` the third call;
the last two are told from a genuine absence by the same `(HTTP 404)`
capture the sweeps above use. None of the three is a reading to act on
until it is asked again.

What the package-content lines have to say: where the wheel is one
package tree, a `package` naming it, whose absence is section 12's
finding; where the wheel is not one, the codes the tool is told to
ignore, and the page, the script and the test that a repository which
escalates owes together rather than singly. `check-sdist` in the gate
wherever an sdist is built, and a `[tool.check-sdist]` table beside an
sdist target that only excludes. A `build-backend` other
than `uv_build` in a project that compiles nothing is section 3's
finding, and it is the one to read first: which table declares the
inclusion follows from it.

### Reading the workflow comments

A reading rather than a command, and no tool covers it: `actionlint`
reads the workflow, `zizmor` reads it for injection, the gate reads the
code — and a sentence asserting that a job "calls three reusable
workflows" sits unchallenged beside a file that calls six. It reads as
authoritative precisely because it sits next to the thing it describes.

1. **Read every comment, end to end.** Not a grep for suspicious words:
   the stale ones read exactly like the true ones.
1. **Check each claim against this repository's tree**, never against
   another comment. Named triggers against the `on:` block; call-graph
   claims against the actual `uses:` and `needs:` lines, grepped and
   counted rather than eyeballed; context references against what they
   resolve to; cron days against every other schedule here and against
   `dependabot.yml`; any file, line or count a comment names re-derived
   independently. **Never against the sibling the file was copied from
   either**: prose moves between these repositories more easily than
   configuration does, so a paragraph true where it was written is an
   ordinary way for a comment to be wrong where it now sits.
1. **Run the command a comment gives, and read it for what it reaches.**
   A comment quoting a command's output is the hardest kind to doubt, and
   the command can confirm a claim rather than test it: a paginated
   endpoint asked without `--paginate` answers for its newest page alone,
   so "nothing here has ever been X" survives every X older than that
   page.
1. **`git log -S <phrase>` on every mismatch**, to separate *was true,
   drifted* from *never matched*. That axis decides whether the fix is
   the comment or the code, and a comment describing a safer design that
   was never built is a finding against the code.
1. **Follow anomalous width.** A comment line past 80 columns breaks
   section 9's rule, and in practice it is the un-rewrapped remainder of
   an earlier fix — the one property of a comment a reader notices
   without reading it, and worth following into the paragraph around it:

   ```shell
   awk 'length > 80 && /^ *#/ {print FILENAME ":" FNR}' .github/workflows/*.yml
   ```

   The 100 columns yaml gets in section 9 are for a line pinned to a
   commit SHA with its tag after it. A comment is not that line.

The file set divides cleanly across readers by size, each file being
independent and the checklist the same for each.

## 16. Checklists

### A new repository

1. Its tier, measured as section 2 measures it, and its row in section
   2's table, in the pull request that creates the repository. The tier
   is which of the steps below the tree owes, and a step for a section
   the tier does not bind is not a gap skipped but a step that does not
   exist for that tree.
1. `git init`, MIT `LICENSE`, `COPYRIGHT`, `AUTHORS.md`.
1. `pyproject.toml`: section 3's build backend, metadata, PEP 639
   licence, keywords matching the topics, urls, dependency groups, and
   the tool tables of sections 5, 6, 7 and 8.
1. Copy the files section 14 names for the tools whose configuration is
   not in `pyproject.toml`, and `.gitattributes` (with the two
   `merge=union` entries). `.python-version` and `.gitignore` are
   written rather than copied, section 14 deciding both per repository:
   the interpreter this repository pins, and what its own build and
   tools write.
1. `.pre-commit-config.yaml`, including the mypy hook section 4's
   criterion chooses and the `pinned-rev` guard; `uv run pre-commit run
   --all-files` until clean; generate `.secrets.baseline`.
1. `.vscode/settings.json` and `.vscode/extensions.json`,
   `mypy-type-checker.importStrategy` taking section 13's value for the
   hook the step above chose.
1. `uv sync`, commit `uv.lock`.
1. `tests/` with the naming convention, a `conftest.py` carrying the
   selective-run coverage hook, the first convention tests, and the
   `tests/README.md` that declares which of section 7's bullets they are
   — with the test that asserts the declaration.
1. `docs/source` and `.readthedocs.yaml`, built with `-W -n`, and
   `sphinx.ext.intersphinx` in `extensions` before `-n` is turned on.
1. Section 12's package-content floor: `[tool.check-wheel-contents]`
   naming the package where the wheel is one package tree, and the page,
   the script and the test where it is not; `check-sdist` wherever an
   sdist is built, reading the inclusion from the table section 3's
   backend declares it in and building through the installer section 12
   names. A `dist` job that inspects what would be published.
1. Workflows: `test` (with its aggregate and its `changes` job), `lint`,
   `docs`, `claude-review`, then the periodic ones the project earns.
1. `.github/dependabot.yml`, `ISSUE_TEMPLATE/`,
   `PULL_REQUEST_TEMPLATE.md`.
1. `CONTRIBUTING.md`, `REVIEWING.md` with the
   `.claude/commands/review.md` that invokes it, `REPOSITORY.md`,
   `CHANGELOG.md`, `CLAUDE.md`; and `SECURITY.md`, `RELEASING.md` and
   `RELEASE_NOTES.md` where the repository publishes, the rows section
   2's table marks for tier 1 alone.
1. GitHub, in this order: default branch `main`; squash-only, with
   auto-merge; `delete_branch_on_merge`; the three rulesets; classic
   protection with the required checks bound to the Actions app; the
   publishing environments; the read-only default token; secret scanning,
   its push protection and Dependabot security updates; private
   vulnerability reporting. Then the topics, which are the `keywords` of the
   `pyproject.toml` step above, and which nothing in the tree holds where
   there is no such file to declare them in; and, where the tree
   releases, the `homepage`, the same URL section 3's field of that name
   carries.
1. Read each setting back with the commands `REPOSITORY.md` records, and
   write the answers into it — the topics included, that being the one
   of them a tree with no `pyproject.toml` records nowhere else.

### Normalizing an existing repository

Ordered by what the gap costs — an unsigned commit or a token that can
write to the repository outranks a formatter — wherever dependency
leaves that order free, because a step whose prerequisite has not landed
cannot be performed, and one that cannot be performed has no cost to
weigh. Dependency is a partial order and fixes only the steps below that
say what they wait for: it has nothing to say about mypy against ruff
against pytest, so ordering the whole list by it would settle those by
nothing at all. Cost settles them, and cost is what makes any prefix of
this list the right prefix — a normalization lands over many pull
requests and stops wherever it stops. The tier comes before the list,
section 2's table: it says which of these steps the tree owes at all.

Not every constraint is an order between two steps, and the ones that
are not hold over all of them. **A rule arrives with its subject**: a
hook lands with the files it reads, and configuration copied from a
sibling comes minus any rule whose subject this tree does not have yet,
each such rule arriving with its file. **A gate's first run is over a
tree it has never seen**, so it runs over the whole tree rather than
over what its own step added — everything the steps before it wrote was
written before the gate that judges it.

1. **`REVIEWING.md` and `claude-review.yml` first**, before anything is
   proposed: section 11 is where the ack of record is that workflow's,
   and the workflow's prompt reads `REVIEWING.md` by name — so a
   repository holding neither has no ack available to it.
   `.claude/commands/review.md` lands with them, section 14 owing it
   wherever `REVIEWING.md` is.
   This is not the costliest gap, it is the one every step that lands as
   a pull request waits on, which is every step below that changes the
   tree. The settings applied straight to the repository — section 11's,
   and the branch rules of the step under this one — are not proposed
   and not reviewed, so they do not wait for it. The credential is an
   organization secret with `visibility=all`, so a repository configures
   nothing for it: `gh api orgs/<org>/actions/secrets` is the reading.
1. **Signatures and branch rules** — `required_signatures`, no direct
   push, linear history, one review, squash-only. An unsigned commit that
   already landed is history; the rule stops the next one.
1. **Token permissions** — `contents: read` by default, one elevation per
   job, and no long-lived publishing token where OIDC works.
1. **Secret scanning and its push protection**, with the settings above:
   each is a switch and each starts paying the moment it is on — section
   11 has which of the two refuses and which reports — and neither reads
   a lock file.
   **Private vulnerability reporting** goes on beside them, section 2
   owing it at every tier: it is what makes the route a `SECURITY.md`
   links exist, and it waits for nothing.
   **Dependabot's updates wait** for the lock below — turned on over the
   outgoing resolution, they propose bumps to a file that step deletes,
   and one landed there is a conflict on the migration rather than a
   fix.
1. **Actions pinned to commit SHAs**, then `actionlint` and `zizmor` to
   zero.
1. **`uv` and a committed lock**, `--locked` in every job, and one
   documented command per job.
1. **What the distribution carries, where the repository publishes** —
   section 3's backend first, since which table declares the inclusion
   follows from it, then section 12's floor:
   `[tool.check-wheel-contents]` naming the package where the wheel is
   one package tree, the page, the script and the test where it is not,
   and `check-sdist` against the archive wherever an sdist is built. A
   backend move is checked by the archive
   it produces and not by the file it edits — an sdist built each way,
   with the member lists compared — since what the outgoing include
   language expressed and the incoming one cannot shows up there and
   nowhere else.
   Everything else the `dist` job runs reads a distribution's account
   of itself, which a `py.typed` lost to a `package-data` typo passes.
1. **`.pre-commit-config.yaml` as the single lint gate**, and the lint
   workflow reduced to running it. Delete any second list of the same
   tools from the workflows. The shared configuration its hooks read
   lands with them — the files section 14 names for the tools whose
   configuration is not in `pyproject.toml` — as does `.gitattributes`,
   whose `merge=union` entries wait for the two history files below.
   Then run it `--all-files`, over everything the steps above added.
   `.vscode/` lands with it, section 13's recommendations being the
   gate's own tools and `importStrategy` following the mypy hook the
   step below writes.
1. **mypy `strict = true`** aimed at the `requires-python` floor, with
   the optional error codes surveyed one at a time, and the hook in the
   gate above that runs it. Every silencing `type: ignore` names its
   code.
1. **ruff** with the widths, the docstring family and `max-complexity`,
   the copyright rule, transcribed from `COPYRIGHT` — so that file lands
   here and not with the root files below — and `FIX`, whose subject is an
   empty backlog: it arrives once the markers it refuses, and any
   `TODO.md`, are issues.
1. **pytest strictness** — `--strict-config`, `--strict-markers`,
   `filterwarnings = ["error"]`, `xfail_strict`. Expect this one to be
   the loudest.
1. **Coverage to 100** — this is the long one, and the ratchet is the
   wrong tool for the climb: measure, cover the reachable, `pragma: no
   cover` with a reason where the line is unreachable, and set
   `fail_under = 100` only once the tree is there. Include the tests in
   `source` from the start.
1. **The convention tests**, which section 7's terms decide, and
   `tests/README.md` declaring which of that section's bullets those
   are. An older repository is where the declaration earns most: it is
   the step that says which conventions this tree has decided it does
   not have, which is otherwise indistinguishable from having forgotten
   them.
1. **The missing root files**, `REPOSITORY.md` first: it is the only
   record of what the settings are.
1. **Dependabot's own configuration, the sentinel workflow, and the
   periodic platform runs** — the updates held above, now that what they
   read is the lock that ships.
1. **The prose pass** — 80 columns, the reasoning and its negative
   results in the configuration comments, no stated counts, and history
   moved to the two files that carry it.
