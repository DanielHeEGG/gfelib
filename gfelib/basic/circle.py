from __future__ import annotations

import gdsfactory as gf

import numpy as np

import gfelib as gl


@gf.cell_with_module_name
def circle(
    radius: float,
    geometry_layer: gf.typings.LayerSpec,
    angle_resolution: float,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    """Returns a circle with release holes

    Args:
        radius: radius of the circle
        geometry_layer: layer to place polygon
        angle_resolution: number of degrees per point
        release_spec: release specifications, `None` for no release
    """
    c = gf.Component()

    _ = c << gf.components.circle(
        radius=radius,
        layer=geometry_layer,
        angle_resolution=angle_resolution,
    )

    if release_spec is None:
        return c

    if not release_spec.released:
        return c

    if radius <= release_spec.distance:
        return c

    s = 2 * (release_spec.hole_radius + release_spec.distance) / np.sqrt(2)
    sr = radius / (radius // s + 1.5)

    for r in np.arange(0, radius, sr):
        steps = 2 * np.pi * r // s + 1
        dt = 2 * np.pi / steps
        t = np.arange(0.5 * dt, 2 * np.pi + dt, dt)
        points = np.stack((r * np.cos(t), r * np.sin(t)), axis=-1)
        for point in points[:-1]:
            ref = c << release_spec.hole
            ref.move(point)

    return c
