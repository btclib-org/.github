# Changelog

What changed in the standard, and why. Nothing here is released — this
repository ships by being read — so the entries are grouped by subject
rather than by version, and the record they make is the one section 15's
audit has no revision to compare against.

## Unreleased

### The repository that owns the standard carries what it names

- **`REVIEWING.md` and `.claude/commands/review.md` are section 14
  verbatim files.** Between the four repositories already aligned to the
  standard, `REVIEWING.md` differed only in its H1 and in the section
  whose title says it is not generic — `btclib-node`, mid-normalization,
  is three sections short of them; that section is handed to `CLAUDE.md`,
  which is the file whose subject is what cannot be read off the tree.
  The command follows it for the same reason, and stays a file of its own
  rather than folding into `CLAUDE.md`, which every session loads
  including the one that wrote the diff.

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

- **`CONTRIBUTING.md` is one file in every repository**, and what is true
  of one tree only — the commands, the gates, which workflows decide a
  merge — is `CLAUDE.md`'s. Section 2's root-files table moves with it,
  and `CLAUDE.md`'s skeleton gains the section that answers what gates a
  merge and what only reports.

- **The files section 2 names and this repository lacked**: `COPYRIGHT`,
  `AUTHORS.md`, `CONTRIBUTING.md`, `REVIEWING.md`, `CHANGELOG.md`,
  `RELEASE_NOTES.md` and `.gitattributes`. `CODE_OF_CONDUCT.md` takes the
  shared text, and `LICENSE` loses its year range — `COPYRIGHT` names the
  holder without one, so the two disagreed the first January nobody
  remembered.

- **`AUTHORS.md` points at this repository's own contributors.** Section
  14 said the file was kept for the organization rather than per package;
  that holds today only because one graph happens to be a superset of the
  others, which nothing re-derives.

- **Section 9 states the rule for a cross-repository reference.** A bare
  `#123` resolves inside the repository it is written in. The rule was
  written in a per-tree section of `REVIEWING.md` and would have been
  lost when that section left.
