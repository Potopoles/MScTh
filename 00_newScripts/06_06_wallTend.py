import os
import copy
import ncClasses.ncField as ncField
from ncClasses.subdomains import setSSI
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
os.chdir('00_newScripts/')

from functions import saveObj 

i_save = 1

ress = ['4', '2', '1']
#ress = ['4', '2']
#ress = ['4']
#ress = ['2']
#ress = ['1']
modes = ['RAW', 'SM']
#modes = ['f']
i_subdomain = 1
altInds = list(range(0,26))
#i_subdomain = 2
#i_subdomain = 22
#altInds = list(range(0,21))
#altInds = list(range(0,16))
#altInds = list(range(20,61))
#i_subdomain = 11
#altInds = list(range(0,26))
##altInds = list(range(15,31))
i_variables = 'Fqv'
ssI, domainName = setSSI(i_subdomain, {'4.4':{}, '2.2':{}, '1.1':{}}) 
ssI['4.4']['altitude'] = altInds 
ssI['2.2']['altitude'] = altInds 
ssI['1.1']['altitude'] = altInds 

ssI['4'] = ssI['4.4']
ssI['2'] = ssI['2.2']
ssI['1'] = ssI['1.1']
#ssIRaw = copy.deepcopy(ssI)

dxs = {'4':4.4, '2':2.2, '1':1.1}

i_walls = ['E', 'W', 'N', 'S', 'bottom', 'top']
i_walls = ['E']
i_walls = ['W']
i_walls = ['S']
i_walls = ['N']

dt0 = datetime(2006,7,11,0)
#dt0 = datetime(2006,7,12,0)
dt1 = datetime(2006,7,20,0)
#dt1 = datetime(2006,7,12,0)


ssIRaw = ssI
for i_wall in i_walls:
    print('########################## ' + i_wall + ' ###########################')
    #i_wall = 'left'
    ssI = copy.deepcopy(ssIRaw)

    if i_wall == 'E':
        for res in ress:
            ssI[res]['rlon'] = [ssIRaw[res]['rlon'][0]]
            ssI[res]['srlon'] = [ssIRaw[res]['srlon'][0]]
        normVec = 1
    elif i_wall == 'W':
        for res in ress:
            ssI[res]['rlon'] = [ssIRaw[res]['rlon'][-1]]
            ssI[res]['srlon'] = [ssIRaw[res]['srlon'][-1]]
        normVec = -1
    elif i_wall == 'S':
        for res in ress:
            ssI[res]['rlat'] = [ssIRaw[res]['rlat'][0]]
            ssI[res]['srlat'] = [ssIRaw[res]['srlat'][0]]
        normVec = 1
    elif i_wall == 'N':
        for res in ress:
            ssI[res]['rlat'] = [ssIRaw[res]['rlat'][-1]]
            ssI[res]['srlat'] = [ssIRaw[res]['srlat'][-1]]
        normVec = -1
    elif i_wall == 'bottom':
        normVec = 1
    elif i_wall == 'top':
        normVec = -1

    #quit()

    # Altitude arrays
    altI = np.asarray(altInds)
    alts = np.asarray(altInds)
    alts[altI <= 60] = altI[altI <= 60]*100
    alts[altI > 60] = (altI[altI > 60] - 60)*1000 + 6000

    nameString = 'alts_'+str(alts[0])+'_'+str(alts[-1])+'_'+domainName
    folder = '../06_bulk/vertSlab' +'/' + nameString
    if not os.path.exists(folder):
        os.mkdir(folder)

    dts = np.arange(dt0,dt1,timedelta(hours=1))
    inpPath = '../01_rawData/topocut/'


    for res in ress:
        #dx = float(res)*1000
        dx = float(dxs[res])*1000
        for mode in modes:
            print('###### '+res+mode+' ######')

            # MODEL SPECIFIC OUTPUT
            out = {}
            out['Fqv'] = np.full(len(dts), np.nan)
            out['Mtot'] = np.full(len(dts), np.nan)
            out['time'] = dts
            out['alts'] = alts
            out['ssI'] = ssIRaw[res]

            nlon = len(ssIRaw[res]['rlon'])
            nlat = len(ssIRaw[res]['rlat'])
            Area = nlon * nlat * float(res)**2
            print('Area is: ' + str(round(Area,0)) + ' km**2')
            out['Area'] = Area
            out['domainName'] = domainName

            for tCount in range(0,len(dts)):
                ncFileName = 'lffd{0:%Y%m%d%H}z.nc'.format(dts[tCount].astype(datetime))
                if tCount % 1 == 0:
                    print('\t\t'+ncFileName)

                calc_src_path = inpPath + mode+ res+ '/calc/'

                #RHOncf = ncField.ncField('RHO', srcNCPath, ssI[res])
                #RHOncf.loadValues()
                #rho = RHOncf.vals
                #rhou = unstaggerZ_4D(rho)
                if i_wall in ['E', 'W']:
                    ncf = ncField.ncField('FQVX', os.path.join(calc_src_path, 'FQVX',
                                          ncFileName), ssI[res])
                elif i_wall in ['S', 'N']:
                    ncf = ncField.ncField('FQVY', os.path.join(calc_src_path, 'FQVY',
                                          ncFileName), ssI[res])
                elif i_wall in ['bottom', 'top']:
                    ncf = ncField.ncField('FQVZ', os.path.join(calc_src_path, 'FQVZ',
                                          ncFileName), ssI[res])
                ncf.loadValues()

                if i_wall in ['E', 'W', 'S', 'N']:
                    flx = ncf.vals * dx * 100 * normVec
                elif i_wall in ['bottom', 'top']:
                    flx = ncf.vals * dx**2 * normVec

                flx_sum = np.nansum(flx)
                out['Fqv'][tCount] = flx_sum

            
            name = 'Fqv_'+i_wall+'_'+res+mode
            print(name)
            print(folder)
            if i_save:
                saveObj(out,folder,name)  

