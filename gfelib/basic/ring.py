from __future__ import annotations

import gdsfactory as gf

import numpy as np

import gfelib as gl


@gf.cell_with_module_name
def ring(
    radius: float,
    width: float,
    angle: float,
    geometry_layer: gf.typings.LayerSpec,
    angle_resolution: float,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    """Returns a ring with release holes

    Args:
        radius: radius of the ring (midpoint between inner and outer radii)
        width: width of the ring
        angle: angular coverage of the ring (unit: degrees)
        geometry_layer: layer to place polygon
        angle_resolution: number of degrees per point
        release_spec: release specifications, `None` for no release
    """
    c = gf.Component()

    _ = c << gf.components.ring(
        radius=radius,
        width=width,
        angle=angle,
        layer=geometry_layer,
        angle_resolution=angle_resolution,
    )

    if release_spec is None:
        return c

    if not release_spec.released:
        return c

    if (
        radius <= release_spec.distance
        or width <= release_spec.distance
        or angle * np.pi / 180 * radius <= release_spec.distance
    ):
        return c

    s = 2 * (release_spec.hole_radius + release_spec.distance) / np.sqrt(2)
    sr = width / (width // s + 1)

    for r in np.arange(radius - 0.5 * width + 0.5 * sr, radius + 0.5 * width, sr):
        n_ang_steps = (angle / 180 * np.pi * r) // s + 1
        dt = angle / 180 * np.pi / n_ang_steps
        t = np.arange(0.5 * dt, angle / 180 * np.pi + dt, dt)
        points = np.stack((r * np.cos(t), r * np.sin(t)), axis=-1)
        for point in points[:-1]:
            ref = c << release_spec.hole
            ref.move(point)

    return c


@gf.cell_with_module_name
def ring_span(
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
        << ring(
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
def ring_full(
    radius: float,
    width: float,
    geometry_layer: gf.typings.LayerSpec,
    angle_resolution: float,
    release_hole_radius: float,
    release_distance: float,
    release_layer: gf.typings.LayerSpec,
) -> gf.Component:
    return ring(
        radius,
        width,
        360,
        geometry_layer,
        angle_resolution,
        release_hole_radius,
        release_distance,
        release_layer,
    )
