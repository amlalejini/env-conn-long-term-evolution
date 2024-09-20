# Scripts

- `gen_spatial_network_events.py` - Converts graph files (in matrix format or as csv of edges) into avida event sequences :(
- `gen-graphs.py` - Generates graphs specified in a json configuration file (e.g., `example-graph-gen-config.cfg`)
- `graph_generators.py` - Collection of graph generator functions. If you want to add a new graph generator, this would be the file to implement it in! (+ add default values to `gen-graphs.py`)
- `graph_utilities.py` - Contains utility functions for reading / writing graph files, etc.
- `utilities.py` - Misc utility functions