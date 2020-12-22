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
from .soilprofile import Soilprofile
from ..helpers import case_insensitive_glob
from ..settings import DEFAULT_CHAINAGE_STEP, MAX_CPT_DISTANCE, MAX_BOREHOLE_DISTANCE, HDSR_SOIL_COLORS
from ..objects.pointrd import PointRD

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