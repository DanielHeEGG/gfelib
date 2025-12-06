import gdsfactory as gf

import numpy as np


@gf.cell_with_module_name
def circle(
    radius: float,
    geometry_layer: gf.typings.LayerSpec,
    angle_resolution: float,
    release_hole_radius: float = 0,
    release_distance: float = 0,
    release_layer: gf.typings.LayerSpec = (0, 0),
) -> gf.Component:
    """Returns a circle with release holes

    Args:
        radius: radius of the circle
        geometry_layer: layer to place polygon
        angle_resolution: number of degrees per point
        release_hole_radius: radius of the release holes, 0 for no release
        release_distance: maximum distance between adjacent release holes, 0 for no release
        release_layer: layer to place release holes
    """
    c = gf.Component()

    _ = c << gf.components.circle(
        radius=radius,
        layer=geometry_layer,
        angle_resolution=angle_resolution,
    )

    if release_hole_radius <= 0 or release_distance <= 0:
        return c

    if radius <= release_distance:
        return c

    hole = gf.components.circle(
        radius=release_hole_radius,
        layer=release_layer,
    )

    max_dist = 2 * (release_hole_radius + release_distance) / np.sqrt(2)
    radial_step_size = radius / (radius // max_dist + 1.5)

    for r in np.arange(0, radius, radial_step_size):
        n_ang_steps = (2 * np.pi * r) // max_dist + 1
        dt = 2 * np.pi / n_ang_steps
        t = np.arange(0.5 * dt, 2 * np.pi + dt, dt)
        points = np.stack((r * np.cos(t), r * np.sin(t)), axis=-1)
        for point in points[:-1]:
            ref = c << hole
            ref.move(point)

    return c
