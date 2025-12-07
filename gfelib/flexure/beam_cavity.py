from __future__ import annotations

import gdsfactory as gf

import gfelib as gl


@gf.cell_with_module_name
def beam_cavity(
    length: float,
    width: float,
    geometry_layer: gf.typings.LayerSpec,
    etch_layer: gf.typings.LayerSpec | None = None,
    etch_width: float = 0,
    etch_length_offset: float = 0,
) -> gf.Component:
    """Returns a beam that is suspended without using release holes, centered at (0, 0). Generates cavity on handle_etch layer optinally

    **Warning**: release holes are never added to thin sections of the beam, regardless of dimensions

    Args:
        length: beam length (x)
        width: beam width (y)
        geometry_layer: beam polygon layer
        etch_layer: layer for handle cavity etch. `None` to omit cavity
        etch_width: width of cavity. 0 to omit cavity
        etch_length_offset: offset to the cavity length. 0 will generate cavity same length as beam
    """
    c = gf.Component()

    _ = c << gf.components.rectangle(
        size=(length, width),
        layer=geometry_layer,
        centered=True,
    )

    if etch_layer and etch_width:
        _ = c << gf.components.rectangle(
            size=(length + etch_length_offset, etch_width),
            layer=etch_layer,
            centered=True,
        )

    c.flatten()
    return c
