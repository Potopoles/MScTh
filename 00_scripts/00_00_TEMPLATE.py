#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
title			:TEMPLATE.py
description	    :
author			:Christoph Heim
date created    :20171121 
date changed    :20190612
usage			:no args
notes			:
python_version	:3.7.1
==============================================================================
"""
import os
os.chdir('00_scripts/')

i_resolutions = 5 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 1 # 0 = no plot, 1 = show plot, 2 = save plot
i_info = 2 # output some information [from 0 (off) to 5 (all you can read)]
import matplotlib
if i_plot == 2:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt


import ncClasses.analysis as analysis
from datetime import datetime
from functions import *
from ncClasses.subdomains import setSSI
####################### NAMELIST INPUTS FILES #######################
# directory of input model folders
inpPath = '../02_fields/diurnal'
#inpPath = '../02_fields/topocut'

others = ['cHSURF', 'nTOT_PREC', 'nHPBL']
hydrometeors = ['zQC', 'zQI', 'zQV', 'zQR', 'zQS', 'zQG']
TTendencies = ['zATT_MIC', 'zATT_RAD', 'zATT_ADV', 'zATT_ZADV', 'zATT_TURB', 'zATT_TOT']
QVTendencies = ['zAQVT_MIC', 'zAQVT_ADV', 'zAQVT_ZADV', 'zAQVT_TURB', 'zAQVT_TOT']
dynamics = ['zW', 'zU', 'zV', 'zT', 'zP']
fieldNames = ['zU', 'cHSURF']
fieldNames = ['nTOT_PREC', 'cHSURF']
fieldNames = ['zAQVT_TURB']
fieldNames = ['nASHFL_S']
fieldNames = ['nALHFL_S']
fieldNames = ['cHSURF']
fieldNames = ['zQV']
fieldNames = ['nPMSL']
fieldNames = ['zT']
#fieldNames = ['zATT_TURB']
#####################################################################		

####################### NAMELIST DIMENSIONS #######################
i_subDomain = 1 # 0: full domain, 1: alpine region
ssI, domainName = setSSI(i_subDomain, {'4':{}, '2':{}, '1':{}}) 
#print(ssI)
#quit() ## PROBLEM WITH SUBDOMAIN!!!

startHght = 0
endHght = 30
altInds = list(range(startHght,endHght+1))
ssI['altitude'] = altInds 

#startTime = datetime(2006,7,11,00)
#endTime = datetime(2006,7,20,23)
#ssI['time'] = [startTime,endTime] # border values (one value if only one time step desired)

#ssI['diurnal'] = [19] # list values
#ssI['diurnal'] = [20,21,22,23,0,1,2,3,4,5] # list values

####################### NAMELIST AGGREGATE #######################
# Options: MEAN, SUM 
ag_commnds = {}
ag_commnds['rlat'] = 'MEAN'
ag_commnds['rlon'] = 'MEAN'
#ag_commnds['time'] = 'MEAN'
#ag_commnds['diurnal'] = 'MEAN'
ag_commnds['altitude'] = 'MEAN'
#ag_commnds['time'] = 'MEAN'
#####################################################################

####################### NAMELIST PLOT #######################
nDPlot = 1 # How many dimensions should plot have (1 or 2)
i_diffPlot = 1 # Draw plot showing difference filtered - unfiltered # TODO
plotOutDir = '../00_plots'
#plotOutDir = '../00_plots/04_coldPools/zFQVy'
plotName = 'test.png'
plotName = 'T_diurnal.png'
#plotName = 'zFQVy_'+str(ssI['diurnal'][0])+'.png'
#plotName = 'LHFL.png'
##### 1D PLOT #########

##### 2D Contour ######
contourTranspose = 0 # Reverse contour dimensions?
plotContour = 0 # Besides the filled contour, also plot the contour?
cmapM = 'seismic' # colormap for Model output (jet, terrain, inferno, YlOrRd)
axis = 'auto' # set 'equal' if keep aspect ratio, else 'auto'
# COLORBAR Models
autoTicks = 0 # 1 if colorbar should be set automatically
Mmask = 1 # Mask Model values lower than MThrMinRel of maximum value?
MThrMinRel = 0.02 # Relative amount of max value to mask (see Mmask)
Mticks = [0.0001,0.0002,0.0003,0.0004,0.0005]
Mticks = list(np.arange(-0.1,0.1,0.02))
# COLORBAR Models
cmapD = 'bwr' # colormap for Difference output (bwr)
#####################################################################


an = analysis.analysis(inpPath, fieldNames)

#an.subSpaceInds = subSpaceInds
an.subSpaceInds = ssI
an.ag_commnds = ag_commnds
an.i_info = i_info
an.i_resolutions = i_resolutions

# RUN ANALYSIS
an.run()

#for res in an.resolutions:
#    for mode in an.modes:
#        print(res+mode)
#        topo = an.vars['cHSURF'].ncos[mode+res].field.vals
#        print(topo)
#quit()


import matplotlib
if i_plot == 2:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt

for res in an.resolutions:
    for mode in an.modes:
        print(res+mode)
        nco = an.vars[fieldNames[0]].ncos[mode+res]
        print(np.nanmean(nco.field.vals))
#quit()
#
#quit()

if i_plot > 0:
    if i_info >= 3:
        print('plotting')
    mainVar = an.vars[an.varNames[0]]
    someField = next(iter(mainVar.ncos.values())).field
    if i_info >= 1:
        print('NONSINGLETONS: ' + str(someField.nNoneSingleton))
    
    if nDPlot == 2 and someField.nNoneSingleton == 2:
        import ncPlots.ncSubplots2D as ncSubplots
        ncs = ncSubplots.ncSubplots(an, nDPlot, i_diffPlot, 'HOR')

        ncs.contourTranspose = contourTranspose
        ncs.plotContour = plotContour
        ncs.cmapM = cmapM
        ncs.axis = axis
        ncs.autoTicks = autoTicks
        ncs.Mmask = Mmask
        ncs.MThrMinRel = MThrMinRel
        ncs.Mticks = Mticks
        ncs.cmapD = cmapD
    
        if 'cHSURF' in an.varNames:
            ncs.plotTopo(an.vars['cHSURF'])
        
        ncs.plotVar(an.vars[an.varNames[0]])
            
        title = 'title' 
        ncs.fig.suptitle(title, fontsize=14)

    elif nDPlot == 1 and someField.nNoneSingleton == 1:
        import ncPlots.ncSubplots1D as ncSubplots
        ncs = ncSubplots.ncSubplots(an, nDPlot, i_diffPlot, 'HOR')
    
        for varName in an.varNames:
            if varName != 'cHSURF':
                ncs.plotVar(an.vars[varName])

        title = 'title' 
        #title = 'SHFL' 
        #title = 'LHFL' 
        ncs.fig.suptitle(title, fontsize=14)

    else:
        raise ValueError('ERROR: CANNOT MAKE ' + str(nDPlot) + 'D-PLOT WITH ' +
        str(someField.nNoneSingleton) + ' NON-SINGLETON DIMS!')

    
    if i_plot == 1:
        plt.show()
    elif i_plot == 2:
        plotPath = plotOutDir + '/' + plotName
        plt.savefig(plotPath, format='png', bbox_inches='tight')
        plt.close('all')

          


