from __future__ import annotations

import gdsfactory as gf

import pydantic
import hashlib


class BeamSpec(pydantic.BaseModel):
    """Additional specifications for complex beams
    - thicker mid-section of the beam

    Parameters:
        thick_length: mid-section length, in the form (abs, rel) -> abs + beam_length * rel
        thick_width: mid-section width, in the form (abs, rel) -> abs + beam_width * rel
        thick_offset: mid-section center offset in the lengthwise direction, in the form (abs, rel) -> abs + beam_length * rel
    """

    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)

    thick_length: tuple[float, float]
    thick_width: tuple[float, float]
    thick_offset: tuple[float, float]

    @property
    def thickened(self) -> bool:
        if self.thick_length[0] == 0 and self.thick_length[1] <= 0:
            return False
        if self.thick_width[0] == 0 and self.thick_width[1] <= 0:
            return False
        return True

    def get_thick_length(self, beam_length: float) -> float:
        x = self.thick_length[0] + self.thick_length[1] * beam_length
        if x <= 0:
            raise ValueError("Thickened mid-section must have length > 0")
        return x

    def get_thick_width(self, beam_width: float) -> float:
        x = self.thick_width[0] + self.thick_width[1] * beam_width
        if x <= 0:
            raise ValueError("Thickened mid-section must have length > 0")
        return x

    def get_thick_offset(self, beam_length: float) -> float:
        return self.thick_offset[0] + self.thick_offset[1] * beam_length

    @property
    def hash(self) -> str:
        return hashlib.md5(str(self).encode()).hexdigest()
