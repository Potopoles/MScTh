#!/bin/bash


cp /project/pr04/heimc/initial_data/wl_4.4_km/4_lm_f/output/zlev/lff*z.nc \
    $SCRATCH/MScTh/01_rawData/4.4
cp /project/pr04/heimc/initial_data/wl_4.4_km_filtered/4_lm_f/output/zlev/lff*z.nc \
    $SCRATCH/MScTh/01_rawData/4.4f
cp /project/pr04/heimc/initial_data/wl_2.2_km/4_lm_f/output/zlev/lff*z.nc \
    $SCRATCH/MScTh/01_rawData/2.2
cp /project/pr04/heimc/initial_data/wl_2.2_km_filtered/4_lm_f/output/zlev/lff*z.nc \
    $SCRATCH/MScTh/01_rawData/2.2f
cp /project/pr04/heimc/initial_data/wl_1.1_km/4_lm_f/output/zlev/lff*z.nc \
    $SCRATCH/MScTh/01_rawData/1.1
cp /project/pr04/heimc/initial_data/wl_1.1_km_filtered/4_lm_f/output/zlev/lff*z.nc \
    $SCRATCH/MScTh/01_rawData/1.1f


exit 1




#srcPath=scratch_save/02_fields/topocut
#srcPath=/scratch/snx1600/heimc/MScTh/02_fields/diurnal
#srcPath=/scratch/snx1600/heimc/MScTh/02_fields/topocut
srcPath=/project/pr04/heimc/initial_data/move

#destPath=$SCRATCH/02_fields/diurnal
#destPath=$SCRATCH/02_fields/topocut
#destPath=/scratch/snx3000/heimc/MScTh/02_fields/diurnal
#destPath=/scratch/snx3000/heimc/MScTh/02_fields/topocut

#var=nPMSL.nc

echo $var

echo 4.4
cp $srcPath/4.4/$var $destPath/4.4/
echo 4.4f
cp $srcPath/4.4f/$var $destPath/4.4f/
echo 2.2
cp $srcPath/2.2/$var $destPath/2.2/
echo 2.2f
cp $srcPath/2.2f/$var $destPath/2.2f/
echo 1.1
cp $srcPath/1.1/$var $destPath/1.1/
echo 1.1f
cp $srcPath/1.1f/$var $destPath/1.1f/

#echo 4.4r
#cp $srcPath/4.4r/$var $destPath/4.4r/
#echo 2.2r
#cp $srcPath/2.2r/$var $destPath/2.2r/
#echo 1.1r
#cp $srcPath/1.1r/$var $destPath/1.1r/

