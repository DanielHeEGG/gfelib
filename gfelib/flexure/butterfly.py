from __future__ import annotations

import gdsfactory as gf

import numpy as np

import gfelib as gl


@gl.utils.default_cell
def butterfly(
    radius0: float,
    radius1: float,
    radius2: float,
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
        radius0: inner carriage inner radius
        radius1: inner carriage outer radius
        radius2: flexure outer radius
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

    angle_end = angles[1] + 0.5 * width_beam / radius1 / (np.pi / 180)

    _ = c << gl.basic.ring(
        radius_inner=radius0,
        radius_outer=radius1,
        angles=(-angle_end, angle_end),
        geometry_layer=geometry_layer,
        angle_resolution=angle_resolution,
        release_spec=release_spec if release_inner else None,
    )

    beam_offset = 0.5 * (radius1 + radius2)
    beam = gl.flexure.beam(
        length=radius2
        - radius1
        + 2 * gl.utils.sagitta_offset_safe(radius1, width_beam, angle_resolution),
        width=width_beam,
        geometry_layer=geometry_layer,
        beam_spec=beam_spec,
        release_spec=release_spec,
    )
    for a in [-angles[0], -angles[1], angles[0], angles[1]]:
        ref = c << beam
        ref.move((beam_offset, 0)).rotate(a, (0, 0))

    return c
