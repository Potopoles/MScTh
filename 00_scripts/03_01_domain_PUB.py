#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
title			:domain.py
description	    :Plot simulation domain with topography and analysis domains
author			:Christoph Heim
date created    :20171121 
date changed    :20190611
usage			:no args
notes			:Figure 1 in paper.
python_version	:3.7.1
==============================================================================
"""
import os
os.chdir('00_scripts/')

i_resolutions = 3 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 2 # 0 = no plot, 1 = show plot, 2 = save plot
i_info = 1 # output some information [from 0 (off) to 5 (all you can read)]
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
#inpPath = '../02_fields/topocut'
inpPath = '../02_fields/diurnal'
#fieldNames = ['cHSURF','nTOT_PREC']
fieldNames = ['cHSURF']
#####################################################################		

####################### NAMELIST DIMENSIONS #######################
i_subDomain = 0 # 0: full domain, 1: alpine region
ssI, domainName = setSSI(i_subDomain, {'4':{}, '2':{}, '1':{}}) 
#####################################################################

####################### NAMELIST AGGREGATE #######################
# Options: MEAN, SUM, DIURNAL
ag_commnds = {}
#####################################################################

####################### NAMELIST PLOT #######################
nDPlot = 2 # How many dimensions should plot have (1 or 2)
plotOutDir = '../00_plots'
plotName = 'domain_AR_and_NI.png'
##### 1D PLOT #########

##### 2D Contour ######
contourTranspose = 0 # Reverse contour dimensions?
plotContour = 0 # Besides the filled contour, also plot the contour?
cmapM = 'terrain' # colormap for Model output (jet, terrain, inferno, YlOrRd)
axis = 'equal' # set 'equal' if keep aspect ratio, else 'auto'
# COLORBAR Models
autoTicks = 1 # 1 if colorbar should be set automatically
Mmask = 0 # Mask Model values lower than MThrMinRel of maximum value?
MThrMinRel = 0.15 # Relative amount of max value to mask (see Mmask)
Mticks = [0.0001,0.0002,0.0003,0.0004,0.0005]
Mticks = list(np.arange(0.0002,0.0022,0.0002))
#####################################################################
an = analysis.analysis(inpPath, fieldNames)

an.subSpaceInds = ssI
an.ag_commnds = ag_commnds
an.i_info = i_info
an.i_resolutions = i_resolutions

# RUN ANALYSIS
an.run()

import matplotlib
if i_plot == 2:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt

if i_plot > 0:
    if i_info >= 3:
        print('plotting')
    mainVar = an.vars[an.varNames[0]]
    nco = mainVar.ncos['RAW1']
    someField = next(iter(mainVar.ncos.values())).field
    if i_info >= 1:
        print('NONSINGLETONS: ' + str(someField.nNoneSingleton))
    
    if nDPlot == 2 and someField.nNoneSingleton == 2:
        import ncPlots.ncPlot2D as ncPlot
        ncp = ncPlot.ncPlot2D(nco)

        ncp.contourTranspose = contourTranspose
        ncp.plotContour = plotContour
        ncp.cmapM = cmapM
        ncp.axis = axis
        ncp.autoTicks = autoTicks
        ncp.Mmask = Mmask
        ncp.MThrMinRel = MThrMinRel
        ncp.Mticks = Mticks
   
        fig, ax = ncp.plotNCO(nco)

        text_size = 25
        df = 50
        col2 = 'red'
        col3 = 'black'
        
        # ALPINE REGION
        x0 = 50; x1 = 237
        y0 = 41; y1 = 155
        ax.plot([x0*4, x1*4], [y0*4, y0*4], '-k', linewidth=2)
        ax.plot([x0*4, x1*4], [y1*4, y1*4], '-k', linewidth=2)
        ax.plot([x0*4, x0*4], [y0*4, y1*4], '-k', linewidth=2)
        ax.plot([x1*4, x1*4], [y0*4, y1*4], '-k', linewidth=2)
        ax.text(x1*4-df, y0*4+df/3, 'A', fontsize=text_size, color='k')

        # CROSSSECT
        x0 = 110; x1 = 135
        y0 = 52; y1 = 135
        ax.plot([x0*4, x1*4], [y0*4, y0*4], '-', lineWidth=2, color=col3)
        ax.plot([x0*4, x1*4], [y1*4, y1*4], '-', lineWidth=2, color=col3)
        ax.plot([x0*4, x0*4], [y0*4, y1*4], '-', lineWidth=2, color=col3)
        ax.plot([x1*4, x1*4], [y0*4, y1*4], '-', lineWidth=2, color=col3)
        ax.text(x1*4+df/4, y1*4-df, 'B', fontsize=text_size, color=col3)

        # LINE CROSSSECT
        x = 120
        y0 = 90; y1 = 140
        ax.plot([x*4, x*4], [y0*4, y1*4], '-', lineWidth=2, color=col2)
        ax.text(x*4-df/3, y0*4-df, 'C', fontsize=text_size, color=col2)
            

    else:
        raise ValueError('ERROR: CANNOT MAKE ' + str(nDPlot) + 'D-PLOT WITH ' +
        str(someField.nNoneSingleton) + ' NON-SINGLETON DIMS!')

    
    if i_plot == 1:
        plt.show()
    elif i_plot == 2:
        plotPath = plotOutDir + '/' + plotName
        plt.savefig(plotPath, format='png', bbox_inches='tight')

          

