# achterhalen van alle gebruikte grondsoortnamen in de boringen

from helpers import case_insensitive_glob
from objects.borehole import Borehole


if __name__ == "__main__":
    soilcodes = []
    bfiles = case_insensitive_glob("./data/boringen", ".gef")
    for bfile in bfiles:
        borehole = Borehole()

        try:
            borehole.read(str(bfile))
            soilcodes += [s.soilcode for s in borehole.soillayers]            

        except Exception as e:
            print(f"Error reading {bfile} with error {e}.")

    shortcodes = ["_".join(s.split('_')[0:2]) for s in soilcodes]


    f = open("unique_soilcodes.csv", 'w')
    for soilcode in list(set(shortcodes)):
        f.write(f"{soilcode}\n")
    f.close()

