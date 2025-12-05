import gdsfactory as gf

import numpy as np


@gf.cell_with_module_name
def polygon(
    points: tuple[tuple[float, float], ...] | list | np.ndarray,
    geometry_layer: gf.typings.LayerSpec,
    release_hole_radius: float,
    release_distance: float,
    release_layer: gf.typings.LayerSpec,
) -> gf.Component:
    """Returns a rectangle with release holes

    Args:
        points: points of polygon (doesn't need to repeat the first point)
        geometry_layer: layer to place polygon
        centered: `True` sets center to (0, 0), `False` sets south-west to (0, 0)
        release_hole_radius: radius of the release holes
        release_distance: maximum distance between adjacent release holes
        release_layer: layer to place release holes
    """
    c = gf.Component()
    shape = c.add_polygon(points, geometry_layer)

    if not shape:
        return c

    bb = c.kcl.to_um(shape.bbox())  # Get bounding box

    hole = gf.components.circle(
        radius=release_hole_radius,
        layer=release_layer,
    )

    max_dist = 2 * (release_hole_radius + release_distance) / np.sqrt(2)
    step_x = bb.width / np.ceil(bb.width / max_dist)
    step_y = bb.height / np.ceil(bb.height / max_dist)

    for y in np.arange(0.5 * step_y, bb.height, step_y):
        for x in np.arange(0.5 * step_x, bb.width, step_x):
            ref = c << hole
            ref.move(
                (
                    x - (0.5 * bb.width),
                    y - (0.5 * bb.height),
                )
            )

    return c
