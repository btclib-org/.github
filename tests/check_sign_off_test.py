# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""Section 11's `Signed-off-by:` check, its script and the jobs running it.

The script reads a repository built by each test, so what is asked is
git's own trailer parsing and not a reading of it. The jobs are read from
both workflows that carry one, and every tree's `lint.yml` is asked
whether it runs one.

The script is loaded by path, `.github/scripts` being no package, as the
other scripts under it are tested.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import pytest

from . import ROOT, by_hand
from .workflows_test import calls_here, jobs

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path
    from types import ModuleType

SCRIPT = ROOT / ".github" / "scripts" / "check_sign_off.py"
WORKFLOWS = ROOT / ".github" / "workflows"
# a pull request's commits, read off the merge commit a pull_request run
# checks out
RANGE = "HEAD^1..HEAD^2"

AUTHOR = "Ann <ann@example.org>"
DEPENDABOT = "dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>"
PRE_COMMIT_CI = (
    "pre-commit-ci[bot] <66853113+pre-commit-ci[bot]@users.noreply.github.com>"
)
CLAUDE = "claude[bot] <209825114+claude[bot]@users.noreply.github.com>"
# what the script reads off a job of GitHub Actions to write the summary
SUMMARY_VARIABLES = (
    "GITHUB_STEP_SUMMARY",
    "GITHUB_BASE_REF",
    "GITHUB_SERVER_URL",
    "GITHUB_REPOSITORY",
)


@pytest.fixture
def script(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Return the script, imported by path, registered before it runs."""
    spec = importlib.util.spec_from_file_location("check_sign_off", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "check_sign_off", module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Make a repository with one base commit the working directory.

    A run of the suite in a job of GitHub Actions has the job's own
    summary file in `GITHUB_STEP_SUMMARY`, which no test writes to.
    """
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for name in SUMMARY_VARIABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)
    _git("init", "--quiet", "--initial-branch=main")
    _commit("base")


def _git(*args: str) -> str:
    """Run git in the working directory as the committer `Ann`."""
    ran = subprocess.run(
        ["git", "-c", "user.name=Ann", "-c", "user.email=ann@example.org", *args],
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    return ran.stdout


def _commit(message: str, author: str = AUTHOR, *, signoff: bool = False) -> None:
    """Commit nothing under this message and author."""
    extra = ["--signoff"] if signoff else []
    _git(
        "commit",
        "--quiet",
        "--allow-empty",
        f"--author={author}",
        "-m",
        message,
        *extra,
    )


@pytest.mark.usefixtures("repo")
def test_a_commit_signed_off_by_its_author_passes(script: ModuleType) -> None:
    """`git commit -s` writes the trailer the check reads."""
    _commit("one", signoff=True)
    _commit("two", "ANN <Ann@Example.org>", signoff=True)

    assert script.refused("main~2..main") == []


@pytest.mark.usefixtures("repo")
def test_a_commit_with_no_trailer_is_refused(script: ModuleType) -> None:
    """The line names the commit and the address the trailer has to carry."""
    _commit("unsigned")

    (line,) = script.refused("main~1..main")

    assert line.endswith(" unsigned: no Signed-off-by: <ann@example.org>")


def _rebase(out: str) -> str | None:
    """Return the `git rebase --signoff` line the failure printed, if any."""
    found = [s for s in map(str.strip, out.splitlines()) if s.startswith("git rebase ")]
    assert len(found) <= 1
    return found[0] if found else None


def _run_in(shell: str, command: str) -> None:
    """Run a printed command in the shell, as `Ann` by git's own config."""
    found = shutil.which(shell)
    if found is None:
        pytest.skip(f"{shell} is not installed")
    _git("config", "user.name", "Ann")
    _git("config", "user.email", "ann@example.org")
    flags = ["-f"] if shell == "zsh" else []
    subprocess.run([found, *flags, "-c", command], capture_output=True, check=True)


def _run_the_fix(script: ModuleType, revisions: str, out: str) -> None:
    """Run the rebase the failure printed, and read the branch again.

    The push that follows it has no remote to go to here.
    """
    rebase = _rebase(out)
    assert rebase is not None
    _run_in("bash", rebase)
    assert script.refused(revisions) == []


@pytest.mark.usefixtures("repo")
@pytest.mark.parametrize("shell", ["bash", "zsh"])
def test_the_command_the_failure_prints_signs_the_branch_off(
    script: ModuleType, capsys: pytest.CaptureFixture[str], shell: str
) -> None:
    """Run as printed, the command adds the trailer to every commit refused.

    The failure says whose identity the trailer takes, and which address
    it has to be, `GIT_COMMITTER_EMAIL` included: where that is exported
    as another address, the trailer carries that one.
    """
    _git("checkout", "--quiet", "-b", "topic")
    _commit("one", signoff=True)
    _commit("two")

    assert script.main(["main..topic"]) == 1
    out = capsys.readouterr().out
    assert "Only an administrator can merge" in out
    assert "GIT_COMMITTER_EMAIL where you export it, must be `ann@example.org`" in out
    rebase = _rebase(out)
    assert rebase == f"git rebase --signoff {_git('rev-parse', 'topic~1').strip()}"
    _run_in(shell, rebase)

    assert script.refused("main..topic") == []


@pytest.mark.usefixtures("repo")
@pytest.mark.parametrize("shell", ["bash", "zsh"])
@pytest.mark.parametrize(
    "accepted",
    [
        "earlier\n\nSigned-off-by: Earlier Name <ann@example.org>",
        "cased\n\nSigned-off-by: Ann <ANN@EXAMPLE.ORG>",
        (
            "reviewed\n\nSigned-off-by: Ann <ann@example.org>\n"
            "Reviewed-by: Bob <bob@example.org>"
        ),
    ],
)
def test_the_rebase_leaves_an_accepted_commit_alone(
    script: ModuleType, capsys: pytest.CaptureFixture[str], shell: str, accepted: str
) -> None:
    """The rebase starts after the commits the check accepts.

    Each of these is accepted, and `git rebase --signoff` would add a
    second trailer to it: it starts at the accepted commit, the parent of
    the oldest refused one, which keeps its sha and its message.
    """
    _git("checkout", "--quiet", "-b", "topic")
    _commit(accepted)
    kept = _git("rev-parse", "HEAD").strip()
    message = _git("show", "-s", "--format=%B", kept)
    _commit("refused one")
    _commit("refused two")

    assert script.main(["main..topic"]) == 1
    rebase = _rebase(capsys.readouterr().out)
    assert rebase == f"git rebase --signoff {kept}"
    _run_in(shell, rebase)

    assert script.refused("main..topic") == []
    assert _git("rev-parse", "topic~2").strip() == kept
    assert _git("show", "-s", "--format=%B", kept) == message


@pytest.mark.usefixtures("repo")
def test_the_steps_start_where_a_merged_in_base_leaves_off(
    script: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    """A branch that merged its base gets steps from the base it merged.

    The merge is the reason no command is given. The interactive rebase
    starts from the base commit last merged, so it replays none of the
    base's commits: `Bob`'s is not signed off, and a rebase from before it
    would bring it into the range.
    """
    _git("checkout", "--quiet", "-b", "topic")
    _commit("work")
    _git("checkout", "--quiet", "main")
    _commit("landed meanwhile", "Bob <bob@example.org>")
    _git("checkout", "--quiet", "topic")
    _git("merge", "--quiet", "--no-edit", "main")
    _commit("more work")

    assert script.main(["main..topic"]) == 1
    out = capsys.readouterr().out

    assert _rebase(out) is None
    assert f"git rebase -i {_git('rev-parse', 'main').strip()}," in out


def _summary_variables(
    monkeypatch: pytest.MonkeyPatch, summary: Path, base: str = "trunk"
) -> None:
    """Set what a job of GitHub Actions on a pull request into `base` sets."""
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    monkeypatch.setenv("GITHUB_BASE_REF", base)
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")


def _block(text: str, language: str) -> list[str]:
    """Return the lines of the summary's one code block in `language`.

    The block ends at the first line that is its opening fence alone.
    """
    lines = text.splitlines()
    (start,) = [
        n
        for n, s in enumerate(lines)
        if s.endswith(language) and set(s.removesuffix(language)) == {"`"}
    ]
    fence = lines[start].removesuffix(language)
    end = lines.index(fence, start + 1)
    return lines[start + 1 : end]


@pytest.mark.usefixtures("repo")
@pytest.mark.parametrize(("base", "named"), [("trunk", "`trunk`"), ("", "the base")])
def test_a_failure_writes_the_summary(
    script: ModuleType,
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch: pytest.MonkeyPatch,
    base: str,
    named: str,
) -> None:
    """The summary names the commit, the fix, the base and the rule.

    Its rebase, run as written, signs the branch off. An empty
    `GITHUB_BASE_REF` is named as the base.
    """
    summary = tmp_path_factory.mktemp("summary") / "step_summary"
    _summary_variables(monkeypatch, summary, base)
    _git("checkout", "--quiet", "-b", "topic")
    _commit("unsigned")
    fork = _git("rev-parse", "main").strip()

    assert script.main(["main..topic"]) == 1
    text = summary.read_text(encoding="utf-8")

    assert text.startswith("### Commits not signed off by their author\n")
    (line,) = _block(text, "text")
    assert line.endswith(" unsigned: no Signed-off-by: <ann@example.org>")
    assert _block(text, "shell") == [
        f"git rebase --signoff {fork}",
        "git push --force-with-lease",
    ]
    assert f"`{fork}` is the commit of {named} the branch starts from" in text
    assert (
        "(https://github.com/owner/repo/blob/HEAD/CONTRIBUTING.md#pull-requests)"
        in text
    )
    _run_the_fix(script, "main..topic", "\n".join(_block(text, "shell")))


@pytest.mark.usefixtures("repo")
def test_the_summary_names_every_commit_refused(
    script: ModuleType,
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A line per commit without the trailer, none for a signed-off one.

    What the step's file held before is kept: the summary is appended.
    """
    summary = tmp_path_factory.mktemp("summary") / "step_summary"
    summary.write_text("earlier\n", encoding="utf-8")
    _summary_variables(monkeypatch, summary)
    _git("checkout", "--quiet", "-b", "topic")
    _commit("first")
    _commit("signed", signoff=True)
    _commit("third", "Bob <bob@example.org>")

    assert script.main(["main..topic"]) == 1
    text = summary.read_text(encoding="utf-8")

    assert text.startswith("earlier\n### Commits not signed off")
    assert [line.split(" ", 1)[1] for line in _block(text, "text")] == [
        "third: no Signed-off-by: <bob@example.org>",
        "first: no Signed-off-by: <ann@example.org>",
    ]


def _commit_as(address: str, message: str = "work") -> None:
    """Write a commit whose address and message git's options would not carry.

    The object is written whole, so that its bytes are the text's, a lone
    surrogate standing for a byte that is not UTF-8.
    """
    identity = f"Ann <{address}> 1794657600 +0000".encode("utf-8", "surrogateescape")
    body = f"{message}\n".encode("utf-8", "surrogateescape")
    tree = _git("rev-parse", "HEAD^{tree}").strip().encode()
    parent = _git("rev-parse", "HEAD").strip().encode()
    raw = b"tree %s\nparent %s\nauthor %s\ncommitter %s\n\n%s" % (
        tree,
        parent,
        identity,
        identity,
        body,
    )
    made = subprocess.run(
        ["git", "hash-object", "-t", "commit", "-w", "--stdin"],
        input=raw,
        capture_output=True,
        check=True,
    )
    _git("update-ref", "HEAD", made.stdout.decode().strip())


def _two_addresses() -> None:
    """Commit as `Ann` and as `Bob`, neither signing off."""
    _commit("mine")
    _commit("theirs", "Bob <bob@example.org>")


def _a_merge() -> None:
    """Merge a signed-off side branch, as `Ann`, under `rebase.rebaseMerges`.

    The rebase would sign the merge off, which the check does not read.
    """
    _git("config", "rebase.rebaseMerges", "true")
    _git("checkout", "--quiet", "-b", "side")
    _commit("side work", signoff=True)
    _git("checkout", "--quiet", "topic")
    _commit("work")
    _git("merge", "--quiet", "--no-ff", "--no-edit", "side")


def _a_bot() -> None:
    """Commit as `Ann`, then as Dependabot, which the check does not read."""
    _commit("work")
    _commit("bump", DEPENDABOT)


def _accepted_after_refused() -> None:
    """Commit as `Ann` with no trailer, then signed off."""
    _commit("work")
    _commit("signed", signoff=True)


def _refused_on_both_sides() -> None:
    """Commit as `Ann` with no trailer, signed off, and with none again.

    The refused commits are not the tail alone: a rebase from the parent
    of the last would leave the first refused.
    """
    _commit("first")
    _commit("signed", signoff=True)
    _commit("last")


def _two_cases_of_one_address() -> None:
    """Commit as `ann@example.org` and `ANN@EXAMPLE.ORG`, two addresses."""
    _commit("lower")
    _commit("upper", "Ann <ANN@EXAMPLE.ORG>")


def _an_unusual_address() -> None:
    """Commit as an address ending in a no-break space."""
    _commit_as("ann@example.org\N{NO-BREAK SPACE}")


def _a_bot_address_cased() -> None:
    """Commit as Dependabot's address in capitals, which the check reads."""
    _commit("bump", "Bot <49699333+DEPENDABOT[BOT]@users.noreply.github.com>")


@pytest.mark.usefixtures("repo")
@pytest.mark.parametrize(
    "made",
    [
        pytest.param(made, id=made.__name__.strip("_"))
        for made in (
            _two_addresses,
            _a_merge,
            _a_bot,
            _accepted_after_refused,
            _refused_on_both_sides,
            _two_cases_of_one_address,
            _an_unusual_address,
            _a_bot_address_cased,
        )
    ],
)
def test_no_command_where_the_rebase_would_sign_off_more(
    script: ModuleType,
    capsys: pytest.CaptureFixture[str],
    made: Callable[[], None],
) -> None:
    """Only the plain case gets `git rebase --signoff`; the others, steps.

    Each case breaks one condition of `refused_tail`, and the rebase would
    there sign off a commit the check does not ask it to, miss one, or
    sign off as an address other than the commit's. The steps say whose
    identity each trailer takes.
    """
    _git("checkout", "--quiet", "-b", "topic")
    made()

    assert script.main(["main..topic"]) == 1
    out = capsys.readouterr().out

    assert _rebase(out) is None
    assert "git commit --amend --no-edit --signoff" in out
    assert "GIT_COMMITTER_EMAIL where exported, must be that author's address" in out
    assert "--reset-author" not in out


@pytest.mark.usefixtures("repo")
def test_a_root_commit_refused_gets_no_command(script: ModuleType) -> None:
    """No commit precedes a root commit for the rebase to start at."""
    _git("checkout", "--quiet", "--orphan", "topic")
    _commit("root")
    root = _git("rev-parse", "HEAD").strip()

    assert script.refused_tail("topic", [root]) is None


@pytest.mark.usefixtures("repo")
def test_an_address_not_utf8_is_read_by_its_bytes(script: ModuleType) -> None:
    """A byte that is not UTF-8 matches itself, and not its escape.

    The escape is how the line shows it.
    """
    _commit_as(
        "bad\udcff@example.org", "same\n\nSigned-off-by: Ann <bad\udcff@example.org>"
    )
    _commit_as(
        "bad\udcff@example.org", "escaped\n\nSigned-off-by: Ann <bad\\xff@example.org>"
    )

    (line,) = script.refused("main~2..main")

    assert line.endswith(" escaped: no Signed-off-by: <bad\\xff@example.org>")


@pytest.mark.usefixtures("repo")
def test_an_empty_address_is_corrected_first(
    script: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    """A commit with no author address cannot be signed off as it stands.

    `Signed-off-by: Ann <>` names no address, so the steps correct the
    author first.
    """
    _commit_as("", "work\n\nSigned-off-by: Ann <>")

    assert script.main(["main~1..main"]) == 1
    out = capsys.readouterr().out

    assert _rebase(out) is None
    assert "git commit --amend --no-edit --reset-author --signoff" in out


FORGED = "\r```\r# FORGED\r```text"


@pytest.mark.usefixtures("repo")
@pytest.mark.parametrize(
    "made",
    [
        (f"normal{FORGED}", AUTHOR),
        ("work", f"Ann <bad{FORGED}@example.org>"),
    ],
)
def test_a_control_character_is_escaped(
    script: ModuleType,
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    made: tuple[str, str],
) -> None:
    """A carriage return in a subject or an address stays on its line.

    In the log as in the summary, the commit takes one line, and the
    heading it carries is not one. An address holding one gets no
    command, and says so.
    """
    subject, author = made
    summary = tmp_path_factory.mktemp("summary") / "step_summary"
    _summary_variables(monkeypatch, summary)
    _commit(subject, author)

    assert script.main(["main~1..main"]) == 1
    out = capsys.readouterr().out
    text = summary.read_text(encoding="utf-8")

    for shown in (out, text):
        assert "# FORGED" not in shown.splitlines()
        assert "\r" not in shown
    (error,) = [s for s in out.splitlines() if s.startswith("::error::")]
    assert "\\r```\\r# FORGED\\r```text" in error
    (line,) = _block(text, "text")
    assert line == error.removeprefix("::error::")
    assert (_rebase(out) is not None) == (author == AUTHOR)
    assert ("No command is printed for an address" in text) == (author != AUTHOR)


@pytest.mark.usefixtures("repo")
def test_a_fence_outlasts_the_backticks_inside(
    script: ModuleType,
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A run of backticks in a subject gets a longer fence round it."""
    summary = tmp_path_factory.mktemp("summary") / "step_summary"
    _summary_variables(monkeypatch, summary, "a`b")
    _commit("x ```` y")

    assert script.main(["main~1..main"]) == 1
    lines = summary.read_text(encoding="utf-8").splitlines()

    start = lines.index("`````text")
    assert lines[start + 2] == "`````"
    assert any(" of `` a`b `` the branch" in s for s in lines)


@pytest.mark.usefixtures("repo")
def test_a_pass_writes_no_summary(
    script: ModuleType,
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A branch whose commits are all signed off leaves the file absent."""
    summary = tmp_path_factory.mktemp("summary") / "step_summary"
    _summary_variables(monkeypatch, summary)
    _commit("signed", signoff=True)

    assert script.main(["main~1..main"]) == 0
    assert not summary.exists()


@pytest.mark.usefixtures("repo")
def test_a_failure_with_no_summary_variable_writes_no_file(
    script: ModuleType, capsys: pytest.CaptureFixture[str]
) -> None:
    """Run locally, the failure prints its fix and writes no file.

    The repository is the working directory, so a file written relative
    to it would show as untracked.
    """
    _commit("unsigned")

    assert script.main(["main~1..main"]) == 1
    assert "git push --force-with-lease" in capsys.readouterr().out
    assert _git("status", "--porcelain", "--ignored") == ""


@pytest.mark.usefixtures("repo")
def test_a_trailer_naming_somebody_else_is_refused(script: ModuleType) -> None:
    """The author's own sign-off is asked for, not anybody's."""
    _commit("forwarded", "Bob <bob@example.org>", signoff=True)

    assert script.refused("main~1..main")


@pytest.mark.usefixtures("repo")
def test_a_trailer_outside_the_last_paragraph_is_refused(script: ModuleType) -> None:
    """Git reads trailers off the message's last paragraph alone."""
    _commit("subject\n\nSigned-off-by: Ann <ann@example.org>\n\nA closing line.")

    assert script.refused("main~1..main")


@pytest.mark.usefixtures("repo")
@pytest.mark.parametrize("bot", [DEPENDABOT, PRE_COMMIT_CI, CLAUDE])
def test_a_bot_commit_is_not_read(script: ModuleType, bot: str) -> None:
    """A commit authored by an address of `BOTS` passes with no trailer."""
    _commit("Bump a dependency", bot)

    assert script.refused("main~1..main") == []


@pytest.mark.usefixtures("repo")
def test_the_agents_commit_passes_with_no_trailer(
    script: ModuleType, tmp_path: Path
) -> None:
    """The implement workflow's commit, with no trailer, passes the check.

    The step runs as the workflow holds it, on a staged edit and the tree
    the gates would have recorded for it, so the address is the one the
    workflow commits under rather than one written here.
    """
    (step,) = [
        step
        for step in jobs(WORKFLOWS / "reusable-claude-implement.yml")["publish"][
            "steps"
        ]
        if step.get("name") == "Commit the edit"
    ]
    message = tmp_path / "in"
    message.mkdir()
    (message / "message").write_text("Do it (closes #7)\n\nThe edit.\n")
    (tmp_path / "edit.txt").write_text("an edit\n")
    _git("add", "edit.txt")
    gated = _git("write-tree").strip()
    subprocess.run(
        ["bash", "-e", "-c", step["run"]],
        env={**os.environ, "IN": str(message), "BRANCH": "topic", "GATED": gated},
        check=True,
    )

    assert _git("show", "-s", "--format=%(trailers)", "topic").strip() == ""
    assert _git("show", "-s", "--format=%an <%ae>", "topic").strip() == CLAUDE
    assert script.refused("main..topic") == []


@pytest.mark.usefixtures("repo")
def test_a_merge_commit_is_not_read(script: ModuleType) -> None:
    """The merge *Update branch* writes carries no trailer and is skipped.

    The commit merged in from the base is outside the range, being the
    base's; the branch's own commit is still read.
    """
    _git("checkout", "--quiet", "-b", "topic")
    _commit("work", signoff=True)
    _git("checkout", "--quiet", "main")
    _commit("landed meanwhile")
    _git("checkout", "--quiet", "topic")
    _git("merge", "--quiet", "--no-edit", "main")

    assert script.refused("main..topic") == []


@pytest.mark.parametrize(("signoff", "code"), [(True, 0), (False, 1)])
@pytest.mark.usefixtures("repo")
def test_the_script_reads_a_pull_requests_merge_commit(
    *,
    signoff: bool,
    code: int,
    tmp_path_factory: pytest.TempPathFactory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Run as a command on the range the jobs pass, with the merge checked out.

    The merge's first parent is the base and its second the head, as on
    the ref GitHub builds for a pull request. The variables are those a
    job sets, and the summary is written on the failure alone.
    """
    summary = tmp_path_factory.mktemp("summary") / "step_summary"
    _summary_variables(monkeypatch, summary, "main")
    _git("checkout", "--quiet", "-b", "topic")
    _commit("work", signoff=signoff)
    _git("checkout", "--quiet", "--detach", "main")
    _git("merge", "--quiet", "--no-ff", "--no-edit", "topic")

    ran = subprocess.run(
        [sys.executable, str(SCRIPT), RANGE],
        capture_output=True,
        encoding="utf-8",
        check=False,
    )

    assert ran.returncode == code, ran.stdout
    assert summary.exists() == bool(code)


def _run(job: dict[str, Any]) -> str:
    """Return the command of the job's step that runs the script."""
    run: str = next(s["run"] for s in job["steps"] if SCRIPT.name in s.get("run", ""))
    return run


@pytest.mark.parametrize(
    ("workflow", "path"),
    [
        ("reusable-lint.yml", f"standard/{SCRIPT.relative_to(ROOT).as_posix()}"),
        ("lint.yml", SCRIPT.relative_to(ROOT).as_posix()),
    ],
)
def test_the_job_reads_the_whole_branch(workflow: str, path: str) -> None:
    """Each job runs the script on the range, over a checkout of all history.

    The reusable job runs this repository's copy, checked out at the
    workflow's own commit beside the caller's tree; this repository's own job
    runs the branch's.
    """
    job = jobs(WORKFLOWS / workflow)["sign-off"]
    checkout = job["steps"][0]

    assert job["name"] == "Sign-off"
    assert job["permissions"] == {"contents": "read"}
    assert "github.event_name == 'pull_request'" in job["if"]
    assert checkout["uses"].startswith("actions/checkout@")
    assert checkout["with"]["fetch-depth"] == 0
    assert f"{path} {RANGE}" in _run(job)


def test_the_lint_gate_checks_the_sign_off(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """The tree's `lint.yml` calls the reusable workflow or runs the script.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    path = trees[repository] / ".github" / "workflows" / "lint.yml"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    called = path.is_file() and any(
        calls_here(str(job.get("uses", "")), "reusable-lint.yml")
        for job in jobs(path).values()
    )
    assert called or SCRIPT.name in text, (
        f"lint.yml neither calls reusable-lint.yml nor runs {SCRIPT.name}; "
        + by_hand(repository, f"grep -c {SCRIPT.name} .github/workflows/lint.yml")
    )
