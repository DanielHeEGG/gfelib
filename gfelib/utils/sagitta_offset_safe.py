from __future__ import annotations

import numpy as np


def sagitta_offset_safe(
    radius: float,
    chord: float,
    angle_resolution: float,
) -> float:
    """Returns the upper bound sagitta of an arc

    Args:
        radius: arc radius
        chord: chord length
        angle_resolution: degrees per point for circular geometries
    """
    # term0 is the safe offset of an chord inside a perfect circle
    # The exact offset is `radius - np.sqrt(radius**2 - (chord / 2) ** 2)`, this term is guaranteed to overestimate given any `chord < 2 * radius`
    term0 = chord**2 / (4 * radius)

    # term1 accounts for circles approximated by a polygon
    # The exact offset is `radius * (1 - np.cos(angular_resolution * np.pi / 180 / 2))`, this term is guaranteed to overestimate
    term1 = radius * (angle_resolution * np.pi / 180) / 8

    return term0 + term1
