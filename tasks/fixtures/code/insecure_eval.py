def parse_filter(user_filter: str) -> object:
    """Synthetic vulnerable fixture. Never use this implementation."""
    return eval(user_filter, {"__builtins__": {}}, {})  # noqa: S307 - intentionally vulnerable fixture
