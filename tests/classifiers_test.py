"""Every classifier a package declares is one PyPI would accept.

`twine check` reads the long description's rendering and not this list,
and a build accepts whatever the file says, so the first thing that
refuses a classifier that is not one is the upload endpoint -- at the
point where a version is already being consumed. `trove-classifiers` is
the same list as a package, which is what makes the question answerable
before then. Section 3 has the argument.

Which interpreter classifiers a package should carry is a different
question, and one a repository can answer about itself: that is
`interpreters_test.py`, in each library, reading its own floor and its
own matrix. This asks only what no single tree can -- whether the string
exists at all -- and asks it of every tree at once.
"""

from __future__ import annotations

from typing import Any

import pytest
from trove_classifiers import classifiers

pytestmark = pytest.mark.integration

PRIVATE = "Private ::"
"""The one prefix PyPI accepts without publishing the list.

It is how a package says it must not be uploaded, so it is not in the
list and is not a defect either.
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
