from __future__ import annotations


import numpy as np
from collections.abc import Sequence

import gfelib as gl

import gdsfactory as gf


@gl.utils.default_cell
def comb(
    comb_height: float,
    comb_width: float,
    comb_gap: float,
    comb_count: int,
    comb_overlap: float,
    geometry_layer: gf.typings.LayerSpec,
    # release_spec=None,
) -> gf.Component:
    """
    Generates an angular comb structure composed of concentric arc fingers.

    Parameters
    ----------
    comb_height : float
        Total height of the comb
    comb_width : float
        Width of each finger
    comb_gap : float
        x gap between adjacent fingers.
    comb_count : int
        Number of gaps (number of fingers = comb_count + 1).
    comb_overlap : float
        x overlap between the fingers
    geometry_layer : LayerSpec
        GDS layer for geometry.
    release_spec : unused
        Reserved for future use.

    Returns
    -------
    gf.Component
    """
    c = gf.Component()

    # Number of fingers
    n_fingers = comb_count + 1
    comb_length = (comb_height + comb_overlap) / 2
    comb_clearance = comb_height - comb_length

    for i in range(n_fingers):
        x = i * (comb_width + comb_gap)
        y = 0 if (i % 2 == 0) else comb_clearance

        finger = gf.components.rectangle(
            size=(comb_width, comb_length), layer=geometry_layer, centered=False
        )

        (c << finger).move((x, y))

    return c
