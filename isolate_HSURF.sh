#!/bin/bash


res=${1}

# isolate HSURF

ncrcat -v HSURF /project/pr04/heimc/initial_data/wl_${res}_km_filtered/4_lm_f/output/mlev/lffd2006071100c.nc ${res}/cHSURF.nc

ncrcat -v HSURF /project/pr04/heimc/initial_data/wl_${res}_km/4_lm_f/output/mlev/lffd2006071100c.nc ${res}/cHSURF.nc
