# achterhalen van alle gebruikte grondsoortnamen in de boringen

import os
from tqdm import tqdm

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
    
    for dtcode, dijktraject in tqdm(dijktrajecten.items()):
        geoprofilecreator.dijktraject = dijktraject
        try:
            geoprofile = geoprofilecreator.execute()
            geoprofile.plot(f"../data/geoprofiel/{dtcode}.png")
        except Exception as e:
            print(f"Got error trying to generate geoprofile for dijktraject {dtcode}; {e}")
    
