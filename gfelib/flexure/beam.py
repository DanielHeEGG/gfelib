from __future__ import annotations

import gdsfactory as gf

import gfelib as gl


@gf.cell_with_module_name
def beam(
    length: float,
    width: float,
    geometry_layer: gf.typings.LayerSpec,
    release_spec: gl.datatypes.ReleaseSpec | None,
    thick_length: float = 0,
    thick_width: float = 0,
    thick_offset: float = 0,
) -> gf.Component:
    """Returns a beam with optional thick mid-section, centered at (0, 0)

    Args:
        length: length (x) of beam
        width: width (y) of beam
        geometry_layer: layer to place polygon
        thick_length: length (x) of thick section
        thick_width: width (y) of thick section
        thick_offset: offset of thick section from center, in x-direction
        release_spec: release specifications, `None` for no release
    """
    c = gf.Component()

    if thick_length == 0 or thick_width == width:
        _ = c << gl.basic.rectangle(
            size=(length, width),
            geometry_layer=geometry_layer,
            centered=True,
            release_spec=release_spec,
        )
        return c

    thin_length = 0.5 * (length - thick_length)
    thin_center = 0.5 * (thick_length + thin_length)

    rect_thick_ref = c << gl.basic.rectangle(
        size=(thick_length, thick_width),
        geometry_layer=geometry_layer,
        centered=True,
        release_spec=release_spec,
    )
    rect_thick_ref.movex(thick_offset)

    rect_thin1_ref = c << gl.basic.rectangle(
        size=(thin_length + thick_offset, width),
        geometry_layer=geometry_layer,
        centered=True,
        release_spec=release_spec,
    )
    rect_thin1_ref.movex(-thin_center + 0.5 * thick_offset)

    rect_thin2_ref = c << gl.basic.rectangle(
        size=(thin_length - thick_offset, width),
        geometry_layer=geometry_layer,
        centered=True,
        release_spec=release_spec,
    )
    rect_thin2_ref.movex(thin_center + 0.5 * thick_offset)

    c.flatten()

    return c
