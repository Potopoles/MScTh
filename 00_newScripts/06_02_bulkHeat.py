import os
import ncClasses.ncField as ncField
from ncClasses.subdomains import setSSI
from datetime import datetime, timedelta
import numpy as np
os.chdir('00_newScripts/')
import matplotlib.pyplot as plt

#from functions import unstaggerZ_1D, unstaggerZ_4D, saveObj 
from functions import saveObj 

ress = ['4.4', '2.2', '1.1']
#ress = ['4.4', '2.2']
modes = ['', 'f']
#modes = ['f']
i_subdomain = 2
i_variables = 'QV' # 'QV' or 'T'
#i_variables = 'T' # 'QV' or 'T'
ssI, domainName = setSSI(i_subdomain, {'4.4':{}, '2.2':{}, '1.1':{}}) 
altInds = list(range(25,61))
altInds = list(range(0,26))
altInds = list(range(0,21))
altInds = list(range(30,62))
#altInds = list(range(0,41))
#altInds = list(range(0,15))
#altInds = list(range(0,21))
print(altInds)
ssI['4.4']['altitude'] = altInds 
ssI['2.2']['altitude'] = altInds 
ssI['1.1']['altitude'] = altInds 

# Altitude arrays
altI = np.asarray(altInds)
alts = np.asarray(altInds)
alts[altI <= 60] = altI[altI <= 60]*100
alts[altI > 60] = (altI[altI > 60] - 60)*1000 + 6000
dz = np.diff(alts)
#altsu = unstaggerZ_1D(alts)

nameString = 'alts_'+str(alts[0])+'_'+str(alts[-1])+'_'+domainName
folder = '../06_bulk' +'/' + nameString
if not os.path.exists(folder):
    os.mkdir(folder)

dt0 = datetime(2006,7,11,0)
#dt0 = datetime(2006,7,12,0)
dt1 = datetime(2006,7,20,0)
#dt1 = datetime(2006,7,13,0)
dts = np.arange(dt0,dt1,timedelta(hours=1))
inpPath = '../01_rawData/topocut/'

if i_variables == 'QV': 
    vars = ['AQVT_TOT', 'AQVT_ADV', 'AQVT_HADV', 'AQVT_ZADV', 'AQVT_TURB', 'AQVT_MIC'] 
    #vars = ['AQVT_TOT', 'AQVT_ADV', 'AQVT_TURB', 'AQVT_MIC'] 
    #vars = ['AQVT_ADV', 'AQVT_HADV', 'AQVT_ZADV', 'AQVT_TOT']
    #vars = ['AQVT_TURB']
elif i_variables == 'T':
    vars = ['ATT_TOT', 'ATT_ADV', 'ATT_HADV', 'ATT_ZADV', 'ATT_RAD', 'ATT_TURB', 'ATT_MIC'] 

print('#########################')
print(nameString)
print(i_variables)
print('#########################')
for res in ress:
    dx = float(res)*1000
    A = np.power(dx,2)
    for mode in modes:
        print('###### '+res+mode+' ######')

        # MODEL SPECIFIC OUTPUT
        out = {}
        for var in vars:
            out[var] = np.full(len(dts), np.nan)
        out['Mtot'] = np.full(len(dts), np.nan)
        out['time'] = dts
        out['alts'] = alts
        #out['altsu'] = altsu
        out['domainName'] = domainName

        for tCount in range(0,len(dts)):
            ncFileName = 'lffd{0:%Y%m%d%H}z.nc'.format(dts[tCount].astype(datetime))
            if tCount % 24 == 0:
                print('\t\t'+ncFileName)
            #print('\t\t'+ncFileName)

            srcNCPath = inpPath + res + mode + '/' + ncFileName

            RHOncf = ncField.ncField('RHO', srcNCPath, ssI[res])
            RHOncf.loadValues()
            rho = RHOncf.vals

            # CALCULATE TENDENCIES
            Mtot = np.nansum(rho*100*A)
            for var in vars:
                NCF = ncField.ncField(var, srcNCPath, ssI[res])
                NCF.loadValues()
                vals = NCF.vals
                out[var][tCount] = np.nansum(vals*rho*100*A)/Mtot

        if i_variables == 'QV': 
            name = 'AQVT_'+res+mode
        elif i_variables == 'T':
            name = 'ATT_'+res+mode
        print(folder)
        print(name)
        saveObj(out,folder,name)  

