import gdsfactory as gf
import numpy as np
from gfelib import released, flexure


@gf.cell_with_module_name
def butterfly_half(
    radius_outer: float,
    radius_inner: float,
    width_beam: float,
    width_inner: float,
    angles: tuple[float, float] = (30.0, 60.0),
    thicken: bool = False,
    thick_ratio: float = 0,
    thick_width: float = 0,
    layer: gf.typings.LayerSpec = 0,
    **kwargs,
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
        geometry_layer: layer to place device
        release_hole_radius: radius of the release holes
        release_distance: maximum distance between adjacent release holes
        release_layer: layer to place release holes

    Keyword Args:
        hollow_inner: whether to put release holes on the inner intermediate stage (False)
    """
    hollow_inner: bool = kwargs.get("hollow_inner", False)
    release_hole_radius: float = kwargs.get("release_hole_radius", 0)
    release_distance: float = kwargs.get("release_distance", 1)
    release_layer: gf.typings.LayerSpec = kwargs.get("release_layer", 1)
    angle_resolution: float = kwargs.get("angle_resolution", 1)

    c = gf.Component()

    angles = sorted(angles)

    # Emit inner intermediate stage
    rmid_inner = radius_inner + width_inner / 2
    start_angle = angles[0] - width_beam / 2 / (radius_inner + width_inner) / (
        np.pi / 180
    )
    end_angle = 180 - start_angle
    if hollow_inner:
        ref = c << released.ring(
            radius=rmid_inner,
            width=width_inner,
            angle=end_angle - start_angle,
            geometry_layer=layer,
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
            layer=layer,
            angle_resolution=angle_resolution,
        )
    ref.rotate(start_angle, (0, 0))

    # Emit four beams
    length_beam = (
        radius_outer - radius_inner - width_inner + width_beam / 2
    )  # Compensate difference between arc and line
    rmid_beam = (radius_outer + radius_inner + width_inner) / 2
    beam = flexure.beam(
        length=length_beam,
        width=width_beam,
        thicken=thicken,
        thick_ratio=thick_ratio,
        thick_width=thick_width,
        layer=layer,
        **kwargs,
    )
    (c << beam).move((rmid_beam, 0)).rotate(angles[0], (0, 0))
    (c << beam).move((rmid_beam, 0)).rotate(angles[1], (0, 0))
    (c << beam).move((rmid_beam, 0)).rotate(180 - angles[0], (0, 0))
    (c << beam).move((rmid_beam, 0)).rotate(180 - angles[1], (0, 0))

    c.flatten()
    return c
