#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
title			:QV_morive_present.py
description	    :Plot lat/lon-altitude cross-sections of water vapor as time
                 evolution
author			:Christoph Heim
date created    :20190510
date changed    :20190622
usage			:no args
notes			:
python_version	:3.7.1
==============================================================================
"""
import os
os.chdir('00_scripts/')

i_resolutions = 5 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 2 # 0 = no plot, 1 = show plot, 2 = save plot
i_info = 0 # output some information [from 0 (off) to 5 (all you can read)]
import matplotlib
if i_plot == 2:
	matplotlib.use('Agg')
import matplotlib.pyplot as plt

from matplotlib import patches

import ncClasses.analysis as analysis
from datetime import datetime, timedelta
from functions import *
from pathlib import Path
####################### NAMELIST INPUTS FILES #######################
models_meta = {
    'RAW1':{
        'col':'red',
    },
    'SM1':{
        'col':'blue',
    },
}
# directory of input model folders
settings = {
    'diurn_movie':{
        'cmapM':'jet',
        'plot_var':'zQV',
        'Mticks':list(np.arange(0,16,0.1)),
    },
}

fieldNames = ['zW', 'zV', 'zU', 'zQV', 'zQC', 'cHSURF','nTOT_PREC',]

case = 'diurn_movie'

inpPath = '../02_fields/topocut'

time_limits = [datetime(2006,7,12,5),
         datetime(2006,7,12,13)]
# from dt_range given by times select the following indices
time_inds = [0,1,2,3,4,5,6,7]
setting = settings[case]

ticksize    = 13
labelsize   = 15
titlesize   = 20
#####################################################################		
cs = [
    {'lon':[90],'lat':[45,120]},    
    {'lon':[107],'lat':[80,135]},    
    {'lon':[115],'lat':[80,135]},    
    {'lon':[120],'lat':[90,140]},    
    {'lon':[150],'lat':[80,150]},    
    {'lon':[165],'lat':[80,150]},    
    {'lon':[50,120],'lat':[75] },    
    {'lon':[60,120],'lat':[90] },    
    {'lon':[70,185],'lat':[100]},    
    {'lon':[70,190],'lat':[115]},    
]
counts = range(0,6)
counts = [3]

for count in counts:
    lon = cs[count]['lon']
    lat = cs[count]['lat']

    if len(lat) == 1:
        raise NotImplementedError('only lat-altitudes cross-sects ' +
                                    'possible currently.')

    print('##################')
    print('lon ' + str(lon))
    print('lat ' + str(lat))
    print('##################')

    ####################### NAMELIST DIMENSIONS #######################
    #subDomain = 1 # 0: full domain, 1: alpine region, 2: zoom in
    # SUBSPACE
    subSpaceIndsIN = {}
    subSpaceIndsIN['rlon'] = lon
    subSpaceIndsIN['rlat'] = lat
        
    subSpaceIndsIN['time'] =  time_limits
    subSpaceIndsIN['altitude'] = np.arange(0,40).tolist()
    #####################################################################

    ####################### NAMELIST AGGREGATE #######################
    # Options: MEAN, SUM, DIURNAL
    ag_commnds = {}
    #ag_commnds['time'] = 'MEAN'
    #####################################################################

    ####################### NAMELIST PLOT #######################
    nDPlot = 2 # How many dimensions should plot have (1 or 2)
    i_diffPlot = 0 # Draw plot showing difference filtered - unfiltered # TODO

    if len(lat) == 2:
        plotOutDir = os.path.join('..','00_plots','02_vCS',case)
        plotName = 'lon_'+str(lon[0])
    elif len(lon) == 2:
        plotOutDir = os.path.join('..','00_plots','02_vCS',case)
        plotName = 'lat_'+str(lat[0])

    pth = Path(plotOutDir)
    pth.mkdir(parents=True, exist_ok=True)
    ##### 1D PLOT #########

    ##### 2D Contour ######
    contourTranspose = 0 # Reverse contour dimensions?
    plotContour = 0 # Besides the filled contour, also plot the contour?
    cmapM = setting['cmapM'] # colormap for Model output (jet, terrain, inferno, YlOrRd)
    axis = 'auto' # set 'equal' if keep aspect ratio, else 'auto'
    # COLORBAR Models
    autoTicks = 0 # 1 if colorbar should be set automatically
    Mmask = 0 # Mask Model values lower than MThrMinRel of maximum value?
    MThrMinRel = 0.03 # Relative amount of max value to mask (see Mmask)
    Mticks = setting['Mticks']
    # COLORBAR Models
    cmapD = 'bwr' # colormap for Difference output (bwr)
    i_diff_topo = False
    #####################################################################
    an = analysis.analysis(inpPath, fieldNames)
    an.subSpaceInds = subSpaceIndsIN
    an.ag_commnds = ag_commnds
    an.i_info = i_info
    an.i_resolutions = i_resolutions

    # RUN ANALYSIS
    an.run()

    import matplotlib
    if i_plot == 2:
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt

	
    for tI,time_ind in enumerate(time_inds):
        fig,axes = plt.subplots(nrows=2, ncols=1, figsize=(10,8))

        for mI,model in enumerate(['SM1','RAW1']):
            ax = axes[mI]

            times = an.vars['nTOT_PREC'].ncos[model].dims['time'].vals
            rlat = an.vars['nTOT_PREC'].ncos[model].dims['rlat'].vals
            rlon = an.vars['nTOT_PREC'].ncos[model].dims['rlon'].vals
            alt = an.vars['zQV'].ncos[model].dims['altitude'].vals

            HSURF = an.vars['cHSURF'].ncos[model].field.vals.squeeze()
            QV = an.vars['zQV'].ncos[model].field.vals[time_ind,:,:].squeeze()
            QC = an.vars['zQC'].ncos[model].field.vals[time_ind,:,:].squeeze()

            ax.fill_between(rlat, 0, HSURF/1000, color='k')
            CF = ax.contourf(rlat, alt, QV*1000, cmap='jet',
                             levels=settings[case]['Mticks'])

            ax.contour(rlat, alt, QV*1000, colors='black', alpha=0.5,
                        linewidths=1, levels=[8])

            ax.contour(rlat, alt, QC*1000, colors='purple', alpha=0.8,
                          linewidths=1.5, levels=[1])


            # QUIVER
            nth_val_vert = 4
            nth_val_hor = 15
            rlat = an.vars['zW'].ncos[model].dims['rlat'].vals[::nth_val_hor]
            rlon = an.vars['zW'].ncos[model].dims['rlon'].vals[::nth_val_hor]
            alt = an.vars['zW'].ncos[model].dims['altitude'].vals[::nth_val_vert]
            W = an.vars['zW'].ncos[model].field.vals.squeeze()[
                            time_ind,::nth_val_vert,::nth_val_hor]
            V = an.vars['zV'].ncos[model].field.vals.squeeze()[
                            time_ind,::nth_val_vert,::nth_val_hor]
            ax.quiver(rlat, alt, V, W, scale=120, width=0.004)
            if mI == 0:
                lat_ind = 7
                alt_ind = 1
                V[:] = np.nan
                W[:] = np.nan
                V[alt_ind,lat_ind] = -10.
                W[alt_ind,lat_ind] = 0.
                ax.quiver(rlat, alt, V, W, scale=120, width=0.004,
                            color='white')
                ax.text(443,0.6,'10 m s$^{-1}$', color='w', fontsize=13)

            # time labels
            if mI == 0:
                hour_string = '{:02d}00'.format(times[time_ind].hour)
                ax.text(365, 3.3, hour_string, size=17, color='black',
                    bbox=dict(boxstyle='round, pad=0.1',ec=(1,1,1,0.5),
                                fc=(1,1,1,0.8)))

            ax.set_ylim(0,subSpaceIndsIN['altitude'][-1]/10)
            ax.set_xlim(rlat[0],rlat[-1])
            ax.set_title(model, fontsize=titlesize)
            if mI == 1:
                ax.set_xlabel('Latitude [km]', fontsize=labelsize)
            ax.set_ylabel('Altitude [km]', fontsize=labelsize)


        cPosLeft    = 0.1
        cPosBot     = 0.058
        cWidth      = 0.8
        cHeight     = 0.025
        cax = fig.add_axes([cPosLeft, cPosBot, cWidth, cHeight])
        MCB = plt.colorbar(mappable=CF, cax=cax, orientation='horizontal')
        cax.tick_params(labelsize=ticksize)
        MCB.set_label('$q_v$ [g kg$^{-1}$]', fontsize=labelsize)


        plt.subplots_adjust(top=0.97, left=0.05, right=0.98, bottom=0.16,
                            hspace=0.25)

        if i_plot == 1:
            plt.show()
        elif i_plot == 2:
            plotPath = plotOutDir + '/' + plotName+'_'+str(time_ind) + '.png'
            plt.savefig(plotPath, format='png', bbox_inches='tight')
            plt.close(fig.number)
        elif i_plot == 3:
            plotPath = plotOutDir + '/' + plotName+'_'+str(time_ind) + '.pdf'
            plt.savefig(plotPath, format='pdf', bbox_inches='tight')
            plt.close(fig.number)

