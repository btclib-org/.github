<!-- markdownlint-disable MD022 MD032 -->
<!-- This file is merge=union, so a rebase joins two sections and drops
     the blank line between them without a conflict: the rule is off
     here for the duration of btclib-org/.github#33, and goes back on
     when that queue is empty. btclib-org/.github#190 is the record. -->

# Changelog

What changed in the standard, and why. Nothing here is released — this
repository ships by being read — so the entries are grouped by subject
rather than by version, and the record they make is the one section 15's
audit has no revision to compare against.

## Unreleased

### `REPOSITORY.md` points at the release fact instead of restating it

- **`REPOSITORY.md` restated that nothing here is released, once in the
  `tag-integrity` reasoning and once in *What is not configured, and
  why*, instead of pointing at `CONTRIBUTING.md`'s *A version, and no
  release*** — issue #291. Both spots now carry the pointer, in the
  shape `bbt`'s `REPOSITORY.md` already uses.

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
