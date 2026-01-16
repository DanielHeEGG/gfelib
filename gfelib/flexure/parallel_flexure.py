from __future__ import annotations

import gdsfactory as gf

import numpy as np

import gfelib as gl


@gl.utils.default_cell
def parallel_flexure(
    length_beam: float,
    width_beam: float,
    length_bar: float,
    width_bar: float,
    beam_pos: list[float],
    geometry_layer: gf.typings.LayerSpec,
    beam_spec: gl.datatypes.BeamSpec | None,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    """Returns a parallel flexure (arbitrary number of beams)

    Args:
        length_beam: Length of each beam
        width_beam: Width of each beam
        length_bar: Total length of the intermediate stage bar
        width_bar: Width of the intermediate stage bar
        beam_pos: list of fractional beam positions. 0 is the leftmost end of the bar, 1 is the rightmost end of the bar
        geometry_layer: layer to generate pattern
        beam_spec: complex beam specifications, `None` for default
        release_spec: release specifications for the bar (optionally also for the beam), `None` for no release
    """
    c = gf.Component()

    rect = c << gl.basic.rectangle(
        size=(length_bar, width_bar),
        geometry_layer=geometry_layer,
        centered=True,
        release_spec=release_spec,
    )
    rect.movey(width_bar / 2 + length_beam)

    beam = gl.flexure.beam(
        length=length_beam,
        width=width_beam,
        geometry_layer=geometry_layer,
        beam_spec=beam_spec,
        release_spec=release_spec,
    )
    for pos in beam_pos:
        x_pos = (pos - 0.5) * length_bar
        if x_pos < -length_bar / 2 + width_beam / 2:
            x_pos = -length_bar / 2 + width_beam / 2
        elif x_pos > length_bar / 2 - width_beam / 2:
            x_pos = length_bar / 2 - width_beam / 2
        (c << beam).rotate(90).move((x_pos, length_beam / 2))

    return c
