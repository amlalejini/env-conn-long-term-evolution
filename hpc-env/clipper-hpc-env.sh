PROJECT_NAME=env-conn-long-term-evolution
REPO_DIR=/mnt/home/lalejina/devo_ws/${PROJECT_NAME}
REPO_SCRIPTS_DIR=${REPO_DIR}/scripts

module purge
module load python/3.11.9
module load gcc/14.2.0
module load CMake/3.30.5
source ${REPO_DIR}/pyenv/bin/activate