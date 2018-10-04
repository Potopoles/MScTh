#!/bin/bash -l
#
#SBATCH --job-name="lwp"
#SBATCH --time=7:00:00
#SBATCH --ntasks=1
#SBATCH --account='pr04'
#SBATCH --constraint=gpu
#SBATCH --partition=normal
#SBATCH --output=sbatch1.out
#SBATCH --error=sbatch1.err

# All datasets take ~ 4 hrs


echo -e "$SLURM_JOB_NAME started on $(date)\n"

srun -n $SLURM_NTASKS sh_run_lwp.sh

echo -e "$SLURM_JOB_NAME finished on $(date)\n"
