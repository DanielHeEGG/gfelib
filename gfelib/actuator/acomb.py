from __future__ import annotations


import numpy as np
from collections.abc import Sequence

import gfelib as gl

import gdsfactory as gf


@gl.utils.default_cell
def angular_comb(
    radius_inner: float,
    radius_outer: float,
    angles: tuple[float, float],
    comb_gap: float,
    comb_count: int,
    comb_overlap_angle: float,
    geometry_layer: gf.typings.LayerSpec,
    angle_resolution: float,
    # release_spec=None,
) -> gf.Component:
    """
    Generates an angular comb structure composed of concentric arc fingers.

    Parameters
    ----------
    radius_inner : float
        Inner radius of the innermost finger.
    radius_outer : float
        Outer radius of the outermost finger.
    angles : (float, float)
        Start and end angles in degrees.
    comb_gap : float
        Radial gap between adjacent fingers.
    comb_count : int
        Number of gaps (number of fingers = comb_count + 1).
    comb_overlap_angle : float
        Angular overlap added on both sides of each finger (degrees).
    geometry_layer : LayerSpec
        GDS layer for geometry.
    angle_resolution : float
        Angular discretization in degrees (passed to ring).
    release_spec : unused
        Reserved for future use.

    Returns
    -------
    gf.Component
    """
    c = gf.Component()

    theta_start, theta_end = sorted(angles)
    span = (theta_end - theta_start + comb_overlap_angle) / 2

    if span <= 0:
        raise ValueError("Invalid geometry: angular span <= 0")

    # Number of fingers
    n_fingers = comb_count + 1

    # Total radial span available
    total_radial_span = radius_outer - radius_inner

    # Solve finger width assuming:
    # n_fingers * finger_width + comb_count * comb_gap = total_radial_span
    finger_width = (total_radial_span - comb_count * comb_gap) / n_fingers

    if finger_width <= 0:
        raise ValueError("Invalid geometry: finger width <= 0")

    for i in range(n_fingers):
        r_in = radius_inner + i * (finger_width + comb_gap)
        r_out = r_in + finger_width

        ring = gf.components.ring(
            radius=(r_in + r_out) / 2,
            width=finger_width,
            angle=span,
            layer=geometry_layer,
            angle_resolution=angle_resolution,
        )

        (c << ring).rotate(theta_start if (i % 2 == 0) else theta_end - span)

    return c
