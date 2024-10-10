#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --mem=8G
#SBATCH --time=03:00:00
#SBATCH --partition=all
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --job-name=2024-10-10-caveman-parameterizations
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=ggmain777@gmail.com


#EXP_SLUG=2024-10-10-caveman-parameterizations
#PROJECT_NAME=env-conn-long-term-evolution
#REPO_DIR=/mnt/home/gordongr/research/${PROJECT_NAME}
#EXPERIMENT_DIR=${PROJECT_NAME}/${EXP_SLUG}

cd /mnt/home/gordongr/research/env-conn-long-term-evolution/experiments/2024-10-10-caveman-parameterizations/hpc/
./job-gen.sh > output.log
