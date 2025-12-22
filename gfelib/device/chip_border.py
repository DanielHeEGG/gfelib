from __future__ import annotations

import gdsfactory as gf

import numpy as np

import gfelib as gl


@gl.utils.default_cell
def chip_border(
    size: gf.typings.Size,
    width: float,
    geometry_layer: gf.typings.LayerSpec,
    handle_layer: gf.typings.LayerSpec | None,
    centered: bool,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    """Returns a released chip border, released chip final size will be `size - width`

    Args:
        size: chip outer width and height
        width: width of the border
        geometry_layer: rectangle polygon layer
        handle_layer: handle polygon layer
        centered: `True` sets center to (0, 0), `False` sets south-west to (0, 0)
    """
    c = gf.Component()

    _ = c << gl.basic.rectangle_ring(
        size=size,
        width=width,
        geometry_layer=geometry_layer,
        centered=centered,
        release_spec=release_spec,
    )

    if handle_layer is None:
        return c

    ref = c << gl.basic.rectangle(
        size=(size[0] - width, size[1] - width),
        geometry_layer=handle_layer,
        centered=centered,
        release_spec=None,
    )
    if not centered:
        ref.move((0.5 * width, 0.5 * width))

    return c
