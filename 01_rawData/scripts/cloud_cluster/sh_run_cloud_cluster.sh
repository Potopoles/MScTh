#!/bin/bash
# run compiled program cloud_cluster for selected model resolutions, modes (raw and smoothed), and time steps.

ress=("4.4" "2.2" "1.1")
#ress=("2.2" "1.1")
#ress=("4.4")
modes=("" "f")
#modes=("")

cd ../../lwp/4.4/

# time step files
tsfs=(lffd200607*z.nc)
#tsfs=(lffd20060715*z.nc)
#tsfs=(lffd2006071515z.nc)

cd ../../scripts/cloud_cluster
for res in "${ress[@]}";do
    for mode in "${modes[@]}";do
        echo "###########" "$res""$mode" "##########"
        for tsf in "${tsfs[@]}"; do
            echo "                  "$tsf
            :

            #echo ../../lwp/"$res""$mode"/"$tsf" ../../cloud_cluster/"$res""$mode"/"$tsf"
            ./cloud_cluster ../../lwp/"$res""$mode"/"$tsf" ../../cloud_cluster/"$res""$mode"/"$tsf" "$res"
        done
    done
done
