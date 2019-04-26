#!/bin/bash
#
#SBATCH --job-name="isolate_var"
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --account='pr04'
#SBATCH --partition=normal
#SBATCH --constraint=gpu
#SBATCH --output=sbatch.out
#SBATCH --error=sbatch.err

echo -e "$SLURM_JOB_NAME started on $(date):\n $command $1 $2\n"

source /users/heimc/scripts/load_modules.sh

srun -c $SLURM_CPUS_PER_TASK -n $SLURM_NTASKS isolate_var.sh

#var_name=zFQVy
#srun -c $SLURM_CPUS_PER_TASK -n $SLURM_NTASKS \
#    python -u diurnal.py $var_name $SLURM_CPUS_PER_TASK


echo -e "$SLURM_JOB_NAME finished on $(date)\n"
