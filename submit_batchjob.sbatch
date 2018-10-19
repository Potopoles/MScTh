#!/bin/bash -l
#
#SBATCH --job-name="06_02"
#SBATCH --time=5:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --account='pr04'
#SBATCH --constraint=gpu
#SBATCH --partition=normal
#SBATCH --output=bOut/sbatch1.out
#SBATCH --error=bOut/sbatch1.err


source load_miniconda.sh

echo -e "$SLURM_JOB_NAME started on $(date):\n $command $1 $2\n"

#srun -n $SLURM_NTASKS python -u 00_scripts/$SLURM_JOB_NAME*.py
srun -c $SLURM_CPUS_PER_TASK -n $SLURM_NTASKS python -u 00_newScripts/$SLURM_JOB_NAME*.py $SLURM_CPUS_PER_TASK

echo -e "$SLURM_JOB_NAME finished on $(date)\n"


