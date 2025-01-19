'''
Generate slurm scripts for mabe jobs
'''
import argparse
import os
import sys
import pathlib
import math
from pyvarco import CombinationCollector

# Add scripts directory to path, import utilities from scripts directory.
sys.path.append(
    os.path.join(
        pathlib.Path(os.path.dirname(os.path.abspath(__file__))).parents[3],
        "scripts"
    )
)
import utilities as utils

# Default configuration values
default_seed_offset = 0
default_account = None
default_num_replicates = 30
default_job_time_request = "48:00:00"
default_job_mem_request = "4G"
default_job_name = "mabe"
executable = "MABE"

default_base_slurm_script_fpath = "./base_slurm_script.txt"

# Create combos
combos = CombinationCollector()

fixed_params_direct = {
    "num_gens": "100000",
    "eval_ifg.mut_prob": "0.0125",

}

special_decorators = [
    "__COPY_OVER",
    "__DYNAMIC"
]

combos.register_var("spatial_structure__DYNAMIC")
combos.add_val(
    "spatial_structure__DYNAMIC",
    [
        "linear-chain",
        "random-waxman",
        "toroidal-lattice",
        "star",
        "well-mixed",
        "wheel",
        "cycle",
        "comet-kite",
        "clique-ring"
    ]
)
# "adj_placement.adj_filename"

def main():
    parser = argparse.ArgumentParser(description="Generate SLURM submission scripts.")
    parser.add_argument("--data_dir", type=str, help="Where is the output directory for phase one of each run?")
    parser.add_argument("--config_dir", type=str, help="Where is the configuration directory for experiment?")
    parser.add_argument("--spatial_structs_dir", type=str, help="Which directory contains spatial structures to be used?")
    parser.add_argument("--param_snapshot_dir", type=str, help="Which directory to dump parameter snapshots?")
    parser.add_argument("--repo_dir", type=str, help="Where is the repository for this experiment?")
    parser.add_argument("--job_dir", type=str, default=None, help="Where to output these job files? If none, put in 'jobs' directory inside of the data_dir")
    parser.add_argument("--replicates", type=int, default=default_num_replicates, help="How many replicates should we run of each condition?")
    parser.add_argument("--seed_offset", type=int, default=default_seed_offset, help="Value to offset random number seeds by")
    parser.add_argument("--hpc_account", type=str, default=default_account, help="Value to use for the slurm ACCOUNT")
    parser.add_argument("--time_request", type=str, default=default_job_time_request, help="How long to request for each job on hpc?")
    parser.add_argument("--mem", type=str, default=default_job_mem_request, help="How much memory to request for each job?")
    parser.add_argument("--jobs_per_subdir", type=int, default=-1, help="How many replicates to clump into job subdirectories")
    parser.add_argument("--runs_per_job", type=int, default=1, help="How many runs to do in a single job?")
    parser.add_argument("--base_slurm", type=str, default=default_base_slurm_script_fpath, help="Slurm script template to use")

    args = parser.parse_args()
    # Load in the base slurm file
    base_slurm_script = ""
    with open(args.base_slurm, "r") as fp:
        base_slurm_script = fp.read()

    # Get list of all combinations to run
    combo_list = combos.get_combos()

    # Calculate how many total jobs we have, and what the last id will be
    num_jobs = args.replicates * len(combo_list)
    # Echo chosen options
    print(f'Generating {num_jobs} across {len(combo_list)} files!')
    print(f" - data_dir: {args.data_dir}")
    print(f" - config_dir: {args.config_dir}")
    print(f" - spatial_structs_dir: {args.spatial_structs_dir}")
    print(f" - param_snapshot_dir: {args.param_snapshot_dir}")
    print(f" - repo_dir: {args.repo_dir}")
    print(f" - job_dir: {args.job_dir}")
    print(f" - replicates: {args.replicates}")
    print(f" - seed_offset: {args.seed_offset}")
    print(f" - hpc_account: {args.hpc_account}")
    print(f" - time_request: {args.time_request}")
    print(f" - mem: {args.mem}")
    print(f" - jobs_per_subdir: {args.jobs_per_subdir}")
    print(f" - runs_per_job: {args.runs_per_job}")
    print(f" - base_slurm: {args.base_slurm}")

    # If no job_dir provided, default to data_dir/jobs
    if args.job_dir == None:
        args.job_dir = os.path.join(args.data_dir, "jobs")

    # Localize some commandline args for convenience ( less typing :) )
    config_dir = args.config_dir
    repo_dir = args.repo_dir
    data_dir = args.data_dir
    spatial_structs_dir = args.spatial_structs_dir
    param_snapshot_dir = args.param_snapshot_dir
    job_dir = args.job_dir

    # Create param snapshot directory if it doesn't exist already
    utils.mkdir_p(param_snapshot_dir)

    # Identify relevant/available spatial structure files
    spatial_structs = combos.get_vals("spatial_structure__DYNAMIC")
    # Only allow .txt files.
    # IMPORTANT: If multiple graph files for a single condition, they must:
    #  - each end with _ID.mat where ID is a value [0:number of replicates)
    #  - all be in matrix format
    struct_files = {
        spatial_struct:[
            filename
            for filename in os.listdir(spatial_structs_dir)
            if filename.startswith(spatial_struct) and (".txt" in filename)
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

    cond_i = 0
    cur_job_id = 0
    cur_subdir_job_cnt = 0
    cur_job_subdir_id = 0
    # How many jobs per array?
    jobs_per_slurm = math.ceil(args.replicates / args.runs_per_job)
    for condition_info in combo_list:
        print(condition_info)
        # Calc current seed
        cur_seed = args.seed_offset + (cur_job_id * args.replicates)

        slurm_prefix = f"RUN_C{cond_i}"
        slurm_str = base_slurm_script
        slurm_str = slurm_str.replace("<<TIME_REQUEST>>", args.time_request)
        slurm_str = slurm_str.replace("<<ARRAY_ID_RANGE>>", f"1-{jobs_per_slurm}")
        slurm_str = slurm_str.replace("<<MEMORY_REQUEST>>", args.mem)
        slurm_str = slurm_str.replace("<<JOB_NAME>>", f"C{cond_i}")
        slurm_str = slurm_str.replace("<<CONFIG_DIR>>", config_dir)
        slurm_str = slurm_str.replace("<<REPO_DIR>>", repo_dir)
        slurm_str = slurm_str.replace("<<SPATIAL_STRUCT_DIR>>", spatial_structs_dir)
        slurm_str = slurm_str.replace("<<PARAM_SNAPSHOT_DIR>>", param_snapshot_dir)
        slurm_str = slurm_str.replace("<<EXEC>>", executable)
        slurm_str = slurm_str.replace("<<JOB_SEED_OFFSET>>", str(cur_seed))
        slurm_str = slurm_str.replace("<<BASE_RUN_DIR>>", data_dir)
        slurm_str = slurm_str.replace("<<CONDITION_ID>>", str(cond_i))
        slurm_str = slurm_str.replace("<<NUM_RUNS_PER_JOB>>", str(args.runs_per_job))
        slurm_str = slurm_str.replace("<<TOTAL_REPLICATES>>", str(args.replicates))
        if args.hpc_account == None:
            slurm_str = slurm_str.replace("<<ACCOUNT_INFO>>", "")
        else:
            slurm_str = slurm_str.replace("<<ACCOUNT_INFO>>", f"#SBATCH --account {args.hpc_account}")



        ###################################################################
        # Write job submission file (if any of the array ids are active)
        ###################################################################
        cur_job_dir = job_dir if args.jobs_per_subdir == -1 else os.path.join(job_dir, f"job-set-{cur_job_subdir_id}")

        utils.mkdir_p(cur_job_dir)
        with open(os.path.join(cur_job_dir, f'{slurm_prefix}.sb'), 'w') as fp:
            fp.write(slurm_str)

        # Update condition id and current job id
        cur_job_id += 1
        cur_subdir_job_cnt += jobs_per_slurm
        if cur_subdir_job_cnt > (args.jobs_per_subdir - jobs_per_slurm):
            cur_subdir_job_cnt = 0
            cur_job_subdir_id += 1
        cond_i += 1

if __name__ == "__main__":
    main()