from __future__ import annotations

import gdsfactory as gf
from collections.abc import Sequence
import pydantic
import hashlib

import gfelib as gl


class ZCantileverBeam(pydantic.BaseModel):
    """Z-cantilever beam specifications

    Parameters:
        length: beam length (y)
        width: beam width (x)
        position: beam x position, in the form (abs, rel) -> abs + z_cantilever.length * rel
        inset_x: beam inset region x-size, in the form (abs, rel) -> abs + z_cantilever.length * rel
        inset_y: beam inset region y-size, in the form (abs, rel) -> abs + z_cantilever.width * rel
        isolation_x: cantilever beam electrical isolation region x-size, in the form (abs, rel) -> abs + z_cantilever.length * rel, set to (0, 0) to disable isolation
        isolation_y: cantilever beam electrical isolation region y-size, in the form (abs, rel) -> abs + z_cantilever.width * rel, set to (0, 0) to disable isolation
        spec: beam specifications
    """

    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)

    length: float
    width: float
    position: tuple[float, float]
    inset_x: tuple[float, float]
    inset_y: tuple[float, float]
    isolation_x: tuple[float, float]
    isolation_y: tuple[float, float]
    spec: gl.datatypes.BeamSpec | None

    def get_position(self, cantilever_length: float) -> float:
        x = self.position[0] + self.position[1] * cantilever_length
        if x < 0:
            raise ValueError("Beam must have position >= 0")
        if x > cantilever_length - self.width:
            raise ValueError("Beam must have position <= cantilever_length - width")
        return x

    @property
    def insetted(self) -> bool:
        if self.inset_x[0] == 0 and self.inset_x[1] <= 0:
            return False
        if self.inset_y[0] == 0 and self.inset_y[1] <= 0:
            return False
        return True

    def get_inset_x(self, cantilever_length: float) -> float:
        x = self.inset_x[0] + self.inset_x[1] * cantilever_length
        if x <= 0:
            raise ValueError("Beam inset region must have x-size > 0")
        return x

    def get_inset_y(self, cantilever_width: float) -> float:
        x = self.inset_y[0] + self.inset_y[1] * cantilever_width
        if x <= 0:
            raise ValueError("Beam inset region must have y-size > 0")
        return x

    @property
    def isolated(self) -> bool:
        if self.isolation_x[0] == 0 and self.isolation_x[1] <= 0:
            return False
        if self.isolation_y[0] == 0 and self.isolation_y[1] <= 0:
            return False
        return True

    def get_isolation_x(self, cantilever_length: float) -> float:
        x = self.isolation_x[0] + self.isolation_x[1] * cantilever_length
        if x <= 0:
            raise ValueError("Beam isolation region must have x-size > 0")
        return x

    def get_isolation_y(self, cantilever_width: float) -> float:
        x = self.isolation_y[0] + self.isolation_y[1] * cantilever_width
        if x <= 0:
            raise ValueError("Beam isolation region must have y-size > 0")
        return x

    @property
    def hash(self) -> str:
        return hashlib.md5(str(self).encode()).hexdigest()


@gl.utils.default_cell
def z_cantilever_half(
    length: float,
    width: float,
    beams: Sequence[ZCantileverBeam],
    clearance: float,
    middle_split: bool,
    geometry_layer: gf.typings.LayerSpec,
    handle_layer: gf.typings.LayerSpec | None,
    release_spec: gl.datatypes.ReleaseSpec | None,
) -> gf.Component:

    c = gf.Component()

    y_offset = 0.5 * clearance if middle_split else 0
    rect_ref = c << gf.components.rectangle(
        size=(length, 0.5 * width - y_offset),
        layer=geometry_layer,
        centered=False,
    )
    rect_ref.movey(y_offset)

    beams.sort(key=lambda x: x.get_position(length))

    for beam in beams:
        position = beam.get_position(length)

        if beam.isolated:
            isolation_x = beam.get_isolation_x(length)
            isolation_y = beam.get_isolation_y(width)

            isolation_region_s = position + 0.5 * beam.width - 0.5 * isolation_x
            isolation_region_s = 0 if isolation_region_s < 0 else isolation_region_s

            isolation_region_e = position + 0.5 * beam.width + 0.5 * isolation_x
            isolation_region_e = (
                length if isolation_region_e > length else isolation_region_e
            )

            isolation_region = gf.Component()
            isolation_region_ref = isolation_region << gf.components.rectangle(
                size=(isolation_region_e - isolation_region_s, isolation_y),
                layer=geometry_layer,
                centered=False,
            )
            isolation_region_ref.move((isolation_region_s, 0.5 * width - isolation_y))
            isolation_region.flatten()

            isolation_expand = isolation_region.copy()
            isolation_expand.offset(layer=geometry_layer, distance=clearance)

            c = gf.boolean(
                A=c,
                B=isolation_expand,
                operation="-",
                layer=geometry_layer,
                layer1=geometry_layer,
                layer2=geometry_layer,
            )

            c = gf.boolean(
                A=c,
                B=isolation_region,
                operation="|",
                layer=geometry_layer,
                layer1=geometry_layer,
                layer2=geometry_layer,
            )

        if beam.insetted:
            inset_x = beam.get_inset_x(length)
            inset_y = beam.get_inset_y(width)

            inset_region_s = position + 0.5 * beam.width - 0.5 * inset_x
            inset_region_s = 0 if inset_region_s < 0 else inset_region_s

            inset_region_e = position + 0.5 * beam.width + 0.5 * inset_x
            inset_region_e = length if inset_region_e > length else inset_region_e

            inset_region = gf.Component()
            inset_region_ref = inset_region << gf.components.rectangle(
                size=(inset_region_e - inset_region_s, inset_y),
                layer=geometry_layer,
                centered=False,
            )
            inset_region_ref.move((inset_region_s, 0.5 * width - inset_y))
            inset_region.flatten()

            c = gf.boolean(
                A=c,
                B=inset_region,
                operation="-",
                layer=geometry_layer,
                layer1=geometry_layer,
                layer2=geometry_layer,
            )

    for beam in beams:
        position = beam.get_position(length)
        inset = beam.get_inset_y(width) if beam.insetted else 0

        ref = c << gl.flexure.beam(
            length=beam.length,
            width=beam.width,
            geometry_layer=geometry_layer,
            beam_spec=beam.spec,
            release_spec=release_spec,
        )
        ref.rotate(angle=90, center=(0, 0))
        ref.move(
            (
                0.5 * beam.width + position,
                0.5 * width + 0.5 * beam.length - inset,
            )
        )

    _ = c << gf.components.rectangle(
        size=(length, 0.5 * width),
        layer=handle_layer,
        centered=False,
    )

    return c
