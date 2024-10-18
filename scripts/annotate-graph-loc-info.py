'''
This script takes the following inputs:
- summary.csv (generated with aggregate.py script)
- graph_birth_info.csv (generated with aggregate-graph-loc-info.py script)

and annotates each location in graph_birth_info with extra information:
- expected births (proportion and raw value given total births)
- proportion actual births
- # task appearances
- proportion of task appearances
'''

import argparse
import os
import networkx as nx
import utilities as utils
import graph_utilities as gutils
import graph_generators as ggens
import matplotlib.pyplot as plt
import statistics as stats

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
    parser.add_argument("--graph_birth_data", type=str, help="Summary data file containing graph birth location data.")
    parser.add_argument("--graphs_dir", type=str, help="Path to directory containing relevant graphs")
    parser.add_argument("--dump_dir", type=str, default=".", help="Where to write output files")

    args = parser.parse_args()
    summary_data_path = args.summary_data
    birth_locs_data_path = args.graph_birth_data
    dump_dir = args.dump_dir
    graphs_dir = args.graphs_dir

    if not os.path.isfile(summary_data_path):
        print(f"Failed to find summary data file: {summary_data_path}")
        exit(-1)

    if not os.path.isfile(birth_locs_data_path):
        print(f"Failed to find birth location data file: {birth_locs_data_path}")
        exit(-1)

    utils.mkdir_p(dump_dir)

    # Read summary file
    summary_data = utils.read_csv(summary_data_path)
    # Read graph birth location data
    graph_birth_loc_data = utils.read_csv(birth_locs_data_path)

    # We can key off of seeds in summary / graph birth loc data to cross reference.
    seeds = [line["seed"] for line in summary_data]
    # print(seeds)
    # *Every* line in summary file must have a unique seed.
    if len(seeds) != len(set(seeds)):
        print("Seeds re-used across rows in summary")
        exit(-1)
    # Identify tasks
    # Collect all tasks (use pop tasks fields to identify)
    tasks = [
        field.replace("pop_task_", "")
        for field in summary_data[-1]
        if "pop_task_" in field and field != "pop_task_total"
    ]
    # print(f"tasks: {tasks}")

    # Identify seeds by graph file
    graph_file_seeds = {}

    # For each run (seed), idenfity task appearance locations
    #  {seed: {loc: task_appearances, ...}, ...}
    # NOTE: not all locations will be represented; only those where tasks appeared
    total_task_appearances_by_loc = {seed:{} for seed in seeds}
    for line in summary_data:
        run_seed = line["seed"]

        # Make note that this seed is associated with this graph file
        graph_file = line["graph_file"]
        if graph_file != "none":
            if not graph_file in graph_file_seeds:
                graph_file_seeds[graph_file] = []
            graph_file_seeds[graph_file].append(run_seed)

        for task in tasks:
            tname = task_name(task)
            task_completed = (line[f"task_loc_{tname}_completed"] == "1") and not ((line[f"task_loc_{tname}_loc_id"] == "-1"))
            if not task_completed:
                continue
            task_loc_id = int(line[f"task_loc_{tname}_loc_id"])
            # Is task location in dictionary yet? If not, add it.
            if not task_loc_id in total_task_appearances_by_loc[run_seed]:
                total_task_appearances_by_loc[run_seed][task_loc_id] = 0
            total_task_appearances_by_loc[run_seed][task_loc_id] += 1

    # for seed in total_task_appearances_by_loc:
    #     print(seed, total_task_appearances_by_loc[seed])
    # exit(-1)

    # Map each seed to its graph file
    seed_to_graph_file = {
        seed:graph_file
        for seed in graph_file_seeds[graph_file]
        for graph_file in graph_file_seeds
    }

    # Total task appearances for each run
    total_task_appearances_by_seed = {
        seed:sum(
            [
                total_task_appearances_by_loc[seed][loc]
                for loc in total_task_appearances_by_loc[seed]
            ]
        )
        for seed in total_task_appearances_by_loc
    }
    # print(total_task_appearances_by_loc)
    # print(total_task_appearances_by_seed)
    # Proportion task appearances by location by seed
    prop_task_appearances_by_loc = {seed:{} for seed in seeds}
    for seed in total_task_appearances_by_loc:
        task_apps_by_loc = total_task_appearances_by_loc[seed]
        total_task_apps = total_task_appearances_by_seed[seed]
        for loc in task_apps_by_loc:
            prop_task_appearances_by_loc[seed][loc] = task_apps_by_loc[loc] / total_task_apps if total_task_apps > 0 else 0

    # Total actual births by seed
    total_births_by_seed = {seed:0 for seed in seeds}
    for line in graph_birth_loc_data:
        graph_seed = line["seed"]
        total_births_by_seed[graph_seed] += int(line["births"])

    # Proportion births by location by seed
    prop_births_by_loc = {seed:{} for seed in seeds}
    for line in graph_birth_loc_data:
        graph_seed = line["seed"]
        loc = line["loc_id"]
        loc_births = int(line["births"])
        total_births = total_births_by_seed[graph_seed]
        prop_births_by_loc[graph_seed][loc] = loc_births / total_births

    # Expected births (will need to load graph)
    graph_expected_births_info = {}
    for graph_file in graph_file_seeds:
        # run_seeds = graph_file_seeds[graph_file]
        graph_path = os.path.join(graphs_dir, graph_file)
        if not os.path.isfile(graph_path):
            print(f"Failed to find graph file: {graph_path}")
        # Load graph
        graph = gutils.read_graph_matrix(graph_path)
        # Calculate expected births for this graph
        graph_expected_births_info[graph_file] = gutils.calc_expected_births(graph)

    # Build output (reuse graph data)
    for line in graph_birth_loc_data:
        graph_file = line["graph_file"]
        seed = line["seed"]
        loc_id = line["loc_id"]
        line["expected_births_prop"] = graph_expected_births_info[graph_file][int(loc_id)]["prop_births"]
        line["expected_births_total"] = total_births_by_seed[seed] * line["expected_births_prop"]
        line["births_prop"] = prop_births_by_loc[seed][loc_id]
        line["task_appearances"] = total_task_appearances_by_loc[seed].get(int(loc_id), 0)
        line["task_appearances_prop"] = prop_task_appearances_by_loc[seed].get(int(loc_id), 0)

    # Output
    basename = os.path.basename(birth_locs_data_path).split(".")[0]
    basename = f"{basename}_annotated.csv"
    utils.write_csv(
        output_path = os.path.join(dump_dir, basename),
        rows = graph_birth_loc_data
    )

if __name__ == "__main__":
    main()