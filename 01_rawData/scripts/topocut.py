import os, sys
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import multiprocessing as mp

ress = ['4.4', '2.2', '1.1']
ress = ['2.2']
ress = ['1.1']

modes = ['', 'f']
modes = ['']
modes = ['f']

path = '../topocut'


def set_topography_to_nan(file, res, mode, path, mask):
    print(file)
    filePath = str(path+'/'+res+mode+'/'+file)
    #print(filePath)

    ncFile = Dataset(filePath, 'a')
    varKeys = list(ncFile.variables.keys())

    # FIND ALL VARIABLES THAT CONTAIN altitude DIMENSION 
    varNames = []
    for key in varKeys:
        if ('altitude' in ncFile[key].dimensions) & (key != 'altitude'):
            varNames.append(key)

    # LOOP THROUGH ALL VARIABLES
    #varNames = ['AQVT_ADV']
    for varName in varNames:
        #print(varName)
        vals = ncFile[varName][:,0:45,:,:]
        vals = np.ma.masked_where(mask == 0,vals)
        #vals = np.ma.set_fill_value(vals,-999)

        #aI = 5
        #plt.contourf(vals[0,aI,:,:].squeeze())
        #plt.colorbar()
        #plt.show()
        #print(vals[0,aI,100:110,100:110])

        ncFile[varName][:,0:45,:,:] = vals

    ncFile.close()






if len(sys.argv) > 1:
    njobs = int(sys.argv[1])
    print('number of jobs is ' + str(njobs))
else:
    print('Number of Jobs not given. Assume 1')
    njobs = 1


for res in ress:
    #res = '4.4'
    #print(res)
    for mode in modes:
        #mode = ''
        print('########### '+res+mode+' ###########')

        # LOAD TOPO DATASET
        topoPath = str('../HSURF/'+res+mode+'.nc')
        ncFile = Dataset(topoPath, 'r')
        topo = ncFile['HSURF'][:].squeeze()
        ncFile.close()
        altitudes = np.append(np.arange(0,6000,100), np.arange(6000,10001,1000))
        # CREATE MASK FOR CURRENT TOPO DATASET (time,altitude,rlat/srlat,rlon/srlon)
        shapeMask = (1,45,)+topo.shape
        mask = np.zeros(shapeMask)

        altInds = range(0,45) # no mountains at higher levels
        for aI in altInds:
            #aI = 35
            alt = altitudes[aI] 
            mask[0,aI,:,:] = topo < alt # 1 where values should NOT be masked


        files = os.listdir(path+'/'+res+mode)

        #files = files[:120]
        files = files[-120:]


        if njobs > 1:
            pool = mp.Pool(processes=njobs)
            input = [ (file, res, mode, path, mask ) for file in files]
            result = pool.starmap(set_topography_to_nan, input)

        else:
            for file in files:
                set_topography_to_nan(file, res, mode, path, mask)






