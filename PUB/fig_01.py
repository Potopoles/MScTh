#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
orig: 03_01_domain_PUB.py
description	    :Plot simulation domain with topography and analysis domains
author			:Christoph Heim
date created    :20171121 
date changed    :31.01.2020
usage			:no args
notes			:Figure 1 in paper.
==============================================================================
"""
import os
os.chdir('00_scripts/')

i_resolutions = 5 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 1 # 0 = no plot, 1 = show plot, 2 = save plot
i_info = 3 # output some information [from 0 (off) to 5 (all you can read)]
import matplotlib
if i_plot == 2:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt

import xarray as xr
from package.domains import dom_alpine_region

import ncClasses.analysis as analysis
from datetime import datetime
from functions import *
from ncClasses.subdomains import setSSI
####################### NAMELIST INPUTS FILES #######################
# directory of input model folders
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
    try:
        nco = mainVar.ncos['RAW1']
    except KeyError:
        nco = mainVar.ncos['RAW4']
    someField = next(iter(mainVar.ncos.values())).field
    if i_info >= 1:
        print('NONSINGLETONS: ' + str(someField.nNoneSingleton))
    
    if nDPlot == 2 and someField.nNoneSingleton == 2:
        import ncPlots.ncPlot2D as ncPlot
        ncp = ncPlot.ncPlot2D(nco, geo_plot=True)

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
        col1 = 'white'
        col2 = 'red'
        col3 = 'white'

        ## ALPINE RIDGE VERT PROF
        #code = '-'
        #x0 = 100; x1 = 160
        #y0 = 100; y1 = 125
        #ax.plot([x0*4, x1*4], [y0*4, y0*4], code, linewidth=2, color=col1)
        #ax.plot([x0*4, x1*4], [y1*4, y1*4], code, linewidth=2, color=col1)
        #ax.plot([x0*4, x0*4], [y0*4, y1*4], code, linewidth=2, color=col1)
        #ax.plot([x1*4, x1*4], [y0*4, y1*4], code, linewidth=2, color=col1)
        #ax.text(x1*4-df, y0*4+df/3, 'A', fontsize=text_size, color=col1)


        ### ALPINE RIDGE
        ##code = '-'
        ##x0 = 110; x1 = 150
        ##y0 = 110; y1 = 120
        ##ax.plot([x0*4, x1*4], [y0*4, y0*4], code, linewidth=2, color=col1)
        ##ax.plot([x0*4, x1*4], [y1*4, y1*4], code, linewidth=2, color=col1)
        ##ax.plot([x0*4, x0*4], [y0*4, y1*4], code, linewidth=2, color=col1)
        ##ax.plot([x1*4, x1*4], [y0*4, y1*4], code, linewidth=2, color=col1)
        ##ax.text(x1*4-df, y0*4+df/3, 'A', fontsize=text_size, color=col1)
        
        # ALPINE REGION
        code = '-'
        x0 = 50; x1 = 237
        y0 = 41; y1 = 155
        ax.plot([x0*4, x1*4], [y0*4, y0*4], code, linewidth=2, color=col1)
        ax.plot([x0*4, x1*4], [y1*4, y1*4], code, linewidth=2, color=col1)
        ax.plot([x0*4, x0*4], [y0*4, y1*4], code, linewidth=2, color=col1)
        ax.plot([x1*4, x1*4], [y0*4, y1*4], code, linewidth=2, color=col1)
        ax.text(x1*4-df, y0*4+df/3, 'A', fontsize=text_size, color=col1)


        # PO VALLEY
        code = '-'
        x0 = 102; x1 = 150 
        y0 = 65; y1 = 97 
        #x0 = 100; x1 = 150 
        #y0 = 71; y1 = 94 
        ax.plot([x0*4, x1*4], [y0*4, y0*4], code, linewidth=2, color=col1)
        ax.plot([x0*4, x1*4], [y1*4, y1*4], code, linewidth=2, color=col1)
        ax.plot([x0*4, x0*4], [y0*4, y1*4], code, linewidth=2, color=col1)
        ax.plot([x1*4, x1*4], [y0*4, y1*4], code, linewidth=2, color=col1)
        ax.text(x1*4+df/5, y1*4-df*3/4, 'E', fontsize=text_size, color=col1)

        ### ALPINE ARC
        ##code = '-'
        ##x0 = 110; x1 = 150 
        ##y0 = 110; y1 = 120
        ##ax.plot([x0*4, x1*4], [y0*4, y0*4], code, linewidth=2, color=col1)
        ##ax.plot([x0*4, x1*4], [y1*4, y1*4], code, linewidth=2, color=col1)
        ##ax.plot([x0*4, x0*4], [y0*4, y1*4], code, linewidth=2, color=col1)
        ##ax.plot([x1*4, x1*4], [y0*4, y1*4], code, linewidth=2, color=col1)
        ##ax.text(x1*4-df, y0*4+df/3, 'E', fontsize=text_size, color=col1)

        # CROSSSECT
        code = '-'
        x0 = 110; x1 = 135
        y0 = 52; y1 = 135
        ax.plot([x0*4, x1*4], [y0*4, y0*4], code, lineWidth=2, color=col3)
        ax.plot([x0*4, x1*4], [y1*4, y1*4], code, lineWidth=2, color=col3)
        ax.plot([x0*4, x0*4], [y0*4, y1*4], code, lineWidth=2, color=col3)
        ax.plot([x1*4, x1*4], [y0*4, y1*4], code, lineWidth=2, color=col3)
        ax.text(x1*4+df/5, y1*4-df*3/4, 'B', fontsize=text_size, color=col3)

        # LINE CROSSSECT
        x = 120
        y0 = 90; y1 = 140
        ax.plot([x*4, x*4], [y0*4, y1*4], '-', lineWidth=2, color=col2)
        ax.text(x*4-df/3, y1*4+df/4, 'C', fontsize=text_size, color=col2)

        # COMBIPRECIP
        path = os.path.join('../02_fields/topocut/OBS1/nTOT_PREC.nc')
        obs = xr.open_dataset(path)
        obs = obs['TOT_PREC']
        #obs = obs.sel(x_1 = dom_alpine_region['lon'], y_1 = dom_alpine_region['lat'])
        obs = obs.isel(time=0)
        #inds = np.ix_([np.arange(0,obs.values.shape[0]),np.argwhere(obs.x_1.values < dom_alpine_region['lon'].start)])

        #xvals = an.vars['cHSURF'].ncos['RAW1'].dims['rlon'].vals
        #yvals = an.vars['cHSURF'].ncos['RAW1'].dims['rlat'].vals

        #inds_x = np.argwhere(obs.x_1.values < dom_alpine_region['lon'].start)
        #obs.values[:,inds_x] = 0
        #inds_x = np.argwhere(obs.x_1.values > dom_alpine_region['lon'].stop)
        #obs.values[:,inds_x] = 0
        #inds_y = np.argwhere(obs.y_1.values < dom_alpine_region['lat'].start)
        #obs.values[inds_y,:] = 0
        #inds_y = np.argwhere(obs.y_1.values > dom_alpine_region['lat'].stop)
        #obs.values[inds_y,:] = 0

        obs.x_1.values = np.arange(0,len(obs.x_1.values))*1.0
        obs.y_1.values = np.arange(0,len(obs.y_1.values))*1.0
        obs.values[~np.isnan(obs.values)] = 1
        obs.values[np.isnan(obs.values)] = 0
        obs.values[490:525,640:668] = 1.
        print(obs.x_1.values.shape)
        print(obs.y_1.values.shape)
        print(obs.values.shape)

        old_xlim = ax.get_xlim()
        old_ylim = ax.get_ylim()
        ax.contour(obs.x_1.values, obs.y_1.values, obs.values, levels=[0.9],
                   colors='red', linewidths=2)
        ax.text(250, 660, 'D', fontsize=text_size, color='red')
        ax.set_xlim(old_xlim)
        ax.set_ylim(old_ylim)
        

        # GEOGRAPHIC LABELS
        text_col = 'orange'
        ax.text(405,172, 'Ligurian Sea', color=text_col, fontsize=text_size*0.60, weight='bold')
        ax.text(447,320, 'Po Valley', color=text_col, fontsize=text_size*0.60, weight='bold')

        # COLORBAR
        ncp.fig.subplots_adjust(left=0.12, right=0.99, bottom=0.20, top=0.99)
        cax = ncp.fig.add_axes([0.12, 0.08, 0.85, 0.025])
        MCB = plt.colorbar(mappable=ncp.CF, cax=cax,
                    orientation='horizontal')
        cax.tick_params(labelsize=18)
        MCB.set_label('Elevation [$m$]', fontsize=22)
            

    else:
        raise ValueError('ERROR: CANNOT MAKE ' + str(nDPlot) + 'D-PLOT WITH ' +
        str(someField.nNoneSingleton) + ' NON-SINGLETON DIMS!')

    
    if i_plot == 1:
        plt.show()
    elif i_plot == 2:
        plotPath = plotOutDir + '/' + plotName
        plt.savefig(plotPath, format='png', bbox_inches='tight')

          


