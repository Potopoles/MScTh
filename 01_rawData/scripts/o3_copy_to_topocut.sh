#!/bin/bash

inp_folder=/net/o3/hymet_nobackup/heimc/data/cosmo_out/MScTh
sel_str=lffd200607*z.nc
i_overwrite=1

models=(RAW4 SM4)
models=(SM2 RAW1 SM1)
models=(RAW4)

for model in ${models[@]} ;do
    echo $model
    mkdir -p ../topocut/$model

    if [ $i_overwrite == 1 ]; then
        echo 'overwrite'
        rm ../topocut/$model/*
        cp $inp_folder/$model/zlev/$sel_str ../topocut/$model/
        #find $inp_folder/$model/zlev/$sel_str -print0 | parallel -0 -j20 \
        #    cp {} ../topocut/$model/
    else
        echo 'do not overwrite'
        cp -u $inp_folder/$model/zlev/$sel_str ../topocut/$model/
    fi
done

