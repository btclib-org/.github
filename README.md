# The btclib-org repository standard

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
section 2's table has it in the tier that publishes nothing.

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
contributor installs one thing and CI installs nothing:

```shell
uv sync                      # the environment, all groups
uv run pytest                # the suite, gated at 100%
uv run pre-commit run --all-files    # the whole lint gate
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
Which of the two a repository is, section 2's tier measures here: what
this organization publishes is what other projects import, so tier 1 is
a library and everything below it an application.

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
Nothing imports it, so covering an older one buys compatibility for
nobody: `.python-version` is the newest version every dependency
publishes for, and `requires-python` is the oldest the tree itself means
to run on, which is that same version where it means to run on one
interpreter alone. Where a dependency holds `.python-version` below the
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
| `docs` | sphinx and the theme |
| `mutation` | the mutation runner |
| `dev` | every group above, and the default of `uv sync` |

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

Where a package is both an extra and a group, the specifier is written
twice and a test refuses the day the two disagree.

### `uv.lock`

Committed, and the only thing that moves it is Dependabot's uv ecosystem
and the `uv-lock` hook. The dependency groups declare no versions: the
whole drift of ruff, mypy, pytest and sphinx lives in the lock file, so
one pull request a week carries all of it, pre-validated by the
`deps-latest` workflow.

`[tool.uv] required-version` names the oldest uv that may read the lock —
low enough for Dependabot's own bundled uv, since it re-locks with that
version regardless. `setup-uv` given no version input reads that key, so
CI needs no second pin.

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
what its own practice needs: `portanode` cuts a signed tag and a GitHub
release by hand, and carries the `RELEASING.md` that says how, which its
tier does not ask for. Below it, a repository short of what its tier
binds is a gap, filed here. A gap with the reason beside it, where a
reader meets the repository — its `CLAUDE.md` or its `REPOSITORY.md` —
is a decision rather than a gap; a sentence that declines a rule and
gives no reason is a gap with a sentence in front of it, this file's
own *a rule with no reason beside it* read from the other side.

| repository | tier |
| --- | --- |
| `btclib` | 1 |
| `btclib-secp256k1` | 1 |
| `bitcoin-core-rpc` | 1 |
| `btclib-benchmarks` | 2 |
| `btclib-node` | 2 |
| `.github` | 2 |
| `bbt` | 2 |
| `portanode` | 3 |

The table is a claim, and the loop below is what checks it, in either
direction — a row the loop contradicts is the finding, and so is a
repository the loop names and the table does not. A new repository is a
row here in the pull request that creates it, section 16's first step.

```shell
for r in $(gh repo list <org> --json name --jq '.[].name'); do
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
tier 2 — there is no coverage here, and section 3 describes a file its
`pyproject.toml` is not — its `CLAUDE.md` says, with the reason.

**A tier-2 repository carries neither `RELEASING.md` nor
`RELEASE_NOTES.md`.** What the first would say is that there is no
release — `bbt`'s opens *Nothing here is released* and `btclib-node`'s
*There is no release, and no machinery for one* — and a file whose
content is its own absence is one sentence in `README.md`, not a file:
the file's being there tells every reader who has not opened it that
there is a procedure here, and `SECURITY.md`, which sends a reader to
it for what a release is in a given tree, sends them instead to a line
the `README.md` can hold. The second is what a user has to act on *at
a release*, on top of the changelog, so where no release is cut it has
nothing to be on top of; `CHANGELOG.md` stays, a change being noticed
whether or not a version names it. The alternative weighed was carrying
both ready, on the ground that a tier-2 repository could release
tomorrow. What that buys is a procedure nobody runs, kept in step with
section 12 by nobody; and the day a release arrives it arrives with
`release.yml`, which is the day the repository is tier 1 and the two
files come with it.

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
| `CHANGELOG.md` | every user-visible change, by group | 1, 2, 3 |
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

- the package directory, holding `py.typed` and a `__init__.py` that
  declares `__all__`;
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

A tree without a package may still keep `tests/` above the floor:
`.github`'s own suite is over the organization rather than over a
package this repository does not hold, and a tier is free to carry more
than it is asked for.

## 3. `pyproject.toml` is the configuration

One file holds the project metadata and every tool that can be
configured in it. Two tools have files of their own — yamllint and
taplo — because they are found by name from the working directory and
their reasoning needs more room than a hook argument has.

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

    A floor and the boundary of the property it keeps are two facts, and
    the comment states both rather than giving the second's number the
    first's reason. Under `uv_build` the sdist's own `pyproject.toml`
    became a normalized copy of the file with the verbatim one kept
    beside it as `pyproject.toml.orig` in `0.12.0`, and a floor above
    that is alignment — with the `uv` the gate pins through
    `uv-pre-commit`, and with the sibling the number was copied from —
    which is the number to lower first if a resolver ever wants it
    lower. The boundary is measured by calling the backend's own hook at
    each version,

    ```shell
    uv run --no-project --with uv_build==<version> python -c \
      "import uv_build; print(uv_build.build_sdist('<outdir>'))"
    ```

    and not with `uv build` under a pinned `requires`: handed a
    requirement its own version does not satisfy, `uv build` falls back
    to the backend it bundles and only warns, so it answers for that copy
    and not for the pin, and the same command on a machine with another
    `uv` answers differently. btclib-org/.github#143 has the table, the
    boundary read off the last `0.11` release and the first `0.12`.
- **The version is declared once**, in `[project]`. The package reads it
  back with `importlib.metadata`; the sphinx `conf.py` parses this file,
  metadata not being available to an uninstalled build. Two declarations
  are two things a release has to compare.
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
    The MIT notice names *The btclib developers*, and `AUTHORS.md` is
    where the archive says the members of that collective are listed —
    section 14 has what the file is, the vendored attribution it carries
    included, and why `COPYRIGHT` is not named beside it. The
    alternative is `LICENSE` alone: what it saves is shipping a file
    whose text is a pointer to github.com, which a reader who has the
    archive and not the site cannot follow, and what it costs is an
    archive that names the collective and never says where its members
    are listed.

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
- **`keywords` are the GitHub topics**, the same names in the same
  lowercase spelling. The keywords carry an order and the topics do not:
  PyPI shows keywords as given, so they are ordered by relevance, while
  `gh api repos/<org>/<repo> --jq '.topics'` answers alphabetically
  whatever was set. So the order is maintained on one side and compared
  on neither, and what it decides is which name is left out when GitHub's
  twenty are full — past twenty the topics are the first twenty
  keywords, which is the one place the two may differ at all.

    Both name what the tree holds. A keyword no module answers to is a
    claim an index makes on a reader's behalf; a module no keyword names
    is why somebody did not find the package. Neither is visible from
    inside the file, so both are read against the tree rather than
    against the list they were copied from.
- **`classifiers` are present**, and each is a claim about this tree
  rather than a line taken from a sibling's: `Typing :: Typed` only where
  a `py.typed` ships, an `Operating System` only where the package is
  built for it and `OS Independent` only where nothing is compiled, and
  one `Programming Language :: Python :: X.Y` per interpreter the matrix
  runs. That last one is a convention this section states, so section 7's
  closing rule makes it a test rather than a hope: a library carries it as
  `interpreters_test.py`, which reads the floor, the
  classifiers and the matrix and refuses a disagreement. Nothing local
  refuses a classifier that is not a classifier at all — `twine check`
  reads the long description and not this list, and a build accepts
  whatever the file says; PyPI's upload endpoint is what rejects one, at
  the point where a version is already being consumed. `trove-classifiers`
  is the same list as a package, and comparing against it is the check
  that can run before then.
- **`[project.urls]`** carries homepage, documentation, download,
  changelog, repository, issues and pull requests.
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
  `name-tests-test` at its default, which is section 7's `*_test.py`.
- **secrets** — `detect-private-key` and `detect-secrets` against a
  committed `.secrets.baseline`. A baseline rather than an exclusion: an
  excluded file is unwatched, where a baseline entry is a finding
  somebody has read. The two entropy plugins stay off where the vectors
  are hex strings, a new one being what a legitimate addition looks like.
  Not gitleaks: every one of its hook ids passes `--staged`, so under
  `--all-files` it scans nothing and passes.
- **spelling** — `codespell` and `typos`, both configured in
  `pyproject.toml`, both skipping vendored vectors: a typo inside an
  upstream vector is part of the vector.
- **prose and markup** — `markdownlint-cli2`, `prettier` (yaml and
  jsonc), `taplo-format`, `yamllint`.
- **schemas** — `check-dependabot` and `check-readthedocs`, because a
  typo in either file is not an error to the service that reads it: it
  silently does nothing, and the evidence is a pull request that never
  arrives.
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
    `bitcoin-core-rpc`'s `[![license: MIT](…)](./LICENSE)` is the
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

## 5. ruff

```toml
[tool.ruff.lint]
preview = true
explicit-preview-rules = true
```

The pair is what lets a rule be named in `ignore` — itself a preview
feature — without turning on everything ruff is still designing. A
preview rule then runs only where `extend-select` names it exactly.

- **`select` is broad and measured.** Every unselected family was run
  over the tree before it was left out, and what is left out is recorded
  with the reason rather than with the count it reached. A family that
  can never fire — datetime rules with no datetime, logging rules with no
  logging — stays out: a rule that cannot fire reads as an enforced
  invariant while enforcing nothing.
- **`ignore` names rules, never codes.** The reason sits in the comment
  and the rule sits in the entry, with nothing to look up between them.
- **`FIX` is selected and `TD` is not.** Unfinished work belongs in an
  issue, where it can be searched, assigned and closed; a marker in a
  comment is a backlog nobody queries, sitting beside code that reads as
  finished. `FIX` refuses four of them — `TODO`, `FIXME`, `XXX` and
  `HACK` — wherever one opens a comment, on its own line or after code.
  `TD` disciplines the format of the first three and says nothing about
  the fourth, and every unsuppressed line it could discipline is a line
  `FIX` already refuses. The two are redundant, so the choice is which
  to keep: formatting a marker, or refusing it. A repository that
  finishes what it starts keeps the refusal.
  What `FIX` does not read bounds what selecting it buys: a marker
  inside a docstring or a string literal is invisible to it, as is a
  mid-sentence mention that opens no comment, and a `TODO.md` at the
  root is the same defect in a file ruff never opens.
- **Docstrings are gated**: the `D` family with `convention = "pep257"`,
  every public module, class, method and function carrying one.
  `__init__` and the magic methods are the two exemptions pep257 itself
  does not ask for, and the `ignore` entry is the whole of each: the
  convention leaves `undocumented-public-init` and
  `undocumented-magic-method` enabled, so a tree naming neither is asked
  for a docstring at every such site. Both entries are the default, and
  declining one is not drift: the rule is then answered with a docstring,
  or with a `# noqa` that `RUF100` retires as soon as one arrives.
  Requiring them of every tree was the alternative, rejected because it
  asks a tree to drop a gate it passes. The convention is also what
  settles the pairs ruff calls incompatible, so `ignore` does not name
  the half it disables: beside a declared convention that entry changes
  no diagnostic and silences no warning. The warning ruff prints over
  such a pair appears only where nothing has settled it.
- **Two widths, and both are enforced**: `ruff-format` reflows code to
  88, and `[tool.ruff.lint.pycodestyle] max-doc-length = 80` holds the
  comments and docstrings — the half of a file the formatter never
  touches — to the width markdown is already held to. A comment ending
  in a URL is exempt. The key is half the switch: `W505` is the rule that
  reads it, so a tree leaving `W` out of `select` states a width and
  enforces none.
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

**Scope is the package, the tests and `.github/scripts`.** What lives
under `.github/scripts` imports the package and no test collects it, so
strict mode is the only thing that reads it between workflow dispatches.

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

- `tests/` mirrors the package, directory for directory.
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
  reproduced.
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
tree and the suite opens no socket.

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

**A `_data` directory beside whatever reads it**, which is `tests/_data/`
where the suite is the only reader and a directory beside the package or
the script where it is not. The underscore says the directory is not a
package: it holds no `__init__.py`, nothing imports it, and the way in is
a path built from `__file__` — the mark the language already puts on a
private module, applied where it is literally true.

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

### Integration tests

`tests/integration/` is whatever needs something the repository does not
ship — a node, a device, an emulator. Each test skips itself without the
environment switch that asks for it, the switch is named in the skip
message, and the directory is omitted from the coverage ratchet: a body
that skips itself would be an uncovered line at every commit rather than
a defect. What covers them is an unattended job, and that job fails if
its tests skipped rather than ran.

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
  hand-written list.

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
  test can reach is not one of these: for a one-off, the pragma with its
  reason beside it is still the answer.
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
  `pragma: no cover` with the reason beside it. Neither is a build left
  red.
- **Measured on one interpreter**, the one `.python-version` pins, which
  is enough at 100 only because no source branches on the version — a
  percentage below 100 could not promise that, the statement count moving
  between versions.
- **A selective run is reported and not gated.** `fail_under` applies to
  every report coverage writes, so `pytest tests/foo` would fail on the
  tree's coverage rather than its own. A `conftest.py` hook drops the
  threshold when the invocation selects a subset — paths, `-k`, `-m` —
  and leaves it alone for `--lf`, `--deselect` or an early `-x`, which
  are not selections. Setting it means writing to
  `config.known_args_namespace`: pytest-cov reads that copy and never
  `config.option`, so the obvious spelling fails silently.
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
  included; Python comments and docstrings by ruff. Code is 88, the
  formatter's; yaml is 100, because an action pinned to a commit SHA with
  its tag in a trailing comment is past 80 before anything else is said.

### `CHANGELOG.md` and `RELEASE_NOTES.md`

- The changelog gets an entry for anything a user would notice, in the
  group it belongs to. The release notes are what a user has to *act* on.
- **One fact each**: the breaking-changes list lives in the release
  notes and the detail behind it in the changelog, so neither restates
  the other.
- **Both are `merge=union` in `.gitattributes`.** Two branches appending
  a bullet to the same group conflict on the insertion point, which is a
  conflict with nothing to decide; union keeps both sides' added lines,
  on rebases included. Its price is that the two files never conflict at
  all, so the *same* entry edited on two branches merges in silence —
  which is the second reason neither file states a count.
- **Union drops the blank line between two sections it joins.** Two
  branches each adding a `###` section under `## Unreleased` produce a
  file whose second heading sits against the bullet above it, which
  MD022 and MD032 both refuse. Reading the file after a rebase is what
  puts the line back: the hook reports and does not fix, and where a
  file disables the two rules at its head the gate says nothing either.

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
- **`paths-ignore` only on `push`.** The same list on `pull_request`
  would produce no run at all for a prose-only diff, and a required check
  that produces no run blocks the merge instead of passing it.
- **`workflow_dispatch` on everything**, including the gates: a branch
  whose pull request is not open yet has no other way to ask.
- **`workflow_call`** where the release workflow reuses the gate.
- Every step is a `uv` command with `--locked`.

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

**What runs weekly does not also gate**, so nothing is asked twice at
the price a gate charges. The converse does not hold: a sentinel runs
its matrix whole, the cells a gate already covered included, because a
matrix with a hole in it is one nobody can read the shape of, and the
hole would be re-derived from the gate every time somebody asked what
ran.

Two tables make the calendar, and they are the calendar — the workflow
owns a day and an hour, the repository owns the minute:

| workflow | day | hour |
| --- | --- | --- |
| `links` | Monday | 04 |
| `vendored-vectors` | Monday | 05 |
| `codeql` | Tuesday | 04 |
| `py-arm-authority` | Tuesday | 05 |
| `deps-latest` | Wednesday | 04 |
| `pypi-install` | Wednesday | 05 |
| `alignment` | Thursday | 04 |
| `os-ubuntu` | Friday | 04 |
| `integration-hwi` | Friday | 05 |
| `os-macos` | Saturday | 04 |
| `os-windows` | Saturday | 05 |
| `mutation` | Sunday | 04 |
| `integration-bitcoind` | Sunday | 05 |

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

A day is a slot rather than a census: it says when that workflow runs
where a repository has it, not that every repository does. Dependabot is
in neither table and runs Thursday, that being the day `deps-latest`
reports
on the upgrade before the pull request arrives — it states its own
schedule in `dependabot.yml`, in a different shape, and picks its own
minute.

`tests/grid_test.py` of this repository reads both tables and every
`cron:` of every repository, in both directions: a schedule no row names
fails there, and so does a row nothing in the organization answers to,
which is what keeps a row here from being a claim nobody checks. The
commands a human runs instead are in section 15.

`deps-latest` is the sentinel that makes a Dependabot pull request a diff
whose result is already known: it upgrades everything the resolver
touches, runs the suite, the lint gate and the packaging checks, and
commits nothing.

### The aggregate job, and the required check

A workflow whose answer gates a pull request ends in a job that `needs`
every other job in it and is named with its workflow — `test: every job
passed` — because a check context is keyed by name alone and two
workflows with a job of the same name produce one ambiguous check.

**A matrix is not what asks for one.** A branch rule can name only a
context a pull request produces, so a workflow triggered by `push` and
`schedule` alone is one no rule can require, however many cells it runs,
and an aggregate there is a name nothing can hold. Where such a workflow
is to gate, the trigger and the aggregate arrive in the same pull
request, and the rule follows them.

- **Never name a matrix cell in the branch rule.** The rule lives outside
  the repository, so a context that stops being produced blocks every
  merge with nothing in the tree to explain why.
- The aggregate **fails hard on anything but `success` or `skipped`**,
  checked by name in a shell loop that always runs — not a boolean
  expression a skipped step could leave unevaluated.
- `skipped` is legitimate on purpose: when the run was superseded by its
  concurrency group, and when a `changes` job decided the diff touches
  nothing those jobs read.
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
writes down its own, with the command that reads it back — nothing here
is recoverable by reading the code.

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
its holder from the review rule *while merging a pull request* and at no
other time, which answers the one thing a solo-maintainer repository
cannot do — produce someone else's approval — and answers nothing
further. A direct push to `main` is refused for everyone. The other mode,
`always`, would permit a direct push, and what it would buy is worth
nothing once the rule is read as asking for a valid signature rather than
for a particular signer.

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

One method is also one entry in a dropdown that GitHub preselects from
whatever was used last — and the dialog that switches auto-merge on
carries the same dropdown, hours before anything merges.

`squash_merge_commit_title` and `squash_merge_commit_message` are set so
that a single-commit branch lands under its own subject and a longer one
under the pull request's title, with the branch's commit messages as the
body — never the pull request's description.

`delete_branch_on_merge` is on.

### What a pull request says it is

**A pull request that closes an issue names it in its title, in
parentheses**: `Say when github-release runs instead of relying on no if
(issue #1142)`. Squash is the only merge method, and
`squash_merge_commit_title` is `COMMIT_OR_PR_TITLE`, so that title is
what the landing commit's subject says — the number reaches `git log`
and stays reachable from a checkout with no forge in front of it. A pull
request that closes nothing carries no parentheses, and adding some
because the shape looks right is how a wrong number gets in.

The title is not the closing mechanism. `Closes #N` in the *description*
is what GitHub acts on, and both are wanted: the description closes the
issue, the title records which one. Neither works across repositories —
a keyword naming another repository's issue is a link and not a close —
so a cross-repository task keeps its tracking issue open until every one
of its pull requests has landed, and somebody closes it by hand.

**That is true of keywords and false of manual links**, which is what
makes it a trap rather than a rule with an exception. A link made by
hand in the Development panel closes its issue on merge exactly as a
keyword does, across repositories included — and it appears in no diff,
no commit message and no description, so every surface a reviewer reads
can say the opposite of what merging will do. It has happened here:
`btclib-org/bitcoin-core-rpc#178`'s body says in as many words that it
does not close `btclib-org/btclib#1160`, and it closed it.

So **what a pull request closes is read before it is merged**, from the
one place that answers:

```shell
gh api graphql -F owner=<org> -F name=<repo> -F num=<n> -f query='
query($owner:String!,$name:String!,$num:Int!){
  repository(owner:$owner,name:$name){
    pullRequest(number:$num){
      closingIssuesReferences(first:10){
        nodes{number repository{nameWithOwner}}}}}}'
```

An issue there that the description does not name is the finding, and a
cross-repository one is the finding this rule exists for: a tracking
issue closed on the first of three repositories leaves the other two
answering to nothing.

### Review

A pull request needs an approving review from somebody other than its
author; GitHub refuses a self-approval, which is why the record of a
review is a comment rather than a forge approval.

**What a landing reads is the ack of record**: a comment whose last line
is `ACK <sha>` or `CHANGES REQUESTED <sha>`, naming a sha because an ack
belongs to a tree and not to a branch. A review that delivers no verdict
is a reading and not an unfinished review; `REVIEWING.md` states that
distinction, and why, for whoever reviews.

**The ack of record is `claude-review.yml`'s**, and an author's own is
not one. A comment from the account that opened the pull request is a
statement that its gates were run — worth having, and not a reading. The
distinction is the whole of why the review requirement exists: an author
verifying their own work cannot find what they did not think to look
for, which is the class of defect a second reader exists to catch. The
workflow runs on `opened`, `reopened`, `synchronize` and
`ready_for_review`, and on demand when a comment names `@claude` — that
last is how a head that moved after the review gets a fresh one, since
the ack does not follow the branch.

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
the thing a human landing the pull request reads before pressing.

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

**A correction is a commit of its own, never an amend.** A force-push
replaces the commits the review is attached to. The one force-push that
stays right is a rebase carrying no new work.

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

**Two things a port must adapt**, and both are claims about the receiving
tree rather than settings. The prompt names `REVIEWING.md`, and it tells
the reviewer that the gates are running beside it on this sha — so a
repository without that file, or without those workflows, needs a prompt
that says something true instead of inheriting a claim about files it
does not have. Copying the workflow faithfully into a tree that has
neither is the same defect as copying any other shared file that
describes one tree, committed by the act of spreading it.

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
weekly instead.

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
`stable` is the highest release tag, an automation rule activates each
new tag, and the webhook has to carry the secret the project's own
integration page issued — one added by hand is refused with a 400 that
GitHub records nowhere else.

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
  anything that is not digits and dots.
- **A rehearsal on TestPyPI** uses `.dev<run number>`, patched in by the
  workflow rather than typed, so it is unique per run and sorts below the
  release it rehearses.
- **The tag is signed**, is checked to be an ancestor of `main`, and is
  checked to say what `pyproject.toml` says.
- **A published sdist reproduces from its tag.** The attestation every
  publisher attaches vouches for bytes, so a release rebuilt from the
  commit its tag names — by running what the release ran — gives those
  bytes back, or the attestation vouches for something no rebuild can
  check. It is stated as a property because the mechanisms setuptools
  needed are not what section 3's backends need: `uv_build` ignores
  `SOURCE_DATE_EPOCH` and writes fixed member metadata into both
  archives, where hatchling reads the variable and writes a constant of
  its own without it. What "reproduces" still names is the normalization
  step, and it is not a belt over that: `normalize_sdist.py` rewrites
  every member of the sdist from the backend's constant to
  `SOURCE_DATE_EPOCH`, the tagged commit's date, ownership cleared and
  the gzip header stamped alike, so the digest the attestation signs is
  the script's output and not the backend's. A publisher with the step
  and one without are not making one guarantee in two styles: they
  attest different bytes of the same tree, which is why every publisher
  carries it rather than each weighing whether its backend has made it
  redundant. That weighing was the alternative, and it was measured as
  the wrong question — on `bitcoin-core-rpc` the step moved every
  member's mtime from `0` to the commit's second and the digest with it,
  btclib-org/.github#140 having the figures — so the reading under which
  a migration could drop the step as inert is the one this sentence
  exists to refuse. `SOURCE_DATE_EPOCH` itself is exported from the
  tagged commit for what reads it — the normalizer, and the bill of
  materials below — and under `uv_build` for nothing else, its archives
  being the same bytes either way. Under hatchling the variable reaches
  the archives too, so exporting it for the bill of materials moves the
  digests the attestation vouches for. The compiled case stays outside
  the property: `btclib-secp256k1`'s wheels are built by cibuildwheel
  against a compiler and a toolchain nothing pins, so there the property
  is stated of the sdist and not of the wheels. Nothing yet re-derives
  it on a released tag — the command that rebuilds one and verifies it
  against the attestation is one a person runs — and that half is
  btclib-org/.github#140's.
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

    `pyroma` reads the metadata through `build`, which takes its
    non-isolated path exactly where the environment satisfies `requires`
    and falls back to an isolated build otherwise. So the hook carries
    `additional_dependencies` naming the backend at `[build-system]`'s
    own specifier: the environment satisfies the declaration by
    construction, and the fallback — a virtual environment pre-commit.ci
    cannot create — is never asked for. btclib-org/.github#145 has the
    run.

    `check-sdist` drives `uv build`, and that is not PEP 517 for this
    backend: given `build-backend = "uv_build"` it builds with the copy
    bundled in the running uv, whether or not isolation is disabled and
    whether or not the environment holds a `uv_build` at all, and where
    `requires` excludes that uv it warns and builds anyway. So naming
    the backend there decides nothing, and what packs the archive the
    gate compares against git is the hook environment's `uv`, which the
    manifest installs unpinned. `args: [--inject-junk, --installer=pip]`
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
- **The smoke test runs again in the release job, without constraints**,
  after the upload rather than before: installing a dependency executes
  its code, and a compromised one must not reach a `dist/` still to be
  handed on.
- **A scheduled workflow installs from the index** and asks whether the
  published artifact *works*, not whether it installs — an import runs
  `__init__.py` alone, where a data file missing from the wheel is opened
  only at the first call that needs it.

Worked answers, each named for the property of its distribution that
decides it rather than as a shape to copy, and each re-derived by section
15's tree commands rather than taken on trust. `bitcoin-core-rpc` names
`package = ["bitcoin_core_rpc"]` and stops there — measured against a
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

A per-file exception belongs in that file's own
`markdownlint-configure-file` comment, not in the shared config read by
files that never trip the rule it relaxes.

**Decided per repository**: `requires-python` and `.python-version`; the
matrix breadth; which optional workflows exist; the ruff `select` list's
project-specific additions and its `per-file-ignores`; what a publishing
repository checks about its package contents past section 12's floor —
the sdist allowlist, and the script a wheel that is not one package tree
needs — which follows the shape of that project's own distribution and
is settled by measuring it, not by copying what a sibling does; the
convention tests, which each project chooses on section 7's terms; and
the `[tool.uv.sources]` table, which exists only while a dependency is
not on the index and goes the day it is.

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
interpreters a tree runs, and says a library carries it as
`interpreters_test.py`; this file is what carries it for a tree that
does not: a library's classifiers are what an index shows whoever is
choosing the package, where an application's declarations are read by
whoever opens the repository. So the ends of an application's window are
compared here rather than by a module of its own. The other answer
weighed was dropping the classifiers a tree that publishes nothing shows
to no index, and what that costs is the comparison itself — the floor
and the matrix are declared either way, and nothing would be left to
read them against. What no command here compares is the classifiers
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
because half of it is a repository setting:

```shell
gh api repos/<org>/<repo> --jq '.topics | join(", ")'
sed -n '/^keywords = \[/,/^\]/p' pyproject.toml
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

Section 1's interpreter window, declared once in `requires-python`,
again in the classifiers, again in `.python-version` and a fourth time
in the matrix the platform sweeps run:

```shell
for r in <every repository>; do
  toml=$(gh api "repos/<org>/$r/contents/pyproject.toml" --jq .content \
    2>/dev/null | base64 -d 2>/dev/null)
  matrix=$(gh api "repos/<org>/$r/contents/.github/workflows" \
    --jq '.[].name' 2>/dev/null | while read -r f; do
      gh api "repos/<org>/$r/contents/.github/workflows/$f" --jq .content |
        base64 -d | sed -nE 's/^ +- "(3\.[0-9]+t?|pypy3\.[0-9]+)"$/\1/p'
    done | sort -u | paste -sd, -)
  printf '%s\tfloor %s\tclassifiers %s\tpin %s\tmatrix %s\n' "$r" \
    "$(printf '%s' "$toml" |
       sed -nE 's/^requires-python = ">=(3\.[0-9]+)"/\1/p')" \
    "$(printf '%s' "$toml" |
       sed -nE 's/^ +"Programming Language :: Python :: (3\.[0-9]+)",$/\1/p' \
       | paste -sd, -)" \
    "$(gh api "repos/<org>/$r/contents/.python-version" --jq .content \
       2>/dev/null | base64 -d 2>/dev/null | grep -v '^#')" "$matrix"
done
```

One line per repository. Where a line carries classifiers, the floor is
the lowest of them, the pin is the highest, and the matrix runs every
one. The library lines are the same window as each other, that window
being python.org's; an application's line is read against the comment in
its own `.python-version` instead, which is where section 1 puts the
dependency that set the ceiling.

The matrix column is empty where no workflow names a list of them,
which is a tree whose workflows name no interpreter at all and a tree
that runs a single one as a key: either way the pin is what runs. A `t`
suffix, in that column or in the pin's, is that version built without
the GIL and so the version a classifier names; a `pypy` prefix is an
implementation, which carries a classifier of its own under
`Implementation` rather than a version. Reading the matrix against the
classifiers is this command's work: what the suite compares them with is
the floor and the pin, and no workflow.

Which repositories publish, which is what section 2's first tier turns
on and so what decides whether a `SECURITY.md` is owed or inherited:

```shell
for r in <every repository>; do
  gh api "repos/<org>/$r/contents/.github/workflows/release.yml" \
    --silent 2>/dev/null && w=release.yml || w=none
  printf '%s\trelease=%s\n' "$r" "$w"
done
curl -s https://pypi.org/pypi/<name>/json | python3 -c 'import json, sys
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
stdout and `|| echo none` would append to it. The second reads the
project urls rather than the status code, because a name this
organization does not publish may be served by somebody else's project
of the same name — so the discriminator is a link back to the
organization and not a `200`. `<name>` is what `pyproject.toml`
declares, which is not always the repository's.

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
  policy=$(gh api "repos/<org>/$r/contents/SECURITY.md" --jq .content \
    2>/dev/null | base64 -d 2>/dev/null)
  [ -n "$policy" ] || { echo 'no SECURITY.md'; continue; }
  printf '%s\n' "$policy" | grep -o -i -E "$one|$any" \
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
upstream's and correctly there.

Section 11's rule that `claude-review.yml` is in every repository, which
no single tree can answer for the others and nothing in `tests/` asks:

```shell
for r in <every repository>; do
  gh api "repos/<org>/$r/contents/.github/workflows/claude-review.yml" \
    --silent 2>/dev/null || echo "$r has no claude-review.yml"
done
```

Silent where the rule is kept, one line per repository where it is not,
and `--silent` for the reason the publishing sweep gives.

The calendar of section 10, across the organization, an audit no single
tree can answer:

```shell
for r in <every repository>; do
  gh api "repos/<org>/$r/contents/.github/workflows" --jq '.[].name' |
  while read -r f; do
    gh api "repos/<org>/$r/contents/.github/workflows/$f" --jq '.content' |
      base64 -d | sed -n "s/^ *- cron: /$r $f /p"
  done
done | sort -k2
```

Sorted by workflow, so a file running on a different day from its
namesake in another tree is one line out of place. A minute shared by two
repositories at the same day and hour is the other finding, for the
reason section 10 gives beside the table.

That loop reads `cron:` and reaches no further, so the calendar's
Dependabot row is not in it: that schedule is an `interval` and a `day`
in `.github/dependabot.yml`, a different shape in a different file, and
it takes a second command.

```shell
for r in <every repository>; do
  gh api "repos/<org>/$r/contents/.github/dependabot.yml" --jq '.content' \
    | base64 -d | sed -n "s/^ *day: /$r dependabot /p" | sort -u
done
```

One line per repository where every ecosystem agrees, more than one
where they do not — which is itself the finding, an ecosystem opening on
a day the sentinel before it does not precede.

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
1. **`git log -S "<phrase>"` on every mismatch**, to separate *was true,
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
1. Copy `.markdownlint.jsonc`, `.yamllint.yaml`, `.taplo.toml`,
   `.gitattributes` (with the two `merge=union` entries),
   `.python-version`, `.gitignore`.
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
1. `docs/source` and `.readthedocs.yaml`, built with `-W --keep-going`.
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
1. GitHub, in this order: default branch `main`; squash-only;
   `delete_branch_on_merge`; the three rulesets; classic protection with
   the required checks bound to the Actions app; the publishing
   environments; the read-only default token; secret scanning, its push
   protection and Dependabot security updates; private vulnerability
   reporting.
1. Read each setting back with the commands `REPOSITORY.md` records, and
   write the answers into it.

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
   lands with them — `.markdownlint.jsonc`, `.yamllint.yaml`,
   `.taplo.toml` — as does `.gitattributes`, whose `merge=union` entries
   wait for the two history files below. Then run it `--all-files`, over
   everything the steps above added. `.vscode/` lands with it, section
   13's recommendations being the gate's own tools and `importStrategy`
   following the mypy hook the step below writes.
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
