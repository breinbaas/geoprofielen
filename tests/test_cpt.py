import pytest

from geoprofielen.objects.cpt import CPT

def test_read():
    cpt = CPT()
    cpt.read("./tests/testdata/in/cpt.gef")
    
    assert(cpt.name == "DKM-227")
    assert(cpt.x == 139081.7)
    assert(cpt.y == 446328.1)
    assert(cpt.z_top == 0.73)
    assert(cpt.z_min == -14.48)


def test_filter():
    cpt = CPT()
    cpt.read("./tests/testdata/in/cpt.gef")

    layers = cpt.filter(0.2)
    assert(layers.shape == (76, 6))

    layers = cpt.filter(0.1)
    assert(layers.shape == (153, 6))

def test_plot():
    cpt = CPT()
    cpt.read("./tests/testdata/in/cpt.gef")
    cpt.convert()
    cpt.plot(filepath="./tests/testdata/out")