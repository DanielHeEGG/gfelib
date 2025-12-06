from __future__ import annotations

import gdsfactory as gf

import numpy as np

import gfelib as gl


@gf.cell_with_module_name
def rectangle(
    size: gf.typings.Size,
    geometry_layer: gf.typings.LayerSpec,
    centered: bool,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    """Returns a rectangle with release holes

    Args:
        size: width and height of rectangle
        geometry_layer: layer to place polygon
        centered: `True` sets center to (0, 0), `False` sets south-west to (0, 0)
        release_spec: release specifications, `None` for no release
    """
    c = gf.Component()

    _ = c << gf.components.rectangle(
        size=size,
        layer=geometry_layer,
        centered=centered,
    )

    if release_spec is None:
        return c

    if not release_spec.released:
        return c

    if size[0] <= release_spec.distance or size[1] <= release_spec.distance:
        return c

    s = 2 * (release_spec.hole_radius + release_spec.distance) / np.sqrt(2)
    sx = size[0] / np.ceil(size[0] / s)
    sy = size[1] / np.ceil(size[1] / s)

    for y in np.arange(0.5 * sy, size[1], sy):
        for x in np.arange(0.5 * sx, size[0], sx):
            ref = c << release_spec.hole
            ref.move(
                (
                    x - (0.5 * size[0] if centered else 0),
                    y - (0.5 * size[1] if centered else 0),
                )
            )

    return c
