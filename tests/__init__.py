"""The alignment suite: what is true between the repositories.

Section 7 of README.md says a test never reaches the network, and every
test here does. That is the whole reason this suite is in this
repository rather than spread across the others: what it checks is not a
property of a tree, it is a property of the organization, and no tree
can hold it. A fact one repository can check about itself stays there,
as a convention test of its own.

Each test is marked `integration`, which is how a run selects or
deselects the suite by name; what skips it without `BTCLIB_INTEGRATION`
in the environment is the autouse fixture in `conftest.py`, a marker
being a label rather than a condition::

    BTCLIB_INTEGRATION=1 uv run --locked --group test pytest
"""
