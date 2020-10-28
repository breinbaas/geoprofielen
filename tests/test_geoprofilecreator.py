import os

from geoprofielen.objects.geoprofilecreator import GeoProfileCreator
from geoprofielen.objects.dbconnector import DBConnector
from geoprofielen.settings import ROOT_DIR

def test_dijktrajecten():
    dbc = DBConnector()
    dijktrajecten = dbc.get_dijktrajecten()

    # test met 237B1
    dijktraject = dijktrajecten['237B1']

    geoprofilecreator = GeoProfileCreator(
        cpt_path = os.path.join(ROOT_DIR, "data/sonderingen"),
        borehole_path = os.path.join(ROOT_DIR, "data/boringen"),
        dijktraject = dijktraject
    )

    geoprofilecreator.execute()
    print(geoprofilecreator.log)
    








