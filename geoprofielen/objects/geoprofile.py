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
import numpy as np

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

    
    def to_dam_input(self, filepath: str, segmentid: int, shapeinput) -> int:
        p = Path(filepath) / self.id
        p.mkdir(parents=True, exist_ok=True)
        fsegments = open(p / "segments.csv", 'w')
        fsoilprofiles = open(p / "soilprofiles.csv", 'w')
        
        fsegments.write("segment_id,soilprofile_id,probability,calculation_type\n")
        fsoilprofiles.write("soilprofile_id,top_level,soil_name\n")

        for i, soilprofile in enumerate(self.soilprofiles):            
            id = f"profiel_{segmentid+i+1}"
            fsegments.write(f"{segmentid+i+1},{id},100,Stability\n")
            fsegments.write(f"{segmentid+i+1},{id},100,Piping\n")
            for soillayer in soilprofile.soillayers:
                fsoilprofiles.write(f"{id},{soillayer.z_top:.02f},{soillayer.soilcode}\n")  
           
            # store points and segmentid
            shapeinput.append((f"{segmentid+i+1}", self.get_partial_refline(soilprofile.x_left, soilprofile.x_right)) )
        
        fsegments.close()
        fsoilprofiles.close()
        return segmentid + len(self.soilprofiles), shapeinput
    
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