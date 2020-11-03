from pydantic import BaseModel
from typing import List

from .soillayer import SoilLayer

class Soilprofile(BaseModel):
    x_left: int = 0
    x_right: int = 0
    source: str = ""
    soillayers: List[SoilLayer] = []

    @property
    def z_top(self) -> float:
        if len(self.soillayers) > 0:
            return max([sl.z_top for sl in self.soillayers])
        raise ValueError("Trying to get ztop from an empty soilprofile")

    @property
    def z_bottom(self) -> float:
        if len(self.soillayers) > 0:
            return min([sl.z_bottom for sl in self.soillayers])
        raise ValueError("Trying to get zbottom from an empty soilprofile")

    @property
    def width(self) -> float:
        return self.x_right - self.x_left


