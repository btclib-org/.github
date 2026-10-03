# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What sections 10 and 12 say of `reusable-build.yml`, read from the file.

The workflow cannot be run from this repository, which builds nothing,
so what makes its signature SLSA Build L3 is asked of the document: the
job that builds holds no OIDC token, the one that signs checks what it
signs against what the build printed, and the weekly rebuild verifies
against the signer a verifier is told to name.
"""

from __future__ import annotations

import re
from typing import Any

import pytest
import yaml

from . import ROOT

_WORKFLOWS = ROOT / ".github" / "workflows"


def _jobs(name: str) -> dict[str, Any]:
    """Return the jobs of one of this repository's workflows."""
    parsed = yaml.safe_load((_WORKFLOWS / name).read_text(encoding="utf-8"))
    jobs: dict[str, Any] = parsed["jobs"]
    return jobs


@pytest.fixture(scope="module")
def jobs() -> dict[str, Any]:
    """Return the jobs of `reusable-build.yml`."""
    return _jobs("reusable-build.yml")


def _uses(job: dict[str, Any]) -> list[str]:
    """List the actions a job's steps use."""
    return [step["uses"] for step in job["steps"] if "uses" in step]


def test_the_build_job_holds_no_token(jobs: dict[str, Any]) -> None:
    """Assert the job that builds can only read the repository."""
    assert jobs["build"]["permissions"] == {"contents": "read"}


def test_only_the_attest_job_signs(jobs: dict[str, Any]) -> None:
    """Assert the signing scopes and the signing step are one job's."""
    assert jobs["attest"]["permissions"] == {
        "id-token": "write",
        "attestations": "write",
    }
    assert not [use for use in _uses(jobs["build"]) if "attest" in use]
    assert [use for use in _uses(jobs["attest"]) if "/attest@" in use]


def test_the_attest_job_checks_the_files_before_it_signs(
    jobs: dict[str, Any],
) -> None:
    """Assert what is signed is what the build job printed."""
    attest = jobs["attest"]
    assert attest["needs"] == "build"
    assert "digests" in jobs["build"]["outputs"]
    steps = attest["steps"]
    signing = next(i for i, s in enumerate(steps) if "/attest@" in s.get("uses", ""))
    checks = [
        step
        for step in steps[:signing]
        if "sha256sum" in step.get("run", "")
        and "| diff -" in step["run"]
        and "needs.build.outputs.digests" in step.get("env", {}).get("DIGESTS", "")
    ]
    assert checks, "no step before the signature compares against the build job"


def test_the_attest_check_fails_when_sha256sum_does(jobs: dict[str, Any]) -> None:
    """Assert the check runs under bash, so that pipefail is on."""
    check = next(s for s in jobs["attest"]["steps"] if "| diff -" in s.get("run", ""))
    assert check["shell"] == "bash"


def test_the_release_checks_the_files_before_it_creates_the_release() -> None:
    """Assert a caller's digests are compared before the release exists."""
    parsed = yaml.safe_load(
        (_WORKFLOWS / "reusable-github-release.yml").read_text(encoding="utf-8")
    )
    # PyYAML reads the key `on` as True
    digests = parsed[True]["workflow_call"]["inputs"]["digests"]
    assert digests["type"] == "string"
    assert not digests["required"]
    assert digests["default"] == ""
    steps = parsed["jobs"]["github-release"]["steps"]
    creating = next(
        i for i, s in enumerate(steps) if "gh release create" in s.get("run", "")
    )
    checks = [
        step
        for step in steps[:creating]
        if "| diff -" in step.get("run", "")
        and "sha256sum dist/* sbom/*" in step["run"]
        and step.get("shell") == "bash"
        and step.get("if") == "inputs.digests != ''"
        and step.get("env", {}).get("DIGESTS") == "${{ inputs.digests }}"
    ]
    assert checks, "no step before the release compares against the build job"


def test_the_workflow_passes_the_build_digests_out() -> None:
    """Assert a caller reads the digests the build job printed."""
    parsed = yaml.safe_load(
        (_WORKFLOWS / "reusable-build.yml").read_text(encoding="utf-8")
    )
    # PyYAML reads the key `on` as True
    outputs = parsed[True]["workflow_call"]["outputs"]
    assert outputs["digests"]["value"] == "${{ jobs.build.outputs.digests }}"


def _hashed(job: dict[str, Any]) -> set[str]:
    """Return the globs the `sha256sum` step of a job reads."""
    globs: set[str] = set()
    for step in job["steps"]:
        found = re.search(r"sha256sum ((?:\S+/\* ?)+)", step.get("run", ""))
        if found:
            globs |= set(found.group(1).split())
    return globs


def test_the_files_hashed_are_the_files_signed(jobs: dict[str, Any]) -> None:
    """Assert both jobs hash the globs the attestation covers."""
    step = next(s for s in jobs["attest"]["steps"] if "/attest@" in s.get("uses", ""))
    signed = set(step["with"]["subject-path"].split())
    assert signed
    assert _hashed(jobs["build"]) == signed
    assert _hashed(jobs["attest"]) == signed


def test_the_rebuild_verifies_the_signer_and_the_tag() -> None:
    """Assert the weekly rebuild names reusable-build.yml and its tag."""
    steps = _jobs("reusable-sdist-rebuild.yml")["rebuild"]["steps"]
    run = next(s["run"] for s in steps if "gh attestation verify" in s.get("run", ""))
    assert '--source-ref "refs/tags/$TAG"' in run
    build = "reusable-build.yml@refs/heads/main"
    attest = "reusable-attest.yml@refs/heads/main"
    assert build in run
    assert attest in run, "the fallback for earlier releases"
    assert run.index(build) < run.index(attest)


def test_the_optional_inputs_default_to_the_build_a_tree_gets_without_them() -> None:
    """Assert a caller passing none of the optional inputs builds as before.

    A tree that calls the workflow with `python` and `version-suffix`
    alone gets `uv build`: none of the inputs added for a tree that
    builds its wheels elsewhere may change that.
    """
    parsed = yaml.safe_load(
        (_WORKFLOWS / "reusable-build.yml").read_text(encoding="utf-8")
    )
    inputs = parsed[True]["workflow_call"]["inputs"]
    assert {name for name, spec in inputs.items() if spec.get("required")} == {"python"}
    assert inputs["submodules"]["default"] is False
    assert inputs["setup-python"]["default"] is False
    assert inputs["sdist-only"]["default"] is False
    assert inputs["dist-artifact"]["default"] == "dist"
    assert inputs["build-constraints"]["default"] == ""


@pytest.mark.parametrize(
    ("command", "variable"),
    [
        ("uv build", "UV_BUILD_CONSTRAINT"),
        ("python -m build -s", "PIP_CONSTRAINT"),
    ],
)
def test_each_build_step_passes_the_constraints_its_builder_reads(
    jobs: dict[str, Any], command: str, variable: str
) -> None:
    """Assert a build step sets the variable its command honours.

    `uv build` ignores PIP_CONSTRAINT, and `python -m build` installs the
    requirements with pip, which ignores UV_BUILD_CONSTRAINT.
    """
    step = next(s for s in jobs["build"]["steps"] if command in s.get("run", ""))
    assert step["env"] == {variable: "${{ inputs.build-constraints }}"}


@pytest.mark.parametrize(
    ("command", "variable"),
    [
        ("uv build", "UV_BUILD_CONSTRAINT"),
        ("python -m build -s", "PIP_CONSTRAINT"),
    ],
)
def test_each_rebuild_step_passes_the_constraints_its_builder_reads(
    command: str, variable: str
) -> None:
    """Assert the weekly rebuild sets what the release build sets."""
    steps = _jobs("reusable-sdist-rebuild.yml")["rebuild"]["steps"]
    step = next(s for s in steps if command in s.get("run", ""))
    assert step["env"] == {variable: "${{ inputs.build-constraints }}"}
