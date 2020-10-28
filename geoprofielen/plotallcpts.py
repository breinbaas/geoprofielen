# achterhalen van alle gebruikte grondsoortnamen in de boringen

from helpers import case_insensitive_glob
from objects.cpt import CPT
from tqdm import tqdm


if __name__ == "__main__":
    sfiles = case_insensitive_glob("./data/sonderingen", ".gef")
    for sfile in tqdm(sfiles):
        cpt = CPT()        
        try:
            cpt.read(str(sfile))
            cpt.convert()
            cpt.plot(filepath="./data/sonderingen", filename=f"{sfile.stem}.png")
        except Exception as e:
            print(f"Error reading {sfile} with error {e}.")

    
