#!/bin/bash

SBATCH --job-name=nature2003replicateexperiment
SBATCH --mail-type=BEGIN,END,FAIL

SBATCH --mail-user=ggmain777@gmail.com
SBATCH --nodes=1
SBATCH --ntasks-per-node=1
SBATCH --mem=4g
SBATCH --time=00-04:00:00
#SBATCH --account=
SBATCH --array=1-30


#USERNAME=gordongr
#EXPERIMENT_ID=
#OUTPUT_DIR=
#CONFIG_FIR=
#SEED_OFFSET=1800

SEED=$((SEED_OFFSET + SLURM_ARRAY_TASK_ID -1))
JOB_ID=${SLURM_ARRAY_TASK_ID}
RUN_DIR=${OUTPUT_DIR}/run_${SEED}

mkdir -p ${RUN_DIR}

cd ${RUN_DIR}

cp ${CONDIG_DIR}/avida .
cp ${CONFIG_DIR}/analyze.cfg .
cp ${CONFIG_DIR}/avida.cfg .
cp ${CONFIG_DIR}/default-heads.org .
#cp ${CONFIG_DIR}/default-heads-sex.org .
cp ${CONFIG_DIR}/default-transsmt.org .
cp ${CONFIG_DIR}/environments.cfg .
cp ${CONFIG_DIR}/events.cfg .
#cp ${CONFIG_DIR}/instset-heads-sex.org
cp ${CONFIG_DIR}/instset-heads.cfg .
cp ${CONFIG_DIR}/instset-transsmt.cfg .

#cant jsut set in config?
EXECUTE="avida -s${SEED} -set " #set env vars
echo ${EXECUTE} > cmd.log
./${EXECUTE} > run.log
./${EXECUTE} -a > analyze.log




rm avida
rm avida.cfg
rm analyze.cfg
rm default-heads.org
#rm default-heads-sex.org
rm defualt-transsmt.org
rm evironments.cfg
rm events.cfg
#rm instset-heads-sex.org
rm instset-heads.cfg
rm instset-transsmt.cfg

