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

run_cfg_fields_to_output = {
    "graph_file",
    "graph_type",
    "seed"
}

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

    args = parser.parse_args()
    data_dir = args.data_dir
    dump_dir = args.dump_dir

    if not os.path.exists(data_dir):
        print("Unable to find data directory.")
        exit(-1)

    utils.mkdir_p(dump_dir)

    # Aggregate run directories.
    run_dirs = [run_dir for run_dir in os.listdir(data_dir) if run_identifier in run_dir]
    print(f"Found {len(run_dirs)} run directories.")

    graph_info_header = None
    graph_info_fpath = os.path.join(dump_dir, "graph_birth_info.csv")
    with open(graph_info_fpath, "w") as fp:
        fp.write("")

    for run_dir_i in range(len(run_dirs)):
        run_dir = run_dirs[run_dir_i]
        print(f"...({run_dir_i + 1}/{len(run_dirs)}) aggregating from {run_dir}")
        run_path = os.path.join(data_dir, run_dir)

        run_graph_info_lines = [] # Holds lines for this run's graph info

        ########################################
        # Extract run parameters
        ########################################
        run_cfg_path = os.path.join(run_path, "data", "run_params.csv")
        run_cfg_data = utils.read_csv(run_cfg_path)
        run_params = {}
        output_param_info = {}
        for line in run_cfg_data:
            param = line["param"]
            value = line["value"]
            run_params[param] = value
            if param in run_cfg_fields_to_output:
                output_param_info[param] = value
        max_pop_size = int(run_params["WORLD_X"]) * int(run_params["WORLD_Y"])

        ########################################
        # Extract birth counts
        ########################################
        loc_birth_counts_path = os.path.join(run_path, "data", "loc_birth_counts.csv")
        loc_birth_counts_data = utils.read_csv(loc_birth_counts_path)
        for line in loc_birth_counts_data:
            birth_count = line["births"]
            loc_id = line["loc_id"]
            run_graph_info_lines.append({"births":birth_count, "loc_id":loc_id})
            run_graph_info_lines[-1].update(output_param_info)

        ########################################
        # Write out to file
        ########################################
        fields = list(run_graph_info_lines[-1].keys())
        fields.sort()
        header = ",".join(fields)
        write_header = False
        if graph_info_header is None:
            write_header = True
            graph_info_header = header
        elif graph_info_header != header:
            print("Header mismatch!")
            exit(-1)
        # Write info line-by-line
        output_lines = []
        for row_i in range(len(run_graph_info_lines)):
            row = run_graph_info_lines[row_i]
            output_lines.append(
                ",".join(str(row[field]) for field in fields)
            )
        with open(graph_info_fpath, "a") as fp:
            if write_header:
                fp.write(graph_info_header)
            fp.write("\n")
            fp.write("\n".join(output_lines))
        output_lines = []

if __name__ == "__main__":
    main()