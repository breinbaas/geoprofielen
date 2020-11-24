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
from shapely.geometry import Polygon, Point

from .pointrd import PointRD

class DijkTraject(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: str = ""
    naam: str = ""
    referentielijn: List[PointRD] = []

    # you can assign a shapely polygon to the dijktraject which 
    # will limit the area where soilinvestigations can be found.
    soilinvestigation_polygon: Polygon = None

    @property
    def chainage_min(self) -> int:
        if len(self.referentielijn) > 0:
            return self.referentielijn[0].chainage
        else:
            return 0

    @property
    def chainage_max(self) -> int:
        if len(self.referentielijn) > 0:
            return self.referentielijn[-1].chainage
        else:
            return 0

    def point_in_soilinvestigation_polygon(self, x: float, y: float) -> bool:
        if self.soilinvestigation_polygon:        
            p = Point(x, y)
            return p.within(self.soilinvestigation_polygon)
        else:
            return True

    def chainage_to_xy(self, chainage: int) -> PointRD:
        if chainage < self.chainage_min or chainage > self.chainage_max:
            raise ValueError(f"Invalid chainage {chainage}, limits are [{self.chainage_min},{self.chainage_max}]")

        for i in range(1,len(self.referentielijn)):
            p1 = self.referentielijn[i-1]
            p2 = self.referentielijn[i]
            if p1.chainage <= chainage and chainage <= p2.chainage:
                dl = chainage - p1.chainage
                x = p1.x + dl / (p2.chainage - p1.chainage) * (p2.x - p1.x)
                y = p1.y + dl / (p2.chainage - p1.chainage) * (p2.y - p1.y)
                point = PointRD(chainage=chainage, x=x, y=y)
                point.to_wgs84() # fill in the blanks
                return point
        
    