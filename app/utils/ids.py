"""Identifier generation utilities."""

import uuid


def generate_id(prefix: str | None = None) -> str:
    """Generate a clean, unique identifier with an optional entity prefix.

    Examples:
        generate_id("usr") -> "usr_3f4a8b2c1d0e"
        generate_id("prj") -> "prj_9a8b7c6d5e4f"
        generate_id("tsk") -> "tsk_1a2b3c4d5e6f"
    """
    raw_id = uuid.uuid4().hex
    if prefix:
        return f"{prefix}_{raw_id[:16]}"
    return raw_id
