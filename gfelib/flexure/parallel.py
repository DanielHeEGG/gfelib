from __future__ import annotations

import gdsfactory as gf

import numpy as np
from collections.abc import Sequence

import gfelib as gl


@gl.utils.default_cell
def parallel(
    bar_length: float,
    bar_width: float,
    beam_length: float,
    beam_width: float,
    beam_pos: Sequence[float],
    geometry_layer: gf.typings.LayerSpec,
    beam_spec: gl.datatypes.BeamSpec | None,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    """Returns a simple parallel flexure with any number of identical beams, south-center of bar is (0, 0)

    Args:
        bar_length: bar length (x)
        bar_width: bar width (y)
        beam_length: beam length (y)
        beam_width: beam width (x)
        beam_pos: list of fractional beam positions (x), where `0` is the leftmost end of the bar, `1` is the rightmost end of the bar
        geometry_layer: flexure polygon layer
        beam_spec: complex beam specifications, `None` for default
        release_spec: release specifications, `None` for no release
    """
    c = gf.Component()

    rect_ref = c << gl.basic.rectangle(
        size=(bar_length, bar_width),
        geometry_layer=geometry_layer,
        centered=True,
        release_spec=release_spec,
    )
    rect_ref.movey(0.5 * bar_width)

    beam = gl.flexure.beam(
        length=beam_length,
        width=beam_width,
        geometry_layer=geometry_layer,
        beam_spec=beam_spec,
        release_spec=release_spec,
    )
    for pos in beam_pos:
        x_pos = (pos - 0.5) * bar_length
        x_lim = 0.5 * bar_length - 0.5 * beam_width
        x_pos = -x_lim if x_pos < -x_lim else x_pos
        x_pos = x_lim if x_pos > x_lim else x_pos
        beam_ref = c << beam
        beam_ref.rotate(90)
        beam_ref.move((x_pos, bar_width + 0.5 * beam_length))

    return c
