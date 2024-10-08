#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --mem=8G
#SBATCH --time=05:00:00
#SBATCH --partition=all
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --job-name=2024-09-26-exploratory-runs
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=ggmain777@gmail.com


#EXP_SLUG=2024-09-26-exploratory-runs
#PROJECT_NAME=env-conn-long-term-evolution
#REPO_DIR=/mnt/home/gordongr/research/${PROJECT_NAME}
#EXPERIMENT_DIR=${PROJECT_NAME}/${EXP_SLUG}

cd /mnt/home/gordongr/research/env-conn-long-term-evolution/experiments/2024-09-26-exploratory-runs/hpc/
./job-gen.sh > output.log

