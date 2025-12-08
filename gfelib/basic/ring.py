from __future__ import annotations

import gdsfactory as gf

import numpy as np

import gfelib as gl


@gf.cell_with_module_name(check_instances=False)
def ring(
    radius: float,
    width: float,
    angles: tuple[float, float],
    geometry_layer: gf.typings.LayerSpec,
    angle_resolution: float,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    """Returns a ring with release holes

    Args:
        radius: ring midpoint radius (midpoint between inner and outer radii)
        width: ring width
        angles: ring start and end angles
        geometry_layer: ring polygon layer
        angle_resolution: degrees per point for circular geometries
        release_spec: release specifications, `None` for no release
    """
    c = gf.Component()

    span = angles[1] - angles[0]
    span += 360 if span < 0 else 0
    span = 360 if span > 360 else span

    ring_ref = c << gf.components.ring(
        radius=radius,
        width=width,
        angle=span,
        layer=geometry_layer,
        angle_resolution=angle_resolution,
    )
    ring_ref.rotate(angles[0], (0, 0))

    if release_spec is None:
        return c

    if not release_spec.released:
        return c

    if (
        radius <= release_spec.distance
        or width <= release_spec.distance
        or span * np.pi / 180 * radius <= release_spec.distance
    ):
        return c

    s = 2 * (release_spec.hole_radius + release_spec.distance) / np.sqrt(2)
    sr = width / (width // s + 1)

    for r in np.arange(radius - 0.5 * width + 0.5 * sr, radius + 0.5 * width, sr):
        steps = span * np.pi / 180 * r // s + 1
        dt = span / 180 * np.pi / steps
        t = np.arange(0.5 * dt, span / 180 * np.pi + dt, dt)
        points = np.stack((r * np.cos(t), r * np.sin(t)), axis=-1)
        for point in points[:-1]:
            ref = c << release_spec.hole
            ref.move(point)
            ref.rotate(angles[0], (0, 0))

    return c


@gf.cell_with_module_name
def ring_span(
    radius: float,
    width: float,
    span: tuple[float, float],
    geometry_layer: gf.typings.LayerSpec,
    angle_resolution: float,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    angle = span[1] - span[0]
    c = gf.Component()
    (
        c << ring(radius, width, angle, geometry_layer, angle_resolution, release_spec)
    ).rotate(span[0], (0, 0))
    c.flatten()
    return c


@gf.cell_with_module_name
def ring_full(
    radius: float,
    width: float,
    geometry_layer: gf.typings.LayerSpec,
    angle_resolution: float,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    return ring(radius, width, 360, geometry_layer, angle_resolution, release_spec)
