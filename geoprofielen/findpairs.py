import os
from tqdm import tqdm
import math
import pandas as pd

from settings import ROOT_DIR
from helpers import case_insensitive_glob
from geoprofielen.objects.cpt import CPT
from geoprofielen.objects.borehole import Borehole

MAX_DIST = 20

if __name__ == "__main__":
    # first let's create a file with matches in x,y coords
    f = open(os.path.join(ROOT_DIR,"data/machinelearning/matches.csv"), 'w')
    sonderingen, boringen = [], []
    sfiles = case_insensitive_glob(os.path.join(ROOT_DIR, "data/sonderingen"), ".gef")
    bfiles = case_insensitive_glob(os.path.join(ROOT_DIR, "data/boringen"), ".gef")

    for sfile in tqdm(sfiles):
        cpt = CPT()
        cpt.read(sfile)
        sonderingen.append(cpt)

    for bfile in tqdm(bfiles):
        borehole = Borehole()
        borehole.read(bfile)

        for cpt in sonderingen:
            dx = cpt.x - borehole.x
            dy = cpt.y - borehole.y
            dl = math.sqrt(dx**2 + dy**2)
            if dl < MAX_DIST:
                f.write(f"{dl},{cpt.filename},{cpt.x},{cpt.y},{borehole.filename},{borehole.x},{borehole.y}\n")

    f.close()

    # ok now we have the pairs let's extract all possible data from both sources
    # this will create a big csv file with cpt data combined with the soilnames of the boreholes
    lines = open(os.path.join(ROOT_DIR,"data/machinelearning/matches.csv"), 'r').readlines()
    finaldata = None
    for line in lines:
        args = line.split(',')
        cpt = CPT()
        cpt.read(args[1])
        borehole = Borehole()
        borehole.read(args[4])
        try:
            borehole.convert()
            data = cpt.as_dataframe()
            data["grondsoort"] = ""

            for soillayer in borehole.soillayers:
                data.loc[(data["z"]>=soillayer.z_bottom) & (data["z"]<=soillayer.z_top), ['grondsoort']] = soillayer.soilcode
                
            data = data.loc[data['grondsoort']!=""]            

            if finaldata is None:
                finaldata = data
            else:
                finaldata = pd.concat([finaldata, data], axis=0)

        except Exception as e:
            print(e)

    finaldata.to_csv(os.path.join(ROOT_DIR,"data/machinelearning/alldata.csv"))