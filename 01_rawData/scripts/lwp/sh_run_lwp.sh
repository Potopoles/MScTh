#!/bin/bash
# run compiled program lwp for selected model resolutions, modes (raw and smoothed), and time steps.

ress=("4.4" "2.2" "1.1")
#ress=("2.2" "1.1")
#ress=("4.4")
modes=("" "f")
#modes=("")

cd ../../topocut/4.4/

# time step files
tsfs=(lffd200607*z.nc)
#tsfs=(lffd20060715*z.nc)
#tsfs=(lffd2006071515z.nc)

cd ../../scripts/lwp
for res in "${ress[@]}";do
    for mode in "${modes[@]}";do
        echo "###########" "$res""$mode" "##########"
        for tsf in "${tsfs[@]}"; do
            echo "                "$tsf
            :
            #echo ../../topocut/"$res""$mode"/"$tsf" ../../lwp/"$res""$mode"/"$tsf"
            ./lwp ../../topocut/"$res""$mode"/"$tsf" ../../lwp/"$res""$mode"/"$tsf"
        done
    done
done
