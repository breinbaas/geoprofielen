import os

from geoprofielen.objects.geoprofilecreator import GeoProfileCreator
from geoprofielen.objects.dbconnector import DBConnector
from geoprofielen.settings import ROOT_DIR

def test_dijktrajecten():
    dbc = DBConnector()
    dijktrajecten = dbc.get_dijktrajecten()

    # test met 237B1
    dijktraject = dijktrajecten['126']

    geoprofilecreator = GeoProfileCreator(
        cpt_path = os.path.join(ROOT_DIR, "data/sonderingen"),
        borehole_path = os.path.join(ROOT_DIR, "data/boringen"),
        dijktraject = dijktraject
    )

    geoprofile = geoprofilecreator.execute()
    geoprofile.plot("./tests/testdata/out/test_geoprofile.png")
    geoprofilecreator.save_log(os.path.join(ROOT_DIR, "data/geoprofiel/creator.log")) 

    








