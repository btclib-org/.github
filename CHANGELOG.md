# Changelog

What changed in the standard, and why. Nothing here is released — this
repository ships by being read — so the entries are grouped by subject
rather than by version, and the record they make is the one section 15's
audit has no revision to compare against.

## Unreleased

### The repository that owns the standard carries what it names

- **`REVIEWING.md` is one file, copied verbatim.** Between the aligned
  repositories it already differed only in its title and in the section
  whose name says it is not generic; that section's contents were, with
  two exceptions, rules the whole organization keeps. Those move into the
  shared body, the two per-tree ones are handed to `CLAUDE.md`, and
  section 14 gains the file — so `tests/verbatim_test.py` compares the
  copies instead of nobody comparing them.

- **A review need not deliver a verdict.** The ack of record is what a
  landing reads and ends in `ACK <sha>` or `CHANGES REQUESTED <sha>`. A
  reading that says what it found and stops is a review too: requiring a
  verdict of every reading prices each thing worth saying at a judgement
  on the whole change.

- **Two rules a reviewer had and the standard did not.** That a cited
  fact exists is not that the citation is honest, and a search for the
  cited term cannot tell them apart. And a review says what it did *not*
  check — a command it could not run, an issue it could not read —
  because a review that answered "does it answer its issues" against the
  pull request's own account of them is reasoning in a circle nobody
  reading the last line would see.

- **`CONTRIBUTING.md`, `CHANGELOG.md` and `.gitattributes` arrive**, and
  `CLAUDE.md` keeps what only a session needs. The root-files table of
  section 2 named them and this repository had none; what the table asks
  of a repository that publishes nothing is still open, and this is the
  part of it that was not in doubt.
