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
                if sp.soillayers == newsoilprofiles[-1].soillayers and sp.x_left == newsoilprofiles[-1].x_right:
                    newsoilprofiles[-1].x_right = sp.x_right
                else:
                    newsoilprofiles.append(sp)
        self.soilprofiles = newsoilprofiles
    
    def to_dam_input(self, filepath: str) -> None:
        p = Path(filepath) / self.id
        p.mkdir(parents=True, exist_ok=True)
        fsegments = open(p / "segments.csv", 'w')
        fsoilprofiles = open(p / "soilprofiles.csv", 'w')
        
        fsegments.write("segment_id,soilprofile_id,probability,calculation_type\n")
        fsoilprofiles.write("soilprofile_id,top_level,soil_name\n")

        for i, soilprofile in enumerate(self.soilprofiles):
            id = f"profiel_{i+1}"
            fsegments.write(f"{i+1},{id},100,Stability\n")
            fsegments.write(f"{i+1},{id},100,Piping\n")
            for soillayer in soilprofile.soillayers:
                fsoilprofiles.write(f"{id},{soillayer.z_top:.02f},{soillayer.soilcode}\n")        
        
        
        fsegments.close()
        fsoilprofiles.close()
    
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

                ax.text(soilprofile.x_mid, self.z_top + 1.0, soilprofile.source, rotation=90)

        ax.set_xlim(self.points[0].chainage, self.points[-1].chainage)
        ax.set_ylim(self.z_bottom - 1.0, self.z_top + 5.0)
        plt.grid(which="both")
        plt.title(f"{self.name} ({self.id})")
        plt.savefig(filename)
        plt.close()