import pytest


from geoprofielen.objects.borehole import Borehole

def test_read():
    borehole = Borehole()
    borehole.read("./tests/testdata/in/borehole.gef")

    assert(borehole.x == 123419)
    assert(borehole.z_top == -0.48)
    assert(len(borehole.soillayers)==7)
    assert(borehole.soillayers[0].soilcode=="Kz3h2_WO_(resten)_DO_TGR_BR_KMST")
    assert(borehole.soillayers[-1].soilcode=="Zs2_ZZG_NE_GR_Restante_BZB.:_KL_(laagjes)")

def test_convert():
    borehole = Borehole()
    borehole.read("./tests/testdata/in/borehole.gef")

    borehole.convert()
    assert(len(borehole.soillayers)==2)

