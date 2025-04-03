import json
from bs4 import BeautifulSoup
import numpy as np
import matplotlib.pyplot as plt


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



# Definir la función de demanda
def Dem(t):
    return 1 + 0.5 * np.sin((2 * np.pi / 10) * (t - 5)) + 0.5 * np.sin((2 * np.pi / 10) * (t - 16))

if __name__ == '__main__':
    # Crear un rango de tiempo de 0 a 24 horas
    t_values = np.linspace(0, 24, 1000)
    dem_values = Dem(t_values)

    # Graficar la función
    plt.figure(figsize=(8, 4))
    plt.plot(t_values, dem_values, label=r"$Dem(t) = 1 + 0.5 \sin\left(\frac{2\pi}{10} (t - 5)\right) + 0.5 \sin\left(\frac{2\pi}{10} (t - 16)\right)$", color='b')

    # Marcar los picos esperados
    plt.axvline(x=8, color='r', linestyle='--', label="Pico Máximo (8:00)")
    plt.axvline(x=18, color='g', linestyle='--', label="Pico Máximo (18:00)")

    # Etiquetas y título
    plt.xlabel("Tiempo (horas)")
    plt.ylabel("Demanda (Dem)")
    plt.title("Función de Demanda con Picos a las 8 y 18 horas")
    plt.legend()
    plt.grid(True)

    # Mostrar la gráfica
    plt.show()