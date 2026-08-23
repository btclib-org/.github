# Changelog

What changed in the standard, and why. Nothing here is released — this
repository ships by being read — so the entries are grouped by subject
rather than by version, and the record they make is the one section 15's
audit has no revision to compare against.

## Unreleased

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
