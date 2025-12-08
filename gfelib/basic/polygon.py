from __future__ import annotations

import gdsfactory as gf

import numpy as np

import gfelib as gl


@gf.cell_with_module_name
def polygon(
    points: tuple[tuple[float, float], ...],
    geometry_layer: gf.typings.LayerSpec,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:
    """Returns a rectangle with release holes

    Args:
        points: points of polygon (doesn't need to repeat the first point)
        geometry_layer: layer to place polygon
        release_specs: release specification
    """
    c = gf.Component()

    shape = c.add_polygon(points, geometry_layer)

    if not release_spec or not shape.is_polygon():
        return c

    # Shrink by release_distance
    reduced = c.get_region(layer=geometry_layer, merge=True)

    # .sized(
    #     -c.kcl.to_dbu(release_spec.hole_radius)
    # )

    bb = c.kcl.to_um(shape.bbox())  # Get bounding box
    size = [bb.width(), bb.height()]
    origin = [bb.left, bb.bottom]
    # print(origin, size)

    if not release_spec.released:
        return c

    if size[0] <= release_spec.distance or size[1] <= release_spec.distance:
        return c

    s = 2 * (release_spec.hole_radius + release_spec.distance) / np.sqrt(2)
    sx = size[0] / np.ceil(size[0] / s)
    sy = size[1] / np.ceil(size[1] / s)

    for y in np.arange(origin[1] + 0.5 * sy, origin[1] + size[1], sy):
        for x in np.arange(origin[0] + 0.5 * sx, origin[0] + size[0], sx):
            pt = c.kcl.to_dbu(gf.kdb.DPoint(x, y))

            if any(p.inside(pt) for p in reduced.each()):
                ref = c << release_spec.hole
                ref.move((x, y))

    return c
