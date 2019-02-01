#!/bin/bash

module load cdo

var=AQVT_HADV
file=lffd2006071312z.nc
res=4.4
mode=''

cdo delete,name=$var $res$mode/$file $res$mode/'out.nc'
mv $res$mode/'out.nc' $res$mode/$file
