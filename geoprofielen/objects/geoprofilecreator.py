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

import folium


from .dijktraject import DijkTraject
from .cpt import CPT, ConversionType
from .borehole import Borehole
from .geoprofile import Geoprofile
from .pgeoprofile import PGeoprofile
from .soilprofile import Soilprofile
from .psoilprofile import PSoilprofile
from ..helpers import case_insensitive_glob
from ..settings import DEFAULT_CHAINAGE_STEP, MAX_CPT_DISTANCE, MAX_BOREHOLE_DISTANCE, NUM_PROB_SOILINVESTIGATIONS, HDSR_SOIL_COLORS, MIN_PROBABILISTIC_SOILPROFILE_LENGTH, MIN_PROBABILISTIC_CPT_BOREHOLE_LENGTH
from ..objects.pointrd import PointRD

class GeoProfileCreator(BaseModel):    
    cpt_path: str
    borehole_path: str    
    dijktraject: DijkTraject = None

    _cpts: List[CPT] = []
    _boreholes: List[Borehole] = []
    _log: List[str] = []
    _plog: List[str] = [] # logfile for probabilistic approach
    is_dirty: bool = True

    @property
    def plog(self) -> List[str]:
        return self._plog

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
                cpt.convert(conversion_type=ConversionType.NEN_5104)
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

    def save_plog(self, filename: str) -> None:
        f = open(filename, 'w')
        for l in self._plog:
            f.write(f"{l}\n")
        f.close()

    def execute_prob(self) -> PGeoprofile:
        result = PGeoprofile()
        result.name = self.dijktraject.naam
        result.id = self.dijktraject.id

        # TODO > geoprofile als aparte class maken en veel van de code daarheen verplaatsen..
        self._plog.append("[i] Reading data...")

        if self.is_dirty:
            self._read_cpts()
            self._read_boreholes()
            self.is_dirty = False
        
        # split in 100m pieces (except for the last which might get a max lenght of 199.99)
        chs = np.arange(self.dijktraject.chainage_min, self.dijktraject.chainage_max, MIN_PROBABILISTIC_SOILPROFILE_LENGTH)
        chs[-1] = self.dijktraject.chainage_max

        for i in range(1, len(chs)):
            left = chs[i-1]
            right = chs[i]
            mid = (left + right) / 2.0
            point = self.dijktraject.chainage_to_xy(mid)

            # find all cpts and boreholes and store the distance to the current point
            # make sure the cpts / boreholes are longer than the required minimal length
            # this makes sure that we don't use soil investigations that are too short
            cpts = [[math.sqrt(math.pow((cpt.x - point.x),2) + math.pow((cpt.y - point.y),2)), cpt] for cpt in self._cpts if cpt.length > MIN_PROBABILISTIC_CPT_BOREHOLE_LENGTH]
            boreholes = [[math.sqrt(math.pow((borehole.x - point.x),2) + math.pow((borehole.y - point.y),2)), borehole] for borehole in self._boreholes if borehole.length > MIN_PROBABILISTIC_CPT_BOREHOLE_LENGTH]
            
            # add all
            total = cpts + boreholes

            # sort on distance and the number we require
            total = sorted(total, key=lambda x: x[0])[:NUM_PROB_SOILINVESTIGATIONS]
            sumdl = sum([t[0] for t in total])

            sumdlf = 0.0
            for t in total:
                sumdlf += sumdl / t[0] # will go wrong in the very theoretical case that point.xy == cpt or borehole.xy

            for t in total:
                t[0] = int(round((sumdl / t[0]) / sumdlf * 100, 0))

            # make sure the sum is 100, note that 99 and 101 might be possible but not more / less than that, no check however
            sumt = sum(t[0] for t in total)
            if sumt > 100: # subtract difference from highest value
                total[total.index(max(total))][0] = total[total.index(max(total))][0] - (sumt - 100)
            if sumt < 100: # add difference to lowest value
                total[total.index(min(total))][0] = total[total.index(min(total))][0] + (100 - sumt)

            # TODO > hier verder
    
    def execute(self, plot_map_path="") -> Geoprofile:
        cptsforplot = []
        boreholesforplot = []

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
        chs = np.arange(self.dijktraject.chainage_min, self.dijktraject.chainage_max, DEFAULT_CHAINAGE_STEP)        

        # and endpoint unless the last point is already with 0.5m from the end point
        if self.dijktraject.chainage_max > chs[-1] + 0.5:
            chs = np.insert(chs, len(chs), self.dijktraject.chainage_max)        
        
        # find all soillayers based on CPTs
        for i in range(0, len(chs)-1):
            left = chs[i]
            right = chs[i+1]
            if right > max(chs):
                right = max(chs)  

            ch = int((left + right) /  2)

            point = self.dijktraject.chainage_to_xy(int((left + right) / 2.))
            point.chainage = ch
            result.points = self.dijktraject.referentielijn

           # find closest CPT but always within MAX_CPT_DISTANCE
            usecpt, useborehole, dlmin_cpt, dlmin_borehole = None, None, 1e9, 1e9
            for cpt in self._cpts:                
                dx = cpt.x - point.x
                dy = cpt.y - point.y
                dl = math.sqrt(dx**2 + dy**2)
                    
                in_polygon = True 
                if self.dijktraject.has_soilinvestigation_polygon(): # any polygon to check?
                    in_polygon = self.dijktraject.point_in_soilinvestigation_polygon(cpt.x, cpt.y)
                
                if dl < MAX_CPT_DISTANCE and dl < dlmin_cpt and in_polygon:
                    dlmin_cpt = dl
                    usecpt = cpt

            # find closest borehole but always within MAX_BOREHOLE_DISTANCE
            for borehole in self._boreholes:                
                dx = borehole.x - point.x
                dy = borehole.y - point.y
                dl = math.sqrt(dx**2 + dy**2)
                    
                in_polygon = True 
                if self.dijktraject.has_soilinvestigation_polygon(): # any polygon to check?
                    in_polygon = self.dijktraject.point_in_soilinvestigation_polygon(borehole.x, borehole.y)
                
                if dl < MAX_BOREHOLE_DISTANCE and dl < dlmin_borehole and in_polygon:
                    dlmin_borehole = dl
                    useborehole = borehole
            
            if usecpt:
                if not usecpt.name in [c[-1] for c in cptsforplot]:
                    cptsforplot.append((usecpt.x, usecpt.y, usecpt.filename))

                soilprofile = Soilprofile(
                    x_left = left,
                    x_right = right,
                    source = str(Path(usecpt.filename).stem),
                    soillayers = usecpt.soillayers
                )                  

                # kunnen we dit combinberen met een borehole?
                if useborehole:
                    if not useborehole.name in [c[-1] for c in boreholesforplot]:
                        boreholesforplot.append((useborehole.x, useborehole.y, useborehole.filename))
                    soilprofile.add(useborehole.soillayers)
                    soilprofile.source += f" + {str(Path(useborehole.filename).stem)}"

                result.soilprofiles.append(soilprofile)
            
            elif useborehole:
                if not useborehole.name in [c[-1] for c in boreholesforplot]:
                    boreholesforplot.append((useborehole.x, useborehole.y, useborehole.filename))
                soilprofile = Soilprofile(
                    x_left = left,
                    x_right = right,
                    source = str(Path(useborehole.filename).stem),
                    soillayers = useborehole.soillayers
                )
                soilprofile._merge() # this prevents from adding boreholelayers < DEFAULT_MINIMUM_LAYERHEIGHT
                result.soilprofiles.append(soilprofile)

        result.merge()

        if len(plot_map_path)>0:
            px = []
            py = []
            for p in self.dijktraject.referentielijn:
                px.append(p.lat)
                py.append(p.lon)

            pmid = (sum(px) / len(px), sum(py) / len(py))

            fmap = folium.Map(location=[pmid[0],pmid[1]], tiles='openstreetmap', zoom_start=17)
            folium.PolyLine(zip(px,py), color="red").add_to(fmap)   

            # HIER!
            # todo add reference image to polyline   

            for b in boreholesforplot:
                prd = PointRD(x=b[0], y=b[1])
                prd.to_wgs84()
                filename = str(b[-1]).replace("\\", "/").replace(".gef", ".png")
                html = f'<img src="file:///{filename}" height=400px />'
                folium.Marker((prd.lat, prd.lon), icon=folium.Icon(color='blue', icon='info-sign'), popup=html).add_to(fmap)


            for b in cptsforplot:
                prd = PointRD(x=b[0], y=b[1])
                prd.to_wgs84()
                filename = str(b[-1]).replace("\\", "/").replace(".gef", ".png")
                html = f'<img src="file:///{filename}" height=400px />'
                folium.Marker((prd.lat, prd.lon), icon=folium.Icon(color='red', icon='info-sign'), popup=html).add_to(fmap)               
            
            fmap.save(str(Path(plot_map_path) / self.dijktraject.id) + ".html")


        return result