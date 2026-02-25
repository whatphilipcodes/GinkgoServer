"""Small math utilities used across the project.

This module provides reusable numeric helpers. Keep functions small and
well-documented for easy reuse in different services.
"""


def normalize(value: str | float | int | None) -> float | None:
    """Normalize a numeric-like `value` to a float in the range [0.0, 1.0]."""
    if value is None:
        return None

    try:
        v = float(value)
    except Exception:
        return None

    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v
