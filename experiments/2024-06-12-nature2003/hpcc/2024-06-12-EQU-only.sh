#!/bin/bash

#SBATCH --nodes=1
#SBATCH --mem=4G
#SBATCH --time=04:00:00
#SBATCH --partition=all
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --job-name=2024-06-12-nature2003
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=ggmain777@gmail.com
#SBATCH --array=1-10


USERNAME=gordongr
EXPERIMENT_ID=2024-06-12-nature2003
PROJECT_ID=env-conn-long-term-evolution
OUTPUT_DIR=/mnt/projects/lalejina_project/data-gordongr/${PROJECT_ID}/${EXPERIMENT_ID}
REPO_DIR=/mnt/home/${USERNAME}/research/${PROJECT_ID}
CONFIG_DIR=${REPO_DIR}/experiments/${EXPERIMENT_ID}/hpcc/config
SEED_OFFSET=1100
TREATMENT_ENVIRONMENT=environment-EQU-only.cfg
SEED=$((SEED_OFFSET + SLURM_ARRAY_TASK_ID -1))
RUN_DIR=${OUTPUT_DIR}/run_${SEED}

mkdir -m 775 -p ${RUN_DIR}
cd ${RUN_DIR}

cp ${CONFIG_DIR}/avida .
cp ${CONFIG_DIR}/analyze.cfg .
cp ${CONFIG_DIR}/avida.cfg .
cp ${CONFIG_DIR}/default-heads.org .
cp ${CONFIG_DIR}/${TREATMENT_ENVIRONMENT} .
cp ${CONFIG_DIR}/events.cfg .
cp ${CONFIG_DIR}/instset-heads.cfg .


EXECUTE="avida -s ${SEED} -set ENVIRONMENT_FILE ${TREATMENT_ENVIRONMENT}"
echo ${EXECUTE} > cmd.log
./${EXECUTE} > run.log
./${EXECUTE} -a > analyze.log




rm avida
rm avida.cfg
rm analyze.cfg
rm default-heads.org
rm ${TREATMENT_ENVIRONMENT}
rm events.cfg
rm instset-heads.cfg

