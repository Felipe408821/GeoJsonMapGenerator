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


def create_route(input_json, output_json):
    stop_contents = read_json("routes/input/" + input_json)
    stops_dict, stops_id_list = procesar_paradas(stop_contents)
    save_json(stops_dict, "routes/output/" + output_json)

    print(stops_id_list)
