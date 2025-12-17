from __future__ import annotations

import gdsfactory as gf

import numpy as np
from collections.abc import Sequence

import gfelib as gl


@gl.utils.default_cell
def via(
    radius_first: float,
    radius_last: float,
    geometry_layers: Sequence[gf.typings.LayerSpec],
    angle_resolution: float,
) -> gf.Component:
    """Returns a via on multiple layers with linearly spaced radii

    Args:
        radius_first: via radius on first layer  (`geometry_layers[0]`)
        radius_last: via radius on last layer (`geometry_layers[-1]`)
        geometry_layers: via polygon layers, if only one layer is specified, `radius_last` is ignored
        angle_resolution: degrees per point for circular geometries
    """
    c = gf.Component()

    step = (
        (radius_last - radius_first) / (len(geometry_layers) - 1)
        if len(geometry_layers) > 1
        else 0
    )
    for i, layer in enumerate(geometry_layers):
        _ = c << gf.components.circle(
            radius=radius_first + i * step,
            angle_resolution=angle_resolution,
            layer=layer,
        )

    return c
