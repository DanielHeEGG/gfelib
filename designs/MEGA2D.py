import gfelib as gl
import gfelib.datatypes as gfd
import gdsfactory as gf
import numpy as np
from gfelib.pdk import LAYER

# Default gap for general separation
gap_size = 10

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

# Default cavity trench width
handle_cavity_width = 50

# Release parameters
rs = gfd.ReleaseSpec(
    hole_radius=3, distance=6, layer=LAYER.device_etch, angle_resolution=18
)

# Beam parameters for butterfly joint
bs = gfd.BeamSpec(thick_length=(0, 0.7), thick_offset=(0, 0), thick_width=(20, 0))


def build_label() -> gf.Component:
    c = gf.Component()
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

    return c
