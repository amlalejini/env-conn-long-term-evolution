'''
This file contains functions for generating different types of graphs (as
networkx objects).

Many of the functions from this are copied / adapted from those in this repository:
    https://github.com/amlalejini/alife-2024-spatial-chem-eco
'''

import random
import networkx as nx
import matplotlib.pyplot as plt

def gen_graph_well_mixed(nodes: int):
    """
    Function generates a well-mixed graph where all nodes are connected by edges.
    Attributes:
        nodes(int): Indicates the number of nodes input by user.
    Returns:
        The well-mixed graph based on the number of nodes and edges connecting the nodes.
    """
    graph = nx.Graph()
    graph.add_nodes_from([i for i in range(nodes)])
    graph.add_edges_from([(j, i) for i in range(nodes) for j in range(i) if i != j])
    return graph

def gen_graph_toroidal_lattice(graph_width:int, graph_height:int):
    """
    Function generates a toroidal lattice graph.
    Attributes:
        graph_width(int): Indicates the width of the lattice domain.
        graph_height(int): Indicates the height of the lattice domain.
    Returns:
        The toroidal graph based number of nodes and edges.
    """
    graph = nx.Graph()
    # Create grid to use to figure out edges
    grid = [[None for c in range(graph_width)] for r in range(graph_height)]
    # Assign vertex ids to each position in grid
    id = 0
    for r in range(graph_height):
        for c in range(graph_width):
            grid[r][c] = id
            graph.add_node(id)
            id += 1
    # Compute edges
    for r in range(graph_height):
        for c in range(graph_width):
            id = grid[r][c]
            up = grid[r-1][c]
            down = grid[(r+1) % graph_height][c]
            right = grid[r][(c+1) % graph_width]
            left = grid[r][c-1]
            graph.add_edge(id, up)
            graph.add_edge(id, down)
            graph.add_edge(id, right)
            graph.add_edge(id, left)
    return graph

def gen_graph_comet_kite(
        core_size:int,
        num_tails:int,
        additional_tail_nodes:int = 0,
        seed:int = 1
    ):
    """
    Function generates a comet-kite graph.

    Algorithm from "Exploring and mapping the universe of evolutionary graphs
    identifies structural properties affecting fixation and probability time"
    (Moller et al)

    Attributes:
        core_size(int): The number of nodes that make up the comet 'core' structure.
        num_tails(int): The number of tails that connect to the comet 'core' structure.
        additional_tail_nodes(int): The randomly assigned node connections that are added to the length of a comet tail.
        seed(int): Integer value used to intialize a pseudorandom generator.
    Returns:
        The comet-kite graph based on the number of nodes and edges.
    """
    random.seed(seed)
    # 1) Generate complete graph
    graph = nx.complete_graph(core_size)
    # If no nodes, return empty graph
    if core_size < 1:
        return graph
    # 2) Pick existing node to attach tail
    tail_root = 0
    # 3) Attach t ("tails") nodes to the tail_root node
    tail_nodes = [t for t in range(core_size, core_size + num_tails)]
    graph.add_nodes_from(tail_nodes)
    graph.add_edges_from([(tail_root, t) for t in tail_nodes])
    if len(tail_nodes) < 1:
        return graph
    # 4) Attach any additional tail nodes to existing tails
    for i in range(additional_tail_nodes):
        attach_point = random.choice(tail_nodes)
        new_node = core_size + num_tails + i
        graph.add_node(new_node)
        graph.add_edge(attach_point, new_node)
        tail_nodes.append(new_node)
    # print("Core nodes:", graph.nodes)
    # print("Initial tail nodes:", tail_nodes)
    # print("Edges: ", graph.edges)
    return graph

def gen_graph_circular_chain(nodes:int):
    """
    Function generates a cyclic graph.
    Attributes:
        nodes(int): The indicated number of nodes within the cyclic graph.
    Returns:
        The cyclic graph based number of nodes and edges.
    """
    graph = nx.path_graph(nodes)
    if nodes > 1:
        graph.add_edge(nodes - 1, 0)
    return graph

def gen_graph_linear_chain(nodes:int):
    """
    Function generates a linear chain or path graph.
    Attributes:
        nodes(int): The indicated number of nodes in the linear chain graph.
    Returns:
        The linear chain based number of nodes and edges.
    """
    graph = nx.Graph()
    graph.add_nodes_from([i for i in range(nodes)])
    graph.add_edges_from([(i, i + 1) for i in range(nodes - 1)])
    return graph

def gen_graph_star(nodes:int):
    """
    Function generates a star graph.
    Attributes:
        nodes(int): The indicated number of nodes in the star.
    Returns:
        A star shaped graph. More of a spoke though. (?)
    """
    graph = nx.star_graph(nodes)
    return graph

def gen_graph_windmill(cliques:int, clique_size:int):
    """
    Function generates a windmill style graph.
    Exploring effect of clusters around central node.
    Attributes:
        cliques(int): The number of cliques surrounding the central node.
        clique_size(int): The number of nodes in cliques.
    Returns:
        A windmill shaped graph.
    """
    graph = nx.windmill_graph(cliques, clique_size)
    return graph

def gen_graph_cycle(nodes:int):
    """
    Function generates a cycle graph.
    Attributes:
        nodes(int): The indicated number of nodes in the star.
    Returns:
        A cycle shaped graph.
    """
    graph = nx.cycle_graph(nodes)
    return graph

def gen_graph_wheel(nodes:int):
    """
    Function generates a wheel graph.
    Attributes:
        The wheel graph consists of a hub node connected to a cycle of (n-1) nodes (networkx)
        nodes(int): The indicated number of nodes in the wheel.
    Returns:
        A wheel shaped graph.
    """
    graph = nx.wheel_graph(nodes)
    return graph


def gen_graph_random_erdos_renyi(nodes:int,edge_prob:float, seed:int):
    """
    Function that generates a random graph structure.
    Attributes:
        nodes(int): The indicated number of nodes that in the random structure.
        edge_prob(float): Represents the probability an edge will be created between nodes.
        seed(int): Positive integer that intializes a random number generator.
    Returns:

    """
    graph = nx.erdos_renyi_graph(nodes, edge_prob, seed)
    print(graph.nodes)
    print(graph.edges)
    return graph

def gen_graph_random_barabasi_albert(nodes:int, edges:int, seed:int):
    """
    Function generates a random graph structure.
    Attributes:
        nodes(int): The indicated number of nodes that will make up the random graph structure.
        edges(int): The indicated number of edges that will connect a new node to an existing node.
        seed(int): Positive integer that intializes a random number generator.
    Returns:
         A random graph structure.
    """
    graph = nx.barabasi_albert_graph(nodes, edges, seed)
    return graph

def gen_graph_random_waxman(nodes:int, beta:float, alpha:float, seed:int):
    """
    Function generates a random graph structure.
    Attributes:
        nodes(int): The indicated number of nodes included in the random graph structure.
        beta(float): Model parameter needed for random waxman graph generator.
        alpha(float): Model parameter needed for random waxman graph generator.
        seed(int): Positive integer that intializes a random number generator.
    Returns:
        A random graph structure.
    """
    graph = nx.waxman_graph(n=nodes,beta=beta,alpha=alpha,seed=seed)
    return graph

def gen_graph_random_geometric(nodes:int, radius:float, dimension:int, seed:int ):
    """
    Function generates a random geometric graph. Based on the workings of Penrose.
    Attributes:
        nodes(int): The indicated number of nodes included in the random graph structure.
        radius(float):
        dimension(int):
        seed(int): Positive integer that intializes a random number generator.
    Returns:
        The a random graph structure based on the parameters of
    """
    graph = nx.random_geometric_graph()
    return graph

def gen_graph_clique_ring(clique_size:int, clique_count:int, nodes_between_cliques:int = 0):
    '''
    Function generates a ring of k-cliques.
    Atributes
        clique_size (int): Size of each clique in the ring
        clique_count (int): Number of cliques in the ring
        nodes_between_cliques (int): Number of nodes between cliques in the ring
    '''
    cliques = [ [(c * clique_size) + k for k in range(clique_size)] for c in range(clique_count)]
    next_node_id = (clique_count * clique_size)
    graph = nx.Graph()
    # Add each clique to graph
    for clique_id in range(len(cliques)):
        clique_nodes = cliques[clique_id]
        graph.add_nodes_from(clique_nodes)
        graph.add_edges_from([(node_j, node_i) for node_i in clique_nodes for node_j in clique_nodes if node_i != node_j])
        # Add all clique nodes, connect them to one another.
        # for node_id in clique_nodes:
        #     graph.add_node()
    # Connect cliques together
    for clique_id in range(len(cliques)):
        next_clique_id = (clique_id + 1) % len(cliques)
        cur_clique_conn_point = random.choice(cliques[clique_id])
        next_clique_conn_point = random.choice(cliques[next_clique_id])
        # If no nodes between cliques, add edge from curren to next.
        if nodes_between_cliques == 0:
            graph.add_edge(cur_clique_conn_point, next_clique_conn_point)
        else:
            # Add between-clique nodes one-by-one
            prev_node = cur_clique_conn_point
            for _ in range(nodes_between_cliques):
                graph.add_node(next_node_id)
                graph.add_edge(prev_node, next_node_id)
                prev_node = next_node_id
                next_node_id += 1
            graph.add_edge(prev_node, next_clique_conn_point)

    # print(graph.nodes)
    # print(graph.edges)

    # print(cliques)
    # print(next_node_id)
    return graph



    # [(j, i) for i in range(nodes) for j in range(i) if i != j]
# g = gen_graph_clique_ring(5, 4, 5)
# nx.draw(g, pos = nx.kamada_kawai_layout(g),  with_labels = True)
# plt.show()