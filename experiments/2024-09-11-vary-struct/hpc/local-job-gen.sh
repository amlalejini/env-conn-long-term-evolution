#!/usr/bin/env bash

REPLICATES=50
EXP_SLUG=2024-09-11-vary-struct
ACCOUNT=devolab
SEED_OFFSET=1000
JOB_TIME=24:00:00
JOB_MEM=8G
PROJECT_NAME=env-conn-long-term-evolution
RUNS_PER_SUBDIR=950

REPO_DIR=/Users/lalejina/devo_ws/${PROJECT_NAME}
REPO_SCRIPTS_DIR=${REPO_DIR}/scripts
HOME_EXP_DIR=${REPO_DIR}/experiments/${EXP_SLUG}
GRAPHS_DIR=${HOME_EXP_DIR}/hpc/spatial-structs
GRAPHS_CFG=${HOME_EXP_DIR}/hpc/graphs.json

DATA_DIR=${HOME_EXP_DIR}/hpc/test/data
JOB_DIR=${HOME_EXP_DIR}/hpc/test/jobs
CONFIG_DIR=${HOME_EXP_DIR}/hpc/config

# (1) Activate appropriate Python virtual environment
source ${REPO_DIR}/pyenv/bin/activate
# (2) Generate graphs
python3 ${REPO_SCRIPTS_DIR}/gen-graphs.py --config ${GRAPHS_CFG} --dump_dir ${GRAPHS_DIR}