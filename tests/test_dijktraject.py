import pytest
from shapely.geometry import Polygon, Point

from geoprofielen.objects.dijktraject import DijkTraject

def test_point_in_soilinvestigation_polygon():
    dt = DijkTraject()
    dt.soilinvestigation_polygon = [(-1,-1),(-1,1),(1,1),(1,-1)]
    assert dt.point_in_soilinvestigation_polygon(x=0, y=0) == True
    assert dt.point_in_soilinvestigation_polygon(x=-2, y=0) == False
    # punten die de polygon zijn uitgesloten van de inhoud van de polygon
    assert dt.point_in_soilinvestigation_polygon(x=1, y=1) == False
    
def test_point_in_soilinvestigation_polygon_no_polygon():
    dt = DijkTraject()
    # alles moet goedgekeurd worden
    assert dt.point_in_soilinvestigation_polygon(x=0, y=0) == True
    assert dt.point_in_soilinvestigation_polygon(x=-2, y=0) == True
    assert dt.point_in_soilinvestigation_polygon(x=1, y=1) == True