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
fieldNames = ['zFQVy', 'cHSURF', 'zQC']
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

diurnals = list(range(8,24))
diurnals.extend(list(range(0,8)))
#diurnals = [10]

diurnals = [list(range(0,24))]
# good ones
diurnals = [[22,23,0,1,2,3,4,5,6,7,8]]
diurnals = [[9,10,11,12,13]]
diurnals = [[14,15]]
diurnals = [[16,17,18]]

diurnals = [[9,10,11,12,13],
            [14,15],
            [17,18],
            [22,23,0,1,2,3,4,5,6,7,8]]
diurnal_labels = ['a) 08:00-13:00','b) 13:00-15:00','c) 16:00-18:00','d) 21:00-08:00']


plotOutDir = '../00_plots/12_summary'
perc_topo = 0

plot_var = 'FQVy'
#plot_var = 'QV'

def set_ax_props(ax, dimy, dimz):
    ax.set_ylim(np.min(dimz),np.max(dimz))
    ax.set_xlim(np.min(dimy),np.max(dimy))


fig,axes_all = plt.subplots(4,3, figsize=(13,16))
fig.subplots_adjust(wspace=0.2, hspace=0.5,
        left=0.05, right=0.95, bottom=0.25, top=0.90)

#plt.suptitle(diurnal_labels[dI])


for dI in range(0,len(diurnals)):
    print(diurnals[dI])
    axes = axes_all[dI,:]

    if isinstance(diurnals[dI], list):
        ssI['diurnal'] = diurnals[dI]
    else:
        ssI['diurnal'] = [diurnals[dI]]
    #plotName = plot_var+'_'+str(dI)+'_'+str(ssI['diurnal'][0])+'.png'
    plotName = 'summary'

    an = analysis.analysis(inpPath, fieldNames)

    #an.subSpaceInds = subSpaceInds
    an.subSpaceInds = ssI
    an.ag_commnds = {}
    an.i_info = i_info
    an.i_resolutions = i_resolutions

    # RUN ANALYSIS
    an.run()

    res = '1.1'
    #res = '4.4'
    dx = float(res)*1000
    dz = 100

    dimx = an.vars['cHSURF'].ncos[res].field.dims['rlon'].vals
    dimy = an.vars['cHSURF'].ncos[res].field.dims['rlat'].vals
    dimz = an.vars['zFQVy'].ncos[res].field.dims['altitude'].vals
    dimd = an.vars['zFQVy'].ncos[res].field.dims['diurnal'].vals

    RAW = {}
    SM = {}
    DIFF = {}
    lims = {}
    RAW['HSURF'] = an.vars['cHSURF'].ncos[res].field.vals
    SM['HSURF'] = an.vars['cHSURF'].ncos[res+'f'].field.vals
    RAW['FQVy'] = an.vars['zFQVy'].ncos[res].field.vals*3600
    SM['FQVy'] = an.vars['zFQVy'].ncos[res+'f'].field.vals*3600
    RAW['QC'] = an.vars['zQC'].ncos[res].field.vals*3600
    SM['QC'] = an.vars['zQC'].ncos[res+'f'].field.vals*3600
    #RAW['QV'] = an.vars['zQV'].ncos[res].field.vals * \
    #                    an.vars['zRHO'].ncos[res].field.vals
    #SM['QV'] = an.vars['zQV'].ncos[res+'f'].field.vals * \
    #                    an.vars['zRHO'].ncos[res+'f'].field.vals


    #### AGGREGATE X
    RAW['FQVy'] = np.nansum(RAW['FQVy'], axis=3)/len(dimx)
    SM['FQVy'] = np.nansum(SM['FQVy'], axis=3)/len(dimx)
    RAW['QC'] = np.nansum(RAW['QC'], axis=3)/len(dimx)
    SM['QC'] = np.nansum(SM['QC'], axis=3)/len(dimx)
    #RAW['QV'] = np.nansum(RAW['QV'], axis=3)/len(dimx)
    #SM['QV'] = np.nansum(SM['QV'], axis=3)/len(dimx)
    #### AGGREGATE DIURNAL
    RAW['FQVy'] = np.mean(RAW['FQVy'], axis=0)
    SM['FQVy'] = np.mean(SM['FQVy'], axis=0)
    RAW['QC'] = np.mean(RAW['QC'], axis=0)
    SM['QC'] = np.mean(SM['QC'], axis=0)
    #RAW['QV'] = np.mean(RAW['QV'], axis=0)
    #SM['QV'] = np.mean(SM['QV'], axis=0)


    ### CALCULATIONS
    # FQVy
    RAW['FQVy'] = RAW['FQVy']/dx
    SM['FQVy'] = SM['FQVy']/dx
    unit_FQVy = '$mm$ $h^{-1}$ $m_{z}^{-1}$'
    name_FQVy = '$Q_{V}$ $Flux$'
    # QV
    unit_QV = '$mm$ $m_{z}^{-1}$'
    name_QV = '$Q_{V}$'
    # CONVERGENCE
    #RAW['CONV'] = np.zeros(RAW['FQVy'].shape)
    #RAW['CONV'][:,1:-1] = -(RAW['FQVy'][:,2:] - RAW['FQVy'][:,:-2])/(2*dx)
    #RAW['CONV'][:,3:-3] = -(RAW['FQVy'][:,6:] - RAW['FQVy'][:,:-6])/(10*dx)
    #SM['CONV'] = np.zeros(SM['FQVy'].shape)
    #SM['CONV'][:,1:-1] = -(SM['FQVy'][:,2:] - SM['FQVy'][:,:-2])/(2*dx)
    #SM['CONV'][:,3:-3] = -(SM['FQVy'][:,6:] - SM['FQVy'][:,:-6])/(10*dx)


    # DIFFERENCE
    DIFF['FQVy'] = RAW['FQVy'] - SM['FQVy']
    #DIFF['QV'] = RAW['QV'] - SM['QV']



    if plot_var == 'FQVy':
        cmap_mod = 'seismic'
        lims[plot_var] = (min(np.min(RAW[plot_var]), np.min(SM[plot_var])), 
                         max(np.max(RAW[plot_var]), np.max(SM[plot_var])))
        levels_mod = np.linspace(-np.max(np.abs(lims[plot_var])),
                                np.max(np.abs(lims[plot_var])), 20)
        levels_diff = np.linspace(-np.max(np.abs(DIFF[plot_var])),
                                np.max(np.abs(DIFF[plot_var])), 20)
        levels_mod = np.arange(-0.20,0.21,0.01)
        levels_diff = np.arange(-0.1,0.105,0.005)
        unit = unit_FQVy; name = name_FQVy
        levels_QC = [np.percentile(RAW['QC'], q=98)]
        levels_QC = [0.07]
        #levels_CONV = [2E-6]
        #quit()
    elif plot_var == 'QV':
        cmap_mod = 'jet'
        lims[plot_var] = (min(np.min(RAW[plot_var]), np.min(SM[plot_var])), 
                         max(np.max(RAW[plot_var]), np.max(SM[plot_var])))
        levels_mod = np.linspace(-np.max(np.abs(lims[plot_var])),
                                np.max(np.abs(lims[plot_var])), 20)
        levels_diff = np.linspace(-np.max(np.abs(DIFF[plot_var])),
                                np.max(np.abs(DIFF[plot_var])), 20)
        levels_mod = np.arange(0,0.015,0.00025)
        levels_diff = np.arange(-0.005,0.005,0.0005)
        unit = unit_QV; name = name_QV


    # SMOOTH
    ax = axes[0]
    ax.text(-0.1,1.1,diurnal_labels[dI], transform=ax.transAxes, size=15)
    CF = ax.contourf(dimy, dimz, SM[plot_var], cmap=cmap_mod, levels=levels_mod)
    #ax.contour(dimy, dimz, SM['CONV'], levels=levels_CONV, colors='green', linewidths=1)
    ax.plot(dimy, SM['HSURF'].mean(axis=1), '-k')
    #ax.plot(dimy, np.percentile(SM['HSURF'], axis=1, q=perc_topo), '-k',
    #        linewidth=0.8)
    ax.fill_between(dimy, 0, np.percentile(SM['HSURF'], axis=1, q=perc_topo), color='k')
    if np.nanmax(SM['QC']) >= np.min(levels_QC):
        ax.contour(dimy, dimz, SM['QC'], levels=levels_QC, colors='orange', linewidths=1)
    set_ax_props(ax, dimy, dimz)
    # RAW
    ax = axes[1]
    ax.plot(dimy, RAW['HSURF'].mean(axis=1), '-k')
    CF = ax.contourf(dimy, dimz, RAW[plot_var], cmap=cmap_mod, levels=levels_mod)
    #ax.contour(dimy, dimz, RAW['CONV'], levels=levels_CONV, colors='green', linewidths=1)
    #ax.plot(dimy, np.percentile(RAW['HSURF'], axis=1, q=perc_topo), '-k',
    #        linewidth=0.8)
    ax.fill_between(dimy, 0, np.percentile(RAW['HSURF'], axis=1, q=perc_topo), color='k')
    if np.nanmax(RAW['QC']) >= np.min(levels_QC):
        ax.contour(dimy, dimz, RAW['QC'], levels=levels_QC, colors='orange', linewidths=1)
    set_ax_props(ax, dimy, dimz)
    # DIFF
    ax = axes[2]
    DCF = ax.contourf(dimy, dimz, DIFF[plot_var], cmap='seismic', levels=levels_diff)
    ax.plot(dimy, SM['HSURF'].mean(axis=1), '-k')
    ax.plot(dimy, np.percentile(SM['HSURF'], axis=1, q=perc_topo), '-k',
            linewidth=0.8)
    #ax.plot(dimy, np.percentile(RAW['HSURF'], axis=1, q=perc_topo), '-k',
    #        linewidth=0.8)
    ax.fill_between(dimy, 0, np.percentile(RAW['HSURF'], axis=1, q=perc_topo), color='k')
    set_ax_props(ax, dimy, dimz)



####COLORBARS
cPosBot = 0.12
xPosLeft = 0.1
width = 0.55
cHeight = 0.05

cax = fig.add_axes([xPosLeft, cPosBot, width, cHeight])
CB = plt.colorbar(mappable=CF, cax=cax,
            orientation='horizontal')
#cax.tick_params(labelsize=9)
CB.set_label(name + ' ['+unit+']')


cax = fig.add_axes([0.7, cPosBot, 0.25, cHeight])
DCB = plt.colorbar(mappable=DCF, cax=cax,
            orientation='horizontal')
#fldUnits = self._getUnits(fld)
DCB.set_label(name + ' ['+unit+']')




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

