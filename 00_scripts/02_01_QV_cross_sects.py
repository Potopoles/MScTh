#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
title			:QV_cross_sects.py
description	    :Plot lat/lon-altitude cross-sections of water vapor.
author			:Christoph Heim
date created    :20190510
date changed    :20190611
usage			:no args
notes			:
python_version	:3.7.1
==============================================================================
"""
import os
os.chdir('00_scripts/')

i_resolutions = 5 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 1 # 0 = no plot, 1 = show plot, 2 = save plot
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
    'mixing':{
        'cmapM':'seismic',
        'plot_var':'zW',
        'Mticks':list(np.arange(-8,8,0.1)),
    },
    'wv':{
        'cmapM':'jet',
        'plot_var':'zQV',
        'Mticks':list(np.arange(0,16,0.1)),
    },
    'fqvz':{
        'cmapM':'seismic',
        'plot_var':'zFQVZ',
        'Mticks':list(np.arange(-50,50,1)*1E-3),
    },
    'rh':{
        'cmapM':'jet',
        'plot_var':'zRH',
        'Mticks':list(np.arange(0,106,2)),
    },
}

fieldNames = ['zW', 'zV', 'zU', 'zQV', 'zQC', 'zFQVY', 'zRH', 'cHSURF',
              'nTOT_PREC', 'zWVP_0_2', 'zWVP_2_4', 'zEQPOTT', 'zT', 'zP']

#case = 'mixing'
case = 'wv'
#case = 'fqvz'
#case = 'rh'

time_mode = 'ts'
time_mode = 'diurnal'

if time_mode == 'ts':
    inpPath = '../02_fields/topocut'
    dt0 = datetime(2006,7,11,0)
    dt1 = datetime(2006,7,20,0)
    dt0 = datetime(2006,7,12,12)
    dt1 = datetime(2006,7,12,13)
    dt_range = np.arange(dt0, dt1, timedelta(hours=1)).tolist()
elif time_mode == 'diurnal':
    inpPath = '../02_fields/diurnal'
    dt_range = np.arange(0,24).tolist()

setting = settings[case]
#####################################################################		
lons = [80, 90, 107, 125, 150, 175, None, None, None, None, None, None, None]
lats = [None, None, None, None, None, None, 60, 75, 90, 100, 110, 120, 130]

cs = [
    {'lon':[90],'lat':[45,120]},    
    {'lon':[107],'lat':[80,135]},    
    {'lon':[115],'lat':[80,135]},    
    {'lon':[120],'lat':[80,135]},    
    {'lon':[150],'lat':[80,150]},    
    {'lon':[165],'lat':[80,150]},    
    {'lon':[50,120],'lat':[75]},    
    {'lon':[60,120],'lat':[90]},    
    {'lon':[70,185],'lat':[100]},    
    {'lon':[70,190],'lat':[115]},    
]


counts = range(0,len(cs))
counts = [3]

for count in counts:
    lon = cs[count]['lon']
    lat = cs[count]['lat']

    print('##################')
    print('lon ' + str(lon))
    print('lat ' + str(lat))
    print('##################')
	
    for dt in dt_range:
        if time_mode == 'ts':
            if dt.hour in [0,6,12,18]:
                print('\t '+str(dt))
        ####################### NAMELIST DIMENSIONS #######################
        #subDomain = 1 # 0: full domain, 1: alpine region, 2: zoom in
        # SUBSPACE
        subSpaceIndsIN = {}
        subSpaceIndsIN['rlon'] = lon
        subSpaceIndsIN['rlat'] = lat
            
        if time_mode == 'ts':
            startTime = datetime(2006,7,dt.day,dt.hour)
            subSpaceIndsIN['time'] = [startTime]
        elif time_mode == 'diurnal':
            subSpaceIndsIN['diurnal'] = [dt]

        subSpaceIndsIN['altitude'] = np.arange(0,50).tolist()
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
            plotOutDir = os.path.join('..','00_plots','02_vCS',case,time_mode,'lon_'+str(lon[0]))
            if time_mode == 'ts':
                plotName = 'lon_'+str(lon[0])+'_'+'{:%d%H}'.format(dt)+'.png'
            elif time_mode == 'diurnal':
                plotName = 'lon_'+str(lon[0])+'_'+'{:2d}'.format(dt)+'.png'
        elif len(lon) == 2:
            plotOutDir = os.path.join('..','00_plots','02_vCS',case,time_mode,'lat_'+str(lat[0]))
            if time_mode == 'ts':
                plotName = 'lat_'+str(lat[0])+'_'+'{:%d%H}'.format(dt)+'.png'
            elif time_mode == 'diurnal':
                plotName = 'lat_'+str(lat[0])+'_'+'{:2d}'.format(dt)+'.png'

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

        if i_info >= 3:
            print('plotting')
        mainVar = an.vars[an.varNames[0]]
        someField = next(iter(mainVar.ncos.values())).field
        if i_info >= 1:
            print('NONSINGLETONS: ' + str(someField.nNoneSingleton))
        import ncPlots.ncSubplots2D as ncSubplots
        ncs = ncSubplots.ncSubplots(an, nDPlot, i_diffPlot, 'HOR')
        plt.close(ncs.fig.number)
        fig,axes = plt.subplots(nrows=2, ncols=2)
        ncs.axes = np.expand_dims(axes[:,0], axis=1)
        ncs.fig = fig

        if nDPlot == 2 and someField.nNoneSingleton == 2:
            ncs.contourTranspose = contourTranspose
            ncs.plotContour = plotContour
            ncs.cmapM = cmapM
            ncs.axis = axis
            ncs.autoTicks = autoTicks
            ncs.Mmask = Mmask
            ncs.MThrMinRel = MThrMinRel
            ncs.Mticks = Mticks
            ncs.cmapD = cmapD
            ncs.i_diff_topo = i_diff_topo

            if 'cHSURF' in an.varNames:
                ncs.plotTopo(an.vars['cHSURF'])
            
            ncs.plotVar(an.vars[setting['plot_var']])

            axlegend = fig.add_axes([0.88,0.9,0.1,0.1])
            axlegend.axis('off')

            ax_raw_prof = fig.add_axes([0.44,0.248,0.1,0.255])
            ax_raw_prof.set_ylim(0,5)
            ax_raw_prof.set_xlim(1,10)
            ax_raw_prof.set_xlabel('mean QV')
            ax_sm_prof = fig.add_axes([0.44,0.604,0.1,0.255])
            ax_sm_prof.set_ylim(0,5)
            ax_sm_prof.set_xlim(300,335)
            ax_sm_prof.set_xlabel('mean (equiv.) POTT')

            lines = []
            y0 = 28
            y_shift = 0
            for rI,model in enumerate(['SM1','RAW1']):
                ax = ncs.axes[rI,0]
                
                # QUIVER
                nth_val = 5
                rlat = an.vars['zW'].ncos[model].dims['rlat'].vals[::nth_val]
                rlon = an.vars['zW'].ncos[model].dims['rlon'].vals[::nth_val]
                alt = an.vars['zW'].ncos[model].dims['altitude'].vals[::nth_val]
                W = an.vars['zW'].ncos[model].field.vals.squeeze()[::nth_val,::nth_val]
                if len(lat) == 2:
                    U_or_V = an.vars['zV'].ncos[model].field.vals.squeeze()[::nth_val,::nth_val]
                    ax.quiver(rlat, alt, U_or_V, W, scale=250)
                elif len(lon) == 2:
                    U_or_V = an.vars['zU'].ncos[model].field.vals.squeeze()[::nth_val,::nth_val]
                    ax.quiver(rlon, alt, U_or_V, W, scale=250)

                # TOT_PREC and WVP and FQVY
                axr1 = axes[0,1]
                axr1.set_ylim(0,30)
                axr1.set_ylabel('WVP [kg/m²]')

                axr2 = axes[1,1]
                axr2.set_ylim(-0.1,0.1)
                axr2.set_ylabel('mean QV flux 0-3 km [kg/m²]')
                axr2.axhline(y=0, color='black', linewidth=1)

                # EQPOTT
                axr2r = axr2.twinx()
                axr2r.set_ylim(-30,0)

                rlat = an.vars['nTOT_PREC'].ncos[model].dims['rlat'].vals
                rlon = an.vars['nTOT_PREC'].ncos[model].dims['rlon'].vals
                alt = an.vars['zQV'].ncos[model].dims['altitude'].vals

                TOT_PREC = an.vars['nTOT_PREC'].ncos[model].field.vals.squeeze()
                WVP_0_2 = an.vars['zWVP_0_2'].ncos[model].field.vals.squeeze()
                WVP_2_4 = an.vars['zWVP_2_4'].ncos[model].field.vals.squeeze()
                T = an.vars['zT'].ncos[model].field.vals.squeeze()
                P = an.vars['zP'].ncos[model].field.vals.squeeze()
                POTT = T*(100000/P)**(287/1005)
                POTT_prof = np.nanmean(POTT, axis=1)
                EQPOTT = an.vars['zEQPOTT'].ncos[model].field.vals.squeeze()
                EQPOTT_diff = EQPOTT[49,:] - np.nanmean(EQPOTT[:31,:], axis=0)
                EQPOTT_prof = np.nanmean(EQPOTT,axis=1)
                FQVY = an.vars['zFQVY'].ncos[model].field.vals.squeeze()
                FQVY_agg = np.nanmean(FQVY[0:31], axis=0)
                FQVY_converg = -np.diff(FQVY_agg)
                from scipy.signal import savgol_filter
                FQVY_converg = savgol_filter(FQVY_converg, 19,3)*3
                rlat_centred = rlat[:-1] + np.diff(rlat)/2.
                QV = an.vars['zQV'].ncos[model].field.vals.squeeze()
                nhor = QV.shape[1]
                QV = np.nansum(QV,axis=1)/nhor
                if len(lat) == 2:
                    for i in range(len(TOT_PREC)-1):
                        rect = patches.Rectangle((rlat[i],0),
                                        width=rlat[i+1]-rlat[i], height=TOT_PREC[i]/10,
                                        color='white')
                        ax.add_patch(rect)
                    ## WVP
                    line, = axr1.plot(rlat, WVP_0_2, label=model+' WVP 0-2km',
                                    color=models_meta[model]['col'], linestyle='-')
                    lines.append(line)
                    line, = axr1.plot(rlat, WVP_2_4, label=model+' WVP 2-4km',
                                    color=models_meta[model]['col'], linestyle='--')
                    lines.append(line)

                    if time_mode == 'diurnal':
                        line, = axr1.plot(rlat, WVP_0_2+WVP_2_4, label=model+' ',
                                        color=models_meta[model]['col'], linestyle=':')

                    axr1.set_xlim(rlat[0],rlat[-1])
                    axr1.text(rlat[int(len(rlat)*0.5)], y0+y_shift,
                                'mean 0-2: {:2.1f}'.format(np.mean(WVP_0_2)),
                                color=models_meta[model]['col'])
                    y_shift -= 4
                    axr1.text(rlat[int(len(rlat)*0.5)], y0+y_shift,
                                'mean 2-4: {:2.1f}'.format(np.mean(WVP_2_4)),
                                color=models_meta[model]['col'])
                    y_shift += 2

                    ## FQVY_agg
                    axr2.set_xlim(rlat[0],rlat[-1])
                    line, = axr2.plot(rlat, FQVY_agg, label=model+' ',
                                    color=models_meta[model]['col'], linestyle='-')
                    line, = axr2.plot(rlat_centred, FQVY_converg, label=model+' ',
                                    color=models_meta[model]['col'], linestyle=':')

                    ## EQPOTT_diff
                    line, = axr2r.plot(rlat, EQPOTT_diff, label=model+' WVP 2-4km',
                                    color=models_meta[model]['col'], linestyle='--')

                    # TOPO
                    if model == 'RAW1':
                        topo = an.vars['cHSURF'].ncos[model].field.vals.squeeze()
                        axr1.fill_between(rlat, 0, topo/5000*30, color=(0.5,0.5,0.5,0.5))
                        axr2.fill_between(rlat, -0.1, topo/5000*0.2-0.1, color=(0.5,0.5,0.5,0.5))

                    # QV Profile
                    ax_raw_prof.plot(QV,alt, color=models_meta[model]['col'])
                    ## EQPOTT_prof
                    ax_sm_prof.plot(EQPOTT_prof,alt, color=models_meta[model]['col'])
                    ## POTT_prof
                    ax_sm_prof.plot(POTT_prof,alt, color=models_meta[model]['col'],
                                    linestyle='--')


                elif len(lon) == 2:
                    for i in range(len(TOT_PREC)-1):
                        rect = patches.Rectangle((rlon[i],0),
                                        width=rlon[i+1]-rlon[i], height=TOT_PREC[i]/10,
                                        color='white')
                        ax.add_patch(rect)

            axlegend.legend(handles=lines)
            ax_raw_prof.grid()
            ax_sm_prof.grid()
            axr1.grid()
            axr2.grid()

            if time_mode == 'ts':
                qc_tick = 0.1
            elif time_mode == 'diurnal':
                qc_tick = 0.05

            qv_tick = 8

            if case in ['wv']:
                ncs.addContour(an.vars['zQC'], 'purple', 0.8, 2, ticks=[qc_tick])
            elif case in ['rh', 'mixing']:
                ncs.addContour(an.vars['zQC'], 'darkgreen', 0.8, 2, ticks=[qc_tick])

            if case == 'wv':
                ncs.addContour(an.vars['zQV'], 'black', 1, 1.0, ticks=[qv_tick])

                
        elif nDPlot == 1 and someField.nNoneSingleton == 1:

            for fldName in an.fieldNames:
                if fldName != 'cHSURF':
                    ncs.plotVar1D(an.vars[fldName])

        else:
            raise ValueError('ERROR: CANNOT MAKE ' + str(nDPlot) + 'D-PLOT WITH ' +
            str(someField.nNoneSingleton) + ' NON-SINGLETON DIMS!')

        ncs.fig.set_size_inches(20,12)
        for ax in ncs.axes.flatten()[:2]:
            ax.set_ylim(0,subSpaceIndsIN['altitude'][-1]/10)
        plt.subplots_adjust(top=0.86, left=0.05, right=0.95, wspace=0.5)



        if len(lat) == 2:
            title = str(dt) + ' lon: ' + str(lon[0])
        elif len(lon) == 2:
            title = str(dt) + ' lat: ' + str(lat[0])
        ncs.fig.suptitle(title, fontsize=28)


        if i_plot == 1:
            plt.show()
        elif i_plot == 2:
            plotPath = plotOutDir + '/' + plotName
            #print(plotPath)
            plt.savefig(plotPath, format='png', bbox_inches='tight')
            plt.close(ncs.fig.number)


