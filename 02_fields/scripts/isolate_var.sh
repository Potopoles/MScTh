#!/bin/bash

source=../../01_rawData/topocut
#source=../../01_rawData/lwp
source_mlev=../../../data/cosmo_out/MScTh
dest=../topocut

models=(RAW4 SM4 RAW2 SM2 RAW1 SM1)
#models=(RAW4 SM4 RAW2 SM2)
#models=(SM1 RAW1)

# zlev
vars=(AQVT_TOT AQVT_ADV AQVT_ZADV AQVT_TURB AQVT_MIC)
vars=(CW QI QC)
vars=(U V QV QC QR QI QS W T P)

# calc
vars=(FQVy EQPOTT FQVZ FQVY RH RHO)
vars=(WVP_0_10 WVP_0_2 WVP_0_4 WVP_2_4 WVP_4_10)
vars=(LWP_0_10 LWP_0_2 LWP_2_4 LWP_4_10)

# mlev
vars=(TOT_PREC U_10M V_10M)
vars=(PS T_S)

# selection
vars=(PS T_S)

#var_grp=zlev
#var_grp=calc
var_grp=mlev

for var in "${vars[@]}"; do
    #var=AQVT_TOT
    echo $var

    for model in "${models[@]}"; do
        echo $model
        mkdir -p $dest/$model
        rm $dest/$model/z${var}.nc
        if [ $var_grp == zlev ]; then
            ncrcat -v $var $source/$model/zlev/lffd*z.nc $dest/$model/z${var}.nc
        elif [ $var_grp == calc ]; then
            for file in $source/$model/calc/${var}/lffd*z.nc; do
                ncks -O --mk_rec_dmn time $file $file
            done
            ncrcat -v $var $source/$model/calc/${var}/lffd*z.nc $dest/$model/z${var}.nc
        elif [ $var_grp == mlev ]; then
            ncrcat -v $var $source_mlev/$model/mlev/lffd*.nc $dest/$model/n${var}.nc
        fi
    done
done



