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
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches

from .psoilprofile import PSoilprofile
from .pointrd import PointRD
from ..settings import HDSR_SOIL_COLORS

# same here.. should (with more time) split it in some parent / child relation because
# we are almost copying the normal Geoprofile.. so not neat, but effective for now
class PGeoprofile(BaseModel):
    id: str = "" # id van het dijktraject
    name: str = ""  # naam van het dijktraject
    points: List[PointRD] = [] # referentielijn
    soilprofiles: List[PSoilprofile] = [] # gevonden grondprofielen

    @property
    def x_left(self):
        if len(self.soilprofiles) > 0:
            return min([sp.x_left for sp in self.soilprofiles])
        raise ValueError("Trying to get xleft from an empty geoprofile")

    @property
    def x_right(self):
        if len(self.soilprofiles) > 0:
            return max([sp.x_right for sp in self.soilprofiles])
        raise ValueError("Trying to get xright from an empty geoprofile")

    @property
    def z_top(self) -> float:
        if len(self.soilprofiles) > 0:
            return max([sp.z_top for sp in self.soilprofiles])
        raise ValueError("Trying to get ztop from an empty geoprofile")

    @property
    def z_bottom(self) -> float:
        if len(self.soilprofiles) > 0:
            return min([sp.z_bottom for sp in self.soilprofiles])
        raise ValueError("Trying to get zbottom from an empty geoprofile")

    def get_xy_from_l_on_refline(self, l):
        for i in range(1,len(self.points)):
            p1 = self.points[i-1]
            p2 = self.points[i]

            if p1.chainage <= l and l <= p2.chainage:
                x = p1.x + (l - p1.chainage) / (p2.chainage - p1.chainage) * (p1.x - p2.x)
                y = p1.y + (l - p1.chainage) / (p2.chainage - p1.chainage) * (p1.y - p2.y)
                return x, y

        raise ValueError(f"Could not find xy for chainage {l}; min chainage = {self.points[0].chainage}, max chainage = {self.points[-1].chainage}")
    
    
    def get_partial_refline(self, chainage_start: int, chainage_end: int):
        result = []
        points = np.linspace(chainage_start, chainage_end, int((chainage_end - chainage_start) / 10.) + 1)
        for p in points:
            result.append(self.get_xy_from_l_on_refline(p))

        return result

    
    def to_dam_input(self, segmentid: int, shapeinput) -> int:
        pass
    
    def plot(self, filename: str) -> None:
        pass