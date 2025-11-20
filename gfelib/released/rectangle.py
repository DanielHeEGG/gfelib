import gdsfactory as gf

import numpy as np


@gf.cell_with_module_name
def rectangle(
    size: gf.typings.Size,
    geometry_layer: gf.typings.LayerSpec,
    centered: bool,
    release_hole_radius: float,
    release_distance: float,
    release_layer: gf.typings.LayerSpec,
) -> gf.Component:
    """Returns a rectangle with release holes

    Args:
        size: width and height of rectangle
        geometry_layer: layer to place polygon
        centered: `True` sets center to (0, 0), `False` sets south-west to (0, 0)
        release_hole_radius: radius of the release holes
        release_distance: maximum distance between adjacent release holes
        release_layer: layer to place release holes
    """
    c = gf.Component()

    _ = c << gf.components.rectangle(
        size=size,
        layer=geometry_layer,
        centered=centered,
    )

    if size[0] <= release_distance or size[1] <= release_distance:
        return c

    hole = gf.components.circle(
        radius=release_hole_radius,
        layer=release_layer,
    )

    s = 2 * (release_hole_radius + release_distance) / np.sqrt(2)
    sx = size[0] / np.ceil(size[0] / s)
    sy = size[1] / np.ceil(size[1] / s)

    for y in np.arange(0.5 * sy, size[1], sy):
        for x in np.arange(0.5 * sx, size[0], sx):
            ref = c << hole
            ref.move(
                (
                    x - (0.5 * size[0] if centered else 0),
                    y - (0.5 * size[1] if centered else 0),
                )
            )

    return c
