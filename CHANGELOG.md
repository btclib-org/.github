# Changelog

What changed in the standard, and why. Nothing here is released — this
repository ships by being read — so the entries are grouped by subject
rather than by version, and the record they make is the one section 15's
audit has no revision to compare against.

## Unreleased

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
