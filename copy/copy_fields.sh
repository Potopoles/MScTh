#!/bin/bash


src_path=/project/pr04/heimc/data/cosmo_out/MScTh
mkdir -p $SCRATCH/MScTh/01_rawData/4.4
cp $src_path/RAW4/4_lm_f/output/zlev/lff*z.nc \
    $SCRATCH/MScTh/01_rawData/4.4

mkdir -p $SCRATCH/MScTh/01_rawData/4.4f
cp $src_path/SM4/4_lm_f/output/zlev/lff*z.nc \
    $SCRATCH/MScTh/01_rawData/4.4f

mkdir -p $SCRATCH/MScTh/01_rawData/2.2
cp $src_path/RAW2/4_lm_f/output/zlev/lff*z.nc \
    $SCRATCH/MScTh/01_rawData/2.2

mkdir -p $SCRATCH/MScTh/01_rawData/2.2f
cp $src_path/SM2/4_lm_f/output/zlev/lff*z.nc \
    $SCRATCH/MScTh/01_rawData/2.2f

mkdir -p $SCRATCH/MScTh/01_rawData/1.1
cp $src_path/RAW1/4_lm_f/output/zlev/lff*z.nc \
    $SCRATCH/MScTh/01_rawData/1.1

mkdir -p $SCRATCH/MScTh/01_rawData/1.1f
cp $src_path/SM1/4_lm_f/output/zlev/lff*z.nc \
    $SCRATCH/MScTh/01_rawData/1.1f




#srcPath=scratch_save/02_fields/topocut
#srcPath=/scratch/snx1600/heimc/MScTh/02_fields/diurnal
#srcPath=/scratch/snx1600/heimc/MScTh/02_fields/topocut
#srcPath=/project/pr04/heimc/initial_data/move
#srcPath=/project/pr04/heimc/02_fields/diurnal

#destPath=$SCRATCH/MScTh/02_fields/diurnal
#destPath=$SCRATCH/02_fields/topocut
#destPath=/scratch/snx3000/heimc/MScTh/02_fields/diurnal
#destPath=/scratch/snx3000/heimc/MScTh/02_fields/topocut

#var=nTOT_PREC.nc
#
#echo $var
#
#echo 4.4
#cp $srcPath/4.4/$var $destPath/4.4/
#echo 4.4f
#cp $srcPath/4.4f/$var $destPath/4.4f/
#echo 2.2
#cp $srcPath/2.2/$var $destPath/2.2/
#echo 2.2f
#cp $srcPath/2.2f/$var $destPath/2.2f/
#echo 1.1
#cp $srcPath/1.1/$var $destPath/1.1/
#echo 1.1f
#cp $srcPath/1.1f/$var $destPath/1.1f/
#
#echo 4.4r
#cp $srcPath/4.4r/$var $destPath/4.4r/
#echo 2.2r
#cp $srcPath/2.2r/$var $destPath/2.2r/
#echo 1.1r
#cp $srcPath/1.1r/$var $destPath/1.1r/
#
