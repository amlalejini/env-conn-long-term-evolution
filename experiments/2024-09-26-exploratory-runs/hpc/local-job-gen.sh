#!/usr/bin/env bash

REPLICATES=3
EXP_SLUG=2024-09-26-exploratory-runs
SEED_OFFSET=1000
JOB_TIME=32:00:00
JOB_MEM=8G
PROJECT_NAME=env-conn-long-term-evolution
RUNS_PER_SUBDIR=950

REPO_DIR=/home/grant/${PROJECT_NAME}
REPO_SCRIPTS_DIR=${REPO_DIR}/scripts
HOME_EXP_DIR=${REPO_DIR}/experiments/${EXP_SLUG}
GRAPHS_DIR=${HOME_EXP_DIR}/hpc/spatial-structs
GRAPHS_CFG=${HOME_EXP_DIR}/hpc/local_test_graphs.json
EVENTS_DIR=${HOME_EXP_DIR}/hpc/events
PARAM_SNAPSHOT_DIR=${HOME_EXP_DIR}/hpc/param_snapshots
AVIDA_LOC_MAPPING_DIR=${HOME_EXP_DIR}/hpc/avida_loc_mappings

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
  --events_dir ${EVENTS_DIR} \
  --runs_per_subdir ${RUNS_PER_SUBDIR} \
  --time_request ${JOB_TIME} \
  --mem ${JOB_MEM} \
  --data_dir ${DATA_DIR} \
  --config_dir ${CONFIG_DIR} \
  --repo_dir ${REPO_DIR} \
  --replicates ${REPLICATES} \
  --job_dir ${JOB_DIR} \
  --seed_offset ${SEED_OFFSET} \
  --spatial_structs_dir ${GRAPHS_DIR}
