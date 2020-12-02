# achterhalen van alle gebruikte grondsoortnamen in de boringen

import os
from pathlib import Path
from geoprofielen.helpers import case_insensitive_glob
from geoprofielen.settings import ROOT_DIR
from geoprofielen.objects.borehole import Borehole
from tqdm import tqdm

f = open(os.path.join(ROOT_DIR,"./data/boringen/unknown_borehole_codes.csv"), 'w')
f_errors = open(os.path.join(ROOT_DIR,"./data/boringen/borehole_read_errors.csv"), 'w')
f_coords = open("./data/boringen/boreholecoords.csv", 'w')


if __name__ == "__main__":
    sfiles = case_insensitive_glob(os.path.join(ROOT_DIR, "data/boringen"), ".gef")
    
    for sfile in tqdm(sfiles):
        borehole = Borehole()        
        try:
            borehole.read(str(sfile)) 
        except Exception as e:
            f_errors.write(f"Error reading {sfile} with error {e}.\n")
            continue

        try:
            borehole.convert()
            borehole.plot(filepath="./data/boringen", filename=f"{sfile.stem}.png")
            f_coords.write(f"{borehole.x},{borehole.y},{Path(borehole.filename).stem}\n")
        except Exception as e:
            f.write(f"{e}\n")

f.close()
f_errors.close()
f_coords.close()
    
