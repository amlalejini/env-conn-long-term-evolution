'''
Generate slurm job submission scripts - one per condition
'''

import argparse
import os
import sys
import pathlib
from pyvarco import CombinationCollector

# Add scripts directory to path, import utilities from scripts directory.
sys.path.append(
    os.path.join(
        pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parents[2],
        "scripts"
    )
)
import utilities as utils
from gen_spatial_network_events import GenSpatialNetworkEventsStr

# Default configuration values
default_seed_offset = 1000
default_account = None
default_num_replicates = 30
default_job_time_request = "48:00:00"
default_job_mem_request = "4G"
default_job_name = "avda"

executable = "avida"

base_slurm_script_fpath = "./base_slurm_script.txt"
base_events_fpath = "./base_events.txt"
base_analyze_fpath = "./base_analyze.txt"

birth_method_modes = {
    "random-neighborhood": "0",
    "well-mixed": "4"
}

# Create combos
combos = CombinationCollector()

# Special parameters are used to generate the SLURM script but not
# used directly as Avida configuration settings
fixed_params_dynamic = {
    # "updates": "100000",
    "updates": "1000",
    "print_data_resolution": "100"
}

fixed_params_direct = {
    "WORLD_X": "60",
    "WORLD_Y": "60",
    "PHYLOGENY_SNAPSHOT_RES": fixed_params_dynamic["print_data_resolution"],
    "SYSTEMATICS_RES": "100",
    "FORCE_MRCA_COMP": "1",
    "COPY_MUT_PROB": "0.0025",
    "DIVIDE_INS_PROB": "0.05",
    "DIVIDE_DEL_PROB": "0.05",
    "FILTER_TIME": "10000",
    "OEE_RES": "1000",
    "TRACK_INDIVIDUALS": "0"
}


special_decorators = [
    "__COPY_OVER",
    "__DYNAMIC"
]

combos.register_var("spatial_structure__DYNAMIC")
# 'well-mixed' and 'torroidal-lattice' are handled as special cases
#  - all others must exist in spatial-structs directory
combos.add_val(
    "spatial_structure__DYNAMIC",
    [
        "well-mixed",
        "torroidal-lattice",
        "star",
        "random-waxman",
        "comet-kite",
        "linear-chain",
        "clique-ring",
        "hierarchical-clique-ring"
    ]
)

'''


TODO:
- analyze.cfg
'''

def main():
    parser = argparse.ArgumentParser(description="Generate SLURM submission scripts.")
    parser.add_argument("--data_dir", type=str, help="Where is the output directory for phase one of each run?")
    parser.add_argument("--config_dir", type=str, help="Where is the configuration directory for experiment?")
    parser.add_argument("--spatial_structs_dir", type=str, help="Which directory contains spatial structures to be used?")
    parser.add_argument("--events_dir", type=str, help="Which directory to dump events files in?")
    parser.add_argument("--param_snapshot_dir", type=str, help="Which directory to dump parameter snapshots?")
    # parser.add_argument("--avida_loc_mapping_dir", type=str, help="Where to dump avida location mapping files?")
    parser.add_argument("--repo_dir", type=str, help="Where is the repository for this experiment?")
    parser.add_argument("--job_dir", type=str, default=None, help="Where to output these job files? If none, put in 'jobs' directory inside of the data_dir")
    parser.add_argument("--replicates", type=int, default=default_num_replicates, help="How many replicates should we run of each condition?")
    parser.add_argument("--seed_offset", type=int, default=default_seed_offset, help="Value to offset random number seeds by")
    parser.add_argument("--hpc_account", type=str, default=default_account, help="Value to use for the slurm ACCOUNT")
    parser.add_argument("--time_request", type=str, default=default_job_time_request, help="How long to request for each job on hpc?")
    parser.add_argument("--mem", type=str, default=default_job_mem_request, help="How much memory to request for each job?")
    parser.add_argument("--runs_per_subdir", type=int, default=-1, help="How many replicates to clump into job subdirectories")

    args = parser.parse_args()

    # Load in the base slurm file
    base_slurm_script = ""
    with open(base_slurm_script_fpath, "r") as fp:
        base_slurm_script = fp.read()

    # Get list of all combinations to run
    combo_list = combos.get_combos()

    # Calculate how many total jobs we have, and what the last id will be
    num_jobs = args.replicates * len(combo_list)

    # Echo chosen options
    print(f'Generating {num_jobs} across {len(combo_list)} files!')
    print(f' - Data directory: {args.data_dir}')
    print(f' - Config directory: {args.config_dir}')
    print(f' - Spatial structs directory: {args.spatial_structs_dir}')
    print(f' - Repository directory: {args.repo_dir}')
    print(f' - Job directory: {args.job_dir}')
    print(f' - Replicates: {args.replicates}')
    print(f' - Account: {args.hpc_account}')
    print(f' - Time Request: {args.time_request}')
    print(f' - Memory: {args.mem}')
    print(f' - Seed offset: {args.seed_offset}')

    # If no job_dir provided, default to data_dir/jobs
    if args.job_dir == None:
        args.job_dir = os.path.join(args.data_dir, "jobs")

    # Create a job file for each condition
    cur_job_id = 0
    cond_i = 0
    cur_subdir_run_cnt = 0
    cur_run_subdir_id = 0

    # Localize some commandline args for convenience ( less typing :) )
    config_dir = args.config_dir
    repo_dir = args.repo_dir
    data_dir = args.data_dir
    spatial_structs_dir = args.spatial_structs_dir
    events_dir = args.events_dir
    param_snapshot_dir = args.param_snapshot_dir
    job_dir = args.job_dir
    # avida_loc_mapping_dir = args.avida_loc_mapping_dir

    # Create events file directory if doesn't already exist
    utils.mkdir_p(events_dir)
    utils.mkdir_p(param_snapshot_dir)
    # utils.mkdir_p(avida_loc_mapping_dir)

    # Identify relevant/available spatial structure files
    spatial_structs = combos.get_vals("spatial_structure__DYNAMIC")
    # Only allow .mat files.
    # IMPORTANT: If multiple graph files for a single condition, they must:
    #  - each end with _ID.mat where ID is a value [0:number of replicates)
    #  - all be in matrix format
    struct_files = {
        spatial_struct:[
            filename
            for filename in os.listdir(spatial_structs_dir)
            if filename.startswith(spatial_struct) and (".mat" in filename)
        ]
        for spatial_struct in spatial_structs
    }
    # Sort any lists of file names on _<number>
    for spatial_struct in struct_files:
        if len(struct_files[spatial_struct]) > 1:
            struct_files[spatial_struct].sort(key = lambda x : int(x.split(".")[0].split("_")[-1]))
            # If more files than replicates, use only first N files
            if args.replicates < len(struct_files[spatial_struct]):
                struct_files[spatial_struct] = struct_files[spatial_struct][:args.replicates]
            elif args.replicates > len(struct_files[spatial_struct]):
                print(f"Too few spatial structure files for requested number of replicates for {spatial_struct}")
                exit(-1)

    # -- Generate analyze.cfg script --
    # Load in the base slurm file
    base_analyze_script = ""
    with open(base_analyze_fpath, "r") as fp:
        base_analyze_script = fp.read()
    # Update updates to match number of updates for this experiment
    base_analyze_script = base_analyze_script.replace("<<NUM_UPDATES>>", str(fixed_params_dynamic["updates"]))
    # Output new analyze file
    with open(os.path.join(config_dir, "analyze.cfg"), "w") as fp:
        fp.write(base_analyze_script)

    # -- Generate slurm script + event files, etc for each condition --
    for condition_info in combo_list:
        print(condition_info)
        # Calc current seed.
        cur_seed = args.seed_offset + (cur_job_id * args.replicates)
        filename_prefix = f'RUN_C{cond_i}'

        file_str = base_slurm_script
        file_str = file_str.replace("<<TIME_REQUEST>>", args.time_request)
        file_str = file_str.replace("<<ARRAY_ID_RANGE>>", f"1-{args.replicates}")
        file_str = file_str.replace("<<MEMORY_REQUEST>>", args.mem)
        file_str = file_str.replace("<<JOB_NAME>>", f"C{cond_i}")
        file_str = file_str.replace("<<CONFIG_DIR>>", config_dir)
        file_str = file_str.replace("<<REPO_DIR>>", repo_dir)
        file_str = file_str.replace("<<EVENTS_DIR>>", events_dir)
        file_str = file_str.replace("<<SPATIAL_STRUCT_DIR>>", spatial_structs_dir)
        file_str = file_str.replace("<<PARAM_SNAPSHOT_DIR>>", param_snapshot_dir)
        file_str = file_str.replace("<<EXEC>>", executable)
        file_str = file_str.replace("<<JOB_SEED_OFFSET>>", str(cur_seed))
        if args.hpc_account == None:
            file_str = file_str.replace("<<ACCOUNT_INFO>>", "")
        else:
            file_str = file_str.replace("<<ACCOUNT_INFO>>", f"#SBATCH --account {args.hpc_account}")

        # Configure run directory
        run_dir = os.path.join(data_dir, f"{filename_prefix}_"+"${SEED}")
        file_str = file_str.replace("<<RUN_DIR>>", run_dir)

        # Add fixed direct params to cmd line arguments
        cmd_line_params = {param:fixed_params_direct[param] for param in fixed_params_direct}

        # -- Generate events file --
        #   cfgs to replace:
        #   - DATA_PRINT_INTERVAL
        #   - CFG_SPATIAL_STRUCT_CMDS
        #   - SAVE_POP_RESOLUTION
        #   - NUM_UPDATES
        base_events_content = ""
        with open(base_events_fpath, "r") as fp:
            base_events_content = fp.read()
        base_events_content = base_events_content.replace(
            "<<DATA_PRINT_INTERVAL>>",
            fixed_params_dynamic["print_data_resolution"]
        )
        base_events_content = base_events_content.replace(
            "<<SAVE_POP_RESOLUTION>>",
            fixed_params_dynamic["updates"]
        )
        base_events_content = base_events_content.replace(
            "<<NUM_UPDATES>>",
            fixed_params_dynamic["updates"]
        )
        # Build events commands
        cond_spatial_struct = condition_info["spatial_structure__DYNAMIC"]
        # Configure birth method based on chosen spatial structure
        if cond_spatial_struct == "well-mixed":
            cmd_line_params["BIRTH_METHOD"] = birth_method_modes["well-mixed"]
        else:
            cmd_line_params["BIRTH_METHOD"] = birth_method_modes["random-neighborhood"]

        cond_struct_files = struct_files[cond_spatial_struct]
        multiple_graphs_for_cond = False
        if (cond_spatial_struct in {"well-mixed", "torroidal-lattice"}):
            cmd_line_params["EVENT_FILE"] = f"events_{cond_spatial_struct}.cfg"
        elif len(cond_struct_files) <= 1:
            cmd_line_params["EVENT_FILE"] = f"events_{cond_spatial_struct}.cfg"
        else:
            cmd_line_params["EVENT_FILE"] = f"events_{cond_spatial_struct}_" + "${RUN_ID}.cfg"
            multiple_graphs_for_cond = True

        world_x = int(cmd_line_params["WORLD_X"])
        world_y = int(cmd_line_params["WORLD_Y"])
        seed_to_source_graph = {}

        event_file_name = "unknown"
        rep_events_str = ""
        graph_file_name = ""
        if (cond_spatial_struct in {"well-mixed", "torroidal-lattice"}):
            # Relying on base avida functionality to implement spatial structure
            # No spatial structure configuration events necessary.
            event_file_name = cmd_line_params["EVENT_FILE"]
            rep_events_str = base_events_content.replace("<<CFG_SPATIAL_STRUCT_CMDS>>", "")
            with open(os.path.join(events_dir, event_file_name), "w") as fp:
                fp.write(rep_events_str)
        elif not multiple_graphs_for_cond:
            # Need to setup ReconfigureCellConnectivity command, and
            # all replicates share the same event file.
            graph_file_name = cond_struct_files[-1]
            event_file_name = cmd_line_params["EVENT_FILE"]
            rep_events_str = base_events_content.replace(
                "<<CFG_SPATIAL_STRUCT_CMDS>>",
                f"u begin ReconfigureCellConnectivity {graph_file_name}"
            )
            with open(os.path.join(events_dir, event_file_name), "w") as fp:
                fp.write(rep_events_str)
        else:
            # Need to setup ReconfigureCellConnectivity command, and all replicates
            # have a unique event file.
            graph_name_prefix = "_".join(cond_struct_files[-1].split("_")[:-1])
            for i in range(len(cond_struct_files)):
                run_id = i
                run_seed = cur_seed + i
                event_file_name = cmd_line_params["EVENT_FILE"].replace("${RUN_ID}", str(run_id))
                # Check that the graph file name matches expectation
                graph_file_name = cond_struct_files[i]
                expected_graph_name = f"{graph_name_prefix}_{run_id}.mat"
                if graph_file_name != expected_graph_name:
                    print(f"Unexpected graph name for condition: {condition_info}")
                    print(f"  Expected: {expected_graph_name}")
                    print(f"  Found: {graph_file_name}")
                # Write new events file
                rep_events_str = base_events_content.replace(
                    "<<CFG_SPATIAL_STRUCT_CMDS>>",
                    f"u begin ReconfigureCellConnectivity {graph_file_name}"
                )
                with open(os.path.join(events_dir, event_file_name), "w") as fp:
                    fp.write(rep_events_str)
            # Graph file name is function of run id
            graph_file_name = f"{graph_name_prefix}_" + "${RUN_ID}.mat"

        # -- Build run configuration cp commands --
        # Copy:
        # - events file
        # - run params snapshot (generated by this script)
        config_cp_cmds = []
        config_cp_cmds.append("cp ${CONFIG_DIR}/*.org .")
        config_cp_cmds.append("cp ${CONFIG_DIR}/*.cfg .")
        config_cp_cmds.append("cp ${EVENTS_DIR}/" + f"{cmd_line_params['EVENT_FILE']} .")
        if graph_file_name != "":
            config_cp_cmds.append("cp ${SPATIAL_STRUCTS_DIR}/" + f"{graph_file_name} .")
        config_cp_cmds.append("cp ${PARAM_SNAPSHOT_DIR}/" + "run_params_${SEED}.csv ./run_params.csv")
        file_str = file_str.replace("<<CONFIG_CP_CMDS>>", "\n".join(config_cp_cmds))

        # -- Build run commands --
        run_cmds = []
        avida_args = "-s ${SEED} " + " ".join([f"-set {param} {cmd_line_params[param]}" for param in cmd_line_params])
        run_cmds.append(f'RUN_PARAMS="{avida_args}"')
        run_cmds.append('echo "./${EXEC} ${RUN_PARAMS}" > cmd.log')
        run_cmds.append('./${EXEC} ${RUN_PARAMS} > run.log')
        file_str = file_str.replace("<<RUN_CMDS>>", "\n".join(run_cmds))

        # -- Build analysis commands --
        analysis_cmds = []
        analysis_cmds.append('./${EXEC} ${RUN_PARAMS} -a > analyze.log')
        file_str = file_str.replace("<<ANALYSIS_CMDS>>", "\n".join(analysis_cmds))

        # -- Snapshot meta-parameters --
        # - Build one parameter snapshot per replicate
        # NOTE: if hitting home directory file quota, could go ahead and write
        # these directly to appropriate run directory
        for i in range(args.replicates):
            run_seed = cur_seed + i
            event_file_name = cmd_line_params["EVENT_FILE"].replace("${RUN_ID}", str(i))
            graph_name = "none"
            if multiple_graphs_for_cond:
                graph_name = graph_file_name.replace("${RUN_ID}", f"{i}")
            elif len(cond_struct_files) == 1:
                graph_name = cond_struct_files[-1]
            param_snapshot = [{"param":param, "value":cmd_line_params[param]} for param in cmd_line_params]
            param_snapshot.append({"param":"graph_file", "value":graph_name})
            param_snapshot.append({"param":"graph_type", "value":cond_spatial_struct})
            param_snapshot.append({"param":"EVENT_FILE_name", "value":event_file_name})
            param_snapshot.append({"param":"seed", "value":run_seed})
            # mapping_fpath = "none"
            # if graph_name != "none":
            #     mapping_fpath = os.path.join(
            #         avida_loc_mapping_dir,
            #         f"avida_loc_map__{event_file_name.split('.')[0]}.csv"
            #     )
            # param_snapshot.append({"param":"loc_mapping_fpath", "value":mapping_fpath})
            snapshot_path = os.path.join(param_snapshot_dir, f"run_params_{run_seed}.csv")
            utils.write_csv(snapshot_path, param_snapshot)

        print("  ", cmd_line_params)

        ###################################################################
        # Write job submission file (if any of the array ids are active)
        ###################################################################
        cur_job_dir = job_dir if args.runs_per_subdir == -1 else os.path.join(job_dir, f"job-set-{cur_run_subdir_id}")

        utils.mkdir_p(cur_job_dir)
        with open(os.path.join(cur_job_dir, f'{filename_prefix}.sb'), 'w') as fp:
            fp.write(file_str)

        # Update condition id and current job id
        cur_job_id += 1
        cond_i += 1
        cur_subdir_run_cnt += args.replicates
        if cur_subdir_run_cnt > (args.runs_per_subdir - args.replicates):
            cur_subdir_run_cnt = 0
            cur_run_subdir_id += 1

if __name__ == "__main__":
    main()
