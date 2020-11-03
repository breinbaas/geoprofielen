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

    def _merge(self) -> None:
        for i, sl in enumerate(self.soillayers):
            if sl.height < DEFAULT_MINIMUM_LAYERHEIGHT:
                if i==0 and len(self.soillayers) > 1:
                    self.soillayers[1].z_top = sl.z_top 
                    self.soillayers.pop() # bye bye
                elif i==len(self.soillayers)-1 and len(self.soillayers)>1:
                    self.soillayers[-2].z_bottom = sl.z_bottom
                    self.soillayers.pop(-1)
                else:
                    z_mid = round((sl.z_top + sl.z_bottom) / 2.,2)
                    self.soillayers[i-1].z_bottom = z_mid
                    self.soillayers[i+1].z_top = z_mid
                    self.soillayers.pop(i)


    def add(self, soillayers: List[SoilLayer]) -> None:
        # only add if the new soilprofile intersects with the current one
        # or else we would have to make up soillayers
        z_top = max([sl.z_top for sl in soillayers])
        z_bottom = min([sl.z_bottom for sl in soillayers])

        if z_top < self.z_bottom or z_bottom > self.z_top:
            return

        toplayers = sorted([sl for sl in self.soillayers if sl.z_top > z_top], key=lambda x: x.z_bottom, reverse=True)
        bottomlayers = sorted([sl for sl in self.soillayers if sl.z_bottom < z_bottom], key=lambda x: x.z_bottom, reverse=True)

        if len(toplayers) > 0:
            toplayers[-1].z_bottom = z_top
        if len(bottomlayers) > 0:
            bottomlayers[0].z_top = z_bottom

        for layer in toplayers[::-1]:
            soillayers.insert(0, layer)
        for layer in bottomlayers:
            soillayers.append(layer)

        self.soillayers = soillayers
        self._merge()





