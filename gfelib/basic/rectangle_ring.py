from __future__ import annotations

import gdsfactory as gf

import numpy as np

import gfelib as gl


@gl.utils.default_cell
def rectangle_ring(
    size: gf.typings.Size,
    width: float,
    geometry_layer: gf.typings.LayerSpec,
    centered: bool,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    """Returns a rectangular ring with release holes

    Args:
        size: rectangle outer width and height
        width: width of the ring
        geometry_layer: rectangle polygon layer
        centered: `True` sets center to (0, 0), `False` sets south-west to (0, 0)
        release_spec: release specifications, `None` for no release
    """
    c = gf.Component()

    release = True

    if release_spec is None:
        release = False

    elif not release_spec.released:
        release = False

    elif size[0] <= release_spec.distance or size[1] <= release_spec.distance:
        release = False

    elif width <= release_spec.distance:
        release = False

    corner = gl.basic.rectangle(
        size=(width, width),
        geometry_layer=geometry_layer,
        centered=False,
        release_spec=release_spec if release else None,
    )
    for y in [0, size[1] - width]:
        for x in [0, size[0] - width]:
            ref = c << corner
            ref.move(
                (
                    x - (0.5 * size[0] if centered else 0),
                    y - (0.5 * size[1] if centered else 0),
                )
            )

    bar_x = gl.basic.rectangle(
        size=(size[0] - 2 * width, width),
        geometry_layer=geometry_layer,
        centered=False,
        release_spec=release_spec if release else None,
    )
    for y in [0, size[1] - width]:
        ref = c << bar_x
        ref.move(
            (
                width - (0.5 * size[0] if centered else 0),
                y - (0.5 * size[1] if centered else 0),
            )
        )

    bar_y = gl.basic.rectangle(
        size=(width, size[1] - 2 * width),
        geometry_layer=geometry_layer,
        centered=False,
        release_spec=release_spec if release else None,
    )
    for x in [0, size[0] - width]:
        ref = c << bar_y
        ref.move(
            (
                x - (0.5 * size[0] if centered else 0),
                width - (0.5 * size[1] if centered else 0),
            )
        )

    return c
