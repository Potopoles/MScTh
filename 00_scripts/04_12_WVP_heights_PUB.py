# Calculate domain Average Precipitation
# author: Christoph Heim
# date: 21 10 2017
# last changed: 12.11.2019
#################################
import os
os.chdir('00_scripts/')

i_resolutions = 5 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 0 # 0 = no plot, 1 = show plot, 2 = save plot
i_info = 2 # output some information [from 0 (off) to 5 (all you can read)]

labelsize = 22
timelabelsize = 25
titlesize = 28
tick_labelsize = 18
suptitle_size = 35

xpos_time = 578
ypos_time = 228

import matplotlib
if i_plot == 2:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


from pathlib import Path
import ncClasses.analysis as analysis
from datetime import datetime
from functions import *
####################### NAMELIST INPUTS FILES #######################
# directory of input model folders
inpPath = '../02_fields/diurnal'

var = 'WVP'
#var = 'LWP'

panel_labels = ['c)', 'd)']
#panel_labels = ['a)', 'b)']

plot_vars = ['z'+var+'_2_10']
plot_vars = ['z'+var+'_0_2']
#plot_vars = ['z'+var+'_0_4']
#plot_vars = ['z'+var+'_2_4']
#plot_vars = ['z'+var+'_4_10']
#plot_vars = ['z'+var+'_0_10']
#plot_vars = ['z'+var+'_0_2','z'+var+'_2_4','z'+var+'_4_10']

vars_meta = {
    'zWVP_0_4':{
        'Mticks':np.arange(10,35,1.0),
        'path_append':'0_4',
        'title_append':'0-4 km',
    },
    'zWVP_0_2':{
        'Mticks':np.arange(7,21.1,0.5),
        'path_append':'0_2',
        'title_append':'0-2 km',
    },
    'zWVP_2_4':{
        'Mticks':np.arange(5,15,0.5),
        'path_append':'2_4',
        'title_append':'2-4 km',
    },
    'zWVP_4_10':{
        'Mticks':np.arange(3,9,0.2),
        'path_append':'4_10',
        'title_append':'4-10 km',
    },
    'zWVP_2_10':{
        #'Mticks':np.arange(10,22,0.5),
        'Mticks':np.arange(7,21.1,0.5),
        'path_append':'2_10',
        'title_append':'2-10 km',
    },
    'zWVP_0_10':{
        'Mticks':np.arange(20,38.1,1),
        'path_append':'0_10',
        'title_append':'0-10 km',
    },
    'zLWP_0_2':{
        'Mticks':np.arange(0.1,2,0.05),
        'path_append':'0_2',
        'title_append':'0-2 km',
    },
    'zLWP_2_4':{
        'Mticks':np.arange(0.1,2,0.05),
        'path_append':'2_4',
        'title_append':'2-4 km',
    },
    'zLWP_4_10':{
        'Mticks':np.arange(0.1,2,0.05),
        'path_append':'4_10',
        'title_append':'4-10 km',
    },
    'zLWP_0_10':{
        'Mticks':np.arange(0.1,2,0.05),
        'path_append':'0_10',
        'title_append':'0-10 km',
    },
}


fieldNames = ['cHSURF']
fieldNames.extend(plot_vars)
#####################################################################		

models = ['SM1', 'RAW1']

####################### NAMELIST DIMENSIONS #######################
#TODO
subDomain = 3 # 0: full domain, 1: alpine region, 2: zoom in
# SUBSPACE
subSpaceIndsIN = {}
if subDomain == 1: # alpine region
    subSpaceIndsIN['rlon'] = [50,237]
    subSpaceIndsIN['rlat'] = [41,155]
elif subDomain == 2: # italy region
    subSpaceIndsIN['rlon'] = [80,180]
    subSpaceIndsIN['rlat'] = [50,120]
elif subDomain == 3: # Po Valley domain
    subSpaceIndsIN['rlon'] = [102,150]
    subSpaceIndsIN['rlat'] = [65,97]


subSpaceIndsIN['diurnal'] = list(range(0,24))
#subSpaceIndsIN['diurnal'] = list(range(0,1))
#####################################################################

####################### NAMELIST AGGREGATE #######################
# Options: MEAN, SUM, DIURNAL
ag_commnds = {}
#####################################################################

####################### NAMELIST PLOT #######################
nDPlot = 2 # How many dimensions should plot have (1 or 2)
i_diffPlot = 0 # Draw plot showing difference filtered - unfiltered # TODO
if len(plot_vars) == 1:
    widthStretch = 13.8
    heightStretch = 7
elif len(plot_vars) == 3:
    widthStretch = 14.5
    heightStretch = 16
#####################################################################
an = analysis.analysis(inpPath, fieldNames)
an.subSpaceInds = subSpaceIndsIN
an.ag_commnds = ag_commnds
an.i_info = i_info
an.i_resolutions = i_resolutions
# RUN ANALYSIS
an.run()

if len(plot_vars) > 1:
    plotOutDir = Path(os.path.join('..','00_plots','04_coldPools','wvp_heights',
                        'together'))
else:
    plotOutDir = Path(os.path.join('..','00_plots','04_coldPools','wvp_heights',
                        vars_meta[plot_vars[0]]['path_append']))
plotOutDir.mkdir(parents=True, exist_ok=True)
dts = ['{num:02d}'.format(num=hour) for hour in \
            an.vars[plot_vars[0]].ncos['RAW1'].dims['diurnal'].vals]

import matplotlib
if i_plot == 2:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt

for tI,dhr in enumerate(subSpaceIndsIN['diurnal']):
    print('######### time ' + str(tI))
    plot_name = var+'_'+dts[tI]
    dhr_string = '{:02d}00 UTC'.format(dhr)

    fig, axes = plt.subplots(len(plot_vars), 2, 
                    figsize=(widthStretch,heightStretch))

    #if len(plot_vars) > 1:
    plt.suptitle(var+' [kg/m²]'+' at '+
                str(dts[tI])+'00 UTC ', fontsize=suptitle_size)

    for vI,plot_var in enumerate(plot_vars):
        print('\t'+plot_var)

        if len(plot_var) == 1:
            plt.suptitle(var+' '+vars_meta[plot_var]['title_append']+':'+
                        str(dts[tI])+'00 UTC ', fontsize=suptitle_size)

        lind = 0
        for mI,model in enumerate(models):
            if len(axes.shape) == 1:
                ax = axes[mI]
            else:
                ax = axes[vI,mI]
            ax.axis('equal')

            topo = an.vars['cHSURF'].ncos[model]
            dimx = topo.dims['rlon']
            dimy = topo.dims['rlat']
            tTicks = np.array([-100,0,100,200,500,1000,1500,2000,
                                2500,3000,3500,4000])
            ax.contourf(dimx.vals, dimy.vals, topo.field.vals, tTicks,
                cmap='binary', alpha=0.7)

            # time label
            ax.text(xpos_time,ypos_time,dhr_string,size=timelabelsize,color='black',
                            bbox=dict(boxstyle='square',ec=(1,1,1,0.5),fc=(1,1,1,0.5)))


            wvp = an.vars[plot_var].ncos[model].field.vals[tI,:,:]
            print(model + ' mean:')
            print(round(np.mean(wvp),2))
            CF = ax.contourf(dimx.vals, dimy.vals, wvp.squeeze(),
                vars_meta[plot_var]['Mticks'],
                cmap='jet', alpha=0.7)

            if len(plot_vars) > 1:
                ax.text(610,226,vars_meta[plot_var]['title_append'],
                        size=25,color='black',
                        bbox=dict(boxstyle='square',ec=(1,1,1,0.5),fc=(1,1,1,0.5)))

            #if tI == 0:
            #    ax.text(375,480,model,size=timelabelsize,color='black',
            #                    bbox=dict(boxstyle='square',ec=(1,1,1,0.5),fc=(1,1,1,0.5)))
            if vI == 0:
                ax.set_title(model, fontsize=timelabelsize)

            if vI == len(plot_vars)-1:
                ax.set_xlabel('x $[km]$',fontsize=labelsize)
            if mI == 0:
                ax.set_ylabel('y $[km]$',fontsize=labelsize)

            ax.tick_params(labelsize=tick_labelsize)

            if len(plot_vars) > 1:
                divider = make_axes_locatable(ax)
                cax = divider.append_axes('right', size='5%', pad=0.05)
                MCB = fig.colorbar(mappable=CF, cax=cax, orientation='vertical')
                cax.tick_params(labelsize=tick_labelsize)
                #MCB.set_label('Water Vapor Path $[kg$ $m^{-2}]$',fontsize=labelsize)

            # make panel label
            pan_lab_x = ax.get_xlim()[0] - (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.00
            pan_lab_y = ax.get_ylim()[1] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.03
            ax.text(pan_lab_x,pan_lab_y,panel_labels[lind], fontsize=20, weight='bold')
            lind += 1

        if len(plot_vars) == 1:
            # colorbar
            xPosLeft = 0.10
            cPosBot = 0.12
            width = 0.80
            cHeight = 0.04
            cax = fig.add_axes([xPosLeft, cPosBot, width, cHeight])
            MCB = plt.colorbar(mappable=CF, cax=cax, orientation='horizontal')
            cax.tick_params(labelsize=tick_labelsize)
            if var == 'WVP':
                #MCB.set_label('Water Vapor Path $[kg$ $m^{-2}]$',fontsize=labelsize)
                MCB.set_label('Vertically Integrated Water Vapor $[kg$ $m^{-2}]$',
                            fontsize=labelsize)
            elif var == 'LWP':
                #MCB.set_label('Liquid Water Path $[kg$ $m^{-2}]$',fontsize=labelsize)
                MCB.set_label('Vertically Integrated Liquid Water$[kg$ $m^{-2}]$',
                            fontsize=labelsize)

    if len(plot_vars) == 1:
        fig.subplots_adjust(wspace=0.13, hspace=0.17,
                left=0.07, right=0.96, bottom=0.28, top=0.855)
    else:
        fig.subplots_adjust(wspace=0.25, hspace=0.17,
                left=0.07, right=0.94, bottom=0.05, top=0.90)

    if i_plot == 1:
        plt.show()
    elif i_plot == 2:
        plotPath = os.path.join(plotOutDir,plot_name+'.png')
        plt.savefig(plotPath, format='png', bbox_inches='tight')
        plt.close(fig.number)

