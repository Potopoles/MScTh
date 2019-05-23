#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
title			:summary.py
description	    :Calculate summary plot for delayed onset and Po Valley night
                 time precip.
author			:Christoph Heim
date created    :20190120 
date changed    :20190521
usage			:no args
notes			:Figure 10 in paper.
python_version	:3.7.1
==============================================================================
"""
import os
from pathlib import Path
os.chdir('00_scripts/')

i_resolutions = 5 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 2 # 0 = no plot, 1 = show plot, 2 = save plot
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
ssI, domainName = setSSI(i_subDomain, {'4.4':{}, '2.2':{}, '1.1':{}}) 

startHght = 0
endHght = 40
altInds = list(range(startHght,endHght+1))
ssI['altitude'] = altInds 

diurnals = [[9,10,11],
            [16,17,18]]
diurnal_labels = ['0800-1100 UTC','1500-1800 UTC']

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
fig,axes_all = plt.subplots(2,3, figsize=(13,9.2))
fig.subplots_adjust(wspace=0.15, hspace=0.45,
        left=0.05, right=0.95, bottom=0.25, top=0.85)


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
    RAW['HSURF']    = an.vars['cHSURF'] .ncos['RAW'+res].field.vals/1000
    SM ['HSURF']    = an.vars['cHSURF'] .ncos['SM'+res].field.vals/1000
    RAW['FQVY']     = an.vars['zFQVY']  .ncos['RAW'+res].field.vals*1000
    SM ['FQVY']     = an.vars['zFQVY']  .ncos['SM'+res].field.vals*1000
    #RAW['QC']       = an.vars['zQC']    .ncos['RAW'+res].field.vals*1000
    #SM['QC']        = an.vars['zQC']    .ncos['SM'+res].field.vals*1000

    #### AGGREGATE X
    RAW['FQVY'] = np.nansum(RAW['FQVY'], axis=3)/len(dimx)
    SM ['FQVY'] = np.nansum(SM ['FQVY'], axis=3)/len(dimx)
    #RAW['QC'] = np.nansum(RAW['QC'], axis=3)/len(dimx)
    #SM['QC'] = np.nansum(SM['QC'], axis=3)/len(dimx)

    #### AGGREGATE DIURNAL
    RAW['FQVY'] = np.mean(RAW['FQVY'], axis=0)
    SM ['FQVY'] = np.mean(SM ['FQVY'], axis=0)
    #RAW['QC'] = np.mean(RAW['QC'], axis=0)
    #SM['QC'] = np.mean(SM['QC'], axis=0)

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
    #levels_mod = np.arange(-0.13,0.14,0.005)
    #levels_diff = np.arange(-0.05,0.055,0.005)
    levels_mod = np.arange(-35,35.1,1.0)
    levels_diff = np.arange(-15,15.1,1.0)
    unit = unit_FQVY; name = name_FQVY
    #levels_QC = [np.percentile(RAW['QC'], q=98)]
    #levels_QC = [0.02]


    # SMOOTH
    ax = axes[0]
    if dI == 0:
        ax.text(-0.15,1.25,diurnal_labels[dI], transform=ax.transAxes, size=time_labelsize)
    else:
        ax.text(-0.15,1.15,diurnal_labels[dI], transform=ax.transAxes, size=time_labelsize)
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


    # RAW
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

    # DIFF
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



####COLORBARS
cPosBot = 0.12
xPosLeft = 0.07
width = 0.55
cHeight = 0.05

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
    plt.savefig(plotPath, format='png', bbox_inches='tight')
    plt.close('all')
elif i_plot == 3:
    plotPath = plotOutDir + '/' + plotName+'.pdf'
    plt.savefig(plotPath, format='pdf', bbox_inches='tight')
    plt.close('all')
#quit()

