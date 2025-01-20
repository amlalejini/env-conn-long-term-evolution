#!/usr/bin/env bash
REPLICATES=10
EXP_SLUG=2025-01-19-vary-struct
ACCOUNT=devolab
SEED_OFFSET=1000
JOB_TIME=8:00:00
JOB_MEM=8G
PROJECT_NAME=env-conn-long-term-evolution
JOBS_PER_SUBDIR=950
RUNS_PER_JOB=5

REPO_DIR=/mnt/home/lalejini/devo_ws/${PROJECT_NAME}
REPO_SCRIPTS_DIR=${REPO_DIR}/scripts
HOME_EXP_DIR=${REPO_DIR}/experiments/mabe2-exps/${EXP_SLUG}
GRAPHS_DIR=${HOME_EXP_DIR}/hpc/spatial-structs
GRAPHS_CFG=${HOME_EXP_DIR}/hpc/graphs.json
PARAM_SNAPSHOT_DIR=${HOME_EXP_DIR}/hpc/param_snapshots
BASE_SLURM_FILE=${HOME_EXP_DIR}/hpc/base_slurm_script.txt

DATA_DIR=${HOME_EXP_DIR}/hpc/test/data
JOB_DIR=${HOME_EXP_DIR}/hpc/test/jobs
CONFIG_DIR=${HOME_EXP_DIR}/hpc/config

# (1) Activate appropriate Python virtual environment
source ${REPO_DIR}/pyenv/bin/activate
# (2) Generate graphs
python3 ${REPO_SCRIPTS_DIR}/gen-graphs.py --config ${GRAPHS_CFG} --dump_dir ${GRAPHS_DIR}
# (3) Generate slurm script
#   - This will generate an events file for each run
python3 gen-sub.py \
  --param_snapshot_dir ${PARAM_SNAPSHOT_DIR} \
  --jobs_per_subdir ${JOBS_PER_SUBDIR} \
  --runs_per_job ${RUNS_PER_JOB} \
  --time_request ${JOB_TIME} \
  --mem ${JOB_MEM} \
  --data_dir ${DATA_DIR} \
  --config_dir ${CONFIG_DIR} \
  --repo_dir ${REPO_DIR} \
  --replicates ${REPLICATES} \
  --job_dir ${JOB_DIR} \
  --hpc_account ${ACCOUNT} \
  --seed_offset ${SEED_OFFSET} \
  --spatial_structs_dir ${GRAPHS_DIR} \
  --base_slurm ${BASE_SLURM_FILE}