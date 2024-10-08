import networkx as nx
import utilities as utils

def read_graph_matrix(file_path:str, directed=False):
    '''
    Read graph saved in matrix format
    '''
    content = None
    with open(file_path, "r") as fp:
        content = fp.read().strip().split("\n")
    matrix = [list(map(int, line.strip().split(","))) for line in content]
    is_square = all([len(row) == len(matrix) for row in matrix])
    if not is_square:
        print("Matrix not square.")
        raise RuntimeError
    graph = nx.Graph() if not directed else nx.DiGraph()
    # Add nodes
    graph.add_nodes_from([i for i in range(len(matrix))])
    # Add edges between nodes
    for row_i in range(len(matrix)):
        row = matrix[row_i]
        for col_i in range(len(row)):
            if row[col_i] > 0:
                graph.add_edge(row_i, col_i)
    return graph

def read_graph_edges_csv(file_path:str, directed=False):
    '''
    Read a graph saved in csv (edges) format
    '''
    # Read edges from csv
    content = utils.read_csv(file_path)
    # Construct empty graph
    graph = nx.Graph() if not directed else nx.DiGraph()
    # Identify all vertices in edge file
    nodes = {line["from"] for line in content if line["from"].lower() != "none"}
    nodes.update({line["to"] for line in content if line["to"].lower() != "none"})
    graph.add_nodes_from(nodes)
    # Add each e
    for edge in content:
        frm = edge["from"]
        to = edge["to"]
        if (frm.lower() == "none") or (to.lower() == "none"):
            continue
        graph.add_edge(frm, to)
    return graph



def write_undirected_graph_to_edges_csv(fname:str, graph:nx.Graph):
    file_content = "" # Will contain output to write to file
    lines = []        # Will be a list of csv rows to write to file

    # We need to track which nodes are represented in the edge list.
    # It is possible that there are nodes with no connections that we'll
    # need to add to the end of the file.
    nodes_represented = set()

    # Loop over edges in graph, creating the line that will be added to the file
    for edge in graph.edges:
        from_node = edge[0]
        to_node = edge[1]
        # Add from --> to
        lines.append(f"{from_node},{to_node}")
        # Add to --> from (because this is an undirected graph;
        #  if this were a directed graph, would not want this line of code)
        lines.append(f"{to_node},{from_node}")
        # Make note of which nodes we've encountered
        nodes_represented.add(from_node)
        nodes_represented.add(to_node)

    # Any nodes not encountered by looping over edges (i.e., nodes that have no edges),
    # we need to add as lines to the file indicating that it is a part of the graph
    for node in graph.nodes:
        if not node in nodes_represented:
            lines.append(f"{node},NONE")

    # Combine lines with header information to create file content
    header = "from,to"
    file_content += header + "\n"
    file_content += "\n".join(lines)
    # Write file content to file
    with open(fname, "w") as fp:
        fp.write(file_content)

# Write networkx graph out as adjacency matrix
def write_undirected_graph_to_matrix(fname:str, graph:nx.Graph):
    file_content = "" # Will contain output to write to file
    lines = []        # Will be a list of csv rows to write to file

    graph_nodes = sorted(graph.nodes)
    for frm in graph_nodes:
        row = []
        for to in graph_nodes:
            row.append(str(int(graph.has_edge(frm, to))))
        lines.append(",".join(row))

    file_content += "\n".join(lines)
    # Write file content to file
    with open(fname, "w") as fp:
        fp.write(file_content)

def calc_expected_births(graph:nx.Graph, self_replace=True):
    expected_births = {node:{"expected_births":0, "prop_births":0} for node in graph.nodes}
    for node in graph.nodes:
        for neighbor in graph.neighbors(node):
            expected_births[node]["expected_births"] += (1 / graph.degree[neighbor])
        if self_replace:
            expected_births[node]["expected_births"] += (1 / graph.degree[node])

    total = sum(expected_births[node]["expected_births"] for node in expected_births)
    for node in expected_births:
        expected_births[node]["prop_births"] = expected_births[node]["expected_births"] / total

    return expected_births


# import graph_generators as ggen
# g = ggen.gen_graph_linear_chain(100)
# e = calc_expected_births(g)
# print(e)