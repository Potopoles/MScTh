import os, copy
from ncClasses.subdomains import setSSI
from datetime import datetime, timedelta
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
os.chdir('00_scripts/')

from functions import saveObj 

inp_dir = os.path.join('..','02_fields','diurnal')

models = {
    'RAW1':{
        'name':'RAW1',
        'res':1.1,
    },
}
i_subdomain = 1

ssI, domainName = setSSI(i_subdomain, {'4.4':{}, '2.2':{}, '1.1':{}}) 

i_walls = ['W', 'E', 'N', 'S']
i_walls = ['S']

mm = models['RAW1']

inp_path = os.path.join(inp_dir,mm['name'],'nU_10M.nc') 
U_10M = xr.open_dataset(inp_path).get('U_10M')
print(U_10M.coords['rlat'])
quit()
print(U_10M.isel(rlon=int(ssI['lon0']*4.4/mm['res']),
                rlat=slice(int(ssI['lat0']*4.4/mm['res']),
                            int(ssI['lat1']*4.4/mm['res']))))

