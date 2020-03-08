import os, sys
import ncClasses.ncField as ncField
from ncClasses.subdomains import setSSI
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
import multiprocessing as mp
os.chdir('00_newScripts/')


models = ['RAW1', 'SM1']
i_subdomain = 1
#var = 'FQV'
#var = 'FQVx'
var = 'FQVy'

ssI, domainName = setSSI(i_subdomain, {'4.4':{}, '2.2':{}, '1.1':{}}) 

dt0 = datetime(2006,7,11,0)
#dt1 = datetime(2006,7,20,1)
dt1 = datetime(2006,7,13,0)
dts = np.arange(dt0,dt1,timedelta(hours=1))
inpPath = '../01_rawData/topocut/'

if len(sys.argv) > 1:
    njobs = int(sys.argv[1])
    print('number of jobs is ' + str(njobs))
else:
    print('Number of Jobs not given. Assume 1')
    njobs = 1


def calc_wqv(ncFileName, dt):
    print(ncFileName)
    out = {}
    for model in models:
        print('\t'+model)
        srcNCPath = inpPath + model + '/zlev/' + ncFileName

        ncf = ncField.ncField('QV', srcNCPath, ssI)
        ncf.loadValues()
        qv = ncf.vals[0,20,:,:]
        WQVncf = ncf.copy() 
        WQVncf.fieldName = var

        #ncf = ncField.ncField('RHO', srcNCPath, ssI)
        #ncf.loadValues()
        #rho = ncf.vals
        
        ncf = ncField.ncField('W', srcNCPath, ssI)
        ncf.loadValues()
        w = ncf.vals[0,20,:,:]

        wqv = w*qv
        wqv = wqv.mean()
        #wqv = rho*w*qv

        #WQVncf.vals = wqv
        #WQVncf.addVarToExistingNC(srcNCPath)
        out[model] = wqv
        out['time'] = dt

    return(out)


wqv = {}
for model in models:
    wqv[model] = []
time = []

if njobs > 1:
    pool = mp.Pool(processes=njobs)
    input = [ ( 'lffd{0:%Y%m%d%H}z.nc'.format(dts[c].astype(datetime)), \
              dts[c], ) for c in range(0,len(dts))]
    results = pool.starmap(calc_wqv, input)
    for result in results:
        for model in models:
            wqv[model].append(result[model])
        time.append(result['time'])

else:
    for i in range(0,len(dts)):
        ncFileName = 'lffd{0:%Y%m%d%H}z.nc'.format(dts[i].astype(datetime))
        out = calc_wqv(ncFileName, dts[i])
        for model in models:
            wqv[model].append(out[model])
        time.append(out['time'])


handles = []
for model in models:
    handle, = plt.plot(time, wqv[model], label=model)
    handles.append(handle)

plt.legend(handles=handles)
plt.show()
