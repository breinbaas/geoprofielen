import shapefile

"""
Dit script verwacht een shape bestanden met daarin een offset van de referentielijn
waarvan 1 richting het water en 1 richting de polder. Het script vertaalt deze
twee lijnen naar een polygon vlak dat gebruikt kan worden om grondonderzoek te limiteren
tot alles wat binnen het vlak valt.

De output is een polygonen shape met daarin de naam van het dijktraject
"""

sf = shapefile.Reader("C:/Users/brein/Programming/Python/HDSR/geoprofielen/data/gis/soilinvestigation_area.shp")
sf_out = shapefile.Writer('C:/Users/brein/Programming/Python/HDSR/geoprofielen/data/gis/soilinvestigation_area_polygons.shp')
sf_out.field('naam', 'C')

shaperecords = sf.shapeRecords()
handled_shaperecords = []
matches = 0

for i in range(len(shaperecords)):
    r1 = shaperecords[i].record
    for j in range(i+1, len(shaperecords)):
        if shaperecords[j].record['naam'] == r1['naam'] and not r1['naam'] in handled_shaperecords:
            handled_shaperecords.append(r1['naam'])

            # now create a polygon out of it
            geom_points = shaperecords[i].shape.points
            geom_points += reversed(shaperecords[j].shape.points)
            geom_points += [geom_points[0]]            
            sf_out.poly([geom_points])
            sf_out.record(r1['naam'])
            

sf_out.close()

