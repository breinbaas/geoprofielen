# this script is made to check a new batch of GEF files for double entries
from tqdm import tqdm
from geoprofielen.objects.borehole import Borehole
from geoprofielen.objects.cpt import CPT
import os, shutil
from pathlib import Path

NEW_GEF_DIR = "c:/Users/brein/Programming/Python/HDSR/geoprofielen/data/_nieuwedata/GEF-bestanden projecten HDSR/"
EXISTING_GEF_BOREHOLE_DIR = "c:/Users/brein/Programming/Python/HDSR/geoprofielen/data/boringen/"
EXISTING_GEF_CPT_DIR = "c:/Users/brein/Programming/Python/HDSR/geoprofielen/data/sonderingen/"

EXPORT_DIR_CPT = "C:/Users/brein/Programming/Python/HDSR/geoprofielen/data/_nieuwedata/cpt"
EXPORT_DIR_BOREHOLE = "C:/Users/brein/Programming/Python/HDSR/geoprofielen/data/_nieuwedata/borehole"

from helpers import case_insensitive_glob

boreholegefs = case_insensitive_glob(EXISTING_GEF_BOREHOLE_DIR, ".gef")
cptgefs = case_insensitive_glob(EXISTING_GEF_CPT_DIR, ".gef") 

boreholes = []
cpts = []

print("Reading existing boreholes...")
for fborehole in tqdm(boreholegefs):
    borehole = Borehole.from_file(fborehole)
    boreholes.append(borehole)

print("Reading existing cpts...")
for fcpt in tqdm(cptgefs):
    cpt = CPT.from_file(fcpt)
    cpts.append(cpt)

# save some stuff for easy checks, might need more characteristics if double entries are found
# but if not this should be fine
cptcoords = [(c.x, c.y, c.z_top) for c in cpts]
boreholecoords = [(b.x, b.y, b.z_top) for b in boreholes]

# read new stuff
print("Checking for double entries...")
for f in tqdm(case_insensitive_glob(NEW_GEF_DIR, ".gef")):
    # is this a cpt or borehole? only one way to find out..
    iscpt, skip = True, False
    lines = open(f, 'r').readlines()
    for line in lines:
        if line.find('#REPORTCODE') > -1 and line.find('GEF-BORE') > -1:
            iscpt = False
            break
        elif line.find('#REPORTCODE') > -1 and line.find('GEF-DISS') > -1:
            iscpt = False
            print(f"Found a dissipation test in file {f}, skipping this one...")
            skip = True
            break

    if not skip:
        if iscpt:
            try:
                cpt = CPT.from_file(f)
                cptinfo = (cpt.x, cpt.y, cpt.z_top)
                if cptinfo in cptcoords:
                    print(f"Found double entry {cpt.filename}")
                else:
                    shutil.move(f, f"{EXPORT_DIR_CPT}/{Path(cpt.filename).name}")
            except Exception as e:
                print(f"Could not read {f} with error {e}")
        else:
            try:
                borehole = Borehole.from_file(f)
                boreholeinfo = (borehole.x, borehole.y, borehole.z_top)
                if boreholeinfo in boreholecoords:
                    print(f"Found double entry {borehole.filename}")
                else:
                    shutil.move(f, f"{EXPORT_DIR_BOREHOLE}/{Path(borehole.filename).name}")
            except Exception as e:
                print(f"Could not read {f} with error {e}")

        
        



    
