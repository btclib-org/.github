# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""A tree's homepage is its btclib.org page, its documentation Read the Docs.

Section 3 sends the two surfaces that carry the name -- `[project.urls]
homepage`, which an index serves with the package, and the repository's
`.homepage`, the *About* link on its page -- to the repository's page on
btclib.org. It has `documentation` name the Read the Docs site exactly
where Read the Docs serves the tree. No gate in the tree the rule binds
compares them: a release ships whatever `pyproject.toml` says, and the
setting is changed in a dashboard. This is the same shape of pair
`topics_test.py` compares, one side a line of `pyproject.toml` and the
other a setting no file in the tree holds, and the section's commands
are what a failure here points at.

A test asked per tree asks one that declares `[project.urls]`, whatever
its tier, and skips one that declares none: the rule is about that
table's fields. The tests after them stub Read the Docs and reach no
network.
"""

from __future__ import annotations

import functools
import io
import json
import re
from email.message import Message
from time import sleep
from typing import Any
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest

from . import ORG, TIMEOUT, Tier, by_hand

HOME = "https://btclib.org/{repository}/"
"""Section 3's `homepage`, on both surfaces."""

SITE = re.compile(r"https://(?P<slug>[a-z0-9-]+)\.readthedocs\.io/")
"""Section 3's `documentation`, matched whole."""

PROJECT = "https://app.readthedocs.org/api/v3/projects/{slug}/"
"""Section 11's *Pages and Read the Docs* project endpoint, public."""

URLS = "sed -n '/^\\[project.urls\\]/,/^\\[/p' pyproject.toml"
"""The command that prints the table, in a checkout."""

ASK = f"curl -s {PROJECT.format(slug='<slug>')} | jq .repository.url"
"""The command that names the repository a project builds from."""

THROTTLED = 429
"""The status Read the Docs answers an anonymous caller over its rate."""

ATTEMPTS = 3
"""How many times a project is asked before a 429 skips the cell."""

PAUSE = 10
"""The longest wait, in seconds, granted to one 429.

A 429 without `Retry-After` in seconds waits this long. One asking for
longer is not waited out: the cell skips at once.
"""

BUDGET = 60
"""The seconds one run spends waiting out 429s, all cells together.

The cells ask one after another, so a limit that holds would otherwise
spend the alignment job's `timeout-minutes` on waits. Once the budget is
spent, a 429 skips its cell at once.
"""

WAITED: list[float] = []
"""The waits this run has spent on 429s."""


def declared(repository: str, pyprojects: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return a tree's `[project.urls]`, or skip a tree that declares none.

    The keys are read the way
    `test_the_project_urls_are_section_3s_names` reads them,
    case folded and a space read as an underscore, so a key spelled
    another way for the same link is found rather than reported missing.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    :returns: the table, its keys spelled as section 3 names them.
    """
    urls = pyprojects[repository].get("project", {}).get("urls")
    if not urls:
        pytest.skip(f"{repository} declares no [project.urls]")
    return {key.lower().replace(" ", "_"): value for key, value in urls.items()}


@functools.cache
def serves(slug: str, repository: str) -> bool:
    """Ask Read the Docs whether a project builds from a repository.

    The slug is not the repository's name, and a slug of that name may
    be somebody else's project: `ecc` is, the tree being served as
    `btclib-ecc`. So the project's `repository.url` is what decides, read
    with any `.git` suffix removed. A slug no project holds answers 404.

    :param slug: the project's slug.
    :param repository: the repository asked about.
    :returns: whether the project exists and builds from that repository.
    """
    project = ask(slug)
    if project is None:
        return False
    url: str = project["repository"]["url"]
    return url.removesuffix(".git") == f"https://github.com/{ORG}/{repository}"


def ask(slug: str) -> dict[str, Any] | None:
    """Read a project from Read the Docs, waiting out a 429.

    A 429 is the service's rate limit and says nothing about the tree, so
    it is asked again after the wait `Retry-After` names, within `PAUSE`
    and `BUDGET`. A 429 that outlasts them skips the cell, naming the
    cause; it never passes it. Any other refusal raises rather than
    asserts, so that no backlog row excuses it.

    :param slug: the project's slug.
    :returns: the project, or `None` where no project holds the slug.
    """
    asked = 0
    while True:
        asked += 1
        try:
            with urlopen(PROJECT.format(slug=slug), timeout=TIMEOUT) as answer:  # noqa: S310
                project: dict[str, Any] = json.load(answer)
        except HTTPError as error:
            with error:
                if error.code == 404:  # noqa: PLR2004
                    return None
                if error.code != THROTTLED:
                    raise
                after = error.headers.get("Retry-After")
        else:
            return project
        wait = int(after) if after and after.isdecimal() else PAUSE
        if asked == ATTEMPTS or wait > min(PAUSE, BUDGET - sum(WAITED)):
            pytest.skip(
                f"Read the Docs answered {slug} with 429 Too Many Requests"
                f" (ask {asked} of {ATTEMPTS}, Retry-After {after!r}): a rate"
                " limit says nothing about the tree"
            )
        WAITED.append(wait)
        sleep(wait)


@pytest.mark.integration
@pytest.mark.tier(Tier.PYTHON)
def test_the_homepage_is_the_page_on_btclib_org(
    repository: str,
    settings: dict[str, dict[str, Any]],
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 3: `.homepage` and `homepage` are both the btclib.org page.

    Compared as written, with no normalization of a trailing slash or of
    case: section 3 spells the URL, and a surface that drops its slash
    is the difference the rule sends to be corrected.

    :param repository: the repository asked about.
    :param settings: the repository documents.
    :param pyprojects: the parsed files.
    """
    urls = declared(repository, pyprojects)
    expected = HOME.format(repository=repository)
    read = {
        ".homepage": settings[repository].get("homepage"),
        "[project.urls] homepage": urls.get("homepage"),
    }
    wrong = {surface: url for surface, url in read.items() if url != expected}
    assert not wrong, f"{wrong}, expected {expected}; " + by_hand(
        repository, f"gh api repos/{ORG}/{repository} --jq .homepage; {URLS}"
    )


@pytest.mark.integration
@pytest.mark.tier(Tier.PYTHON)
def test_the_documentation_is_the_read_the_docs_site_serving_the_tree(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 3: `documentation` is the Read the Docs site, where there is one.

    Read the Docs serving the tree is a setting outside it, so it is read
    off the service. The slugs asked are the one `documentation` names,
    the repository's name and the distribution's name; the last two are
    how a tree served there and declaring nothing is found. A tree served
    under another slug that it declares nowhere passes unseen.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    documentation = declared(repository, pyprojects).get("documentation")
    slugs = {repository, pyprojects[repository]["project"].get("name", repository)}
    if isinstance(documentation, str) and (site := SITE.fullmatch(documentation)):
        slugs.add(site["slug"])
    sites = [
        f"https://{slug}.readthedocs.io/"
        for slug in sorted(slugs)
        if serves(slug, repository)
    ]
    command = by_hand(repository, f"{URLS}; {ASK}")
    if not sites:
        assert documentation is None, (
            f"documentation is {documentation!r}, and Read the Docs serves"
            f" {repository} under none of {sorted(slugs)}; " + command
        )
        return
    assert documentation in sites, (
        f"documentation is {documentation!r}, and Read the Docs serves"
        f" {repository} at {sites}; " + command
    )


class _Site:
    """Read the Docs as a script of answers, each a status or a project."""

    def __init__(self, *answers: tuple[int, str | None] | dict[str, Any]) -> None:
        self.answers = list(answers)
        self.asked = 0

    def __call__(self, url: str, timeout: float) -> io.BytesIO:  # noqa: ARG002
        """Answer the next entry of the script, the way `urlopen` does.

        :param url: the endpoint asked.
        :param timeout: the bound, which a script does not need.
        :returns: the project's document.
        :raises HTTPError: where the entry is a status.
        """
        self.asked += 1
        answer = self.answers.pop(0)
        if isinstance(answer, dict):
            return io.BytesIO(json.dumps(answer).encode())
        code, after = answer
        headers = Message()
        if after is not None:
            headers["Retry-After"] = after
        raise HTTPError(url, code, "scripted", headers, io.BytesIO())


@pytest.fixture
def slept(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Stand in for `sleep` and for this run's spent waits.

    :param monkeypatch: the fixture that undoes both.
    :returns: the waits slept, in order.
    """
    waits: list[float] = []
    monkeypatch.setattr(f"{__name__}.sleep", waits.append)
    monkeypatch.setattr(f"{__name__}.WAITED", [])
    return waits


def test_a_429_is_waited_out_and_the_project_read(
    monkeypatch: pytest.MonkeyPatch, slept: list[float]
) -> None:
    """A 429 then a 200: the wait `Retry-After` names, then the answer."""
    project = {"repository": {"url": f"https://github.com/{ORG}/stub.git"}}
    site = _Site((THROTTLED, "1"), project)
    monkeypatch.setattr(f"{__name__}.urlopen", site)
    assert ask("stub") == project
    assert (site.asked, slept) == (2, [1])


def test_a_429_that_lasts_skips_and_never_passes(
    monkeypatch: pytest.MonkeyPatch, slept: list[float]
) -> None:
    """A 429 on every ask skips the cell after `ATTEMPTS`, naming 429."""
    site = _Site(*[(THROTTLED, "1")] * ATTEMPTS)
    monkeypatch.setattr(f"{__name__}.urlopen", site)
    with pytest.raises(pytest.skip.Exception, match="429 Too Many Requests"):
        ask("stub")
    assert (site.asked, slept) == (ATTEMPTS, [1] * (ATTEMPTS - 1))


@pytest.mark.parametrize(
    ("after", "spent"),
    [(str(PAUSE + 1), 0), ("1", BUDGET)],
    ids=["longer-than-the-pause", "budget-spent"],
)
def test_a_429_past_the_bounds_skips_at_once(
    monkeypatch: pytest.MonkeyPatch, slept: list[float], after: str, spent: float
) -> None:
    """A wait over `PAUSE`, or over what `BUDGET` has left, is not slept."""
    monkeypatch.setattr(f"{__name__}.WAITED", [spent])
    site = _Site((THROTTLED, after))
    monkeypatch.setattr(f"{__name__}.urlopen", site)
    with pytest.raises(pytest.skip.Exception, match="429 Too Many Requests"):
        ask("stub")
    assert (site.asked, slept) == (1, [])


def test_the_waits_spend_the_budget_then_a_429_skips_at_once(
    monkeypatch: pytest.MonkeyPatch, slept: list[float]
) -> None:
    """Each wait counts against `BUDGET`, and once it is spent none is slept."""
    project: dict[str, Any] = {"repository": {}}
    rounds = BUDGET // PAUSE
    paid: list[tuple[int, str | None] | dict[str, Any]] = [
        (THROTTLED, str(PAUSE)),
        project,
    ]
    site = _Site(*paid * rounds, (THROTTLED, "1"), project)
    monkeypatch.setattr(f"{__name__}.urlopen", site)
    for _ in range(rounds):
        assert ask("stub") == project
    assert slept == [PAUSE] * rounds
    with pytest.raises(pytest.skip.Exception, match="429 Too Many Requests"):
        ask("stub")
    assert (site.asked, slept) == (2 * rounds + 1, [PAUSE] * rounds)


def test_a_429_without_retry_after_waits_the_pause(
    monkeypatch: pytest.MonkeyPatch, slept: list[float]
) -> None:
    """No `Retry-After` in seconds is read as `PAUSE`."""
    site = _Site((THROTTLED, None), (THROTTLED, "a date"), {"repository": {}})
    monkeypatch.setattr(f"{__name__}.urlopen", site)
    assert ask("stub") == {"repository": {}}
    assert slept == [PAUSE, PAUSE]


@pytest.mark.parametrize(("code", "expected"), [(404, None), (500, HTTPError)])
def test_other_refusals_are_not_retried(
    monkeypatch: pytest.MonkeyPatch,
    slept: list[float],
    code: int,
    expected: type[HTTPError] | None,
) -> None:
    """A 404 is no project; any other refusal raises, with no wait."""
    site = _Site((code, None))
    monkeypatch.setattr(f"{__name__}.urlopen", site)
    if expected is None:
        assert ask("stub") is None
    else:
        with pytest.raises(expected):
            ask("stub")
    assert (site.asked, slept) == (1, [])
