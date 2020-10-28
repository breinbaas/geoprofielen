__author__ = "Breinbaas | Rob van Putten"
__copyright__ = "Copyright 2020"
__credits__ = ["Rob van Putten"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Rob van Putten"
__email__ = "breinbaasnl@gmail.com"
__status__ = "Development"

import math
import psycopg2
from postgis.psycopg import register
from postgis import LineString, MultiLineString
from typing import List

from .pointrd import PointRD
from .dijktraject import DijkTraject
from ..secrets import DB_SERVER, DB_PASSWORD, DB_USER, DB_NAME

class DBConnector():
    def __init__(self):        
        self.conn = psycopg2.connect(
            host=DB_SERVER,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        register(self.conn)

    def _select(self, sql):
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            result = cur.fetchall()        
            cur.close()
            return result
        except (Exception, psycopg2.Error) as error:
            print(f"Got database error; {error}") 

    def get_dijktrajecten(self) -> List[DijkTraject]:
        result = {}
        rows = self._select("select geom, subsect_id, naam from rwk_areaal_2024")

        for row in rows:
            id = row[1]
            naam = row[2]

            pts = []
            if type(row[0]) == MultiLineString:
                for ls in row[0]:
                    pts += [p for p in ls.coords]
            elif type(row[0]) == LineString:
                pts = [p for p in ls.coords]

            # get coords (in WGS84)
            pts = [PointRD(lon=p[0], lat=p[1]) for p in pts]
            # apply conversion to add RD coords
            for p in pts: p.to_rd()
            # add chainage to point
            chainage = 0
            for i, p in enumerate(pts):
                if i>0:
                    dx = pts[i].x - pts[i-1].x
                    dy = pts[i].y - pts[i-1].y
                    chainage += math.sqrt(dx**2 + dy**2)
                    p.chainage = int(chainage)
            # remove point with same chainage
            final_pts, chainages = [], []
            for p in pts:
                if not p.chainage in chainages:
                    final_pts.append(p)
                    chainages.append(p.chainage)

            result[row[1]] = DijkTraject(
                    id = row[1],
                    naam = row[2],
                    referentielijn = final_pts
                )

        return result


    