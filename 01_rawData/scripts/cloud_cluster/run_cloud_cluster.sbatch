#!/bin/bash -l
#
#SBATCH --job-name="cloud_cluster"
#SBATCH --time=0:30:00
#SBATCH --ntasks=1
#SBATCH --account='pr04'
#SBATCH --constraint=gpu
#SBATCH --partition=debug
#SBATCH --output=sbatch.out
#SBATCH --error=sbatch.err

# for 4.4 & 4.4f took 5 min
# for 2.2 & 2.2f took 45 min
# for 1.1 & 1.1f took 6h



echo -e "$SLURM_JOB_NAME started on $(date)\n"

srun -n $SLURM_NTASKS sh_run_cloud_cluster.sh

echo -e "$SLURM_JOB_NAME finished on $(date)\n"
