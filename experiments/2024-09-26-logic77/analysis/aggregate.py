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

# -- TODO: make this into a .json configuration file? --
# Run configuration fields to keep as fields in summary output file.
run_cfg_fields_summary = {
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
}

run_cfg_fields_time_series = {
    "graph_type",
    "seed"
}

# Fields to pull from phylodiversity.csv file
phylodiversity_fields_summary = {
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

phylodiversity_fields_time_series = {
    "current_phylogenetic_diversity",
    "diversity",
}

# Fields to pull from oee.csv
oee_fields_summary = {
    "change",
    "novelty",
    "ecology",
    "complexity"
}

# Fields to pull from dominant.csv
dominant_fields_summary = {
    "dominant_lineage_length",
    "dominant_deleterious_steps",
    "dominant_phenotypic_volatility",
    "dominant_unique_phenotypes"
}

time_fields_summary = {
    "average_generation"
}

time_fields_time_series = {
    "average_generation"
}

count_fields_summary = {
    "number_of_organisms"

}

count_fields_time_series = {
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

def add_time_series_info(
    time_series_data,
    run_data,
    fields,
    prefix = None
):
    # For each relevant line in run data, add relevant fields to time_series_data
    for line in run_data:
        # Skip over updates we don't want to sample
        line_update = int(line["update"])
        if not line_update in time_series_data:
            continue
        for field in line:
            if field in fields:
                if prefix is None:
                    time_series_data[line_update][field] = line[field]
                else:
                    time_series_data[line_update][f"{prefix}_{field}"] = line[field]



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
    parser.add_argument("--summary_update", type=int, help="Update to pull summary data for?")
    parser.add_argument("--time_series_units", type=str, default="interval", choices=["interval", "total"], help="Unit for resolution of time series")
    parser.add_argument("--time_series_resolution", type=int, default=1, help="What resolution should we collect time series data at?")

    args = parser.parse_args()
    data_dir = args.data_dir
    dump_dir = args.dump_dir
    target_update = args.summary_update
    time_series_units = args.time_series_units
    time_series_resolution = args.time_series_resolution

    if not os.path.exists(data_dir):
        print("Unable to find data directory.")
        exit(-1)

    # Verify time series resolution >= 1
    if time_series_resolution < 1:
        print("Time series resolution must be >= 1")
        exit(-1)

    utils.mkdir_p(dump_dir)

    # Aggregate run directories.
    run_dirs = [run_dir for run_dir in os.listdir(data_dir) if run_identifier in run_dir]
    print(f"Found {len(run_dirs)} run directories.")

    # Create file to hold time series data
    time_series_content = []    # This will hold all the lines to write out for a single run; written out for each run.
    time_series_header = None   # Holds the time series file header (verified for consistency across runs)
    time_series_fpath = os.path.join(dump_dir, f"time_series.csv")

    with open(time_series_fpath, "w") as fp:
        fp.write("")

    # For each run directory...
    # summary_header = None
    summary_content_lines = []
    for run_dir_i in range(len(run_dirs)):
        run_dir = run_dirs[run_dir_i]
        print(f"...({run_dir_i + 1}/{len(run_dirs)}) aggregating from {run_dir}")
        run_path = os.path.join(data_dir, run_dir)

        run_summary_info = {} # Hold summary information about this run.
        time_series_info = {} # Hold time series information. Indexed by update.

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
            if param in run_cfg_fields_summary:
                run_summary_info[param] = value

        max_pop_size = int(run_params["WORLD_X"]) * int(run_params["WORLD_Y"])

        ########################################
        # Extract data from phylodiversity.csv
        ########################################
        phylodiversity_path = os.path.join(run_path, "data", "phylodiversity.csv")
        phylodiversity_data = utils.read_csv(phylodiversity_path)

        # Search for update nearest
        updates = [int(row["update"]) for row in phylodiversity_data]
        if len(updates) == 0:
            continue

        # did run finish with respect to target update?
        run_finished_target = target_update in updates

        # Extract time series updates (only if run reached target)
        time_series_updates = utils.filter_time_points(
            updates,
            method = time_series_units,
            resolution = time_series_resolution
        ) if run_finished_target else []
        time_series_updates = set(time_series_updates)
        # Add run cfg information to time_series info
        time_series_info = {
            update:{field:run_params[field] for field in run_cfg_fields_time_series}
            for update in time_series_updates
        }
        for update in time_series_updates:
            time_series_info[update]["update"] = update

        # Extract summary info
        run_target_update = nearest(target_update, updates)
        run_summary_info["update"] = run_target_update
        run_summary_info["reached_target_update"] = run_finished_target
        run_summary_info.update(
            extract_summary_data(
                data = phylodiversity_data,
                target_update = run_target_update,
                fields = phylodiversity_fields_summary,
                prefix = "phylodiv"
            )
        )

        # Extract time series info from phylodiversity data
        if run_finished_target:
            add_time_series_info(
                time_series_data = time_series_info,
                run_data = phylodiversity_data,
                fields = phylodiversity_fields_time_series,
                prefix = "phylodiv"
            )

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
                fields = dominant_fields_summary,
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
                fields = time_fields_summary,
                prefix = "time"
            )
        )

        # Extract time series info
        if run_finished_target:
            add_time_series_info(
                time_series_data = time_series_info,
                run_data = time_data,
                fields = time_fields_time_series,
                prefix = "time"
            )

        del time_data

        ########################################
        # Extract data from tasks.dat
        ########################################
        tasks_path = os.path.join(run_path, "data", "tasks.dat")
        tasks_data = utils.read_avida_dat_file(tasks_path)
        pop_thresh = 0.01 * max_pop_size

        tasks_summary_data = extract_summary_data(
            data = tasks_data,
            target_update = run_target_update,
            fields = {field for field in tasks_data[-1] if field != "update"}
        )
        tasks = set(tasks_summary_data.keys())

        for line in tasks_data:
            total_tasks_done = 0
            for task in tasks:
                task_cnt = int(line[task])
                task_exec = task_cnt >= pop_thresh
                line[f"{task}_done"] = int(task_exec)
                total_tasks_done += int(task_exec)
            line["total_tasks_done"] = total_tasks_done

        print("Tasks:",tasks)

        # Calculate task completion separately for summary
        pop_tasks_completed = {
            f"pop_task_{task}":int(float(tasks_summary_data[task]) >= pop_thresh)
            for task in tasks_summary_data
        }
        pop_tasks_total = sum(pop_tasks_completed[task] for task in pop_tasks_completed)
        run_summary_info.update(
            pop_tasks_completed
        )
        run_summary_info["pop_task_total"] = pop_tasks_total

        # Extract time series info
        if run_finished_target:
            add_time_series_info(
                time_series_data = time_series_info,
                run_data = tasks_data,
                fields = {"total_tasks_done", "equals_done"},
                prefix = "pop_task"
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
        dom_tasks_total = 0
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

            # dom_tasks_total = sum([int(run_summary_info[f"dom_detail_{task}"]) for task in tasks])

            del dom_detail_data
        else:
            # run_summary_info.update(
            #     {
            #         f"dom_detail_{task}":"0" for task in tasks
            #     }
            # )
            run_summary_info.update(
                {"dom_detail_gestation_time":"-1", "dom_detail_genome_length":"-1"}
            )

        run_summary_info["dom_task_total"] = dom_tasks_total

        ########################################
        # Add summary info to summary content lines
        summary_content_lines.append(run_summary_info)

        ############################################################
        # Output time series data for this run
        if run_finished_target:
            # Order the updates
            time_series_update_order = list(time_series_updates)
            time_series_update_order.sort()
            # Order the fields
            time_series_fields = list(time_series_info[time_series_update_order[0]].keys())
            time_series_fields.sort()
            # If we haven't written the header, write it.
            write_header = False
            if time_series_header == None:
                write_header = True
                time_series_header = ",".join(time_series_fields)
            elif time_series_header != ",".join(time_series_fields):
                print("Time series header mismatch!")
                exit(-1)

            # Write time series content line-by-line
            time_series_content = []
            for u in time_series_update_order:
                time_series_content.append(",".join([str(time_series_info[u][field]) for field in time_series_fields]))
            with open(time_series_fpath, "a") as fp:
                if write_header:
                    fp.write(time_series_header)
                fp.write("\n")
                fp.write("\n".join(time_series_content))
            time_series_content = []
        ############################################################

    # Write summary info out
    summary_path = os.path.join(dump_dir, "summary.csv")
    utils.write_csv(summary_path, summary_content_lines)











if __name__ == "__main__":
    main()