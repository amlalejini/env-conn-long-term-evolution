import utilities as utils
import graph_generators as ggen
import networkx as nx
import statistics as stats

def summarize_graph(graph, name):
    properties = {"graph_name": name}
    # Check connectivity
    is_connected = nx.is_connected(graph)
    # Density
    properties["density"] = nx.density(graph)
    # Degree (mean, median, variance)
    node_degrees = [pair[1] for pair in nx.degree(graph)]
    properties["degree_mean"] = stats.mean(node_degrees)
    properties["degree_median"] = stats.median(node_degrees)
    properties["degree_variance"] = stats.variance(node_degrees)
    print("  degree done")
    properties["girth"] = nx.girth(graph)
    print("  girth done")
    properties["degree_assortivity_coef"] = nx.degree_assortativity_coefficient(graph)
    print("  degree assortivity coef done")
    properties["num_articulation_points"] = len(list(nx.articulation_points(graph)))
    print("  articulation points done")
    # properties["num_bridges"] = len(list(nx.bridges(graph)))
    # properties["max_clique_size"] = len(nx.make_max_clique_graph(graph).nodes)
    # properties["avg_clustering"] = nx.average_clustering(graph)
    # print("  avg clustering done")
    # properties["transitivity"] = nx.transitivity(graph)
    # print("  transitivity done")
    # properties["num_connected_components"] = nx.number_connected_components(graph)
    # properties["avg_node_connectivity"] = nx.average_node_connectivity(graph)
    # properties["edge_connectivity"] = nx.edge_connectivity(graph)
    # properties["node_connectivity"] = nx.node_connectivity(graph)
    # print("  connectivity done")
    properties["diameter"] = nx.diameter(graph) if is_connected else "error"
    print("  diameter done")
    # properties["radius"] = nx.radius(graph) if is_connected else "error"
    properties["kemeny_constant"] = nx.kemeny_constant(graph) if is_connected else "error"
    print("  kemeny constant done")
    # properties["global_efficiency"] = nx.global_efficiency(graph)
    # properties["wiener_index"] = nx.wiener_index(graph)
    # length_results = nx.all_pairs_shortest_path_length(graph)
    # max_short_path = max([max(focal_node[1].values()) for focal_node in length_results])
    # properties["longest_shortest_path"] = max_short_path
    return properties

def main():
    '''
    '''
    num_graphs = 1
    graph_size = 3600
    graphs = []
    graph_content = []

    ##########################################
    # generate focal graphs
    ##########################################
    # Generate random waxman graphs
    for i in range(num_graphs):
        print("  rw", i)
        graph = ggen.gen_graph_random_waxman(graph_size, 0.4, 0.2, i)
        graph_content.append(summarize_graph(graph, f"random_waxman_{i}"))

    # Comet-kite
    for i in range(num_graphs):
        graph = ggen.gen_graph_comet_kite(
            core_size = 1440,
            num_tails = 720,
            additional_tail_nodes = 1440
        )
        ggen.add_random_nodes(graph, graph_size)
        graph_content.append(summarize_graph(graph, f"comet_kite_{i}"))

    # Clique ring
    for i in range(num_graphs):
        graph = ggen.gen_graph_clique_ring(
            clique_size = 115,
            clique_count = 30,
            nodes_between_cliques = 5
        )
        ggen.add_random_nodes(graph, graph_size)
        graph_content.append(summarize_graph(graph, f"clique_ring_{i}"))

    # Wheel
    graph_content.append(
        summarize_graph(ggen.gen_graph_wheel(nodes = graph_size), "wheel")
    )

    #  Star
    graph_content.append(
        summarize_graph(ggen.gen_graph_star(nodes = graph_size), "star")
    )

    # Lattice
    graph_content.append(
        summarize_graph(
            ggen.gen_graph_toroidal_lattice(graph_width=60, graph_height=60),
            "toroidal-lattice"
        )
    )

    # Linear chain
    graph_content.append(
        summarize_graph(
            ggen.gen_graph_linear_chain(graph_size),
            "linear-chain"
        )
    )

    # Cycle
    graph_content.append(
        summarize_graph(
            ggen.gen_graph_cycle(graph_size),
            "cycle"
        )
    )

    # Windmill
    graph = ggen.gen_graph_windmill(clique_size=59, cliques=60)
    ggen.add_random_nodes(graph, graph_size)
    graph_content.append(
        summarize_graph(
            graph,
            "windmill"
        )
    )

    # Generate graph_size well-mixed graph
    graph_content.append(
        summarize_graph(
            ggen.gen_graph_well_mixed(graph_size),
            "well-mixed"
        )
    )

    ##########################################
    # Analyze graphs
    ##########################################
    # print("analyzing graph summary properties")
    # for graph_dict in graphs:


    utils.write_csv(output_path = "vg-graph-properties.csv", rows = graph_content)


if __name__ == "__main__":
    main()
