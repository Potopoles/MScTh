#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
orig: 00_scripts/11_00_summary_PUB.py
description	    Calculate summary plot for delayed onset and Po Valley night
                time precipitation.
author			Christoph Heim
date created    20.01.2019
date changed    31.10.2019
usage			no args
notes			Figure 12 in paper.
==============================================================================
"""
import os
from pathlib import Path
os.chdir('00_scripts/')

i_resolutions = 5 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 3 # 0 = no plot, 1 = show plot, 2 = save plot
i_info = 0 # output some information [from 0 (off) to 5 (all you can read)]
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

fieldNames = ['zFQVY', 'cHSURF']#, 'zQC']
#####################################################################		

####################### NAMELIST DIMENSIONS #######################
i_subDomain = 10 # 0: full domain, 1: alpine region
ssI, domainName = setSSI(i_subDomain, {'4':{}, '2':{}, '1':{}}) 

startHght = 0
endHght = 40
altInds = list(range(startHght,endHght+1))
ssI['altitude'] = altInds 

diurnals = [[9,10,11,12],
            [17,18],
            [23,0,1,2,3,4,5,6]]
diurnal_labels = ['0800-1200 UTC','1600-1800 UTC', '2200-0600 UTC']

plotName = 'summary'
plotOutDir = '../00_plots/12_summary'
Path(plotOutDir).mkdir(parents=True, exist_ok=True)
perc_topo = 0

plot_var = 'FQVY'

labelsize = 16
titlesize = 20
time_labelsize = 20
tick_labelsize = 14


def set_ax_props(ax, dimy, dimz):
    ax.set_ylim(np.min(dimz),np.max(dimz))
    ax.set_xlim(np.min(dimy),np.max(dimy))


#fig,axes_all = plt.subplots(4,3, figsize=(13,16))
#fig,axes_all = plt.subplots(2,3, figsize=(13,9.2))
fig,axes_all = plt.subplots(3,3, figsize=(11,11))
fig.subplots_adjust(wspace=0.15, hspace=0.50,
        left=0.05, right=0.95, bottom=0.15, top=0.90)


panel_labels = ['a)','b)', 'c)', 'd)', 'e)', 'f)', 'g)', 'h)', 'i)']
lind = 0
for dI in range(0,len(diurnals)):
    print(diurnals[dI])
    axes = axes_all[dI,:]

    if isinstance(diurnals[dI], list):
        ssI['diurnal'] = diurnals[dI]
    else:
        ssI['diurnal'] = [diurnals[dI]]

    an = analysis.analysis(inpPath, fieldNames)

    an.subSpaceInds = ssI
    an.ag_commnds = {}
    an.i_info = i_info
    an.i_resolutions = i_resolutions

    # RUN ANALYSIS
    an.run()

    res = an.resolutions[0]
    dx = an.grid_spacings[res]
    dz = 100
    
    dimx = an.vars['cHSURF'].ncos['RAW'+res].field.dims['rlon'].vals
    dimy = an.vars['cHSURF'].ncos['RAW'+res].field.dims['rlat'].vals
    dimz = an.vars['zFQVY'] .ncos['RAW'+res].field.dims['altitude'].vals
    dimd = an.vars['zFQVY'] .ncos['RAW'+res].field.dims['diurnal']


    RAW = {}
    SM = {}
    DIFF = {}
    lims = {}
    RAW['HSURF']    = np.ma.filled(an.vars['cHSURF'] .ncos['RAW'+res].field.vals,np.nan)/1000
    SM ['HSURF']    = np.ma.filled(an.vars['cHSURF'] .ncos['SM'+res] .field.vals,np.nan)/1000
    RAW['FQVY']     = np.ma.filled(an.vars['zFQVY']  .ncos['RAW'+res].field.vals,np.nan)*1000
    SM ['FQVY']     = np.ma.filled(an.vars['zFQVY']  .ncos['SM'+res] .field.vals,np.nan)*1000

    #### AGGREGATE X
    n_nan_x_RAW = np.sum(np.isnan(RAW['FQVY']),axis=3)
    n_nan_x_SM = np.sum(np.isnan(SM['FQVY']),axis=3)
    #RAW['FQVY'] = np.nansum(RAW['FQVY'], axis=3)/len(dimx)
    #SM ['FQVY'] = np.nansum(SM ['FQVY'], axis=3)/len(dimx)
    RAW['FQVY'] = np.nansum(RAW['FQVY'], axis=3)/(len(dimx) - n_nan_x_RAW)
    SM ['FQVY'] = np.nansum(SM ['FQVY'], axis=3)/(len(dimx) - n_nan_x_SM)
    RAW['FQVY'][np.isnan(RAW['FQVY'])] = 0.
    SM['FQVY'][np.isnan(SM['FQVY'])] = 0.

    #### AGGREGATE DIURNAL
    RAW['FQVY'] = np.mean(RAW['FQVY'], axis=0)
    SM ['FQVY'] = np.mean(SM ['FQVY'], axis=0)

    unit_FQVY  = '$g$ $m^{-2}$ $s^{-1}$'
    name_FQVY  = '$Q_{V}$ $Flux$'
    name_dFQVY = '$\Delta$ $Q_{V}$ $Flux$'

    ### CALCULATIONS
    #RAW['FQVY'] = RAW['FQVY']/dx
    #SM ['FQVY'] = SM ['FQVY']/dx
    #unit_FQVY = '$mm$ $h^{-1}$ $m_{z}^{-1}$'
    #name_FQVY = '$Q_{V}$ $Flux$'

    # DIFFERENCE
    DIFF['FQVY'] = RAW['FQVY'] - SM['FQVY']

    cmap_mod = 'seismic'
    lims[plot_var] = (min(np.min(RAW[plot_var]), np.min(SM[plot_var])), 
                     max(np.max(RAW[plot_var]), np.max(SM[plot_var])))
    levels_mod = np.linspace(-np.max(np.abs(lims[plot_var])),
                            np.max(np.abs(lims[plot_var])), 20)
    levels_diff = np.linspace(-np.max(np.abs(DIFF[plot_var])),
                            np.max(np.abs(DIFF[plot_var])), 20)
    # original with 2 labels
    levels_mod = np.arange(-40,41.1,2.0)
    levels_diff = np.arange(-20,20.1,1.0)
    #levels_mod = np.arange(-40,40.1,1.0)
    #levels_diff = np.arange(-40,40.1,1.0)
    unit = unit_FQVY; name = name_FQVY
    #levels_QC = [np.percentile(RAW['QC'], q=98)]
    #levels_QC = [0.02]

    SM[plot_var][SM[plot_var] < levels_mod[0]] = levels_mod[0]
    SM[plot_var][SM[plot_var] > levels_mod[-1]] = levels_mod[-1]
    RAW[plot_var][RAW[plot_var] < levels_mod[0]] = levels_mod[0]
    RAW[plot_var][RAW[plot_var] > levels_mod[-1]] = levels_mod[-1]
    DIFF[plot_var][DIFF[plot_var] < levels_diff[0]] = levels_diff[0]
    DIFF[plot_var][DIFF[plot_var] > levels_diff[-1]] = levels_diff[-1]


    ##################################################################
    # SMOOTH
    ##################################################################
    ax = axes[0]
    if dI == 0:
        ax.text(-0.15,1.25,diurnal_labels[dI], transform=ax.transAxes, size=time_labelsize)
    else:
        ax.text(-0.15,1.20,diurnal_labels[dI], transform=ax.transAxes, size=time_labelsize)
    if dI == 0:
        ax.set_title('SM1', fontsize=titlesize)
    CF = ax.contourf(dimy, dimz, SM[plot_var], cmap=cmap_mod, levels=levels_mod)
    #ax.contour(dimy, dimz, SM['CONV'], levels=levels_CONV, colors='green', linewidths=1)
    ax.plot(dimy, SM['HSURF'].mean(axis=1), '-k')
    #ax.plot(dimy, np.percentile(SM['HSURF'], axis=1, q=perc_topo), '-k',
    #        linewidth=0.8)
    ax.fill_between(dimy, 0, np.percentile(SM['HSURF'], axis=1, q=perc_topo), color='k')
    #if np.nanmax(SM['QC']) >= np.min(levels_QC):
    #    ax.contour(dimy, dimz, SM['QC'], levels=levels_QC, colors='orange', linewidths=1)
    set_ax_props(ax, dimy, dimz)
    ax.tick_params(labelsize=tick_labelsize)
    ax.set_ylabel('Altitude [km]', fontsize=labelsize)
    if dI == len(diurnals)-1:
        ax.set_xlabel('Latitude [km]', fontsize=labelsize)

    # make panel label
    pan_lab_x = ax.get_xlim()[0] - (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.00
    pan_lab_y = ax.get_ylim()[1] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05
    ax.text(pan_lab_x,pan_lab_y,panel_labels[lind], fontsize=15, weight='bold')
    lind += 1

    ##################################################################
    # RAW
    ##################################################################
    ax = axes[1]
    if dI == 0:
        ax.set_title('RAW1', fontsize=titlesize)
    ax.plot(dimy, RAW['HSURF'].mean(axis=1), '-k')
    CF = ax.contourf(dimy, dimz, RAW[plot_var], cmap=cmap_mod, levels=levels_mod)
    #ax.contour(dimy, dimz, RAW['CONV'], levels=levels_CONV, colors='green', linewidths=1)
    #ax.plot(dimy, np.percentile(RAW['HSURF'], axis=1, q=perc_topo), '-k',
    #        linewidth=0.8)
    ax.fill_between(dimy, 0, np.percentile(RAW['HSURF'], axis=1, q=perc_topo), color='k')
    #if np.nanmax(RAW['QC']) >= np.min(levels_QC):
    #    ax.contour(dimy, dimz, RAW['QC'], levels=levels_QC, colors='orange', linewidths=1)
    set_ax_props(ax, dimy, dimz)
    ax.tick_params(labelsize=tick_labelsize)
    if dI == len(diurnals)-1:
        ax.set_xlabel('Latitude [km]', fontsize=labelsize)

    # make panel label
    pan_lab_x = ax.get_xlim()[0] - (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.00
    pan_lab_y = ax.get_ylim()[1] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05
    ax.text(pan_lab_x,pan_lab_y,panel_labels[lind], fontsize=15, weight='bold')
    lind += 1

    ##################################################################
    # DIFF
    ##################################################################
    ax = axes[2]
    if dI == 0:
        ax.set_title('RAW1 - SM1', fontsize=titlesize)
    DCF = ax.contourf(dimy, dimz, DIFF[plot_var], cmap='PuOr_r', levels=levels_diff)
    ax.plot(dimy, SM['HSURF'].mean(axis=1), '-k')
    ax.plot(dimy, np.percentile(SM['HSURF'], axis=1, q=perc_topo), '-k',
            linewidth=0.8)
    #ax.plot(dimy, np.percentile(RAW['HSURF'], axis=1, q=perc_topo), '-k',
    #        linewidth=0.8)
    ax.fill_between(dimy, 0, np.percentile(RAW['HSURF'], axis=1, q=perc_topo), color='k')
    set_ax_props(ax, dimy, dimz)
    ax.tick_params(labelsize=tick_labelsize)
    if dI == len(diurnals)-1:
        ax.set_xlabel('Latitude [km]', fontsize=labelsize)

    # make panel label
    pan_lab_x = ax.get_xlim()[0] - (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.00
    pan_lab_y = ax.get_ylim()[1] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05
    ax.text(pan_lab_x,pan_lab_y,panel_labels[lind], fontsize=15, weight='bold')
    lind += 1



####COLORBARS
cPosBot = 0.05
xPosLeft = 0.07
width = 0.55
cHeight = 0.03

cax = fig.add_axes([xPosLeft, cPosBot, width, cHeight])
cax.tick_params(labelsize=tick_labelsize)
CB = plt.colorbar(mappable=CF, cax=cax,
            orientation='horizontal')
CB.set_label(name + ' ['+unit+']',fontsize=labelsize)


cax = fig.add_axes([0.69, cPosBot, 0.25, cHeight])
cax.tick_params(labelsize=tick_labelsize)
DCB = plt.colorbar(mappable=DCF, cax=cax,
            orientation='horizontal')
#DCB.set_ticks(np.arange(-0.05,0.055,0.025))
DCB.set_label(name_dFQVY + ' ['+unit+']',fontsize=labelsize)




if i_plot == 1:
    plt.show()
elif i_plot == 2:
    plotPath = plotOutDir + '/' + plotName+'.png'
    print(plotPath)
    plt.savefig(plotPath, format='png', bbox_inches='tight')
    plt.close('all')
elif i_plot == 3:
    plotPath = plotOutDir + '/' + plotName+'.pdf'
    print(plotPath)
    plt.savefig(plotPath, format='pdf', bbox_inches='tight')
    plt.close('all')
#quit()

