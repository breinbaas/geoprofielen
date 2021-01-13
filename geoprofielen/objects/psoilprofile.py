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

# yeah, if I had more time this should definitely have been a child class of the shared SoilProfile properties..
# but hey.. no time now so simply copy and paste :-)
class PSoilprofile(BaseModel):
    x_left: int = 0
    x_right: int = 0
    source: str = ""
    soillayers: List[SoilLayer] = []
    probability: int = 0      

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

    





