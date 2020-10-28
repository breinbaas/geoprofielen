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

from .dijktraject import DijkTraject
from .cpt import CPT
from .borehole import Borehole
from ..helpers import case_insensitive_glob
from ..settings import DEFAULT_CHAINAGE_STEP, MAX_CPT_DISTANCE, MAX_BOREHOLE_DISTANCE

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
        self._log.append("[W] Borehole reading not implemented yet.")
        # files = case_insensitive_glob(self.borehole_path, ".gef")

    def execute(self) -> None:
        self._log.append("[i] Reading data...")
        self._read_cpts()
        self._read_boreholes()
        
        self._log.append("[i] Matching reference line with available cpts / borehole...")
        
        # create a spacing
        chs = np.arange(self.dijktraject.chainage_min + DEFAULT_CHAINAGE_STEP / 2, self.dijktraject.chainage_max, DEFAULT_CHAINAGE_STEP)
        
        # find all soillayers based on CPTs
        result = []        
        current_cpt = None
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
                    result.append([left, right, usecpt.soillayers, cpt.filename])
                else:
                    if result[-1][-1] == cpt.filename:
                        result[-1][1] = right
                    else:
                        result.append([left, right, usecpt.soillayers, cpt.filename])
            else:
                if len(result) == 0:
                    result.append([left, right, None, ''])
                else:
                    if result[-1][-2] is None:
                        result[-1][1] = right
                    else:
                        result.append([left, right, None, ''])
                

        
        
        i = 1

        

            

