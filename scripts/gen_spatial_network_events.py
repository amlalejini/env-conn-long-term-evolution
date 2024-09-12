'''
This script generates a sequence event commands that configures a given spatial structure
in avida.

'''
import utilities as utils
import graph_utilities as gutils
import argparse
import os

def GenClearConnectionsCmd(trigger_str:str = "u begin"):
    return f"{trigger_str} DisconnectCellsAll"

def GenDisconnectCmd(pos_1, pos_2, trigger_str:str = "u begin"):
    '''
    Disconnect two positions given as x,y coordinates.
    '''
    return f"{trigger_str} DisconnectCells {pos_1[0]} {pos_1[1]} {pos_2[0]} {pos_2[1]}"

def GenDisconnectAllCmds(positions:list, trigger_str:str = "u begin"):
    # Because avida treats disconnects bidirectionally, don't need to disconnect
    # from both ends of a connection in separate commands.
    return [GenDisconnectCmd(positions[i], positions[k], trigger_str) for i in range(0, len(positions)) for k in range(i, len(positions))]

def GenConnectCmd(pos_1, pos_2, trigger_str:str = "u begin"):
    '''
    Connect the two positions, each given as x,y coordinates
    '''
    return f"{trigger_str} ConnectCells {pos_1[0]} {pos_1[1]} {pos_2[0]} {pos_2[1]}"

def GenConnectCmds(connections, trigger_str:str = "u begin"):
    return [GenConnectCmd( conn[0], conn[1] ) for conn in connections]

def GenSpatialNetworkEventsStr(
    world_x:int,
    world_y:int,
    graph_format:str,
    graph_file:str,
    directed_graph:bool
):
    # Build list of all possible positions given world_x and world_y
    all_positions = [(x, y) for x in range(world_x) for y in range(world_y)]

    # Generate commands to disconnect all grid cells
    #GenDisconnectAllCmds(all_positions, "u begin")
    disconnect_all_cmds = GenClearConnectionsCmd("u begin")

    in_graph = None
    if graph_format == "edges":
        in_graph = gutils.read_graph_edges_csv(
            graph_file,
            directed = directed_graph
        )
    elif graph_format == "matrix":
        in_graph = gutils.read_graph_matrix(
            graph_file,
            directed = directed_graph
        )
    else:
        print("Invalid graph format choice.")
        exit(-1)

    # Make sure avida grid is large enough to accomodate graph size
    # Exit if it won't work. Warn if there's a mismatch.
    node_ids = list(in_graph.nodes)
    if len(node_ids) > len(all_positions):
        print("Avida world size too small to accomodate size of graph.")
        print(f"  Avida environment size: {len(all_positions)}")
        print(f"  # nodes in graph: {len(node_ids)}")
        exit(-1)
    elif len(node_ids) != len(all_positions):
        print("WARNING: Avida environment is larger than input graph.")
        print("  Continuing conversion, but some locations in Avida will not be used")

    # Map node ids from input graph to x,y locations in the avida grid
    # (create mappings for both directions for convenience)
    node_ids.sort() # Sort to make mappings consistent from run-to-run
    node_to_xy = {node_ids[i]:all_positions[i] for i in range(len(node_ids))}
    xy_to_node = {node_to_xy[node_id]:node_id for node_id in node_to_xy}
    # print(node_to_xy)

    # When avida adds a connection, it adds the connection from->to and to->from without checking if this is a duplicate addition
    # So, we need to make sure avida doesn't add duplicates! (thus, using a set here)
    connections = set()
    conn_sets = set()
    # For every edge in the input graph, add a connection
    # print("edges: ", in_graph.edges)
    for edge in in_graph.edges:
        # Add connection to connection set
        frm_xy = node_to_xy[edge[0]]
        to_xy = node_to_xy[edge[1]]
        # Check if we've seen this edge (in either direction) already
        conn_set = frozenset([frm_xy, to_xy])
        if conn_set in conn_sets:
            continue
        # If we haven't, add to sets
        conn_sets.add( conn_set )
        connections.add( (frm_xy, to_xy) )
        # If undirected graph, make sure we also connect the reverse
        # NOTE: Avida is *undirected*, so don't add duplicate edges.
        # if not args.directed_graph:
        #     connections.add( (to_xy, frm_xy) )

    connection_cmds = GenConnectCmds(connections, "u begin")

    # Build command sequence string
    event_cmds = "\n".join(
        ["# -- Disconnect all locations --"] + disconnect_all_cmds + ["# -- Reconnect locations to impose spatial structure -- "] + connection_cmds
    )

    return event_cmds

def main():
    parser = argparse.ArgumentParser(
        usage = "Generates sequence of avida events that configures a spatial given spatial structure"
    )
    # parser.add_argument("--graph_dir", type = str, default = "./", help = "Directory with graphs to load and process.")
    parser.add_argument("--dump_dir", type = str, default = "./", help = "Where to write output files?")
    parser.add_argument("-x", "--world_x", type = int, default = 10, help = "Avida world size (in the x dimension)")
    parser.add_argument("-y", "--world_y", type = int, default = 10, help = "Avida world size (in the y dimension)")
    parser.add_argument("--graph_format", type = str, choices=["matrix", "edges"], default = "matrix", help = "Format of input graph")
    parser.add_argument("--graph_file", type = str, help = "Graph file to convert into an avida event command sequence")
    parser.add_argument("--directed_graph", type = bool, default = False, help = "Read input graph as directed or undirected? WARNING: Avida is undirected!")
    parser.add_argument("-o", "--out_name", type = str, default = "event_cmds.dat", help = "File name to dump event commands into")

    args = parser.parse_args()

    # Create output directory if it doesn't already exist
    utils.mkdir_p(args.dump_dir)

    event_cmds = GenSpatialNetworkEventsStr(
        world_x = args.world_x,
        world_y = args.world_y,
        graph_format = args.graph_format,
        graph_file = args.graph_file,
        directed_graph = args.directed_graph
    )

    with open(os.path.join(args.dump_dir, args.out_name), "w") as fp:
        fp.write(event_cmds)

if __name__ == "__main__":
    main()




