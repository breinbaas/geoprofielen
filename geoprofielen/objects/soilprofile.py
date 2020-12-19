__author__ = "Breinbaas | Rob van Putten"
__copyright__ = "Copyright 2020"
__credits__ = ["Rob van Putten"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Rob van Putten"
__email__ = "breinbaasnl@gmail.com"
__status__ = "Development"

from pydantic import BaseModel
from typing import List

from .soillayer import SoilLayer
from ..settings import DEFAULT_MINIMUM_LAYERHEIGHT

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

    @property
    def x_mid(self) -> float:
        return (self.x_left + self.x_right) / 2.

    def _merge(self) -> None:
        to_remove = [i for i in range(len(self.soillayers)) if self.soillayers[i].height < DEFAULT_MINIMUM_LAYERHEIGHT]
        
        if len(to_remove) == 0:
            return

        idx = to_remove[0]
        if idx == 0 and len(self.soillayers)>1:
            self.soillayers[1].z_top = self.soillayers[0].z_top
            self.soillayers.pop(0)
        elif idx == len(self.soillayers) - 1:
            self.soillayers[len(self.soillayers-2)].z_bottom = self.soillayers[len(self.soillayers)-1].z_bottom
            self.soillayers.pop(len(self.soillayers)-1)
        else:
            z_mid = round((self.soillayers[idx].z_top + self.soillayers[idx].z_bottom) / 2.0, 2)
            self.soillayers[idx-1].z_bottom = z_mid
            self.soillayers[idx+1].z_top = z_mid
            self.soillayers.pop(idx)

        self._merge()


    def add(self, soillayers: List[SoilLayer]) -> None:
        # only add if the new soilprofile intersects with the current one
        # or else we would have to make up soillayers
        result = [sl for sl in soillayers] # or copy.deepcopy()

        z_top = max([sl.z_top for sl in result])
        z_bottom = min([sl.z_bottom for sl in result])

        if z_top < self.z_bottom or z_bottom > self.z_top:
            return

        toplayers = sorted([sl for sl in self.soillayers if sl.z_top > z_top], key=lambda x: x.z_bottom, reverse=True)
        bottomlayers = sorted([sl for sl in self.soillayers if sl.z_bottom < z_bottom], key=lambda x: x.z_bottom, reverse=True)

        if len(toplayers) > 0:
            toplayers[-1].z_bottom = z_top
        if len(bottomlayers) > 0:
            bottomlayers[0].z_top = z_bottom

        for layer in toplayers[::-1]:
            result.insert(0, layer)
        for layer in bottomlayers:
            result.append(layer)

        self.soillayers = [sl for sl in result]
        self._merge()





