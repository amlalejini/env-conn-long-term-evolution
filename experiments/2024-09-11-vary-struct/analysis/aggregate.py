'''
Aggregate data.
This script generates the following output files:
- A summary file with one line per-replicate.
'''

import argparse
import os
import sys
import pathlib

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
phylodiversity_fields = {
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
}

# Fields to pull from oee.csv
oee_fields = {
    "change",
    "novelty",
    "ecology",
    "complexity"
}

# Fields to pull from dominant.csv
dominant_fields = {
    "dominant_lineage_length",
    "dominant_deleterious_steps",
    "dominant_phenotypic_volatility",
    "dominant_unique_phenotypes"
}

time_fields = {
    "average_generation"
}

count_fields = {
    "number_of_organisms"

}

def nearest(target:int, updates:list):
    return min(updates, key = lambda x:abs(target - x))

def extract_summary_data(data, target_update, fields, prefix=None):
        info = {}

        # Grab the data line that matches the target update for this run
        summary_data = [
            line
            for line in data
            if (target_update is None) or (int(line["update"]) == target_update)
        ][-1]

        # Add specified fields to run summary data
        for field in summary_data:
            if field in fields:
                if prefix is None:
                    info[field] = summary_data[field]
                else:
                    info[f"{prefix}_{field}"] = summary_data[field]

        return info


def append_csv(output_path, out_lines, field_order):
    lines = []
    for info in out_lines:
        line = ",".join([str(info[field]) for field in field_order])
        lines.append(line)
    out_content = "\n" + "\n".join(lines)
    with open(output_path, "a") as fp:
        fp.write(out_content)

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
    # summary_header = None
    summary_content_lines = []
    for run_dir_i in range(len(run_dirs)):
        run_dir = run_dirs[run_dir_i]
        print(f"...({run_dir_i + 1}/{len(run_dirs)}) aggregating from {run_dir}")
        run_path = os.path.join(data_dir, run_dir)

        run_summary_info = {} # Hold summary information about this run.

        ########################################
        # Extract run parameters
        ########################################
        run_cfg_path = os.path.join(run_path, "data", "run_params.csv")
        run_cfg_data = utils.read_csv(run_cfg_path)
        run_params = {}
        for line in run_cfg_data:
            param = line["param"]
            value = line["value"]
            run_params[param] = value
            # Add a subset of parameters to summary information for this run.
            if param in run_cfg_fields:
                run_summary_info[param] = value

        max_pop_size = int(run_params["WORLD_X"]) * int(run_params["WORLD_Y"])

        ########################################
        # Extract data from phylodiversity.csv
        ########################################
        phylodiversity_path = os.path.join(run_path, "data", "phylodiversity.csv")
        phylodiversity_data = utils.read_csv(phylodiversity_path)

        # Search for update nearest
        updates = [int(row["update"]) for row in phylodiversity_data]
        run_target_update = nearest(target_update, updates)
        run_summary_info["update"] = run_target_update

        run_summary_info.update(
            extract_summary_data(
                data = phylodiversity_data,
                target_update = run_target_update,
                fields = phylodiversity_fields,
                prefix = "phylodiv"
            )
        )

        # NOTE - if we wanted time series data, here's where we'd add.

        # Done with phylodiversity data
        del phylodiversity_data

        ########################################
        # Extract data from oee.csv
        ########################################
        # oee_path = os.path.join(run_path, "data", "oee.csv")
        # oee_data = utils.read_csv(oee_path)

        # run_summary_info.update(
        #     extract_summary_data(
        #         data = oee_data,
        #         target_update = run_target_update,
        #         fields = oee_fields,
        #         prefix = "oee"
        #     )
        # )

        # del oee_data

        ########################################
        # Extract data from dominant.csv
        ########################################
        dominant_path = os.path.join(run_path, "data", "dominant.csv")
        dominant_data = utils.read_csv(dominant_path)

        run_summary_info.update(
            extract_summary_data(
                data = dominant_data,
                target_update = run_target_update,
                fields = dominant_fields,
                prefix = "dominant"
            )
        )

        del dominant_data

        ########################################
        # Extract data from first_task_locs.csv
        ########################################
        first_task_locs_path = os.path.join(run_path, "data", "first_task_locs.csv")
        first_task_locs_data = utils.read_csv(first_task_locs_path)

        first_task_loc_info  = {}
        for line in first_task_locs_data:
            task_name = line["task_name"]
            first_task_loc_info.update({
                f"task_loc_{task_name}_completed": line["completed"],
                f"task_loc_{task_name}_loc_id": line["loc_id"],
                f"task_loc_{task_name}_loc_x": line["loc_x"],
                f"task_loc_{task_name}_loc_y": line["loc_y"]
            })
        run_summary_info.update(first_task_loc_info)

        del first_task_locs_path

        ########################################
        # Extract data from time.dat
        ########################################
        time_path = os.path.join(run_path, "data", "time.dat")
        time_data = utils.read_avida_dat_file(time_path)

        run_summary_info.update(
            extract_summary_data(
                data = time_data,
                target_update = run_target_update,
                fields = time_fields,
                prefix = "time"
            )
        )

        del time_data

        ########################################
        # Extract data from tasks.dat
        ########################################
        tasks_path = os.path.join(run_path, "data", "tasks.dat")
        tasks_data = utils.read_avida_dat_file(tasks_path)
        tasks_summary_data = extract_summary_data(
            data = tasks_data,
            target_update = run_target_update,
            fields = {field for field in tasks_data[-1] if field != "update"}
        )
        tasks = set(tasks_summary_data.keys())
        print("Tasks:",tasks)

        # Determine which tasks are completed by > 1% of the population.
        # Count these tasks as being "covered" by the population.
        # for task in tasks_summary_data:
        #     print(task, tasks_summary_data[task])
        # print(tasks_data)

        pop_thresh = 0.01 * max_pop_size
        pop_tasks_completed = {
            f"pop_task_{task}":int(float(tasks_summary_data[task]) >= pop_thresh)
            for task in tasks_summary_data
        }
        run_summary_info.update(
            pop_tasks_completed
        )

        del tasks_data

        ########################################
        # Extract data from count.dat
        ########################################
        # count_path = os.path.join(run_path, "data", "count.dat")
        # count_data = utils.read_avida_dat_file(count_path)

        # run_summary_info.update(
        #     extract_summary_data(
        #         data = count_data,
        #         target_update = run_target_update,
        #         fields = count_fields,
        #         prefix = "count"
        #     )
        # )

        # del count_data

        ########################################
        # Extract data from detail-dominant.dat
        ########################################
        dom_detail_path = os.path.join(run_path, "data", "detail_dominant.dat")
        dom_detail_fields = {"gestation_time", "genome_length"}
        dom_detail_fields.update(tasks)
        if os.path.exists(dom_detail_path):
            dom_detail_data = utils.read_avida_dat_file(dom_detail_path)

            run_summary_info.update(
                extract_summary_data(
                    data = dom_detail_data,
                    target_update = None,
                    fields = dom_detail_fields,
                    prefix = "dom_detail"
                )
            )

            del dom_detail_data
        else:
            run_summary_info.update(
                {
                    f"dom_detail_{task}":"0" for task in tasks
                }
            )
            run_summary_info.update(
                {"dom_detail_gestation_time":"-1", "dom_detail_genome_length":"-1"}
            )

        ########################################
        # Add summary info to summary content lines
        summary_content_lines.append(run_summary_info)

    # Write summary info out
    summary_path = os.path.join(dump_dir, "summary.csv")
    utils.write_csv(summary_path, summary_content_lines)











if __name__ == "__main__":
    main()