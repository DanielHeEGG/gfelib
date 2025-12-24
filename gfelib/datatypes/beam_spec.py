from __future__ import annotations

import gdsfactory as gf

import pydantic
import hashlib


class BeamSpec(pydantic.BaseModel):
    """Additional specifications for complex beams
    - thicker mid-section of the beam

    Parameters:
        release_thin: `True` to place release holes on thin beam sections
        release_thick: `True` to place release holes on thick beam sections
        thick_length: mid-section length, in the form (abs, rel) -> abs + beam_length * rel
        thick_width: mid-section width, in the form (abs, rel) -> abs + beam_width * rel
        thick_offset: mid-section center offset in the lengthwise direction, in the form (abs, rel) -> abs + beam_length * rel
        handle_etch_length: handle layer etch length, in the form (abs, rel) -> abs + beam_length * rel
        handle_etch_width: handle layer etch width, in the form (abs, rel) -> abs + beam_width * rel
        handle_etch_offset: handle layer etch center offset in the lengthwise direction, in the form (abs, rel) -> abs + beam_length * rel
        handle_etch_layer: handle etch rectangle polygon layer
    """

    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)

    release_thin: float = False
    release_thick: float = False

    thick_length: tuple[float, float] = (0, 0)
    thick_width: tuple[float, float] = (0, 0)
    thick_offset: tuple[float, float] = (0, 0)

    handle_etch_length: tuple[float, float] = (0, 0)
    handle_etch_width: tuple[float, float] = (0, 0)
    handle_etch_offset: tuple[float, float] = (0, 0)
    handle_etch_layer: gf.typings.LayerSpec | None = None

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
            raise ValueError("Thickened mid-section must have width > 0")
        return x

    def get_thick_offset(self, beam_length: float) -> float:
        return self.thick_offset[0] + self.thick_offset[1] * beam_length

    @property
    def handle_etched(self) -> bool:
        if self.thick_length[0] == 0 and self.thick_length[1] <= 0:
            return False
        if self.thick_width[0] == 0 and self.thick_width[1] <= 0:
            return False
        if self.handle_etch_layer is None:
            return False
        return True

    def get_handle_etch_length(self, beam_length: float) -> float:
        x = self.handle_etch_length[0] + self.handle_etch_length[1] * beam_length
        if x <= 0:
            raise ValueError("Handle etch rectangle must have length > 0")
        return x

    def get_handle_etch_width(self, beam_width: float) -> float:
        x = self.handle_etch_width[0] + self.handle_etch_width[1] * beam_width
        if x <= 0:
            raise ValueError("Handle etch rectangle must have width > 0")
        return x

    def get_handle_etch_offset(self, beam_length: float) -> float:
        return self.handle_etch_offset[0] + self.handle_etch_offset[1] * beam_length

    @property
    def hash(self) -> str:
        return hashlib.md5(str(self).encode()).hexdigest()
