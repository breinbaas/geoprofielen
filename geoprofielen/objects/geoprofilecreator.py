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

from pathlib import Path


from .dijktraject import DijkTraject
from .cpt import CPT
from .borehole import Borehole
from .geoprofile import Geoprofile
from .soilprofile import Soilprofile
from ..helpers import case_insensitive_glob
from ..settings import DEFAULT_CHAINAGE_STEP, MAX_CPT_DISTANCE, MAX_BOREHOLE_DISTANCE, HDSR_SOIL_COLORS

class GeoProfileCreator(BaseModel):    
    cpt_path: str
    borehole_path: str    
    dijktraject: DijkTraject = None

    _cpts: List[CPT] = []
    _boreholes: List[Borehole] = []
    _log: List[str] = []
    is_dirty: bool = True

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

    def execute(self) -> Geoprofile:
        result = Geoprofile()
        result.name = self.dijktraject.naam
        result.id = self.dijktraject.id

        # TODO > geoprofile als aparte class maken en veel van de code daarheen verplaatsen..
        self._log.append("[i] Reading data...")

        if self.is_dirty:
            self._read_cpts()
            self._read_boreholes()
            self.is_dirty = False
        
        self._log.append("[i] Matching reference line with available cpts / borehole...")
        
        # create a spacing
        chs = np.arange(self.dijktraject.chainage_min + DEFAULT_CHAINAGE_STEP / 2, self.dijktraject.chainage_max, DEFAULT_CHAINAGE_STEP)
        
        # find all soillayers based on CPTs
        for ch in chs:
            left = ch - DEFAULT_CHAINAGE_STEP / 2
            right = ch + DEFAULT_CHAINAGE_STEP / 2

            if ch==chs[-1]:
                right = chs[-1]

            point = self.dijktraject.chainage_to_xy(ch)
            point.chainage = ch
            result.points.append(point)
            
            # find closest CPT but always within MAX_CPT_DISTANCE
            usecpt, dlmin = None, 1e9
            for cpt in self._cpts:                
                dx = cpt.x - point.x
                dy = cpt.y - point.y
                dl = math.sqrt(dx**2 + dy**2)
                if dl < MAX_CPT_DISTANCE and dl < dlmin:
                    dlmin = dl
                    usecpt = cpt

            # find closest borehole but always within MAX_BOREHOLE_DISTANCE
            useborehole, dlmin = None, 1e9
            for borehole in self._boreholes:                
                dx = borehole.x - point.x
                dy = borehole.y - point.y
                dl = math.sqrt(dx**2 + dy**2)
                if dl < MAX_BOREHOLE_DISTANCE and dl < dlmin:
                    dlmin = dl
                    useborehole = borehole
            
            
            if usecpt:
                soilprofile = Soilprofile(
                    x_left = left,
                    x_right = right,
                    source = str(usecpt.filename),
                    soillayers = usecpt.soillayers
                )           

                # kunnen we dit combinberen met een borehole?
                if useborehole:
                    soilprofile.add(useborehole.soillayers)

                result.soilprofiles.append(soilprofile)


        # find all soillayers based on boreholes


        result.merge()
        return result