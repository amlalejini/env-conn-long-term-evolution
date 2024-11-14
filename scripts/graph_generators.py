'''
This file contains functions for generating different types of graphs (as
networkx objects).

Many of the functions from this are copied / adapted from those in this repository:
    https://github.com/amlalejini/alife-2024-spatial-chem-eco
'''
#TODO input validation/ edge case testing
print
import random
import networkx as nx
#import matplotlib.pyplot as plt
from typing import Optional

def gen_graph_well_mixed(nodes:int):
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
    graph = nx.star_graph(nodes - 1)
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

def gen_graph_random_erdos_renyi(nodes:int, edge_prob:float, seed:int):
    """
    Function that generates a random graph structure.
    Attributes:
        nodes(int): The indicated number of nodes that in the random structure.
        edge_prob(float): Represents the probability an edge will be created between nodes.
        seed(int): Positive integer that intializes a random number generator.
    Returns:

    """
    graph = nx.erdos_renyi_graph(nodes, edge_prob, seed)
    #print(graph.nodes)
    #print(graph.edges)
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

def gen_graph_random_geometric(nodes:int, radius:float, dimension:int, seed:int):
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
    graph = nx.random_geometric_graph(
        nodes,
        radius = radius,
        dim = dimension,
        seed = seed
    )
    return graph

def gen_graph_barbell(
      clique_size:int,
      chain_size:int
):
    '''
    Function generates a barbell graph (https://networkx.org/documentation/stable/reference/generated/networkx.generators.classic.barbell_graph.html)
    A barbell graph is a linear chain with two cliques on either end of the chain.
    Attributes:
        clique_size(int)
        chain_size(int)
    '''
    return nx.barbell_graph(m1 = clique_size, m2 = chain_size)

def gen_graph_clique_ring(
        clique_size:int,
        clique_count:int,
        nodes_between_cliques:int = 0,
        seed:Optional[int] = None
    ):
    '''
    Function generates a ring of k-cliques.
    Atributes
        clique_size (int): Size of each clique in the ring
        clique_count (int): Number of cliques in the ring
        nodes_between_cliques (int): Number of nodes between cliques in the ring
    '''
    # If seed provided, reset random number generator with that seed.
    if not seed is None:
        random.seed(seed)

    cliques = [ [(c * clique_size) + k for k in range(clique_size)] for c in range(clique_count)]
    next_node_id = (clique_count * clique_size)
    graph = nx.Graph()
    # Add each clique to graph
    for clique_id in range(len(cliques)):
        clique_nodes = cliques[clique_id]
        graph.add_nodes_from(clique_nodes)
        graph.add_edges_from([(node_j, node_i) for node_i in clique_nodes for node_j in clique_nodes if node_i != node_j])
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
    return graph

def _build_clique_ring_internal(
        clique_size: int,
        clique_count: int,
        nodes_between_cliques: int = 0,
        start_id: int = 0
    ):
    '''
    helper function for gen_graph_hierarhical_clique_ring
    '''
    # Generate clique node ids (per-clique)
    cliques = [ [((c * clique_size) + k) + start_id for k in range(clique_size)] for c in range(clique_count)]
    # Generate clique edges
    edges = [[clique_nodes[i], clique_nodes[j]] for clique_nodes in cliques for i in range(0, len(clique_nodes)) for j in range(i+1, len(clique_nodes))]
    next_node_id = start_id + (clique_count * clique_size)
    all_nodes = [node for clique in cliques for node in clique]
    # Connect cliques together
    for clique_id in range(len(cliques)):
        next_clique_id = (clique_id + 1) % len(cliques)
        cur_clique_conn_point = random.choice(cliques[clique_id])
        next_clique_conn_point = random.choice(cliques[next_clique_id])
        # If no nodes between cliques, add edge from curren to next.
        if nodes_between_cliques == 0:
            edges.append((cur_clique_conn_point, next_clique_conn_point))
        else:
            # Add between-clique nodes one-by-one
            prev_node = cur_clique_conn_point
            for _ in range(nodes_between_cliques):
                all_nodes.append(next_node_id)
                edges.append((prev_node, next_node_id))
                prev_node = next_node_id
                next_node_id += 1
            edges.append((prev_node, next_clique_conn_point))
    return {"nodes": all_nodes, "edges": edges}

def gen_graph_hierarchical_clique_ring(
    clique_size:int,
    community_count:int,
    layers: int = 0,
    nodes_between_communities:int = 0,
    seed:Optional[int] = None
):
    # If seed provided, reset random number generator with that seed.
    if not seed is None:
        random.seed(seed)
    # Layers = 0, no layers just single clique ring
    num_clique_rings = community_count**layers
    rings = []
    next_node_id = 0
    for _ in range(num_clique_rings):
        rings.append(
            _build_clique_ring_internal(
                clique_size = clique_size,
                clique_count = community_count,
                nodes_between_cliques = nodes_between_communities,
                start_id = next_node_id
            )
        )
        next_node_id += len(rings[-1]["nodes"])

    # Build a color map
    # color_map = {}
    # for ring_i in range(len(rings)):
    #     for node in rings[ring_i]["nodes"]:
    #         color_map[node] = ring_i
    # print(rings)
    # Build hierarchy bottom-up
    # In sets of size "community_count", merge rings together until everything has been merged.
    while len(rings) > 1:
        # print("-------merge layer-------")
        new_rings = []
        cur_ring = 0
        merges = len(rings) // community_count
        # print(f"Num merges to do: {merges}")
        # print(f"Total rings to merge together: {len(rings)}")
        # next_ring_id = (cur_ring + 1) %
        for _ in range(merges):
            # print(f"   Merging {community_count} rings together")
            # Connect community_count rings together
            new_rings.append({"nodes": [], "edges": []})
            first_ring = cur_ring
            for comm in range(community_count):
                # next ring to use?
                # next_ring = (cur_ring + 1) % len(rings)
                if comm < community_count - 1:
                    next_ring = cur_ring + 1
                else:
                    next_ring = first_ring
                # connect cur_ring to next ring
                cur_ring_conn_point = random.choice(rings[cur_ring]["nodes"])
                next_ring_conn_point = random.choice(rings[next_ring]["nodes"])
                if nodes_between_communities == 0:
                    new_rings[-1]["edges"].append((cur_ring_conn_point, next_ring_conn_point))
                    continue
                prev_node = cur_ring_conn_point
                for _ in range(nodes_between_communities):
                    new_rings[-1]["nodes"].append(next_node_id)
                    new_rings[-1]["edges"].append((prev_node, next_node_id))
                    prev_node = next_node_id
                    next_node_id += 1
                new_rings[-1]["edges"].append((prev_node, next_ring_conn_point))
                # Add all nodes/edges from ring_i to new_rings
                new_rings[-1]["nodes"].extend(rings[cur_ring]["nodes"])
                new_rings[-1]["edges"].extend(rings[cur_ring]["edges"])
                cur_ring += 1

            # # Connect cur ring back to first ring
            # cur_ring_conn_point = random.choice(rings[cur_ring]["nodes"])
            # first_ring_conn_point = random.choice(rings[first_ring]["nodes"])
            # if nodes_between_communities == 0:
            #     new_rings[-1]["edges"]

        # Update rings to be new_rings
        rings = new_rings

    # Create networkx graph
    graph = nx.Graph()
    graph.add_nodes_from(rings[0]["nodes"])
    graph.add_edges_from(rings[0]["edges"])
    # print(graph.nodes)
    # print(graph.edges)

    # nx.draw(
    #     graph,
    #     pos = nx.spring_layout(graph, iterations=10000),
    #     with_labels = True,
    #     # labels = [color_map[node] if node in color_map else num_clique_rings+1 for node in list(graph.nodes())],
    #     node_color = [color_map[node] if node in color_map else num_clique_rings+1 for node in list(graph.nodes())]
    # )
    # plt.show()

    return graph


def gen_graph_random_k_regular(k:int, nodes:int, seed:int):
    """
    Function generates a k-regular graph.
    Attributes:
        k(int): number of degrees of every node
        nodes(int): number of nodes in the graph
        seed(int): Positive integer that intializes a random number generator

    Returns:
        A random k-regular Graph on n nodes.
    """
    graph = nx.random_regular_graph(k, nodes, seed)
    return graph

def gen_graph_circular_ladder_graph(nodes:int):
    """
    Function generates a circullar ladder graph.
    Attributes:

        nodes(int): number of nodes in the graph
    Returns:
        A circular ladder Graph on n nodes.
    """
    if nodes% 2 != 0:
        raise Exception("impossible to generate circular ladder graph given inputs, nodes must be even")
    #generates 2 n length cycles. if you want n nodes in your graph, the nx graph must pass n/2
    graph = nx.circular_ladder_graph(int(nodes/2))
    return graph

def gen_graph_connected_caveman(num_cliques:int, clique_size:int):
    """
    Function generates a connected caveman graph.
    Attributes:
        num_cliques(int): The indicated number of cliques in the graph.
        clique_size(int): The size(number of vertices) in each clique
    Returns:
        A set of cliques connected via reataching one edge to a neighboring clique along a central cylce such that n cliques form a single unbroken loop (Watts 1999)
    """
    graph = nx.connected_caveman_graph(num_cliques, clique_size)
    return graph

# TODO See if guranteed connected/enforce connected

#allows for loops
#dont think graph can be disconnected but TODO add try catch
#can generate "chain of clique" esq structure
def gen_graph_relaxed_caveman(num_cliques:int, clique_size:int, P_rewiring:float, seed:int):
    """
    Function generates a relaxed caveman graph.
    Attributes:
        num_cliques(int): The indicated number of cliques in the graph.
        clique_size(int): The size(number of vertices) in each clique
        P_rewiring(flaot): The probability of rewiring each edge
        seed(int): Positive integer that intializes a random number generator
    Returns:
        A set of cliques (connected??) with each edge randomly reqired with specified probability to different clique
    """
    graph = nx.relaxed_caveman_graph(num_cliques, clique_size, P_rewiring, seed)
    return graph


def gen_graph_star_like(nodes:int, added_connections:int, seed:int):
    """
    Function generates a star-like graph.
    Attributes:
        nodes(int): Number of desired nodes in graph
        added_connections(int) the number of edges added randomly between pre-existing nodes
        seed(int): Positive integer that intializes a random number generator

    Returns:
       a star graph graph with randomly added edges(set number or random probability for all vertices tbd)
    """
    graph = nx.Graph()

    # If seed provided, reset random number generator with that seed.
    if not seed is None:
        random.seed(seed)
    #declare variables
    center_node = 0
    list_nodes = []
    list_nodes.append(center_node)
    list_edges = []

    #instantiate nodes
    for node in range(1, nodes):
        list_nodes.append(node)
        #For all nodes n, add edge between n and center node
        list_edges.append((0,node))
    graph.add_nodes_from(list_nodes)


    #ensure the number of added connections is correct
    while(len(list_edges) < (nodes -1 + added_connections)):

    #add new connections to graph
        for i in range (0, added_connections):
        #assign node1 any node other than center node
            node1 = random.choice(list_nodes)
            while(node1 == 0):
                node1 = random.choice(list_nodes)
            #find unique(not center or node1) node2
            node2 = random.choice(list_nodes)
            while(node2 == 0 or node2 == node1):
                node2 = random.choice(list_nodes)
                #print( str(node1) + "," + str(node2))

            #add edge if edge does not already exist
            if (node1,node1) not in list_edges:
                list_edges.append((node1,node2))
    graph.add_edges_from(list_edges)
    return graph

def gen_graph_probabilistic_star_like(nodes:int, P_connection:float, seed:int):
    """
    Function generates a star-like graph.
    Attributes:
        nodes(int): Number of desired nodes in graph
        added_connections(int) the number of edges added randomly between pre-existing nodes
        P_connecitons(flaot): Probability that each node generates a new edge between random node in graph
        seed(int): Positive integer that intializes a random number generator

    Returns:
       a star graph graph with randomly added edges(random probability for all vertices)
    """
    graph=nx.Graph()

    center_node = 0
    list_nodes = []
    list_nodes.append(center_node)
    list_edges = []

    #instantiate nodes
    for node in range(1, nodes):
        list_nodes.append(node)
        #For all nodes n, add edge between n and center node
        list_edges.append((0,node))
    graph.add_nodes_from(list_nodes)

    #for every node randomly add edge
    for n in range(1,nodes):
        #randomly select second node
        n2 = random.choice(list_nodes)
        #if edge already exist, append or loop, reassign n2
        while((n,n2) in list_edges or n == n2):
            n2 = random.choice(list_nodes)

        if random.random() <= P_connection:
            list_edges.append((n,n2))
    #convert to nxgraph
    graph.add_nodes_from(list_nodes)
    graph.add_edges_from(list_edges)
    return graph

def gen_graph_ring_k_regular(nodes:int, k:int, return_nxGraph:bool = True):
    """
    Function algorithmically generates a k-regular graph.
    Attributes:
        k(int): number of degrees of every node
        nodes(int): number of nodes in the graph
    Returns:
        A ring-like k-regular Graph on n nodes.
    """
    if (nodes * k) % 2 != 0:
        raise Exception("impossible to generate k-regular graph given inputs")
    list_nodes = []
    list_edges = []
    #instantiate nodes
    for n in range(nodes):
        list_nodes.append(n)
    #2 different methods for odd and even k's
    if k %2 ==0:
       for node in range(nodes):
            endpoints =[]
            endpoint1 = node
            for i in range(1,int(k/2) + 1):
                #add k nearest neighbors to list of other endpoints, think of nodes in a circle
                endpoints.append(list_nodes[(node +i) % len(list_nodes)])
                endpoints.append(list_nodes[(node -i) % len(list_nodes)])

                for endpoint2 in endpoints:
                    if (endpoint1,endpoint2) not in list_edges:
                        list_edges.append((endpoint1, endpoint2))

    #if k odd
    else:
        for node in range(nodes):
            endpoints = []
            endpoint1 = node
            for i in range(1, int(k/2) +1):
                #add k nearest neighbors to list of other endpoints, think of nodes in a circle
                endpoints.append(list_nodes[(node +i) % len(list_nodes)])
                endpoints.append(list_nodes[(node -i) % len(list_nodes)])
                #add node opposite node
                endpoints.append(list_nodes[( (node + (int(len(list_nodes)/2)))) % len(list_nodes)])

            #add edges to grpah
            for endpoint2 in endpoints:
                if (endpoint1,endpoint2) not in list_edges: #Pretty sure this line causes disgustingly long run-time for large k/num_edges
                        list_edges.append((endpoint1, endpoint2))
    if return_nxGraph:
        graph = nx.Graph()
        graph.add_nodes_from(list_nodes)
        graph.add_edges_from(list_edges)
    else:
        graph = {"nodes": list_nodes, "edges": list_edges}
    return graph

# def gen_graph_hierarchical_k_regular(layers:int, k:int, layer_size:int, connection_path_size:int):
#     graph = nx.Graph()
#     if layers == 0:
#         return gen_graph_ring_k_regular(layer_size,k,False)
#     else:
#         #generate k-regular
#         # repalce each node with one smaller layer k-reg
#         #

#         #toplayer = k-regular graph
#         toplayer = gen_graph_ring_k_regular(layer_size,k,False)
#         #every node becomes lower layer k-regular
#         for node in toplayer["nodes"]:
#             toplayer["nodes"][node] = gen_graph_hierarchical_k_regular(layers -1, k, layer_size, connection_path_size)["nodes"]

# #TODO rename nodes
#         for subList in toplayer["ndoes"]:
#             for node in sublist

#         for edge in toplayer["edges"]:
#             endpoint1 = random.choice(toplayer["nodes"][edge[0]])
#             endpoint2 = random.choice(toplayer["nodes"][edge[1]])
#             if connection_path_size == 0:
#                 toplayer["edges"][edge] = (endpoint1, endpoint2)
#             else:
#                 #TODO ?? ensure that connecting-cahin-nodes are not selected for future endpoints
#                 #create connection chains
#                 #this wont work but I think this is the gist
#                 for i in range(1, connection_path_size):
#                     toplayer["nodes"].append(toplayer["nodes"][-1][-1] + i)
#                     toplayer["edges"].append((endpoint1,toplayer["nodes"][-1][-1]))
#                 toplayer["edges"].append((toplayer["nodes"][-1][-1],endpoint2))


#     # graph.add_nodes_from(toplayer["nodes"])
#     # graph.add_edges_from(toplayer["edges"])
#     #print(graph)
#     print(toplayer)
#     # nx.draw(
#     #         graph,
#     #         pos = nx.spring_layout(graph, iterations=10000),
#     #         with_labels = True,
#     #     )
#     # plt.show()

# #     return graph


def add_random_nodes(graph:nx.Graph, new_size:int, seed:Optional[int] = None):
    '''
    Given a networkx graph, add random nodes to increase size to new_size

    If # of nodes in graph >= new_size already, do nothing.
    '''
    # If seed provided, reset random number generator with that seed.
    if not (seed is None):
        random.seed(seed)

    def get_next_id(next_id):
        while next_id in graph:
            next_id += 1
        return next_id

    # Ensure that next node id is unique
    next_node_id = get_next_id(len(graph))
    while len(graph) < new_size:
        # Pick a random node
        conn_node = random.choice(list(graph.nodes))
        graph.add_node(next_node_id)
        graph.add_edge(conn_node, next_node_id)
        next_node_id = get_next_id(next_node_id + 1)

# Make dictionary that associates name with generator function

_graph_generators = {
    "well-mixed": gen_graph_well_mixed,
    "toroidal-lattice": gen_graph_toroidal_lattice,
    "comet-kite": gen_graph_comet_kite,
    "linear-chain": gen_graph_linear_chain,
    "star": gen_graph_star,
    "random-erdos-renyi": gen_graph_random_erdos_renyi,
    "random-barabasi-albert": gen_graph_random_barabasi_albert,
    "random-waxman": gen_graph_random_waxman,
    "random-geometric": gen_graph_random_geometric,
    "cycle": gen_graph_cycle,
    "wheel": gen_graph_wheel,
    "windmill": gen_graph_windmill,
    "clique-ring": gen_graph_clique_ring,
    "hierarchical-clique-ring": gen_graph_hierarchical_clique_ring,
    "barbell": gen_graph_barbell,
    #Newly added by Grant
    "random-k-regular": gen_graph_random_k_regular,
    "connected-caveman": gen_graph_connected_caveman,
    "relaxed-caveman": gen_graph_relaxed_caveman,
    #"detour": gen_graph_detour,
    #"regular-island": gen_graph_regular_island,
    "star-like": gen_graph_star_like,
    "probabilistic-star-like": gen_graph_probabilistic_star_like,
    "ring-k-regular": gen_graph_ring_k_regular,
    "circular-ladder-graph": gen_graph_circular_ladder_graph

}

def get_generator_fun(name:str):
    return _graph_generators[name]

# g = gen_graph_hierarchical_clique_ring(
#     layers = 2,
#     clique_size = 5,
#     community_count= 3,
#     nodes_between_communities = 4
# )


# nx.draw(
    #     graph,
    #     pos = nx.spring_layout(graph, iterations=10000),
    #     with_labels = True,
    # )
    # plt.show()






#Detour graph removed since at large scale we predict similar results to complete graph

# if __name__ == "__main__":
#     main()