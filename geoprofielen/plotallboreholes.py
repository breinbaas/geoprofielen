# achterhalen van alle gebruikte grondsoortnamen in de boringen

import os
from helpers import case_insensitive_glob
from settings import ROOT_DIR
from objects.borehole import Borehole
from tqdm import tqdm

f = open(os.path.join(ROOT_DIR,"tests/testdata/out/unknown_borehole_codes.csv"), 'w')

if __name__ == "__main__":
    sfiles = case_insensitive_glob(os.path.join(ROOT_DIR, "data/boringen"), ".gef")

    for sfile in tqdm(sfiles):
        borehole = Borehole()        
        try:
            borehole.read(str(sfile))
            try:
                borehole.convert()
                borehole.plot(filepath="./data/boringen", filename=f"{sfile.stem}.png")
            except Exception as e:
                f.write(f"{e}\n")


            
        except Exception as e:
            print(f"Error reading {sfile} with error {e}.")

f.close()

    
