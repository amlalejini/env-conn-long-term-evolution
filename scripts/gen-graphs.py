'''
This script takes a .json file that describes graphs to generate, and outputs
requested graph files.
'''
import argparse
import json
import os
import graph_generators as ggen
import utilities as utils
import graph_utilities as gutils

# Define default values for generating each graph type
# - Fall back to defaults if not defined in config file.
defaults = {
    "well-mixed": {
        "nodes": 100
    },
    "toroidal-lattice": {
        "graph_width": 10,
        "graph_height": 10
    },
    "comet-kite": {
        "core_size": 40,
        "num_tails": 20,
        "additional_tail_nodes": 40
    },
    "linear-chain": {
        "nodes": 100
    },
    "star": {
        "nodes": 100
    },
    "random-erdos-renyi": {
        "nodes": 100,
        "edge_prob": 0.05,
        "seed": None

    },
    "random-barabasi-albert": {
        "nodes": 100,
        "edges": 10,
        "seed": None
    },
    "random-waxman": {
        "nodes": 100,
        "beta": 0.4,
        "alpha": 0.2,
        "seed": None
    },
    "random-geometric": {
        "nodes": 100,
        "radius": 5,
        "dimension": 2,
        "seed": None
    },
    "cycle": {
        "nodes": 100
    },
    "wheel": {
        "nodes": 100
    },
    "windmill": {
        "nodes": 100
    },
    "clique-ring": {
        "clique_size": 8,
        "clique_count": 10,
        "nodes_between_cliques": 2,
        "seed": None
    },
    "hierarchical-clique-ring": {
        "clique_size": 8,
        "community_count": 10,
        "layers": 2,
        "nodes_between_communities": 2,
        "seed": None
    }
}

output_modes = {
    "matrix": {
        "ext": "mat",
        "write_fun": gutils.write_undirected_graph_to_matrix
    },
    "edges": {
        "ext": "csv",
        "write_fun": gutils.write_undirected_graph_to_edges_csv
    }
}

def main():
    parser = argparse.ArgumentParser(description="Graph generator commandline interface.")
    parser.add_argument("--config", type=str, default="graphs.cfg", help=".json configuration file with settings for each graph to generate.")
    parser.add_argument("--dump_dir", type=str, default=".", help="Where to write output files")
    parser.add_argument("-l", "--list_graphs", action="store_true", help="List all available graphs (does not run generators).")
    parser.add_argument("-o", "--overwrite", action="store_true", help="If output file with exact same name exists in dump directory, regenerate and overwrite.")

    args = parser.parse_args()

    # List graphs?
    if args.list_graphs:
        print("Available graph generators:")
        for graph in ggen._graph_generators:
            print(f"  - {graph}")
        exit()

    # Read graph configuration
    if not os.path.isfile(args.config):
        print(f"Failed to open configuraiton file: {args.config}")
        exit(-1)
    config = None
    with open(args.config, "r") as fp:
        config = json.load(fp)
    # print(config)

    # Create dump directory
    utils.mkdir_p(args.dump_dir)

    # Loop over graphs specified in config, creating each.
    if "graphs-to-generate" not in config:
        print("Failed to find 'graphs-to-generate' list in configuration.")
        exit(-1)
    for graph_cfg in config["graphs-to-generate"]:
        graph_name = graph_cfg["graph"]
        generator = ggen.get_generator_fun(graph_name)
        gen_defaults = defaults[graph_name]
        gen_params = None
        if "params" in graph_cfg:
            # If params are specified in config, use them.
            # Fall back to defaults if missing any params.
            gen_params = {
                param:graph_cfg["params"][param] if param in graph_cfg["params"] else gen_defaults[param]
                for param in gen_defaults
            }
        else:
            # Otherwise, use all defaults.
            gen_params = {
                param:gen_defaults[param] for param in gen_defaults
            }
        # Default to generating one instance of this graph
        count = 1 if "count" not in graph_cfg else graph_cfg["count"]
        mode = "matrix" if "output_mode" not in graph_cfg else graph_cfg["output_mode"]
        if mode not in output_modes:
            print(f"Unrecognized output mode in graph config: \n{graph_cfg}")
            print("Defaulting to matrix output mode.")
            mode = "matrix"
        base_out_name = graph_name if "output_id" not in graph_cfg else graph_cfg["output_id"]
        print(f"Generating graphs {graph_cfg}")
        for i in range(count):
            # Build output file name
            out_name = ""
            if count > 1:
                file_id = i if ("base_seed" not in graph_cfg) or (graph_cfg["base_seed"] is None) else graph_cfg["base_seed"] + i
                out_name = f"{base_out_name}_{file_id}.{output_modes[mode]["ext"]}"
            else:
                out_name = f"{base_out_name}.{output_modes[mode]["ext"]}"
            out_path = os.path.join(args.dump_dir, out_name)
            if (not args.overwrite) and os.path.isfile(out_path):
                print(f"  {out_path} already exists, not overwriting")
                continue
            # Determine seed to use if graph generator takes seed
            # - Override seed in defaults/params with base + i if base seed is given
            if ("seed" in gen_params) and ("base_seed" in graph_cfg):
                gen_params["seed"] = graph_cfg["base_seed"] + i

            # Generate graph
            print(f"  Gen {out_name}: {gen_params}")
            graph = generator(**gen_params)

            # Grow graph?
            if "increase_size_to" in graph_cfg:
                # Note: set random seed here? Already set for random graphs, but not for non-random.
                ggen.add_random_nodes(graph, graph_cfg["increase_size_to"])
            print(f"  - Num nodes in graph: {len(graph)}")
            print(f"  - Num edges in graph: {len(graph.edges)}")
            output_modes[mode]["write_fun"](out_path, graph)

if __name__ == "__main__":
    main()