# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The comment `reusable-sign-off-comment.yml` keeps on a pull request.

Its steps are read out of the workflow and run here, as the runner runs
them, against stand-ins for `gh` and `uv` and a bare repository on disk
in place of GitHub: which comment the last step writes, which pull
request the first finds, and what the check job fetches and what it
writes. The body is the script's, `check_sign_off.py`, read here for
what a subject can do to it. No live run is read: a `workflow_run`
workflow runs only once it is on the default branch, and only a fork's
pull request shows the token it is there for.

The rest reads the workflows' shape, which is what zizmor's
`dangerous-triggers` decline on the caller's trigger rests on, and asks
every tree for its caller.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys
from typing import TYPE_CHECKING, Any

import pytest
import yaml

from . import ROOT, SELF, by_hand
from .claude_release_test import outputs, run_step, stand_in
from .workflows_test import LOCAL, calls_here, document, jobs, triggers

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path
    from types import ModuleType

WORKFLOWS = ROOT / ".github" / "workflows"
WORKFLOW = WORKFLOWS / "reusable-sign-off-comment.yml"
CALLER = WORKFLOWS / "sign-off-comment.yml"
SCRIPT = ROOT / ".github" / "scripts" / "check_sign_off.py"

BOT = {"login": "github-actions[bot]", "type": "Bot"}
SOMEBODY = {"login": "mallory", "type": "User"}
ANOTHER_BOT = {"login": "claude[bot]", "type": "Bot"}

# the fields of the triggering run the workflows may read, the branch as
# data alone
TRUSTED = frozenset({"event", "head_sha", "head_branch", "head_repository.owner.login"})
# every expression the two workflows hold, its spaces folded: the run is
# read through these alone, its event compared and nothing else of it
ALLOWED = frozenset(
    {
        *(f"github.event.workflow_run.{field}" for field in TRUSTED - {"event"}),
        "github.event.workflow_run.event == 'pull_request'",
        "github.token",
        "job.workflow_sha",
        "runner.temp",
        "steps.find.outputs.number",
        "steps.find.outputs.base",
        "steps.find.outputs.number != ''",
        "steps.check.outputs.number",
        "steps.check.outputs.failed",
        "steps.check.outputs.digest",
        "steps.check.outputs.number != ''",
        "needs.check.outputs.number",
        "needs.check.outputs.failed",
        "needs.check.outputs.digest",
        "needs.check.outputs.number != ''",
    }
)
# an expression as GitHub finds one in a string
EXPRESSION = re.compile(r"\$\{\{(.*?)\}\}", re.DOTALL)
# the file the runner writes the triggering run's whole payload to, by
# its variable, its directory or its name
EVENT_FILE = re.compile(
    r"github_event_path|_github_workflow|event\.json", re.IGNORECASE
)

# the one line that declines zizmor's finding
DECLINE = "  workflow_run: # zizmor: ignore[dangerous-triggers]"

NUMBER = 7
ANN = "Ann <ann@example.org>"
# what the stand-in `gh` writes each call it gets to, one per line
CALLS = "calls"


def _script() -> ModuleType:
    """Return `check_sign_off.py`, imported by path."""
    spec = importlib.util.spec_from_file_location("check_sign_off", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MARKER: str = _script().MARKER


def _step(job: str, name: str) -> dict[str, Any]:
    """Return the step of that name in a job of the reusable workflow."""
    found: list[dict[str, Any]] = jobs(WORKFLOW)[job]["steps"]
    (step,) = [s for s in found if s.get("name") == name]
    return step


def _comment(number: int | str, user: dict[str, str], body: str) -> dict[str, Any]:
    """Return a comment as the issue comments endpoint lists it."""
    return {"id": number, "user": user, "body": body}


OURS = _comment(11, BOT, f"{MARKER}\n### Commits not signed off")
SECOND = _comment(12, BOT, f"{MARKER}\n### Every commit is signed off")
PLANTED = _comment(10, SOMEBODY, f"{MARKER}\nlooks like the bot's")
QUOTED = _comment(13, BOT, f"> {MARKER}\nanother workflow's")
EDITED = _comment(14, BOT, f"{MARKER}\r\nedited in the browser")
EMPTY = _comment(15, SOMEBODY, "")
BOTS = _comment(16, ANOTHER_BOT, f"{MARKER}\nanother bot's")


def _decide(pages: list[list[dict[str, Any]]], *, failed: bool) -> str:
    """Run the step's own decision over the pages `gh api --paginate` prints.

    It prints each page's array, one after the other.
    """
    program = _step("comment", "Post or edit the comment")["env"]["DECIDE"]
    ran = subprocess.run(
        [
            "jq",
            "-rn",
            "--arg",
            "marker",
            MARKER,
            "--arg",
            "failed",
            "true" if failed else "false",
            program,
        ],
        input="".join(json.dumps(page) for page in pages),
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    return ran.stdout.strip()


@pytest.mark.parametrize(
    ("pages", "failed", "wanted"),
    [
        ([[]], True, "create"),
        ([[OURS]], True, "update 11"),
        ([[OURS]], False, "update 11"),
        ([[]], False, "nothing"),
        ([[PLANTED]], True, "create"),
        ([[PLANTED]], False, "nothing"),
        ([[PLANTED, OURS, SECOND]], True, "update 11"),
        ([[PLANTED], [OURS]], False, "update 11"),
        ([[QUOTED, EMPTY]], True, "create"),
        ([[EDITED]], False, "update 14"),
        ([[BOTS]], False, "nothing"),
    ],
    ids=[
        "none, a failure",
        "ours, a failure",
        "ours, a pass",
        "none, a pass",
        "the marker in somebody's comment, a failure",
        "the marker in somebody's comment, a pass",
        "two of ours",
        "ours on a later page",
        "the marker not first, and an empty body",
        "the marker before a carriage return",
        "the marker in another bot's comment",
    ],
)
def test_the_comment_is_edited_created_on_a_failure_or_left(
    pages: list[list[dict[str, Any]]], *, failed: bool, wanted: str
) -> None:
    """The first comment of the bot's opening with the marker is edited.

    Where there is none, a failure posts one and a pass posts nothing.
    """
    assert _decide(pages, failed=failed) == wanted


# answers `gh api` with `GH_HEAD` for a pull request's head and the file
# `GH_PAGES` names for a list, and writes
# every call and, for a write, the body file's text to `GH_CALLS`
_GH = """\
printf '%s\\n' "$*" >> "$GH_CALLS"
for arg in "$@"; do
  case "$arg" in
    body=@*) cat "${arg#body=@}" >> "$GH_CALLS" ;;
  esac
done
case "$*" in
  *--silent*) ;;
  *"/pulls/"*) printf '%s\n' "$GH_HEAD" ;;
  *) cat "$GH_PAGES" ;;
esac
"""


def _bench(tmp_path: Path, pages: list[list[dict[str, Any]]]) -> dict[str, str]:
    """Write the stand-in `gh` and its answer, and return the step's runner.

    :returns: what the runner sets that the steps read.
    """
    bench = tmp_path / "bench"
    bench.mkdir()
    stand_in(bench, "gh", _GH)
    answer = tmp_path / "pages.json"
    answer.write_text("".join(json.dumps(page) for page in pages), encoding="utf-8")
    temp = tmp_path / "temp"
    temp.mkdir()
    return {
        "BENCH": str(bench),
        "GH_PAGES": str(answer),
        "GH_CALLS": str(tmp_path / CALLS),
        "RUNNER_TEMP": str(temp),
        "GITHUB_OUTPUT": str(tmp_path / "output"),
        "GITHUB_REPOSITORY": "owner/repo",
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
        "GH_TOKEN": "token",
    }


def _calls(env: dict[str, str]) -> list[str]:
    """Return the lines the stand-in `gh` wrote."""
    path = pathlib.Path(env["GH_CALLS"])
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def _post(
    tmp_path: Path,
    pages: list[list[dict[str, Any]]],
    *,
    failed: bool,
    digest: str | None = None,
    **given: str,
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    """Run the comment step on a body the check job wrote.

    :param given: values that replace what the step is otherwise given.
    :returns: the finished step, and the calls `gh` got.
    """
    env = _bench(tmp_path, pages)
    body = tmp_path / "temp" / "sign-off-comment" / "body.md"
    body.parent.mkdir()
    body.write_text(f"{MARKER}\nthe body\n", encoding="utf-8")
    step = _step("comment", "Post or edit the comment")
    env |= {
        **step["env"],
        "NUMBER": str(NUMBER),
        "HEAD_SHA": "a" * 40,
        "GH_HEAD": "a" * 40,
        "FAILED": "true" if failed else "false",
        "DIGEST": digest or hashlib.sha256(body.read_bytes()).hexdigest(),
    }
    env |= given
    ran = run_step(step["run"], tmp_path, tmp_path / "bench", env)
    return ran, _calls(env)


PULL = f"api repos/owner/repo/pulls/{NUMBER} --jq .head.sha"
LIST = f"api --paginate repos/owner/repo/issues/{NUMBER}/comments?per_page=100"


@pytest.mark.parametrize(
    ("pages", "failed", "wanted"),
    [
        (
            [[PLANTED]],
            True,
            [
                PULL,
                LIST,
                (
                    f"api --silent -X POST repos/owner/repo/issues/{NUMBER}/comments"
                    " -F body=@{body}"
                ),
                MARKER,
                "the body",
            ],
        ),
        (
            [[OURS]],
            False,
            [
                PULL,
                LIST,
                (
                    "api --silent -X PATCH repos/owner/repo/issues/comments/11"
                    " -F body=@{body}"
                ),
                MARKER,
                "the body",
            ],
        ),
        ([[PLANTED]], False, [PULL, LIST]),
    ],
    ids=["created", "edited", "left"],
)
def test_the_step_writes_what_it_decides(
    tmp_path: Path,
    pages: list[list[dict[str, Any]]],
    *,
    failed: bool,
    wanted: list[str],
) -> None:
    """The body goes from the file the check job wrote, whole."""
    ran, calls = _post(tmp_path, pages, failed=failed)

    body = tmp_path / "temp" / "sign-off-comment" / "body.md"
    assert ran.returncode == 0, ran.stderr
    assert calls == [call.replace("{body}", str(body)) for call in wanted]


def test_a_body_another_job_wrote_is_not_posted(tmp_path: Path) -> None:
    """A body whose digest is not the check job's stops the step first."""
    ran, calls = _post(tmp_path, [[]], failed=True, digest="0" * 64)

    assert ran.returncode != 0
    assert "not the one the check job wrote" in ran.stdout
    assert calls == []


@pytest.mark.parametrize(
    ("number", "comment"),
    [("7/../8", OURS), (str(NUMBER), _comment("11/../12", BOT, OURS["body"]))],
    ids=["the number", "the comment's id"],
)
def test_a_path_for_a_number_is_refused(
    tmp_path: Path, number: str, comment: dict[str, Any]
) -> None:
    """The step writes to no path a value it did not check is a number."""
    ran, calls = _post(tmp_path, [[comment]], failed=True, NUMBER=number)

    assert ran.returncode != 0
    assert not [call for call in calls if "--silent" in call]


def test_a_pull_request_that_moved_on_gets_nothing(tmp_path: Path) -> None:
    """Where the head is no longer the run's, the step writes nothing.

    The run of an older head can reach this job after a newer one's.
    """
    ran, calls = _post(tmp_path, [[OURS]], failed=True, GH_HEAD="b" * 40)

    assert ran.returncode == 0, ran.stderr
    assert calls == [PULL]


def test_each_comment_waits_for_the_one_before_it() -> None:
    """The comment job's group alone, and it cancels no run, pending or not.

    `queue: max` keeps every pending run where the default would cancel
    one for the next, so that the newest head's is not cancelled by an
    older head's queued after it. With the head read again before the
    write, the last run to write is the newest head's.
    """
    assert "concurrency" not in document(CALLER)
    assert "concurrency" not in document(WORKFLOW)
    found = jobs(WORKFLOW)
    assert [job for job in found if "concurrency" in found[job]] == ["comment"]
    assert found["comment"]["concurrency"] == {
        "group": "sign-off-comment-${{ needs.check.outputs.number }}",
        "cancel-in-progress": False,
        "queue": "max",
    }


def _pull(number: int, sha: str, *, draft: bool = False) -> dict[str, Any]:
    """Return a pull request as the pulls endpoint lists it."""
    return {
        "number": number,
        "state": "open",
        "draft": draft,
        "head": {"sha": sha},
        "base": {"ref": "main"},
        "title": "never read",
    }


HEAD = "a" * 40


@pytest.mark.parametrize(
    ("pages", "branch", "wanted"),
    [
        ([[_pull(NUMBER, HEAD)]], "topic", {"number": str(NUMBER), "base": "main"}),
        ([[_pull(NUMBER, "b" * 40)]], "topic", {}),
        ([[_pull(NUMBER, HEAD), _pull(8, HEAD)]], "topic", {}),
        ([[_pull(NUMBER, HEAD, draft=True)]], "topic", {}),
        ([[]], "topic", {}),
        ([[_pull(NUMBER, HEAD)]], "", {}),
    ],
    ids=[
        "one at the head",
        "moved on",
        "two at the head",
        "a draft",
        "none",
        "no branch",
    ],
)
def test_the_pull_request_is_the_one_open_at_the_run_s_head(
    tmp_path: Path,
    pages: list[list[dict[str, Any]]],
    branch: str,
    wanted: dict[str, str],
) -> None:
    """Anything but one open pull request at the head finds nothing.

    The branch reaches the API as a query parameter, never as shell text.
    """
    env = _bench(tmp_path, pages)
    step = _step("check", "Find the pull request")
    env |= {"OWNER": "fork", "BRANCH": branch, "HEAD_SHA": HEAD}
    ran = run_step(step["run"], tmp_path, tmp_path / "bench", env)

    assert ran.returncode == 0, ran.stderr
    assert outputs(tmp_path / "output") == wanted
    if branch:
        (call,) = _calls(env)
        assert "-f head=fork:topic" in call


@pytest.mark.parametrize(
    ("key", "value"),
    [("base", "a..b"), ("number", 0), ("number", "7/../8")],
    ids=["a base git cannot name", "no number", "a path for a number"],
)
def test_what_the_api_answers_is_checked(
    tmp_path: Path, key: str, value: str | int
) -> None:
    """The base is a refspec's part and the number a path's, so both are read.

    One git refuses, or anything but a number, stops the step.
    """
    pull = _pull(NUMBER, HEAD)
    if key == "base":
        pull["base"]["ref"] = value
    else:
        pull["number"] = value
    env = _bench(tmp_path, [[pull]])
    step = _step("check", "Find the pull request")
    env |= {"OWNER": "fork", "BRANCH": "topic", "HEAD_SHA": HEAD}
    ran = run_step(step["run"], tmp_path, tmp_path / "bench", env)

    assert ran.returncode != 0
    assert outputs(tmp_path / "output") == {}


GIT_ENV = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Ann",
    "GIT_AUTHOR_EMAIL": "ann@example.org",
    "GIT_COMMITTER_NAME": "Ann",
    "GIT_COMMITTER_EMAIL": "ann@example.org",
}


def _git(
    repository: Path, *args: str, stdin: str = "", author: str = "ann@example.org"
) -> str:
    """Run git on a repository with no configuration but its own."""
    ran = subprocess.run(
        ["git", f"--git-dir={repository}", *args],
        input=stdin,
        env={**os.environ, **GIT_ENV, "GIT_AUTHOR_EMAIL": author},
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    return ran.stdout.strip()


def _server(
    tmp_path: Path, messages: list[str], author: str = "ann@example.org"
) -> tuple[Path, str, str]:
    """Write GitHub's half: a base commit, and a branch of these messages.

    Each commit is written with `git commit-tree` over one file, so the
    repository holds trees and blobs a fetch could bring. The base is
    `main`, the branch `refs/pull/<NUMBER>/head`, its commits authored
    at `author`.

    :returns: the server's directory, the base's sha and the head's.
    """
    root = tmp_path / "server"
    repository = root / "owner" / "repo"
    repository.mkdir(parents=True)
    _git(repository, "init", "--quiet", "--bare")
    _git(repository, "config", "uploadpack.allowFilter", "true")
    blob = _git(repository, "hash-object", "-w", "--stdin", stdin="code\n")
    tree = _git(repository, "mktree", stdin=f"100644 blob {blob}\tcode.py\n")
    base = head = _git(repository, "commit-tree", "-m", "base", tree)
    for message in messages:
        head = _git(
            repository,
            "commit-tree",
            "-p",
            head,
            "-F",
            "-",
            tree,
            stdin=message,
            author=author,
        )
    _git(repository, "update-ref", "refs/heads/main", base)
    _git(repository, "update-ref", f"refs/pull/{NUMBER}/head", head)
    return root, base, head


# `uv run … <script> <arguments>` as the interpreter running the tests,
# writing down first what the script would read of the lazy-fetch guard
_UV = f"""\
printf '%s' "${{GIT_NO_LAZY_FETCH-unset}}" > "$UV_SAW"
while [ $# -gt 0 ]; do
  case "$1" in
    *.py) break ;;
    *) shift ;;
  esac
done
exec {shlex.quote(sys.executable)} "$@"
"""


def _check(
    tmp_path: Path,
    messages: list[str],
    *,
    head: str | None = None,
    author: str = "ann@example.org",
    uv: str = _UV,
) -> tuple[subprocess.CompletedProcess[str], dict[str, str], str]:
    """Run the check job's fetch and script on a branch of these messages.

    :param head: the run's head commit, the branch's own where None.
    :param author: the address the branch's commits are authored at.
    :param uv: the stand-in for `uv`.
    :returns: the finished step, its outputs, and the sha the branch
        starts from.
    """
    root, base, tip = _server(tmp_path, messages, author)
    env = _bench(tmp_path, [])
    stand_in(tmp_path / "bench", "uv", uv)
    workspace = tmp_path / "workspace"
    scripts = workspace / "standard" / ".github" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / SCRIPT.name).write_bytes(SCRIPT.read_bytes())
    step = _step("check", "Check the commits")
    env |= {
        **GIT_ENV,
        **step["env"],
        "NUMBER": str(NUMBER),
        "BASE": "main",
        "HEAD_SHA": head or tip,
        "GITHUB_SERVER_URL": root.as_uri(),
        "GITHUB_REPOSITORY": "owner/repo",
        "UV_SAW": str(tmp_path / "uv-saw"),
    }
    ran = run_step(step["run"], workspace, tmp_path / "bench", env)
    return ran, outputs(tmp_path / "output"), base


def _fetched(tmp_path: Path) -> set[str]:
    """Return the kinds of object the check job's repository holds."""
    listed = _git(
        tmp_path / "temp" / "sign-off.git",
        "cat-file",
        "--batch-all-objects",
        "--batch-check=%(objecttype)",
    )
    return set(listed.split())


def _body(tmp_path: Path) -> str:
    """Return the comment the check job wrote."""
    return (tmp_path / "temp" / "sign-off-comment" / "body.md").read_text(
        encoding="utf-8"
    )


def test_the_check_job_fetches_commits_alone_and_writes_the_failure(
    tmp_path: Path,
) -> None:
    """A branch with a commit not signed off gets the failure's comment.

    The repository holds commits and no tree and no blob, and the script
    reads them with lazy fetching off.
    """
    signed = "one\n\nSigned-off-by: Ann <ann@example.org>\n"
    ran, found, base = _check(tmp_path, [signed, "two\n"])

    assert ran.returncode == 0, ran.stderr
    assert _fetched(tmp_path) == {"commit"}
    assert (tmp_path / "uv-saw").read_text(encoding="utf-8") == "1"
    assert found["number"] == str(NUMBER)
    assert found["failed"] == "true"
    body = _body(tmp_path)
    assert found["digest"] == hashlib.sha256(body.encode()).hexdigest()
    assert body.startswith(f"{MARKER}\n### Commits not signed off by their author\n")
    assert " two: no Signed-off-by: <ann@example.org>" in body
    assert body.endswith(f"\n{_script().CLOSING}\n")
    one = _git(tmp_path / "temp" / "sign-off.git", "rev-parse", "refs/pull/head~1")
    assert f"git rebase --signoff {one}" in body
    assert f"`{base}` is the commit of `main` the branch starts from" in body


def test_the_warning_counts_from_the_first_request() -> None:
    """The week starts at the first request, whoever made it, on no date.

    Where the week from the last reopen ends later, that week counts, so
    that the author has the week to push the trailers.

    An earlier request is a maintainer's or this job's own before a pass,
    so the comment names no start of its own, and how the pull request
    comes back is the link to `CONTRIBUTING.md` the summary ends with.
    """
    closing = _script().CLOSING
    body = _script().comment(
        [" two: no Signed-off-by: <ann@example.org>"], [], [], "a", ""
    )

    assert "seven days after the first request to sign off on it" in closing
    assert "that warns of the closing" in closing
    assert "this comment or an earlier one" in closing
    assert "or seven days after its last reopen, where that is later" in closing
    assert not re.search(r"[0-9]", closing)
    assert "posted" not in closing
    assert body.index("CONTRIBUTING.md#pull-requests)") < body.index(closing)


def test_the_check_job_writes_the_pass(tmp_path: Path) -> None:
    """A branch whose commits are all signed off gets the pass's comment."""
    ran, found, _ = _check(tmp_path, ["one\n\nSigned-off-by: Ann <ann@example.org>\n"])

    assert ran.returncode == 0, ran.stderr
    assert _fetched(tmp_path) == {"commit"}
    assert found["failed"] == "false"
    head = _git(tmp_path / "temp" / "sign-off.git", "rev-parse", "refs/pull/head")
    assert _script().CLOSING not in _body(tmp_path)
    assert _body(tmp_path) == "\n".join(
        [
            MARKER,
            "### Every commit is signed off by its author",
            "",
            (
                f"Each commit read up to `{head[:12]}` carries a Signed-off-by:"
                " trailer with its author's address."
            ),
            "",
        ]
    )


def test_a_branch_that_moved_writes_nothing(tmp_path: Path) -> None:
    """Where the fetched head is not the run's, the job leaves no output."""
    ran, found, _ = _check(tmp_path, ["two\n"], head="b" * 40)

    assert ran.returncode == 0, ran.stderr
    assert found == {}
    assert not (tmp_path / "temp" / "sign-off-comment").exists()


# each subject, and the word of it that shows where it is rendered
# a script that writes this to the file after `--comment`, and exits so
_WRITES = """\
while [ "$1" != --comment ]; do shift; done
{write}
exit {code}
"""


@pytest.mark.parametrize(
    ("write", "code"),
    [("", 1), (': > "$2"', 1), ('echo body > "$2"', 2)],
    ids=["no body", "an empty body", "a body and another exit"],
)
def test_a_script_that_writes_no_comment_stops_the_step(
    tmp_path: Path, write: str, code: int
) -> None:
    """Only a body the script wrote, and its exit 0 or 1, reach the output.

    An uncaught error exits 1 too, and writes no body. Any other exit is
    the step's.
    """
    uv = _WRITES.format(write=write, code=code)
    ran, found, _ = _check(tmp_path, ["two\n"], uv=uv)

    assert ran.returncode != 0
    assert found == {}


LONG = "a" * 70000 + "@example.org"


def _size(text: str) -> int:
    """Return the text's size in UTF-8 bytes."""
    return len(text.encode("utf-8", "surrogatepass"))


def test_a_long_address_is_listed_and_named_nowhere_else(tmp_path: Path) -> None:
    """An address past 254 characters gets no command naming it.

    The body stays within the limit, counted in bytes.
    """
    ran, found, _ = _check(tmp_path, ["two\n"], author=LONG)

    assert ran.returncode == 0, ran.stderr
    assert found["failed"] == "true"
    body = _body(tmp_path)
    assert _size(body) <= _script().LIMIT
    assert LONG not in "\n".join(_outside(body))
    assert "longer than 254 characters" in body


def test_a_subject_of_wide_characters_is_bounded_in_bytes() -> None:
    """A character of four bytes counts four towards the limit."""
    script = _script()
    wide = chr(0x1F600) * 600
    lines = [f"{n:012} {wide}: no Signed-off-by: <a@b>" for n in range(200)]
    body = script.comment(lines, [], [], "f" * 40, "main")

    assert _size(body) <= script.LIMIT


HOSTILE = {
    "ping @mallory\n": "@mallory",
    "<!-- hide qqq\n": "qqq",
    "zzz --> end\n": "zzz",
    "::error::forged\n": "forged",
    "x ```` wbacktick\n": "wbacktick",
    "carriage\rreturn ``` text\n": "carriage",
    "first line\nsecond line of the subject\n": "second line",
    "line\u2028separator\u2029paragraph\n": "separator",
}


def _outside(body: str) -> list[str]:
    """Return the body's lines outside its one `text` block.

    The fence is longer than any backtick run inside the block.
    """
    lines = body.splitlines()
    (start,) = [n for n, s in enumerate(lines) if s.endswith("`text")]
    fence = lines[start].removesuffix("text")
    end = lines.index(fence, start + 1)
    assert set(fence) == {"`"}
    runs = re.findall("`+", "\n".join(lines[start + 1 : end]))
    assert len(fence) > max(map(len, runs), default=0)
    return lines[:start] + lines[end + 1 :]


def test_a_subject_stays_text_inside_the_code_block(tmp_path: Path) -> None:
    """A mention, an HTML comment, a workflow command or a fence is text.

    Each subject is on one line of the block, its control characters
    escaped, behind a fence longer than any backtick run in it, and
    nothing of it is outside the block. The marker is the one HTML
    comment outside it.
    """
    ran, found, _ = _check(tmp_path, list(HOSTILE))

    assert ran.returncode == 0, ran.stderr
    assert found["failed"] == "true"
    body = _body(tmp_path)
    assert not {"\r", "\u2028", "\u2029"} & set(body)
    outside = "\n".join(_outside(body))
    for word in HOSTILE.values():
        assert word in body
        assert word not in outside
    assert outside.count("<!--") == outside.count("-->") == 1
    assert outside.startswith(MARKER)
    assert "carriage\\rreturn" in body
    assert "first line second line of the subject" in body


def test_a_comment_past_github_s_limit_lists_what_fits() -> None:
    """The lines that fit are listed, and a last line counts the rest."""
    script = _script()
    lines = [f"{n:012} {'x' * 1000}: no Signed-off-by: <a@b>" for n in range(100)]
    body = script.comment(lines, [], [], "f" * 40, "main")

    assert _size(body) <= script.LIMIT
    shown = [s for s in body.splitlines() if s.endswith("<a@b>")]
    assert 0 < len(shown) < len(lines)
    assert f"and {len(lines) - len(shown)} more" in body.splitlines()
    assert len(script.comment(lines[:1], [], [], "f" * 40, "main")) < script.LIMIT


def test_the_caller_takes_a_completed_run_of_lint() -> None:
    """The trigger, and the permissions the calling job grants and no more."""
    (job,) = jobs(CALLER).values()

    assert triggers(CALLER) == {
        "workflow_run": {"workflows": ["lint"], "types": ["completed"]}
    }
    assert document(CALLER)["permissions"] == {"contents": "read"}
    assert job["uses"].startswith("./.github/workflows/reusable-sign-off-comment.yml")
    assert job["permissions"] == {"contents": "read", "pull-requests": "write"}
    assert job["cache-mode"] == "none"


def test_the_decline_sits_on_the_trigger() -> None:
    """The caller declines the finding on `workflow_run`, and nowhere else."""
    for workflow, wanted in ((CALLER, [DECLINE]), (WORKFLOW, [])):
        lines = workflow.read_text(encoding="utf-8").splitlines()
        assert [s for s in lines if "dangerous-triggers]" in s] == wanted


def test_each_job_holds_one_permission_beyond_reading_the_tree() -> None:
    """The job reading the commits writes nothing; the writer reads none."""
    found = jobs(WORKFLOW)

    assert triggers(WORKFLOW) == {"workflow_call": None}
    assert document(WORKFLOW)["permissions"] == {"contents": "read"}
    assert list(found) == ["check", "comment"]
    assert found["check"]["permissions"] == {
        "contents": "read",
        "pull-requests": "read",
    }
    assert found["comment"]["permissions"] == {"pull-requests": "write"}
    assert "github.event.workflow_run.event == 'pull_request'" in found["check"]["if"]
    assert found["comment"]["needs"] == "check"
    for job in found.values():
        assert job["cache-mode"] == "none"


def _runs(job: str) -> list[str]:
    """Return the `run:` of each step of a job."""
    return [s["run"] for s in jobs(WORKFLOW)[job]["steps"] if "run" in s]


def test_no_expression_reaches_a_shell() -> None:
    """Every value reaches a `run:` through `env:`."""
    for job in jobs(WORKFLOW):
        for run in _runs(job):
            assert "${{" not in run


def _strings(node: object) -> Iterator[tuple[object, str]]:
    """Yield each string a parsed workflow holds, with the key it is under.

    A key is yielded too, under None.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(key, str):
                yield None, key
            if isinstance(value, str):
                yield key, value
            else:
                yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            if isinstance(value, str):
                yield None, value
            else:
                yield from _strings(value)


def _expressions(text: str) -> set[str]:
    """Return every expression a workflow's text holds, its spaces folded.

    It is read from the text and from what YAML parses it to, since an
    escape in a quoted string spells `${{` only once parsed. An `if:` is
    an expression whole where `${{ }}` does not wrap it, a `${{` inside
    it included.
    """
    found = set(EXPRESSION.findall(text))
    for key, value in _strings(yaml.safe_load(text)):
        found |= set(EXPRESSION.findall(value))
        if key == "if":
            wrapped = re.fullmatch(r"\s*\$\{\{(.*)\}\}\s*", value, re.DOTALL)
            found.add(wrapped[1] if wrapped else value)
    return {" ".join(expression.split()) for expression in found}


def _refused(text: str) -> list[str]:
    """Return what a workflow holds beyond `ALLOWED`, and each event file named.

    The event file is the whole payload of the triggering run, so a
    `run:` reading it reads every field `TRUSTED` leaves out.
    """
    named = [EVENT_FILE.findall(text)]
    named += [EVENT_FILE.findall(s) for _, s in _strings(yaml.safe_load(text))]
    return [*sorted(_expressions(text) - ALLOWED), *(n for s in named for n in s)]


def test_the_run_is_read_for_the_fields_trusted_alone() -> None:
    """Every expression is one `ALLOWED` lists, and none names the event file.

    The run's conclusion, its artifacts and its names are the branch's
    to write, so neither workflow reads them, nor the script.
    """
    for workflow in (WORKFLOW, CALLER):
        assert _refused(workflow.read_text(encoding="utf-8")) == [], workflow.name
    assert _expressions(WORKFLOW.read_text(encoding="utf-8")) == ALLOWED
    assert _expressions(CALLER.read_text(encoding="utf-8")) == set()
    assert not EVENT_FILE.search(SCRIPT.read_text(encoding="utf-8"))
    assert "title" not in WORKFLOW.read_text(encoding="utf-8")
    assert "%an" not in SCRIPT.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("line", "hostile"),
    [
        (
            "    if: ${{ github.event.workflow_run.event == 'pull_request' }}\n",
            "    if: github['event'].workflow_run.conclusion == 'success'\n",
        ),
        (
            "          SCRIPT: standard/.github/scripts/check_sign_off.py\n",
            "          T: ${{ github['event']['workflow_run']['display_title'] }}\n",
        ),
        (
            "          SCRIPT: standard/.github/scripts/check_sign_off.py\n",
            "          T: ${{ github.Event.workflow_run.display_title }}\n",
        ),
        (
            "          SCRIPT: standard/.github/scripts/check_sign_off.py\n",
            '          T: "\\u0024{{ github.event.workflow_run.display_title }}"\n',
        ),
        (
            "          export GIT_NO_LAZY_FETCH=1\n",
            (
                "          jq -r .workflow_run.display_title"
                ' "${RUNNER_TEMP}/_github_workflow/event.json"\n'
            ),
        ),
    ],
    ids=["bracket in a bare if", "brackets", "case", "an escape", "the event file"],
)
def test_another_spelling_of_the_run_is_refused(line: str, hostile: str) -> None:
    """A field read by brackets, by case, by an escape or from the event file.

    `hostile` goes in where `line` is, or before it where `line` stays
    to be found.
    """
    text = WORKFLOW.read_text(encoding="utf-8")
    assert line in text
    kept = "" if line.lstrip().startswith("if:") else line
    changed = text.replace(line, hostile + kept, 1)

    assert yaml.safe_load(changed)
    assert _refused(changed)


def test_no_file_of_the_branch_is_checked_out_or_cached() -> None:
    """The one checkout is this repository's scripts, at the workflow's commit.

    The fetch asks for commit objects alone, with lazy fetching off, and
    the job that writes fetches nothing.
    """
    steps = [s for job in jobs(WORKFLOW).values() for s in job["steps"]]
    actions = [s["uses"].split("@")[0] for s in steps if "uses" in s]
    (checkout,) = [
        s for s in steps if s.get("uses", "").startswith("actions/checkout@")
    ]
    (uv,) = [s for s in steps if s.get("uses", "").startswith("astral-sh/setup-uv@")]
    (fetch,) = [run for run in _runs("check") if "git fetch" in run]

    assert "actions/cache" not in actions
    assert checkout["with"] == {
        "repository": "btclib-org/.github",
        "ref": "${{ job.workflow_sha }}",
        "path": "standard",
        "persist-credentials": False,
        "sparse-checkout": ".github/scripts",
    }
    assert uv["with"] == {"enable-cache": False}
    assert "--filter=tree:0" in fetch
    assert fetch.startswith("export GIT_NO_LAZY_FETCH=1\n")
    assert not [s for s in jobs(WORKFLOW)["comment"]["steps"] if "checkout" in str(s)]
    assert not [run for run in _runs("comment") if "git " in run]


def test_every_tree_comments_on_a_sign_off_it_refuses(
    repository: str,
    trees: dict[str, Path],
) -> None:
    """The tree's `sign-off-comment.yml` calls the reusable workflow.

    On a completed run of `lint`, with the comment's permission granted
    to the calling job. This tree calls it by path.

    :param repository: the repository asked about.
    :param trees: the checkouts.
    """
    path = trees[repository] / ".github" / "workflows" / CALLER.name
    listed = by_hand(repository, f"ls .github/workflows/{CALLER.name}")
    assert path.is_file(), f"{repository} has no {CALLER.name}; {listed}"
    calls = [
        job
        for job in jobs(path).values()
        if calls_here(str(job.get("uses", "")), WORKFLOW.name)
        or (
            repository == SELF
            and str(job.get("uses", "")).startswith(
                tuple(f"{p}.github/workflows/{WORKFLOW.name}" for p in LOCAL)
            )
        )
    ]
    assert triggers(path) == triggers(CALLER)
    assert [job.get("permissions") for job in calls] == [
        {"contents": "read", "pull-requests": "write"}
    ]
