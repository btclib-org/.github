# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What keeps `reusable-claude-implement.yml` within section 10's rule.

The rule is section 10's, and the workflow's header says how the file
keeps it. These tests read that configuration: the scopes each token is
asked for, the agent's allow list and the job that runs the agent's
edit. The scripts `comment`, `label`, `check-admission` and
`check-message`, the command running the gates and the step committing
the edit are read out of the workflow and run here, the scripts against
a stand-in `gh`, so what is asked is what the runner writes.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any

import pytest

from . import ROOT
from .workflows_test import jobs

# the reusable workflow, which holds the jobs and their scripts
WORKFLOW = ROOT / ".github/workflows/reusable-claude-implement.yml"

# the jobs that run the agent
AGENTS = ("assess", "implement")

# the scripts' exit status for arguments they refuse
REFUSED = 2

# what the step writes beside the scripts: the number and the repository
TARGET = "7 o/r\n"

# the keys the action requests at their default, `write`, unless listed
DEFAULTS = {"contents", "issues", "pull_requests"}

# the one Bash rule shape an agent gets: a script of its job's directory
SCRIPT_RULE = re.compile(r"^Bash\(\$\{\{ runner\.temp \}\}/claude-(\w+)/(\w+):\*\)$")


def action(job: str) -> dict[str, str]:
    """Read the `with:` of a job's claude-code-action step.

    :param job: the job's id.
    :returns: the step's inputs.
    """
    found: list[dict[str, str]] = [
        step["with"]
        for step in jobs(WORKFLOW)[job]["steps"]
        if step.get("uses", "").startswith("anthropics/claude-code-action@")
    ]
    (inputs,) = found
    return inputs


def tools(job: str, flag: str) -> list[str]:
    """Read the rules after one flag of a job's `claude_args`.

    :param job: the job's id.
    :param flag: `--allowedTools` or `--disallowedTools`.
    :returns: the rules, up to the next flag.
    """
    args = shlex.split(action(job)["claude_args"])
    rules: list[str] = []
    for arg in args[args.index(flag) + 1 :]:
        if arg.startswith("--"):
            break
        rules.append(arg)
    return rules


def scripts(job: str) -> dict[str, str]:
    """Read the scripts a job writes, by name, out of its heredocs.

    :param job: the job's id.
    :returns: each script's text.
    """
    found = {}
    for step in jobs(WORKFLOW)[job]["steps"]:
        run = step.get("run", "")
        for match in re.finditer(r'cat > "\$DIR/([\w-]+)" <<\'SCRIPT\'\n', run):
            found[match[1]] = run[match.end() :].split("\nSCRIPT\n", 1)[0] + "\n"
    return found


@pytest.mark.parametrize("job", AGENTS)
def test_the_agent_s_token_lists_every_default_and_cannot_push(job: str) -> None:
    """Each default is named, and `contents` is read-only.

    A key left out keeps the action's `write`.

    :param job: the job's id.
    """
    listed: dict[str, str] = {}
    for line in action(job)["additional_permissions"].splitlines():
        if line.strip():
            key, value = line.split(":", 1)
            listed[key.strip()] = value.strip()
    assert set(listed) == DEFAULTS
    assert listed["contents"] == "read"


def test_the_published_token_is_asked_for_no_workflows_scope() -> None:
    """`publish` asks for contents and pull requests, nothing more."""
    (run,) = [
        step["run"]
        for step in jobs(WORKFLOW)["publish"]["steps"]
        if "github-app-token-exchange" in step.get("run", "")
    ]
    assert '{"permissions": {"contents": "write", "pull_requests": "write"}}' in run


@pytest.mark.parametrize("job", AGENTS)
def test_the_agent_runs_nothing_but_its_job_s_scripts(job: str) -> None:
    """Every Bash rule names a script of the job's own directory.

    :param job: the job's id.
    """
    rules = [rule for rule in tools(job, "--allowedTools") if rule.startswith("Bash")]
    assert rules
    for rule in rules:
        found = SCRIPT_RULE.match(rule)
        assert found, rule
        assert found[1] == job
        assert found[2] in scripts(job)


def test_the_editing_agent_is_kept_out_of_git() -> None:
    """Edit and Write are denied `.git/`, a deny winning over an allow."""
    assert {"Edit(./.git/**)", "Write(./.git/**)"} <= set(
        tools("implement", "--disallowedTools")
    )


def test_the_job_running_the_edit_asks_for_no_secret_and_no_oidc_token() -> None:
    """`gates` reads the tree, names no secret, and uploads nothing."""
    job: dict[str, Any] = jobs(WORKFLOW)["gates"]
    assert job["permissions"] == {"contents": "read"}
    assert "secrets." not in str(job)
    assert not [
        step for step in job["steps"] if "upload-artifact" in step.get("uses", "")
    ]


def test_no_job_runs_again_on_a_re_run() -> None:
    """Each job's condition holds `github.run_attempt == 1`.

    The header says a re-run is refused, and "Re-run failed jobs" can re-run
    any job.
    """
    for name, job in jobs(WORKFLOW).items():
        assert "github.run_attempt == 1" in job["if"], name


def test_a_job_behind_a_skipped_one_still_runs() -> None:
    """Each job with `needs:` opens with `!cancelled()` and reads each result.

    Without a status function, a skipped `assess` skips every job behind
    it, whatever their conditions say.
    """
    for name, job in jobs(WORKFLOW).items():
        needs = job.get("needs", [])
        for needed in [needs] if isinstance(needs, str) else needs:
            assert job["if"].startswith("${{ !cancelled()"), name
            assert f"needs.{needed}.result" in job["if"], (name, needed)


def test_no_step_hides_a_failed_gh_call_in_a_pipe() -> None:
    """A `gh` or `curl` call is never piped on or excused with `|| true`.

    The steps run without `pipefail`, so a pipe would carry on past a
    failed call with an empty answer.
    """
    for name, job in jobs(WORKFLOW).items():
        for step in job["steps"]:
            for line in commands(step.get("run", "")):
                unquoted = re.sub(r"'[^']*'", "''", line)
                for call in re.finditer(r"(^|[\s(])(gh|curl)\s", unquoted):
                    rest = unquoted[call.end() :]
                    assert not re.search(r"(?<!\|)\|(?!\|)", rest), (name, line)
                    assert "|| true" not in rest, (name, line)


def waiting() -> list[str]:
    """Read the labels that say why an issue waits, from the label script.

    :returns: the labels.
    """
    script = scripts("assess")["label"]
    (case,) = re.findall(r"^\s*([\w|-]+)\) ;;$", script, re.MULTILINE)
    labels: list[str] = str(case).split("|")
    return labels


def test_implement_starts_on_no_issue_that_waits() -> None:
    """Its condition, on every path, refuses each label saying an issue waits.

    The removal of `decision` skips `assess`, which reads the labels on the
    other path.
    """
    condition = jobs(WORKFLOW)["implement"]["if"]
    head = condition.split("&& (needs.assess", 1)[0]
    assert waiting() == ["decision", "needs-hardware", "needs-maintainer"]
    for label in waiting():
        assert f"!contains(github.event.issue.labels.*.name, '{label}')" in head


def test_the_gates_run_as_a_user_of_their_own() -> None:
    """The one step running the caller's gates runs them through `sudo -u`.

    `env -i` hands that user none of the runner's variables.
    """
    (run,) = [
        step["run"]
        for step in jobs(WORKFLOW)["gates"]["steps"]
        if "gates.sh" in step.get("run", "")
    ]
    assert "sudo useradd --create-home --shell /bin/bash claude-gates" in run
    command = gates_command(run)
    assert command.startswith(DROP), command
    lines = commands(run)
    (probe,) = [
        index
        for index, line in enumerate(lines)
        if line.startswith(DROP) and "/home/claude-gates/probe " in line
    ]
    assert probe < lines.index(command)


# how the step drops to the gates' user, with none of the runner's variables
DROP = "sudo -u claude-gates -H env -i "


def commands(run: str) -> list[str]:
    """Read a step's script as commands, each continuation joined.

    :param run: the step's script.
    :returns: its lines, a command on each.
    """
    return [line.strip() for line in re.sub(r"\\\n\s*", " ", run).splitlines()]


def gates_command(run: str) -> str:
    """Read the one command that runs `gates.sh`, its continuations joined.

    :param run: the step's script.
    :returns: the command, on one line.
    """
    (command,) = [
        line for line in commands(run) if "bash -e /home/claude-gates/gates.sh" in line
    ]
    return command


def test_the_gates_command_reader_sees_a_dropped_privilege_drop() -> None:
    """The mutation the check exists for: the same command without `sudo -u`."""
    mutated = (
        "sudo -u claude-gates -H env -i /home/claude-gates/probe\n"
        'bash -c "cd /home/claude-gates/tree && git add -A \\\n'
        '  && bash -e /home/claude-gates/gates.sh"\n'
    )
    assert not gates_command(mutated).startswith("sudo -u claude-gates")


def test_the_probe_asks_for_each_thing_the_gates_user_must_not_reach() -> None:
    """The runner's home, the docker socket, other users' environ, sudo."""
    (run,) = [
        step["run"]
        for step in jobs(WORKFLOW)["gates"]["steps"]
        if "gates.sh" in step.get("run", "")
    ]
    probe = run.split("<<'SCRIPT'\n", 1)[1].split("\nSCRIPT\n", 1)[0]
    for asked in ("/home/runner", "docker.sock", "/proc/", "sudo -n true"):
        assert asked in probe, asked
    assert "usermod" not in run
    assert "sudoers" not in run


@pytest.fixture
def bench(tmp_path: Path) -> Path:
    """Make a stand-in for `gh` that records its arguments.

    :param tmp_path: a directory of this test's own.
    :returns: the directory, first on the path the scripts run with.
    """
    stand_in = tmp_path / "gh"
    stand_in.write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" > {tmp_path}/gh.argv\n')
    stand_in.chmod(0o755)
    (tmp_path / "target").write_text(TARGET)
    return tmp_path


def run(
    bench: Path, job: str, name: str, *args: str
) -> subprocess.CompletedProcess[str]:
    """Write one of a job's scripts beside the stand-in and run it.

    :param bench: the stand-in's directory.
    :param job: the job whose script runs.
    :param name: the script's name.
    :param args: its arguments.
    :returns: the finished process.
    """
    script = bench / name
    script.write_text(scripts(job)[name])
    script.chmod(0o755)
    env = {**os.environ, "PATH": f"{bench}:{os.environ['PATH']}"}
    return subprocess.run(
        [str(script), *args],
        input="body\n",
        capture_output=True,
        encoding="utf-8",
        check=False,
        env=env,
    )


def recorded(bench: Path) -> list[str] | None:
    """Read what the stand-in was called with.

    :param bench: the stand-in's directory.
    :returns: its arguments, or None where it never ran.
    """
    argv = bench / "gh.argv"
    return argv.read_text().splitlines() if argv.exists() else None


@pytest.mark.parametrize("job", AGENTS)
def test_each_agent_job_writes_its_scripts(job: str) -> None:
    """A comment and a label for the agent, and the anchor for the step.

    :param job: the job's id.
    """
    assert set(scripts(job)) == {"comment", "label", "check-admission"}
    assert not [
        rule for rule in tools(job, "--allowedTools") if "check-admission" in rule
    ]


def test_publish_checks_the_admission_and_the_message() -> None:
    """The admission is read again where the edit is published."""
    assert set(scripts("publish")) == {"check-admission", "check-message"}


def test_the_agent_can_write_its_message_after_the_setup(tmp_path: Path) -> None:
    """The message's directory is made writable, outside the locked one.

    :param tmp_path: stands in for the runner's temporary directory.
    """
    steps = jobs(WORKFLOW)["implement"]["steps"]
    (make,) = [step for step in steps if "MESSAGE" in step.get("env", {})]
    message = make["env"]["MESSAGE"].replace("${{ runner.temp }}", str(tmp_path))
    locked = "${{ runner.temp }}/claude-implement"
    assert not make["env"]["MESSAGE"].startswith(locked + "/")
    (tmp_path / "claude-implement").mkdir(mode=0o555)
    subprocess.run(
        ["bash", "-e", "-c", make["run"]],
        env={**os.environ, "MESSAGE": message},
        check=True,
    )
    (Path(message) / "message").write_text("Do it (closes #7)\n")
    assert (Path(message) / "message").read_text() == "Do it (closes #7)\n"
    rule = "Write(/${{ runner.temp }}/claude-implement-message/message)"
    assert rule in tools("implement", "--allowedTools")


@pytest.mark.parametrize("job", AGENTS)
@pytest.mark.parametrize("label", ["decision", "needs-hardware", "needs-maintainer"])
def test_the_label_script_applies_a_label_that_says_why_an_issue_waits(
    bench: Path, job: str, label: str
) -> None:
    """A label saying why an issue waits reaches `gh issue edit`, no more.

    :param bench: the stand-in's directory.
    :param job: the job whose script runs.
    :param label: the label asked for.
    """
    done = run(bench, job, "label", label)
    assert done.returncode == 0, done.stderr
    assert recorded(bench) == ["issue", "edit", "7", "-R", "o/r", "--add-label", label]


@pytest.mark.parametrize("job", AGENTS)
@pytest.mark.parametrize(
    "args",
    [
        pytest.param([], id="no argument"),
        pytest.param(["agent"], id="agent"),
        pytest.param(["security"], id="another label"),
        pytest.param(["decision", "agent"], id="two"),
        pytest.param(["decision,agent"], id="a list"),
        pytest.param(["--remove-label"], id="a flag"),
    ],
)
def test_the_label_script_refuses_any_other(
    bench: Path, job: str, args: list[str]
) -> None:
    """Anything else is refused, status 2, `gh` unrun.

    :param bench: the stand-in's directory.
    :param job: the job whose script runs.
    :param args: the arguments.
    """
    done = run(bench, job, "label", *args)
    assert done.returncode == REFUSED
    assert done.stderr.startswith("label: "), done.stderr
    assert recorded(bench) is None


@pytest.mark.parametrize("job", AGENTS)
def test_the_comment_script_posts_on_the_issue_from_standard_input(
    bench: Path, job: str
) -> None:
    """No argument; the body is read by `gh` from standard input.

    :param bench: the stand-in's directory.
    :param job: the job whose script runs.
    """
    done = run(bench, job, "comment", "--edit-last")
    assert done.returncode == REFUSED
    assert done.stderr == "comment: takes no argument\n", done.stderr
    assert recorded(bench) is None
    done = run(bench, job, "comment")
    assert done.returncode == 0, done.stderr
    assert recorded(bench) == ["issue", "comment", "7", "-R", "o/r", "--body-file", "-"]


def check(
    bench: Path, message: str, number: str = "7"
) -> subprocess.CompletedProcess[str]:
    """Run `publish`'s message check on a message.

    :param bench: the stand-in's directory.
    :param message: the message, on standard input.
    :param number: the issue's number, as the argument.
    :returns: the finished process.
    """
    script = bench / "check-message"
    script.write_text(scripts("publish")["check-message"])
    script.chmod(0o755)
    return subprocess.run(
        [str(script), number],
        input=message,
        capture_output=True,
        encoding="utf-8",
        check=False,
    )


@pytest.mark.parametrize(
    "message",
    [
        "Do the thing (closes #7)\n",
        "Do the thing (closes #7)\n\nIt fixes the parser, see #8.\n",
        "Do the thing (closes #7)\n\nMail me at a@b.org.\n",
        "Do the thing (closes #7)\n\nMail first.last@b.org instead.\n",
        "Do the thing (closes #7)\n\nThe parser is used by: the CLI.\n",
        "Do the thing (closes #7)\n\nThe node waits on stand-by: idle.\n",
    ],
)
def test_the_message_check_passes_the_issue_s_own_citation(
    bench: Path, message: str
) -> None:
    """The subject's own `(closes #7)`, a bare reference, an address.

    :param bench: the stand-in's directory.
    :param message: the message.
    """
    done = check(bench, message)
    assert done.returncode == 0, done.stdout + done.stderr


@pytest.mark.parametrize(
    "message",
    [
        pytest.param("Do the thing\n", id="no citation"),
        pytest.param("Do the thing (closes #8)\n", id="another issue"),
        pytest.param("Do it (closes #7)\n\nCloses #8\n", id="body keyword"),
        pytest.param("Do it (closes #7)\n\nfixes: o/r#3\n", id="qualified"),
        pytest.param("Do it (closes #7)\n\nFixes o/r#8\n", id="same line"),
        pytest.param("Do it (closes #7)\n\nFixes\no/r#8\n", id="across lines"),
        pytest.param("Do it (closes #7)\n\nCloses\n\n#8\n", id="across a blank line"),
        pytest.param(
            "Do it (closes #7)\n\nResolves https://github.com/o/r/issues/3\n",
            id="url",
        ),
        pytest.param("Do it (closes #7) fixes #9 (closes #7)\n", id="in subject"),
        pytest.param("Do it (closes #7)\n\nThanks @someone\n", id="mention"),
        pytest.param("Do it (closes #7)\n\nsee .@someone\n", id="after a dot"),
        pytest.param("Do it (closes #7)\n\nx-@someone\n", id="after a hyphen"),
        pytest.param("Do it (closes #7)\n\n@someone\n", id="line start"),
        pytest.param("Do it (closes #7)\n\ncafé@someone\n", id="after an accent"),
        pytest.param("Do it (closes #7)\n\n見@someone\n", id="after a CJK letter"),
        pytest.param("Do it (closes #7)\n\nThanks _@octocat_\n", id="emphasis"),
        pytest.param("Do it (closes #7)\n\nIt _fixes #8_ too\n", id="keyword emphasis"),
        pytest.param("Do it (closes #7)\nand more\n\nbody\n", id="subject runs on"),
        pytest.param("Do it (closes #7)\n \nbody\n", id="spaces on line two"),
        pytest.param(
            "Do it (closes #7)\n\nCo-authored-by: A <a@b.org>\n", id="co-author"
        ),
        pytest.param(
            "Do it (closes #7)\n\nSigned-off-by: A <a@b.org>\n", id="sign-off"
        ),
        pytest.param("Do it (closes #7)\n\nreviewed-by : A\n", id="any -by: trailer"),
        pytest.param(
            "Do it (closes #7)\n\n  Co-authored-by: A <a@b.org>\n", id="indented"
        ),
        pytest.param(
            "Do it (closes #7)\n\n\tCo-authored-by: A <a@b.org>\n", id="tab-indented"
        ),
    ],
)
def test_the_message_check_refuses_any_other_closing_or_mention(
    bench: Path, message: str
) -> None:
    """Any other closing reference, a mention, a `-by:` trailer, a long subject.

    :param bench: the stand-in's directory.
    :param message: the message.
    """
    done = check(bench, message)
    assert done.returncode == 1
    # one of the check's own refusals, not a failure of the script
    refusal = re.compile(r"^check-message: (the|a) ", re.MULTILINE)
    assert refusal.search(done.stderr), done.stderr


@pytest.mark.parametrize("number", ["", "7a", "$(id)"])
def test_the_message_check_takes_a_number(bench: Path, number: str) -> None:
    """The argument is digits or the check refuses to run.

    :param bench: the stand-in's directory.
    :param number: the argument.
    """
    done = check(bench, "Do the thing (closes #7)\n", number)
    assert done.returncode == REFUSED
    assert done.stderr == "check-message: not a number\n", done.stderr


# a stand-in `gh` for `check-admission`: the events, the labels and the
# last edit from files beside it, and a permission for the logins it
# names, any other answering as GitHub does for a bot or a deleted account
ADMISSION_GH = """#!/bin/sh
here=${0%/*}
case $2 in
  repos/o/r/issues/7/events)
    [ -f "$here/events.json" ] || { echo "gh: HTTP 502" >&2; exit 1; }
    cat "$here/events.json" ;;
  repos/o/r/issues/7/labels)
    [ -f "$here/labels.txt" ] || { echo "gh: HTTP 502" >&2; exit 1; }
    cat "$here/labels.txt" ;;
  repos/o/r/collaborators/admin1/permission) echo admin ;;
  repos/o/r/collaborators/writer/permission) echo write ;;
  graphql)
    [ -f "$here/edited.txt" ] || { echo "gh: HTTP 502" >&2; exit 1; }
    cat "$here/edited.txt" ;;
  *) echo "gh: Not Found (HTTP 404)" >&2; exit 1 ;;
esac
"""

T0 = "2026-11-03T10:00:00Z"
T1 = "2026-11-03T10:00:01Z"
T_BEFORE = "2026-11-03T09:59:59Z"


def event(kind: str, login: str | None, at: str) -> dict[str, Any]:
    """Make one `agent` label event, or a rename where the kind says so.

    :param kind: `labeled`, `unlabeled` or `renamed`.
    :param login: the actor's login, None for a deleted account.
    :param at: the event's time.
    :returns: the event, as the API gives it.
    """
    actor = None if login is None else {"login": login}
    return {"event": kind, "label": {"name": "agent"}, "actor": actor, "created_at": at}


ADMIN = event("labeled", "admin1", T0)


@pytest.mark.parametrize(
    ("events", "labels", "edited", "expected"),
    [
        pytest.param([ADMIN], "agent", "", 0, id="admitted"),
        pytest.param(
            [ADMIN, event("labeled", "claude[bot]", T1)],
            "agent",
            "",
            0,
            id="a bot after",
        ),
        pytest.param(
            [ADMIN, event("labeled", None, T1)], "agent", "", 0, id="ghost after"
        ),
        pytest.param(
            [ADMIN, event("labeled", "writer", T1)], "agent", "", 0, id="a writer after"
        ),
        pytest.param([ADMIN], "agent", T_BEFORE, 0, id="edited before"),
        pytest.param([ADMIN], "agent", T0, 1, id="edited in the same second"),
        pytest.param([ADMIN], "agent", T1, 1, id="edited after"),
        pytest.param(
            [ADMIN, event("renamed", "someone", T1)], "agent", "", 1, id="renamed after"
        ),
        pytest.param(
            [ADMIN, event("unlabeled", "writer", T1)], "", "", 1, id="withdrawn"
        ),
        pytest.param(
            [
                ADMIN,
                event("unlabeled", "writer", T1),
                event("labeled", "writer", "2026-11-03T10:00:02Z"),
            ],
            "agent",
            "",
            1,
            id="withdrawn and relabelled by a writer",
        ),
        pytest.param([ADMIN], "", "", 1, id="label gone"),
        pytest.param([ADMIN], "agent-x", "", 1, id="a longer label"),
        pytest.param([event("labeled", "writer", T0)], "agent", "", 1, id="no admin"),
        pytest.param([], "", "", 1, id="never labelled"),
    ],
)
def test_the_admission_covers_the_issue_until_withdrawn_or_edited(
    tmp_path: Path,
    events: list[dict[str, Any]],
    labels: str,
    edited: str,
    expected: int,
) -> None:
    """An administrator's label, still carried, and nothing changed since.

    :param tmp_path: a directory of this test's own.
    :param events: the issue's events, one page.
    :param labels: the labels the issue carries now, one per line.
    :param edited: the body's last edit, empty where never edited.
    :param expected: the exit status.
    """
    (tmp_path / "events.json").write_text(json.dumps([events]))
    (tmp_path / "labels.txt").write_text(labels + "\n" if labels else "")
    (tmp_path / "edited.txt").write_text(edited + "\n")
    done = admission(tmp_path)
    assert done.returncode == expected, done.stdout + done.stderr
    # a refusal is the script's own, with its reason, not a failed call
    assert ("::error::#7: " in done.stdout) == bool(expected), done.stdout


@pytest.mark.parametrize("missing", ["events.json", "labels.txt", "edited.txt"])
def test_the_admission_fails_where_the_api_cannot_be_read(
    tmp_path: Path, missing: str
) -> None:
    """A failed call is an error, not an answer: no refusal stands in for it.

    :param tmp_path: a directory of this test's own.
    :param missing: the answer the stand-in fails to give.
    """
    (tmp_path / "events.json").write_text(json.dumps([[ADMIN]]))
    (tmp_path / "labels.txt").write_text("agent\n")
    (tmp_path / "edited.txt").write_text("\n")
    (tmp_path / missing).unlink()
    done = admission(tmp_path)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "::error::" not in done.stdout, done.stdout
    assert "gh: HTTP 502" in done.stderr, done.stderr


def admission(bench: Path) -> subprocess.CompletedProcess[str]:
    """Run `check-admission` against the stand-in.

    :param bench: where the stand-in and its answers go.
    :returns: the finished process.
    """
    stand_in = bench / "gh"
    stand_in.write_text(ADMISSION_GH)
    stand_in.chmod(0o755)
    script = bench / "check-admission"
    script.write_text(scripts("assess")["check-admission"])
    script.chmod(0o755)
    env = {**os.environ, "PATH": f"{bench}:{os.environ['PATH']}"}
    return subprocess.run(
        [str(script), "o/r", "7"],
        capture_output=True,
        encoding="utf-8",
        check=False,
        env=env,
    )


def gated(tree: Path, gates: str) -> subprocess.CompletedProcess[str]:
    """Stage a tree as the runner does, then run the gates' user's command.

    The runner's `git add -A` is the unpack step's; what the gates' user
    then runs is the command the workflow gives it, its paths pointed here.

    :param tree: a git checkout holding the edit, unstaged.
    :param gates: the gates' script.
    :returns: the finished command.
    """
    subprocess.run(["git", "-C", str(tree), "add", "-A"], check=True)
    (tree.parent / "gates.sh").write_text(gates)
    (run,) = [
        step["run"]
        for step in jobs(WORKFLOW)["gates"]["steps"]
        if "gates.sh" in step.get("run", "")
    ]
    inner = gates_command(run).split('bash -c "', 1)[1].rsplit('"', 1)[0]
    inner = inner.replace("/home/claude-gates/tree", str(tree))
    inner = inner.replace("/home/claude-gates/gates.sh", str(tree.parent / "gates.sh"))
    return subprocess.run(
        ["bash", "-c", inner], capture_output=True, encoding="utf-8", check=False
    )


@pytest.mark.parametrize(("ignored", "expected"), [("", 0), ("dep.py\n", 1)])
def test_the_gates_run_on_the_files_the_commit_holds(
    tmp_path: Path, ignored: str, expected: int
) -> None:
    """A dependency `.gitignore` keeps out of the commit is gone for the gates.

    :param tmp_path: a directory of this test's own.
    :param ignored: the tree's `.gitignore`, naming the new dependency or not.
    :param expected: the gates' exit status.
    """
    tree = tmp_path / "tree"
    tree.mkdir()
    subprocess.run(["git", "-C", str(tree), "init", "-q"], check=True)
    (tree / ".gitignore").write_text(ignored)
    (tree / "uses.py").write_text("import dep\n")
    (tree / "dep.py").write_text("")
    done = gated(tree, f"cd {tree} && python3 -c 'import uses'\n")
    assert done.returncode == expected, done.stderr
    assert ("No module named 'dep'" in done.stderr) == bool(expected), done.stderr


def test_publish_commits_only_the_tree_the_gates_ran_on() -> None:
    """The commit step compares its index with the tree `gates` recorded."""
    (step,) = [
        step
        for step in jobs(WORKFLOW)["publish"]["steps"]
        if "commit -q -s" in step.get("run", "")
    ]
    assert step["env"]["GATED"] == "${{ needs.gates.outputs.tree }}"
    assert '"$(git write-tree)" != "$GATED"' in step["run"]


def committed(
    tree: Path, edit: str | None, name: str = ".coderabbit.yaml"
) -> subprocess.CompletedProcess[str]:
    """Stage an edit and run `publish`'s commit step on it, `commit` stubbed.

    :param tree: a git checkout holding `.coderabbit.yaml` at HEAD.
    :param edit: the new text of the file named, None to leave it.
    :param name: the file the edit writes.
    :returns: the finished step.
    """
    (tree / "other.txt").write_text("an edit\n")
    if edit is not None:
        (tree / name).write_text(edit)
    subprocess.run(["git", "-C", str(tree), "add", "-A"], check=True)
    gated = subprocess.run(
        ["git", "-C", str(tree), "write-tree"],
        capture_output=True,
        encoding="utf-8",
        check=True,
    ).stdout.strip()
    (step,) = [
        step
        for step in jobs(WORKFLOW)["publish"]["steps"]
        if "commit -q -s" in step.get("run", "")
    ]
    run = step["run"].split("git -c user.name=", 1)[0] + "echo committed\n"
    return subprocess.run(
        ["bash", "-e", "-c", run],
        cwd=tree,
        env={**os.environ, "BRANCH": "claude/issue-7", "GATED": gated},
        capture_output=True,
        encoding="utf-8",
        check=False,
    )


def coderabbit_tree(tmp_path: Path) -> Path:
    """Make a checkout whose HEAD holds a `.coderabbit.yaml`.

    :param tmp_path: a directory of this test's own.
    :returns: the checkout.
    """
    tree = tmp_path / "tree"
    tree.mkdir()
    git = ["git", "-C", str(tree)]
    subprocess.run([*git, "init", "-q"], check=True)
    (tree / ".coderabbit.yaml").write_text("reviews:\n  auto_approve: false\n")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run(
        [*git, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"],
        check=True,
    )
    return tree


def test_publish_commits_an_edit_that_leaves_coderabbit_alone(tmp_path: Path) -> None:
    """The control: an edit elsewhere reaches the commit.

    :param tmp_path: a directory of this test's own.
    """
    done = committed(coderabbit_tree(tmp_path), None)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "committed" in done.stdout


@pytest.mark.parametrize(
    "name", [".coderabbit.yaml", ".coderabbit.yml", ".CodeRabbit.yml"]
)
def test_publish_refuses_an_edit_to_coderabbit(tmp_path: Path, name: str) -> None:
    """A staged `.coderabbit.yaml` or `.coderabbit.yml`, any case, stops it.

    :param tmp_path: a directory of this test's own.
    :param name: the file the edit writes.
    """
    tree = coderabbit_tree(tmp_path)
    done = committed(tree, "reviews:\n  auto_approve: true\n", name)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "CodeRabbit's configuration" in done.stdout
    assert "committed" not in done.stdout
