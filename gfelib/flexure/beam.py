from __future__ import annotations

import gdsfactory as gf

import gfelib as gl


@gl.utils.default_cell
def beam(
    length: float,
    width: float,
    geometry_layer: gf.typings.LayerSpec,
    beam_spec: gl.datatypes.BeamSpec | None,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    """Returns a complex beam, centered at (0, 0)

    **Warning**: if beam_spec is not specified, release holes are never added to the beam, regardless of dimensions

    Args:
        length: beam length (x)
        width: beam width (y)
        geometry_layer: beam polygon layer
        beam_spec: complex beam specifications, `None` for default
        release_spec: release specifications, `None` for no release
    """
    c = gf.Component()

    if beam_spec is None:
        _ = c << gl.basic.rectangle(
            size=(length, width),
            geometry_layer=geometry_layer,
            centered=True,
            release_spec=None,
        )
        return c

    if beam_spec.handle_etched:
        handle_rect = c << gl.basic.rectangle(
            size=(
                beam_spec.get_handle_etch_length(length),
                beam_spec.get_handle_etch_width(width),
            ),
            geometry_layer=beam_spec.handle_etch_layer,
            centered=True,
            release_spec=None,
        )
        handle_rect.movex(beam_spec.get_handle_etch_offset(length))

    if not beam_spec.thickened:
        _ = c << gl.basic.rectangle(
            size=(length, width),
            geometry_layer=geometry_layer,
            centered=True,
            release_spec=release_spec if beam_spec.release_thin else None,
        )
        return c

    thick_length = beam_spec.get_thick_length(length)
    thick_width = beam_spec.get_thick_width(width)
    thick_offset = beam_spec.get_thick_offset(length)

    thin_length = 0.5 * (length - thick_length)
    thin_center = 0.5 * (thick_length + thin_length)

    rect_thick_ref = c << gl.basic.rectangle(
        size=(thick_length, thick_width),
        geometry_layer=geometry_layer,
        centered=True,
        release_spec=release_spec if beam_spec.release_thick else None,
    )
    rect_thick_ref.movex(thick_offset)

    rect_thin1_ref = c << gl.basic.rectangle(
        size=(thin_length + thick_offset, width),
        geometry_layer=geometry_layer,
        centered=True,
        release_spec=release_spec if beam_spec.release_thin else None,
    )
    rect_thin1_ref.movex(-thin_center + 0.5 * thick_offset)

    rect_thin2_ref = c << gl.basic.rectangle(
        size=(thin_length - thick_offset, width),
        geometry_layer=geometry_layer,
        centered=True,
        release_spec=release_spec if beam_spec.release_thin else None,
    )
    rect_thin2_ref.movex(thin_center + 0.5 * thick_offset)

    return c
