from __future__ import annotations
from typing import Literal

import gdsfactory as gf

import numpy as np

import gfelib as gl


@gf.cell_with_module_name
def zlever(
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
    stopper_pos: float | None = None,
    stopper_polarity: Literal["in", "out"] = "out",
    stopper_length: float = 0,
    stopper_width: float = 0,
    stopper_release_specs: gl.datatypes.ReleaseSpec | None = None,
    separator_gap: float = 2,
    separator_margin: float = 5,
) -> gf.Component:
    """Returns a pantographic Z joint (4 torsional beams) with electrical isolation and stopper, used in MEGA devices

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
    _ = c << gl.flexure.zpant(
        width_stage=width_stage,
        length_stage=length_stage,
        width_beam=width_beam,
        length_beam=length_beam,
        geometry_layer=geometry_layer,
        handle_layer=handle_layer,
        handle_offset=handle_offset,
        release_specs=None,
        cavity_layer=cavity_layer,
        cavity_width=cavity_width,
        cavity_length_offset=cavity_length_offset,
    )

    # Object to cut the device layer
    sep = gf.Component()
    sep << gf.components.rectangle(
        size=(separator_gap, length_stage + width_beam),
        layer=geometry_layer,
        centered=True,
    )

    if stopper_pos:
        stopper_center = np.array(
            (
                width_stage / 2 + stopper_length / 2,
                length_stage * (0.5 - stopper_pos + 0.5 * stopper_width),
            )
        )

        if stopper_polarity == "out":
            # Meshed part is outside
            stopper = gl.basic.rectangle(
                size=(stopper_length, length_stage * stopper_width),
                centered=True,
                release_spec=stopper_release_specs,
                geometry_layer=geometry_layer,
            )
        else:
            # Meshed part is inside
            stopper = gf.components.rectangle(
                size=(stopper_length, length_stage * stopper_width),
                centered=True,
                layer=geometry_layer,
            )

        (c << stopper).move(tuple(np.array((1, 1)) * stopper_center))
        (c << stopper).move(tuple(np.array((-1, 1)) * stopper_center))

        # Generate stopper isolation
        # Check that the stopper is wide enough
        assert (
            length_stage * stopper_width >= 2 * stopper_release_specs.distance
        ), ValueError("Stopper is too narrow, will get released")
        iso_left = separator_gap + separator_margin
        iso_right = width_stage / 2 + stopper_length
        r0 = gf.components.rectangle(
            size=(iso_right - iso_left, length_stage * stopper_width),
            layer=geometry_layer,
            centered=True,
        )

        r1 = gf.components.rectangle(
            size=(
                iso_right - iso_left + 2 * separator_gap,
                length_stage * stopper_width + 2 * separator_gap,
            ),
            layer=geometry_layer,
            centered=True,
        )

        r01 = gf.boolean(
            A=r1,
            B=r0,
            operation="A-B",
            layer=geometry_layer,
        )

        iso = gf.Component()
        (iso << r01).move(((iso_left + iso_right) / 2, stopper_center[1]))
        # Emit the ring twice
        sep << iso
        (sep << iso).mirror_x()

        if stopper_polarity == "in":
            # Generate meshed part for inside stopper
            holes = gl.basic.rectangle(
                size=(width_stage / 2 - iso_left, length_stage * stopper_width),
                centered=True,
                release_spec=stopper_release_specs,
                geometry_layer=geometry_layer,
            )
            (c << holes).move(((iso_left + width_stage / 2) / 2, stopper_center[1]))
            (c << holes).move((-(iso_left + width_stage / 2) / 2, stopper_center[1]))

    cnew = gf.boolean(
        c,
        sep,
        "A-B",
        layer=geometry_layer,
        layer1=geometry_layer,
        layer2=geometry_layer,
    )

    # Emit the remaining layers
    cnew << c.remove_layers(layers=[geometry_layer])
    cnew.flatten()
    return cnew
