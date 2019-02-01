#!/bin/bash -l
#
#SBATCH --job-name="diurnal"
#SBATCH --time=1:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --account='pr04'
#SBATCH --constraint=gpu
#SBATCH --partition=normal
#SBATCH --output=bOut/sbatchCW.out
#SBATCH --error=bOut/sbatchCW.err


source load_miniconda.sh

echo -e "$SLURM_JOB_NAME started on $(date):\n $command $1 $2\n"

# NORMAL SCRIPTS
#srun -c $SLURM_CPUS_PER_TASK -n $SLURM_NTASKS python -u 00_newScripts/$SLURM_JOB_NAME*.py $SLURM_CPUS_PER_TASK
#srun -c $SLURM_CPUS_PER_TASK -n $SLURM_NTASKS python -u 00_scripts/$SLURM_JOB_NAME*.py $SLURM_CPUS_PER_TASK

# DIURNAL 
FIELDNAME=zCW
srun -c $SLURM_CPUS_PER_TASK -n $SLURM_NTASKS python -u 00_scripts/00_02*.py $FIELDNAME

# SPECIAL
#module load CDO
#cdo sub 02_fields/topocut/1.1/zFQVy.nc 02_fields/topocut/1.1f/zFQVy.nc 1.1_diff_zFQVy.nc
#cdo sub 02_fields/topocut/1.1/zFQVx.nc 02_fields/topocut/1.1f/zFQVx.nc 1.1_diff_zFQVx.nc

echo -e "$SLURM_JOB_NAME finished on $(date)\n"


