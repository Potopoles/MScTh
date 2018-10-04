#!/bin/bash -l
#
#SBATCH --job-name="topoCut"
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --account='pr04'
#SBATCH --constraint=gpu
#SBATCH --partition=normal
#SBATCH --output=bOut/sbatch.out
#SBATCH --error=bOut/sbatch.err

#fileName = "$SLURM_JOB_NAME*"

# for 4.4 takes 8 minutes

echo -e "$SLURM_JOB_NAME started on $(date):\n $command $1 $2\n"

srun -n $SLURM_NTASKS python -u topoCut.py

echo -e "$SLURM_JOB_NAME finished on $(date)\n"


