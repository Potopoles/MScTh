#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
title			radar.py
description	    Plot diurnal TOT_PREC cycle evaluation with radar.
                Uses data from script 10_00_proc_radar.py
author			Christoph Heim
date created    20190524 
date changed    20190524
usage			no args
notes			
python_version	3.7.1
==============================================================================
"""
import os
os.chdir('00_scripts/')

i_resolutions = 3 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 1 # 0 = no plot, 1 = show plot, 2 = save plot
i_info = 1 # output some information [from 0 (off) to 5 (all you can read)]
import matplotlib
if i_plot == 2:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt


import ncClasses.analysis as analysis
from ncClasses.ncObject import ncObject
from datetime import datetime
from functions import *
from ncClasses.subdomains import setSSI
from netCDF4 import Dataset
####################### NAMELIST INPUTS FILES #######################
inpPath = '../02_fields/radar_diurn'

fieldNames = ['nTOT_PREC']
modes = ['RAW', 'SM', 'OBS']
model_modes = ['RAW', 'SM']

i_subDomain = 0 # 0: full domain, 1: alpine region
ssI, domainName = setSSI(i_subDomain, {'4.4':{}, '2.2':{}, '1.1':{}}) 
#####################################################################		

####################### NAMELIST AGGREGATE #######################
# Options: MEAN, SUM 
ag_commnds = {}
#####################################################################

####################### NAMELIST PLOT #######################
nDPlot = 1 # How many dimensions should plot have (1 or 2)
i_diffPlot = 0 # Draw plot showing difference filtered - unfiltered # TODO
plotOutDir = '../00_plots'

# 1D PLOT
plotName = '10_evaluation/1D'

##### 2D Contour ######
contourTranspose = 0 # Reverse contour dimensions?
plotContour = 0 # Besides the filled contour, also plot the contour?
cmapM = 'jet' # colormap for Model output (jet, terrain, inferno, YlOrRd)
axis = 'equal' # set 'equal' if keep aspect ratio, else 'auto'
# COLORBAR Models
autoTicks = 0 # 1 if colorbar should be set automatically
Mmask = 1 # Mask Model values lower than MThrMinRel of maximum value?
MThrMinRel = 0.03 # Relative amount of max value to mask (see Mmask)
Mticks = list(np.arange(10,320,20))
# COLORBAR Models
cmapD = 'bwr' # colormap for Difference output (bwr)
#####################################################################


an = analysis.analysis(inpPath, fieldNames)

#an.subSpaceInds = subSpaceInds
an.ag_commnds = ag_commnds
an.subSpaceInds = ssI
an.i_info = i_info
an.i_resolutions = i_resolutions

an.run()



if i_plot > 0:
    if i_info >= 3:
        print('plotting')
    mainVar = an.vars[an.varNames[0]]
    someField = next(iter(mainVar.ncos.values())).field
    if i_info >= 1:
        print('NONSINGLETONS: ' + str(someField.nNoneSingleton))
    
    if nDPlot == 1 and someField.nNoneSingleton == 1:
        from ncPlots.ncSubplots1D import ncSubplots
        ncs = ncSubplots(an, nDPlot, i_diffPlot, 'HOR')

        for varName in an.varNames:
            if varName != 'cHSURF':
                ncs.plotVar(an.vars[varName])

        xvals = np.arange(0,25)
        for mI,mode in enumerate(model_modes):
            ax = ncs.axes[0,mI]
            vals = an.vars[fieldNames[0]].ncos['OBS1'].field.vals
            line, = ax.plot(xvals, vals.squeeze(), color='grey', label='OBS')
            if ax.get_legend() is not None:
                lines = ax.get_legend().get_lines()
                texts = ax.get_legend().get_texts()
                labels = [text.get_text() for text in texts]
                labels.append('OBS')
                lines.append(line)
                ax.legend(handles=lines, labels=labels)
            ylim = ax.get_ylim()
            print(ylim)
            ylim = (ylim[0], ylim[1]*1.05)
            ax.set_ylim(ylim)

            if mI == 0:
                ax.set_ylabel('Rain Rate $[mm$ $h^{-1}]$')
            else:
                ax.set_ylabel('')
            ax.set_xlabel('Hour')


        # PRECIP MEAN DAILY SUM
        x = 3
        yTop = 1.1
        dy = 0.18
        size = 12
        for rowInd,mode in enumerate(model_modes):

            # TODO: Turn around because sum labels are wrong else
            # Don't know why --> it's a mess!
            if mode == 'f':
                mode = ''
            elif mode == '':
                mode = 'f'


            if ncs.orientation == 'VER':
                ax = ncs.axes[rowInd,0]
            elif ncs.orientation == 'HOR':
                ax = ncs.axes[0,rowInd]
            if mode != 'D':
                ax.text(x, yTop+dy, 'Sum:', size=size,
                        bbox=dict(boxstyle='square',ec=(1,1,1,0.5),fc=(1,1,1,0.5)))
            # PLOT ADJUSTMENTS
            ax.set_xlabel('Hour',fontsize=12)
            if mode == '':
                #ax.legend_.remove()
                ax.set_ylabel('',fontsize=12)
            else:
                ax.set_ylabel(r'Rain Rate $[mm$ $h^{-1}]$',fontsize=12)
            ax.set_ylim(0,0.3)



            # MODEL RESOLUTIONS
            for rI,res in enumerate(ncs.ress):
                # GET VALUES AND DIMENSIONS				
                fld = an.vars['nTOT_PREC'].ncos[str(mode+res)].field
                if mode != 'd':
                    sum = str(round(np.sum(fld.vals),1)) + ' mm' 
                    ax.text(x, yTop-dy*rI, sum, color=ncs.colrs[rI], size=size,
                            bbox=dict(boxstyle='square',ec=(1,1,1,0.5),fc=(1,1,1,0.5)))
            # RADAR
            fld = an.vars['nTOT_PREC'].ncos['RAW'+str(res)].field
            if mode != 'd':
                sum = str(round(np.sum(fld.vals),1)) + ' mm' 
                ax.text(x, yTop-dy*(rI+1), sum, color='grey', size=size,
                        bbox=dict(boxstyle='square',ec=(1,1,1,0.5),fc=(1,1,1,0.5)))


        #stretchCol = 3.8
        #stretchRow = 3.8
        #ncols = 2; nrows = 1
        #fig, axes = plt.subplots(ncols=ncols, nrows=nrows,
        #                figsize=(ncols*stretchCol,nrows*stretchRow))
        #for mI,mode in enumerate(model_modes):
        #    ax = axes[mI]
        #    for res in an.resolutions:
        #        vals = an.vars[fieldNames[0]].ncos[res+mode].field.vals
        #        ax.plot(vals.squeeze())
        #plt.show()

    else:
        raise ValueError('ERROR: CANNOT MAKE ' + str(nDPlot) + 'D-PLOT WITH ' +
        str(someField.nNoneSingleton) + ' NON-SINGLETON DIMS!')

    
    if i_plot == 1:
        plt.show()
    elif i_plot == 2:
        plotPath = plotOutDir + '/' + plotName+'.png'
        plt.savefig(plotPath, format='png', bbox_inches='tight')
        plt.close('all')
    elif i_plot == 3:
        plotPath = plotOutDir + '/' + plotName+'.pdf'
        plt.savefig(plotPath, format='pdf', bbox_inches='tight')
        plt.close('all')

          


