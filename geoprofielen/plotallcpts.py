# achterhalen van alle gebruikte grondsoortnamen in de boringen
from pathlib import Path
from geoprofielen.helpers import case_insensitive_glob
from geoprofielen.objects.cpt import CPT, ConversionType
from tqdm import tqdm


if __name__ == "__main__":
    f = open("./data/sonderingen/cptcoords.csv", 'w')
    sfiles = case_insensitive_glob("./data/sonderingen", ".gef")
    for sfile in tqdm(sfiles):
        cpt = CPT()        
        try:
            cpt.read(str(sfile))
            cpt.convert()
            cpt.plot(filepath="./data/sonderingen", filename=f"{sfile.stem}_threetype.png")
            cpt.convert(conversion_type=ConversionType.NEN_5104)
            cpt.plot(filepath="./data/sonderingen", filename=f"{sfile.stem}_nen.png")
            f.write(f"{cpt.x},{cpt.y},{Path(cpt.filename).stem}\n")

        except Exception as e:
            print(f"Error reading {sfile} with error {e}.")

    f.close()

    
