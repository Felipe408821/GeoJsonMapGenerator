import os
import osmnx as ox
import numpy as np
import matplotlib.pyplot as plt


def create_map(city):
    """Crea y visualiza un mapa de la ciudad con carreteras y paradas de autobús."""
    # pylint: disable=invalid-name

    # Obtenemos los datos
    graph = get_road_network(city)
    bus_stops = get_bus_stops(city)

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
    plt.legend(prop={'size': 28}, markerscale=20)
    plt.show()

    # Exportar el mapa a una imagen
    export_image(fig, "MajadahondaMap", "png")

    # Exportar el grafo y las paradas a Shapefile
    export_shapefiles("shapefiles", graph, bus_stops)


def get_road_network(city, network_type="drive"):
    """Obtiene la red de carreteras de la ciudad."""
    return ox.graph_from_place(city, network_type=network_type)


def get_bus_stops(city):
    """Obtiene las paradas de autobús de la ciudad."""
    tags = {'highway': 'bus_stop'}
    bus_stops = ox.geometries.geometries_from_place(city, tags)
    bus_stops['id'] = range(1, len(bus_stops) + 1)
    return bus_stops


def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def export_image(fig, file_name, file_format):
    fig.savefig("images/" + file_name +"." + file_format, dpi=600, bbox_inches='tight', pad_inches=0, format=file_format)

    print("Imagen exportada correctamente.")


def export_shapefiles(directory, graph, bus_stops):
    """Exporta el grafo y las paradas de autobús a Shapefile."""
    # Convierte el grafo en GeoDataFrames (nodos y aristas)
    nodos, aristas = ox.graph_to_gdfs(graph)

    # Exporta los nodos a Shapefile
    nodos_path = path_output(directory, "nodos.shp")
    nodos.to_file(nodos_path)

    # Exporta las aristas a Shapefile
    aristas_path = path_output(directory, "aristas.shp")
    aristas.to_file(aristas_path)

    # Exporta las paradas de autobús a Shapefile
    bus_path = path_output(directory, "paradas.shp")
    bus_stops.to_file(bus_path)

    print("Datos exportados a Shapefile correctamente.")


def path_output(directory, file_name):
    return os.path.join(directory, file_name)
