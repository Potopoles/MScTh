#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
title			:orig: 04_08_precipSum_PUB.py
description	    :Plot accumulated daytime and nighttime precipitation map.
author			:Christoph Heim
date created    :22.11.2017
date changed    :07.06.2019
usage			:no args
notes			:
python_version	:3.7.1
==============================================================================
"""
import os, copy
os.chdir('00_scripts/')

i_resolutions = 3 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 2 # 0 = no plot, 1 = show plot, 2 = save plot
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
#inpPath = '../02_fields/subDomDiur'
inpPath = '../02_fields/diurnal'
#inpPath = '../02_fields/topocut'

fieldNames = ['nTOT_PREC', 'cHSURF']
#####################################################################		

####################### NAMELIST DIMENSIONS #######################
i_subDomain = 1 # 0: full domain, 1: alpine region
ssI, domainName = setSSI(i_subDomain, {'4':{}, '2':{}, '1':{}}) 

ssI['diurnal'] = [20,21,22,23,0,1,2,3,4,5,6,7] # list values
ssI['diurnal'] = [8,9,10,11,12,13,14,15,16,17,18,19] # list values

#ssI['diurnal'] = [12,13,14,15,16,17] # list values
#ssI['diurnal'] = [18,19,20,21,22,23] # list values
#ssI['diurnal'] = [0 ,1 ,2 ,3 ,4 ,5 ] # list values
#ssI['diurnal'] = [6 ,7 ,8 ,9 ,10,11] # list values

####################### NAMELIST AGGREGATE #######################
# Options: MEAN, SUM 
ag_commnds = {}
#ag_commnds['rlat'] = 'MEAN'
#ag_commnds['rlon'] = 'MEAN'
#ag_commnds['time'] = 'SUM'
ag_commnds['diurnal'] = 'SUM'
#ag_commnds['altitude'] = 'MEAN'
#####################################################################

####################### NAMELIST PLOT #######################
nDPlot = 2 # How many dimensions should plot have (1 or 2)
i_diffPlot = 0 # Draw plot showing difference filtered - unfiltered # TODO
plotOutDir = '../00_plots/04_coldPools'
#plotName = 'Accum_Precip_'+str(ssI['diurnal'][0])+'-'+str(ssI['diurnal'][-1]+1)+'_ens2'
plotName = 'Accum_Precip_'+str(ssI['diurnal'][0])+'-'+str(ssI['diurnal'][-1]+1)
##### 1D PLOT #########

##### 2D Contour ######
contourTranspose = 0 # Reverse contour dimensions?
plotContour = 0 # Besides the filled contour, also plot the contour?
cmapM = 'jet' # colormap for Model output (jet, terrain, inferno, YlOrRd)
axis = 'equal' # set 'equal' if keep aspect ratio, else 'auto'
# COLORBAR Models
autoTicks = 0 # 1 if colorbar should be set automatically
Mmask = 1 # Mask Model values lower than MThrMinRel of maximum value?
MThrMinRel = 0.02 # Relative amount of max value to mask (see Mmask)
Mticks = list(np.arange(10,125,10))
# COLORBAR Models
cmapD = 'bwr' # colormap for Difference output (bwr)
#####################################################################


an = analysis.analysis(inpPath, fieldNames, use_obs=True)

#an.subSpaceInds = subSpaceInds
an.subSpaceInds = ssI
an.ag_commnds = ag_commnds
an.i_info = i_info
an.i_resolutions = i_resolutions

# RUN ANALYSIS
an.run()
print(an.vars['nTOT_PREC'].ncos['RAW1'].field.vals.shape)
#quit()


import matplotlib
if i_plot == 2:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt


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
        
        (fig,axes,MCB) = ncs.plotVar(an.vars[an.varNames[0]])

        MCB.set_label(r'Total Accumulated Precipitation $[mm]$', fontsize=19*ncs.MAG)


        # ADD OBSERVATIONS
        old_size = fig.get_size_inches()
        new_size = [old_size[0]*1.31, old_size[1]*1.00]
        fig.set_size_inches(new_size)
        fig.subplots_adjust(right=0.71, wspace=0.15, hspace=0.4,
                            bottom=0.23)
        ncs.cax.set_position(pos=[0.10, 0.08, 0.58, 0.03])

        width, height = axes[0,0].get_position().bounds[2:4]
        ax = fig.add_axes([0.74, 0.42, width, height])
        ax.set_xlabel('x [$km$]', fontsize=ncs.MAG*19)
        ax.set_title('OBS', fontsize=ncs.MAG*22)


        fld = an.vars['nTOT_PREC'].ncos['OBS1'].field
        vals = copy.deepcopy(fld.vals).squeeze()
        vals[vals > ncs.levels[-1]] = ncs.levels[-1]
        dims = fld.noneSingletonDims			
        dimx, dimy, fld = ncs._prepareDimAndFields(dims, fld)

        pan_lab_x = dimx.vals[0] - (dimx.vals[-1] - dimx.vals[0]) * 0.00
        pan_lab_y = dimy.vals[0] + (dimy.vals[-1] - dimy.vals[0]) * 1.07
        ax.text(pan_lab_x,pan_lab_y,'g)', fontsize=15, weight='bold')


        topo = an.vars['cHSURF'].ncos['RAW1'].field
        topo.vals[np.isnan(vals)] = np.nan

        ncs._plotTopo(ax, topo)
        ax.contourf(dimx.vals, dimy.vals,
                    vals, levels=ncs.levels,
                    cmap='jet')
        #plt.show()
        #quit()

            
        #title = 'Accum. Precip. '+str(ssI['diurnal'][0])+'-'+str(ssI['diurnal'][-1]+1)
        #ncs.fig.suptitle(title, fontsize=14)

        

        for rowInd,mode in enumerate(an.modes):
            if ncs.orientation == 'VER':
                ax = ncs.axes[rowInd,0]
            elif ncs.orientation == 'HOR':
                ax = ncs.axes[0,rowInd]

            ## PLOT ADJUSTMENTS
            #ax.set_xlabel('Latitude',fontsize=12)
            #if mode == '':
            #    ax.legend_.remove()
            #    ax.set_ylabel('',fontsize=12)
            #else:
            #    ax.set_ylabel(r'Rain Rate $[mm h^{-1}]$',fontsize=12)
            #ax.set_ylim(0,1.7)



    elif nDPlot == 1 and someField.nNoneSingleton == 1:
        import ncPlots.ncSubplots1D as ncSubplots
        ncs = ncSubplots.ncSubplots(an, nDPlot, i_diffPlot, 'HOR')
    
        for varName in an.varNames:
            if varName != 'cHSURF':
                ncs.plotVar(an.vars[varName])

        title = 'title' 
        ncs.fig.suptitle(title, fontsize=14)

    else:
        raise ValueError('ERROR: CANNOT MAKE ' + str(nDPlot) + 'D-PLOT WITH ' +
        str(someField.nNoneSingleton) + ' NON-SINGLETON DIMS!')

    
    if i_plot == 1:
        plt.show()
    elif i_plot == 2:
        plotPath = plotOutDir + '/' + plotName + '.png'
        print(plotPath)
        plt.savefig(plotPath, format='png', bbox_inches='tight')
        plt.close('all')
    elif i_plot == 3:
        plotPath = plotOutDir + '/' + plotName+'.pdf'
        print(plotPath)
        plt.savefig(plotPath, format='pdf', bbox_inches='tight')
        plt.close('all')

          


