"""
Módulo principal para crear un mapa GEOJSON.
"""

from map import map as mapa
from routes import routes as route

if __name__ == '__main__':
    #mapa.create_map("Majadahonda, Spain", False, False)

    route.create_route("652_vuelta.json", "652B.json")
