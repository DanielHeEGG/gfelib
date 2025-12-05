import gdsfactory as gf

import numpy as np


@gf.cell_with_module_name
def arc(
    radius: float,
    width: float,
    angle: float,
    geometry_layer: gf.typings.LayerSpec,
    angle_resolution: float,
    release_hole_radius: float,
    release_distance: float,
    release_layer: gf.typings.LayerSpec,
) -> gf.Component:
    """Returns a ring with release holes

    Args:
        radius: radius of the ring (midpoint between inner and outer radii)
        width: width of the ring
        angle: angular coverage of the ring (degs)
        geometry_layer: layer to place polygon
        angle_resolution: number of degrees per point
        release_hole_radius: radius of the release holes
        release_distance: maximum distance between adjacent release holes
        release_layer: layer to place release holes
    """
    c = gf.Component()

    _ = c << gf.components.ring(
        radius=radius,
        width=width,
        angle=angle,
        layer=geometry_layer,
        angle_resolution=angle_resolution,
    )

    if (
        radius <= release_distance
        or width <= 2 * release_distance
        or angle * np.pi / 180 * (radius + 0.5 * width) <= 2 * release_distance
    ):
        return c

    hole = gf.components.circle(
        radius=release_hole_radius,
        layer=release_layer,
    )

    max_dist = 2 * (release_hole_radius + release_distance) / np.sqrt(2)
    radial_step = width / (width // max_dist + 1)

    for r in np.arange(
        radius - 0.5 * width + 0.5 * radial_step, radius + 0.5 * width, radial_step
    ):
        n_ang_steps = (angle / 180 * np.pi * r) // max_dist + 1
        dt = angle / 180 * np.pi / n_ang_steps
        t = np.arange(0.5 * dt, angle / 180 * np.pi + dt, dt)
        points = np.stack((r * np.cos(t), r * np.sin(t)), axis=-1)
        for point in points[:-1]:
            ref = c << hole
            ref.move(point)

    return c


@gf.cell_with_module_name
def arc_span(
    radius: float,
    width: float,
    span: tuple[float, float],
    geometry_layer: gf.typings.LayerSpec,
    angle_resolution: float,
    release_hole_radius: float,
    release_distance: float,
    release_layer: gf.typings.LayerSpec,
) -> gf.Component:
    angle = span[1] - span[0]
    c = gf.Component()
    (
        c
        << arc(
            radius,
            width,
            angle,
            geometry_layer,
            angle_resolution,
            release_hole_radius,
            release_distance,
            release_layer,
        )
    ).rotate(span[0], (0, 0))
    c.flatten()
    return c


@gf.cell_with_module_name
def ring(
    radius: float,
    width: float,
    geometry_layer: gf.typings.LayerSpec,
    angle_resolution: float,
    release_hole_radius: float,
    release_distance: float,
    release_layer: gf.typings.LayerSpec,
) -> gf.Component:
    return arc(
        radius,
        width,
        360,
        geometry_layer,
        angle_resolution,
        release_hole_radius,
        release_distance,
        release_layer,
    )
