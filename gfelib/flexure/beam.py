import gdsfactory as gf
import numpy as np
from gfelib.basic import rectangle


@gf.cell_with_module_name
def beam(
    length: float,
    width: float,
    thicken: bool,
    thick_ratio: float,
    thick_width: float,
    geometry_layer: gf.typings.LayerSpec,
    release_hole_radius: float,
    release_distance: float,
    release_layer: gf.typings.LayerSpec,
) -> gf.Component:
    """Returns a beam with optional thickened part with release holes

    Args:
        size: width and height of rectangle
        geometry_layer: layer to place polygon
        centered: `True` sets center to (0, 0), `False` sets south-west to (0, 0)
        release_hole_radius: radius of the release holes
        release_distance: maximum distance between adjacent release holes
        release_layer: layer to place release holes
    """
    c = gf.Component()

    if not thicken:
        c << gf.components.rectangle(
            size=(length, width),
            layer=geometry_layer,
            centered=True,
        )
        return c

    thin_len = (1 - thick_ratio) * length / 2
    thick_len = thick_ratio * length
    thin_center = (thick_len + thin_len) / 2
    # Emit thickened rectangle
    c << rectangle(
        size=(thick_len, thick_width),
        geometry_layer=geometry_layer,
        centered=True,
        release_hole_radius=release_hole_radius,
        release_distance=release_distance,
        release_layer=release_layer,
    )
    # Emit thin sections
    (
        c
        << gf.components.rectangle(
            size=(thin_len, width), layer=geometry_layer, centered=True
        )
    ).move((thin_center, 0))

    (
        c
        << gf.components.rectangle(
            size=(thin_len, width), layer=geometry_layer, centered=True
        )
    ).move((-thin_center, 0))

    c.flatten()
    return c
