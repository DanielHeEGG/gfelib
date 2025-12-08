import gfelib as gl
import gfelib.datatypes as gfd
import gdsfactory as gf
import numpy as np
from gfelib.pdk import LAYER

# Default gap size and wire size
gap_size = 10
wire_size = 20

# Default angular resolutions
angle_resolution_high = 1.0
angle_resolution_low = 36.0

# Release distance
release_distance = 6

# Default label size
label_size = 150

# Label text
label_text = "MEGA2D V55 2026"

# Size of chip
chip_size = (6000.0, 6000.0)
# Frame margin on device layer
chip_margin = 100
# Release hole region width
chip_mesh_width = 100
# Usable size
chip_size_usable = tuple(
    np.array(chip_size) - 2 * (chip_margin + chip_mesh_width + gap_size)
)

# Release hole parameters
rs = gfd.ReleaseSpec(
    hole_radius=3,
    distance=release_distance,
    layer=LAYER.device_etch,
    angle_resolution=angle_resolution_low,
)

# Beam parameters for butterfly joint
bs = gfd.BeamSpec(thick_length=(0, 0.7), thick_offset=(0, 0), thick_width=(20, 0))


# Default cavity trench width
handle_cavity_width = 50

# Z Lever parameters
zlever_len_stage = 500
zlever_width_stage = 200
zlever_width_beam = 12
zlever_len_beam = 100
zlever_pos = 1700
zlever_stop = {
    "pos": [0.8, 0.4],
    "len": [100, 70],
    "pol": ["in", "out"],
    "width": [0.1, 0.1],
    "release_spec": rs,
}
zlever_cavity_offset = 0
zlever_handle_offset = 0
zlever_separator_gap = gap_size
zlever_separator_margin = wire_size

# Z Platform parameters

zplat_radius_outer = 1500.0
zplat_radius_inner = 1200.0
zplat_conn_width = 100
zplat_anchor_size = (100, 300)
zplat_anchor_yoffset = -110


def build_label() -> gf.Component:
    """Creates label text at the upper-left corner of the chip"""
    c = gf.Component(name="label")
    c << gf.components.text(
        text=label_text,
        size=label_size,
        position=(0, 0),
        justify="center",
        layer=LAYER.device_etch,
    )
    textwidth = c.bbox().width()
    (
        c
        << gf.components.rectangle(
            size=(textwidth + 2 * gap_size, label_size + 2 * gap_size),
            centered=True,
            layer=LAYER.device,
        )
    ).move((0, label_size / 2))

    c.move(
        (
            -chip_size_usable[0] / 2 + textwidth / 2 + gap_size,
            chip_size_usable[1] / 2 - label_size - gap_size,
        )
    )
    return c


def build_pads():
    pass


def build_zstage():
    """
    Builds the Z pantographic stage, stage ring
    """
    c = gf.Component(name="ZStage")

    zlever = gl.mega.zlever(
        width_stage=zlever_width_stage,
        length_stage=zlever_len_stage,
        width_beam=zlever_width_beam,
        length_beam=zlever_len_beam,
        geometry_layer=LAYER.device,
        handle_layer=LAYER.handle,
        handle_offset=zlever_handle_offset,
        cavity_layer=LAYER.handle_etch,
        cavity_width=handle_cavity_width,
        cavity_length_offset=zlever_cavity_offset,
        stopper_length=zlever_stop["len"],
        stopper_polarity=zlever_stop["pol"],
        stopper_width=zlever_stop["width"],
        stopper_pos=zlever_stop["pos"],
        stopper_release_specs=zlever_stop["release_spec"],
        separator_gap=zlever_separator_gap,
        separator_margin=zlever_separator_margin,
    )

    # Connection between ring and zstage
    conn = gf.Component()
    connWidth = zlever_width_stage + 2 * zlever_len_beam + 2 * zplat_conn_width
    (
        conn
        << gf.components.rectangle(
            size=(connWidth, zlever_pos - zplat_radius_inner - 2 * gap_size),
            centered=True,
            layer=LAYER.handle,
        )
    ).move((0, (zlever_pos + zplat_radius_inner - 2 * gap_size) / 2))
    device_anchor = gf.components.rectangle(
        size=zplat_anchor_size,
        centered=True,
        layer=LAYER.device,
    )
    (conn << device_anchor).move(
        (
            (zplat_anchor_size[0] + zlever_width_stage) / 2 + zlever_len_beam,
            zlever_pos + zplat_anchor_yoffset,
        )
    )
    (conn << device_anchor).move(
        (
            -(zplat_anchor_size[0] + zlever_width_stage) / 2 - zlever_len_beam,
            zlever_pos + zplat_anchor_yoffset,
        )
    )

    # Generate 4 copies
    for ang in [0, 90, 180, 270]:
        (c << zlever).move((0, zlever_pos + zlever_len_stage / 2)).rotate(ang, (0, 0))
        (c << conn).rotate(ang, (0, 0))

    _ = c << gf.components.ring(
        radius=(zplat_radius_outer + zplat_radius_inner) / 2,
        width=(zplat_radius_outer - zplat_radius_inner),
        angle_resolution=angle_resolution_high,
        layer=LAYER.handle,
    )

    c.flatten()

    return c


def build_rotator():
    c = gf.Component()
    c << gl.actuator.rotator_gear(
        radius_inner=1000,
        radius_outer=1500,
        width_inner=50,
        teeth_pitch=3,
        teeth_width=2.5,
        teeth_height=7,
        teeth_clearance=3.0,
        teeth_phase=(-1 / 3, 0, 1 / 3),
        teeth_count=60,
        inner_rotor=True,
        rotor_span=160,
        geometry_layer=LAYER.device,
        angle_resolution=1.0,
        release_spec=rs,
    )
    return c


def build_interconnects():
    pass


def build_MEGA2D() -> gf.Component:
    c = gf.Component()

    # Emit chip border
    c << gl.mega.chip(
        size=chip_size,
        margin=chip_margin,
        width_mesh=chip_mesh_width,
        width_cavity=handle_cavity_width,
        geometry_layer=LAYER.device,
        cavity_layer=LAYER.handle_etch,
        release_specs=rs,
    )

    # Emit label
    c << build_label()

    # Emit zstage
    c << build_zstage()

    # Emit rotator
    c << build_rotator()

    return c
