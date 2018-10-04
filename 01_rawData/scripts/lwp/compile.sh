#!/bin/bash

ftn -o lwp lwp.f90 `/opt/cray/pe/netcdf/4.4.1.1.3/bin/nf-config --fflags --flibs`
