#!/bin/bash

#projPath=scratch_save/02_fields/topocut
#scraPath=$SCRATCH/02_fields/topocut
projPath=scratch_save/02_fields/diurnal
scraPath=$SCRATCH/02_fields/diurnal
var=nTOT_PREC.nc

echo $var

echo 4.4
cp $projPath/4.4/$var $scraPath/4.4/
echo 4.4f
cp $projPath/4.4f/$var $scraPath/4.4f/
echo 2.2
cp $projPath/2.2/$var $scraPath/2.2/
echo 2.2f
cp $projPath/2.2f/$var $scraPath/2.2f/
echo 1.1
cp $projPath/1.1/$var $scraPath/1.1/
echo 1.1f
cp $projPath/1.1f/$var $scraPath/1.1f/

