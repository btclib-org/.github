<!-- markdownlint-disable-next-line first-line-heading -->
## What this changes

<!-- What the code does now that it did not do before, and why.
     Link the issue it closes, if there is one: "Closes #123". -->

## How it was verified

<!-- The test that covers it, the vector it reproduces, the command you
     ran. New behaviour without a test is the usual reason a pull request
     waits. -->

## Checks

<!-- Only the first of these is a required check: `Lint` is the whole of
     what a merge here is gated on, and its job declines a draft pull
     request, so a draft gets no report from it at all. Running it
     before pushing is how you find out before the run does. A red suite
     run shows on the pull request and holds nothing, and it runs at all
     only on a pull request touching `alignment.yml`'s `paths:`. Nothing
     reads `CHANGELOG.md` for whether a change needed an entry. An
     unsigned commit is refused where it is written to `main`, by a
     ruleset rather than by a run, and what a squash writes there is the
     commit GitHub composes rather than the branch's own, so that rule
     never reaches yours. So the last three are yours and your
     reviewer's; CONTRIBUTING.md's *What gates a merge, and what only
     reports* is where the division is stated.
     A repository whose commands differ from these carries a template of
     its own; this one is what GitHub shows where there is none. -->

- [ ] the lint gate is clean: `uvx pre-commit run --all-files`
- [ ] the suite passes, with `BTCLIB_INTEGRATION` set — without it
      every test skips and the run exits 0; `alignment.yml` carries
      the command
- [ ] `CHANGELOG.md` has an entry, if a user would notice the change
- [ ] every commit carries a verified signature

## Anything the reviewer should know

<!-- A decision you are unsure of, an alternative you rejected, a
     specification that is ambiguous, a follow-up you left out on
     purpose. Delete the section if there is none. -->
