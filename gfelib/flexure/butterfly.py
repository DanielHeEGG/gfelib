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
    geometry_layer: gf.typings.LayerSpec,
    thick_length: float,
    thick_width: float,
    thick_offset: float,
    release_inner: bool,
    angle_resolution: float,
    release_hole_radius: float,
    release_distance: float,
    release_layer: gf.typings.LayerSpec,
) -> gf.Component:
    """Returns a half-butterfly joint (4 beams)

    Args:
        radius_inner: inner radius of the inner carriage
        radius_outer: outer radius of the joint
        width_inner: width of the inner carriage
        width_beam: width of the beams
        angles: angles to place beams
        geometry_layer: layer to place polygon
        thick_length: length of beam thick section
        thick_width: width of beam thick section
        thick_offset: offset of beam thick section, positive is away from center
        release_inner: `True` to release inner carriage
        angle_resolution: number of degrees per point
        release_hole_radius: radius of the release holes
        release_distance: maximum distance between adjacent release holes
        release_layer: layer to place release holes
    """
    c = gf.Component()

    angles = sorted(angles)

    angle_start = angles[0] - 0.5 * width_beam / (radius_inner + width_inner) / (
        np.pi / 180
    )

    inner_carriage_ref = c << gl.basic.ring(
        radius=radius_inner + 0.5 * width_inner,
        width=width_inner,
        angle=180 - 2 * angle_start,
        geometry_layer=geometry_layer,
        angle_resolution=angle_resolution,
        release_hole_radius=release_hole_radius if release_inner else 0,
        release_distance=release_distance if release_inner else 0,
        release_layer=release_layer,
    )
    inner_carriage_ref.rotate(angle_start, (0, 0))

    beam_offset = 0.5 * (radius_outer + radius_inner + width_inner)
    beam = gl.flexure.beam(
        length=radius_outer - radius_inner - width_inner + 0.5 * width_beam,
        width=width_beam,
        geometry_layer=geometry_layer,
        thick_length=thick_length,
        thick_width=thick_width,
        thick_offset=thick_offset,
        release_hole_radius=release_hole_radius,
        release_distance=release_distance,
        release_layer=release_layer,
    )
    for a in [angles[0], angles[1], 180 - angles[1], 180 - angles[0]]:
        ref = c << beam
        ref.move((beam_offset, 0)).rotate(a, (0, 0))

    c.flatten()

    return c
