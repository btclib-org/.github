"""The probe's regex against the shapes its docstring claims."""

import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "probe_1642", Path(__file__).parent.parent / ".github/scripts/probe_1642.py"
)


def test_sha() -> None:
    """A short and a full sha match; uppercase and six characters do not."""
    assert SPEC is not None and SPEC.loader is not None
    module = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(module)
    assert module.SHA.match("abcdef0")
    assert module.SHA.match("a" * 40)
    assert not module.SHA.match("ABCDEF0")
    assert not module.SHA.match("abcdef")
