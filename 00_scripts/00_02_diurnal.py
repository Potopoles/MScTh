#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
title			:diurnal.py
description	    :Calculate mean diurnal cycle for fields.
author			:Christoph Heim
date created    :20171121 
date changed    :20190522
usage			:arg1: Var with type prefix. e.g. nTOT_PREC or zU
notes			:
python_version	:3.7.1
==============================================================================
"""
import os
os.chdir('00_scripts/')

import matplotlib.pyplot as plt


import ncClasses.ncObject as ncObject
from datetime import datetime
from functions import *
import os, sys
####################### NAMELIST INPUTS FILES #######################
# directory of input model folders
inpPath = '../02_fields/topocut'
outPath = '../02_fields/diurnal'

if len(sys.argv) > 1:
    fieldNames = [sys.argv[1]]
    print('fieldName is ' + str(fieldNames))
else:
    print('No fieldName argument given')
    print('exit')
    quit()

models=['RAW4', 'SM4', 'RAW2', 'SM2' ,'RAW1', 'SM1']
#models=['OBS4', 'OBS2', 'OBS1']
models=['RAW1', 'SM1','RAW4', 'SM4', 'RAW2', 'SM2']

#####################################################################		
dx = {'RAW4':4.4, 'SM4':4.4, 'OBS4':4.4,
        'RAW2':2.2, 'SM2':2.2, 'OBS2':2.2,
        'RAW1':1.1, 'SM1':1.1, 'OBS1':1.1,}

for fieldName in fieldNames:
    print(fieldName)
    for model in models:
        print(model)

        varName = fieldName[1:]

        inpFilePath = inpPath + '/' + model + '/' + fieldName + '.nc'
        outFilePath = outPath + '/' + model + '/' + fieldName + '.nc'

        nco = ncObject.ncObject(inpFilePath, dx[model], fieldName[1:])        

        #nco.selField(varName)
        if fieldName in 'nTOT_PREC':
            nco.load_as_diurnal('SUM')
        else:
            nco.load_as_diurnal('MEAN')
        # SAVE FILE
        if os.path.exists(outFilePath):
            os.remove(outFilePath)
        nco.saveToNewNC(outFilePath)

