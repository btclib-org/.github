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
statement is this file; keeping it true is the issue tracker beside it,
a divergence between two repositories belonging to neither of them. A
repository that has fallen behind the standard is an issue against the
repository, tracked here; one that has gone *ahead* of it — a practice
worth having everywhere, arrived at in one place — is an issue against
this file, and the standard changes.

**And not only drift: the ongoing maintenance that crosses repositories
is tracked here too**, whether or not the standard has anything to say
about it, since it lands as one pull request per repository and wants a
single place to be closed from.

The reference implementations are `btclib`, `btclib-secp256k1`,
`bitcoin-core-rpc` and `btclib-benchmarks`: where they agree, this file
states the rule, and where they differ it says which part of the
difference is a decision and which is only the age of the repository.

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
  `CODE_OF_CONDUCT.md` is kept here and nowhere else, being one policy
  for the organization rather than anything a tree says about itself;
  `SECURITY.md` is kept here *and* in each repository that publishes,
  the table below saying why and section 15 the command that answers
  which.
- **This file** is inherited by nothing and is the point: one statement
  of the standard, linked from each repository's `CONTRIBUTING.md`,
  rather than a copy per repository for the copies to drift apart in.
- **The issue tracker** is the maintenance, an alignment finding staying
  open until every repository it names has answered, which is the thing
  an issue filed on a single repository cannot do.

Nothing here is released: this repository ships by being read, and
`CONTRIBUTING.md`'s *A version, and no release* is what the placeholder
version in `pyproject.toml` is for.

**A finding that spans repositories is filed here, and only here**, the same
divergence written up once per repository acquiring several numbers and no
owner. **An issue names a user, a build, a release or a setting affected**: a
shape a test cannot read is that test's defect, fixed there or the reading
dropped, and a session filing more than one issue reads the tracker first, one
worker filing for all. The shape is one issue naming the repositories it is
about, with a checkbox per repository and the command that re-derives the
finding, and it closes when the last box is ticked; a per-repository issue is
for work that is genuinely that repository's alone, and links to the issue here
where it is a share of one, closing when that repository's pull request lands.

**A decision taken here that removes an artifact owes a sweep of every
tree for what asserts it.** What a tree says about a tag, a release page
or a setting is false from the moment the decision lands, and that tree
did not change to make it so. The sweep goes in the deciding diff where
what asserts the artifact is in a tree that diff already touches, and
otherwise in an issue filed with the deciding one; no command checks
that a decision did this, which puts it among section 15's readings
rather than its comparisons.

Branch rules, rulesets and repository settings are *not* inherited from
here either. On an organization plan without organization-wide rulesets
they are applied per repository, which section 15 is how to verify.

## How to use this file

- **A new repository** — work down the sections in order. Section 16's
  first checklist is the same list without the reasoning.
- **An existing repository** — section 16's second checklist is ordered
  by what a gap costs, wherever dependency leaves that order free.
- **A rule with no reason beside it is not this file's rule.** Every
  setting below was decided against an alternative, and the alternative
  is what stops the next reader from undoing it — in a sentence, not in
  a paragraph.
- **A numbered section's rule enters this file together with what reads
  it — a hook of section 4 or a test of `tests/` — or it does not
  enter**: a rule only a reader enforces turns every landing into a
  finding. **What reads it reads configuration** — a file a tool parses,
  a workflow, the API — and not prose: a test over prose is a parser of
  prose. This preamble is read by the review, `REVIEWING.md`'s *This
  repository in particular*.
- **This file does not grow by accretion.** What a rule costs in lines
  comes out of what its arrival makes redundant where it lands, and
  `git diff --numstat origin/main -- README.md` is the read; the file
  grows where the search for that payment comes back empty and nowhere
  else. A census, a dated measurement, a line number and the tour of
  rejected alternatives are refused outright, and belong to the pull
  request that made the change (btclib-org/.github#1075).

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
runs the same command verbatim, so a workflow change that leaves
`CONTRIBUTING.md`'s last section behind makes that file wrong rather
than merely stale. A workflow whose command lives only in the workflow
says so where it is written.

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

**A library publishes and declares the classifier
`Topic :: Software Development :: Libraries :: Python Modules`. Every
other repository is an application.** Section 2's tier is whether an
index carries the distribution for somebody else's resolver to reach,
and the classifier is what the distribution on it says it is; publishing
alone is the rejected proxy, and `btclib-node` is what it reads wrong, a
full node being a program its users run. No command refuses a library
that declines the classifier, the two being one shape on disk.

A **library covers every interpreter still in support**: the floor is
the oldest Python that has not reached end of life, `.python-version` is
the newest released, and the classifiers name every version between them
while the platform sweeps run each. Neither end is a choice, the
[Python release cycle](https://devguide.python.org/versions/) moving
both, so a library's window changes on a date rather than on a decision.
The libraries name one window between them, and section 15's command is
what reads it.

An **application takes the newest interpreter its dependencies allow**,
not being there to be imported: `.python-version` is the newest version
every dependency publishes for, and `requires-python` the oldest the
tree itself means to run on, which is that same version where it means
to run on one interpreter alone. Where a dependency holds
`.python-version` below the newest release, that file's comment names
the dependency and the condition for raising it, a ceiling with no
reason beside it reading as a preference.

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
group that was selected and not one another group includes; a project
with no such dependency keeps the two names or not as its own workflows
ask.

`build` and `check` are two names because one tree holds both and they
mean different things there: `--only-group build` compiles wheels,
`--only-group check` reads them without compiling anything. A tree with
no build step of its own still names its inspection tools `check`, so
the command means the same thing everywhere.

`fuzz` is `mutation`'s shape, a scheduled workflow's group rather than a
gate's: a tree declares it where that workflow runs the fuzzer as a
`uv run` command, and not where the targets are compiled inside the
fuzzing service's own image.

An engine that publishes wheels for the platform it fuzzes on and no
source archive is specified with the marker naming that platform, `uv
lock` resolving without one and a missing marker costing a developer's
`uv sync` off that platform.

`dev` reaches every group *the tree itself declares*, transitively
through `include-group`, rather than every row of this table, and a
group no developer runs by hand is no exception to it: one sync is then
enough to run anything the tree runs.

Where a package is both an extra and a group, the specifier is written
twice and a test refuses the day the two disagree.

### `uv.lock`

Committed, and the only thing that moves it is Dependabot's uv ecosystem
and the `uv-lock` hook. A dependency group's own entry may carry a lower
bound, and nothing here moves one: the drift of ruff, mypy, pytest and
sphinx above it lives in the lock file, so one pull request a week
carries all of it, pre-validated by the `deps-latest` workflow.

`[tool.uv] required-version` names the oldest uv that may read the lock,
and every tree the root-files table binds to `uv.lock` carries it. The
floor is set at the ceiling — the newest uv Dependabot's own bundled
updater still reads — because that updater runs `uv lock` with exactly
the uv it ships and refuses rather than upgrading itself, so a floor
above the ceiling would silently stop every lock update it attempts.
Below it, an *older* uv rewrites the lock. Section 15 carries the
command that measures the floor, and `setup-uv` given no version input
reads that key, so CI needs no second pin.

**The `uv-lock` hook's `rev:` is at or above that floor**: the pin
selects the uv the hook bundles rather than the project's own, and under
the floor the hook refuses to run inside the required lint check.
`tests/hooks_test.py` asks for at least the floor and not for equality,
`autoupdate` moving the pin while the floor waits on the ceiling.

## 2. The tree

### Which repositories, and how far

This file is written for a Python package that publishes, and the
organization holds repositories that are not one. How far it binds a
repository is that repository's **tier**, measured rather than declared,
by two files:

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
  and `pypi-install`.
- **Tier 1 — a Python package that publishes.** The whole file.

A rule whose subject the tree does not hold asks nothing of it, at any
tier — `.taplo.toml` in a tree with no `toml`. An alignment finding
states which it is: a rule with no subject here, or a rule with a
subject that is declined.

**A tier is a floor, not a ceiling.** Above it, a repository carries
what its own practice needs, as `portanode` carries a `RELEASING.md`.
Below it, a repository short of what its tier binds is a gap, filed
here; a gap with the reason beside it, in the repository's `CLAUDE.md`
or its `REPOSITORY.md`, is a decision, and a sentence that declines a
rule and gives no reason is still a gap.

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

The loop below checks the table in both directions: a row it
contradicts is a finding, and so is a repository it names that the
table does not. A new repository is a row here in the pull request that
creates it, section 16's first step. `<org>` sits last by section 9.

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

`.github` is this repository, and its row is measured like the others;
what it declines of tier 2 — coverage, and the metadata of section 3
only an index reads — its `CLAUDE.md` says, with the reason.
`btclib-org.github.io`, the organization site served by Pages from its
`main` (btclib-org/.github#530), is measured the same way.

**A tier-2 repository carries neither `RELEASING.md` nor `RELEASE_NOTES.md`.**
The first would only say there is no release, which every such tree states
under its own `CONTRIBUTING.md`'s *A version, and no release*; the second is
what a user acts on *at a release*. A release arrives with `release.yml`,
which makes the repository tier 1, and the two files come with it.

### Root files

Each is one fact in one place, and the last column is which tiers owe
the row, the reason for a row that is not every tier's sitting beside
whatever decides it:

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

**`SECURITY.md` is tier 1's row**, because the sdist carries the file to
a reader who has the archive and not github.com; where nothing is
published, GitHub shows this repository's copy. An inherited policy
cannot name a tree's own flaws, so a tree with any to state says them in
its `README.md` and its issue tracker.

**The private channel that row promises is a setting as well as a
file.** The file is tier 1's and the setting — *Report a vulnerability*
on the Security tab — is every tier's, the policy sending a reporter to
the Security tab of the repository the defect is in, which need not
carry a policy of its own.

**The address kept beside the form** is *security at btclib dot org*,
spelled out rather than as a `mailto:` or with an `@`, the forms a
harvester lifts. It is one address for the organization, a reporter
being unable to check whether a mailbox is read.

**The badges at a `README.md`'s head are never curated.** A curated list
has no answer to *should this tree carry that badge*: where a property
of the repository decides a badge the answer is read off the tree, and
where none does the membership is written down, the row growing with
section 10's calendar and a tree wanting a shorter row dropping a
sentinel and its badge.

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

**The suite's badge is the `test` workflow's**: a tree running its suite
elsewhere, as this one does in `alignment.yml`, carries no `test` badge.

**Building documentation and being served by Read the Docs are two
properties**, a tree that builds `docs/` and subscribes no service being
complete, which *The documentation* below says. Which trees are served
is read from each tree's `REPOSITORY.md`, a subscription being a setting
outside the tree.

**The licence badge is tier 1's**, the repository page already stating
the licence (`gh api repos/<org>/<repo> --jq .license.spdx_id`) and the
badge earning its line where the README travels, to an index and in an
sdist.

**A sentinel's badge is recorded rather than derived**, because the
sentinel is, in section 10's *Which trees carry which sentinel*: a tree
drops the badge and the workflow together or keeps both.

**That badge is the workflow-run one for every sentinel but
`scorecard`** —
`github.com/<org>/<repo>/actions/workflows/<name>.yml/badge.svg`.
`scorecard` publishes a score rather than a pass or fail, and its badge
is that score, `api.scorecard.dev/projects/github.com/<org>/<repo>/badge`,
tied by section 10's `scorecard` subsection to `publish_results: true`.

**Every workflow-status badge carries `?branch=main`** on that URL, the
gates' and the sentinels' alike: the row is an audit of `main`, and
where a workflow has no run on `main` an unqualified badge renders
another branch's, a deleted one's included, with nothing saying so —
[GitHub's own](https://docs.github.com/en/actions/how-tos/monitoring-and-troubleshooting-workflows/monitoring-workflows/adding-a-workflow-status-badge)
fallback. A tree that lands the badge dispatches the workflow from
`main`, by section 10's *`workflow_dispatch` on everything*, rather than
waiting for the schedule. The pre-commit.ci badge,
`results.pre-commit.ci/badge/github/<org>/<repo>/main.svg`, is the
service's own and carries its branch in its path.

**A workflow-status badge's link carries `?query=branch%3Amain`**, the
same filter in the spelling the runs page takes, so the page a reader
lands on lists the runs the image answers for.

**The order is fixed**, in three groups, and a tree skips what it does
not own and keeps the rest in that order, so two `README.md` files
compare like with like:

1. what the software is — the version beside `github/v/release`, the
   development status, the licence, the downloads, the supported Python
   versions, `implementation` and `wheel`;
1. whether it works — pre-commit.ci, `lint`, `test`, `docs` and Read the
   Docs, then the sentinels in section 10's calendar order, so a
   workflow moved to another day moves its badge; the calendar has no
   row for the gates, and this list is where their order is decided;
1. what the OpenSSF makes of it — the Scorecard badge, then the Best
   Practices badge, on a line of their own; `scorecard` being the
   calendar's last row, the sentinels end where that line begins.

`img.shields.io/pypi/wheel` and `img.shields.io/pypi/implementation`
are read off the files a release uploaded, not off what the project
declares. `github/v/release` is read in a **pair** with the PyPI version
badge, a disagreement being a release that reached the forge and not the
index.

**A badge that answers with anything but a measurement is a question
with two answers**: the thing it reads has not happened yet, which is
datable and not a defect, or it should have happened and did not, as for
a renamed workflow. Each service words that answer its own way, so it is
read and not matched; section 15 has the command for the narrower half,
a badge not served at all.

What is refused:

- **a badge that asserts a tool rather than measuring one** —
  `linted with ruff`, `code style: black`, rendering the same once the
  tool is gone;
- **`img.shields.io/badge/license-MIT-blue`**, that defect again, which
  the derived licence badge replaces;
- **`last-commit`, `commit-activity` and `contributors`** — they measure
  activity rather than the tree, so a quiet month on a finished library
  reads as decay;
- **a coverage badge** — section 8's floor already refuses a fall;
- **REUSE compliance** — `reuse unregistered` is a registration with a
  service, not a property of the tree;
- **`img.shields.io/pypi/types`**, which reads the `Typing :: Typed`
  classifier and not the shipped `py.typed`, so it restates section 3's
  classifier rule;
- **a link to the repository** — it measures nothing; section 3's
  `[project.urls]` reaches a reader of the index page or the sdist
  instead.

The Read the Docs host is `app.readthedocs.org` and not `readthedocs.org`,
which redirects to it: one spelling, and the target, a redirect being
something its owner can retire. **The downloads badge links to
`pepy.tech/projects/<name>`**, plural, for that same reason, and is
pepy's rather than `img.shields.io/pypi/dm`, which counts the last month
and so falls with nothing changed.

The Best Practices badge is admitted where REUSE's is refused, rendering
for a registered project the questionnaire's live state, which the
Scorecard's `CII-Best-Practices` check scores. Registration is the
maintainer's attestation, and a tree section 10's `scorecard` entry does
not name has a row complete without the badge.

**`CONTRIBUTING.md`'s badge block is inside this rule's reach, and it is
not the row.** Where *This repository in particular* opens with toolchain
badges, the block's first line is its admission rule: each badge names a
choice the sections below explain, or a place to go — the repository
link being admitted there as the place to go — where the README keeps
the ones that can turn red. The block is not owed; a block without its
sentence is refused.

**A publishing repository's `README.md` ends with the line naming who
supports the work**, under a thematic break:

```markdown
---

The btclib organization and its projects are actively supported by
[DGI](https://dgi.io) and [CheckSig](https://checksig.com).
```

It is tier 1's for the reason `SECURITY.md` is: an index renders the
README with no organization beside it. Below tier 1, `profile/README.md`
says it once for all. The line is identical everywhere, and names the
organization rather than one of its packages, with `links` noticing a
dead URL.

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
ask of it. The other three have a package as their subject, not a tier,
so a tree installing none — `package = false`, or a build backend given
no module to build — owes none of the three, and may still keep `tests/`
above the floor, as `.github`'s own suite over the organization does.

**`PULL_REQUEST_TEMPLATE.md` sits under `.github/`**, with the forge's
other inputs, though GitHub also reads it from the root or `docs/`.
Wherever GitHub reads it is rejected: trees would differ for nothing.

**The package directory sits under `src/`.** A package at the root is on
`sys.path` whenever anything runs from there, so an import can resolve
to the checkout instead of the installed distribution, which section 7's
convention tests exist to tell apart; under `src/` the suite tests what
was built or fails outright.

**The package directory is singular by the rule and not by omission.**
One tree is one distribution carrying one package of its own: a
`module-name` listing several modules, and a dotted `module-name =
"foo.bar"` building a leaf under a shared namespace, are both shapes
this file does not state, and a project wanting several packages stays
several repositories. `tests/surface_test.py`'s `package()` reads the
key rather than resolving it, so either shape meets a message naming the
repository and the key.

### The documentation

**A tree that releases a Python package provides documentation; a tree
that documents need not release.** A release carries a URL no later pull
request can correct, for the reason section 11's *Pages and Read the
Docs* gives, so what it points at has to exist. The converse does not
follow: a tree that builds `docs/` and subscribes no service is
complete.

`docs/source/` holds a few hand-written pages around a reference sphinx
generates from the docstrings of a typed public API.

**The theme is `furo`**, declared in the `docs` group and named in
`docs/source/conf.py`: built for that shape — the content first, the
navigation and the page's contents in sidebars, light and dark from one
setting — where `shibuya`'s landing pages are surface these trees would
not use. Whether sphinx stays the generator is open.

**The build runs `-n` as well as `-W`.** `-W` turns a warning into an
error, and an unresolved cross-reference — a renamed class in a
`:class:` role, a moved function — is not a warning without `-n`, so the
build is green and the link goes nowhere.

**`sphinx.ext.intersphinx` comes first**, with a mapping for python and
for whatever else the annotations reach. Without one, a name from
outside the tree — `collections.abc.Sequence`, `pathlib.Path` — draws
`reference target not found`, and `-n` measures the standard library.

**`intersphinx_cache_limit = 0` where a mapping names a sibling of this
organization.** Sphinx reuses a fetched inventory for as many days as
the key allows, invisibly to a diff and even under `-E`, and a sibling's
`latest` moves on this organization's own landings: a name it removed
still resolves on a checkout and fails on a runner. Asked of every
mapping, it would cost every build a fetch and fail offline under `-W`.

**`nitpick_ignore` holds only entries whose reason is written beside
them**, an entry being a reference that genuinely cannot resolve. Every
entry is a reference the build stops checking, so a broad
`nitpick_ignore_regex` gives up the check itself — the trade section 5
makes over `ignore` and section 8 over `exclude_also`.

**`myst_heading_anchors` is 6.** Unset, myst generates no heading
anchors, and a link into a root markdown file's heading fails `-W` under
`-n`; six is every level markdown heads at, a fixed point rather than a
depth re-derived from headings that move.

**`--keep-going` is not passed.** In the sphinx `uv.lock` resolves the
flag is accepted, hidden from `--help` and unused: `-W` alone reports
every warning a build raises and fails at the end.

**`exclude_patterns` names what the tree writes under `docs/source/`,
and is empty where nothing does.** `sphinx-quickstart` seeds `_build`,
`Thumbs.db` and `.DS_Store`, of which the last two are never documents
under the `.md` and `.rst` suffixes these trees declare and `_build` is
live only for a build directory written inside the source directory.

**`templates_path` names the directory under `docs/source/` where the
tree keeps its own templates, and a tree keeping none does not carry the
key.** `sphinx-quickstart` seeds `_templates` and git carries no empty
directory, so the key arrives naming nothing, and sphinx builds green on
it while it reads as a theme override.

## 3. `pyproject.toml` is the configuration

One file holds the project metadata and every tool that can be
configured in it. A tool the lint gate runs that looks for its
configuration by name and not there keeps a file of its own, which the
hook then passes no path to; section 14 names each of those files.

- **The build backend is `uv_build` where the project is pure Python.**
  The sdist's inclusion is then declared as glob patterns in
  `[tool.uv.build-backend]` rather than in a file with a language of its
  own. What makes a project the exception is what it compiles:
  `btclib-secp256k1` builds a vendored C library through cffi and cmake,
  which hatchling answers with a build hook and `uv_build` does not.

    Section 2's `src/` rule matches each backend's own default, so
    neither needs a key that states it: `uv_build` looks under `src/`
    unless `[tool.uv.build-backend] module-root` overrides it.

    `requires` names every entry — the backend among them — with a
    floor and a **ceiling at the next major above the newest release
    the tree has measured to work**, tightened to whatever release broke
    it where a break has been measured, as `hatchling>=1.27,<1.32.1` is:
    an isolated PEP 517 build resolves every entry fresh, outside
    `uv.lock`, so an unbounded one builds under whatever release exists
    on the day. A release is measured by a build of this tree that
    resolved it and ran against it. `tests/pyproject_test.py` asks only
    that both bounds be present.

    Under `uv_build` the ceiling sits tighter, at the next minor, uv
    bumping its own minor for a breaking change and releasing this
    backend with itself; that is uv's discipline, not a general rule.

    The floor is the boundary of the property it keeps — under
    `uv_build`, the sdist carrying `pyproject.toml.orig` beside its
    normalized copy — and the comment at the key gives the measurement.
    That boundary is found by calling the backend's own sdist hook at
    each version, not through `uv build` under a pinned `requires`. A
    floor above it excludes backends that keep the property.
- **The version is declared once**, in `[project]`. The package reads it
  back with `importlib.metadata` and the sphinx `conf.py` parses this
  file; two declarations are two things a release has to compare.
- **The name in `[project]` is the distribution's, and the repository
  is named after it, hyphenated, never after the import package.** PEP
  503 normalizes runs of `-`, `_` and `.` in a distribution name to a
  single `-`, so the hyphen is the canonical spelling, where an import
  package is a Python identifier whose grammar admits `_` and never `-`.

    **`name` itself takes that same canonical spelling**, the rule above
    asking only that a distribution and its repository agree.

    **Wherever the distribution is named for somebody to read or copy,
    it takes that spelling**: the normalization installs the same
    distribution either way and no gate reports it, so the written form
    decides what a reader copies. `tests/names_test.py` reads the
    position rather than the spelling, and the rest is a reader's catch.

    **A PyPI page is linked as `https://pypi.org/project/<name>/`**, the
    form `https://pypi.org/p/<name>` redirects to: the site serves
    either spelling and redirects neither, so which one a reader is
    shown is the writer's.

    **The bullet has no subject where a tree builds no distribution**: a
    `package = false` tree's `[project].name` names none and is its own
    choice, PEP 503 folding `.github` to `-github` in any case.
- **PEP 639 licensing**: `license = "MIT"` as an SPDX string and
  `license-files`, not the deprecated table and not a `License ::`
  classifier. The floor that carries them is the backend's own, an
  older hatchling rejecting both halves outright; a constant copied from
  another project is a requirement the build does not use.

    **`license-files` names `LICENSE` and `AUTHORS.md`, and nothing
    else**, in a file that declares a build backend: where nothing is
    built the key names files into an archive that does not exist, and
    `AUTHORS.md` is where the archive says the collective is listed.

    **Nothing local refuses the classifier beside the expression**, a
    file carrying both passing `twine check` and the
    `trove-classifiers` comparison alike, which is why this is a rule.
- **`authors` names what the MIT notice names**, in every file that
  declares a `[project]` table, whether or not that file builds
  anything: `COPYRIGHT`, `LICENSE` and ruff's `CPY` header already fix
  the collective. Scoping the key to a file that declares a build
  backend leaves it unread in a tree that builds nothing.

    **The address is fixed by the trees agreeing, not by a literal
    here**: section 15's suite asks that the name be `COPYRIGHT`'s and
    that every declaring tree answer the same address as every other.
- **`keywords` are the GitHub topics**, the same names in the same
  lowercase spelling. The keywords carry an order and the topics do not:
  PyPI shows keywords as given, while
  `gh api repos/<org>/<repo> --jq '.topics'` answers alphabetically. The
  order decides which name is left out when GitHub's twenty are full.

    Both name what the tree holds, so both are read against the tree
    rather than against the list they were copied from.

    **The rule turns on the `[project]` table and not on the index.** A
    tree that uploads nothing declares the list all the same, so the
    topics github.com shows have something to be read against; a
    repository with no `pyproject.toml` has section 16's checklist.
- **`classifiers` are present**, and each is a claim about this tree
  rather than a line taken from a sibling's: `Typing :: Typed` and
  `py.typed` ship together or neither ships, both being PEP 561's
  promise that the installed package carries types; an
  `Operating System` only where the package is built for it and
  `OS Independent` only where nothing is compiled; and one
  `Programming Language :: Python :: X.Y` per interpreter the matrix
  runs. A `t` suffix in the matrix names that same `X.Y`, unlike a
  `pypy` prefix, which has a classifier of its own under
  `Implementation`.

    PyPI's own `Free Threading` classifiers are a maturity level an
    author claims, and one is declared where the merge gate — the jobs
    the required check waits on — exercises the free-threaded build.

    Section 7's closing rule makes these tests rather than hopes: a tree
    that publishes — section 15 saying why publishing decides that and
    not section 1's library — carries `interpreters_test.py`, which
    reads the floor, the classifiers and the matrix and refuses a
    disagreement, `Free Threading`, naming no one version, being gated
    by a biconditional instead. Nothing local refuses a classifier that
    is not one at all, so a tree compares against `trove-classifiers`.

    `.github`'s own suite reads a tracked `py.typed` rather than an
    installed one, `surface_test.py` and `classifiers_test.py` asking
    `git ls-files`; where a tree publishes, section 12's
    `check-wheel-contents` verifies it once the package is named there.
    A tree short of tier 1 owes the marker with no gate over it.
- **`[project.urls]`** carries homepage, documentation, download,
  changelog, repository, issues and pull requests.

    **The names above are a publisher's, and a tree that declares the
    table and releases nothing carries the ones with a referent.**
    `documentation` and `changelog` are the two such a tree has none
    for: no site stands behind it, and `changelog` is the name each
    publisher here gives `RELEASE_NOTES.md`, which section 2 gives a
    tier-1 tree alone. Pointing it at the `CHANGELOG.md` every tier
    carries is the rejected alternative, one name serving two documents.

    **A releasing tree's `homepage` is its own documentation site, in
    both surfaces that carry the name**: this field, which an index
    serves with the package, and the repository's `.homepage`, the
    *About* link on its page. A project's home is what documents it and
    not a project page. The two are read apart:

    ```shell
    gh api repos/<org>/<repo> --jq '.homepage'
    sed -n '/^\[project.urls\]/,/^\[/p' pyproject.toml
    ```

    Where they disagree, moving the setting to whatever `pyproject.toml`
    declares consecrates the state rather than correcting it: the rule
    sends both surfaces to the documentation the tree itself provides.
    **`documentation` names that same URL, and stays**, being the field
    indexes and tools read for documentation specifically.
- **No upper bound on a sibling dependency.** Two projects developed
  together coordinate a break at release time, where a ceiling makes a
  published artifact refuse a version it works with.
- **Every comment carries the reason and the negative result**, held to
  section 9's 80 columns by the `toml-comment-width` hook, which reads
  them as bytes.

## 4. The lint gate is `.pre-commit-config.yaml`

**The lint workflow runs this very file.** There is never a second list
of the same tools in a workflow: what CI enforces is exactly what a
local run of it enforces, and a hook cannot be gated by pre-commit.ci
alone.

**Every hook that has a fix mode runs with it turned on**, a check-only
hook spending a human round on a finding a flag would have applied. A
hook stays check-only where it has none.

### The `ci:` block

```yaml
ci:
  autofix_prs: false
  autoupdate_commit_msg: "Update the pinned pre-commit hook revisions"
  autoupdate_schedule: weekly
  skip: [mypy]
```

`autofix_prs: false` because a bot committing to a branch is at odds
with a setup where no workflow token can write; a failing hook is fixed
by its author. `skip: [mypy]` because that hook shells out to uv, which
pre-commit.ci does not have — the lint workflow covers it. No
`autoupdate_branch`: the default branch is the only branch.

### What the hooks cover

- **the file checking itself** — `meta`'s `check-hooks-apply` and
  `check-useless-excludes`, so a pattern that has stopped matching fails
  rather than quietly stopping; and a local `pinned-rev` pygrep hook
  refusing a `rev:` that names a bare major or a prerelease, both of
  which `autoupdate` offers as readily as a release.

    **A version this file holds against `autoupdate` is declared in a
    local hook**, the one shape it does not reach, `autoupdate`
    rewriting the `rev:` of every `repo:` but `local` and `meta`.
- **hygiene** — `trailing-whitespace`, `end-of-file-fixer`,
  `mixed-line-ending --fix=lf`, `check-case-conflict`,
  `fix-byte-order-marker`, `check-merge-conflict`, `check-vcs-permalinks`,
  `check-added-large-files`, and `check-shebang-scripts-are-executable`
  wherever the repository has scripts.
- **submodules** — the rule is *pinned*, not *forbidden*, a submodule
  being the one dependency in neither the lock file nor an sdist.
  `forbid-submodules` where there are none; where one is legitimate, a
  local hook refusing an unpinned or moved submodule takes its place,
  and section 11's `gitsubmodule` ecosystem says when upstream moved.
- **syntax** — `check-yaml`, `check-json`, `check-toml`,
  `pretty-format-json`.
- **Python shape** — `debug-statements`, `check-docstring-first`, and
  `name-tests-test` at its default, the spelling section 7 states.

    **`check-docstring-first` takes an exclusion naming the modules that
    carry a PEP 258 attribute docstring**, which sphinx renders on a
    built api page and the hook reads as a second module docstring; it
    names paths and not the directory holding them, a hook with no file
    to read failing `check-hooks-apply`.
- **secrets** — `detect-private-key` and `detect-secrets` against a
  committed `.secrets.baseline`. A baseline, not an exclusion: an
  excluded file is unwatched, where a baseline entry is a finding
  somebody has read. The two entropy plugins stay off where the vectors
  are hex strings; not gitleaks, whose hook ids all pass `--staged`.
- **spelling** — `codespell` and `typos`, both configured in
  `pyproject.toml`, both skipping vendored vectors: a typo inside an
  upstream vector is part of the vector. `typos` is a `local` hook
  pinned through `additional_dependencies`.

    **`codespell --version` answers `0.1.dev1+g<sha>` and not the
    release its `rev:` names**, what follows the `g` being the commit:

    ```shell
    gh api --jq .sha repos/codespell-project/codespell/commits/<rev>
    ```

    The commits endpoint, so the command holds however the repository tags.
- **prose and markup** — `markdownlint-cli2`, `prettier` (yaml and
  jsonc), `taplo-format`, `yamllint`.
- **schemas** — `check-dependabot`, `check-readthedocs`,
  `check-github-issue-config` and `check-github-issue-forms`, because a
  typo in one of them is not an error to the service that reads it: it
  silently does nothing. The issue pair selects narrowly, both carrying
  `types: [yaml]`, and each goes where `ISSUE_TEMPLATE/` holds it.
- **workflows** — `actionlint` and `zizmor`, both at zero findings, both
  required to stay there. actionlint via its Python packaging, the
  upstream hook's only non-docker id needing a go toolchain.
- **Python** — `ruff-check --fix` and `ruff-format`.
- **docstrings against signatures** — `pydoclint` over the package: the
  `D` family checks that a docstring *exists*, this that it describes
  the parameters and the return the signature declares.
  `skip-checking-short-docstrings` is **each repository's to set, and
  what decides it is the form a docstring's contract takes there**: at
  its default a docstring carrying sections is held against the
  signature and one carrying none taken at its word. So `false` where a
  section is how that tree's docstrings state it, the default where they
  state it in prose, the answer going in `[tool.pydoclint]`, section 3's
  rule and not a new one.
- **types** — a mypy hook, below.
- **packaging** — `uv-lock`, `pyroma`, and `check-sdist` wherever an
  sdist is built, section 12's condition rather than a second one.

    **`pyroma` is declared locally as well, and run out of the `check`
    group**: `language: system` with
    `entry: uv run --locked --only-group check pyroma`, and upstream's
    own `args: [-d, --min=10, .]`, `pass_filenames: false` and
    `always_run: true` written out. Its version is then the lock file's,
    and a bound naming no prerelease is the only thing holding the
    packaging checker at a release; what the shape buys is the bot's
    pull request going red while it carries one (btclib-org/.github#1199).

### The local hooks

- **mypy** — a trade-off with two right answers rather than a rule.
  Either way `--ignore-missing-imports` is off: it turns an unresolved
  or misspelled import into `Any`, which is the opposite of strict.

    - **A local hook**, `language: system`, running `uv run --locked
      --no-default-groups --group lint --group test mypy <package> tests
      .github/scripts` with `pass_filenames: false`, checking against the
      project's own locked environment. Its price is `skip: [mypy]` in
      the `ci:` block, `uv` being absent on pre-commit.ci.
    - **`mirrors-mypy` with pinned `additional_dependencies`**, where the
      type check needs a small, stable set pinnable by hand. Its price is
      that second declaration, which nothing keeps equal to `uv.lock`;
      what it buys is the type gate running on pre-commit.ci too, and
      what decides between the two is which price is smaller.
- **`toml-comment-width`** — pygrep, 80 bytes on a toml comment, columns
  where the comment is ASCII: `.{80}\S*[ \t]` reports a line only when
  whitespace is left past byte 80, so a one-token overflow is exempt.
- **`decoded-subprocess-encoding`** — pygrep refusing `text=True` and
  `universal_newlines=True`: a decoded child process takes the locale's
  encoding, the defect ruff's `unspecified-encoding` catches one layer
  in.
- **`reasonless-coverage-pragma`** — pygrep refusing a `#`-comment
  `pragma: no cover` or `pragma: no branch` with nothing after it on its
  own line, narrower than section 8's own acceptance command: the match
  wants a `#` immediately before `pragma`, so a docstring quoting the
  rule is not refused.
- **`local-link-prefix`** — pygrep refusing a markdown link whose
  destination is local and is not explicitly relative, beginning
  neither `./` nor `../`, in every repository of the organization, this
  one included: an explicit relative prefix is what lets a check
  downstream key on one pattern.

    Where documentation is built, `docs.yml` greps the built html for
    `href="#./` or `href="#../`, what MyST renders in place of a link
    `docs/source/conf.py`'s `RootFileLinks` transform cannot resolve.

    **The prefix is the rule, and not the extension**, an extensionless
    destination and a path into a subdirectory reaching that fallback
    too; whether a destination exists at all is section 10's `links`
    workflow's question. A `[` preceded by a backtick is exempt.
- **`no-hyphen-at-end-of-line`** — pygrep refusing a line that ends
  inside a word, at that word's own hyphen, in the file types whose
  prose a build renders: markdown, reStructuredText and Python. Markdown
  joins two source lines with a space, so a word wrapped there renders
  with the hyphen *and then a space* inside it, which a diff does not show.

    **A docstring reaches that rendering by another route**, which is
    what puts Python in the list: docutils leaves the break in the
    paragraph it builds and html collapses it to a space. Over Python
    the hook refuses more than a build renders.
- **`unquoted-placeholder`** — pygrep refusing a placeholder that stands
  as a whole argument and carries quotes, in every repository of the
  organization, this one included. Section 9 is the rule and what the
  quoting costs: quotes make the angle brackets ordinary text, so a
  paste made before the placeholder is filled in reaches the tool with
  the placeholder as its value instead of failing at the shell.

    **`CHANGELOG.md` and `RELEASE_NOTES.md` are outside it**, by
    `exclude: ^(CHANGELOG|RELEASE_NOTES)\.md$`: section 9 makes both
    append-only, so a refused shape in a landed entry has no repair.

    **What separates an exempt quote from a refused one is a property of
    the line, not of the fence around it**: no shell puts a space around
    an assignment's `=`, and a quote nested inside a quote of the other
    kind is a nested program's. A reader meeting an over-report rewrites
    the line rather than waiving the hook.
- **`check-changelog`** — a local hook, `language: system`, running
  `python3 .github/scripts/check_changelog.py` with `pass_filenames:
  false` and `always_run: true` over `CHANGELOG.md`, ahead of
  `markdownlint-cli2` so it reads the file before that hook's `--fix`
  repairs the seam the blank-line check names. `merge=union` stays on
  that file (btclib-org/.github#21's ruling) and this is the gate its
  price bought back: a repeated `###` heading, a heading with no blank
  line above it (btclib-org/.github#760) and an entry past section 9's
  three-line bound are all refused.

    A heading is repeated only where the matching text does not end up
    adjacent once the merge is done, two branches adding the same new
    heading at the one shared anchor being folded into one entry, or
    where a new heading repeats one already in the section at the
    shared base.

    The check has to fire before the merge that creates the duplicate,
    which only a hook on the branch does; news fragments and a
    landed-order gate are declined at btclib-org/.github#305 and
    btclib-org/.github#516.

    **The hook runs on every invocation, and carries no `files:`**, the
    script being handed no file list for a filter to decide anything
    about, and `check-hooks-apply` passing over an `always_run` hook;
    a filter kept and `--all-files` remembered by hand is a convention
    held in prose where this is a hook that fires.

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
  a release's future ones alike, rather than a hand-picked list that
  rots: `ALL` takes a new family in on the pull request that bumps
  ruff's own pinned rev, which is the day somebody is already looking at
  what changed.
- **`ignore` holds three kinds of entry, told apart by what its comment
  argues.** A rule the formatter conflicts with, cited from ruff's own
  `docs/formatter.md` and not argued here, the list being the vendor's;
  a rule this tree declines on its own merits, argued in the comment
  beside it; and a finding that is real and is not in `ignore` at all,
  fixed or answered with a `# noqa` and a reason at its own site, which
  `RUF100` retires the day nothing needs it.
- **`ignore` names rules, never codes.** The reason sits in the comment
  and the rule sits in the entry, with nothing to look up between them.
- **`FIX` runs and `TD` is in `ignore`.** Unfinished work belongs in an
  issue, where it can be searched, assigned and closed; a marker in a
  comment is a backlog nobody queries, sitting beside code that reads as
  finished. `FIX` refuses `TODO`, `FIXME`, `XXX` and `HACK` wherever one
  opens a comment, on its own line or after code, where `TD` disciplines
  the format of the first three and disagrees with `FIX` where the two
  meet: `TD001` steers a refused `FIXME` toward `TODO`, which `FIX002`
  refuses just as hard. The rejected alternative keeps `TD003`, so that a
  marker
  stands provided it links an issue — rejected because `TD003` checks
  that the link exists and never that the issue behind it is still open.
  A marker inside a docstring or a string literal, and a `TODO.md` at
  the root, are outside what `FIX` reads.
- **Docstrings are gated**: the `D` family with `convention = "pep257"`,
  every public module, class, method and function carrying one.
  `undocumented-magic-method` and `undocumented-public-init` are the two
  `ignore` entries, the convention leaving both enabled: a magic method
  is documented by the data model it implements, so a docstring on
  `__repr__` saying it returns `repr(self)` is the restatement section
  9's *One fact in one place* argues against, and the second rule checks
  that a docstring exists rather than that it says anything, PEP 257
  putting the constructor's documentation in `__init__`'s own docstring
  either way. Both entries are the default, and declining one is not
  drift: the rule is then answered with a docstring, or with a `# noqa`
  that `RUF100` retires as soon as one arrives. The convention also
  settles the pairs ruff calls incompatible, so `ignore` does not name
  the half it disables.
- **Code and prose have separate widths, and both are enforced**:
  `ruff-format` reflows code to 88, and `[tool.ruff.lint.pycodestyle]
  max-doc-length = 80` holds the docstrings and whole-line comments —
  prose the formatter never reflows — to the width markdown is already
  held to. A comment ending in a URL is exempt where everything ahead of
  the URL fits the width, and one following code on its line is outside
  the key — *a Python comment following code on its line is outside the
  number*, section 9. `W505` is the rule that reads the key and is inert
  without it, ruff having no default doc length.
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
    a copy that can drift from its source with every gate green.
    `tests/copyright_test.py` of this repository derives the regex from
    each tree's `COPYRIGHT` and refuses one that is not it byte for byte,
    so that the copies are comparable and a drifted one names its own
    difference.
- **`per-file-ignores`** covers `__init__.py` re-exports and the test
  tree's `assert`, non-cryptographic `random` and the pytest-style rules
  a test legitimately trips. The `D` rules are **not** among them: a
  public test function states what it verifies.

## 6. The code is typed, and mypy is strict

**Every function declares the types of its parameters and of what it
returns**, and `strict = true` is what refuses one that does not. The
obligation and the setting are one rule and not two: without it an
unannotated `def` is not the absence of a claim but the widest one —
mypy takes every parameter and the return as `Any` — so a bare
signature loosens the code around it and not only itself.

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
are caught up on, not an override switching a strict flag off for the
directory that fails it, and not the same bundle enumerated flag by
flag: the first two leave `[tool.mypy]` stating a strictness the tree
does not have, and the third states which checks it passes where what is
required is that every function in it declares its types. Where a single
line genuinely cannot be typed the answer is at that line and never in
this table: its own `# type: ignore[code]`, relaxing a check and never
the annotation itself, rather than a second global exemption.

**Configured is not enforced, and this section asks for both.** The rule
is met where the lint gate runs mypy over the tree, so a `[tool.mypy]`
no hook reads sets a severity rather than applying one. Which hook runs
it, and the shapes it comes in, is section 4's.

`strict = true` is the floor, not the ceiling, and the codes above are
the ceiling: **the same list in every tree**, not a survey each one runs
for itself, because a code that finds nothing today is a ratchet — what
it catches is the line written after the survey. Among them
`ignore-without-code`, so a `type: ignore` names the rule it silences;
`deprecated`, the early warning `filterwarnings = ["error"]` buys at
runtime; and `redundant-expr`, `possibly-undefined` and
`warn_unreachable`, which find the runtime guard whose static type
promises more than an untrusted source can. A code mypy enables on its
own under the version the lock pins is not in the list, and a key
already at the value the block would give it is not in the block:
naming either states a check it does not buy — `mypy --help` writes the
flag that changes a default and gives the default direction as its
inverse, so a setting reachable only as an inverse
(`--show-error-codes`, under `--hide-error-codes`) is one mypy has
already.

**Scope is the package, the tests and `.github/scripts`.** A test whose
subject is a script under `.github/scripts` loads it by path, that
directory being no package, so the type check is what reads a script
before it runs whether or not one was written for it.

**`docs/source/conf.py` is outside it.** Sphinx is the `docs` group's
and no shape of section 4's mypy hook installs it, so what that file
imports is unresolved in the hook's environment; and `python_version` is
one value for the whole table, so the file would be checked at the floor
the library declares and never runs on. Every documentation build
executes `conf.py`, so a repository that brings the file into scope
answers the version question first, and that answer is its own.

One run, at the floor. A second pass at the newest interpreter would
check the same code where no source is conditional on the version.

## 7. Tests

### Layout and naming

- `tests/` mirrors the package, directory for directory — or
  `tests/unit/` does, where the suite splits by kind under *Functional
  tests* below.
- **`*_test.py`**, enforced by `name-tests-test` at its default.
  pytest's `python_files` collects `test_*.py` and `*_test.py` alike, so
  a file named outside both is not a red test but no test; one shape is
  what lets a check downstream key on one pattern, for
  `local-link-prefix`'s reason, and the hook's default is which.
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
  a marker nobody registered, is an error rather than a misspelled
  `skipif` that silently stops skipping.
- **`filterwarnings = ["error"]`, with no blanket ignore.** A deprecation
  warning is the early form of a break, and an ignore added here names
  the warning and says what would let it go.
- **`xfail_strict`**: a test expected to fail that passes is a fixed bug
  still marked broken.
- **`--cov` in addopts, and never as the last token.** `--cov` takes an
  optional value, so last it swallows the first path the command line
  gives — a run measuring nothing against a threshold of 100.
- **`-n auto --dist worksteal`** where the suite is long enough for the
  pool to pay, measured on CI rather than on a laptop; `worksteal` where
  the cost is lopsided, `load` handing the queue out in chunks.
- **`pytest-randomly` is installed and needs no flag.** It shuffles and
  prints the seed, which guards the one thing a green suite cannot tell
  you about itself: whether a test passes because of what ran before it.
  `-p no:randomly` puts the file order back when a failure has to be
  reproduced, and a suite declining the shuffle declares it in
  `tests/README.md`, with a reason weighed against what the plugin
  catches — an order two tests need is not one, since the sequence can
  live inside one test.
- **A suite that waits on anything outside its own process carries a
  measured per-test timeout.** A hang is the one failure a suite cannot
  report on itself: the run stops rather than fails, and the workflow's
  `timeout-minutes` names the job rather than the test. Such a suite
  sets pytest-timeout's `timeout`, measured against its own slowest test
  on a loaded machine and the measurement written beside the number; a
  suite of pure functions does not owe one.
- **No `slow` marker unless a measurement earns one.** A plain run is the
  run that has looked at everything.
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

Where the comparison is a test, this is a golden file. Where it is a
page or a document, it is a hook with a `--check` flag instead, written
`language: python`, stdlib-only and `always_run: true`, so it runs on
pre-commit.ci as well, where `uv` is absent — `always_run` rather than a
`files:` pattern, an artifact going stale from an edit to any input.

### Test data is vendored, never fetched

Every file a test reads is committed beside it, a suite that fetches its
input having a verdict that depends on somebody else's uptime.

**Two kinds of file, and only one of them can be pinned.** A *vendored
upstream file* is a copy of a file in somebody else's repository, and a
commit and a git blob SHA-1 identify the original. *Recorded or
constructed data* is written from a project's source rather than copied
from it, so there is no upstream blob for a pin to name and the entry
says instead which source it was written from and how a reader
reproduces it. What the tree derives from its own code is neither, and
the subsection above has it.

**A data directory beside whatever reads it**, which is `tests/_data/` where the
suite is the only reader and a directory beside the package or the script where
it is not. The underscore is `tests/_data/`'s alone, saying the directory is not
a package where a sibling of `tests/__init__.py` would otherwise read as
importable; at the root nothing is a package, so the directory takes the name
that says what it holds, and the way in is a path built from `__file__` either
way.

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

`blob` is the git blob SHA-1 a tree entry already carries and
`git hash-object` reproduces locally, where a digest of the bytes says
whether the copy changed here and never whether upstream moved; `pulled`
is what `git log --follow --diff-filter=A` answers, and `behind` is
staleness rather than a defect. Under the
block a verdict says how the copy stands to that blob — identical,
identical but for what a fixer in the gate rewrote, or transcribed where
the upstream is prose. A fixer that would rewrite those bytes for
nothing is excluded from the directory.

**A repository with vendored upstream files runs `vendored-vectors`**,
which re-checks every pin on section 10's schedule and opens an issue on
drift rather than refreshing anything. One whose data is all recorded
says so where the workflow would be, an absent check otherwise reading
as an omission.

A vector the tree fails is vendored anyway and marked `xfail`, never left
out — an absent vector hides the defect it would have shown, and
`xfail_strict` turns the marker red the day the defect is fixed. A
licence travels with what it covers, under a name that cannot be read as
licensing the directory around it.

### A capability the platform may refuse is asked for inside a guard

The call that asks for it sits in a `try`, and the refusal becomes a
`pytest.skip` naming what refused, which this section's `-ra` reports.
Creating a symlink is the case the family carries, an account without
`SeCreateSymbolicLinkPrivilege` getting an `OSError` rather than a link:
what the guard is for is a contributor's own machine rather than a
runner, which holds the privilege and runs the case either way. The
case's `def` carries section 8's `pragma: no cover`; the `except` and
the `pytest.skip` under it are not the site, being the lines that do not
run wherever the capability is granted. Leaving the call bare is the
rejected alternative, and what it costs is a red suite on the one
machine that cannot run the case.

### Integration tests

`tests/integration/` is whatever needs something the repository does not
ship — a node, a device, an emulator. Each test skips itself without the
environment switch that asks for it, the switch is named in the skip
message, and the directory is omitted from the coverage ratchet, a body
that skips itself otherwise being an uncovered line at every commit.
What covers them is an unattended job, and that job fails if its tests
skipped rather than ran.

### Functional tests

`tests/functional/` sits beside `integration/` where a suite's subject
is a running process rather than a module, a test that drives what the
repository ships over a port having no module to sit beside.
`tests/unit/` then carries the mirror; every directory is in
`testpaths`, so a bare run is still the whole suite; and the split is
declared in `tests/README.md` with its reason, this section's own rule
for a convention only prose states. The two are told apart by what they
need rather than by how long they take: `integration/` needs something
the repository does not ship, `functional/` needs nothing it does not.
Flattening is the rejected alternative, moving the record of which tests
hold a port where a `testpaths` entry cannot see it.

### Property tests

A tree that has the property section 10's `fuzz` entry keys on owes a
property layer, whether or not that section's record gives it the
sentinel: a property test answers *does this hold over the domain I
described*, where a fuzzer answers *what is in the domain I did not
describe*. hypothesis is the named shape, its profiles registered once
in `tests/conftest.py` rather than repeated on every `@given`:

```python
settings.register_profile("default", deadline=None, max_examples=500)
settings.register_profile("thorough", deadline=None, max_examples=2_000)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "default"))
```

`deadline=None`, because a per-example time limit is a timing flake on whichever
cell of the matrix is slowest; the default example count set where its cost on
the whole suite is affordable; and the deep profile opt-in, the search that
finds a latent defect not being one to run at every commit, and what it finds
graduating into a vector test rather than staying in a search that may not
repeat it. A tree that answers the property with hand-rolled properties over the
same domain declares that in `tests/README.md`, and a suite whose subject is a
measurement rather than a parser does not owe the layer at all.

### Convention tests

The distinguishing feature of the suite, and the part an older repository
is most likely to lack. A convention that only prose states is a
convention that drifts; each of these turns one into a red test, and none
of them carries an exemption list that is allowed to grow:

- **the public surface** — `__all__` is declared by every module and
  package at every depth, a module under a private name excepted as no
  part of that surface, and a census walks the tree rather than listing
  it, so a new public name fails until it is exported or recorded. Where
  the package is published this is not a bullet the clause below
  excuses: `py.typed` says the types are supported, and which names are
  public is the other half of that sentence;
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
  construction that forgot the argument is what turns red.

A new repository does not need all of these. It needs the ones its own
conventions state in prose, and the rule that a convention worth stating
is worth a test — the public surface excepted, which a repository
publishing an importable package has whether its prose states it or not.

**Which of them a repository implements is declared, not inferred.**
`tests/README.md` names each bullet above that this repository tests and
the module that tests it, and a test in the same suite asserts that
declaration is true. The suites do not agree on names and are right not
to: a package of one module folds several of these checks into the one
file that is about it. The escape clause above makes an *absent*
convention test indistinguishable from a convention the repository does
not have, and the declaration is what tells those two apart.

**A convention test moves with the code it walks.** A module carved out
into a repository of its own stops being walked the moment it leaves,
so the convention tests that covered moving code are part of what moves
and both `tests/README.md` files change in the same pair of pull
requests. What must *not* be aligned is where those tests live or what
they are called — only which conventions are tested, and that each tree
says which.

## 8. Coverage at 100%

**A tree gates the code it holds against the failure that code has**, and
the coverage floor below is one such gate rather than the whole rule. A
package that installs is measured by that floor. Course material is
measured by whether it still runs on the dependencies pinned today, a
floor over code nothing executes measuring nothing. A suite whose
subject is outside its own tree is itself the gate rather than something
with one — `.github`'s suite runs against the other repositories, so a
floor here would be the instrument measuring itself.

Which of them applies is read off what the tree installs. A tree that
installs no package owes no floor, that rule having no subject there;
what it owes instead is the gate its own material's failure asks for, in
the workflow a reader already goes to for what runs that material.

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
- **`branch = true`.** Statement coverage alone calls a half-tested `if`
  fully covered: the line ran, one of its two ways out never did. The
  gate is 100% of statements *and* branches.
- **`exclude_also` where the unreachable thing is one shape repeated.**
  A failure no input can provoke — a `raise RuntimeError` behind a call
  that cannot fail — is excluded once, by pattern, rather than carrying
  a `pragma: no cover` at every site. A pattern that would also exclude
  something a test can reach is not one of these: for a one-off, the
  pragma is still the answer.
- **`source` is named, never left to `--cov` alone.** Unnamed, it measures
  every file the run imports, which reaches a script a test imports by
  path — uncovered, because nothing runs its `main()` but a subprocess.
- **100 is not the same rule with the bar raised.** coverage special-cases
  the value: nothing short of an exact 100.00% passes, where 99.99 passed
  everything above 99.985%. It also makes the report agree with the exit
  code, which a threshold inside the rounding step does not.
- **What it costs is paid at the site**: a line no ordinary run reaches is
  covered by patching what stands in the way, or carries a
  `pragma: no cover` with its reason. Neither is a build left red.

  **A statement only some invocations execute is covered only on those
  invocations**, so it takes a test of its own rather than a pragma: a
  pragma there would exclude a statement every run the project cares
  about does execute.

  **The reason goes on the pragma's own line, after ` -- `, for
  `pragma: no cover` and `pragma: no branch` alike** — the dash a
  comment writes, an em dash being this file's own. What the position
  buys is that

  ```shell
  git grep -nE 'pragma: no (cover|branch)$' -- '*.py'
  ```

  answers empty in a tree that keeps the rule, so every line it names is
  a defect under it. Section 4's `reasonless-coverage-pragma` hook
  refuses a `#`-comment pragma with no ` -- ` reason at the gate,
  narrower than the command above: its pattern wants the `#` immediately
  before `pragma`, so a bare mention of the phrase in a comment's own
  prose is left to a reader running the command. ` - ` is the rejected
  alternative, and what it costs is a check written for one spelling
  answering a confident zero for a tree that writes the other, which is
  what

  ```shell
  git grep -nE 'pragma: no (cover|branch) - [^-]' -- '*.py'
  ```

  is for.

  **Where a no-argument signature leaves `ruff format` nothing to reflow
  but itself, the inline half moves to the decorator's line where one
  exists.** Adding the reason after ` -- ` pushes such a `def` line past
  what the formatter will leave on one line, and coverage excludes the
  whole node from a pragma on the decorator exactly as it does from one
  on the unreflowed `def` line. Where there is no decorator, the reflow
  happens anyway and the reason stays on the signature's own last line:

  ```python
  def f() -> (
      None
  ):  # pragma: no cover -- reason
  ```

  every physical line of one multi-line statement mapping back to its
  first. A whole-line comment written above the `def` instead excludes
  nothing, coverage's decorator range starting at an undecorated `def`'s
  own first line.

  **A reason too long for the line goes above it as well, the inline
  half naming the case.** The fuller reason is the comment over the
  line, or the docstring the file or the function already opens with
  where one reason covers every pragma under it. Letting it **replace**
  the inline half is the rejected alternative, and what it costs is the
  gate: a conforming tree would then answer the grep non-empty.

  **A pragma is a comment, and one inside a string is not a site.**
  coverage matches its exclusion patterns against the raw source a line
  at a time rather than tokenizing it first, so what leaves `statements`
  is the statement the matched line belongs to — one nobody wrote the
  pragma for, and no percentage reports the loss. So prose in a Python
  file writes the pragma in backticks and without its `#`, which is what
  keeps it out of both commands above; the `#` in a `.toml` comment, in
  a workflow's, or in a `CHANGELOG.md` entry is outside the rule rather
  than short of it, coverage reading Python source alone. Which of the
  two a line named above is, the output does not say: what answers it is
  a parser rather than a pattern, and section 15 runs one.
- **Measured on one interpreter**, the one `.python-version` pins, which
  is enough at 100 only because no source branches on the version.
- **The flags live in `pyproject.toml`, and a job types `pytest` with
  nothing after it.** `addopts` carries the coverage flags and
  `[tool.coverage.report]` the floor, so a copy typed into a workflow is
  a copy a maintainer never runs. What a job may still type is an
  argument about that job rather than a second copy of a tree-wide
  setting, and what tells the two apart is whether the run does anything
  differently without it: an explicit `--cov-fail-under` qualifies
  wherever the job's construction asks for it.
- **The configuration is read from wherever the run starts.** coverage
  looks for its configuration in the directory the process started in,
  so a suite run from `tests/` finds no `source`, no `branch = true`
  and no `fail_under`: it measures a different set of files and exits 0
  whatever the number is. A tree with a local floor either points the
  run at its configuration from wherever it starts, or makes such a run
  say it is ungated rather than letting it pass as the gate.
- **A selective run is reported and not gated.** `fail_under` applies to
  every report coverage writes, so `pytest tests/foo` would fail on the
  tree's coverage rather than its own. A `conftest.py` hook drops the
  threshold when the invocation asks for something other than the whole
  suite — paths, `-k`, `-m`, `--deselect`, `--ignore`, `--ignore-glob`,
  `--lf` — and never overrules an explicit `--cov-fail-under`. A path is
  a selection only where it leaves a `testpaths` entry out, `pytest
  tests` being what a bare run already collects. The paths are
  `config.option.file_or_dir`, which is `None` and not `[]` under
  `--help`, so a containment test that iterates it ends `--help` in a
  traceback; and setting the threshold means writing to
  `config.known_args_namespace`, pytest-cov reading that copy and never
  `config.option`. An early `-x` is outside the set either way: what
  cuts that run short is a failure and not what the invocation asked
  for.
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
is one a later change can falsify in silence, and what lengthens it
without adding to it is deleted.

- **Tone: neutral, factual, dry.** Explanatory detail is wanted;
  decoration is not, and the sentence that only introduces the next one
  is decoration.
- **A docstring states the contract; a comment carries the reasoning.**
  The docstring says what the call takes, returns or raises, and the
  rule the behaviour comes from — not the name again. The comment says
  why the code is as it is and why not the obvious alternative, which
  stops the next reader from "fixing" a deliberate choice; one rejected
  alternative is the whole of that, and a tour of the others is not.
- **Cite the authority.** Where behaviour comes from a standard, name it;
  where the project deviates, say so and say why.
- **Measure, don't assert.** A number in prose comes from a command, and
  the command belongs beside it. Never state how many of anything a file
  holds: a stated total is a line every open branch has to edit. A
  sentence claims no more than its command answered — *every*, *the
  only* and *none* owe a hunted counterexample — and a control is a
  perturbation the same fault cannot silence, not the check run again
  with another pattern.
- **One fact in one place.** Two files stating the same thing become two
  files disagreeing about it; the second points at the first. What a
  package's reader does not have — the repositories downstream of it —
  it does not name.
- **A reference to another repository is qualified.** A bare `#123`
  resolves inside the repository it is written in, so a cross-repository
  reference is `owner/repo#123` or it points somewhere else in silence.
  The one exemption is a pull request's closing keyword, which the forge
  reads in its own form. A citation names what the issue records, never
  what state the tracker holds it in, the first staying true when the
  issue closes.
- **A citation of a section carries the words it is found by.** A
  heading reads as durable and is retitled by whoever improves a
  sentence, so a section is cited by words the document holds — a
  heading, a bullet's opening, or the number where the document numbers
  its sections — and where it holds none the prose states the thing
  instead of pointing at it. `tests/citations_test.py` resolves a
  citation against the document it names, in every tree.
- **No history in the prose.** Comments say why the code is as it is, in
  the present tense. History has two files of its own.
- **80 columns everywhere prose lives** — markdown by MD013, tables
  included; a Python docstring and a whole-line comment by ruff's
  `max-doc-length`; a toml comment by a pygrep hook. Code is 88, the
  width `ruff format` produces; yaml is 100, because an action pinned to
  a commit SHA with its tag in a trailing comment is past 80 before
  anything else is said. A Python comment following code on its line is
  outside the number: nothing rewraps it, and a reason that will not fit
  goes into the comment above the line.
- **A placeholder is bare, and last.** `<` and `>` are the shell's
  redirections, so a paste made before `<org>` is filled in fails at the
  parse where the placeholder stands bare and last, and reaches the tool
  with the placeholder as a value where quotes make it text. A
  placeholder inside a larger string — `"repos/<org>/$r"` — or a quote
  another language needs is outside this. A line that writes gets a
  fence of its own, since a shell discards a parse error's line and runs
  the next; a value the reader sets goes in an assignment block above
  the fence and is read as `${name:?}`. A comment goes above the fence
  as prose: to an interactive `zsh` a `#` is a word, and an apostrophe
  after it opens a quote that swallows the lines below.
- **A comment whose first word is `shellcheck` is a directive.** Wrap so
  the word does not begin a line: a sentence that happens to parse as a
  directive suppresses a real finding, and the gate exits 0.

### `CHANGELOG.md` and `RELEASE_NOTES.md`

- **An entry is a `###` title and at most three lines.** The title says
  what changed. The body cites the issue in its own text — `(closes #N)`
  where the change closes it, `(issue #N)` where it does not, and
  `(closes owner/repo#N)` across repositories — and carries no
  measurement, no count and no history; the reasoning is the pull
  request's. Section 4's `check-changelog` refuses a longer body.
- **A `###` names one entry, and a new entry goes at the end of the open
  section**, above the heading of the latest release — at the end of the
  file where nothing has been released. The changelog takes what a user
  would notice; the release notes take what a user has to act on;
  neither restates the other.
- **Both files are `merge=union` in `.gitattributes`.** Two branches
  appending at one anchor rebase without a conflict, the driver keeping
  both sides in landing order and sometimes eating the blank line
  between them. `check-changelog` names the seam, a repeated heading and
  a double close, and not the position, which a person reads off a
  command `CONTRIBUTING.md` has.
- **Nothing already written is rewritten.** An entry speaks of its own
  day, and a count in it that has since moved stays. An entry in the
  open section is a live claim, though: a later entry that bears on it
  says so in a sentence, and the append stays an append.
- **A released section may leave `CHANGELOG.md` for its own
  `changelog/v<version>.md`**, that file holding one release and the
  index in `CHANGELOG.md`'s preamble linking it. Past a size ceiling
  GitHub's contents API answers a file with an empty `content` at HTTP
  200, and a file per release is what keeps each of them under it.
  Nothing already written in an archived file is rewritten either, and
  it takes no `merge=union` driver, nothing appending to a release its
  own tag has sealed.

## 10. Workflows

### What every workflow does

- **Every action is pinned to a commit SHA**, with the tag in a comment beside
  the pin: trailing it, or above it where a trailing one would take the line
  past the width `.yamllint.yaml` sets. A tag is a name its owner can move, and
  these run in a job that can read the workflow token. A call to a reusable
  workflow of `btclib-org/.github` names `@main` instead, its `main` being held
  by section 11's rulesets as the caller's is; zizmor is told so,
  `btclib-org/.github/*: ref-pin` under `unpinned-uses`.
- **A tree pins an action at one commit throughout its own workflows**, so
  a new workflow takes the pin the tree already carries rather than the
  newest release: two commits of one action are two versions in effect at
  once, with nothing in either file saying so.
- **An aggregate waits on the jobs of its own file, so a gate the trees do
  not run job for job alike is copied rather than called, and what becomes
  a call is a cell of it.** An aggregate written into a shared workflow would
  have to take the cells with it, `needs:` naming only the jobs beside it;
  `test.yml` is copied on that ground, with its `changes` job a call of
  `reusable-changes.yml` where a tree has one, and `needs:` lists that stop
  differing are what reopens the question (btclib-org/.github#35).
- **A calling job carries only the keywords GitHub's list allows**, which
  actionlint enforces: `timeout-minutes`, `runs-on`, `steps` and `env` are off
  that list, so each is the callee's to set, and an input carrying a caller's
  value across is a copy in disguise (btclib-org/.github#35).
- **A called job that runs Python takes its interpreter from the calling tree
  where the version is a claim that tree makes, and from the callee where it
  is not.** `uv run --locked` resolves what the caller's `.python-version`
  names; where the subject is a version that pin does not give, the callee
  takes it as a required input with no default, a default being a claim this
  repository cannot make for a tree; and a job reading no lock names the
  version on the command line, `uv run --no-project` otherwise taking the
  caller's pin and `uvx` whatever uv resolves (btclib-org/.github#35).
- **A caller's pin does not reach the callee**, whose own Dependabot moves it,
  so a tree's workflow files do not name every version its runs use.
- **`permissions: contents: read` at the workflow level**, and one elevation per
  job where a job needs more: the job that writes a release holds no OIDC token,
  and the job that signs writes no release.
- **`timeout-minutes` on every job that runs steps**, far above what the work
  needs: it bounds a hung job holding a runner. A called job's is the callee's,
  one number for every caller, which only a caller the bound would cut raises.
- **`checkout` passes `persist-credentials: false`.**
- **Concurrency groups are named literally** —
  `group: test-${{ github.event.pull_request.number || github.ref }}` — never
  through `github.workflow`, the *caller's* name in a called workflow, so two
  called workflows would share a group and cancel each other. `github.ref` is
  the caller's there too, so a gate the release workflow calls appends
  `${{ inputs.concurrency-suffix }}` (btclib-org/.github#1083). The key is the
  pull request's own number and not `github.head_ref`
  (btclib-org/btclib#1158); a run with no pull request falls back to `ref`.
- **Triggers**: `push: branches: [main]` and `pull_request`. A push trigger on
  every branch would run the workflow twice for an open pull request, in two
  groups that do not cancel each other; `main` keeps its own trigger because a
  merge creates a commit the pull request never tested.
- **`pull_request` types** are
  `[opened, reopened, synchronize, ready_for_review, closed]`.
  `ready_for_review` because a readied pull request would otherwise wait for its
  next push; `closed` so the merge lands in the pull request's own concurrency
  group. Draft and closed pull requests decline the work in an `if`.
- **`cancel-in-progress` is `true`, and a workflow that takes `closed` and
  declares no `push` trigger writes
  `${{ !(github.event.action == 'closed' && github.event.pull_request.merged) }}`
  instead.** Nothing runs such a workflow on the commit a merge creates, so the
  run in flight is the only reading the merged content gets, and the closed,
  merged run queues behind it (btclib-org/btclib-secp256k1#523). The expression
  tests `merged` rather than `closed` alone because a new push and a close
  without a merge leave nothing worth finishing. **A workflow whose product is a
  comment on the pull request keeps `true`**, `claude-review.yml` for the reason
  section 11 gives. **A `push` trigger carrying `paths` or `paths-ignore`
  declares one**, so such a workflow keeps `true` even where a merge whose files
  the filter excludes leaves it no push run (btclib-org/.github#1238). The
  rejected alternative is the bullet below, `false` with `closed` omitted: it
  spares the run in flight too, at the price of a new push no longer cancelling
  its predecessor.
- **A workflow whose concurrency group sets `cancel-in-progress: false` omits
  `closed`, and says beside its trigger that it does.** There a closed event
  cancels nothing and only starts a run every job declines, so such a workflow's
  `if` guards the draft alone.
- **`paths-ignore` only on `push`.** On `pull_request` it would produce no run
  for a prose-only diff, and a required check that produces no run blocks the
  merge instead of passing it.
- **`workflow_dispatch` on everything**, including the gates: a branch whose
  pull request is not open yet has no other way to ask.
- **`workflow_call`** where the release workflow reuses the gate.
- Every step is a `uv` command with `--locked`.
- **A step that waits for something outside the run is a script under
  `.github/scripts` with a test, not a loop in a `run:` block.** The step exists
  for the verdict it reaches when the wait runs out, which only a test reaches
  (btclib-org/btclib#1165). The wait counts against a deadline rather than
  against attempts, and its test substitutes the transport and the clock.

### The set, and its cadence

A gate runs on a pull request and on a push:

| workflow | what it varies |
| --- | --- |
| `test` | — |
| `lint` | — |
| `docs` | — |
| `release` | a tag, calling the others before it publishes |

**One image and one interpreter.** `ubuntu-latest` and the version in
`.python-version`, and nothing a gate runs varies further: the plan puts a
ceiling on an organization's concurrent jobs, and at that ceiling a second image
before a review buys a rarer answer at the price of every review. Everything
else answers weekly and before a release. The ceiling's figure lives in
`REPOSITORY.md`'s *Plan-gated settings*, beside the command that re-derives it,
and a workflow header or `CONTRIBUTING.md` gives the reasoning with the ceiling
unnumbered.

**An interpreter axis is a gate cell rather than a sentinel row exactly where
the extra cell runs in parallel with the cells already gating the review, and
where it is the pinned interpreter run a second time rather than a version the
package newly claims to support.** `btclib-node`'s `test.yml` carries `3.14t` on
this ground, in a `free-threaded` job beside the `coverage` job at `3.14`. Where
either condition fails, the row belongs in the weekly calendar.

**What runs weekly does not also gate**, so nothing is asked twice at the price
a gate charges. The converse does not hold: a sentinel runs its matrix whole,
the cells a gate covers included, so that its shape reads without re-deriving a
hole from the gate. A sentinel cell that runs the suite passes `--no-cov`,
section 8's floor being a claim about one interpreter on one image;
`reusable-deps-latest.yml`'s header argues an input for the tree that has
established 100% across a sweep's every cell and wants it held there.

**A sentinel's own work is not a pull request's business either, and *not
required* is not the free half of that**: a pull request waits on every check
listed, gating or not.

**What decides is the clock, not the trigger.** A calendar workflow may carry a
`pull_request` trigger `paths`-filtered to its own configuration and to what
that configuration reads, and what then runs is the whole sweep rather than a
cheaper check of it. What decides is how much one run adds to the wait on the
checks a pull request already has — seconds keep the trigger, minutes or hours
leave the calendar the whole of it:

```shell
gh run list --repo <owner>/<repo> --workflow <name>.yml \
  --json createdAt,updatedAt,conclusion
```

Run it for the gate's workflow too, counting only completed runs: `skipped` and
`cancelled` did none of the work. `workflow_call` and
`push: branches: [main]` are outside the question. An unfiltered
`pull_request` needs a reason of its own, stated in the header, and the
organization has three such reasons: this repository's `alignment`, whose
run is seconds and whose subject is nearly every file of the tree;
`integration-bitcoind`, whose regtest job is a required check and where a
required check that never runs blocks a merge; and `codeql`, whose result
the OpenSSF Scorecard reads off a merged pull request's own commits.

**A rewrite owes a dispatch.** A schedule-only workflow keeps the previous
file's verdict as its newest run until its cron comes round, so a landing that
changes its steps dispatches it from `main` and reads the badge after that run;
a comment-only change owes nothing. Whatever triggered the newest run, it is
stale unless its `head_sha` descends from the file's last edit:

```shell
gh api repos/<owner>/<repo>/actions/workflows/<name>.yml/runs \
  --jq '.workflow_runs[0].head_sha'
git log -1 --format=%H -- .github/workflows/<name>.yml
```

This is a person's check rather than a gate's, which would cost an API call per
scheduled workflow of every tree on every run. `workflow_dispatch` also runs a
sentinel too new to have runs, or by hand before a release.

Two tables make the calendar, and they are the calendar — the workflow owns a
day and an hour, the repository owns the minute:

| workflow | day | hour |
| --- | --- | --- |
| `vendored-vectors` | Monday | 03 |
| `bootstrap-dns` | Monday | 04 |
| `mutation` | Monday | 05 |
| `fuzz` | Tuesday | 04 |
| `integration-bitcoind` | Tuesday | 05 |
| `zkp-oracle` | Wednesday | 02 |
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

**The rows are in the order of what they ask about**, family by family. A new
sentinel takes the slot its family already holds rather than the end of the
table: section 2 puts the Scorecard badge at the head of the OpenSSF line
because `scorecard` is the last row, so a sentinel appended past it takes that
reason away. The day and the hour place a row among the families, so a slot free
between two rows of another family does not seat it.

**The week is the whole of the grid's period**: every row is weekly, and a
workflow that would rather run monthly runs weekly instead.

**The weekday is the same in every repository**, so a failure notification names
the workflow by its day. The minute is the repository's because GitHub queues
same-minute schedules across repositories and a long enough queue drops a run;
`:00` is in no row, being the minute everybody else's cron picks.

**The hour is chosen against this organization's own load, not GitHub's**, whose
documented remedy for its queue is the minute and names no hour. A row starts
its workflow in every tree that has it, so the rows sit before the working day,
when the ceiling is not being spent on a pull request somebody waits for.

**The hour is UTC, and the band grows downward**: a UTC hour falls later in the
morning while the clocks are forward, and the band's late end reaches the
working day first. **A `timezone:` beside a `cron:` fails `tests/grid_test.py`
outright**, rather than being converted.

A day is a slot rather than a census: *Which trees carry which sentinel* below
is which repositories run it. Dependabot is in neither table and runs Thursday,
the day `deps-latest` reports on the upgrade before the pull request arrives,
with its own minute in `dependabot.yml`.

`tests/grid_test.py` reads both tables and every `cron:` of every repository, in
both directions: a schedule no row names fails there, and so does a row nothing
in the organization answers to. Section 15 has the commands a human runs
instead.

`deps-latest` is the sentinel that makes a Dependabot pull request a diff whose
result is already known: it upgrades everything the resolver touches, runs the
suite, the lint gate and the packaging checks, and commits nothing.
`deps-oldest` is its mirror, verifying the claim a floor makes to whoever
installs: `uv lock --resolution lowest-direct` where `deps-latest` runs
`uv lock --upgrade`, in one cell on the oldest interpreter holding
`requires-python` and the dependency specifiers together. Not `lowest`, which
takes transitive dependencies to their minima too and resolves environments that
do not install. What it finds is an issue against the floor.

**`links.yml`'s `targets:` names every markdown file the tree tracks, and the
`*.rst` it tracks where it tracks any**:
`'"**/*.md" ".github/**/*.md" ".claude/**/*.md" "docs/**/*.rst"'`. The string is
the claim that these are the files whose links are checked, and a tracked file
outside it is one this workflow never reads. The rejected alternative for the
`rst` term is the documentation build's own `sphinx-build -n -W`, which fetches
no URL. A hidden directory takes a term of its own because lychee's
walker skips one unless a term names it, and reaches it by a wildcard only when
asked with `--hidden`, which this job does not pass. `tests/links_test.py` asks
each tree's string against that tree's own `git ls-files`, the two file types as
two questions.

`links` runs lychee with `--include-fragments`, so a link into a heading is
checked as an anchor: the forge serves a page whose fragment resolves to nothing
rather than a 404, so a renamed heading breaks the links into it with nothing
red in its own tree. **A `github.com/<owner>/<repo>#heading` link is unchecked
by this flag the moment the step holds a token, which every `links.yml` does**:
lychee's GitHub fallback answers it from the repositories API with `200`
(btclib-org/.github#630), while `blob/main/<path>#heading` stays checked. The
token stays, an unauthenticated runner being rate limited hard enough to look
like rot, so the anchors of this file's headings that every `CONTRIBUTING.md`,
`SECURITY.md` and `CODE_OF_CONDUCT.md` cites are asked offline;
`tests/links_test.py` asks every tree's lychee step for the flag and reads those
anchors against every tree's tracked markdown.

**A sentinel's row arrives with the workflow, and one pull request can do both
only where the first tree is this one**, which then takes the row in the pull
request giving it the workflow. Where the first tree is another repository the
row lands first, and the debt issue its paragraph of *Which trees carry which
sentinel* names carries it:
`test_every_row_of_the_calendar_names_something_that_exists` asks GitHub whether
that issue is open, so the exemption expires when it closes. An adoption pull
request names the tree owing the workflow and the issue carrying the debt; a row
missing either is refused.

**A row that moves is red until the last tree follows it**:
`test_every_cron_is_the_instant_the_calendar_names` names every tree still on
the old instant, which is the port's work, bounded by the issue carrying the
ports.

### Which trees carry which sentinel

Section 14 leaves *which optional workflows exist* to each repository, and these
are not left there: what a tree owes is decided once and ported.

This is the record: one entry per calendar row, naming the trees that carry that
sentinel, in the order the two tables above give the rows and the repositories.
A tree an entry names runs the workflow and shows its badge, section 2's row
reading its sentinels from here; a tree an entry does not name is asked nothing
by that row.

- `vendored-vectors` — `btclib`, `btclib-secp256k1`,
  `btclib-benchmarks`, `btclib-node`;
- `bootstrap-dns` — `btclib-node`;
- `mutation` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`,
  `btclib-benchmarks`, `btclib-node`;
- `fuzz` — `btclib`, `btclib-secp256k1`, `btclib-node`;
- `integration-bitcoind` — `btclib`, `bitcoin-core-rpc`, `btclib-node`;
- `zkp-oracle` — `btclib`;
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
- `sdist-rebuild` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`,
  `btclib-node`;
- `codeql` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`,
  `btclib-benchmarks`, `btclib-node`;
- `scorecard` — `btclib`, `btclib-secp256k1`, `bitcoin-core-rpc`,
  `btclib-node`.

**An entry is what was decided, not what a tree happens to hold**, where section
2's tier is read off the tree. A tree short of what its entry names is a gap in
that tree and not a correction owed here, and a tree carrying a sentinel no
entry gives it is the same finding from the other side. `tests/grid_test.py`
reads the workflow half of both against every tree, a red cell there bounded by
the issue a `BACKLOG` row of `tests/__init__.py` names.

Where a property of the tree decides membership it is stated below; where none
does, the entry is the whole of it. A tree owing a sentinel it does not carry is
a debt with an issue behind it, and its entry gains the tree when the workflow
and the badge land together.

- **`mutation` follows a suite over code the tree ships.** A coverage floor at
  100 says every line and branch ran, not that an assertion would notice it
  being wrong, so the sentinel is worth most where the floor is highest, and
  publishing is not the key. `bbt` holds no suite over its notebooks and scripts
  and gains the sentinel the day it gains one (btclib-org/.github#301).
  `.github`'s suite is over the other repositories, so a mutant here would land
  in the measuring instrument.
- **`scorecard` asks a repository that is public and is not a fork**, and that
  is the bar rather than the key: the entry above says whether a tree clearing
  it runs the sentinel. The OpenSSF Scorecard reads only public repositories,
  and `ossf/scorecard-action`'s README does not support a fork, which
  `gh api repos/<org>/<repo> --jq .fork` answers. The badge is what the row is
  kept for. **A check scoring below its maximum is an issue against what it
  found**, never a sentence in section 14 explaining the score.

    The badge and the published score want `publish_results: true`, and the job
    wants `id-token: write` for the transparency-log entry,
    `security-events: write` to file code scanning alerts, and `actions: read`
    with `contents: read`.

    **Its triggers are the action's and not this section's**, the one exception
    to *`workflow_dispatch` on everything* above: that README supports `push`
    and `schedule` on the default branch and calls `workflow_dispatch`
    experimental.

    **The trees this entry names owe a registration at bestpractices.dev**, and
    section 2's row carries its badge: `CII-Best-Practices` is the check reading
    it. Registering is an account action, carried by btclib-org/.github#350. The
    questionnaire restates how a vulnerability is reported, how a release is cut
    and what gates a change, so a change to any of them owes a pass over it.
- **`fuzz` follows a tree that parses whatever a stranger sends**: nobody stands
  between the parser and an adversary choosing the bytes. `btclib` and
  `btclib-secp256k1` read transactions, scripts, PSBTs, signatures and extended
  keys off the wire, and `btclib-node` speaks the peer-to-peer protocol;
  `bitcoin-core-rpc` reads an instance its own operator runs, which the property
  does not reach. `btclib-secp256k1`'s targets reach the vendored C on purpose:
  what they exercise is this tree's own length checks in front of it
  (btclib-org/.github#342). Section 7's *Property tests* has how a fuzzer and
  the property layer stand to each other. A crash the sentinel finds is an issue
  against the parser, never a suppression, and its regression is an ordinary
  test naming the input and what the parser now does with it; it does not go in
  `fuzz/corpus/`, a *seed* corpus that `btclib`'s `tests/fuzz_corpus_test.py`
  requires to stay valid input. What fills the workflow is the tree's — which
  entry points are targets and which harness runs them, `atheris` under
  ClusterFuzzLite in Actions or under OSS-Fuzz. What is fixed here is the name
  the calendar keys on and which trees owe one.
- **`deps-oldest` follows a tree that builds a distribution.** Its
  `requires-python` and its dependency specifiers are a claim made to whoever
  installs it; a tree that installs nothing makes none, so `bbt` and this
  repository are outside the row whatever their `pyproject.toml` declares. It is
  the set `deps-latest` names, the two asking one question in opposite
  directions.
- **`sdist-rebuild` follows a tree that publishes an attestation.** A released
  tag either rebuilds to the sdist that was signed or the attestation vouches
  for bytes no rebuild answers for: section 12 states that property, and each
  tree's `RELEASING.md` names the steps a rebuild replays. The sentinel compares
  against the attestation's digests, `gh attestation verify` over the rebuilt
  file, not against PyPI's, which say what the index holds rather than what was
  signed. It runs weekly rather than in the release, where it would compare a
  build with itself. The compiled wheel is outside the property for the reason
  section 12 gives, and a rebuild that disagrees is an issue against the tree it
  ran in.
- **`wheel-reproducibility` follows a tree that ships a compiled wheel**, asking
  how far section 12's exemption of compiled wheels from `sdist-rebuild` stands.
  It builds one interpreter's wheel twice on one image and diffs the archives
  member by member, then diffs the wheels two images of one platform built, the
  second with a different toolchain. btclib-org/btclib-secp256k1#524 is where
  the property is being reached for; a platform whose wheels disagree is an
  issue against what the run names. btclib-org/btclib-secp256k1#538 carries the
  port until that tree's `cron:` is the instant above and its badge is in the
  row.
- **`homepage` follows a tree serving a page generated from another tree's
  file.** `btclib-org.github.io`'s `index.md` is derived from
  `profile/README.md` here, and the sentinel asks whether the served copy still
  says what that file says. The drift arrives from a landing here, so no pull
  request there is the occasion to ask, and asking from this suite would redden
  `main` here for a drift another repository owns.
- **`zkp-oracle` follows a tree with an implementation of its own to compare.**
  The tree it asks holds the side written in Python; `btclib-secp256k1` is the
  other side, built from its sdist, not a tree the row reaches.
- **A platform row leaves a tree's entry where a gate cell asks the whole of
  what that tree's sentinel asked.** That cell gates on the suite and not on the
  coverage floor, and its place before a review is the trade *An interpreter
  axis is a gate cell rather than a sentinel row* names. Where that trade does
  not hold, or the cell is narrower than the sentinel's matrix, the sentinel
  keeps its whole matrix on the calendar and the entry keeps the tree.
  `btclib-node` is out of the `os-windows` entry on this ground, its `test.yml`
  gating a `windows-latest` cell at the interpreter `.python-version` pins.

### The aggregate job, and the required check

A workflow whose answer gates a pull request ends in a job that `needs` every
other job in it whose own result is a claim about the pull request, and is named
with its workflow — `test: every job passed` — because a check context is keyed
by name alone and two workflows with a job of the same name produce one
ambiguous check.

**This subsection is about every aggregate, a required check being what a branch
rule makes of one**: a red job below is a blocked merge only where a rule holds
its context.

**Which of two shapes the aggregate reads is decided by whether something in the
tree actually calls the workflow, not by whether it merely declares
`workflow_call:`.** A workflow nothing calls reads its run's job listing; one a
`release.yml` or another workflow `uses:` reads `needs`. `btclib-benchmarks`'s
`test.yml` declares `workflow_call:` and nothing calls it, so it reads the
listing.

**A job engineered to conclude successfully whatever it finds makes no such
claim, and stays out of `needs` for exactly as long as that holds** — a step
tolerated with `continue-on-error: true` and reported by a step of its own.
`btclib-node`'s `free-threaded` job, which reports rather than gates, is out of
`test-passed`'s `needs:` while the wheel its sync step depends on does not
publish (btclib-org/btclib-node#746).

**A matrix is not what asks for one.** A branch rule can name only a context a
pull request produces, so a workflow on `push` and `schedule` alone cannot be
required; where it is to gate, the trigger and the aggregate arrive in one pull
request and the rule follows.

- **Never name a matrix cell in the branch rule.** The rule lives outside the
  repository, so a context that stops being produced blocks every merge with
  nothing in the tree to explain why.
- **The job carries an `if:` of its own: a job with `needs` and no `if:` is
  skipped when one of those needs fails**, and `skipped` is silence about the
  failure it exists to report. The condition is `!cancelled()`, beside the draft
  and closed conditions; `always()` would fail the job on a run its concurrency
  group superseded.
- **What the aggregate of a workflow that is only ever a run's own reads is that
  run's job listing, asked of the API rather than of `needs`** —
  `repos/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}/jobs`, each finished
  row's `conclusion`, in a step failing on anything but `success` and `skipped`.
  **Both names, whatever the workflow's own jobs can report today**: a `changes`
  job or narrower `if:` added later re-opens `skipped`. The job elevates to
  `actions: read` and hands `github.token` to the call.
- **The listing is asked for in full** — `gh api --paginate`, with
  `per_page=100` — since a matrix makes a run's job count unbounded and rows
  past a page go missing silently.
- **A matrix reports one result to `needs` and one row per cell to the
  listing**, and **a boolean `if:` over `needs` decides nothing when it is
  false**, the step being skipped and a skipped step leaving its job green over
  a red matrix (btclib-org/btclib#1001).
- **A shell allowlist over `join(needs.*.result, ' ')` is vacuous on an empty
  join** (btclib-org/btclib#1454): `for` gets no words and exits 0. A `case`
  ahead of the loop refuses it, over the results comma-joined:
  `case ",$results," in *,,*)` catches an empty field anywhere, `join` writing
  one separator between every pair.
- **What answers that vacuity where the aggregate reads its own run's job
  listing is a count of the run's unfinished jobs, and the count is the
  aggregate itself alone** — a count, because a name is what a rename moves. The
  aggregate's own row has a `null` conclusion while the step reads, and this
  count judges it.
- **The listing's unit is the run and not the workflow, which is why the count
  above is the own-run shape's alone.** Under `workflow_call` the caller's jobs
  and the called workflow's are one run, and the publishing jobs are unfinished
  because they wait on this one.
- **A workflow something in the tree actually calls keeps to `needs` throughout,
  on a direct run exactly as on a reused one**, reading the `case` above before
  the allowlist: `btclib`'s `test.yml` is `release.yml`'s call. The price is the
  btclib-org/btclib#1001 shape, which `needs` cannot see.
- **What gates the release is the caller's own `needs:` on the calling job**: a
  `workflow_call` job's result already reflects every job the called workflow
  ran.
- **One shape for all is refused in both directions, for two different
  reasons.** The listing under `workflow_call` answers for the caller's
  unfinished jobs; `needs` on a workflow nothing calls gives up the listing's
  protection against the `#1001` shape for nothing.
- `skipped` is legitimate on purpose: when the run was superseded by its
  concurrency group, and when a `changes` job decided the diff touches nothing
  those jobs read. A filter naming only `success` fails the job on every run a
  `changes` job empties.
- **A `changes` job** is the cheapest job in the workflow and decides whether
  the rest runs. It answers `true` on every trigger that has no base to diff
  against, and the files it counts as prose are narrower than they look: the
  README is the package's long description, the docs are read by tests, and the
  history files are parsed by the suite.
- Where a single job is what gates, **that job is the context**.
- **Renaming a required check cannot be done in a pull request**: the branch
  stops producing the old name while the rule still waits for it. The rule moves
  first, against the branch, and the pull request follows.

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
than wording them for itself: `README.md` written into the second limb
names a sibling's own file.

The claim rejected is `this file is the whole of them`, which no command
checks: telling the fields a repository decides from the rest of the
endpoint's answer is a reading, where the perimeter above is one this
file fixes and a copy can be held to.

**The section headed `## What this file passes over` is where a copy
says what falls outside that scope.**

**A copy does not claim that nothing it records has another form in the
tree.** The topics are section 3's `keywords`, a releasing tree's
`.homepage` is the `[project.urls]` field of that name, and a Pages
custom domain has the root `CNAME` carrying the same value — so where a
tree holds one of those, the record is a second copy read back for
comparison, and that copy's own section on it says so.

**`has_wiki` and `has_projects` are off, and a copy reads both back**,
this sentence being what puts them inside the perimeter: an unused wiki
is a second place to look for what the tracker records, and the projects
board a per-user view of the same issues.

**`has_issues` is not with them**, and a copy records it: `CONTRIBUTING.md`
and section 16's `ISSUE_TEMPLATE/` both rest on each repository's tracker.

**Section 10's `scorecard` bar splits on that same test.** The sentinel
reads a public repository only, so a copy reads `.visibility` back.
Nothing sets `.fork`: a repository arrives as a fork or it does not, so
no limb reaches it and section 10 states that half of the bar.

**Whether GitHub Pages is configured is inside the perimeter too, on
every tree and not only the one that serves a site from its own root.**
`gh api repos/<org>/<repo>/pages` answers every repository, and a
recorded `404` is what makes a later silent flip to `on` visible. The
default branch is inside by the general rule, section 16's checklist
setting it; a copy reads both back with the commands that answer them.

**A recorded answer is documentation, and a reader is its check.**
What `tests/` gates is the live endpoint against the rule this file
states — the merge method, the signatures, the token, the wiki and the
projects board, the topics, the homepage, private vulnerability
reporting — and never a copy's prose against the endpoint. The rejected
alternative reads each quoted answer back, and its parser of prose cost
more issues than the drift it caught (btclib-org/.github#1017).

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
the bots' included.

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
someone else's approval. A direct push to `main` is refused for everyone;
`always` would permit one, for nothing a valid signature does not
already give.

**What it excuses is the rule, not the approval count**, and
`dismiss_stale_reviews_on_push` is a parameter of that same rule. So the
dismissal binds every merge except the ones this organization makes, and
the `sha` on `CONTRIBUTING.md`'s merge call is what refuses a moved head.

Two settings hold the door, not one: the classic review requirement is
cleared for the maintainer by `enforce_admins: false` *plus* admin, and
turning `enforce_admins` on would deadlock every solo merge. That setting
clears the whole of classic protection for that account, `strict`
included, so being up to date with `main` is a rebase somebody runs and
not a rule the forge holds: a branch merged behind `main` lands a tree
nothing has run.

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
merge settings. Off, every landing waits on somebody pressing *Squash
and merge* when the last check goes green, and nothing turns red.

`squash_merge_commit_title` and `squash_merge_commit_message` are set so
that a single-commit branch lands under its own subject and a longer one
under the pull request's title, with the branch's commit messages as the
body — never the pull request's description. `delete_branch_on_merge`
is on.

**A subject is one physical line.** `%s` joins a wrapped subject up to
the first blank line where the squash does not, so a wrapped subject
lands truncated at its first line, the citation it carried left in the
body, and nothing turns red. The first line of `%B` is the read that
shows the wrap:

```shell
git show -s --format=%B <sha> | head -1
```

### What a pull request says it is

**A pull request that closes an issue names it in its title, in
parentheses**: `Say when github-release runs instead of relying on no if
(closes #1142)`. Which of the title and the branch's own commit subject
lands is *Merge method*'s rule, so the parentheses belong on whichever
one that is. Either way the number reaches `git log` and stays reachable
from a checkout with no forge in front of it.

**A pull request that advances an issue it does not close names it the
same way, `(issue #N)`**: without it the subject carries no number at
all. The token holds one meaning wherever the standard writes it —
section 9's `CHANGELOG.md` citation and this one both name an issue the
change does not close — and which of the two a change carries is decided
by what is true of it. Reserving `(issue #N)` for `CHANGELOG.md` alone
is rejected, since a branch answering half an issue would then land with
nothing in `git log` pointing at what it answered.

A pull request that neither closes nor advances an issue carries no
parentheses. Nothing already landed is rewritten, a title and a landed
commit subject included: section 9's *Nothing already written is
rewritten* is this same rule, read from the title's side of it.

**A title citing several issues joins them for the reader, and the
parser binds the verb to the first**: `(closes #319, #388)` closes only
the first on its own, so a subject that must close alone repeats the
verb, `(closes #319) (closes #388)`. The description carries every
keyword either way.

**The title is not the closing mechanism.** `Closes #N` in the
*description* is what GitHub acts on, and both are wanted: the
description closes the issue, the title records which one. The bare `#N`
form is repository-local; the qualified `owner/repo#N` form closes
across repositories exactly as `#N` closes within one.

**GitHub does not parse negation**, so a sentence declaring that a
keyword closes nothing is the sentence most likely to hold one. A
mention that must not close names the issue with no verb immediately in
front of it — `tracking issue: owner/repo#N`, never
`<verb> owner/repo#N` — and a cross-repository task keeps its tracking
issue open this way until every one of its pull requests has landed, and
somebody closes it by hand.

**Adjacency is the test, and two parsers read a keyword.** A verb the
number does not immediately follow does not fire. One parser reads the
description and answers `closingIssuesReferences`, and it needs the
keyword and the number on one physical line; the other closes on a push,
reads the landed message, and crosses a newline. An issue's timeline
says which fired — a `closed` event carries the commit's sha where the
push closed it and null where the description did, so a null says
nothing against the push:

```shell
gh api repos/<org>/<repo>/issues/<n>/timeline --paginate \
  --jq '.[] | select(.commit_id != null) | {event, commit_id}'
```

**So the keyword and its reference share a physical line, and a block of
several is written one keyword per line**, which no wrapper can split
and no formatter is let reflow. What catches a loss is counting the
registrations against the number intended. `<n>` sits last for the
reason section 9 gives:

```shell
gh pr view --json closingIssuesReferences \
  --jq '.closingIssuesReferences | length' <n>
```

The failure is stable, so asking twice answers only the indexing lag; a
zero that survives repeated reads is a parse that never ran, and an edit
that resubmits the body re-triggers it.

**A manual link carries no form to get right and no keyword to omit.**
Made in the Development panel, it closes its issue on merge regardless
of repository and appears in no diff, commit message or description. So
**what a pull request closes is read before it is merged**, from the one
place that answers. The variables follow the query, which puts `<n>`
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
cross-repository one is the finding this rule exists for. A title or an
entry carrying `closes` for a number missing from that answer, or `issue`
for one present in it, is wrong on the parser's own evidence, and a
correct title is not evidence for the citations it travels with.

**That read describes the pull request, not what a squash will land**:
the squash message is composed at merge time, after any pre-merge read.
So the read is taken twice — `closingIssuesReferences` before the merge,
and the timeline read above after it, for every reference the landed
message names. A `closed` event naming the just-landed sha for a
reference the first read did not name is the finding. Taking the title
verbatim as the squash subject is declined as a rule about how a person
presses the button, where the second read runs however it was pressed.

**Negation is checked against the branch's own commit subjects and
bodies**, since the forge's two parsers can read the same words
differently. Before the pull request is opened:

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

Every hit outside the title's own `(closes #N)` parentheses is the
finding, and a number the title carries that the scan does not find is
a keyword the branch's own words never state. The separator is `\s`,
crossing a newline, because the landed message meets the push parser.

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
and not an unfinished review; `REVIEWING.md` states that distinction.

**The ack of record is posted as a review of type COMMENT**, whichever
of the three it carries — `gh pr review --comment` — and never as a
forge approval or a forge request for changes:

```shell
gh api orgs/<org>/actions/permissions/workflow \
  --jq .can_approve_pull_request_reviews
gh api repos/<org>/<repo>/pulls/<n>/reviews --jq '.[].user.login'
```

The first answers `false`, closing the route a `GITHUB_TOKEN` would
take. The second answers `claude[bot]`, a GitHub App's identity, which
that setting does not govern: what forbids `--approve` is the prompt,
`Bash(gh pr:*)` in `claude_args` permitting it otherwise.
`--request-changes` goes unused, so that the body's last line, which the
job's verification step reads, is the one place the verdict lives.

**What the forge then holds is a record of the review and not an
approval**, and it does not buy the OpenSSF Scorecard's `Code-Review`
check, which does not count a review by a bot as code review.

**btclib-org/.github#341 holds the removal of the ruleset's
`bypass_actors`**, which would put a person's approval on the critical
path of every merge.

**The ack of record is `claude-review.yml`'s**, and an author's own is
not one: a comment from the account that opened the pull request says
its gates were run, and is not a reading. What triggers the workflow is
section 10's *`pull_request` types* — the exemption there is for a group
that does not cancel in progress, and this group cancels — and a comment
naming `@claude`, which is how a head that moved after the review gets a
fresh one. A closed run posts no review, the review job declining that
action: what the type buys is the group, where the run supersedes a
review nobody is going to read.

**The workflow is present and neither the review nor a `@claude` answer
runs.** `reusable-claude-review.yml`'s two jobs each carry
`if: vars.CLAUDE_REVIEW_ENABLED == 'true'`, an organization variable, and
every caller reaches both:

```shell
gh api orgs/<org>/actions/variables --jq '.variables[].name'
```

It names nothing, and an undefined `vars.X` is the empty string, so the
absence is the off state and creating it with that value is the whole
switch; the file is kept current meanwhile. A tree whose gate is off has
no ack of record, and a landing there reads a person's reading. The
switch is the organization's so that no tree can be forgotten.

**A pull request that adds or edits `claude-review.yml` gets no ack**
until the change is on `main`, for the reason the workflow's own header
gives. It lands on its gates and a description saying so, and carries
that change alone; one touching another workflow is reviewed as usual.

**A green check is an ack of the head, and nothing weaker.** The job's
last step reads back what was posted: a refusal, a verdict never
written, and an ack naming a sha the branch has moved past are a red row
each. What the review found is the comment's to say, whatever the
colour.

It is **not a required check**, its own header saying why: it is what a
person landing the pull request reads before pressing.

`REVIEWING.md` is the standard a review measures a diff against.

**A review pass runs locally against the branch before it is pushed**:
`.claude/commands/review.md` with no argument reads the diff against
`origin/main` and `REVIEWING.md`, posts nothing and is not the ack of
record, so that the forge's round is the last rather than the first. It
reaches what the gates do not — a count nothing re-derives, a bare
cross-repository reference, a paragraph a change elsewhere falsified. A
pass run from the session that wrote the diff re-performs the author's
reading.

**A gate already run on this sha is relied on, and the run is named**;
where none is on the record the review runs the gates, a failing one
being the strongest finding available. A rebase voids the reliance.

**What a diff decides with is run, not read.** A regex, a hook pattern,
a grep, a script or a query the diff adds is executed by the review,
against the shapes its prose claims and the shapes the tree holds, and
the finding quotes what it printed; a claim the prose makes about the
tree is checked the same way. Where it cannot be run, the summary says
so in those words: a hand trace can carry a finding but not an ack.

**What a force-push costs is the review attached to the sha it
replaces**, a bot's included, and whether there is one is read before the
push:

```shell
gh pr list --repo <org>/<repo> --state open --head <branch> --json number
gh api repos/<org>/<repo>/pulls/<n>/reviews \
  --jq '.[] | "\(.user.login) \(.state) \(.commit_id[0:8])"'
```

`pulls/<n>/comments` counts inline comments only, so it reads zero for a
review carrying none. An open pull request may already carry one, a bot
reviewing within seconds of the open, so the read decides rather than the
timing: an amend and a new commit alike leave a review pinned to the
replaced sha, and a rebase carrying no new work stays right.

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

The first answers with the name or nothing, `--silent` for the reason
section 15's publishing sweep gives. The token is an
**organization** secret at `visibility=all`, so a repository adopting
the workflow configures nothing for it. It is in both stores for the
reason *Dependabot and pre-commit.ci* gives below. Why the job has the
shape it has is in the workflow's own header.

**The prompt is `reusable-claude-review.yml`'s, and a port adapts no
part of it.** What a port adapts is the `uses:` reference — a path where
the callee is the calling tree's own file, `@main` from anywhere else —
the inputs the call passes, an `extra-prompt` paragraph about what the
receiving tree ships and the `extra-allowed-tools` its own commands
need, and the header saying why that tree runs a review at all.

**A citation of this standard names it rather than a `README.md`**,
which everywhere else is section 2's file about that repository, in one
of these shapes:

- `section 11 of the organization's standard`, where the rule cited is in
  this section and no one subsection of it holds the rule, and wherever
  the sentence is the one that names the standard;
- `section 11's *Review*`, or whichever subsection does hold the rule
  cited;
- `the organization's standard`, with no section number, where the rule
  cited is not in this section.

**What chooses the shape is what holds the rule, never where the
sentence sits**: the two secret stores a Dependabot-initiated run reads
are stated in this section's own prose and in *Dependabot and
pre-commit.ci*, so their citation names no subsection. A file citing it
names the standard in full somewhere, `section 11` alone not saying
which document it is a section of. A finding about prose cites section 9
and one about a rule stated without its reason cites *How to use this
file*, not section 11.

**A review reads more than the sha.** The prompt has the reviewer read
the title and description again before a finding about either, for the
reason it gives; with no `edited` trigger, a later correction clears
such a finding only through a further push or a `close`/`reopen`.

### Tokens, publishing, scanning

- **The default `GITHUB_TOKEN` is read-only repository-wide**; a job
  needing more declares it. This is a *setting*, inherited from an
  organization default that ships as `write`, and the workflow-level
  `permissions:` block is the braces and not the belt:

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
    default for good — the endpoint takes neither `null` nor `inherit`,
    and none reports which repositories override. So a repository that
    pins its own is recorded in its `REPOSITORY.md`, and whoever moves
    the organization default moves those with it.
- **A caller's `permissions:` block bounds the workflow it calls rather
  than standing in for what that workflow declares.** A called job with
  no block of its own gets what the called workflow declares at its top
  level, not what the caller grants beyond it; the
  `GITHUB_TOKEN Permissions` group each job's log opens with says so:

    ```shell
    gh api --allow-escape-sequences repos/<org>/<repo>/actions/jobs/<id>/logs
    ```

    **The bound refuses rather than trims.** A scope a called job
    declares that the caller's list leaves off fails the run before any
    job starts, as a `startup_failure`. So a caller's list names the
    scopes the called jobs declare, and naming the called workflow's
    top-level scopes too keeps an unmeasured case out of a release
    (btclib-org/.github#912).
- **Secret scanning, its push protection and Dependabot security updates
  are on.** All three are free on a public repository and off by
  default; push protection is the one that refuses the push rather than
  reporting it afterwards.
- **Publishing waits for an approval**: `pypi` and `testpypi` are
  environments requiring a review, and `pypi` is restricted to `v*` tags.
  Trusted publishing via OIDC, so no long-lived token exists.
- **A repository declares `pypi` and `testpypi` where it publishes, and
  no environment besides.** Each is named by a job of the release
  workflow and carries the review above; an environment nothing names
  and nothing gates is found at the endpoint, not recorded:

    ```shell
    gh api repos/<org>/<repo>/environments \
      --jq '.environments[] | "\(.name) \(.protection_rules | length)"'
    ```

    **`github-pages` is GitHub's**, created by enabling Pages and
    protected by GitHub, so it is outside the rule above and outside
    `REPOSITORY.md`.
- **Code scanning**: the analysis runs from a workflow, and GitHub's
  default setup is *off* — the two cannot both be on, and while the
  setting is on the upload is refused. Turning it off has an order that
  never leaves `main` unmergeable: drop the context from the rule,
  disable the setting, re-run, merge.
- **Secret scanning's non-provider patterns and validity checks are
  plan-gated**, and the API answers a `PATCH` with 200 while leaving them
  disabled. The `detect-secrets` hook is the compensating control.

### Dependabot and pre-commit.ci

`github-actions` everywhere, every tree having workflows for it to read,
and three more where the tree has what they watch: `uv` where a
`uv.lock` exists, `bundler` where a site Gemfile does, `gitsubmodule`
where a submodule does — conditional by section 2's rule for a subject
the tree does not hold. Pre-commit hook revisions have no Dependabot
ecosystem, so pre-commit.ci updates them weekly, except a hook whose
`repo:` is `local`: what moves that version is where the hook pins it,
the `uv` ecosystem above where that is `uv.lock`, a hand edit where it
is `additional_dependencies`.

`gitsubmodule` follows upstream's *default branch*, so its pull request
says that upstream moved and is not the bump: a release pins the tagged
commit by hand. The local hook refuses an unpinned or moved pointer and
says nothing about upstream.

Each ecosystem groups its updates into one pull request, since every pull
request runs the whole matrix — the one exemption is `btclib-org.github.io`'s
`bundler` block, a single gem having nothing to group with. The `uv`
ecosystem's group is named `dev-tooling`. Weekly with a seven-day cooldown: a
compromised release is usually yanked within days. None declares a
`target-branch`: one naming a missing branch fails nowhere and proposes
nothing.

**A Dependabot pull request reads a different secret store.** A
`pull_request` run whose actor is `dependabot[bot]` gets the Dependabot
secrets rather than the Actions secrets, so a secret a workflow needs
there is registered in both, under the same name; failing loudly on an
empty one is what turns the omission into a red check. A credential too
sensitive to hold there at all -- an organization-wide App private key
-- is the one case this does not fit: `alignment.yml` declines the run
for that actor instead of registering a copy to fail loudly against,
its own header carrying the reason.

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
each new tag. The project's public API answers without a token:

```shell
p=https://app.readthedocs.org/api/v3/projects/<slug>
curl -s "$p/"
curl -s "$p/versions/?active=true"
```

The first answers `default_branch` and the `repository.url` the slug
serves; the second, `latest`, `stable` and the tags the rule activated.

**What connects a repository to Read the Docs is the organization-wide
`read-the-docs-community` GitHub App, not a per-repository webhook**, so
a repository records the installation and an empty hook list. Both
names stand in a block of their own, for the reason section 9 gives:

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

`repository_selection: all` makes one installation the connection for
every repository. A hook the second command finds is stale and is
deleted rather than repaired, the App doing all it was for and its
masked secret leaving nothing read back to say whether it still works.

The **slug** is what serves the site, and it is not the project's name:
renaming the project leaves the slug, and renaming the slug makes the old
one stop answering rather than redirect. Get that URL right before a
release, because `pyproject.toml`'s `documentation` reaches the metadata
of every version already on the index, which no later release corrects.

## 12. Releasing

- **Calendar versioning, `YYYY.M.D`.** Between releases the declared version is
  `YYYY.M`, month only, so a checkout of `main` reports itself as work in
  progress. A fourth component exists only for a release that shipped broken and
  cannot be reuploaded. No release candidates: there is no pre-release, only a
  version not yet tagged, and a check refuses anything that is not digits and
  dots. The one exemption is a wrapper whose version names the upstream it
  wraps, its own `README.md` stating the scheme and a fourth component there
  meaning a rewrap: `btclib-secp256k1` releases `M.N.P` for the libsecp256k1
  `vM.N.P` inside it, so that no caller reads a changelog to answer *which
  upstream is this*.
- **A rehearsal on TestPyPI** uses `.dev<run number>`, patched in by the
  workflow rather than typed, so it is unique per run and sorts below the
  release it rehearses.
- **The tag is signed**, is checked to be an ancestor of `main`, and is checked
  to say what `pyproject.toml` says.
- **The release pull request closes the cycle's sections and opens the next.**
  It retitles the work-in-progress section of `CHANGELOG.md` and of
  `RELEASE_NOTES.md` to the version being tagged and opens an empty
  work-in-progress section above them, in the same pull request, so the topmost
  `##` heading of either file on the default branch is a work-in-progress
  heading at every commit. The next generic version does not travel with the
  retitle: the tag says what `pyproject.toml` says, so the bump stays in the
  pull request that sets it. A release publishes the section just retitled,
  whose heading is the tag's own, and not the empty one above it.
- **A published sdist reproduces from its tag.** The attestation every publisher
  attaches vouches for bytes, so a release rebuilt from the commit its tag names
  — by running what the release ran — gives those bytes back. What the release
  ran is `RELEASING.md`'s to name: the steps between the tag and the archive,
  with the reason beside each. Every publisher runs a normalization step after
  the build, replacing the member metadata the backend wrote, the digest the
  attestation signs being the pipeline's output.
  `SOURCE_DATE_EPOCH` is exported from the tagged commit for what reads it — the
  normalizer, and the bill of materials below. `sdist-rebuild.yml` re-derives
  the property weekly, rebuilding the latest release's sdist from its tag and
  running `gh attestation verify` over it; section 10's record names the trees
  that carry it.
- **The compiled wheels are outside that property**, and are named rather than
  passed over, the index attesting every one beside the sdist under PEP 740: a
  verifier who rebuilds one and gets other bytes would otherwise not know
  whether that is a defect. What is measured is narrower than what
  `btclib-secp256k1` publishes: `wheel-reproducibility.yml` builds one
  interpreter's wheel twice in one image and diffs the archives, and whether a
  wheel of another ABI tag reproduces is measured on no trigger, the published
  `py3-none-*` ones being btclib-org/btclib-secp256k1#540. Pinning the
  environment so they reproduce across two images is a digest on the container
  the Linux build compiles inside, btclib-org/btclib-secp256k1#524; on macOS and
  Windows the toolchain is chosen from what a runner image already carries, so
  the same pin states nothing to a verifier who was never on the machine and is
  declined — btclib-org/btclib-secp256k1#554.
- **A bill of materials is published beside the distribution files**, by every
  publisher, and the attestation signs it with them: one answer rather than an
  answer and its exemptions. Its timestamp is `SOURCE_DATE_EPOCH` and its serial
  number derives from the distribution files' digests, so a rebuild of a
  released tag writes the same document and the attestation verifies it as it
  does the archives. An exemption for a wrapper does not follow from
  `Requires-Dist` naming only its `cffi`: the vendored library is a component
  too, at the commit its submodule pins.
- **What is published is inspected first** — `twine check --strict`,
  `check-wheel-contents` and `pyroma --min 10` on the files the release will
  publish; then the wheel is installed from an empty directory and smoke-tested,
  so the import finds the wheel and not the source tree. Those read a
  distribution's *metadata*, and an unconfigured `check-wheel-contents` reads
  the wheel's own `RECORD`: none of them asks what the tree the wheel was built
  from has, so a `py.typed` dropped by a `package-data` typo passes all of them.
- **So the wheel is diffed against the package tree it claims to carry**, in
  both directions, and where that tree is the whole of the wheel's library the
  diff is `[tool.check-wheel-contents]` naming it, a line of configuration
  rather than a check to maintain. Where the wheel is *not* one package tree,
  that flag has no wording for it, and the repository owes a script saying what
  the flag cannot, its allowlist stated in prose and compared against the
  script's constants by a test, in both directions, so neither is free to drift.
  Another check implying the same diff does not stand in for the flag where the
  flag applies.
- **The sdist is diffed against what git tracks**, in both directions, by
  `check-sdist` in the gate of every repository that builds one. It builds the
  archive and compares it against the index, and its exit code says which way
  the two differ: a tracked file the archive dropped, or a member git does not
  track. Neither direction is loud otherwise, so the check is not conditional on
  the inclusion being an include list, and what it costs an exclude-list tree is
  a `[tool.check-sdist]` table naming the tracked files its archive leaves out
  on purpose. Which table declares the inclusion is the backend's — `uv_build`
  reads `[tool.uv.build-backend]`, hatchling `[tool.hatch.build.targets.sdist]`
  — so `check-sdist` keys a plugin on `[build-system]` and reads that backend's
  own exclusions, leaving `[tool.check-sdist]` holding only what no pattern of
  the backend's accounts for. Past that, an allowlist for the sdist is the
  escalation a repository takes when its archive carries more than the package.
- **A hook that builds the project builds it with the backend `[build-system]`
  admits**, and only one of the two hooks builds through PEP 517 at all. Both
  build without isolation:
  `check-sdist` runs on pre-commit.ci, which cannot create the isolated
  environment, and `pyroma` runs from a group already holding the backend,
  where an isolated build would resolve `requires` from an index instead.

    `pyroma`'s non-isolated path never reads `requires`, so the backend is in
    the `check` group beside `pyroma` itself, at `[build-system]`'s own
    specifier, which keeps it importable.

    `check-sdist` drives `uv build`, which is not PEP 517 for this backend:
    given `build-backend = "uv_build"` it builds with the copy bundled in the
    running uv, so naming the backend there decides nothing. The hook takes
    `args: [--inject-junk, --installer=pip]` instead, which builds through
    `build --no-isolation`: that reads the environment, so the backend
    `additional_dependencies` names is the one that packs the archive, and it
    refuses an environment `[build-system]`'s `requires` does not admit.
    `--inject-junk` is repeated because `args:` replaces the manifest's list
    rather than adding to it.

    **That alone does not keep the two specifiers equal** — a `requires` widened
    past the hook's line still leaves that line satisfying it and green.
    `btclib-secp256k1`'s `hook_pins_test.py` asserts the hook's
    `additional_dependencies` and `[build-system]`'s `requires` name the same
    requirements (btclib-org/btclib-secp256k1#945); the hook's other trees carry
    no such test. Pinning `uv` on the hook instead leaves even that first half
    silent.
- **A release is checked against the last one for a break in the public
  surface**, by `griffe check` in the release path, comparing the tag being cut
  against the tag before it. Section 7's census answers *is this module's
  surface stated* and never *did this release take something the last one gave*,
  and `RELEASE_NOTES.md` is written by hand, so nothing else can tell that an
  entry is missing. `griffe check` walks the public API of two git references,
  names each break by the kind of break it is, and exits non-zero having found
  any. What it reports is either a `RELEASE_NOTES.md` entry or a reason for not
  being one, written where the release is being written.

    **The release path and not the merge gate.** Before 1.0 a package breaks its
    surface deliberately, so a gate comparing the branch against the last
    release ends every run in a human deciding which breaks are allowed. It
    becomes a gate the day btclib-org/btclib#651 settles a deprecation policy,
    the question then being *did the surface change without the release of
    warning the policy owes*, which a command can answer on its own; so the
    invocation takes a second reference pair rather than being replaced by
    one.

- **A job named in `needs:` that is not a gate takes `always()` in the
  dependent's own guard**, beside an explicit `needs.<job>.result == 'success'`
  for each listed job that is one. The public-surface check above is such a
  job, and `needs:` alone refuses to start a job whose listed dependency failed
  or was skipped. Listing it orders the reading before the upload, and
  the guard is what says the reading's result decides nothing. `always()` here
  and not section 10's `!cancelled()`, a release workflow producing no required
  check for a superseded run to turn red.
- **The widening does not propagate, so each dependent states it for itself.** A
  bare `needs:` reads back through the listed job's own `needs:` chain, so a job
  two hops from the non-gating one is skipped although the dependency it names
  succeeded. Putting `always()` on the non-gating job itself moves nothing, a
  job that ran and failed stopping a dependent exactly as a skipped one does;
  dropping it from `needs:` costs the ordering.
- **A release run is audited job by job for `skipped`, not for red.** A failed
  job is loud; a skipped one carries no step, so a release whose post-publish
  check never ran reads as a release that finished. What answers is the run's
  own job listing, its run id in a block of its own for the reason section 9's
  bullet gives:

    ```shell
    run=<id>
    ```

    ```shell
    gh api --paginate \
      "repos/{owner}/{repo}/actions/runs/${run:?}/jobs?per_page=100" \
      --jq '.jobs[] | [.conclusion, (.steps|length), .name] | @tsv'
    ```

    read against the jobs the release was expected to hold.
- **The smoke test runs again in the release job, without constraints**, after
  the upload rather than before: installing a dependency executes its code, and
  a compromised one must not reach a `dist/` still to be handed on.
- **A scheduled workflow installs from the index** and asks whether the
  published artifact *works*, not whether it installs — an import runs
  `__init__.py` alone, where a data file missing from the wheel is opened only
  at the first call that needs it.
- **That workflow is where the post-publish check lives, called by the release
  as a job of its own, and never a step appended to a publish job.** A publish
  job downloads the distribution files and hands them to
  `pypa/gh-action-pypi-publish`, so nothing in it provisions a toolchain: a step
  appended there fails on the command's name or on the interpreter's version,
  and neither failure names the runner as its cause. The reusable workflow
  provisions its own toolchain, so nobody placing the check there has to know
  any of this.
- **Placement also decides whether the failure is legible**, both placements
  running after an upload neither can undo. A job that fails is a row of its own
  in the listing above, red beside a publish job that stayed green; a step that
  fails turns the publish job itself red, and every job guarded on that job's
  `success` skips with it — the attestation and the GitHub release among them —
  leaving a release published, unattested and unannounced behind one red job
  that names none of it.
- **The check reads the index for the version the tag names**, so a first
  release is no different from any other: the call passes the tag, the wait
  holds until the index serves that version, and it fails on its deadline rather
  than let the matrix install the version the tag replaces. What has nothing to
  read before a first release is the schedule, which passes no version, waits
  for nothing and installs whatever the index serves at the time. A rehearsal
  has no such job either: the check reads the release index.

## 13. Editor and agent configuration

`.vscode/settings.json` and `.vscode/extensions.json` are tracked and
hold no preference. Every recommended extension is a tool the lint gate
already runs, and the settings put the fixing ones on save: what the
editor fixes is what the hook would have fixed, so nothing reaches
`git commit` for the first time there. An extension with no hook behind
it is a second opinion nothing enforces, and the reflex installs that
would fight a hook are listed as `unwantedRecommendations`. Anything
machine-local belongs in the editor's own user settings.

**`mypy-type-checker.importStrategy` follows section 4's branch**, and getting
it wrong is silent both ways. With the local hook it is `fromEnvironment`: the
mypy the extension bundles is a different version from the locked one, and an
`enable_error_code` name it does not know is dropped with a warning no extension
surfaces. With the mirror it is `useBundled`, there being no project mypy to
point at — `fromEnvironment` against a `.venv` without one reports nothing at
all rather than failing.

The exception is a package that is a **compiled extension**, and it goes the
other way: the mirror's isolated environment has no built extension, so the
editor cannot use it whatever the hook does. It reads the project's instead,
which `uv sync` built the extension into — so `fromEnvironment` under the
mirror.

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
and the condition. A condition is one backticked pathspec and nothing
else, and says the tree tracks a file it names — a path, or a glob such
as `*.toml`, which a reader answers with `git ls-files` and
`tests/verbatim_test.py` of this repository reads off each tree by that
same call. A file this section keeps out of the list because its subject
is its own tree's is not compared and is owed all the same, so its own
paragraph says who owes a copy in these same spellings.

A clause's opening ends at a comma, a semicolon, a colon or a full stop, or at
the end of the clause, and the rest of its prose goes after it. So a clause
narrows by its condition and never by a qualifier written into `owed by every
repository`, which owes the copy of every tree: that test refuses such a
qualifier rather than reading past it. The rejected alternative enumerates the
continuations admitted after the phrase, which is a second list to keep in step
with this one.

A clause that test reads, it reads both ways: a tree short of a copy it is owed
is a finding rather than a tree the comparison passes over, and so is a copy in
a tree whose observable is absent, that copy being one the standard gives that
tree no clause for. Every condition this section writes is read that way,
`.taplo.toml`'s file type included, and a clause in neither spelling raises
rather than taking its tree out of both readings. The rejected alternative
leaves a condition naming a file type as prose, and what it costs is an
obligation nothing asks any tree about.

The paths are what that test compares:

- `.markdownlint.jsonc` — owed by every repository; no rule disabled.
  What it names is a style where markdownlint's default is "consistent",
  which asks each file to agree with itself and therefore lets two files
  disagree.
- `.yamllint.yaml` — owed by every repository; the default set, extended rather
  than listed, with `line-length` raised to 100 and two rules disabled, and
  `document-start` raised from the default's warning to an error because the
  hook runs no `--strict` and a warning exits 0. Extending is what makes it a
  rule set at all, yamllint enabling no rule a configuration does not name. The
  two disabled rules carry the reason beside them, `comments` because dependabot
  writes the spacing it objects to and `truthy` because the `on:` a workflow
  opens with is the spelling GitHub Actions requires.
- `.taplo.toml` — owed where `*.toml`; four-space indent, `reorder_keys`
  left false because the order of a table is an argument,
  `array_auto_collapse` false so that adding an entry is a one-line diff.
- `COPYRIGHT` — owed by every repository: the notice every source file opens
  with, three lines naming the holder and pointing at `LICENSE`, and the source
  the `notice-rgx` of section 5 is transcribed from. A repository file and not a
  distributed one, so it is not in `license-files`: `LICENSE` carries the holder
  for whoever has the archive.
- `LICENSE` — owed by every repository: MIT, the holder named and no year
  range. A range is a line nobody updates, and `COPYRIGHT` states the
  holder without one.
- `.claude/commands/review.md` — owed where `REVIEWING.md`: it is the
  invocation and not a second copy of the standard, and it stays a
  file of its own rather than folding into `CLAUDE.md`, which is read by
  every session including the one that wrote the diff.
- `.github/scripts/mutation_counts.py` — owed where
  `.github/workflows/mutation.yml`: that workflow is what runs it, and
  section 10's `mutation` entry is what decides which trees carry the
  workflow. It counts a Cosmic Ray session by outcome, so a tree the
  sentinel leaves out has no session for it to read.
- `.github/scripts/wait_for_pypi_release.py` — owed where
  `.github/workflows/pypi-install.yml`: that workflow is what runs it,
  and section 10's `pypi-install` entry is what decides which trees
  carry the workflow. `reusable-wait-for-index.yml`'s own
  `actions/checkout` declares `sparse-checkout: .github/scripts` and no
  `repository:`, so a called workflow resolves it against the caller
  and each tree runs its own copy.
- `.github/scripts/wait_for_readthedocs_build.py` — owed where
  `.github/workflows/release.yml`: its `documented` job is what runs it, and
  holding that workflow is the whole of the condition. The bullet above names a
  decider and this one cannot, section 2 reading a tier off `release.yml`'s
  presence — *measured rather than declared* — so that a tier cannot in turn
  decide it. `reusable-documented.yml`'s own `actions/checkout` declares the
  same `sparse-checkout` and no `repository:`, so each tree runs its own copy
  here too.

**Verbatim in part**, the file around it being the repository's own and so
nothing a comparison by path can do: the `ci:` block of
`.pre-commit-config.yaml`, the mypy strictness block, the ruff width and
complexity settings, the pytest strictness flags, and `fail_under = 100`. Of the
`ci:` block, `autofix_prs`, `autoupdate_commit_msg` and `autoupdate_schedule`
are the shared part, with the values section 4 gives; `skip:` is the
repository's own, because it names hooks of that file that pre-commit.ci cannot
run. `tests/verbatim_test.py` compares none of these, its subject being a path:
what holds a part equal across the copies is that each was written from this
file, and that a command of section 15 greps for it, which none does for the
`ci:` block.

**A part is held against this file, and not against the other copies.**
Section 4 states `check-changelog`'s keys, and `tests/hooks_test.py`
reads them off each gate, resolving the hook by its `id` so that where a
gate keeps the stanza is no drift in it. The rejected alternative
compares that stanza between the trees, which is green wherever the
copies agree and are wrong together — the state each tree's
btclib-org/.github#1138 port is the fix for. Any other part above gets
its check in that shape on the day it gets one: this file states the
value, and a test asks each tree for it.

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
- `CLAUDE.md` — owed by every repository, and compared byte for byte in each
  from `## The primary checkout is the maintainer's` to the next heading at the
  same level. The section is what every session reads before its first edit, and
  it states the same rule in every tree; the rest of the file is that
  repository's own. The rejected alternative compares the whole file, which
  would report drift in the part that is meant to differ.
- `.github/scripts/check_changelog.py` — owed by every repository, every tree
  carrying a `CHANGELOG.md` and every one of them `merge=union` in
  `.gitattributes`, and the same file in each up to the same heading. Section
  4's `check-changelog` hook is what runs it; under the heading is
  `_GRANDFATHERED_ENTRIES`, a fact about that repository's history rather than
  about the script every repository carries alike.

`tests/verbatim_test.py` compares what precedes that heading where a file
carries one, the whole file where it does not, and only the section a bullet
names where the bullet itself quotes one — each ending at a single newline, so
the marker is the declaration and the blank line a copy puts before it is a
spelling rather than content.

`AUTHORS.md` is owed by every repository and differs in two ways that are the
repository's own. It points at **that repository's** contributor graph: a single
shared pointer would leave the first person to contribute somewhere else
uncredited in silence. And a tree that vendors somebody else's work attributes
it here, which is what the file is for — `btclib-secp256k1` says that the
vendored libsecp256k1 is not its work, carries its own licence and its own
authors, and is only ever read from. It is named in prose and not as a bullet
deliberately: a file meant to differ per repository can never satisfy a byte
comparison.

`CODE_OF_CONDUCT.md` is out of the list for the opposite reason: there is one
copy of it, in this repository, and a comparison needs two. The organization
advertises a single policy because there is a single file, rather than because
every copy of it agrees with this one.

`claude-review.yml` is owed by every repository section 11 governs, and section
15's existence loop is what checks that — not this list. A bullet would assume
this repository's own copy is a receiver like every other tree's, which
`CONTRIBUTING.md`'s and `REVIEWING.md`'s are: this repository holds the callee,
so its call and a receiving copy's differ by the adaptation section 11's *The
workflow, and what a port of it has to adapt* states, and the comparison would
fail forever rather than the way `EXPECTED_DRIFT` expects.

Whether the receiving copies must otherwise read alike is open, not decided
here: `btclib-org/.github#267` raised it, and `btclib-org/.github#35`'s
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

**Getting onto the per-repository list below takes a reason of one kind**:
something true of that repository that makes the shared answer wrong — its
Python floor, the shape of its distribution, what it ships, what its tests are
about. Every entry on the list carries one. *This tree already does it
differently* is not such a reason: precedent by accretion is how a standard
stops being one.

**Decided per repository**: `requires-python` and `.python-version`; the matrix
breadth; which optional workflows exist past those section 10 keys on a property
of the tree; the ruff `ignore` list's entries a tree declines on its own merits
and its `per-file-ignores`; what a publishing repository checks about its
package contents past section 12's floor — the sdist allowlist, and the script a
wheel that is not one package tree needs — which is settled by measuring that
project's own distribution rather than by copying what a sibling does; the
convention tests, which each project chooses on section 7's terms; and the
`[tool.uv.sources]` table, which exists only while a dependency is not on the
index and goes the day it is.

`.gitignore` is decided per repository and so outside the compared list above:
what a tree ignores is what its own build and tools write. A package that
compiles an extension ignores the object files and the shared library it links.
The rejected alternative is one file copied into every tree, holding the union
of what any of them writes: it grows with every repository added, and a reader
of one tree cannot tell from it which entries that tree needs.

`.github/scripts/check_vendored_vectors.py` is per repository by subject, owed
where `.github/workflows/vendored-vectors.yml`, and deliberately outside the
compared list above: each copy parses the pin file its own tree keeps, so the
bytes differ wherever the subjects do, which no comparison by path can read as
anything but drift. That workflow is what runs the script weekly, and a tree
vendoring nothing keeps no pin file for it to parse. `btclib-node` keeps its
copy at `.github/scripts/check_vendored_pin.py`, a different name and not only
different bytes, and the departure is a decided one: the job is the same job,
and that copy's own header says where it departs — it opens no tracking issue on
drift, where `btclib`'s does. What every copy owes instead is a header sentence
naming what it parses and where it departs from the siblings doing the same job,
so a reader holding two copies knows which difference was decided. Its failure
mode is why the sentence is owed: an entry shape the script does not match is
skipped and the run is green, so a fix that is not about one tree's entry shape
is carried to every copy in the same campaign, the header being what says which
parts those are.

`tests/conventions_test.py` is per repository by subject, owed where
`tests/README.md`, and outside the compared list for the same reason: each copy
reads the declaration its own tree keeps, so its rows are that tree's, and so is
the `tests/` root it resolves a declared module against — `btclib-node` keeps
its copy at `tests/unit/conventions_test.py`, a different path and not only
different bytes. That file is where section 7 asks a suite to declare which of
its conventions it tests, so a tree that declares nothing has nothing for this
module to read. What the copies hold in common is a job rather than a text: read
the declaration section 7 asks for and assert that every convention it names has
a module holding a test for it. The header sentence a copy owes is about this
module: what it reads, and which of its departures are decided rather than
accidental. This repository's copy reads section 7's list of conventions off
`README.md` rather than transcribing it — which a sibling cannot, the standard
being in another repository — and says so. Its failure mode is why the sentence
is owed: a defect in the parsing that shared job needs sits in every copy
carrying it and turns nothing red anywhere, so a fix that is not about one
tree's rows or its root is carried to every copy in the same campaign, which is
what `btclib-org/.github#651` records.

## 15. Auditing a repository against this file

Alignment is measured, not remembered: each command below answers for one
section above. **Much of it runs on its own**: `tests/`, weekly from
`alignment.yml`, asks every repository these questions, a test per question and
a row per repository, since no tree holds this file. Module docstrings name
their sections, and section 2's tier the repositories, a tree it does not bind
skipped with the reason. The backlog in `tests/__init__.py` runs recorded
failures as strict expected failures naming the issue, so a tree that catches up
is reported until its row goes.

The commands below ask the same of the tree in front of you, and what the suite
does not ask yet or cannot. A repository answers for itself where it can:
`interpreters_test.py`, `conventions_test.py`, the hook-pin tests. Section 3's
rule that the classifiers name a tree's interpreters is `interpreters_test.py`
where a tree publishes and the window sweep below where it does not: publishing
decides, not being a library, because an index shows the classifiers of any
distribution. A workflow's interpreters against the window stay a reading: one
outside it is correct where the reason is beside it.

The settings: squash the only method, signatures required with an **empty**
bypass list, the self-merge bypass in `pull_request` mode and never `always`,
and a token that is `read`:

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

The tree, reading exit codes and not filtered output:

```shell
grep -n 'strict = true\|fail_under = 100\|branch = true\|"FIX"\|"TD"' \
    pyproject.toml
grep -n 'id: mypy' .pre-commit-config.yaml
git ls-files 'TODO*' '**/TODO*'
grep -hoE 'uses: [^ ]+' .github/workflows/*.yml | grep -v '@[0-9a-f]\{40\}'
grep -nE -B1 'uses: [^ ]+@[0-9a-f]{40}[^#]*$' .github/workflows/*.yml
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

- `strict = true` with no `id: mypy` is section 6's finding and a finding on its
  own: the strictness is configured and nothing runs it.
- An action not pinned to forty hex digits, a workflow with no `permissions:`
  block, and a `--frozen` anywhere are each a finding.
- A pin with no trailing tag comment is a finding unless the line printed above
  it carries the tag, which is what section 10 asks of a pin a trailing comment
  would take past the width.
- A `build-backend` other than `uv_build` in a project compiling nothing is
  section 3's finding, and decides which table declares inclusion. Section 12
  owes a `package` naming a one-package wheel, else the ignored codes and an
  escalating repository's page, script and test together; `check-sdist` gates
  wherever an sdist is built, with `[tool.check-sdist]` beside an sdist target
  only excluding.
- `tests/README.md` is section 7's answer and no command computes it: a bullet
  owed by that section and not claimed is the finding, and a claimed one is
  answered by the test asserting it.

Section 8's pragmas, telling a site from a string carrying the form:

```shell
git ls-files '*.py' | python3 -c 'import re, sys, tokenize
form = re.compile(r"#\s*pragma: no (cover|branch)")
for path in sys.stdin.read().splitlines():
    try:
        with tokenize.open(path) as source:
            tokens = list(tokenize.generate_tokens(source.readline))
    except (OSError, SyntaxError, UnicodeDecodeError, tokenize.TokenError):
        print(f"{path}\tunreadable")
        continue
    for t in tokens:
        m = form.search(t.string)
        if m is None or t.type == tokenize.COMMENT:
            continue
        line = t.start[0] + t.string[: m.start()].count("\n")
        kind = tokenize.tok_name[t.type]
        print(f"{path}:{line}\t{kind} opening at line {t.start[0]}")'
```

No output is the answer; a line is section 8's finding, where the form matched
and where its token opens. The key is not-`COMMENT`, not `STRING`, as f-strings
tokenize differently on 3.11 and 3.14; `unreadable` keeps silence from covering
a skipped file.

The metadata an index shows, half a repository setting, chained because the last
command writes (section 9); the first two name one set, up to GitHub's twenty:

```shell
gh api repos/<org>/<repo> --jq '.topics | join(", ")' &&
sed -n '/^keywords = \[/,/^\]/p' pyproject.toml &&
uv build --sdist && uvx twine check dist/*.tar.gz
```

`twine check` reads less than its name suggests (section 3), so the classifiers
are asked before a release; an empty list is the answer, and a string is one
PyPI refuses on upload:

```shell
uvx --with trove-classifiers python -c '
import pathlib, tomllib
from trove_classifiers import classifiers
declared = tomllib.loads(
    pathlib.Path("pyproject.toml").read_text()
)["project"]["classifiers"]
print([c for c in declared if c not in classifiers])'
```

`gh api` puts a failure's body on stdout and exits non-zero, so a `sed` over the
fetch turns a failed call into a blank that reads as a repository owing nothing.
Sweeps reading a file or the workflow list use two helpers setting `$ok` to
`found`, `absent` for a `(HTTP 404)`, or `unreadable`, which is no reading until
asked again and is printed rather than dropped:

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

Section 1's interpreter window, in `requires-python`, classifiers, pin and
matrix:

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

Where a line carries classifiers, the floor is the lowest, the pin the highest,
and the matrix, which only this compares, runs every one, the pin running where
it is empty. `library` lines share python.org's window; an `application` line is
read against the comment in its `.python-version`.

Section 1's uv floor, and the ceiling Dependabot's bundled updater ships, above
which it refuses to re-lock:

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

`ceiling=absent` or empty is `dependabot-core` moving what this rests on, acted
on that day. `lock=yes` with an empty `floor=` is the finding; `lock=no` owes
none. A `floor=` version other than `ceiling=` is a finding: below, the tree
admits a uv older than its lock updates; above, those updates have stopped.

Which repositories publish, deciding under section 2's first tier whether a
`SECURITY.md` is owed, and section 11's `claude-review.yml` everywhere, which
`tests/` does not ask; `--silent` because `--jq` puts a 404's body on stdout:

```shell
for r in <every repository>; do
  e=$(gh api "repos/<org>/$r/contents/.github/workflows/release.yml" \
    --silent 2>&1) && w=release.yml \
    || { printf '%s' "$e" | grep -q '(HTTP 404)' && w=none \
         || w=unreadable; }
  printf '%s\trelease=%s\n' "$r" "$w"
done

for r in <every repository>; do
  e=$(gh api "repos/<org>/$r/contents/.github/workflows/claude-review.yml" \
    --silent 2>&1) && continue
  printf '%s' "$e" | grep -q '(HTTP 404)' \
    && echo "$r has no claude-review.yml" \
    || echo "$r: claude-review.yml unreadable"
done
```

Both halves are the question, `release.yml` and the index, and neither answers
alone. A repository the endpoint cannot find also answers `(HTTP 404)`, so a
stale roster reads as `none`. The index is asked for a link back to this
organization, not a `200`, as somebody else may publish the name; `<name>` is
`pyproject.toml`'s, in its own block as the path continues past it (section 9):

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

Section 2's private channel: a setting that answers `true` everywhere, and an
address. *no SECURITY.md* is an inheriting repository, read beside the
publishing sweep; a blank line is a policy with no address found; an `@` form is
the finding. No other spelled-out address matches, since `btclib-secp256k1`
rightly gives upstream's:

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

Section 2's badge rule and section 10's record, read by source and not alt text,
which can say `license: MIT` over a refused
`img.shields.io/badge/license-MIT-blue.svg`. A badge neither gives the tree, one
the row lacks, and a row out of order are each a finding; `(absent)` is a
`README.md` section 2 owes:

```shell
for r in <every repository>; do
  read_or_mark README.md
  if [ "$ok" = found ]; then
    printf '%s' "$content" \
      | sed -nE "s|^\[!\[[^]]*\]\(([^)]*)\).*|$r\t\1|p"
  else printf '%s\t(%s)\n' "$r" "$ok"; fi
done
```

What each badge renders: anything but `200` is the finding, and its title is
read against the rule; Read the Docs and pepy print `(no title)` and are read
from the image:

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

Section 10's calendar and its Dependabot row. A file on a different day from its
namesake sorts out of place; two repositories on one minute of one day and hour,
for section 10's reason, and a tree the workflow's record entry does not name
are findings too, as are ecosystems on several days. `absent` is a
`.github/dependabot.yml` section 2's *Directories* owes:

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

for r in <every repository>; do
  read_or_mark .github/dependabot.yml
  [ "$ok" = found ] || { echo "$r dependabot $ok"; continue; }
  printf '%s' "$content" | sed -n "s/^ *day: /$r dependabot /p" | sort -u
done
```

Section 7's vendored-data pins: `workflow=no` beside a path, or a workflow with
no path, is the finding; `pins=none` is nothing vendored or other provenance:

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

**`RELEASING.md`'s by-hand recovery paths are exercised by incident, and that is
accepted rather than overlooked**: a scratch repository would join every sweep.
A walk is written down above `github-release` or in the broken release's
`CHANGELOG.md` entry, naming the release and what skipped the job. A column
above zero is where to look; with `0` in both, a skipped `github-release` beside
a present release is a walk. The raw media type and emptiness test catch a `200`
with empty `content` past the limit:

```shell
for r in <every publisher>; do
  for f in .github/workflows/release.yml CHANGELOG.md; do
    if body=$(gh api "repos/<org>/$r/contents/$f" \
      -H "Accept: application/vnd.github.raw" 2>/dev/null) \
      && [ -n "$body" ]
    then n=$(printf '%s' "$body" | grep -ciE \
      'recreated by hand|created by hand from|by hand from the run')
    else n=unreadable
    fi
    printf '%s\t%s=%s\n' "$r" "$f" "$n"
  done
done
```

### Reading the workflow comments

No tool checks them.

1. **Read every comment, end to end**: stale ones read like true ones.
1. **Check each claim against this repository's tree**, never another comment or
   the sibling it came from: triggers against `on:`, call graphs against `uses:`
   and `needs:` counted, context references against what they resolve to, cron
   days against every schedule and `dependabot.yml`, any file, line or count
   re-derived.
1. **Run the command a comment gives**, reading what it reaches: without
   `--paginate` an endpoint answers for its newest page alone.
1. **`git log -S <phrase>` on every mismatch**: *drifted* or *never matched*
   decides whether the comment or the code is fixed, and a comment describing a
   safer design never built is a finding against the code.
1. **Follow a comment line past 80 columns**, usually an un-rewrapped fix;
   section 9's yaml 100 is for a pinned SHA line only:

   ```shell
   awk 'length > 80 && /^ *#/ {print FILENAME ":" FNR}' .github/workflows/*.yml
   ```

## 16. Checklists

### A new repository

1. Its tier, measured as section 2 measures it, and its row in section
   2's table, in the pull request that creates the repository. The tier
   is which of the steps below the tree owes: a step for a section the
   tier does not bind does not exist for that tree.
1. `git init`, MIT `LICENSE`, `COPYRIGHT`, `AUTHORS.md`.
1. `pyproject.toml`: section 3's build backend, metadata, PEP 639
   licence, keywords matching the topics, urls, dependency groups, and
   the tool tables of sections 5, 6, 7 and 8.
1. Copy the files section 14 names for the tools whose configuration is
   not in `pyproject.toml`, and `.gitattributes` (with the two
   `merge=union` entries). `.python-version` and `.gitignore` are
   written rather than copied, section 14 deciding both per repository.
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
cannot be performed. Dependency is a partial order and fixes only the
steps below that say what they wait for; cost settles the rest, and it
is what makes any prefix of this list the right prefix, a normalization
landing over many pull requests and stopping wherever it stops. The tier
comes before the list, section 2's table: it says which of these steps
the tree owes at all.

A constraint that is not an order between two steps holds over all of
them. **A rule arrives with its subject**: a hook lands with the files
it reads, and configuration copied from a sibling comes minus any rule
whose subject this tree does not have yet, each such rule arriving with
its file. **A gate's first run is over a tree it has never seen**, so it
runs over the whole tree rather than over what its own step added.

1. **`REVIEWING.md` and `claude-review.yml` first**, before anything is
   proposed: section 11 is where the ack of record is that workflow's,
   and the workflow's prompt reads `REVIEWING.md` by name — so a
   repository holding neither has no ack available to it.
   `.claude/commands/review.md` lands with them, section 14 owing it
   wherever `REVIEWING.md` is.
   It is not the costliest gap but the one every step that lands as a
   pull request waits on. The settings applied straight to the
   repository — section 11's, and the branch rules of the step under
   this one — are not proposed and not reviewed, so they do not wait for
   it. The credential is an organization secret with `visibility=all`,
   so a repository configures nothing for it:
   `gh api orgs/<org>/actions/secrets` is the reading.
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
   outgoing resolution, they propose bumps to a file that step deletes.
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
   backend move is checked by the archive it produces and not by the
   file it edits — an sdist built each way, with the member lists
   compared — since what the outgoing include language expressed and the
   incoming one cannot shows up there and nowhere else.
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
   `filterwarnings = ["error"]`, `xfail_strict`.
1. **Coverage to 100** — this is the long one, and the ratchet is the
   wrong tool for the climb: measure, cover the reachable, `pragma: no
   cover` with a reason where the line is unreachable, and set
   `fail_under = 100` only once the tree is there. Include the tests in
   `source` from the start.
1. **The convention tests**, which section 7's terms decide, and
   `tests/README.md` declaring which of that section's bullets those
   are. The declaration says which conventions this tree has decided it
   does not have, which is otherwise indistinguishable from having
   forgotten them.
1. **The missing root files**, `REPOSITORY.md` first: it is the only
   record of what the settings are.
1. **Dependabot's own configuration, the sentinel workflow, and the
   periodic platform runs** — the updates held above, now that what they
   read is the lock that ships.
1. **The prose pass** — 80 columns, the reasoning and its negative
   results in the configuration comments, no stated counts, and history
   moved to the two files that carry it.
