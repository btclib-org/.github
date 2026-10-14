# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""The review's one read-only `gh api`, and the rule that admits it.

`reusable-claude-review.yml` gives the review a script, `gh-get`, in place
of `Bash(gh api ...)`: a pattern cannot refuse a `--method POST` written
after the path, and the script can. The script is read out of the
workflow and run here against a stand-in `gh`, so what is asked is the
script the runner writes and not a copy of it.

The allow rule is read as text, since what admits the script is Claude
Code's own matching, measured in the workflow's header.
"""

from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

import pytest

from . import ROOT
from .workflows_test import steps

if TYPE_CHECKING:
    from pathlib import Path

# the reusable review, which holds the script and the allow list
WORKFLOW = ROOT / ".github/workflows/reusable-claude-review.yml"

# a blob's name: 40 lowercase hex digits
SHA = "0123456789abcdef0123456789abcdef01234567"

BLOB = f"o/r/git/blobs/{SHA}"
FILE = "o/r/contents/src/a.py"


def script_text() -> str:
    """Read the `gh-get` script out of the step that writes it.

    :returns: the body of the heredoc.
    """
    (run,) = [
        step["run"] for step in steps(WORKFLOW) if "<<'SCRIPT'" in step.get("run", "")
    ]
    body: str = run.split("<<'SCRIPT'\n", 1)[1]
    return body.split("\nSCRIPT\n", 1)[0] + "\n"


@pytest.fixture
def gh_get(tmp_path: Path) -> tuple[Path, Path]:
    """Write the script beside a stand-in `gh` that records its arguments.

    :param tmp_path: a directory of this test's own.
    :returns: the script and the file the stand-in writes its arguments to.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    record = tmp_path / "argv"
    stand_in = bin_dir / "gh"
    stand_in.write_text(f'#!/bin/sh\nprintf "%s\\n" "$@" > {record}\n')
    stand_in.chmod(0o755)
    script = bin_dir / "gh-get"
    script.write_text(script_text())
    script.chmod(0o755)
    return script, record


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run the script with the stand-in `gh` first on the path.

    :param script: the script.
    :param args: its arguments.
    :returns: the finished process.
    """
    env = {**os.environ, "PATH": f"{script.parent}:{os.environ['PATH']}"}
    return subprocess.run(
        ["/bin/sh", str(script), *args],
        capture_output=True,
        encoding="utf-8",
        check=False,
        env=env,
    )


@pytest.mark.parametrize(
    "arg",
    [
        BLOB,
        FILE,
        "btclib-org/.github/contents/.github/workflows/test.yml",
        "o/r/contents/README.md?ref=main",
        (
            "C2SP/wycheproof/contents/testvectors_v1/ecdsa_secp256k1_sha256_test.json"
            "?ref=0123456789abcdef"
        ),
        "a-b/c.d_e/contents/x/y-z.txt?ref=refs/heads/a-b",
    ],
)
def test_it_reads_a_blob_or_a_file_with_a_get_and_nothing_else(
    gh_get: tuple[Path, Path],
    arg: str,
) -> None:
    """An accepted argument reaches `gh` as a GET after `--`, and as no more."""
    script, record = gh_get
    done = run(script, arg)
    assert done.returncode == 0, done.stderr
    assert record.read_text().splitlines() == [
        "api",
        "--method",
        "GET",
        "-H",
        "Accept: application/vnd.github.raw+json",
        "--",
        f"repos/{arg}",
    ]


@pytest.mark.parametrize(
    "args",
    [
        pytest.param([BLOB, "-X", "POST"], id="trailing -X POST"),
        pytest.param([BLOB, "--method", "POST"], id="trailing --method"),
        pytest.param([FILE, "--method=DELETE"], id="trailing --method="),
        pytest.param([BLOB, "-f", "a=b"], id="trailing -f"),
        pytest.param([BLOB, "-F", "a=b"], id="trailing -F"),
        pytest.param([BLOB, "--input", "f"], id="trailing --input"),
        pytest.param(["-X", "POST", BLOB], id="leading -X"),
        pytest.param(["--method=POST"], id="leading option"),
        pytest.param(["-H"], id="leading -H"),
        pytest.param([f"-{BLOB}"], id="leading hyphen on the path"),
        pytest.param([BLOB, FILE], id="second argument"),
        pytest.param([], id="no argument"),
        pytest.param([""], id="empty argument"),
        pytest.param([f"{BLOB} -X POST"], id="flags inside the argument"),
        pytest.param([f"{BLOB};gh"], id="semicolon"),
        pytest.param(["o/r/contents/$(id)"], id="substitution"),
        pytest.param(["o/r/contents/a\nb"], id="newline"),
        pytest.param(["o/r/contents/../../../orgs/x"], id="dot dot"),
        pytest.param(["o/r/contents/a..b"], id="two dots in a name"),
        pytest.param(["o/r/issues"], id="other path"),
        pytest.param(["o/r/issues/1/comments"], id="other path, deeper"),
        pytest.param(["o/r/git/trees/" + SHA], id="trees"),
        pytest.param(["o/r/git/blobs"], id="blobs without a sha"),
        pytest.param([f"o/r/git/blobs/{SHA[:39]}"], id="short sha"),
        pytest.param([f"o/r/git/blobs/{SHA}0"], id="long sha"),
        pytest.param([f"o/r/git/blobs/{SHA.upper()}"], id="upper case sha"),
        pytest.param([f"o/r/git/blobs/{SHA}?x=y"], id="query on a blob"),
        pytest.param(["o/r/contents/"], id="empty path"),
        pytest.param(["o/r/contents/?ref=main"], id="query, no path"),
        pytest.param(["o/r/contents/a?ref="], id="empty ref"),
        pytest.param(["o/r/contents/a?ref=b&x=y"], id="second query field"),
        pytest.param(["o/r/contents/a?x=y"], id="other query"),
        pytest.param(["o/r/contents/a?ref=b?c"], id="second question mark"),
        pytest.param(["o/r/contents/a=b"], id="equals in a path"),
        pytest.param(["orgs/o"], id="no repository"),
        pytest.param(["o"], id="owner alone"),
        pytest.param(["/r/contents/a"], id="empty owner"),
        pytest.param(["o//contents/a"], id="empty repository"),
        pytest.param(["./r/contents/a"], id="owner a dot"),
        pytest.param(["o/./contents/a"], id="repository a dot"),
        pytest.param(["repos/o/r/contents/a"], id="repos prefix"),
        pytest.param(["https://api.github.com/repos/o/r/contents/a"], id="a url"),
    ],
)
def test_it_refuses_everything_else_and_does_not_call_gh(
    gh_get: tuple[Path, Path],
    args: list[str],
) -> None:
    """Anything but one blob or file path is refused, status 2, `gh` unrun."""
    script, record = gh_get
    done = run(script, *args)
    assert done.returncode == 2, (done.returncode, done.stderr)
    assert done.stderr.startswith("gh-get: ")
    assert not record.exists()


def allow_list() -> list[str]:
    """Read the review step's `--allowedTools` words out of `claude_args`.

    :returns: each quoted word after the flag, expressions unevaluated.
    """
    (args,) = [
        step["with"]["claude_args"]
        for step in steps(WORKFLOW)
        if step.get("id") == "review"
    ]
    tail = args.split("--allowedTools", 1)[1]
    return [word for word in tail.split('"') if word.strip()]


def test_the_allow_list_admits_the_script_and_no_bare_gh_api() -> None:
    """The script has a rule of its own, and no rule names `gh api`.

    A rule `Bash(gh api ...)` of any shape admits a method flag written
    after the path, which is why the script exists.
    """
    words = allow_list()
    assert "Bash(${{ runner.temp }}/claude-review/gh-get:*)" in words
    assert not [word for word in words if "gh api" in word]
