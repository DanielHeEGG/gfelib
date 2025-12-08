from __future__ import annotations


def sagitta_offset_safe(radius: float, chord: float) -> float:
    """Returns the upper bound sagitta of an arc

    The exact offset is `radius - np.sqrt(radius**2 - (chord / 2) ** 2)`, this function is guaranteed to overestimate given any `chord < 2 * radius`

    Args:
        radius: arc radius
        chord: chord length
    """
    return chord**2 / (4 * radius)
