#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
title			WVP_diurn.py
description	    Plot water vapor path over Po Valley.
author			Christoph Heim
date created    20190606
date changed    20190607
usage			no args
notes			
python_version	3.7.1
==============================================================================
"""
import os
os.chdir('00_scripts/')

i_resolutions = 5 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 2 # 0 = no plot, 1 = show plot, 2 = save plot
i_info = 2 # output some information [from 0 (off) to 5 (all you can read)]

widthStretch = 10.6
heightStretch = 4

xpos_mem = 340
ypos_mem = 430
xpos_time = 618
ypos_time = 228


labelsize = 28
timelabelsize = 25
member_label_size = 30
titlesize = 28
tick_labelsize = 18


import matplotlib
if i_plot == 2:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt

import ncClasses.analysis as analysis
from datetime import datetime
from functions import *
####################### NAMELIST INPUTS FILES #######################
# directory of input model folders
inpPath = '../02_fields/diurnal'
WVP_heights = '0_10'
Mticks = np.arange(20,38.1,1) 
WVP_heights = '0_2'
Mticks = np.arange(5,22,0.5)
WVP_heights = '2_4'
Mticks = np.arange(5,15,0.5)
WVP_heights = '4_10'
Mticks = np.arange(3,9,0.2)
plotName = 'WVP_'+WVP_heights+'_diurnal'
fieldNames = ['cHSURF', 'zWVP_'+WVP_heights]
#####################################################################		
diurn_hours = [8,12,16,20,0,4]

####################### NAMELIST DIMENSIONS #######################
subDomain = 2 # 0: full domain, 1: alpine region, 2: zoom in
# SUBSPACE
subSpaceIndsIN = {}
if subDomain == 1: # alpine region
    subSpaceIndsIN['rlon'] = [50,237]
    subSpaceIndsIN['rlat'] = [41,155]
elif subDomain == 2: # italy region
    subSpaceIndsIN['rlon'] = [80,180]
    subSpaceIndsIN['rlat'] = [50,120]
#####################################################################

####################### NAMELIST AGGREGATE #######################
# Options: MEAN, SUM, DIURNAL
ag_commnds = {}
#####################################################################

####################### NAMELIST PLOT #######################
nDPlot = 2 # How many dimensions should plot have (1 or 2)
i_diffPlot = 0 # Draw plot showing difference filtered - unfiltered # TODO
plotOutDir = '../00_plots/04_coldPools'
import os
if not os.path.exists(plotOutDir):
    os.makedirs(plotOutDir)

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

nts = len(diurn_hours)
fig, axes = plt.subplots(nts, 2, figsize=(widthStretch,nts*heightStretch))

dts = an.vars['zWVP_'+WVP_heights].ncos['RAW'+an.resolutions[0]].dims['diurnal'].vals
for tI,dhr in enumerate(diurn_hours):
    rI = tI
    dhr_string = '{:02d}00'.format(dhr)
    ########SMOOOTHED
    cI = 0
    ax = axes[rI,cI]
    ax.axis('equal')

    topo = an.vars['cHSURF'].ncos['SM'+an.resolutions[0]]
    dimx = topo.dims['rlon']
    dimy = topo.dims['rlat']
    tTicks = np.array([-100,0,100,200,500,1000,1500,2000,2500,3000,3500,4000,4500])
    ax.contourf(dimx.vals, dimy.vals, topo.field.vals, tTicks,
        cmap='binary', alpha=0.7)

    wvp = an.vars['zWVP_'+WVP_heights].ncos['SM'+an.resolutions[0]].field.vals[dhr,:,:]
    CF = ax.contourf(dimx.vals, dimy.vals, wvp.squeeze(), Mticks,
        cmap='jet', alpha=0.7)

    ax.text(xpos_time,ypos_time,dhr_string,size=timelabelsize,color='black',
                    bbox=dict(boxstyle='square',ec=(1,1,1,0.5),fc=(1,1,1,0.5)))

    if tI == 0:
        ax.text(xpos_mem,ypos_mem,'SM1',size=member_label_size,color='black',
                        bbox=dict(boxstyle='square',ec=(1,1,1,0.5),fc=(1,1,1,0.5)))

    if rI == nts-1:
        ax.set_xlabel('x $[km]$',fontsize=labelsize)
    if cI == 0:
        ax.set_ylabel('y $[km]$',fontsize=labelsize)

    ax.tick_params(labelsize=tick_labelsize)

    ############ RAW
    cI = 1
    ax = axes[rI,cI]
    ax.axis('equal')

    topo = an.vars['cHSURF'].ncos['RAW'+an.resolutions[0]]
    dimx = topo.dims['rlon']
    dimy = topo.dims['rlat']
    tTicks = np.array([-100,0,100,200,500,1000,1500,2000,2500,3000,3500,4000,4500])
    ax.contourf(dimx.vals, dimy.vals, topo.field.vals, tTicks,
        cmap='binary', alpha=0.7)

    wvp = an.vars['zWVP_'+WVP_heights].ncos['RAW'+an.resolutions[0]].field.vals[dhr,:,:]
    CF = ax.contourf(dimx.vals, dimy.vals, wvp.squeeze(), Mticks,
        cmap='jet', alpha=0.7)

    ax.text(xpos_time,ypos_time,dhr_string,size=timelabelsize,color='black',
                    bbox=dict(boxstyle='square',ec=(1,1,1,0.5),fc=(1,1,1,0.5)))

    if tI == 0:
        ax.text(xpos_mem,ypos_mem,'RAW1',size=member_label_size,color='black',
                bbox=dict(boxstyle='square',ec=(1,1,1,0.5),fc=(1,1,1,0.5)))

    if rI == nts-1:
        ax.set_xlabel('x $[km]$',fontsize=labelsize)
    if cI == 0:
        ax.set_ylabel('y $[km]$',fontsize=labelsize)

    ax.tick_params(labelsize=tick_labelsize)


    ############ colorbar
    xPosLeft = 0.10
    cPosBot = 0.05
    width = 0.80
    cHeight = 0.018
    cax = fig.add_axes([xPosLeft, cPosBot, width, cHeight])
    MCB = plt.colorbar(mappable=CF, cax=cax, orientation='horizontal')
    cax.tick_params(labelsize=tick_labelsize)
    MCB.set_label('Water Vapor Path $[kg$ $m^{-2}]$',fontsize=labelsize)


    fig.subplots_adjust(wspace=0.18, hspace=0.17,
            left=0.07, right=0.98, bottom=0.12, top=1.0)

if i_plot == 1:
    plt.show()
elif i_plot == 2:
    plotPath = plotOutDir + '/' + plotName+'.png'
    plt.savefig(plotPath, format='png', bbox_inches='tight')

