from __future__ import annotations

import gdsfactory as gf

import numpy as np

import gfelib as gl


@gf.cell_with_module_name
def zpant(
    width_stage: float,
    length_stage: float,
    width_beam: float,
    length_beam: float,
    geometry_layer: gf.typings.LayerSpec,
    handle_layer: gf.typings.LayerSpec | None = None,
    handle_offset: float = 0,
    cavity_layer: gf.typings.LayerSpec | None = None,
    cavity_width: float = 0,
    cavity_length_offset: float = 0,
    release_specs: gl.datatypes.ReleaseSpec | None = None,
) -> gf.Component:
    """Returns a pantographic Z joint (4 torsional beams), with handle layer generation options

    Args:
        width_stage: width of stage (X direction)
        length_stage: length of stage (Y direction)
        width_beam: width of the beam (Y direction)
        length_beam: length of the beam (X direction)
        geometry_layer: layer to generate the pattern
        handle_layer: if not None, generate a rectangular block beneath the stage on this layer
        handle_offset: When handle_layer is not None, this controls the size of the rectangular block relative to the stage size
        cavity_layer: layer to generate cavity beneath the beams
        cavity_width: width of the cavities beneath the beams
        cavity_length_offset: length offset of the cavities
        release_specs: if not None, the stage will be made hollow by adding release holes according to the specs.
            Handle layer block generation is automatically disabled in this case

    """
    c = gf.Component()

    if not release_specs:
        # No release hole
        _ = c << gf.components.rectangle(
            size=(width_stage, length_stage + width_beam),
            layer=geometry_layer,
            centered=True,
        )
        if handle_layer:
            # Generate handle layer block if specified
            _ = c << gf.components.rectangle(
                size=(
                    width_stage + 2 * handle_offset,
                    length_stage + width_beam + 2 * handle_offset,
                ),
                layer=handle_layer,
                centered=True,
            )
    else:
        # With release holes
        _ = c << gl.basic.rectangle(
            size=(width_stage, length_stage + width_beam),
            geometry_layer=geometry_layer,
            centered=True,
            release_spec=release_specs,
        )

    # Generate four flexure beams
    beam_center_pos = np.array((width_stage / 2 + length_beam / 2, length_stage / 2))
    beam = gl.flexure.beam_cavity(
        length=length_beam,
        width=width_beam,
        geometry_layer=geometry_layer,
        cavity_layer=cavity_layer,
        cavity_width=cavity_width,
        cavity_length_offset=cavity_length_offset,
    )
    (c << beam).move(tuple(np.array([1, 1]) * beam_center_pos))
    (c << beam).move(tuple(np.array([1, -1]) * beam_center_pos))
    (c << beam).move(tuple(np.array([-1, -1]) * beam_center_pos))
    (c << beam).move(tuple(np.array([-1, 1]) * beam_center_pos))

    c.flatten()

    return c
