#!/bin/bash

#nczip=/home/heimc/package/my_nczip
nczip=/home/heimc/package/nczip
compression=-1
directory=RAW1


for file in $directory/*;
do 
    echo "$file";
    $nczip $compression "$file"
done
