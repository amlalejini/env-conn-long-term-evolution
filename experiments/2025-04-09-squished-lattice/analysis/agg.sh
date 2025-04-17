USERNAME=lalejina
EXP_SLUG=2025-04-09-squished-lattice
PROJECT_NAME=env-conn-long-term-evolution

REPO_DIR=/mnt/home/${USERNAME}/devo_ws/${PROJECT_NAME}
REPO_SCRIPTS_DIR=${REPO_DIR}/scripts
HOME_EXP_DIR=${REPO_DIR}/experiments/${EXP_SLUG}
GRAPHS_DIR=${HOME_EXP_DIR}/hpc/spatial-structs
DATA_DIR=/mnt/projects/${USERNAME}_project/${PROJECT_NAME}/${EXP_SLUG}

ANALYSIS_DIR=${HOME_EXP_DIR}/analysis/
DUMP_DIR=${ANALYSIS_DIR}/dump/

FINAL_UPDATE=100000

python3 aggregate.py \
  --data_dir ${DATA_DIR} \
  --dump_dir ${DUMP_DIR} \
  --summary_update ${FINAL_UPDATE} \
  --time_series_units total \
  --time_series_resolution 100

python3 ${REPO_SCRIPTS_DIR}/aggregate-graph-loc-info.py \
  --data_dir ${DATA_DIR} \
  --dump_dir ${DUMP_DIR}

python3 ${REPO_SCRIPTS_DIR}/annotate-graph-loc-info.py \
  --summary_data ${DUMP_DIR}/summary.csv \
  --graph_birth_data ${DUMP_DIR}/graph_birth_info.csv \
  --graphs_dir ${GRAPHS_DIR} \
  --dump_dir ${DUMP_DIR}

python3 ${REPO_SCRIPTS_DIR}/summarize-node-properties.py \
  --summary_data ${DUMP_DIR}/summary.csv \
  --graph_birth_data ${DUMP_DIR}/graph_birth_info.csv \
  --graphs_dir ${GRAPHS_DIR} \
  --dump_dir ${DUMP_DIR}

python3 ${REPO_SCRIPTS_DIR}/run-morans-i.py \
  --graph_loc_data ${DUMP_DIR}/graph_birth_info_annotated.csv \
  --graphs_dir ${GRAPHS_DIR} \
  --dump_dir ${DUMP_DIR}