# achterhalen van alle gebruikte grondsoortnamen in de boringen

import os
from tqdm import tqdm
import shapefile
from pathlib import Path

from geoprofielen.objects.geoprofilecreator import GeoProfileCreator
from geoprofielen.objects.dbconnector import DBConnector
from geoprofielen.settings import ROOT_DIR

if __name__ == "__main__":
    dbc = DBConnector()
    dijktrajecten = dbc.get_dijktrajecten()

    geoprofilecreator = GeoProfileCreator(
        cpt_path = os.path.join(ROOT_DIR, "data/sonderingen"),
        borehole_path = os.path.join(ROOT_DIR, "data/boringen")
    )
    
    # todo > create LocationSegments.shp
    segmentid = 0 # we need ids that are unique over all dijktrajecten so we can create one big shapefile
    shapeinput = [] # this is where we store all info for the shape

    p = Path(ROOT_DIR) / "data/dam"
    p.mkdir(parents=True, exist_ok=True)
    
    fsegments = open(p / "segments.csv", 'w')
    fsoilprofiles = open(p / "soilprofiles.csv", 'w')
    fsegments.write("segment_id,soilprofile_id,probability,calculation_type\n")
    fsoilprofiles.write("soilprofile_id,top_level,soil_name\n")

    for dtcode, dijktraject in tqdm(dijktrajecten.items()):
        geoprofilecreator.dijktraject = dijktraject
        try:
            geoprofile = geoprofilecreator.execute()
            if len(geoprofile.soilprofiles) == 0: continue
            
            geoprofile.plot(os.path.join(ROOT_DIR, f"data/geoprofiel/{dtcode}.png"))
            
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

    w = shapefile.Writer(os.path.join(ROOT_DIR, "data/dam/LocationSegments.shp"))
    w.field('segment_id', 'C')

    for segment_id, xypoints in shapeinput:
        w.record(segment_id)
        w.line([xypoints])

    w.close()
    
