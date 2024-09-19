'''
Aggregate data.
This script generates the following output files:
- A summary file with one line per-replicate.
'''

import argparse
import os
import sys

# Add scripts directory to path, import utilities from scripts directory.
sys.path.append(
    os.path.join(
        pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parents[2],
        "scripts"
    )
)
import utilities as utils

run_identifier = "RUN_"

# Run configuration fields to keep as fields in summary output file.
run_cfg_fields = [
    "WORLD_X",
    "WORLD_Y",
    "COPY_MUT_PROB",
    "DIVIDE_INS_PROB",
    "DIVIDE_DEL_PROB",
    "BIRTH_METHOD",
    "graph_file",
    "graph_type",
    "events_file_name",
    "seed"
]

# Fields to pull from phylodiversity.csv file
phylodiversity_fields = [
    "mean_evolutionary_distinctiveness",
    "min_evolutionary_distinctiveness",
    "max_evolutionary_distinctiveness",
    "variance_evolutionary_distinctiveness",
    "current_phylogenetic_diversity",
    "num_taxa",
    "total_orgs",
    "ave_depth",
    "num_roots",
    "mrca_depth",
    "diversity",
    "mrca_changes"
]

# Fields to pull from oee.csv
oee_fields = [
    "change",
    "novelty",
    "ecology",
    "complexity"
]

# Fields to pull from dominant.csv
dominant_fields = [
    "dominant_lineage_length",
    "dominant_deleterious_steps",
    "dominant_phenotypic_volatility",
    "dominant_unique_phenotypes"
]



def main():
    parser = argparse.ArgumentParser(description = "Run submission script.")
    parser.add_argument("--data_dir", type=str, help="Where is the base output directory for each run?")
    parser.add_argument("--dump_dir", type=str, help="Where to dump this?", default=".")
    parser.add_argument("--update", type=int, help="Update to pull data for?")
    # parser.add_argument("--time_series_range", type=int, help="The range (in updates) to collect time series data?", nargs=2)

    args = parser.parse_args()
    data_dir = args.data_dir
    dump_dir = args.dump_dir
    target_update = args.update

    if not os.path.exists(data_dir):
        print("Unable to find data directory.")
        exit(-1)

    utils.mkdir_p(dump_dir)

    # Aggregate run directories.
    run_dirs = [run_dir for run_dir in os.listdir(data_dir) if run_identifier in run_dir]
    print(f"Found {len(run_dirs)} run directories.")

    # For each run directory...
    summary_header = None
    summary_content_lines = []
    for run_dir_i in range(len(run_dirs)):
        run_dir = run_dirs[run_dir_i]
        print(f"...({run_dir_i + 1}/{len(run_dirs)}) aggregating from {run_dir}")
        run_path = os.path.join(data_dir, run_dir)

        run_summary_info = {} # Hold summary information about this run.

        ########################################
        # Extract run parameters
        ########################################
        run_cfg_path = os.path.join(run_path, "run_params.csv")
        run_cfg_data = utils.read_csv(run_cfg_path)
        run_params = {}
        for line in run_cfg_data:
            param = line["parameter"]
            value = line["value"]
            run_params[param] = value
            # Add a subset of parameters to summary information for this run.
            if param in run_cfg_fields:
                run_summary_info[param] = value

        # TODO:
        # - phylodiversity.csv
        # - oee.csv
        # - dominant.csv
        # - data/first_task_locs.csv
        # - data/time.dat (average generation)








if __name__ == "__main__":
    main()