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
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches

from .soilprofile import Soilprofile
from .pointrd import PointRD
from ..settings import HDSR_SOIL_COLORS

class Geoprofile(BaseModel):
    id: str = "" # id van het dijktraject
    name: str = ""  # naam van het dijktraject
    points: List[PointRD] = [] # referentielijn
    soilprofiles: List[Soilprofile] = [] # gevonden grondprofielen

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

    def merge(self) -> None:
        newsoilprofiles = []
        for sp in self.soilprofiles:
            if len(newsoilprofiles) == 0:
                newsoilprofiles.append(sp)
            else:
                if sp.source == newsoilprofiles[-1].source and sp.x_left == newsoilprofiles[-1].x_right:
                    newsoilprofiles[-1].x_right = sp.x_right
                else:
                    newsoilprofiles.append(sp)
        self.soilprofiles = newsoilprofiles
    
    def plot(self, filename: str) -> None:
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot()

        for soilprofile in self.soilprofiles:
            for soillayer in soilprofile.soillayers:
                soilcolor = HDSR_SOIL_COLORS[soillayer.soilcode]

                ax.add_patch(
                    patches.Rectangle(
                        (soilprofile.x_left, soillayer.z_bottom),
                        soilprofile.width,
                        soillayer.height,
                        fill=True,
                        facecolor=soilcolor,
                    )   
                )

                ax.text(soilprofile.x_left, self.z_top + 1.0, Path(soilprofile.source).name)

        ax.set_xlim(self.x_left, self.x_right)
        ax.set_ylim(self.z_bottom - 1.0, self.z_top + 2.0)
        plt.grid(which="both")
        plt.title(f"{self.name} ({self.id})")
        plt.savefig(filename)