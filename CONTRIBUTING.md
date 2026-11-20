# Contributing

What this repository holds in common with the others of the organization
— the toolchain, the lint gate, the tool tables behind it, the workflow
set and the branch rules — is stated once in the
[organization's standard](https://github.com/btclib-org/.github), each
rule with the alternative it was decided against. It binds this
repository, so a change departing from it is a divergence, and one filed
as an issue in btclib-org/.github rather than here: a difference between
two repositories belongs to neither of them.

**This file is the same in every repository of the organization up to
its last section.** What is true of one tree only — the commands that
build its environment, the gates it runs, which of its workflows decide
a merge — is under that heading, and the comparison stops there.

How the organization decides, and who holds which role, is
[`GOVERNANCE.md`][governance]; what it intends to do, and what it
deliberately does not, is [`ROADMAP.md`][roadmap]. Both are the
organization's, one copy each beside the standard.

## The issue tracker

Where an issue is filed, and what an alignment finding has to name, is
[the standard's *What this repository is*][s-what]: an issue spanning
repositories, or whose subject is the standard, goes to
[btclib-org/.github](https://github.com/btclib-org/.github/issues), and
one about this tree alone stays here.

A finding noticed while doing something else goes where `REVIEWING.md`'s
*What is filed, and what is not* says, for an author as much as for a
reviewer: a pull request answering two questions cannot be accepted for
either.

An issue labelled `good first issue` is one set aside for a first
contribution: small and self-contained.
[One search][good-first] lists the open ones across the organization, so
a newcomer need not know in advance which repository to look in.

## Documentation and comments

[Section 9 of the standard][s9] is the prose style beyond *Write
plainly* below, and it governs the prose this tree ships — comments,
docstrings and markdown. It is not restated here: a second wording is
the one that goes stale, which is that section's own *One fact in one
place*.

A commit message is prose this tree ships too, though section 9 does not
say so: [the only merge method the rule accepts][s11] puts it on `main`
as the landing commit's body, so what is written in one is read there
long after the branch is gone.

## Working with an LLM

**Development here is LLM-based.** Most issues, code and reviews are
written by agentic sessions that the maintainer directs and reads.
Humans are welcome, as long as they are comfortable working that way.

**A contribution is yours, whoever wrote it.** Read every line before
you open the pull request, understand it, and be ready to answer
a review without the model. Text or code you have not read, or cannot
explain, is closed without review.

**For a pull request the agent opened, whoever approves it reads every
line and answers for it as their own**, the agent being the pull-request
agent of [`GOVERNANCE.md`][governance]'s *Roles*. The maintainer,
landing it through the bypass without an approval, reads every line and
answers for it instead, the landing being their own act; requiring an
approval even where the bypass is kept is the alternative set aside. The
agent signs off nothing, since a bot cannot certify the [Developer
Certificate of Origin][dco], so the approval, or that landing, is the
certification.

**The `agent` label hands an issue to that agent**, in a repository
that calls its implement workflow. [Section 11][s11]'s *Labels and issue types*
says who applies it, [section 10][s10] what the agent does with an issue
it admits, and the workflow's header which issues it takes, what answers
a `decision`, and the switch that turns it on.

**Write plainly**, in the tree and on the forge: the point first, plain
words, one fact per sentence. On the forge, the title and the first
sentence carry the point; a body is at most two short paragraphs before
any code block or template section; a comment is about 250 words, and
never more than 300, with no list and no heading; a review's summary
takes the shape `REVIEWING.md`'s *The verdict* gives it.

## Pull requests

What `main` accepts, and what it refuses to everyone, is [section 11 of
the standard][s11]. Run the gates locally before opening anything —
the last section of this file says which they are — because CI runs
exactly them, so a red run there is a local run that was not done.

**Every commit of a pull request carries a `Signed-off-by:` trailer
naming its author**, which certifies the [Developer Certificate of
Origin][dco]. `git commit -s` adds it, and `git rebase --signoff <base>`
adds it to commits already made. The `Sign-off` check is required, so
only an administrator can merge a pull request with a commit the check
refuses: *Landing it* says why `--admin` waits for no required check.
The check's failure prints the command that adds the trailer. [The
standard's *Signatures*][s-sigs] says why a signature does not replace
it, and which commits the `Sign-off` job skips.

What a pull request's title and description have to say about the issues
it closes, and why a manual link in the Development panel is a trap
neither of them shows, is [the standard's *What a pull request says it
is*][s-title]. Read it before opening one; it is the rule most often
found broken after the fact.

**Before it is opened, the branch's own commit subjects and bodies are
read against that same rule.** The description does not exist yet to
disagree with them, and [the standard][s-title] has the command that
scans the branch's own commit text for a verb in front of a reference.

**The two spellings are named here as well as there, against [section 9's
*One fact in one place*][s9]**, the paragraph above naming the section
and not the forms, which are the half a citation is got wrong in:
`(closes #N)` cites an issue the change closes, wherever the citation
sits — the title, the commit subject where [*Merge method*][s11] makes
that the thing that lands — and `(issue #N)`
cites, in those same places, an issue the change advances and does *not*
close. One token holds one meaning whichever file it sits in, so the
pair is chosen by what is true of the change rather than by which file
is being written, and a tree's own landed subjects are not what to copy
it from: nothing already landed is rewritten, so what a repository wrote
before the rule stays where it is.

`REVIEWING.md` is the standard a review is written against, and is this
file's other half. Read before opening a pull request, it is what the
pull request will be answered against.

A pull request adds no entry to `CHANGELOG.md` or `RELEASE_NOTES.md`, a
release's own pull request excepted ([section 9][s9], [section 12][s12]).

### One subject, opened as soon as it is written

A pull request answers one question. Issues that share a subject are one
pull request, closing each of them; issues that do not are one pull
request each, however small either of them is.

It is opened the moment it is written and verified — not held for the
previous one to be reviewed or to land, and not batched with the next. A
batch arrives as one reviewing job with several subjects, which is the
shape that costs the most to read; a finished pull request held back is
review that could have started and did not. A security advisory's fix is
the exception, held back as [section 12][s12]'s *A security advisory is
worked in this order* says.

Working this way stacks branches, which is fine and costs one rule: a
child whose base was amended is moved with the old base named,
