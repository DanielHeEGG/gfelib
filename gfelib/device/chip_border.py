from __future__ import annotations

import gdsfactory as gf

import numpy as np

import gfelib as gl


@gl.utils.default_cell
def chip_border(
    size: gf.typings.Size,
    width: float,
    geometry_layer: gf.typings.LayerSpec,
    centered: bool,
    release_spec: gl.datatypes.ReleaseSpec | None,
    cavity_spec: gl.datatypes.CavitySpec | None,
) -> gf.Component:
    """Returns a released chip border

    Args:
        size: chip outer width and height
        width: width of the border
        geometry_layer: rectangle polygon layer
        centered: `True` sets center to (0, 0), `False` sets south-west to (0, 0)
        release_spec: release specifications, `None` for no release
        cavity_spec: handle cavity specifications, `None` for no etch
    """
    c = gf.Component()

    _ = c << gl.basic.rectangle_ring(
        size=size,
        width=width,
        geometry_layer=geometry_layer,
        centered=centered,
        release_spec=release_spec,
    )

    if cavity_spec is None:
        return c

    _ = c << gl.basic.rectangle_ring(
        size=(size[0] - width + cavity_spec.width, size[1] - width + cavity_spec.width),
        width=cavity_spec.width,
        geometry_layer=cavity_spec.layer,
        centered=centered,
        release_spec=None,
    )

    return c
