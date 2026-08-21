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
is configured to do, and why. It is written to be read twice: once when
a repository is created, so that the shape is right from the first
commit, and once when an existing one is normalized, so that the gap is
a list rather than an impression.

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
  only: nothing is copied into a tree, so no hook reads it, no sdist
  carries it, and a repository that wants the file gated keeps its own.
- **This file** is inherited by nothing and is the point: one statement
  of the standard, linked from each repository's `CONTRIBUTING.md`,
  rather than a copy per repository for the copies to drift apart in.
- **The issue tracker** is the maintenance. An alignment finding names
  the repositories it is about and the command that re-derives it, and
  stays open until every one of them answers — which is the thing an
  issue filed on a single repository cannot do, its checkboxes being
  invisible from the others.

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
  by what a gap costs, not by what it takes to close: an unsigned commit
  or a token that can write to the repository outranks a formatter.
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
runs the same command verbatim. `CONTRIBUTING.md` carries each CI job's
command literally, so a workflow change that does not update it makes
that file wrong rather than merely stale.

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

### Dependency groups

Groups rather than extras, because uv has no default extra: an extra
alone would leave `uv sync` resolving a project without it.

| group | what it holds |
| --- | --- |
| `harness` | the test runner and its plugins, nothing else |
| `test` | `harness` plus whatever the suite delegates to |
| `lint` | mypy, pre-commit, ruff |
| `build` | what inspects a distribution before it is published |
| `docs` | sphinx and the theme |
| `mutation` | the mutation runner |
| `dev` | every group above, and the default of `uv sync` |

The `harness`/`test` split is what lets a job ask for the suite *without*
the optional native dependency, since uv's `--no-group` suppresses a
group that was selected and not one another group includes. A project
with no such dependency still keeps the two names, so the workflows are
the same file everywhere.

Where a package is both an extra and a group, the specifier is written
twice and a test refuses the day the two disagree.

### `uv.lock`

Committed, and the only thing that moves it is Dependabot's uv ecosystem
and the `uv-lock` hook. The dependency groups declare no versions: the
whole drift of ruff, mypy, pytest and sphinx lives in the lock file, so
one pull request a week carries all of it, pre-validated by the `latest`
workflow.

`[tool.uv] required-version` names the oldest uv that may read the lock —
low enough for Dependabot's own bundled uv, since it re-locks with that
version regardless. `setup-uv` given no version input reads that key, so
CI needs no second pin.

## 2. The tree

### Root files

Every repository carries these, and each is one fact in one place:

| file | what it is |
| --- | --- |
| `README.md` | the package's long description, and the site homepage |
| `LICENSE` | MIT, referred to by SPDX from `pyproject.toml` |
| `COPYRIGHT` | the three-line notice every source file opens with |
| `AUTHORS.md` | a pointer to the contributor graph, not a list |
| `CODE_OF_CONDUCT.md` | a pointer to the PSF code of conduct |
| `SECURITY.md` | reporting, supported versions, known limitations |
| `CONTRIBUTING.md` | how to work: commands, conventions, pull requests |
| `REVIEWING.md` | the standard a review is written against |
| `REPOSITORY.md` | the settings that live outside the tree |
| `RELEASING.md` | how a release is cut, and how one is recovered |
| `CHANGELOG.md` | every user-visible change, by group |
| `RELEASE_NOTES.md` | what a user has to *act* on, on top of it |
| `CLAUDE.md` | what an agent needs and cannot read off the tree |
| `MANIFEST.in` | what the sdist carries |
| `pyproject.toml` | the project and every tool's configuration |
| `uv.lock` | the pinned resolution |

**Every `README.md` ends with the same line**, under a thematic break,
naming who supports the work:

```markdown
---

btclib is actively supported by [DGI](https://dgi.io) and
[CheckSig](https://checksig.com).
```

Identical everywhere, this repository's own README and the organization
profile included, and identical on purpose: a reader arriving at any one
of these repositories should not have to work out whether it is somebody's
weekend project. Reworded per repository it would be several claims to
keep true instead of one, and the `links` workflow is what notices if
either URL stops resolving.

Dotfiles: `.pre-commit-config.yaml`, `.python-version`, `.gitattributes`,
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

## 3. `pyproject.toml` is the configuration

One file holds the project metadata and every tool that can be
configured in it. Two tools have files of their own — yamllint and
taplo — because they are found by name from the working directory and
their reasoning needs more room than a hook argument has.

- **The version is declared once**, in `[project]`. The package reads it
  back with `importlib.metadata`; the sphinx `conf.py` parses this file,
  metadata not being available to an uninstalled build. Two declarations
  are two things a release has to compare.
- **PEP 639 licensing**: `license = "MIT"` as an SPDX string and
  `license-files`, not the deprecated table and not a `License ::`
  classifier. `requires = ["setuptools>=77"]` is the floor both halves
  need.
- **`keywords` are the GitHub topics**, in the same order and the same
  lowercase spelling, ordered by relevance: PyPI shows them as given.
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
  dependency that would sit in neither the lock file nor Dependabot's
  reach nor an sdist; where one is legitimate, a local hook refusing an
  unpinned or moved submodule takes its place.
- **syntax** — `check-yaml`, `check-json`, `check-toml`,
  `pretty-format-json`.
- **Python shape** — `debug-statements`, `check-docstring-first`,
  `name-tests-test` at its default, `*_test.py`.
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
- **types** — a mypy hook, below.
- **packaging** — `uv-lock`, `check-manifest`, `pyroma`.

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

    **A badge hides its destination behind an image, and the first
    version of this hook could not reach it.** `bitcoin-core-rpc`'s
    README linking its licence file was cited as the live case for the
    rule, and that link is `[![license: MIT](…)](./LICENSE)` — a link
    text written `[^]]*` stops at the `]` closing the alt text, so the
    scan checked the image `src` and never the badge's own href. The
    cited evidence was the one destination the rule did not cover, in
    every repository that carries badges. Link text is therefore
    `(?:[^]]|\]\([^)]*\))*`, a character that is not `]` or a whole
    `](…)` group, which steps over the image and still checks the `src`
    by backtracking. Measured: a badge href renders exactly what a
    plain href renders, so every row of the table above can be written
    as a badge destination.

    Measured in all three publishing repositories, with an unresolvable
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
- **Docstrings are gated**: the `D` family with `convention = "pep257"`,
  every public module, class, method and function carrying one.
  `__init__` and the magic methods are the two exemptions pep257 itself
  does not ask for.
- **Two widths, and both are enforced**: `ruff-format` reflows code to
  88, and `[tool.ruff.lint.pycodestyle] max-doc-length = 80` holds the
  comments and docstrings — the half of a file the formatter never
  touches — to the width markdown is already held to. A comment ending
  in a URL is exempt.
- **`max-complexity = 10`**, ruff's default, with a `# noqa` and a reason
  at each site over it rather than a global bound at the tree's worst.
  `RUF100` then fails the noqa as unused the moment a refactor brings the
  function under the line, so the list can only shrink.
- **The copyright notice is a ruff rule**, `CPY` with a `notice-rgx`
  spelling out all three lines of `COPYRIGHT` and anchored with `^`. It
  replaces the copyright-notice hook, which checked only staged files
  unless given `--enforce-all` and therefore checked nothing under
  `--all-files`.
- **`per-file-ignores`** covers `__init__.py` re-exports and the test
  tree's `assert`, non-cryptographic `random` and the pytest-style rules
  a test legitimately trips. The `D` rules are **not** among them: a
  public test function states what it verifies.

## 6. mypy, strict

```toml
[tool.mypy]
strict = true
warn_unreachable = true
python_version = "<the requires-python floor>"
show_column_numbers = true
show_error_codes = true
enable_error_code = [...]
```

`strict = true` is the floor, not the ceiling: the optional error codes
strict does not turn on are surveyed one by one and enabled — among them
`ignore-without-code`, so a `type: ignore` names the rule it silences and
a blanket one cannot creep in; `deprecated`, which is the early warning
`filterwarnings = ["error"]` buys at runtime; and `redundant-expr`,
`possibly-undefined` and `warn_unreachable`, each of which finds the
runtime guard whose static type promises more than an untrusted source
can.

A site that needs one of those relaxed carries its own
`# type: ignore[code]`, never a second global exemption.

**Scope is the package, the tests and `.github/scripts`.** What lives
under `.github/scripts` imports the package and no test collects it, so
strict mode is the only thing that reads it between workflow dispatches.

One run, at the floor. A second pass at the newest interpreter would
check the same code where no source is conditional on the version.

## 7. Tests

### Layout and naming

- `tests/` mirrors the package, directory for directory.
- **`*_test.py`**, enforced by `name-tests-test` at its default. A file
  named so that pytest never collects it is not a red test, it is no
  test, and nothing but the report's count moves.
- Shared test code lives in a package `__init__.py` — vector loaders,
  helpers — never in a module whose name says "test" and holds none.
- `tests/_data/` holds vendored vectors, with a `README.md` recording
  where each came from and what pins it.

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
  package at every depth, and a census walks the tree rather than listing
  it, so a new public name fails until it is exported or recorded;
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
is worth a test.

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
weighed against.

- **Tone: neutral, factual, dry.** Explanatory detail is wanted;
  decoration is not.
- **A docstring states the contract** — what the call takes, what it
  returns or raises, and the rule the behaviour comes from. Not a
  restatement of the name.
- **A comment carries the reasoning, including the negative result** —
  why the code is as it is, and why *not* the obvious alternative. The
  second half is what stops the next reader from "fixing" a deliberate
  choice, and it is what makes a configuration file reviewable rather
  than merely readable.
- **Cite the authority.** Where behaviour comes from a standard, name it;
  where the project deviates, say so and say why.
- **Measure, don't assert.** A number in prose comes from a command, and
  the command belongs beside it. Never state a count that nothing checks,
  and never state how many of anything a file holds: a stated total is a
  line every open branch has to edit, and two branches moving it to the
  same wrong number merge without a conflict.
- **One fact in one place.** Two files stating the same thing become two
  files disagreeing about it; the second points at the first.
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

| workflow | when | what it varies |
| --- | --- | --- |
| `test` | pull request, push | platforms × interpreters |
| `lint` | pull request, push | — |
| `docs` | pull request, push | — |
| `integration` | pull request, push | a node, an emulator |
| `codeql` | push to main, weekly | languages |
| `windows`, `macos` | weekly, and a release | platform × interpreter |
| `latest` | weekly | dependencies upgraded |
| `links`, `mutation` | weekly | — |
| `published` | monthly, and a release | what the index serves |
| `release` | a tag | calls the gates, then publishes |

**What waits for a merge is the first four rows and nothing else.** The
reason is one number: the ceiling the plan puts on an organization's
concurrent jobs. At that ceiling a pull request's wall clock is the wait
for a slot rather than the work, so a platform row earns a place before a
review only if it is cheap to wait for. The expensive ones answer weekly
and before a release instead — a regression sitting on `main` for at most
a week, against every review paying for it.

`latest` is the sentinel that makes a Dependabot pull request a diff
whose result is already known: it upgrades everything the resolver
touches, runs the suite, the lint gate and the packaging checks, and
commits nothing.

### The aggregate job, and the required check

A matrix workflow ends in a job that `needs` every other job in it and is
named with its workflow — `test: every job passed` — because a check
context is keyed by name alone and two workflows with a job of the same
name produce one ambiguous check.

- **Never name a matrix cell in the branch rule.** The rule lives outside
  the repository, so a context that stops being produced blocks every
  merge with nothing in the tree to explain why.
- The aggregate **fails hard on anything but `success` or `skipped`**,
  checked by name in a shell loop that always runs — not a boolean
  expression a skipped step could leave unevaluated.
- `skipped` is legitimate on purpose: when the run was superseded by its
  concurrency group, and when a `changes` job decided the diff touches
  nothing the matrix reads.
- **A `changes` job** is the cheapest job in the workflow and decides
  whether the rest runs. It answers `true` on every trigger that has no
  base to diff against, and the files it counts as prose are narrower
  than they look: the README is the package's long description, the docs
  are read by tests, and the history files are parsed by the suite.
- Where a single job is what gates, **that job is the context**. A
  workflow whose whole answer becomes required needs an aggregate.
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
turning `enforce_admins` on would deadlock every solo merge.

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

### Review

A pull request needs an approving review from somebody other than its
author; GitHub refuses a self-approval, which is why the record of a
review is a comment whose last line is `ACK <sha>` or
`CHANGES REQUESTED <sha>`, naming a sha because an ack belongs to a tree
and not to a branch.

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

Three ecosystems: `github-actions`, `uv`, and `bundler` where a site
Gemfile exists. Pre-commit hook revisions are the fourth and have no
Dependabot ecosystem — pre-commit.ci updates them weekly instead.

Each ecosystem groups its updates into one pull request, since every pull
request runs the whole matrix. Weekly with a seven-day cooldown: a
compromised release is usually yanked within days, and the sentinel
workflow has already exercised the drift, so each pull request is a small
diff whose result is known. None declares a `target-branch`: without one
the default branch is the target, and a `target-branch` naming a branch
that is not there is not an error anywhere — it is a repository where
nothing is ever proposed.

### Pages and Read the Docs

Where a repository serves a site from its own root, the source, the
build type and the CNAME are settings rather than files, and a workflow
builds the same site so that a failure is a red check rather than a page
served broken. Read the Docs' `latest` follows the default branch,
`stable` is the highest release tag, an automation rule activates each
new tag, and the webhook has to carry the secret the project's own
integration page issued — one added by hand is refused with a 400 that
GitHub records nowhere else.

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
- **The build is reproducible**: `SOURCE_DATE_EPOCH` from the tagged
  commit, and a normalization step for the sdist. The bill of materials
  is reproducible for the same reason, so a rebuild verifies against the
  attestation exactly as the distribution files do.
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
- **The sdist's half follows from how its inclusion is declared.** An
  include list drops a tracked file nobody added to it, silently, and
  `check-manifest` gating the tree against the archive is what answers
  that; an exclude-list sdist target ships a new file by default, so its
  failure is an archive too wide, which is not silent. Past that, an
  allowlist for the sdist — which members may sit at the archive's root,
  that every member is a regular file or a directory where a tar can
  carry a symlink or a device node, that no directory holds another
  distribution's metadata — is the escalation a repository takes when its
  archive carries more than the package.
- **The smoke test runs again in the release job, without constraints**,
  after the upload rather than before: installing a dependency executes
  its code, and a compromised one must not reach a `dist/` still to be
  handed on.
- **A monthly workflow installs from the index** and asks whether the
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
the flag and `check-manifest` between them leave unpinned.
`btclib-secp256k1` has no package to name: every wheel it ships carries a
compiled artifact at the wheel's own root, so it keeps `ignore = ["W003",
"W009"]` for the top-level member that is not a mistake, and its script
asks what the flag has no wording for — which artifact a wheel of that
tag must carry, and that it is not the zero-byte one a half-finished
build step leaves behind. Its sdist target is an exclude list, so the
sdist half is not its question. `btclib` owes that half: its `MANIFEST.in`
is an include list, and its archive carries the suite and the vendored
vectors, where which files may sit at the root and what kind of member the
tar holds are questions nothing it runs otherwise asks.

## 13. Editor and agent configuration

`.vscode/settings.json` and `.vscode/extensions.json` are tracked and
hold no preference. Every recommended extension is a tool the lint gate
already runs, and the settings put the fixing ones on save: what the
editor fixes is what the hook would have fixed, so nothing reaches
`git commit` for the first time there. An extension with no hook behind
it is a second opinion nothing enforces, and the reflex installs that
would fight a hook are listed as `unwantedRecommendations`. Anything
machine-local belongs in the editor's own user settings.

`CLAUDE.md` carries what an agent cannot read off the tree: where the
gates are, which local run is the gate and which is only a report, the
non-obvious failure modes, and the rule that a session never works in the
maintainer's own checkout — a worktree per session, and never `git stash`
in one, `refs/stash` being shared across worktrees. `.claude/` is tracked
beside it, with the same argument as `.vscode/`.

## 14. Copied verbatim, and decided per repository

**The same file in every repository**, and deliberately so — prose and
configuration move between them, and a paragraph that lints in one has to
lint in the others:

- `.markdownlint.jsonc` — no rule disabled; what it names is a style
  where markdownlint's default is "consistent", which asks each file to
  agree with itself and therefore lets two files disagree.
- `.yamllint.yaml` — two rules of the default set enabled, `line-length`
  at 100 and `document-start`. The rest report a convention rather than a
  defect, each with the reason it stays off.
- `.taplo.toml` — four-space indent, `reorder_keys` left false because
  the order of a table is an argument, `array_auto_collapse` false so
  that adding an entry is a one-line diff.
- `COPYRIGHT`, `AUTHORS.md`, `CODE_OF_CONDUCT.md`, and the `ci:` block
  of `.pre-commit-config.yaml`.
- The mypy strictness block, the ruff width and complexity settings, the
  pytest strictness flags, and `fail_under = 100`.

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
convention tests, which follow the conventions that project's prose
states; and the
`[tool.uv.sources]` table, which exists only while a dependency is not on
the index and goes the day it is.

## 15. Auditing a repository against this file

Alignment is measured, not remembered. Each command below answers for
one section above.

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
grep -n 'strict = true\|fail_under = 100\|branch = true' pyproject.toml
grep -hoE 'uses: [^ ]+' .github/workflows/*.yml | grep -v '@[0-9a-f]\{40\}'
grep -L '^permissions:' .github/workflows/*.yml
grep -rn -- '--frozen' .github/workflows/
grep -rn 'merge=union' .gitattributes
git ls-files MANIFEST.in '*package-content-policy*' '*_contents*'
sed -nE '/^\[tool\.check-wheel-contents\]/,/^\[/{/^[a-z]/p;}' pyproject.toml
sed -nE '/^\[.*targets\.sdist\]/,/^\[/{/^[a-z]/p;}' pyproject.toml
uv run pre-commit run --all-files
```

An action not pinned to forty hex digits, a workflow with no
`permissions:` block, and a `--frozen` anywhere are each a finding on
their own. Check exit codes, not filtered output.

What the package-content lines have to say: where the wheel is one
package tree, a `package` naming it, whose absence is section 12's
finding; where the wheel is not one, the codes the tool is told to
ignore, and the page, the script and the test that a repository which
escalates owes together rather than singly. A tracked `MANIFEST.in` says
the sdist half is owed; an sdist target that only excludes says it is
not.

## 16. Checklists

### A new repository

1. `git init`, MIT `LICENSE`, `COPYRIGHT`, `AUTHORS.md`,
   `CODE_OF_CONDUCT.md`.
1. `pyproject.toml`: metadata, PEP 639 licence, keywords matching the
   topics, urls, dependency groups, and the tool tables of sections 5, 6,
   7 and 8.
1. Copy `.markdownlint.jsonc`, `.yamllint.yaml`, `.taplo.toml`,
   `.gitattributes` (with the two `merge=union` entries),
   `.python-version`, `.gitignore`.
1. `.pre-commit-config.yaml`, including the local mypy hook and the
   `pinned-rev` guard; `uv run pre-commit run --all-files` until clean;
   generate `.secrets.baseline`.
1. `uv sync`, commit `uv.lock`.
1. `tests/` with the naming convention, a `conftest.py` carrying the
   selective-run coverage hook, and the first convention tests.
1. `docs/source` and `.readthedocs.yaml`, built with `-W --keep-going`.
1. `MANIFEST.in`, `[tool.check-manifest]`, and a `dist` job that inspects
   what would be published.
1. Workflows: `test` (with its aggregate and its `changes` job), `lint`,
   `docs`, then the periodic ones the project earns.
1. `.github/dependabot.yml`, `ISSUE_TEMPLATE/`,
   `PULL_REQUEST_TEMPLATE.md`.
1. `CONTRIBUTING.md`, `REVIEWING.md`, `REPOSITORY.md`, `SECURITY.md`,
   `RELEASING.md`, `CHANGELOG.md`, `RELEASE_NOTES.md`, `CLAUDE.md`.
1. GitHub, in this order: default branch `main`; squash-only;
   `delete_branch_on_merge`; the three rulesets; classic protection with
   the required checks bound to the Actions app; the publishing
   environments; the read-only default token.
1. Read each setting back with the commands `REPOSITORY.md` records, and
   write the answers into it.

### Normalizing an existing repository

Ordered by what the gap costs, not by what it takes to close.

1. **Signatures and branch rules** — `required_signatures`, no direct
   push, linear history, one review, squash-only. An unsigned commit that
   already landed is history; the rule stops the next one.
1. **Token permissions** — `contents: read` by default, one elevation per
   job, and no long-lived publishing token where OIDC works.
1. **Actions pinned to commit SHAs**, then `actionlint` and `zizmor` to
   zero.
1. **`uv` and a committed lock**, `--locked` in every job, and one
   documented command per job.
1. **`.pre-commit-config.yaml` as the single lint gate**, and the lint
   workflow reduced to running it. Delete any second list of the same
   tools from the workflows.
1. **mypy `strict = true`** aimed at the `requires-python` floor, with
   the optional error codes surveyed one at a time. Every silencing
   `type: ignore` names its code.
1. **ruff** with the widths, the docstring family and `max-complexity`,
   and the copyright rule.
1. **pytest strictness** — `--strict-config`, `--strict-markers`,
   `filterwarnings = ["error"]`, `xfail_strict`. Expect this one to be
   the loudest.
1. **Coverage to 100** — this is the long one, and the ratchet is the
   wrong tool for the climb: measure, cover the reachable, `pragma: no
   cover` with a reason where the line is unreachable, and set
   `fail_under = 100` only once the tree is there. Include the tests in
   `source` from the start.
1. **The convention tests**, one per convention the prose already states.
1. **The missing root files**, `REVIEWING.md` and `REPOSITORY.md` first:
   the second is the only record of what the settings are.
1. **Dependabot, the sentinel workflow, and the periodic platform runs.**
1. **The prose pass** — 80 columns, the reasoning and its negative
   results in the configuration comments, no stated counts, and history
   moved to the two files that carry it.

---

btclib is actively supported by [DGI](https://dgi.io) and
[CheckSig](https://checksig.com).
