'''
This script takes a summary file + graph file directory and outputs data needed
to screen for hotspots.
'''
import argparse
import os
import networkx as nx
import utilities as utils
import graph_utilities as gutils
import graph_generators as ggens
import matplotlib.pyplot as plt


# TODO - handle well-mixed and toroidal lattice separately
exclude_graphs = {
    "clique-ring_",
    "comet-kite_",
    "well-mixed"
}


def task_name(in_name):
    '''
    Annoyingly, task names are inconsistent because of avida oddities
    '''
    mapping = {"andnot": "andn", "ornot": "orn", "equals":"equ"}
    if in_name in mapping:
        return mapping[in_name]
    elif "logic_" in in_name:
        parts = in_name.split("_")
        parts[-1] = parts[-1].upper()
        return "_".join(parts)
    else:
        return in_name


def main():
    parser = argparse.ArgumentParser(description="Screen for hotspots")
    parser.add_argument("--summary_data", type=str, help="Summary data file that contains task appearance data.")
    parser.add_argument("--graphs_dir", type=str, help="Path to directory containing relevant graphs")
    parser.add_argument("--dump_dir", type=str, default=".", help="Where to write output files")
    # parser.add_argument("--")

    args = parser.parse_args()
    summary_data_path = args.summary_data
    graphs_dir = args.graphs_dir
    dump_dir = args.dump_dir

    if not os.path.isfile(summary_data_path):
        print(f"Failed to find summary data file: {summary_data_path}")
        exit(-1)

    if not os.path.isdir(graphs_dir):
        print(f"Failed to find graphs directory: {graphs_dir}")
        exit(-1)

    utils.mkdir_p(dump_dir)

    # Read over summary file
    summary_data = utils.read_csv(summary_data_path)
    # NOTE - assumes all runs in summary have same world size
    world_x = int(summary_data[-1]["WORLD_X"])
    world_y = int(summary_data[-1]["WORLD_Y"])
    world_size = world_x * world_y

    # Collect all tasks
    tasks = [
        field.replace("pop_task_", "")
        for field in summary_data[-1]
        if "pop_task_" in field and field != "pop_task_total"
    ]
    print(tasks)

    ############################################################################
    # Load summary data, extract task first appearance locations
    ############################################################################
    # Organize data by graph file / graph type
    data_by_graph = {}
    for line in summary_data:
        if any(g in line["graph_file"] for g in exclude_graphs) or line["graph_file"] != "linear-chain.mat":
            continue
        graph = line["graph_file"] if line["graph_file"] != "none" else line["graph_type"]
        if not graph in data_by_graph:
            data_by_graph[graph] = []
        data_by_graph[graph].append(line)

    graph_files = list(data_by_graph.keys())
    graph_files.sort()

    # Distributions of task locations by task
    graph_task_loc_info = {
        graph: { task:[] for task in tasks }
        for graph in graph_files
    }

    graph_tasks_agg_loc_info = {
        graph: []
        for graph in graph_files
    }

    graph_tasks_appearances = {
        graph: { task: 0 for task in tasks }
        for graph in graph_files
    }

    graph_total_tasks = {
        graph: 0
        for graph in graph_files
    }

    # For each graph, get all first location appearances
    for graph in graph_task_loc_info:
        for line in data_by_graph[graph]:
            for task in tasks:
                tname = task_name(task)
                task_completed = (line[f"task_loc_{tname}_completed"] == "1") and not ((line[f"task_loc_{tname}_loc_id"] == "-1"))
                if not task_completed:
                    continue
                # task_loc_x = line[f"task_loc_{task}_loc_x"]
                # task_loc_y = line[f"task_loc_{task}_loc_y"]
                task_loc_id = int(line[f"task_loc_{tname}_loc_id"])
                graph_tasks_agg_loc_info[graph].append(task_loc_id)
                graph_task_loc_info[graph][task].append(task_loc_id)
                graph_tasks_appearances[graph][task] += 1
                graph_total_tasks[graph] += 1


    ############################################################################
    # Add task appearances by location
    ############################################################################
    location_info = {}
    for graph in graph_task_loc_info:
        location_info[graph] = {}
        # Add per-task appearances to location information
        for task in tasks:
            task_locs = graph_task_loc_info[graph][task]
            for loc in task_locs:
                if not loc in location_info[graph]:
                    location_info[graph][loc] = {task:{"count":0,"prop":0} for task in tasks}
                    location_info[graph][loc]["all"] = {"count":0, "prop":0}
                location_info[graph][loc][task]["count"] += 1
                location_info[graph][loc]["all"]["count"] += 1

        # Calculate proportions (per task and aggregated)
        for loc in location_info[graph]:
            for task in tasks:
                if graph_tasks_appearances[graph][task] > 0:
                    location_info[graph][loc][task]["prop"] = location_info[graph][loc][task]["count"] / graph_tasks_appearances[graph][task]
            if graph_total_tasks[graph] > 0:
                location_info[graph][loc]["all"]["prop"] = location_info[graph][loc]["all"]["count"] / graph_total_tasks[graph]

    # for loc in location_info["linear-chain.mat"]:
    #     print(loc, ":", location_info["linear-chain.mat"][loc]["all"])

    ############################################################################
    # Load each graph, output properties
    ############################################################################
    graph_expected_births_info = {}
    for graph_file in graph_files:
        if graph_file == "well-mixed": continue
        graph_path = os.path.join(graphs_dir, graph_file)
        # Load graph
        # - If well-mixed or torroidal lattice generate directly
        graph = None
        if graph_file in ["toroidal-lattice", "torroidal-lattice"]:
            graph = ggens.gen_graph_toroidal_lattice(world_x, world_y)
        else:
            graph = gutils.read_graph_matrix(graph_path)

        graph_expected_births_info[graph_file] = gutils.calc_expected_births(graph)
        # TODO - load graph birth locations

        # Add attributes to graph nodes
        for loc in graph.nodes():
            expected_births = graph_expected_births_info[graph_file][loc]["prop_births"]
            all_task_prop = location_info[graph_file][loc]["all"]["prop"] if loc in location_info[graph_file] else 0
            all_vs_expected = all_task_prop - expected_births
            graph.nodes[loc]["expected_births"] = expected_births
            graph.nodes[loc]["all_task_prop"] = all_task_prop
            graph.nodes[loc]["all_vs_expected"] = all_vs_expected

        # if graph_file == "linear-chain.mat":
        #     ginfo = dict(graph.nodes(data=True))
        #     for loc in ginfo:
        #         print(loc, ginfo[loc])

        # Draw graph
        # nx.draw(
        #     graph,
        #     pos = nx.planar_layout(graph)
        #     # pos = nx.spring_layout(graph, iterations=100)
        #     # with_labels = True,
        #     # labels = [color_map[node] if node in color_map else num_clique_rings+1 for node in list(graph.nodes())],
        # )
        # plt.show()

    # print(graph_expected_births_info)







if __name__ == "__main__":
    main()