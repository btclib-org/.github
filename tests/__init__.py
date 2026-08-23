"""The alignment suite: whether the repositories still agree with README.md.

Section 7 of README.md says a test never reaches the network, and every
test here does. That is the whole reason this suite is in this
repository rather than spread across the others: what it measures is
agreement with the standard, and the standard is here. A test in a
repository's own tree answers for that repository's reading of a rule
on the day it was written; a test here reads the rule as the file
states it now, and asks it of every repository at once. Section 15 of
that file is the audit this is the running half of.

A test that takes a `repository` argument is asked once per repository,
`conftest.py` parametrizing it at collection, and `repositories.py` says
which tier of repository a question reaches and which failures the
tracker already records. A test that takes the session fixtures instead
asks what no single tree can answer -- the calendar, the verbatim
copies -- and runs once.

Each test that reaches GitHub is marked `integration`, which is how a
run selects or deselects them by name -- `backlog_test.py` asks
`conftest.py` itself and is not; what skips the suite without
`BTCLIB_INTEGRATION` in the environment is `conftest.py` at collection,
a marker being a label rather than a condition::

    BTCLIB_INTEGRATION=1 uv run --locked --group test pytest
"""
