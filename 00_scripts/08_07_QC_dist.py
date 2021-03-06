#################################
# Calculate domain Average Precipitation
# author: Christoph Heim
# date: 21 10 2017
#################################
import os
os.chdir('00_scripts/')

i_resolutions = 3 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 3 # 0 = no plot, 1 = show plot, 2 = save plot
i_info = 2 # output some information [from 0 (off) to 5 (all you can read)]
altInds = [10,20,30,40,50,60,61,62,63,64]
altInds = [43]
#altInds = [50]

import matplotlib
if i_plot > 1:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt


import ncClasses.analysis as analysis
from datetime import datetime
from functions import *
####################### NAMELIST INPUTS FILES #######################
# directory of input model folders
inpPath = '../02_fields/topocut'

others = ['cHSURF', 'nTOT_PREC', 'nHPBL']
hydrometeors = ['zQC', 'zQI', 'zQV', 'zQR', 'zQS', 'zQG']
TTendencies = ['zATT_MIC', 'zATT_RAD', 'zATT_ADV', 'zATT_ZADV', 'zATT_TURB', 'zATT_TOT']
QVTendencies = ['zAQVT_MIC', 'zAQVT_ADV', 'zAQVT_ZADV', 'zAQVT_TURB', 'zAQVT_TOT']
dynamics = ['zW', 'zU', 'zV', 'zT', 'zP']
fieldNames = ['zQC']
#fieldNames = ['zQV']
#####################################################################		

####################### NAMELIST DIMENSIONS #######################
subDomain = 1 # 0: full domain, 1: alpine region
# SUBSPACE
subSpaceInds = {}
if subDomain == 0: # (use topocut) 
    domainName = 'Whole_Domain'
if subDomain == 1: 
    domainName = 'Alpine_Region'
    if inpPath == '../02_fields/topocut': # (in case of topocut)
        subSpaceInds['rlon'] = [50,237]
        subSpaceInds['rlat'] = [41,155]
    else: # (in case of subDomDiur) 
        pass


startTime = datetime(2006,7,11,0)
endTime = datetime(2006,7,19,23)
#endTime = datetime(2006,7,12,23)
subSpaceInds['time'] = [startTime,endTime] # border values
for startHght in altInds:
    #startHght = 40
    print('##########################################    ' + str(startHght))
    #startHght = 40
    endHght = startHght 
    subSpaceInds['altitude'] = list(range(startHght,endHght+1))
    #####################################################################

    ag_commnds = {}
    an = analysis.analysis(inpPath, fieldNames)

    an.subSpaceInds = subSpaceInds
    an.ag_commnds = ag_commnds
    an.i_info = i_info
    an.i_resolutions = i_resolutions

    # RUN ANALYSIS
    an.run()

    if startHght > 60:
        altitude = 6000 + (startHght-60)*1000
    else:
        altitude = startHght*100

    outPath = '../00_plots/08_cloud_cluster/'

    an.vars['zQC'].setValueLimits()
    binMin = 0
    binMax = an.vars['zQC'].max
    nbins = 50
    bins = np.linspace(binMin,binMax,num=nbins)
    binsCentred = bins[0:(len(bins)-1)] + np.diff(bins)/2

    freqs = {}
    nPoints = {}
    outRess = []
    outModes = []

    for res in an.resolutions: 
        for mode in an.modes:
            simLabel = str(res)+mode
            print(simLabel)
            vals = an.vars['zQC'].ncos[str(res)+mode].field.vals
            vals = vals.flatten()
            vals = vals[~np.isnan(vals)] # remove mountains

            # CREATE HISTOGRAMS
            nPoint = np.histogram(vals, bins=bins)[0]
            #nPoints.append(nPoint[0]) 
            nPoints[simLabel] = nPoint
            freq = nPoint/len(vals)
            #freqs.append(freq)
            freqs[simLabel] = freq
            outRess.append(str(res))
            outModes.append(mode)

    colrs = [(0,0,0), (0,0,1), (1,0,0)]
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(11,4))
    handles = []
    modeStrings = ['SM', 'RAW', '(RAW - SM)/SM']
    xmin = binMin
    xmax = binMax
    ymin = 1E-8
    ymax = 1E0
    labelsize = 12
    titlesize = 14

    for rI,res in enumerate(an.resolutions): 
        # SMOOTH
        ax = axes[0]
        line, = ax.semilogy(binsCentred, freqs[str(res)+'f'], color=colrs[rI]) 
        handles.append(line)

        # RAW
        ax = axes[1]
        ax.semilogy(binsCentred, freqs[str(res)+''], color=colrs[rI]) 

        # DELTA
        ax = axes[2]
        minSamples = 30
        nRaw = nPoints[str(res)+'']
        nSm = nPoints[str(res)+'f']
        mask = np.full(len(nRaw),1)
        mask[nRaw < minSamples] = 0
        mask[nSm < minSamples] = 0
        raw = freqs[str(res)+'']
        sm = freqs[str(res)+'f']
        raw[raw == 0] = np.nan
        sm[sm == 0] = np.nan
        ratio = (raw - sm)/sm
        ratio[mask == 0] = np.nan
        ax.plot(binsCentred, ratio, color=colrs[rI]) 

    for mI,mode in enumerate(['','f','d']):
        # SMOOTH
        ax = axes[mI]
        ax.set_xlabel('Concentration [$kg$ $kg^{-1}$]',fontsize=labelsize)
        if mI == 0:
            ax.set_ylabel('Frequency',fontsize=labelsize)
            ax.legend(handles,an.resolutions)
        ax.set_xlim((xmin,xmax))
        if mI < 2:
            ax.set_ylim((ymin,ymax))
        else:
            ax.set_ylim((-0.8,0.8))
        ax.axvline(x=0, color='k', lineWidth=0.5)
        ax.axhline(y=0, color='k', lineWidth=0.5)
        ax.set_title(modeStrings[mI],fontsize=titlesize)
        ax.grid()


    fig.subplots_adjust(wspace=0.23,left=0.07, right=0.95, bottom=0.15, top=0.85)


    if i_plot == 2:
        outName = 'QC_dist_and_diff_alt_'+str(altitude)+'_NEW.png'
        plt.savefig(outPath + outName)
    elif i_plot == 3:
        outName = 'QC_dist_and_diff_alt_'+str(altitude)+'_NEW.pdf'
        #outName = 'QV_dist_and_diff_alt_'+str(altitude)+'_NEW.pdf'
        plt.savefig(outPath + outName)
    elif i_plot == 1:
        plt.show()
    plt.close(fig)
