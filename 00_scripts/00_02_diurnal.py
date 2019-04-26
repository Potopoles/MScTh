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

i_resolution = 1

if len(sys.argv) > 1:
    fieldNames = [sys.argv[1]]
    print('fieldName is ' + str(fieldNames))
else:
    print('No fieldName argument given')
    print('exit')
    quit()


#####################################################################		
if i_resolution == 1:
    ress = ['4.4']
elif i_resolution == 2:
    ress = ['4.4', '2.2']
elif i_resolution == 3:
    ress = ['4.4','2.2','1.1']
elif i_resolution == 4:
    ress = ['2.2']
elif i_resolution == 5:
    ress = ['1.1']
modes = ['', 'f']
#modes = ['r']


for fieldName in fieldNames:
    print(fieldName)
    for res in ress:
        for mode in modes:
            print(str(res) + mode)

            varName = fieldName[1:]

            inpFilePath = inpPath + '/' + res+mode + '/' + fieldName + '.nc'
            outFilePath = outPath + '/' + res+mode + '/' + fieldName + '.nc'

            nco = ncObject.ncObject(inpFilePath, res, fieldName[1:])        
            print('Object generated')
            #quit()
            #nco.selField(varName)
            if fieldName in 'nTOT_PREC':
                nco.loadAsDiurnal('SUM')
            else:
                nco.loadAsDiurnal('MEAN')
            # SAVE FILE
            if os.path.exists(outFilePath):
                os.remove(outFilePath)
            nco.saveToNewNC(outFilePath)

