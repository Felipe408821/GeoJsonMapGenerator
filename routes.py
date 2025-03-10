def route():
    # Guarda los resultados en un archivo OSM
    with open("bus_651_relation.osm", "w", encoding="utf-8") as file:
        file.write(result.get_xml())

    print("Datos de la relación guardados en 'bus_651_relation.osm'.")
    #processRoute()


def processRoute():
    # Carga el archivo OSM
    tree = ET.parse("bus_651_relation.osm")
    root = tree.getroot()

    # Itera sobre los elementos del archivo OSM
    for element in root:
        if element.tag == "relation" and element.attrib["id"] == "4109022":
            print(f"Relación encontrada: {element.attrib['id']}")
            for member in element.findall("member"):
                print(
                    f"  Miembro: Tipo={member.attrib['type']}, Ref={member.attrib['ref']}, Rol={member.attrib.get('role', 'N/A')}")
        elif element.tag in ["node", "way"]:
            print(f"Elemento: {element.tag}, ID: {element.attrib['id']}")
            for tag in element.findall("tag"):
                print(f"  {tag.attrib['k']}: {tag.attrib['v']}")