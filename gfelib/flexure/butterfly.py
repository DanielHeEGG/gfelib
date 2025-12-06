import gdsfactory as gf

import numpy as np

import gfelib as gl


@gf.cell_with_module_name
def butterfly(
    radius_outer: float,
    radius_inner: float,
    width_beam: float,
    width_inner: float,
    angles: tuple[float, float] = (30.0, 60.0),
    thicken: bool = False,
    thick_ratio: float = 0,
    thick_width: float = 0,
    release_hole_on_inner_carriage: bool = True,
    angle_resolution: float = 1,
    geometry_layer: gf.typings.LayerSpec = 0,
    release_hole_radius: float = 0,
    release_distance: float = 1,
    release_layer: gf.typings.LayerSpec = 1,
) -> gf.Component:
    """Returns a half-butterfly joint (4 beams)

    Args:
        radius_outer: OD of the joint
        radius_inner: ID of the joint
        angles: 2-tuple of the beam angles (typically (30, 60))
        width_beam: width of thin part of beam
        width_inner: width of inner intermediate stage
        thicken: whether to thicken middle part of beam
        thick_ratio: ratio of thickened part
        thick_width: width of thickened part
        release_hole_on_inner_carriage: whether to hollow the inner intermediate stage
        geometry_layer: layer to place device
        release_hole_radius: radius of the release holes
        release_distance: maximum distance between adjacent release holes
        release_layer: layer to place release holes
    """
    c = gf.Component()

    angles = sorted(angles)

    # Emit inner intermediate stage
    rmid_inner = radius_inner + width_inner / 2
    start_angle = angles[0] - width_beam / 2 / (radius_inner + width_inner) / (
        np.pi / 180
    )
    end_angle = 180 - start_angle
    if release_hole_on_inner_carriage:
        ref = c << gl.basic.ring(
            radius=rmid_inner,
            width=width_inner,
            angle=end_angle - start_angle,
            geometry_layer=geometry_layer,
            release_distance=release_distance,
            release_hole_radius=release_hole_radius,
            release_layer=release_layer,
            angle_resolution=angle_resolution,
        )
    else:
        ref = c << gf.components.ring(
            radius=rmid_inner,
            width=width_inner,
            angle=end_angle - start_angle,
            layer=geometry_layer,
            angle_resolution=angle_resolution,
        )
    ref.rotate(start_angle, (0, 0))

    # Emit four beams
    length_beam = (
        radius_outer - radius_inner - width_inner + width_beam / 2
    )  # Compensate difference between arc and line
    rmid_beam = (radius_outer + radius_inner + width_inner) / 2
    beam = gl.flexure.beam(
        length=length_beam,
        width=width_beam,
        thicken=thicken,
        thick_ratio=thick_ratio,
        thick_width=thick_width,
        geometry_layer=geometry_layer,
        release_layer=release_layer,
        release_hole_radius=release_hole_radius,
        release_distance=release_distance,
    )
    (c << beam).move((rmid_beam, 0)).rotate(angles[0], (0, 0))
    (c << beam).move((rmid_beam, 0)).rotate(angles[1], (0, 0))
    (c << beam).move((rmid_beam, 0)).rotate(180 - angles[0], (0, 0))
    (c << beam).move((rmid_beam, 0)).rotate(180 - angles[1], (0, 0))

    c.flatten()
    return c
