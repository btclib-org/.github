# Copyright (c) The btclib developers
# Distributed under the MIT software license, see the accompanying
# LICENSE file or https://opensource.org/license/mit for the full text.

"""What section 3 asks of the `classifiers` a package declares.

Every string in the list is one PyPI would accept, and none of them is
the `License ::` the licence expression replaces. Both are rules a tree
keeps by hand: `twine check` reads the long description's rendering and
not this list, and a build accepts whatever the file says.

For a string that is not a classifier the first refusal is the upload
endpoint -- at the point where a version is already being consumed.
`trove-classifiers` is the same list as a package, which is what makes
the question answerable before then. For the pair nothing refuses it
before the upload either: section 3 has what each backend does with one
file carrying both, and the backends this standard keeps build it.
Section 3 has the argument for either.

Which interpreter classifiers a package should carry is a different
question, and one a repository can answer about itself: that is
`interpreters_test.py`, in each library, reading its own floor and its
own matrix. What is here is what a tree is not relied on to ask of
itself, asked of every tree at once.
"""

from __future__ import annotations

from typing import Any

import pytest
from trove_classifiers import classifiers

from . import Tier, by_hand

pytestmark = pytest.mark.integration

PRIVATE = "Private ::"
"""The one prefix PyPI accepts without publishing the list.

It is how a package says it must not be uploaded, so it is not in the
list and is not a defect either.
"""

LICENSE_CLASSIFIER = "License ::"
"""The prefix of the classifiers a PEP 639 expression replaces.

PyPI's list holds them as current entries, so the comparison below
passes them and the rule that refuses them is section 3's alone.
"""


def test_every_classifier_is_a_classifier(
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """A string that is not in the list is a string PyPI will refuse.

    :param pyprojects: the parsed files.
    """
    unknown: dict[str, list[str]] = {}
    for repository, parsed in sorted(pyprojects.items()):
        declared = parsed.get("project", {}).get("classifiers", [])
        wrong = [
            classifier
            for classifier in declared
            if classifier not in classifiers and not classifier.startswith(PRIVATE)
        ]
        if wrong:
            unknown[repository] = wrong
    assert not unknown, f"classifiers PyPI does not know: {unknown}"


@pytest.mark.tier(Tier.PYTHON)
def test_no_license_classifier_beside_the_expression(
    repository: str,
    pyprojects: dict[str, dict[str, Any]],
) -> None:
    """Section 3: the SPDX expression is the licence, and the classifier goes.

    The pair is what an archive carries into the index as two
    declarations of one fact. A tree declaring the classifier and no
    expression is short of the expression, which is section 3's other
    half and a question nothing here asks -- btclib-org/.github#173.

    The `classifiers` list is what is read, and not the file: a tree
    whose comment explains the classifier's absence holds the string
    without declaring it.

    :param repository: the repository asked about.
    :param pyprojects: the parsed files.
    """
    project = pyprojects[repository].get("project", {})
    expression = project.get("license")
    beside = [
        classifier
        for classifier in project.get("classifiers", [])
        if classifier.startswith(LICENSE_CLASSIFIER)
    ]
    assert not (isinstance(expression, str) and beside), (
        f"license = {expression!r} beside {beside}; "
        + by_hand(repository, "grep -n 'License ::' pyproject.toml")
    )
