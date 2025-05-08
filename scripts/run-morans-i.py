import argparse
import os
import networkx as nx
import utilities as utils
import graph_utilities as gutils
import statistics as stats
import copy
import sys
import pathlib
# Add scripts directory to path, import utilities from scripts directory.
sys.path.append(
    os.path.join(
        pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parents[0],
        "third-party",
        "network_correlation"
    )
)
import stats as gstats



# import stats

# (1) Load annotated birth info
# (2) Organize by run (seed)
# (3) For each run:
#     - Load graph
#     - Annotate graph with attribute of interest
#     - Compute statistic on graph

def main():
    parser = argparse.ArgumentParser(description="Screen for hotspots")
    parser.add_argument("--graph_loc_data", type=str, help="Summary data file containing graph data by location.")
    parser.add_argument("--graphs_dir", type=str, help="Path to directory containing relevant graphs")
    parser.add_argument("--dump_dir", type=str, default=".", help="Where to write output files")

    args = parser.parse_args()
    graph_loc_data_path = args.graph_loc_data
    graphs_dir = args.graphs_dir
    dump_dir = args.dump_dir

    if not os.path.isfile(graph_loc_data_path):
        print(f"Failed to find data file: {graph_loc_data_path}")
        exit(-1)

    if not os.path.isdir(graphs_dir):
        print(f"Failed to find graphs directory: {graphs_dir}")
        exit(-1)

    utils.mkdir_p(dump_dir)

    print("Running Moran's i on graphs")

    # Load graph_loc data
    graph_loc_data = utils.read_csv(graph_loc_data_path)
    graph_files = list({line["graph_file"] for line in graph_loc_data})
    graphs = {}
    for graph_file in graph_files:
        graph_file_path = os.path.join(graphs_dir, graph_file)
        graphs[graph_file] = gutils.read_graph_matrix(graph_file_path)

    # Organize data by run
    data_by_run = {}
    graph_files_by_run = {}
    for line in graph_loc_data:
        run_seed = line["seed"]
        if not run_seed in data_by_run:
            graph_files_by_run[run_seed] = line["graph_file"]
            data_by_run[run_seed] = []
        data_by_run[run_seed].append(line)

    # For each run, annotate a graph
    graphs_by_run = {}
    output_content = []
    cnt = 0
    for run_id in data_by_run:
        print(f"Processing run {cnt+1}/{len(data_by_run)}")
        info = {}
        graph_file = graph_files_by_run[run_id]
        # Start by making a copy of this type of graph
        graphs_by_run[run_id] = copy.deepcopy(graphs[graph_file])
        # Next, annotate using graph data
        run_data = data_by_run[run_id]
        for line in run_data:
            loc_id = int(line["loc_id"])
            births = line["births"]
            task_apps = line["task_appearances"]
            if not loc_id in graphs_by_run[run_id].nodes:
                print(f"Failed to find loc {loc_id} in {graph_file} for run {run_id}")
                continue
            graphs_by_run[run_id].nodes[loc_id]["births"] = int(births)
            graphs_by_run[run_id].nodes[loc_id]["task_apps"] = int(task_apps)
        # Graph is annotated, so we can run statistics.
        task_result = gstats.moran(
            graphs_by_run[run_id],
            name = "task_apps",
            alt = "greater",
            Np = 100,
            drop_weights=False
        )
        birth_result = gstats.moran(
            graphs_by_run[run_id],
            name = "births",
            alt = "greater",
            Np = 100,
            drop_weights=False
        )
        # null: data, return_dists:True, drop_weights=True
        # Np: number of permutations
        # return format: I, p-value, distances

        # local_task_result = stats.local_moran(
        #     graphs_by_run[run_id],
        #     name = "task_apps",
        #     alt = "greater",
        #     Np = 100,
        #     drop_weights=False
        # )

        task_moran_i = task_result[0]
        task_p_val = task_result[1]
        birth_moran_i = birth_result[0]
        birth_p_val = birth_result[1]
        print(f"  Run: {run_id} ({graph_file})")
        print(f"    Task Moran's I: {task_moran_i}, p-val: {task_p_val}")
        print(f"    Birth Moran's I: {birth_moran_i}, p-val: {birth_p_val}")
        info["seed"] = run_id
        info["graph_file"] = graph_file
        info["task_morans_i"] = task_moran_i
        info["task_p_val"] = task_p_val
        info["birth_morans_i"] = birth_moran_i
        info["birth_p_val"] = birth_p_val

        output_content.append(info)
        cnt += 1

    utils.write_csv(os.path.join(dump_dir, "morans_i.csv"), output_content)


if __name__ == "__main__":
    main()