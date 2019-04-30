#!/bin/bash

source=../../01_rawData/topocut
#source=../../01_rawData/lwp
dest=../topocut

ress=(4.4 2.2 1.1)
modes=("" f)

#ress=(4.4)
#modes=("" f)

vars=("AQVT_TOT" "AQVT_ADV" "AQVT_ZADV" "AQVT_TURB" "AQVT_MIC")
vars=("CW" "QI" "QC")

vars=("FQVy")
vars=("WVP")
vars=(U V)
vars=(RHO)

for var in "${vars[@]}"; do
    #var=AQVT_TOT
    echo $var

    for res in "${ress[@]}"; do
        for mode in "${modes[@]}"; do
            echo $res$mode
            rm $dest/$res$mode/z${var}.nc
            ncrcat -v $var $source/$res$mode/lffd*z.nc $dest/$res$mode/z${var}.nc
        done
    done
done



