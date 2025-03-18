"""
Módulo principal para crear un mapa SHP.
"""

import map as mapa
import routes as route

if __name__ == '__main__':
    mapa.create_map("Majadahonda, Spain", True, False)

    route.create_route("L2.json", "L2.json")
