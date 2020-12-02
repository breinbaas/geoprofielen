# achterhalen van alle gebruikte grondsoortnamen in de boringen

import os
from tqdm import tqdm
import shapefile
from pathlib import Path

from geoprofielen.objects.geoprofilecreator import GeoProfileCreator
from geoprofielen.objects.dbconnector import DBConnector
from geoprofielen.settings import ROOT_DIR

PILOT_AREA = [
    "118A1",
    "118B1",
    "118B2",
    "118B3",
    "151",
    "150",
    "118B4",
    "141",
    "140",
    "117A",
    "117B",
    "117C1"    
]

SOILINVESTIGATION_POLYGON_FILE = "C:/Users/brein/Programming/Python/HDSR/geoprofielen/data/gis/soilinvestigation_area_polygons.shp"

if __name__ == "__main__":
    dbc = DBConnector()

    # maak een selectie op basis van de pilot area
    dijktrajecten = {k:v for k,v in dbc.get_dijktrajecten().items() if v.id in PILOT_AREA}
    
    geoprofilecreator = GeoProfileCreator(
        cpt_path = os.path.join(ROOT_DIR, "data/sonderingen"),
        borehole_path = os.path.join(ROOT_DIR, "data/boringen")
    )
    
    # todo > create LocationSegments.shp
    segmentid = 0 # we need ids that are unique over all dijktrajecten so we can create one big shapefile
    shapeinput = [] # this is where we store all info for the shape

    p = Path(ROOT_DIR) / "data/dam/pilot"
    p.mkdir(parents=True, exist_ok=True)
    
    fsegments = open(p / "segments.csv", 'w')
    fsoilprofiles = open(p / "soilprofiles.csv", 'w')
    fsegments.write("segment_id,soilprofile_id,probability,calculation_type\n")
    fsoilprofiles.write("soilprofile_id,top_level,soil_name\n")

    # also read the polygons for the search for soilinvestigations
    sfrecords = []
    if os.path.isfile(SOILINVESTIGATION_POLYGON_FILE):
        sf = shapefile.Reader(SOILINVESTIGATION_POLYGON_FILE)
        sfrecords = sf.shapeRecords()

    for dtcode, dijktraject in tqdm(dijktrajecten.items()):
        # check if a polygon can be assigned
        for i in range(len(sfrecords)):
            if dijktraject.naam == sfrecords[i].record['naam']:
                dijktraject.soilinvestigation_polygon = sfrecords[i].shape.points
                break
        
        geoprofilecreator.dijktraject = dijktraject
        try:
            geoprofile = geoprofilecreator.execute()
            if len(geoprofile.soilprofiles) == 0: continue
            
            geoprofile.plot(os.path.join(ROOT_DIR, f"data/geoprofiel/pilot/{dtcode}.png"))
            
            # yes.. ugly.. I know :-/
            lines_segments, lines_soilprofiles, segmentid, shapeinput = geoprofile.to_dam_input(segmentid, shapeinput)   

            for line in lines_segments:
                fsegments.write(line)   
            for line in lines_soilprofiles:
                fsoilprofiles.write(line)

        except Exception as e:
            print(f"Got error trying to generate geoprofile for dijktraject {dtcode}; {e}")

    fsegments.close()
    fsoilprofiles.close()

    w = shapefile.Writer(os.path.join(ROOT_DIR, "data/dam/pilot/LocationSegments.shp"))
    w.field('segment_id', 'C')

    for segment_id, xypoints in shapeinput:
        w.record(segment_id)
        w.line([xypoints])

    w.close()
    
