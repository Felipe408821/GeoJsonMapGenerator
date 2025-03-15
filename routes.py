import json
from bs4 import BeautifulSoup

if __name__ == '__main__':
    # Cargar el archivo JSON
    with open('ruta/651_ida.json', 'r', encoding='utf-8') as f:
        stop_contents = json.load(f)

    # Crear un diccionario para almacenar la información
    stops_dict = {}
    codigos_list = []

    # Procesar cada elemento del JSON
    for i, content in enumerate(stop_contents):
        # Parsear el contenido HTML con BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Extraer el nombre de la parada (stopName)
        stop_name = soup.find('div', class_='Line_stopName__qAGtR')
        stop_name = stop_name.text.strip() if stop_name else None

        # Extraer el código de la parada (stopCodeSection)
        stop_code = soup.find('div', class_='Line_stopCodeSection__oJq+D')
        stop_code = stop_code.text.strip().replace('#', '') if stop_code else None

        # Almacenar en el diccionario
        if stop_name and stop_code:
            stops_dict[f"Parada {i + 1}"] = {
                "stopName": stop_name,
                "stopCodeSection": stop_code
            }
            codigos_list.append(stop_code)

    # Guardar el diccionario en un archivo JSON
    with open('ruta/stops_info.json', 'w', encoding='utf-8') as f:
        json.dump(stops_dict, f, ensure_ascii=False, indent=4)

    # Guardar el listado de códigos en un archivo JSON
    with open('ruta/codigos_list.json', 'w', encoding='utf-8') as f:
        json.dump(codigos_list, f, ensure_ascii=False, indent=4)

    # Mostrar el diccionario resultante
    print(stops_dict)

    # Mostrar el listado de códigos
    print(codigos_list)