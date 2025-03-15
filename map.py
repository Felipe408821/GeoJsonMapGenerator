import os
import osmnx as ox
import numpy as np
import networkx as nx
import shapely.geometry
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from shapely.geometry import Point
import matplotlib.patches as mpatches


def create_map(city, flag_image, flag_geojson):
    """Crea y visualiza un mapa de la ciudad con carreteras y paradas de autobús."""
    # pylint: disable=invalid-name

    # Obtenemos los datos
    graph = get_road_network(city)
    buildings = get_buildings(city)
    bus_stops = get_bus_stops(city)

    graph, bus_stops = integrate_bus_stops_into_graph(graph, bus_stops)

    check_grafo(graph, bus_stops)

    # Crea una figura y un eje para la red de carreteras
    fig, ax = ox.plot_graph(
        graph,
        figsize=(30, 30),
        node_color='b',
        node_size=0,
        edge_color='gray',
        show=False,
        close=False
    )

    if not buildings.empty:
        buildings.plot(ax=ax, color='blue', alpha=0.5, label='Edificios')

    # Si se encontraron paradas de autobús, plotea las paradas
    if not bus_stops.empty:
        bus_stops.plot(ax=ax, color='red', marker='o', markersize=0.1, label='Paradas de autobús')

        # Almacena las posiciones de los textos para evitar solapamientos
        text_positions = []  # Guarda las coordenadas de los textos ya colocados

        # Itera sobre las paradas y coloca los textos con flechas
        for idx, row in bus_stops.iterrows():
            x, y = row.geometry.x, row.geometry.y  # Coordenadas de la parada
            texto = str(row['id'])  # Texto del ID
            dx, dy = 15, 10

            # Verifica si el texto se solapa con otros textos ya colocados
            for pos in text_positions:
                if distance((x + dx, y + dy), pos) < 0.2:  # Si hay solapamiento
                    dx, dy = -dx, -dy  # Cambia la dirección del desplazamiento

            # Añade la anotación con flecha
            ax.annotate(
                text=texto,  # Texto del ID
                xy=(x, y),  # Coordenadas de la parada
                xytext=(dx, dy),  # Desplazamiento del texto
                textcoords='offset points',  # Usar puntos de desplazamiento
                fontsize=8,  # Tamaño de la fuente
                color='white',  # Color del texto
                ha='center',  # Alineación horizontal centrada
                va='center',  # Alineación vertical centrada
                arrowprops=dict(arrowstyle='->', color='white', lw=0.5)  # Flecha
            )

            # Guarda la posición del texto para evitar solapamientos futuros
            text_positions.append((x + dx, y + dy))

    # Personaliza el gráfico
    ax.set_title('Red de carreteras y paradas de autobús en Majadahonda', fontsize=32)

    # Crear manualmente los elementos de la leyenda
    road_line = mlines.Line2D([], [], color='gray', linewidth=2, label='Carreteras')
    bus_stop_marker = mlines.Line2D([], [], color='red', marker='o', linestyle='None',
                                    markersize=10, label='Paradas de autobús')
    building_patch = mpatches.Patch(color='blue', alpha=0.5, label='Edificios')

    # Añadir la leyenda
    plt.legend(handles=[road_line, bus_stop_marker, building_patch], prop={'size': 28})

    if flag_image:
        plt.show()
        # Exportar el mapa a una imagen
        export_image(fig, "MajadahondaMap", "png")

    if flag_geojson:
        # Exportar el grafo y las paradas a Shapefile
        export_geojson("geojson", graph, buildings, bus_stops)


def integrate_bus_stops_into_graph(G, bus_stops):
    """Integra las paradas de autobús conectándolas a la arista más cercana."""
    new_g = G.copy()
    nodes, edges = ox.graph_to_gdfs(new_g)

    new_bus_stops = bus_stops.copy()
    new_bus_stops["node_id"] = None  # Nueva columna para los nodos asignados
    new_bus_stops["geometry"] = None  # Se actualizarán las geometrías con las nuevas posiciones

    for idx, row in bus_stops.iterrows():
        bus_point = row.geometry
        closest_edge = None
        min_distance = float('inf')
        projected_point = None

        # Buscar la arista más cercana
        for edge_idx, edge in edges.iterrows():
            line = edge.geometry  # Línea de la arista
            proj = line.interpolate(line.project(bus_point))  # Proyectar parada sobre la arista
            dist = bus_point.distance(proj)

            if dist < min_distance:
                min_distance = dist
                closest_edge = edge_idx  # edge_idx es (u, v, key)
                projected_point = proj

        #print("Arista más cercana: ", closest_edge)

        # Si encontramos una arista válida, agregar la parada como nodo
        if closest_edge and projected_point:
            u, v, key = closest_edge  # Extraer nodos de la arista
            edge_data = G.get_edge_data(u, v, key).copy() # Copiamos los atributos de la arista

            new_node = max(new_g.nodes) + 1  # Nuevo ID de nodo

            if new_g.has_node(u) and new_g.has_node(v):
                pass
            else:
                print(f"Error: No se puede agregar la arista ({u}, {v}) porque uno de los nodos no existe")

            new_g.add_node(new_node, x=projected_point.x, y=projected_point.y)

            print("Creamos nodo: ", new_node, projected_point.x, projected_point.y)

            if new_g.has_edge(u, v, key):
                print("Eliminando arista ", u, v)
                new_g.remove_edge(u, v, key)
            else:
                pass
                # print("Arista ", u, v, " no existe"

            edge_data['geometry'] = shapely.geometry.LineString(
                [(new_g.nodes[u]["x"], new_g.nodes[u]["y"]),
                 (new_g.nodes[new_node]["x"], new_g.nodes[new_node]["y"])]
            )
            new_g.add_edge(u, new_node, **edge_data)
            print("Creamos arista1: ", u, new_node)

            edge_data['geometry'] = shapely.geometry.LineString(
                [(new_g.nodes[new_node]["x"], new_g.nodes[new_node]["y"]),
                (new_g.nodes[v]["x"], new_g.nodes[v]["y"])]
            )
            new_g.add_edge(new_node, v, **edge_data)
            print("Creamos arista2: ", new_node, v)

            if new_g.has_edge(u, new_node) and new_g.has_edge(new_node, v):
                print(f"Conexión correcta: ({u}, {new_node}) y ({new_node}, {v})")
            else:
                print(f"Error: No se crearon correctamente las conexiones desde {u} hacia {v}")

            #print("\n")
            # Actualizar bus_stops con el nuevo nodo y coordenadas
            new_bus_stops.at[idx, "node_id"] = new_node
            new_bus_stops.at[idx, "geometry"] = Point(projected_point.x, projected_point.y)

    return new_g, new_bus_stops


def get_road_network(city, network_type="drive"):
    """Obtiene la red de carreteras de la ciudad."""
    return ox.graph_from_place(city, network_type=network_type)


def get_buildings(city):
    """Obtiene las edificaciones de la ciudad."""
    return ox.features.features_from_place(city, tags={'building': True})


def get_bus_stops(city):
    """Obtiene las paradas de autobús de la ciudad."""
    tags = {'highway': 'bus_stop'}
    bus_stops = ox.features.features_from_place(city, tags)
    bus_stops['id'] = range(1, len(bus_stops) + 1)
    return bus_stops


def distance(p1, p2):
    # pylint: disable=invalid-name
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def export_image(fig, file_name, file_format):
    directory = "images"
    # Crear el directorio si no existe
    check_directory(directory)

    fig.savefig(directory + "/" + file_name + "." + file_format, dpi=600, pad_inches=0,
                bbox_inches='tight', format=file_format)

    print("Imagen exportada correctamente.")


def export_geojson(directory, graph, buildings, bus_stops):
    """Exporta el grafo y las paradas de autobús a GeoJson."""
    # Crear el directorio si no existe
    check_directory(directory)

    # Convierte el grafo en GeoDataFrames (nodos y aristas)
    nodos, aristas = ox.graph_to_gdfs(graph)

    # Exporta los nodos
    nodos.to_file(os.path.join(directory, "nodos.geojson"), driver="GeoJSON")

    aristas["osmid"] = aristas["osmid"].apply(lambda x: x[0] if isinstance(x, list) else x)
    # Exporta las aristas
    aristas.to_file(os.path.join(directory, "aristas.geojson"), driver="GeoJSON")

    buildings = buildings[buildings.geometry.type.isin(['Polygon', 'MultiPolygon'])]
    # Exportar edificios
    buildings.to_file(os.path.join(directory, "edificios.geojson"), driver="GeoJSON")

    # Exporta las paradas de autobús
    bus_stops.to_file(os.path.join(directory, "paradas.geojson"), driver="GeoJSON")

    print("Datos exportados a GeoJson correctamente.")


def check_directory(directory):
    # Crear el directorio si no existe
    if not os.path.exists(directory):
        os.makedirs(directory)


def check_grafo(graph, bus_stops):

    # Verificar conexiones de los nuevos nodos
    for idx, row in bus_stops.iterrows():
        node_id = row["node_id"]
        neighbors = list(graph.neighbors(node_id))



        if len(neighbors) < 2:
            print(f"ERROR: Nodo {node_id} tiene solo {len(neighbors)} conexiones.", neighbors)
        else:
            print(f"Nodo {node_id} correctamente conectado con {len(neighbors)} nodos.")

    # Verificar si el grafo es fuertemente conexo
    if nx.is_strongly_connected(graph):
        print("El grafo es fuertemente conexo. Todas las paradas están integradas correctamente.")
    else:
        print("ERROR: El grafo NO es fuertemente conexo. Algunas paradas podrían no estar conectadas.")

    # Si el grafo no es conexo, ver qué componentes están desconectados
    components = list(nx.strongly_connected_components(graph))
    print(f"Hay {len(components)} componentes desconectados en el grafo.")
