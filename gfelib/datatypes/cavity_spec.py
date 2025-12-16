from __future__ import annotations

import gdsfactory as gf

import pydantic
import hashlib


class CavitySpec(pydantic.BaseModel):
    """Handle layer cavity specifications

    Parameters:
        width: cavity etch width
        layer: handle layer
    """

    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)

    width: float
    layer: gf.typings.LayerSpec

    @property
    def hash(self) -> str:
        return hashlib.md5(str(self).encode()).hexdigest()
