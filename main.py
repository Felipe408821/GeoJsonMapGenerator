"""
Módulo principal para crear un mapa SHP.
"""

import map as mapa
import routes as route

if __name__ == '__main__':
    #mapa.create_map("Majadahonda, Spain", False, True)

    route.create_route("652_ida.json", "652A.json")
