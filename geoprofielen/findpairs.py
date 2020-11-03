import os
from tqdm import tqdm
import math
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

from settings import ROOT_DIR, HDSR_SOIL_COLORS
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

            # now we're here let's also plot the boreholedata and cpt's to see the difference in borehole vs cpt interpretation
            fig = plt.figure(figsize=(6, 10))
            ax = fig.add_subplot()
            data = cpt.as_dataframe()
            data.plot(x='qc',y='z', ax=ax, label='qc [MPa]')
            data['Rf'] = 50. - data['Rf']
            data.plot(x='Rf',y='z', ax=ax, label='Rf [%]')
            cpt.convert()
            
            ax.text(1, cpt.soillayers[0].z_top + 1.0, Path(cpt.filename).stem)
            for soillayer in cpt.soillayers:
                facecolor = HDSR_SOIL_COLORS[soillayer.soilcode]
                ax.add_patch(
                    patches.Rectangle(
                        (0, soillayer.z_bottom),
                        25,
                        soillayer.height,
                        fill=True,
                        facecolor=facecolor,
                    )
                )

            ax.text(41, borehole.soillayers[0].z_top + 1.0, Path(borehole.filename).stem)
            for soillayer in borehole.soillayers:
                facecolor = HDSR_SOIL_COLORS[soillayer.soilcode]
                ax.add_patch(
                    patches.Rectangle(
                        (25, soillayer.z_bottom),
                        25,
                        soillayer.height,
                        fill=True,
                        facecolor=facecolor,
                    )
                )
            
            ax.grid(which="both")  
            zmax = max([sl.z_top for sl in cpt.soillayers] + [sl.z_top for sl in borehole.soillayers])          
            zmin = min([sl.z_bottom for sl in cpt.soillayers] + [sl.z_bottom for sl in borehole.soillayers])          
            ax.set_xlim(0,50)
            ax.set_ylim(zmin - 1.0, zmax + 3.0)
            name = f"{Path(cpt.filename).stem}_{Path(borehole.filename).stem}"

            dist = math.sqrt(math.pow(borehole.x - cpt.x, 2) + math.pow(borehole.y - cpt.y, 2))

            plt.title(f"{name} distance={dist:0.2f}m")
            plt.savefig(os.path.join(ROOT_DIR,f"data/machinelearning/{name}.png"))
            plt.close()

        except Exception as e:
            print(e)

    finaldata.to_csv(os.path.join(ROOT_DIR,"data/machinelearning/alldata.csv"))

    
