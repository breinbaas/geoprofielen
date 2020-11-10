ROOT_DIR = "C:/Users/brein/Programming/Python/HDSR/geoprofielen/" # verwijzing naar data locatie

DEFAULT_MINIMUM_LAYERHEIGHT = 0.2 # minimale laaghoogte bij grondsoort conversies (bvt cpt -> grondsoorten)
DEFAULT_CHAINAGE_STEP = 10 # stapgrootte tussen punten op de referentielijn om te zoeken naar grondonderzoek

MAX_CPT_DISTANCE = 100 # maximale afstand tussen RD punt en sondering
MAX_BOREHOLE_DISTANCE = 100 # maximale afstand tussen RD punt en boring

HDSR_SOIL_COLORS = { # kleuren die gekoppeld zijn aan de HDSR grondsoorten
    "klei_siltig":"#75923c",
    "klei_zandig":"#c3d69b",
    "klei_humeus":"#6b6c44",
    "veen":"#984806",
    "zand":"#ffff00",
    "leem":"#ffc000"
}

BOREHOLE_CODES = { # vertaling van boring code in gef bestand naar HDSR grondsoorten
    "klei_siltig":["Ks1", "Ks2", "Ks3", "Ks4", "K_","Ks","k2_"], # note met Ilse afgesproken dat Ks4 als klei_siltig wordt geclassificeerd
    "klei_zandig":["Kz1","Kz2","Kz3","kZ3"],
    "klei_humeus":["Kh1","Kh2","Kh3"],
    "veen":["Kh4","Vkm","Vk1","Vk2","Vk3","Vz1","Vz2","V_","Vm_","Vz"], # note met Ilse afgesproken dat Kh4 als veen wordt geclassificeerd
    "zand":["Zs1","Zs2","Zs3","Zs4","Lz1","Lz2","Lz3","ZMG","ZMF","ZZF","ZZG","Z_","Zk","Zg2","Zh2","zg2"],
    "leem":["Lz1","Lz2","Lz3"]
}