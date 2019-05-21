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
#models=['RAW4', 'SM4']
#models=['RAW2', 'SM2']
#models=['RAW2', 'SM2' ,'RAW1', 'SM1']
#models=['SM1']

#####################################################################		
dx = {'RAW4':4.4, 'SM4':4.4,
        'RAW2':2.2, 'SM2':2.2,
        'RAW1':1.1, 'SM1':1.1,}

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
            nco.loadAsDiurnal('SUM')
        else:
            nco.loadAsDiurnal('MEAN')
        # SAVE FILE
        if os.path.exists(outFilePath):
            os.remove(outFilePath)
        nco.saveToNewNC(outFilePath)

