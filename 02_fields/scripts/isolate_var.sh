#!/bin/bash

#source=../../01_rawData/lwp
source_obs=../../radar
source_mlev=../../../data/cosmo_out/MScTh
source=../../01_rawData/topocut
dest=../topocut

models=(RAW4 SM4 RAW2 SM2 RAW1 SM1)
#models=(RAW4 SM4 RAW2 SM2)
#models=(SM1 RAW1)
#models=(OBS4 OBS2 OBS1)

# zlev
vars=(AQVT_TOT AQVT_ADV AQVT_ZADV AQVT_TURB AQVT_MIC)
vars=(ATT_TOT ATT_ADV ATT_ZADV ATT_TURB ATT_MIC ATT_RAD)
vars=(CW QI QC, CW)
vars=(U V QV QC QR QI QS W T P)

# calc
vars=(FQVy EQPOTT FQVZ FQVY RH RHO)
vars=(WVP_0_10 WVP_0_2 WVP_0_4 WVP_2_4 WVP_4_10)
vars=(LWP_0_10 LWP_0_2 LWP_2_4 LWP_4_10)

# mlev
vars=(TOT_PREC U_10M V_10M)
vars=(PS T_S)

# obs
vars=(TOT_PREC)

# selection
#vars=(ATT_TOT ATT_ADV ATT_ZADV ATT_TURB ATT_MIC ATT_RAD)
vars=(ATT_MIC ATT_RAD)

var_grp=zlev
#var_grp=calc
#var_grp=mlev
#var_grp=obs

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
        elif [ $var_grp == obs ]; then
            ncrcat -v $var $source_obs/$model/CPCH*.nc $dest/$model/n${var}.nc
        fi
    done
done



