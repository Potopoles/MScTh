#!/bin/bash

source=../../01_rawData/topocut
#source=../../01_rawData/lwp
dest=../topocut

models=(RAW4 SM4 RAW2 SM2 RAW1 SM1)

vars=("AQVT_TOT" "AQVT_ADV" "AQVT_ZADV" "AQVT_TURB" "AQVT_MIC")
vars=("CW" "QI" "QC")

vars=("FQVy")
vars=("WVP")
vars=(U V QV QC QR QI QS W T P)
#vars=(RHO)

for var in "${vars[@]}"; do
    #var=AQVT_TOT
    echo $var

    for model in "${models[@]}"; do
        echo $model
        mkdir -p $dest/$model
        rm $dest/$model/z${var}.nc
        ncrcat -v $var $source/$model/lffd*z.nc $dest/$model/z${var}.nc
    done
done



