from __future__ import annotations

import gdsfactory as gf

import numpy as np
from collections.abc import Sequence

import gfelib as gl


@gf.cell_with_module_name
def rotator_gear(
    radius_inner: float,
    radius_outer: float,
    width_inner: float,
    teeth_pitch: float,
    teeth_width: float,
    teeth_height: float,
    teeth_clearance: float,
    teeth_phase: Sequence[float],
    teeth_count: int,
    inner_rotor: bool,
    rotor_span: float,
    geometry_layer: gf.typings.LayerSpec,
    angle_resolution: float,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    """Returns a half-rotator actuator

    **Warning**: release holes are never added to the electrostatic teeth, regardless of dimensions

    Args:
        radius_inner: inner carriage inner radius
        radius_outer: outer carriage outer radius
        width_inner: inner carriage width
        teeth_pitch: electrostatic teeth pitch, in units of length
        teeth_width: electrostatic teeth width, in units of length
        teeth_height: electrostatic teeth height
        teeth_clearance: teeth clearance between stator and rotor
        teeth_phase: phase offsets for each bank of teeth (unit: degrees)
        teeth_count: number of teeth per bank
        inner_rotor: `True` sets inner carriage as rotor nad outer carriage as stator, vice versa
        rotor_span: angular width of the rotor carriage (unit: degrees)
        geometry_layer: actuator polygon layer
        angle_resolution: degrees per point for circular geometries
        release_spec: release specifications, `None` for no release
    """
    c = gf.Component()

    radius_teeth_inner = radius_inner + width_inner
    radius_teeth_outer = radius_teeth_inner + 2 * teeth_height + teeth_clearance
    teeth_width_angle = teeth_width / radius_teeth_inner / (np.pi / 180)
    teeth_pitch_angle = teeth_pitch / radius_teeth_inner / (np.pi / 180)

    stator_teeth_angles = []
    angle_offset = 0
    for phase in teeth_phase:
        angle_offset += phase * teeth_pitch_angle / 360
        phase_angles = []
        for _ in range(teeth_count):
            phase_angles.append(angle_offset)
            angle_offset += teeth_pitch_angle
        angle_offset -= phase * teeth_pitch_angle / 360
        stator_teeth_angles.append(phase_angles)
    stator_offset = -0.5 * angle_offset + 0.5 * teeth_pitch_angle

    rotor_radius = radius_inner + 0.5 * width_inner
    rotor_width = width_inner
    rotor_teeth_x = radius_teeth_inner + 0.4 * teeth_height
    stator_radius = 0.5 * (radius_teeth_outer + radius_outer)
    stator_width = radius_outer - radius_teeth_outer
    stator_teeth_x = radius_teeth_outer - 0.4 * teeth_height
    if not inner_rotor:
        rotor_radius, stator_radius = stator_radius, rotor_radius
        rotor_width, stator_width = stator_width, rotor_width
        rotor_teeth_x, stator_teeth_x = stator_teeth_x, rotor_teeth_x

    teeth = gf.components.rectangle(
        size=(teeth_height * 1.1, teeth_width),
        layer=geometry_layer,
        centered=True,
    )

    # rotor ring
    _ = c << gl.basic.ring(
        radius=rotor_radius,
        width=rotor_width,
        angles=(-0.5 * rotor_span, 0.5 * rotor_span),
        geometry_layer=geometry_layer,
        angle_resolution=angle_resolution,
        release_spec=release_spec,
    )

    # rotor teeth
    for angle in np.arange(
        0.5 * teeth_pitch_angle,
        0.5 * (rotor_span - teeth_pitch_angle),
        teeth_pitch_angle,
    ):
        ref_pos = c << teeth
        ref_pos.movex(rotor_teeth_x)
        ref_pos.rotate(angle, (0, 0))
        ref_neg = c << teeth
        ref_neg.movex(rotor_teeth_x)
        ref_neg.rotate(-angle, (0, 0))

    for phase in stator_teeth_angles:
        # stator ring
        ring_ref = c << gl.basic.ring(
            radius=stator_radius,
            width=stator_width,
            angles=(
                phase[0] - 0.5 * teeth_width_angle,
                phase[-1] + 0.5 * teeth_width_angle,
            ),
            geometry_layer=geometry_layer,
            angle_resolution=angle_resolution,
            release_spec=None,
        )
        ring_ref.rotate(stator_offset, (0, 0))

        # stator teeth
        for angle in phase:
            ref = c << teeth
            ref.movex(stator_teeth_x)
            ref.rotate(angle + stator_offset, (0, 0))

    c.flatten()
    return c
