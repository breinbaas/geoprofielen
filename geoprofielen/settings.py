ROOT_DIR = "/home/breinbaas/Programming/Python/HDSR/geoprofielen/"

HDSR_SOIL_COLORS = {
    "klei_siltig":"#75923c",
    "klei_siltig of klei,zandig":"#e3172b", # funny color because this one needs to go!
    "klei_zandig":"#c3d69b",
    "klei_humeus":"#6b6c44",
    "veen":"#984806",
    "zand":"#ffff00",
    "leem":"#ffc000"
}

BOREHOLE_CODES = {
    "klei_siltig":["Ks1", "Ks2", "Ks3","K_","Ks","k2_"],
    "klei_siltig of klei,zandig":["Ks4"], #todo > nagaan welke keuze we hier maken
    "klei_zandig":["Kz1","Kz2","Kz3","kZ3"],
    "klei_humeus":["Kh1","Kh2","Kh3"],
    "veen":["Kh4","Vkm","Vk1","Vk2","Vk3","Vz1","Vz2","V_","Vm_","Vz"], # note met Ilse afgesproken dat Kh4 als veen wordt geclassificeerd
    "zand":["Zs1","Zs2","Zs3","Zs4","Lz1","Lz2","Lz3","ZMG","ZMF","ZZF","ZZG","Z_","Zk","Zg2","Zh2","zg2"],
    "leem":["Lz1","Lz2","Lz3"]
}