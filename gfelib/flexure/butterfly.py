from __future__ import annotations

import gdsfactory as gf

import numpy as np

import gfelib as gl


@gf.cell_with_module_name
def butterfly(
    radius_inner: float,
    radius_outer: float,
    width_inner: float,
    width_beam: float,
    angles: tuple[float, float],
    release_inner: bool,
    geometry_layer: gf.typings.LayerSpec,
    angle_resolution: float,
    beam_spec: gl.datatypes.BeamSpec | None,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    """Returns a half-butterfly joint (4 beams)

    Args:
        radius_inner: inner carriage inner radius
        radius_outer: joint outer radius
        width_inner: inner carriage width
        width_beam: beam width
        angles: beam placement angles
        release_inner: `True` to release inner carriage
        geometry_layer: joint polygon layer
        angle_resolution: degrees per point for circular geometries
        beam_spec: complex beam specifications, `None` for default
        release_spec: release specifications, `None` for no release
    """
    c = gf.Component()

    angles = sorted(angles)

    angle_start = angles[0] - 0.5 * width_beam / (radius_inner + width_inner) / (
        np.pi / 180
    )

    _ = c << gl.basic.ring(
        radius=radius_inner + 0.5 * width_inner,
        width=width_inner,
        angles=(angle_start, 180 - angle_start),
        geometry_layer=geometry_layer,
        angle_resolution=angle_resolution,
        release_spec=release_spec if release_inner else None,
    )

    beam_offset = 0.5 * (radius_outer + radius_inner + width_inner)
    beam = gl.flexure.beam(
        length=radius_outer - radius_inner - width_inner + 0.5 * width_beam,
        width=width_beam,
        geometry_layer=geometry_layer,
        beam_spec=beam_spec,
        release_spec=release_spec,
    )
    for a in [angles[0], angles[1], 180 - angles[1], 180 - angles[0]]:
        ref = c << beam
        ref.move((beam_offset, 0)).rotate(a, (0, 0))

    c.flatten()

    return c
