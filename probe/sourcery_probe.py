"""A file with one use-named-expression finding, for the Sourcery probe."""


def first(d: dict[str, str]) -> str | None:
    """Return the value under "a", if any."""
    x = d.get("a")
    if x:
        return x
    return None
