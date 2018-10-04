#!/bin/bash

ftn -O3 -c -o clustering_cray.o clustering_nonperiodic.f90
ftn -target-network=none -O3 -o cloud_cluster cloud_cluster.f90 clustering_cray.o `/opt/cray/pe/netcdf/4.4.1.1.3/bin/nf-config --fflags --flibs`
