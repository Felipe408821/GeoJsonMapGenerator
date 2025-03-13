import xml.etree.ElementTree as ET
from osgeo import gdal


def processRoute():
    # Carga el archivo OSM
    tree = ET.parse("651_route.osm")
    root = tree.getroot()

    # Itera sobre los elementos del archivo OSM
    for element in root:
        if element.tag == "relation" and element.attrib["id"] == "4109022":
            print(f"Relación encontrada: {element.attrib['id']}")
            for member in element.findall("member"):
                print(f"  Miembro: Tipo={member.attrib['type']}, "
                      f"Ref={member.attrib['ref']}, Rol={member.attrib.get('role', 'N/A')}")
        elif element.tag in ["node", "way"]:
            print(f"Elemento: {element.tag}, ID: {element.attrib['id']}")
            for tag in element.findall("tag"):
                print(f"  {tag.attrib['k']}: {tag.attrib['v']}")

    osm_a_shp("651_route.osm", "prueba.shp")


def osm_a_shp(archivo_osm, archivo_shp):
    """
    Convierte un archivo OSM a Shapefile.

    Args:
        archivo_osm: Ruta al archivo OSM de entrada.
        archivo_shp: Ruta al archivo Shapefile de salida.
    """
    try:
        # Abre el archivo OSM
        driver_osm = ogr.GetDriverByName('OSM')
        datasource_osm = driver_osm.Open(archivo_osm)

        # Crea el Shapefile de salida
        driver_shp = ogr.GetDriverByName('ESRI Shapefile')
        datasource_shp = driver_shp.CreateDataSource(archivo_shp)

        # Obtiene la capa del OSM (puntos, líneas, polígonos)
        for i in range(datasource_osm.GetLayerCount()):
            capa_osm = datasource_osm.GetLayer(i)

            # Crea la capa correspondiente en el Shapefile
            capa_shp = datasource_shp.CreateLayer(capa_osm.GetName(), capa_osm.GetSpatialRef(), capa_osm.GetGeomType())

            # Copia las definiciones de los campos (atributos)
            definicion_capa = capa_osm.GetLayerDefn()
            for j in range(definicion_capa.GetFieldCount()):
                definicion_campo = definicion_capa.GetFieldDefn(j)
                capa_shp.CreateField(definicion_campo)

            # Copia las características (geometrías y atributos)
            for feature_osm in capa_osm:
                feature_shp = ogr.Feature(capa_shp.GetLayerDefn())
                feature_shp.SetGeometry(feature_osm.GetGeometryRef())

                # Copia los atributos
                for j in range(definicion_capa.GetFieldCount()):
                    feature_shp.SetField(j, feature_osm.GetField(j))

                capa_shp.CreateFeature(feature_shp)

        # Cierra los datasources
        datasource_osm = None
        datasource_shp = None

        print(f"Archivo Shapefile guardado en '{archivo_shp}'.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")


if __name__ == '__main__':
    try:
        from osgeo import gdal

        print(gdal.VersionInfo())
        print("GDAL/OGR is installed correctly.")
        processRoute()

    except ImportError:
        print("GDAL/OGR is NOT installed.")
