# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What `sdist-rebuild`, `pypi-install` and `links` do in a tree never released.

Each asks the releases API whether the repository has released, and
each step that asks is read out of its workflow and run here against a
stand-in for `gh`: for a repository never released, one released, an
API that does not answer, and an API that answers something other than
a list. Only the first may skip anything, and the others that find no
release must fail the step.

The stand-in applies the step's own `--jq` filter to the body it is
given, with `jq` in place of the gojq `gh` embeds, so what decides is
the filter the runner runs.
"""

from __future__ import annotations

import re
import shlex
from typing import TYPE_CHECKING, Any

import pytest

from . import ROOT
from .claude_release_test import outputs, run_step, stand_in
from .workflows_test import document, jobs

if TYPE_CHECKING:
    from pathlib import Path

_WORKFLOWS = ROOT / ".github" / "workflows"
_SDIST = _WORKFLOWS / "reusable-sdist-rebuild.yml"
_WAIT = _WORKFLOWS / "reusable-wait-for-index.yml"
_LINKS = _WORKFLOWS / "reusable-links.yml"

# what the stand-in answers, and how it fails where the API is down.
# `gh api` hands its body to the `--jq` filter and prints strings raw
_GH = """\
if [ -n "$GH_DOWN" ]; then
  echo "error connecting to api.github.com" >&2
  exit 1
fi
case "$1" in
  api)
    filter=.
    while [ $# -gt 0 ]; do
      case "$1" in
        --jq) filter=$2; shift 2 ;;
        *) shift ;;
      esac
    done
    printf '%s' "$GH_BODY" | jq -r "$filter" ;;
  release)
    if [ -z "$GH_TAG" ]; then echo "release not found" >&2; exit 1; fi
    echo "$GH_TAG" ;;
  *) exit 2 ;;
esac
"""

# each case, as the body the releases API answers
_NEVER = {"GH_BODY": "[]", "GH_TAG": ""}
_RELEASED = {"GH_BODY": '[{"tag_name": "v2026.11.13"}]', "GH_TAG": "v2026.11.13"}
_DOWN = {"GH_DOWN": "1"}

# a 200 whose body is no list: each has a `length` of 0 in jq, so a
# filter reading `length` alone would take it for no release
_NO_LIST = ["null", "{}", '""', "0"]

# the steps that ask, by name, and each with its workflow and its job
_FIND = "Find the latest release"
_REFUSE = "Refuse a released repository the index does not have"
_ASIDE = "Set aside the downloads badge of a repository never released"
_ASKING = [
    (_SDIST, "release", _FIND),
    (_WAIT, "wait-for-index", _REFUSE),
    (_LINKS, "links", _ASIDE),
]


def _step(workflow: Path, job: str, name: str) -> dict[str, Any]:
    """Read one step of a job, by its name."""
    (found,) = [s for s in jobs(workflow)[job]["steps"] if s.get("name") == name]
    return dict(found)


def _run(
    tmp_path: Path, workflow: Path, job: str, name: str, api: dict[str, str]
) -> tuple[int, str, dict[str, str]]:
    """Run a step with the API answering as given.

    :returns: the exit code, what the step printed, and its outputs.
    """
    bench = tmp_path / "bench"
    bench.mkdir()
    stand_in(bench, "gh", _GH)
    output = tmp_path / "output"
    env = {
        "GITHUB_REPOSITORY": "btclib-org/coin-addresses",
        "GITHUB_OUTPUT": str(output),
        "PACKAGE": "coin-addresses",
        "GH_DOWN": "",
        **api,
    }
    done = run_step(_step(workflow, job, name)["run"], tmp_path, bench, env)
    return done.returncode, done.stdout + done.stderr, outputs(output)


def test_a_tree_never_released_finds_no_tag(tmp_path: Path) -> None:
    """The lookup passes with a notice and no tag."""
    code, printed, found = _run(tmp_path, _SDIST, "release", _FIND, _NEVER)
    assert code == 0, printed
    assert "::notice::btclib-org/coin-addresses has never released" in printed
    assert found == {}


def test_a_released_tree_finds_its_latest_tag(tmp_path: Path) -> None:
    """The control: a repository with a release passes its tag on."""
    code, printed, found = _run(tmp_path, _SDIST, "release", _FIND, _RELEASED)
    assert code == 0, printed
    assert found == {"tag": "v2026.11.13"}


def test_a_released_tree_with_no_latest_fails(tmp_path: Path) -> None:
    """Releases with none marked latest fail as `gh release view` fails."""
    api = {**_RELEASED, "GH_TAG": ""}
    code, printed, found = _run(tmp_path, _SDIST, "release", _FIND, api)
    assert code == 1
    assert "release not found" in printed
    assert found == {}


def test_an_api_that_does_not_answer_fails_the_lookup(tmp_path: Path) -> None:
    """An API that is down never reads as a tree never released."""
    code, _, found = _run(tmp_path, _SDIST, "release", _FIND, _DOWN)
    assert code == 1
    assert found == {}


def test_the_rebuild_runs_only_on_a_tag() -> None:
    """The rebuild skips where the lookup found none, and reads its tag."""
    found = jobs(_SDIST)
    assert list(found) == ["release", "rebuild"]
    assert found["release"]["outputs"] == {"tag": "${{ steps.release.outputs.tag }}"}
    rebuild = found["rebuild"]
    assert rebuild["needs"] == "release"
    assert rebuild["if"] == "needs.release.outputs.tag != ''"
    checkout = next(s for s in rebuild["steps"] if "checkout@" in s.get("uses", ""))
    assert checkout["with"]["ref"] == "${{ needs.release.outputs.tag }}"
    verify = next(
        s for s in rebuild["steps"] if "gh attestation verify" in s.get("run", "")
    )
    assert verify["env"]["TAG"] == "${{ needs.release.outputs.tag }}"


def test_an_unpublished_package_never_released_passes(tmp_path: Path) -> None:
    """The index has no project and the repository no release: a notice."""
    code, printed, _ = _run(tmp_path, _WAIT, "wait-for-index", _REFUSE, _NEVER)
    assert code == 0, printed
    assert "::notice::" in printed
    assert "nothing to install" in printed


def test_an_unpublished_package_released_fails(tmp_path: Path) -> None:
    """A released repository the index does not have is an error.

    That is a `package` input naming the wrong project, or a release
    that never reached the index: either way the matrix must not skip.
    """
    code, printed, _ = _run(tmp_path, _WAIT, "wait-for-index", _REFUSE, _RELEASED)
    assert code == 1
    assert "::error::btclib-org/coin-addresses has released" in printed


def test_an_api_that_does_not_answer_fails_the_wait(tmp_path: Path) -> None:
    """An API that is down never reads as a package never published."""
    code, _, _ = _run(tmp_path, _WAIT, "wait-for-index", _REFUSE, _DOWN)
    assert code == 1


def test_the_wait_reports_published_to_its_caller() -> None:
    """The script's answer is the job's output and the workflow's.

    The releases question runs only on the script's no.
    """
    wait = jobs(_WAIT)["wait-for-index"]
    script = next(s for s in wait["steps"] if s.get("id") == "index")
    assert '--output "$GITHUB_OUTPUT"' in script["run"]
    assert wait["outputs"] == {"published": "${{ steps.index.outputs.published }}"}
    assert _step(_WAIT, "wait-for-index", _REFUSE)["if"] == (
        "steps.index.outputs.published == 'false'"
    )
    on = document(_WAIT)[True]["workflow_call"]
    assert on["outputs"]["published"]["value"] == (
        "${{ jobs.wait-for-index.outputs.published }}"
    )


def _excluded(tmp_path: Path, repository: str) -> re.Pattern[str]:
    """Return the pattern lychee excludes in a repository never released."""
    bench = tmp_path / "bench"
    bench.mkdir()
    stand_in(bench, "gh", _GH)
    output = tmp_path / "output"
    env = {
        "GITHUB_REPOSITORY": repository,
        "GITHUB_OUTPUT": str(output),
        "GH_DOWN": "",
        **_NEVER,
    }
    done = run_step(_step(_LINKS, "links", _ASIDE)["run"], tmp_path, bench, env)
    assert done.returncode == 0, done.stdout + done.stderr
    flag, pattern = shlex.split(outputs(output)["exclude"])
    assert flag == "--exclude"
    return re.compile(pattern)


@pytest.mark.parametrize(
    "url",
    [
        "https://pepy.tech/projects/coin-addresses",
        "https://static.pepy.tech/badge/coin-addresses",
        "https://static.pepy.tech/badge/coin-addresses/month",
        "https://pepy.tech/projects/coin-addresses?versions=1",
    ],
)
def test_a_tree_never_released_sets_aside_its_own_downloads(
    tmp_path: Path, url: str
) -> None:
    """The pepy links naming the repository are excluded."""
    assert _excluded(tmp_path, "btclib-org/coin-addresses").search(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://pepy.tech/projects/coin-addresses-x",
        "https://pepy.tech/projects/btclib",
        "https://example.org/https://pepy.tech/projects/coin-addresses",
        "https://pypi.org/project/coin-addresses/",
        "https://github.com/btclib-org/coin-addresses/releases",
    ],
)
def test_a_tree_never_released_checks_every_other_link(
    tmp_path: Path, url: str
) -> None:
    """Nothing but the repository's own pepy links is excluded."""
    assert not _excluded(tmp_path, "btclib-org/coin-addresses").search(url)


def test_a_dot_in_the_name_is_a_dot(tmp_path: Path) -> None:
    """The name is escaped, so its dot matches nothing else."""
    pattern = _excluded(tmp_path, "btclib-org/btclib-org.github.io")
    assert pattern.search("https://pepy.tech/projects/btclib-org.github.io")
    assert not pattern.search("https://pepy.tech/projects/btclib-orgxgithub.io")


def test_a_released_tree_excludes_nothing(tmp_path: Path) -> None:
    """The control: a repository with a release checks its pepy links."""
    code, printed, found = _run(tmp_path, _LINKS, "links", _ASIDE, _RELEASED)
    assert code == 0, printed
    assert found == {}


def test_an_api_that_does_not_answer_fails_the_links(tmp_path: Path) -> None:
    """An API that is down never reads as a tree never released."""
    code, _, found = _run(tmp_path, _LINKS, "links", _ASIDE, _DOWN)
    assert code == 1
    assert found == {}


def test_lychee_reads_the_exclusion() -> None:
    """The step's output reaches lychee's arguments, before the targets."""
    args = _step(_LINKS, "links", "Check the links")["with"]["args"]
    exclude = "${{ steps.released.outputs.exclude }}"
    assert exclude in args
    assert args.index(exclude) < args.index("${{ inputs.targets }}")


@pytest.mark.parametrize("body", _NO_LIST)
@pytest.mark.parametrize(
    ("workflow", "job", "name"), _ASKING, ids=["sdist-rebuild", "wait", "links"]
)
def test_an_answer_that_is_no_list_fails_the_step(
    tmp_path: Path, workflow: Path, job: str, name: str, body: str
) -> None:
    """A body that is no list never reads as a repository never released."""
    api = {"GH_BODY": body, "GH_TAG": ""}
    code, printed, found = _run(tmp_path, workflow, job, name, api)
    assert code != 0, printed
    assert "the releases API answered no list" in printed
    assert "never released" not in printed
    assert found == {}
