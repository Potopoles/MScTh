import os, sys, time
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import multiprocessing as mp




def set_topography_to_nan(file, model, path, mask):
    print(file)
    filePath = str(path+'/'+model+'/'+file)
    ncFile = Dataset(filePath, 'a')
    varKeys = list(ncFile.variables.keys())

    # FIND ALL VARIABLES THAT CONTAIN altitude DIMENSION 
    varNames = []
    for key in varKeys:
        if ('altitude' in ncFile[key].dimensions) & (key != 'altitude'):
            varNames.append(key)

    # LOOP THROUGH ALL VARIABLES
    for varName in varNames:
        var = ncFile[varName]
        var.setncattr('missing_value',fill_value)

        # only look at values below 4.5 km because topo is not higher
        # than that.
        vals = var[:,0:45,:,:]
        vals = np.ma.masked_where(mask == 0,vals)
        np.ma.set_fill_value(vals,fill_value)

        ncFile[varName][:,0:45,:,:] = vals

    ncFile.close()





if __name__ == '__main__':

    t00 = time.time()

    if len(sys.argv) > 1:
        njobs = int(sys.argv[1])
        print('number of jobs is ' + str(njobs))
    else:
        print('Number of Jobs not given. Assume 1')
        njobs = 1

    path = '../topocut'
    fill_value = -999999.0

    models = ['RAW4']
    models = ['SM4']

    file_subsel_inds = None
    #file_subsel_inds = slice(0,1)


    for model in models:
        print('########### '+model+' ###########')
        t0 = time.time()

        # LOAD TOPO DATASET
        topoPath = str('../HSURF/'+model+'.nc')
        ncFile = Dataset(topoPath, 'r')
        topo = ncFile['HSURF'][:].squeeze()
        ncFile.close()
        altitudes = np.append(np.arange(0,6000,100),
                            np.arange(6000,10001,1000))
        # CREATE MASK FOR CURRENT TOPO DATASET \
        #   (time,altitude,rlat/srlat,rlon/srlon)
        shapeMask = (1,45,)+topo.shape
        mask = np.zeros(shapeMask)

        altInds = range(0,45) # no mountains at higher levels
        for aI in altInds:
            #aI = 35
            alt = altitudes[aI] 
            mask[0,aI,:,:] = topo < alt # 1 where values should NOT be masked


        files = os.listdir(path+'/'+model)
        if file_subsel_inds is not None:
            files = files[file_subsel_inds]


        if njobs > 1:
            pool = mp.Pool(processes=njobs)
            input = [ (file, model, path, mask ) for file in files]
            result = pool.starmap(set_topography_to_nan, input)

        else:
            for file in files:
                set_topography_to_nan(file, model, path, mask)

        print(time.time() - t0)

    print(time.time() - t00)





