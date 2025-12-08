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
    stopper_pos: float | list[float] | None = None,
    stopper_polarity: Literal["in", "out"] | list[Literal["in", "out"]] = "out",
    stopper_length: float | list[float] = 0,
    stopper_width: float | list[float] = 0,
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
        stopper_pos: Edge position(s) of stoppers (in fraction of length_stage). If None, skip stoppers. Can be a list for multiple stoppers
        stopper_polarity: "out" for holes outside, "in" for holes inside. Can be a list
        stopper_length: length (x) of stopper that extends out of the stage. Can be a list
        stopper_width: width (y) of stopper (in fraction of length_stage). Can be a list
        stopper_release_specs: Release hole specs for holes on the stopper. If None, no hole is generated
        separator_gap: Gap between electrically isolated parts
        separator_margin: Central clearance width

    """
    if stopper_pos:
        if not isinstance(stopper_pos, list):
            stopper_pos: list[float] = [stopper_pos]
        if not isinstance(stopper_length, list):
            stopper_length: list[float] = [stopper_length]
        if not isinstance(stopper_width, list):
            stopper_width: list[float] = [stopper_width]
        if not isinstance(stopper_polarity, list):
            stopper_polarity: list[Literal["in", "out"]] = [stopper_polarity]

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
        min_stop_frac = (0.5 * width_beam + separator_gap) / length_stage
        max_stop_frac = 1 - min_stop_frac
        for spos, spol, slen, swid in zip(
            stopper_pos, stopper_polarity, stopper_length, stopper_width
        ):
            assert min_stop_frac <= spos <= max_stop_frac, ValueError(
                f"Stopper position must be between {min_stop_frac} and {max_stop_frac}"
            )
            if spol == "out":
                if swid == -1:
                    swid = spos - min_stop_frac
                else:
                    assert spos - swid >= min_stop_frac, ValueError(
                        f"stopper_position - stopper_width must be >= {min_stop_frac}"
                    )
            else:
                if swid == -1:
                    swid = max_stop_frac - spos
                else:
                    assert spos + swid <= max_stop_frac, ValueError(
                        f"stopper_position + stopper_width must be <= {max_stop_frac}"
                    )
            stopper_center = np.array(
                (
                    width_stage / 2 + slen / 2,
                    (
                        length_stage * (0.5 - spos + 0.5 * swid)
                        if spol == "out"
                        else length_stage * (0.5 - spos - 0.5 * swid)
                    ),
                )
            )

            if spol == "out":
                # Meshed part is outside
                stopper = gl.basic.rectangle(
                    size=(slen, length_stage * swid),
                    centered=True,
                    release_spec=stopper_release_specs,
                    geometry_layer=geometry_layer,
                )
            else:
                # Meshed part is inside
                stopper = gf.components.rectangle(
                    size=(slen, length_stage * swid),
                    centered=True,
                    layer=geometry_layer,
                )

            (c << stopper).move(tuple(np.array((1, 1)) * stopper_center))
            (c << stopper).move(tuple(np.array((-1, 1)) * stopper_center))

            # Generate stopper isolation
            # Check that the stopper is wide enough
            if stopper_release_specs:
                assert (
                    length_stage * swid >= 2 * stopper_release_specs.distance
                ), ValueError("Stopper is too narrow, will get released")
            iso_left = separator_gap + separator_margin
            iso_right = width_stage / 2 + slen
            r0 = gf.components.rectangle(
                size=(iso_right - iso_left, length_stage * swid),
                layer=geometry_layer,
                centered=True,
            )

            r1 = gf.components.rectangle(
                size=(
                    iso_right - iso_left + 2 * separator_gap,
                    length_stage * swid + 2 * separator_gap,
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

            if spol == "in" and stopper_release_specs:
                # Generate meshed part for inside stopper
                holes_right = max(width_stage / 2, width_stage / 2 + handle_offset)
                holes = gl.basic.rectangle(
                    size=(holes_right - iso_left, length_stage * swid),
                    centered=True,
                    release_spec=stopper_release_specs,
                    geometry_layer=geometry_layer,
                )
                (c << holes).move(((iso_left + holes_right) / 2, stopper_center[1]))
                (c << holes).move((-(iso_left + holes_right) / 2, stopper_center[1]))

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
