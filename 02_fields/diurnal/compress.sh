#!/bin/bash

nczip=/home/heimc/package/my_nczip
compression=-1
#directory=RAW1
directory=SM4


for file in $directory/*;
do 
    echo "$file";
    $nczip $compression "$file"
done
