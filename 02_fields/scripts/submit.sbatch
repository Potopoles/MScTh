#!/bin/bash
#
#SBATCH --job-name="isolate_var"
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --account='pr04'
#SBATCH --partition=debug
#SBATCH --constraint=gpu
#SBATCH --output=sbatch.out
#SBATCH --error=sbatch.err

srun -c $SLURM_CPUS_PER_TASK -n $SLURM_NTASKS isolate_var.sh
