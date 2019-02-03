#!/bin/bash -l
#
#SBATCH --job-name="copy"
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --account='pr04'
#SBATCH --partition=xfer
#SBATCH --output=process.out
#SBATCH --error=process.err

module unload xalt


echo -e "$SLURM_JOB_NAME started on $(date):\n $command $1 $2\n"

srun -n $SLURM_NTASKS copy_scratch_project.sh
#srun -n $SLURM_NTASKS copy_fields.sh

echo -e "$SLURM_JOB_NAME finished on $(date)\n"


