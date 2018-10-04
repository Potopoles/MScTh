import os
import ncClasses.ncField as ncField
from ncClasses.subdomains import setSSI
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
os.chdir('00_newScripts/')


ress = ['4.4', '2.2', '1.1']
ress = ['2.2', '1.1']
#ress = ['4.4']
modes = ['', 'f']
i_subdomain = 0

ssI, domainName = setSSI(i_subdomain, {'4.4':{}, '2.2':{}, '1.1':{}}) 

dt0 = datetime(2006,7,20,0)
dt0 = datetime(2006,7,11,0)
dt1 = datetime(2006,7,20,1)
dts = np.arange(dt0,dt1,timedelta(hours=1))
inpPath = '../01_rawData/topocut/'

for i in range(0,len(dts)):
    ncFileName = 'lffd{0:%Y%m%d%H}z.nc'.format(dts[i].astype(datetime))
    print(ncFileName)

    for res in ress:
        for mode in modes:
            #print('\t'+res+mode)
            srcNCPath = inpPath + res + mode + '/' + ncFileName

            ncf = ncField.ncField('QV', srcNCPath, ssI)
            ncf.loadValues()
            qv = ncf.vals
            FQVncf = ncf.copy() 
            FQVncf.fieldName = 'FQV'

            ncf = ncField.ncField('RHO', srcNCPath, ssI)
            ncf.loadValues()
            rho = ncf.vals
            
            ncf = ncField.ncField('U', srcNCPath, ssI)
            ncf.loadValues()
            u = ncf.vals

            ncf = ncField.ncField('V', srcNCPath, ssI)
            ncf.loadValues()
            v = ncf.vals

            uv = np.sqrt(np.power(u,2) + np.power(v,2))
            fqv = rho*uv*qv

            FQVncf.vals = fqv
            FQVncf.addVarToExistingNC(srcNCPath)
