**GeoJsonMapGenerator** is a preprocessing tool designed to generate the geographic and route data required for the **AutoBusRoutingMAS** multi-agent simulation. It provides automated generation of city maps and bus routes in compatible formats for use within the GAMA platform.

The repository includes:

1. A script to generate GEOJSON maps containing roads and bus stops by simply providing the name of a city.
2. A route processing module that takes raw bus route input and produces structured route and stop identifiers ready to be used in GAML.
3. Output folders containing generated files compatible with the AutoBusRoutingMAS simulation.
4. A single entry point (main.py) to choose between map or route generation workflows.
