# Governance

How the [btclib-org](https://github.com/btclib-org) organization makes
decisions, which roles it has, who holds each, and what each owes. It is
one document for every repository of the organization. GitHub inherits no
governance file from this repository, so a repository links here rather
than carrying a copy.

## The model

**btclib-org has a single maintainer, who takes the decisions the written
rules leave open.** The maintainer administers the organization, is the
only account the branch rules let merge without another person's approval,
and is where a review that does not converge goes.

The written rules come first. The
[organization's standard](https://github.com/btclib-org/.github) binds
every repository, and each repository's `CONTRIBUTING.md`, `REVIEWING.md`,
`REPOSITORY.md` and, where it carries one, `RELEASING.md` bind that
repository. A rule changes by a pull request like any other change.

## How a decision is made

- **A question is an issue.** One spanning repositories, or about the
  standard, is filed in this repository's tracker, and one about a single
  repository in that repository's tracker: `CONTRIBUTING.md`'s *The issue
  tracker* says which.
- **A decision is recorded on the issue it answers**, as a comment the
  maintainer writes, and the issue is the record.
  **TODO (maintainer):** confirm this sentence. It describes practice seen
  on the trackers; `CONTRIBUTING.md`'s *The landing queue* states it for
  one kind of decision only, a bounded exception to that queue.
- **A change is accepted through a pull request**, and section 11's
  *Branch protection and rulesets* is the rule: every change reaches
  `main` through one, squashed, carrying a valid signature, and with an
  approving review from somebody other than its author. The maintainer is
  the only bypass actor, in `pull_request` mode, so the maintainer can
  merge a pull request without that approval and nobody can push to
  `main` directly. `CONTRIBUTING.md`'s *The review* and *Landing it* are
  the exchange and the landing.
- **A disagreement goes to the maintainer.** One that survives a second
  exchange between author and reviewer goes to the maintainer instead of
  into a third round, as `CONTRIBUTING.md`'s *The review* says. A `NACK`
  is a disagreement with the change itself, in the sense section 11's
  *Review* gives it.
- **A release is cut the way the repository's `RELEASING.md` says**,
  with a signed tag, and its upload to an index waits for a person's
  approval of the publishing environment: section 11's *Signatures* and
  *Tokens, publishing, scanning*, and section 12 of the standard.
- **A vulnerability is reported privately**, through the channels this
  repository's [`SECURITY.md`](./SECURITY.md) names.

## Roles

Each entry says who holds the role and names the file that says what it
owes, rather than restating it.

- **The maintainer** holds the organization's administration and the
  bypass above, and takes the decisions *How a decision is made* gives
  the role; a repository's `RELEASING.md` names the maintainer as the
  reviewer of its publishing environments. The role is held by
  [`fametrano`](https://github.com/fametrano), Ferdinando Ametrano, and
  the organization's administrators are read back with:

  ```shell
  gh api "orgs/btclib-org/members?role=admin" --jq '.[].login'
  ```

  **TODO (maintainer):** who reads the address `SECURITY.md` gives beside
  the Security tab. No file of the organization says.
- **A repository administrator or collaborator** holds access to one
  repository, granted in that repository's settings and not by the
  organization, so it differs from repository to repository. The
  repository's name stands in a block of its own, for the reason section
  9's *A placeholder is bare, and last* gives, and the call needs an
  authenticated caller:

  ```shell
  repo=<repo>
  ```

  ```shell
  gh api "repos/btclib-org/${repo:?}/collaborators?affiliation=direct" \
    --jq '.[] | "\(.login) \(.role_name)"'
  ```

  **TODO (maintainer):** whether the grants that command lists stay, and
  what holding one obliges. No file of the organization says.
- **A contributor** is anybody opening an issue or a pull request, and
  owes what `CONTRIBUTING.md` says.
- **A reviewer** is anybody reading a pull request they did not write,
  and owes what [`REVIEWING.md`](./REVIEWING.md) says.
- **The review bot** is each repository's `claude-review.yml`, which
  calls this repository's `reusable-claude-review.yml`. It posts the ack
  of record, as a review of type COMMENT and never as an approval, and it
  runs only where the organization variable `CLAUDE_REVIEW_ENABLED` is
  `true`: section 11's *Review* has the rule and the command that reads
  the variable. It is not a required check.
- **Dependabot** opens the pull requests that update each repository's
  dependencies, per that repository's `.github/dependabot.yml`, and they
  pass the same rule as anybody's. Section 11's *Dependabot and
  pre-commit.ci* is which ecosystems it watches.
- **pre-commit.ci** runs each repository's `.pre-commit-config.yaml` and
  opens the weekly pull request that updates its hook revisions. Section
  4's `ci:` block is its configuration.

## Continuity

Whether the organization can go on without its maintainer is not answered
here: btclib-org/.github#1321 records that it needs a second person with
organization administrative rights.
