################################
# Calculate domain Average Precipitation
# author: Christoph Heim
# date: 21 10 2017
#################################
import os
os.chdir('00_scripts/')

i_resolutions = 5 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 1 # 0 = no plot, 1 = show plot, 2 = save plot
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
#inpPath = '../02_fields/subDomDiur'
inpPath = '../02_fields/diurnal'
#inpPath = '../02_fields/topocut'

others = ['cHSURF', 'nTOT_PREC', 'nHPBL']
hydrometeors = ['zQC', 'zQI', 'zQV', 'zQR', 'zQS', 'zQG']
TTendencies = ['zATT_MIC', 'zATT_RAD', 'zATT_ADV', 'zATT_ZADV', 'zATT_TURB', 'zATT_TOT']
QVTendencies = ['zAQVT_MIC', 'zAQVT_ADV', 'zAQVT_ZADV', 'zAQVT_TURB', 'zAQVT_TOT']
dynamics = ['zW', 'zU', 'zV', 'zT', 'zP']
fieldNames = ['zU', 'cHSURF']
fieldNames = ['nTOT_PREC', 'cHSURF']
fieldNames = ['zAQVT_TURB']
fieldNames = ['nASHFL_S']
fieldNames = ['nALHFL_S']
fieldNames = ['cHSURF']
fieldNames = ['zQV']
fieldNames = ['zQV', 'cHSURF', 'zQC']
#fieldNames = ['zFQVy', 'cHSURF', 'zQV', 'zRHO']
#####################################################################		

####################### NAMELIST DIMENSIONS #######################
i_subDomain = 10 # 0: full domain, 1: alpine region
ssI, domainName = setSSI(i_subDomain, {'4.4':{}, '2.2':{}, '1.1':{}}) 
#print(ssI)
#quit() ## PROBLEM WITH SUBDOMAIN!!!

startHght = 0
endHght = 40
altInds = list(range(startHght,endHght+1))
ssI['altitude'] = altInds 

#startTime = datetime(2006,7,11,00)
#endTime = datetime(2006,7,20,23)
#ssI['time'] = [startTime,endTime] # border values (one value if only one time step desired)

#diurnals = [[9,10,11],
#            [16,17,18]]
#diurnal_labels = ['0800-1100 UTC','1500-1800 UTC']
#plotName = 'summary'


diurnals = [[9,10,11],
            [16,17,18]]
diurnal_labels = ['0800-1100 UTC','1500-1800 UTC']
plotName = 'summary'


plotOutDir = '../00_plots/12_summary'
perc_topo = 0

plot_var = 'FQVy'
plot_var = 'QV'

#models={'RAW':'RAW4', 'SM':'SM4'}
models={'RAW':'RAW1', 'SM':'SM1'}
#dx = 4400
dx = 1100
dz = 100


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

#plt.suptitle(diurnal_labels[dI])


for dI in range(0,len(diurnals)):
    print(diurnals[dI])
    axes = axes_all[dI,:]

    if isinstance(diurnals[dI], list):
        ssI['diurnal'] = diurnals[dI]
    else:
        ssI['diurnal'] = [diurnals[dI]]

    an = analysis.analysis(inpPath, fieldNames)

    #an.subSpaceInds = subSpaceInds
    an.subSpaceInds = ssI
    an.ag_commnds = {}
    an.i_info = i_info
    an.i_resolutions = i_resolutions

    # RUN ANALYSIS
    an.run()

    dimx = an.vars['cHSURF'].ncos[models['RAW']].field.dims['rlon'].vals
    dimy = an.vars['cHSURF'].ncos[models['RAW']].field.dims['rlat'].vals
    dimz = an.vars['zQV'].ncos[models['RAW']].field.dims['altitude'].vals
    dimd = an.vars['zQV'].ncos[models['RAW']].field.dims['diurnal']
    #dimd = [val.hour for val in an.vars['zQV'].ncos[models['RAW']].field.dims['time'].vals]

    RAW = {}
    SM = {}
    DIFF = {}
    lims = {}
    RAW['HSURF'] = an.vars['cHSURF'].ncos[models['RAW']].field.vals/1000
    SM['HSURF'] = an.vars['cHSURF'].ncos[models['SM']].field.vals/1000
    RAW['QV'] = an.vars['zQV'].ncos[models['RAW']].field.vals*1000
    SM['QV'] = an.vars['zQV'].ncos[models['SM']].field.vals*1000
    RAW['QC'] = an.vars['zQC'].ncos[models['RAW']].field.vals*1000
    SM['QC'] = an.vars['zQC'].ncos[models['SM']].field.vals*1000

    #### AGGREGATE X
    RAW['QV'] = np.nansum(RAW['QV'], axis=3)/len(dimx)
    SM['QV'] = np.nansum(SM['QV'], axis=3)/len(dimx)
    RAW['QC'] = np.nansum(RAW['QC'], axis=3)/len(dimx)
    SM['QC'] = np.nansum(SM['QC'], axis=3)/len(dimx)
    #### AGGREGATE DIURNAL
    RAW['QV'] = np.mean(RAW['QV'], axis=0)
    SM['QV'] = np.mean(SM['QV'], axis=0)
    RAW['QC'] = np.mean(RAW['QC'], axis=0)
    SM['QC'] = np.mean(SM['QC'], axis=0)


    ### CALCULATIONS
    # QV
    RAW['QV'] = RAW['QV']/dx
    SM['QV'] = SM['QV']/dx
    unit_QV = '$g$ $kg^{-1}$'
    name_QV = '$Q_{V}$'

    # DIFFERENCE
    DIFF['QV'] = RAW['QV'] - SM['QV']

    cmap_mod = 'jet'
    lims[plot_var] = (min(np.min(RAW[plot_var]), np.min(SM[plot_var])), 
                     max(np.max(RAW[plot_var]), np.max(SM[plot_var])))
    levels_mod = np.linspace(-np.max(np.abs(lims[plot_var])),
                            np.max(np.abs(lims[plot_var])), 20)
    levels_diff = np.linspace(-np.max(np.abs(DIFF[plot_var])),
                            np.max(np.abs(DIFF[plot_var])), 20)
    levels_mod = np.arange(0,0.011,0.0001)
    levels_diff = np.arange(-0.0035,0.00351,0.0002)
    unit = unit_QV; name = name_QV
    levels_QC = [0.02]


    # SMOOTH
    ax = axes[0]
    if dI == 0:
        ax.text(-0.15,1.25,diurnal_labels[dI], transform=ax.transAxes, size=time_labelsize)
    else:
        ax.text(-0.15,1.15,diurnal_labels[dI], transform=ax.transAxes, size=time_labelsize)
    if dI == 0:
        ax.set_title('SM1.1', fontsize=titlesize)
    CF = ax.contourf(dimy, dimz, SM[plot_var], cmap=cmap_mod, levels=levels_mod)
    #ax.contour(dimy, dimz, SM['CONV'], levels=levels_CONV, colors='green', linewidths=1)
    ax.plot(dimy, SM['HSURF'].mean(axis=1), '-k')
    #ax.plot(dimy, np.percentile(SM['HSURF'], axis=1, q=perc_topo), '-k',
    #        linewidth=0.8)
    ax.fill_between(dimy, 0, np.percentile(SM['HSURF'], axis=1, q=perc_topo), color='k')
    if np.nanmax(SM['QC']) >= np.min(levels_QC):
        ax.contour(dimy, dimz, SM['QC'], levels=levels_QC, colors='orange', linewidths=1)
    set_ax_props(ax, dimy, dimz)
    ax.tick_params(labelsize=tick_labelsize)
    ax.set_ylabel('Altitude [km]', fontsize=labelsize)
    if dI == len(diurnals)-1:
        ax.set_xlabel('Latitude [km]', fontsize=labelsize)


    # RAW
    ax = axes[1]
    if dI == 0:
        ax.set_title('RAW1.1', fontsize=titlesize)
    ax.plot(dimy, RAW['HSURF'].mean(axis=1), '-k')
    CF = ax.contourf(dimy, dimz, RAW[plot_var], cmap=cmap_mod, levels=levels_mod)
    #ax.contour(dimy, dimz, RAW['CONV'], levels=levels_CONV, colors='green', linewidths=1)
    #ax.plot(dimy, np.percentile(RAW['HSURF'], axis=1, q=perc_topo), '-k',
    #        linewidth=0.8)
    ax.fill_between(dimy, 0, np.percentile(RAW['HSURF'], axis=1, q=perc_topo), color='k')
    if np.nanmax(RAW['QC']) >= np.min(levels_QC):
        ax.contour(dimy, dimz, RAW['QC'], levels=levels_QC, colors='orange', linewidths=1)
    set_ax_props(ax, dimy, dimz)
    ax.tick_params(labelsize=tick_labelsize)
    if dI == len(diurnals)-1:
        ax.set_xlabel('Latitude [km]', fontsize=labelsize)

    # DIFF
    ax = axes[2]
    if dI == 0:
        ax.set_title('RAW1.1 - SM1.1', fontsize=titlesize)
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
#DCB.set_ticks(np.arange(-0.0035,0.00355,0.0020))
DCB.set_ticks([-0.0030,0,0.0030])
DCB.set_label(name + ' ['+unit+']',fontsize=labelsize)




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

