PROJECT_NAME=env-conn-long-term-evolution
REPO_DIR=/mnt/home/lalejini/devo_ws/${PROJECT_NAME}
REPO_SCRIPTS_DIR=${REPO_DIR}/scripts

module purge
module load Python/3.11.5
module load GCCcore/13.2.0
module load CMake/3.27.6
source ${REPO_DIR}/pyenv/bin/activate