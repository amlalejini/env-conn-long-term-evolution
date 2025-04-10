#!/usr/bin/env bash

REPLICATES=30
EXP_SLUG=2025-04-09-squished-lattice
ACCOUNT=devolab
SEED_OFFSET=10000
JOB_TIME=8:00:00
JOB_MEM=8G
PROJECT_NAME=env-conn-long-term-evolution
RUNS_PER_SUBDIR=950
USERNAME=lalejina

REPO_DIR=/mnt/home/${USERNAME}/devo_ws/${PROJECT_NAME}
REPO_SCRIPTS_DIR=${REPO_DIR}/scripts
HOME_EXP_DIR=${REPO_DIR}/experiments/${EXP_SLUG}
GRAPHS_DIR=${HOME_EXP_DIR}/hpc/spatial-structs
GRAPHS_CFG=${HOME_EXP_DIR}/hpc/graphs.json
EVENTS_DIR=${HOME_EXP_DIR}/hpc/events
PARAM_SNAPSHOT_DIR=${HOME_EXP_DIR}/hpc/param_snapshots

DATA_DIR=/mnt/projects/${USERNAME}_project/data/${PROJECT_NAME}/${EXP_SLUG}
JOB_DIR=${DATA_DIR}/jobs
CONFIG_DIR=${HOME_EXP_DIR}/hpc/config

# (1) Activate appropriate Python virtual environment
source ${REPO_DIR}/hpc-env/clipper-hpc-env.sh
# (2) Generate graphs
python3 ${REPO_SCRIPTS_DIR}/gen-graphs.py --config ${GRAPHS_CFG} --dump_dir ${GRAPHS_DIR}
# (3) Generate slurm script
#   - This will generate an events file for each run
python3 gen-sub.py \
  --param_snapshot_dir ${PARAM_SNAPSHOT_DIR} \
  --events_dir ${EVENTS_DIR} \
  --runs_per_subdir ${RUNS_PER_SUBDIR} \
  --time_request ${JOB_TIME} \
  --mem ${JOB_MEM} \
  --data_dir ${DATA_DIR} \
  --config_dir ${CONFIG_DIR} \
  --repo_dir ${REPO_DIR} \
  --replicates ${REPLICATES} \
  --job_dir ${JOB_DIR} \
  --hpc_account ${ACCOUNT} \
  --seed_offset ${SEED_OFFSET} \
  --spatial_structs_dir ${GRAPHS_DIR}