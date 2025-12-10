from __future__ import annotations

import gdsfactory as gf

import gfelib as gl


@gf.cell_with_module_name
def chip_border(
    size: tuple[float, float],
    margin: float,
    width_mesh: float,
    width_cavity: float,
    geometry_layer: gf.typings.LayerSpec,
    cavity_layer: gf.typings.LayerSpec,
    release_specs: gl.datatypes.ReleaseSpec | None = None,
) -> gf.Component:
    """Returns a releasable chip

    Args:
        size: size of the chip (width, height)
        margin: width of the frame on each side
        width)mesh: width of the mesh
        width_cavity: width of the cavity (handle etch)
        geometry_layer: layer to put device
        cavity_layer: layer to put handle etch
        release_specs: release specs. If None, no holes will be generated
    """
    c = gf.Component()

    chip = gf.components.rectangle(size=size, layer=geometry_layer, centered=True)

    opening = gf.components.rectangle(
        size=(size[0] - 2 * margin, size[1] - 2 * margin),
        layer=geometry_layer,
        centered=True,
    )

    c << gf.boolean(
        chip,
        opening,
        operation="A-B",
        layer=geometry_layer,
    )

    meshbar_x = gl.basic.rectangle(
        size=(size[0] - 2 * margin - width_mesh, width_mesh),
        geometry_layer=geometry_layer,
        centered=True,
        release_spec=release_specs,
    )
    meshbar_y = gl.basic.rectangle(
        size=(width_mesh, size[1] - 2 * margin - width_mesh),
        geometry_layer=geometry_layer,
        centered=True,
        release_spec=release_specs,
    )

    (c << meshbar_x).move((-width_mesh / 2, (size[1] - 2 * margin - width_mesh) / 2))
    (c << meshbar_x).move((width_mesh / 2, -(size[1] - 2 * margin - width_mesh) / 2))
    (c << meshbar_y).move((-(size[0] - 2 * margin - width_mesh) / 2, -width_mesh / 2))
    (c << meshbar_y).move(((size[0] - 2 * margin - width_mesh) / 2, width_mesh / 2))

    handle0 = gf.components.rectangle(
        size=(
            size[0] - 2 * margin + width_cavity - width_mesh,
            size[1] - 2 * margin + width_cavity - width_mesh,
        ),
        layer=cavity_layer,
        centered=True,
    )
    handle1 = gf.components.rectangle(
        size=(
            size[0] - 2 * margin - width_cavity - width_mesh,
            size[1] - 2 * margin - width_cavity - width_mesh,
        ),
        layer=cavity_layer,
        centered=True,
    )

    c << gf.boolean(
        handle0,
        handle1,
        operation="A-B",
        layer=cavity_layer,
    )

    c.flatten()
    return c
