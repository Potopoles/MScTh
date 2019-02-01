#!/bin/bash -l
#
#SBATCH --job-name="topoCut"
#SBATCH --time=0:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --account='pr04'
#SBATCH --constraint=gpu
#SBATCH --partition=debug
#SBATCH --output=bOut/topocut.out
#SBATCH --error=bOut/topocut.err

#fileName = "$SLURM_JOB_NAME*"

# for 4.4 takes 8 minutes

echo -e "$SLURM_JOB_NAME started on $(date):\n $command $1 $2\n"

srun -c $SLURM_CPUS_PER_TASK -n $SLURM_NTASKS python -u topocut.py $SLURM_CPUS_PER_TASK


echo -e "$SLURM_JOB_NAME finished on $(date)\n"


