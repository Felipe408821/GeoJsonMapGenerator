import json
from bs4 import BeautifulSoup

def read_json(ruta):
    """Carga un archivo JSON desde la routes especificada."""
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)


def extraer_info_parada(soup):
    """Extrae el nombre y el código de la parada del HTML parseado."""
    stop_name = soup.find('div', class_='Line_stopName__qAGtR')
    stop_code = soup.find('div', class_='Line_stopCodeSection__oJq+D')
    return {
        "stopName": stop_name.text.strip() if stop_name else None,
        "stopCodeSection": stop_code.text.strip().replace('#', '') if stop_code else None
    }


def procesar_paradas(stop_contents):
    """Procesa una lista de contenidos HTML para extraer información de las paradas."""
    stops_dict = {}
    codigos_list = []
    for i, content in enumerate(stop_contents):
        soup = BeautifulSoup(content, 'html.parser')
        info_parada = extraer_info_parada(soup)
        if info_parada["stopName"] and info_parada["stopCodeSection"]:
            stops_dict[f"Parada {i + 1}"] = info_parada
            codigos_list.append(info_parada["stopCodeSection"])
    return stops_dict, codigos_list


def save_json(datos, ruta):
    """Guarda los datos en un archivo JSON en la routes especificada."""
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
        print("[INFO]: Datos sobre la ruta especificada generados correctamente.")


def check_route():
    """Compara los códigos de parada del archivo JSON con las referencias del archivo GEOJSON."""

    # Cargar los datos del archivo JSON
    with open("routes/output/651A.json", 'r', encoding='utf-8') as f:
        paradas_json = json.load(f)

    # Cargar los datos del archivo GEOJSON
    with open("geojson/paradas.geojson", 'r', encoding='utf-8') as f:
        paradas_geojson = json.load(f)

    # Extraer los códigos de parada del JSON
    codigos_json = {parada['stopCodeSection'] for parada in paradas_json.values()}

    # Extraer las referencias del GEOJSON
    referencias_geojson = {feature['properties']['ref'] for feature in paradas_geojson['features'] if
                           'ref' in feature['properties']}

    # Encontrar las paradas en el JSON que no están en el GEOJSON
    paradas_no_encontradas = codigos_json - referencias_geojson

    # Imprimir las paradas no encontradas
    if paradas_no_encontradas:
        print("Las siguientes paradas del JSON no se encontraron en el GEOJSON:")
        for codigo in paradas_no_encontradas:
            for nombre_parada, detalles in paradas_json.items():
                if detalles['stopCodeSection'] == codigo:
                    print(f"  - {nombre_parada} - {detalles['stopName']} (Código: {codigo})")
    else:
        print("Todas las paradas del JSON se encontraron en el GEOJSON.")


def create_route(input_json, output_json):
    stop_contents = read_json("routes/input/" + input_json)
    stops_dict, stops_id_list = procesar_paradas(stop_contents)
    save_json(stops_dict, "routes/output/" + output_json)

    print(stops_id_list)
