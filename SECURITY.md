# Security policy

What GitHub shows for a [btclib-org](https://github.com/btclib-org)
repository carrying no policy of its own. Which repositories carry one,
and why publishing is what decides it, is section 2 of
[the standard](https://github.com/btclib-org/.github#2-the-tree).

## Reporting a vulnerability

If you have found a security vulnerability, please do not open a GitHub
issue: an issue is public from the moment it is filed, and so is the
window between filing it and a fix landing.

Report it privately instead, through *Report a vulnerability* on the
Security tab of the repository the defect is in. It opens an advisory
only the maintainers can see, the discussion stays private until an
advisory is published, and it is a thread you are in — what is asked and
what is fixed reaches you without anybody having to remember to write.
Whether that route is open on a given repository is a setting rather
than a file:

```shell
gh api repos/btclib-org/<repo>/private-vulnerability-reporting
```

If it answers `{"enabled":false}`, or you have no GitHub account, or you
would rather not use it for this, responsible disclosure by email to
*security at btclib dot org* is equally welcome. An address needs no
account and no repository setting to work, which is why it is kept
beside the button rather than replaced by it.

## What belongs here, and what belongs upstream

A defect belongs to the project whose code decides the wrong thing,
which is not always the project you were running: these repositories
build on one another and on software nobody here wrote. Where what was
parsed, signed or verified is itself wrong, the defect is most likely
the library's; where a correct answer is put to the wrong use, it
belongs to whatever did that. A dependency's flaw is the dependency's,
and reaches you through an ordinary version bump once its own
maintainers have fixed it.

Report it wherever you found it, though: routing a report is the
maintainers' job and not the reporter's, and a doubt about which project
owns a flaw is not a reason to keep it to yourself.

## Supported versions

Only the latest release is supported, and nothing is backported: a fix
is published as a new release. What a release *is* differs between these
repositories — a distribution on an index, or a signed tag and a GitHub
release with the source archive attached to it, or nothing yet — and
`RELEASING.md` is what says which of those a given repository cuts, and
therefore what upgrading means there. Where it says nothing is released,
what anybody runs is a checkout of `main` and a fix reaches them when
they pull it.

**A copy receives nothing automatically.** Vendoring a source file, or
unpacking an archive into a folder, is a supported way to use some of
this work, and this is its price: a fix reaches an installed package
through a dependency bump and reaches a copy only when somebody replaces
the file. Record beside the copy which release it came from.

## Limitations, not vulnerabilities

Some of what looks like a defect is deliberate and documented — a
private key published as a worked example, a service bound where the
reader is told it is bound, a binary this organization did not build.
Which of them a repository has is that repository's to say and this file
cannot say it for it. Read its `README.md` and its open issues first,
and report it anyway if neither answers: a limitation reported twice
costs a reply, and one nobody reported costs more.
