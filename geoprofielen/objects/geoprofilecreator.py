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
import os
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
from pathlib import Path


from .dijktraject import DijkTraject
from .cpt import CPT
from .borehole import Borehole
from ..helpers import case_insensitive_glob
from ..settings import DEFAULT_CHAINAGE_STEP, MAX_CPT_DISTANCE, MAX_BOREHOLE_DISTANCE, HDSR_SOIL_COLORS

class GeoProfileCreator(BaseModel):    
    cpt_path: str
    borehole_path: str    
    dijktraject: DijkTraject

    _cpts: List[CPT] = []
    _boreholes: List[Borehole] = []
    _log: List[str] = []

    @property
    def log(self) -> List[str]:
        return self._log

    def _read_cpts(self) -> None:
        files = case_insensitive_glob(self.cpt_path, ".gef")
        self._log.append(f"[i] Reading {len(files)} cpt files...")

        for f in files:
            cpt = CPT()
            try:
                cpt.read(f)
                cpt.convert()
                self._cpts.append(cpt)
            except Exception as e:
                self._log.append(f"[E] error in cpt file {f}; {e}")

        self._log.append(f"[i] Found {len(self._cpts)} valid CPTs.")


    def _read_boreholes(self) -> None:
        files = case_insensitive_glob(self.borehole_path, ".gef")
        self._log.append(f"[i] Reading {len(files)} borehole files...")

        for f in files:
            borehole = Borehole()
            try:
                borehole.read(f)
                borehole.convert()
                self._boreholes.append(borehole)
            except Exception as e:
                self._log.append(f"[E] error in borehole file {f}; {e}")

        self._log.append(f"[i] Found {len(self._boreholes)} valid boreholes.")

    def save_log(self, filename: str) -> None:
        f = open(filename, 'w')
        for l in self._log:
            f.write(f"{l}\n")
        f.close()

    def execute(self) -> None:
        # TODO > geoprofile als aparte class maken en veel van de code daarheen verplaatsen..
        self._log.append("[i] Reading data...")
        self._read_cpts()
        self._read_boreholes()
        
        self._log.append("[i] Matching reference line with available cpts / borehole...")
        
        # create a spacing
        chs = np.arange(self.dijktraject.chainage_min + DEFAULT_CHAINAGE_STEP / 2, self.dijktraject.chainage_max, DEFAULT_CHAINAGE_STEP)
        
        # find all soillayers based on CPTs
        result = []        
        for ch in chs:
            left = ch - DEFAULT_CHAINAGE_STEP / 2
            right = ch + DEFAULT_CHAINAGE_STEP / 2

            if ch==chs[-1]:
                right = chs[-1]

            point = self.dijktraject.chainage_to_xy(ch)
            
            # find closest CPT but always within MAX_CPT_DISTANCE
            usecpt, dlmin = None, 1e9
            for cpt in self._cpts:                
                dx = cpt.x - point.x
                dy = cpt.y - point.y
                dl = math.sqrt(dx**2 + dy**2)
                if dl < MAX_CPT_DISTANCE and dl < dlmin:
                    dlmin = dl
                    usecpt = cpt

            if usecpt:
                if len(result) == 0:
                    result.append([left, right, usecpt.soillayers, usecpt])
                else:
                    if result[-1][-1] == usecpt:
                        result[-1][1] = right
                    else:
                        result.append([left, right, usecpt.soillayers, usecpt])
            else:
                if len(result) == 0:
                    result.append([left, right, None, None])
                else:
                    if result[-1][-2] is None:
                        result[-1][1] = right
                    else:
                        result.append([left, right, None, None])


            
        # just for show here in this code, should be moved to better location
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot()

        z_min, z_max = 1e9, -1e9
        for r in [r for r in result if r[2]]:
            left = r[0]
            right = r[1]
            chmin = self.dijktraject.chainage_min
            chmax = self.dijktraject.chainage_max
            soillayers = r[2]

            for sl in soillayers:
                z_top = sl.z_top
                z_bottom = sl.z_bottom

                if z_top > z_max: z_max = z_top
                if z_bottom < z_min: z_min = z_bottom

                soilcolor = HDSR_SOIL_COLORS[sl.soilcode]

                ax.add_patch(
                    patches.Rectangle(
                        (left, z_bottom),
                        right - left,
                        sl.height,
                        fill=True,
                        facecolor=soilcolor,
                    )   
                )

                ax.text(left, z_max + 1.0, Path(r[-1].filename).name)

        ax.set_xlim(self.dijktraject.chainage_min, self.dijktraject.chainage_max)
        ax.set_ylim(z_min - 1.0, z_max + 2.0)
        plt.grid(which="both")
        plt.title(f"{self.dijktraject.naam} ({self.dijktraject.id})")
        plt.savefig("./data/geoprofiel/test.png")


        

            

