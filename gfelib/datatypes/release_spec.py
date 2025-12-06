from __future__ import annotations

import gdsfactory as gf

import pydantic
import hashlib


class ReleaseSpec(pydantic.BaseModel):
    """Isotropic release specifications

    Parameters:
        hole_radius: radii of circular release holes
        distance: isotropic release distance
        angle_resolution: number of degrees per point for circular polygons
        layer: release hole layer
    """

    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)

    hole_radius: float
    distance: float
    angle_resolution: float
    layer: gf.typings.LayerSpec

    @property
    def released(self) -> bool:
        if self.hole_radius <= 0:
            return False
        if self.distance <= 0:
            return False
        return True

    @property
    def hole(self) -> gf.Component:
        return gf.components.circle(
            radius=self.hole_radius,
            angle_resolution=self.angle_resolution,
            layer=self.layer,
        )

    @property
    def hash(self) -> str:
        return hashlib.md5(str(self).encode()).hexdigest()
