import argparse
import os
import sys
import networkx as nx
import graph_utilities as graph_utils
import utilities as utils
import statistics as stats

def write_csv(output_path, summary_dict):
    # (1) What's the header?
    header = list(summary_dict[0].keys())
    header.sort()
    # (2) Collect all lines as strings
    lines = []
    for info in summary_dict:
        line_header_info = sorted(list(info.keys()))
        if line_header_info != header:
            print("Header mismatch!")
            exit(-1)
        line = ",".join([str(info[field]) for field in header])
        lines.append(line)
    out_content = ",".join(header) + "\n"
    out_content += "\n".join(lines)

    with open(output_path, "w") as fp:
        fp.write(out_content)

    return header

def analyze_graph(graph):
    properties = {}

    # Check connectivity
    print("Calculating: connectivity")
    is_connected = nx.is_connected(graph)
   
    # Density
    print("Calculating: density")
    properties["density"] = nx.density(graph)
    
    # Degree (mean, median, variance)
    print("Calculating: Degree(mean,meadian,variance)")
    node_degrees = [pair[1] for pair in nx.degree(graph)]
    properties["degree_mean"] = stats.mean(node_degrees)
    properties["degree_median"] = stats.median(node_degrees)
    properties["degree_variance"] = stats.variance(node_degrees)

    print("Calculating: girth")
    properties["girth"] = nx.girth(graph)

    print("Calculating: degree assortivity coefficient")
    properties["degree_assortivity_coef"] = nx.degree_assortativity_coefficient(graph)

    print("Calculating: Bridges")
    properties["num_bridges"] = len(list(nx.bridges(graph)))

    print("Calculating: Clique number")
    properties["max_clique_size"] = len(nx.make_max_clique_graph(graph).nodes)

    print("Calculating: transitivity")
    properties["transitivity"] = nx.transitivity(graph)

    print("Calculating: average clustering")
    properties["avg_clustering"] = nx.average_clustering(graph)

    print("Calculating: connected components")
    properties["num_connected_components"] = nx.number_connected_components(graph)

    print("Calculating: number of articulation points")
    properties["num_articulation_points"] = len(list(nx.articulation_points(graph)))

    # Takes a long time
    # print("Calculating: average node connectivity")
    # properties["avg_node_connectivity"] = nx.average_node_connectivity(graph)

    print("Calculating: edge connectivity")
    properties["edge_connectivity"] = nx.edge_connectivity(graph)

    #Took a couple minutes on test graphs but did run. 
    print("Calculating: node connectivity")
    properties["node_connectivity"] = nx.node_connectivity(graph)

    print("Calculating: diameter")
    properties["diameter"] = nx.diameter(graph) if is_connected else "error"

    print("Calculating: radius")
    properties["radius"] = nx.radius(graph) if is_connected else "error"
    
    #kemeny_constant not a part of nx anymore
    # print("Calculating: kemney constant")
    # properties["kemeny_constant"] = nx.kemeny_constant(graph) if is_connected else "error"

    print("Calculating: global efficiency")
    properties["global_efficiency"] = nx.global_efficiency(graph)

    print("Calculating: wiener index")
    properties["wiener_index"] = nx.wiener_index(graph)
    # properties["small_world_sigma"] = nx.sigma(graph)
    # properties["small_world_omega"] = nx.omega(graph)

    #Recent additions
    length_results = nx.all_pairs_shortest_path_length(graph)
    max_short_path = max([max(focal_node[1].values()) for focal_node in length_results])
    properties["longest_shortest_path"] = max_short_path
    # properties["connectivity"] = nx.all_pairs_node_connectivity(graph)

    return properties

def main():
    parser = argparse.ArgumentParser(
        usage = "Computes and records graph properties from graphs."
    )
    parser.add_argument("--graph_dir", type = str, default = "./", help = "Directory with graphs to load and process.")
    parser.add_argument("--graph_file_identifiers", type = str, nargs="+", default=["graph"], help = "Set of strings to match to in graph file names.")
    parser.add_argument("--dump_dir", type = str, default = "./", help = "Where to write output files?")
    parser.add_argument("--output_name", type = str, default = "graph-properties.csv", help = "Name of output file.")

    args = parser.parse_args()
    graph_dir = args.graph_dir
    graph_file_identifiers = args.graph_file_identifiers
    dump_dir = args.dump_dir
    output_name = args.output_name

    utils.mkdir_p(dump_dir)

    # Verify that the given graph directory exits
    if not os.path.exists(graph_dir):
        print("Unable to find graph directory.")
        exit(-1)
    # Gather file names of graphs to process
    graph_files = [f for f in os.listdir(graph_dir) if all([s in f for s in graph_file_identifiers])]
    graph_data = []
    cur_g = 0
    for graph_file in graph_files:
        cur_g += 1
        print(f"-- {graph_file} --")
        print(f"Processing graph {cur_g} / {len(graph_files)}")
        graph_path = os.path.join(graph_dir, graph_file)
        graph = graph_utils.read_graph_matrix(graph_path, directed=False)
        graph_properties = analyze_graph(graph)
        graph_properties["graph_name"] = graph_file
        # Extract "graph type" from file name (makes assumptions about file name scheme)
        graph_type = graph_file
        graph_type = graph_type.replace("graph-", "")
        graph_type = graph_type.split(".")[0]
        graph_type = graph_type.split("_")[0]
        graph_properties["graph_type"] = graph_type

        for key in graph_properties:
            print(f"{key}: {graph_properties[key]}")

        graph_data.append(graph_properties)

    write_csv(os.path.join(dump_dir, output_name), graph_data)


if __name__ == "__main__":
    main()
