import ncClasses.variable as variable
import ncClasses.ncObject as ncObject
from copy import deepcopy
import numpy as np
from timeit import default_timer as timer
from datetime import datetime, timedelta
#from functions import usedMem
#import sys

# CLASS TO STRUCTURE THE ANALYSIS.
# CONTAINS INSTANCES OF variable.
class analysis:
    from netCDF4 import Dataset

    def __init__(self, inpPath, varNames, use_obs=False):
        self.inpPath = inpPath
        self.varNames = varNames

        # NAMES and Types OF THE NC FILES
        # (example: inpFileNames: 'zW.nc' and fileType: 'z')
        self.inpFileNames, self.fileTypes = self._getInpFileNames(
                                            self.varNames)

        if use_obs:
            self.modes = ['SM', 'RAW', 'OBS'] # '' = raw, 'f' = filtered
            self.modeNames = ['SM', 'RAW', 'OBS']
            #self.modes = ['RAW'] # '' = raw, 'f' = filtered
            #self.modeNames = ['RAW']
        else:
            self.modes = ['SM', 'RAW'] # '' = raw, 'f' = filtered
            self.modeNames = ['SM', 'RAW']
        
        # CREATE VARIABLE INSTANCES
        self.vars = {}
        for vN in self.varNames:
            var = variable.variable(vN)	
            self.vars[vN] = var
            self.vars[vN].label = vN[1:]

    def set_resolutions(self):
        self.grid_spacings = {'4':4400,'2':2200,'1':1100}
        if self.i_resolutions == 1:
            self.resolutions = ['4']
        elif self.i_resolutions == 2:
            self.resolutions = ['4', '2']
        elif self.i_resolutions == 3:
            self.resolutions = ['4', '2', '1']
        elif self.i_resolutions == 4:
            self.resolutions = ['2']
        elif self.i_resolutions == 5:
            self.resolutions = ['1']
        else:
            print('NO VALID RESOLUTION CODE')
        

    def run(self):
        self.set_resolutions()
        
        # CREATE KEYS OF ALL ncObjects TO CREATE FOR EACH VARIABLE.
        self.ncoKeys = []
        self.dxs = []
        for res in self.resolutions:
            for mode in self.modes:
                self.ncoKeys.append(mode+res)
                self.dxs.append(float(res))

        # LOOP THROUGH VARIABLE NAMES TO FILL variables WITH ncObjects
        for i,vN in enumerate(self.varNames):
            starttimeVar = timer()
            
            if self.i_info >= 1:
                print(vN)
                
            ## LOOP THROUGH ncoKeys TO CREATE ncObjects
            for j,ncoKey in enumerate(self.ncoKeys):
                
                if self.i_info >= 2:
                    print('\t'+ncoKey)
                
                # LOAD ncObject
                if self.i_info >= 3:
                    print('\t\tload models')

                # TODO quick fix
                #if ncoKey in ['SM1', 'RAW1']:
                #    #inpFilePath = self.inpPath + '/' + ncoKey+'_1' + '/' + self.inpFileNames[i]
                #    #inpFilePath = self.inpPath + '/' + ncoKey+'_2' + '/' + self.inpFileNames[i]
                #    inpFilePath = self.inpPath + '/' + ncoKey+'_3' + '/' + self.inpFileNames[i]
                #else:
                #    inpFilePath = self.inpPath + '/' + ncoKey + '/' + self.inpFileNames[i]
                # TODO old version
                inpFilePath = self.inpPath + '/' + ncoKey + '/' + self.inpFileNames[i]
                name = ncoKey
                self.vars[vN].ncos[ncoKey] = ncObject.ncObject(inpFilePath,
                                                self.dxs[j], fieldName=vN[1:])
                nco = self.vars[vN].ncos[ncoKey]

                if self.i_info >= 3:
                    print('\t\tdim subspace')
                nco.subSpaceInds = self._setSubspaceInds(
                                            self.subSpaceInds, self.dxs[j])
                nco.cutDimsToSubSpace() 

                # AGGREGATE
                if self.i_info >= 3:
                    print('\t\taggregate')
                nco.prepareAggregate(self.ag_commnds)
        
                # LOAD FIELDS
                if self.i_info >= 3:
                    print('\t\tload fields')
                nco.loadValuesOfField()

        if self.i_info >= 1:
            endtimeVar = timer()
            print('#######################################################')
            print('elapsed time:\t\t\t\t\t' + str(np.round(endtimeVar - starttimeVar)) + ' s')
            
    def getNCOsOfVar(self, varName=None):
        """For given variable with name 'varName' returns a list of all ncObjects
           If varName is not given will return ncos for first variable.
           Also returns the varName"""
        # SELECT VARIABLE NAME
        if varName is None:
            vN = self.varNames[0]
        else:
            vN = varName
        # FIND NCOS
        ncos = []
        for key,nco in self.vars[vN].ncos.items():
            ncos.append(nco)
        return(ncos, vN)
             

    def prepareForPlotting(self):
        """Runs all the necessary things to make fields of ncObjects ready for plotting"""
        for varName in self.varNames:
            ncos, varName = self.getNCOsOfVar(varName)
            for nco in ncos:
                nco.field.prepareForPlotting()
            self.vars[varName].setValueLimits()
            
        
    def _setSubspaceInds(self, subSpaceIndsIN, dx):
        """For each dimension given in subSpaceIndsIN passes the
            information on to the modelRes object"""	

        # MAKE SURE THAT THIS VARIABLE HAS ITS OWN SUBSPACEINDS OBJECT
        subSpaceInds = deepcopy(subSpaceIndsIN)

        # LON AND LAT
        fact = int(4.4/dx)
        for key in ['rlon','rlat', 'x_1', 'y_1']:
            if key in subSpaceInds:
                if not isinstance(subSpaceInds[key], list):
                    raise TypeError('subSpaceInds of key "' + key +
                                        '" must be a list!')
                if len(subSpaceInds[key]) not in [1,2]:
                    raise ValueError('subSpaceInds of key "' + key +
                                        '" must have length 1 or 2!')
                subSpaceInds[key] = [x * fact for x in subSpaceInds[key]]
                if len(subSpaceInds[key]) == 2:
                    subSpaceInds[key] = list(range(subSpaceInds[key][0],
                                            subSpaceInds[key][1]+1))


        
        # TIME
        if 'time' in subSpaceInds:
            if not isinstance(subSpaceInds['time'], list):
                raise TypeError('subSpaceInds of key "time" must be a list ' +
                'giving the start and the end datetime of the time window!')
            if not isinstance(subSpaceInds['time'][0], datetime):
                raise TypeError('Elements of subSpaceInds with key "time" must be datetime!')

            dt0 = datetime(2006,7,11,00)
            timeInds = []
            # CREATE DATETIME SERIES
            if len(subSpaceInds['time']) > 1:
                if subSpaceInds['time'][1] == subSpaceInds['time'][0]:
                    raise ValueError('Time input border elements are identical. If you want to use one '+
                                    'time step only then only insert one time!')
                from datetime import timedelta
                now = subSpaceInds['time'][0]
                last = subSpaceInds['time'][1]
                times = []
                while now < last:
                    times.append(now)
                    now += timedelta(hours=1)
                subSpaceInds['time'] = times
                    
            for time in subSpaceInds['time']:
                dDay = (time - dt0).days
                dSec = (time - dt0).seconds
                dHr = dDay*24 + dSec/3600
                timeInds.append(int(dHr))
            subSpaceInds['time'] = timeInds

        # DIURNAL
        if 'diurnal' in subSpaceInds:
            if not isinstance(subSpaceInds['diurnal'], list):
                raise TypeError('subSpaceInds of key "diurnal" must be a list!')
        # ALTITUDE, nothing necessary
        if 'altitude' in subSpaceInds:
            if not isinstance(subSpaceInds['altitude'], list):
                raise TypeError('subSpaceInds of key "altitude" must be a list!')
        
        return(subSpaceInds)
        

                    
    def _getInpFileNames(self, fieldNames):
        inpFileNames = []
        fileTypes = []
        for fldName in fieldNames:
            fileTypes.append(fldName[0])
            inpFileNames.append(fldName + '.nc')
        return(inpFileNames, fileTypes)
        
        
        
