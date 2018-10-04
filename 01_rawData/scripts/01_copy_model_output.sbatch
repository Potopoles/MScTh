#!/bin/bash
#
#SBATCH --job-name="copy"
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --account='pr04'
#SBATCH --partition=xfer
#SBATCH --output=sbatch.out
#SBATCH --error=sbatch.err

#module unload daint-gpu
#module load daint-mc


models=("4.4" "2.2" "1.1")
modes=("" "_filtered")
#models=("4.4")
#modes=("")

command="cp -r"
constantParamString="lffd2006071100c.nc"


for model in "${models[@]}" # MODEL LOOP
do
	:
	#model="4.4"

	for mode in "${modes[@]}" # MODE LOOP
	do
		:
		#mode="_filtered"

		modelString="initial_data/wl_${model}_km${mode}"
		if [ "$mode" = "_filtered" ]; then
			modelSaveString="${model}f"
		else
			modelSaveString="${model}"
		fi
		echo $modelSaveString

		cd /scratch/snx3000/heimc/01_rawData/
		if [ ! -d "$modelSaveString" ]; then
			mkdir "$modelSaveString"
		fi

		cd /project/pr04/heimc
		$command ${modelString}/output/lm_f/mlev /scratch/snx3000/heimc/01_rawData/${modelSaveString}/
		cd /scratch/snx3000/heimc/01_rawData/${modelSaveString}
		mv mlev/"$constantParamString" mlev/constantParams.nc
		mv mlev/* .
		rm -r mlev

		#cd /project/pr04/heimc
		#$command ${modelString}/output/lm_f/zlev /scratch/snx3000/heimc/01_rawData/${modelSaveString}/
		#cd /scratch/snx3000/heimc/01_rawData/${modelSaveString}
		#mv zlev/"$constantParamString" zlev/constantParamsz.nc
		#mv zlev/* .
		#rm -r zlev

	done # MODE LOOP
done # MODEL LOOP

#module unload daint-mc
#module load daint-gpu

