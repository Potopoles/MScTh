from datetime import datetime, timedelta
import numpy as np
import os
os.chdir('00_newScripts/')

from functions import loadObj 

ress = ['4.4', '2.2', '1.1']
ress = ['4.4', '2.2']
ress = ['2.2']
ress = ['4.4']
modes = ['f', '', 'd']

i_plot = 1

path = 'alts_0_2500_Alpine_Region'
path = 'alts_0_2000_Northern_Italy'
#path = 'alts_0_10000_Northern_Italy'
#path = 'alts_0_10000_Alpine_Region'

#path = 'alts_3000_7000_Northern_Italy'
#path = 'alts_0_2000_Alpine_Region'
#path = 'alts_0_3000_Alpine_Region'
#vars = ['AQVT_TOT', 'AQVT_ADV', 'AQVT_HADV', 'AQVT_ZADV', 'AQVT_TURB', 'AQVT_MIC'] 

###########################################
#varGroup = 'AQVT'
#plotName = 'AQVT'
##vars = ['AQVT_TOT', 'AQVT_ADV', 'AQVT_TURB', 'AQVT_MIC']
#vars = ['AQVT_TOT', 'AQVT_ADV', 'AQVT_TURB', 'AQVT_MIC', 'AQVT_HADV']
##ltypes = ['-', '-', ':', '--']
#ltypes = ['-', '-', ':', '--', ':']
##lwidths = [1.8,0.8,1,1]
#lwidths = [1.8,0.8,1,1,2]
##varLabels = ['TOT', 'ADV', 'TURB', 'MIC']
#varLabels = ['TOT', 'ADV', 'TURB', 'MIC', 'HADV']
#unit = r'$[h^{-1}]$'
#ylabel = 'Net Moistening '+unit
#fact = 3600
#minm = -5E-8*fact
#maxm = 6E-8*fact
#mind = -1E-8*fact
#maxd = 1E-8*fact
###########################################
#varGroup = 'ATT'
#plotName = 'ATT'
#vars = ['ATT_TOT', 'ATT_ADV', 'ATT_TURB', 'ATT_MIC']
#ltypes = ['-', '-', ':', '--']
#lwidths = [1.8,0.8,1,1]
#varLabels = ['TOT', 'ADV', 'TURB', 'MIC']
#unit = r'$[K$ $h^{-1}]$'
#ylabel = 'Net Heating '+unit
#fact = 3600
#minm = -1E-4*fact
#maxm = 2E-4*fact
#mind = -2E-5*fact
#maxd = 2E-5*fact
##########################################
#varGroup = 'AQVT'
#plotName = 'AQVT_ADVSEP'
#vars = ['AQVT_ADV', 'AQVT_HADV', 'AQVT_ZADV']
#ltypes = ['-', '--', ':']
#lwidths = [1,1,1]
#varLabels = ['ADV', 'HADV', 'ZADV']
#unit = r'$[h^{-1}]$'
#ylabel = 'Net Moistening '+unit
#fact = 3600
#minm = -12E-8*fact
#maxm = 8E-8*fact
#mind = -3E-8*fact
#maxd = 3E-8*fact
##########################################
#varGroup = 'ATT'
#plotName = 'ATT_ADVSEP'
#vars = ['ATT_ADV', 'ATT_HADV', 'ATT_ZADV']
#ltypes = ['-', '--', ':']
#lwidths = [1,1,1]
#varLabels = ['ADV', 'HADV', 'ZADV']
#unit = r'$[K$ $h^{-1}]$'
#ylabel = 'Net Heating '+unit
#fact = 3600
#minm = -3E-4*fact
#maxm = 3E-4*fact
#mind = -1E-4*fact
#maxd = 1E-4*fact
##########################################
## NORTHERN ITALY PLAINS
#varGroup = 'AQVT'
#plotName = 'AQVT_Northern_Italy'
#vars = ['AQVT_TOT', 'AQVT_ADV', 'AQVT_TURB', 'AQVT_MIC']
#ltypes = ['-', '-', ':', '--']
#lwidths = [1.8,0.8,1,1]
#varLabels = ['TOT', 'ADV', 'TURB', 'MIC']
#unit = r'$[h^{-1}]$'
#ylabel = 'Net Moistening '+unit
#fact = 3600
#minm = -7E-8*fact
#maxm = 7E-8*fact
#mind = -4E-8*fact
#maxd = 4E-8*fact
##########################################
## NORTHERN ITALY PLAINS SEPARATION
#varGroup = 'AQVT'
#plotName = 'AQVT_ADVSEP_Northern_Italy'
#vars = ['AQVT_ADV', 'AQVT_HADV', 'AQVT_ZADV']
#ltypes = ['-', '--', ':']
#lwidths = [1,1,1]
#varLabels = ['ADV', 'HADV', 'ZADV']
#unit = r'$[h^{-1}]$'
#ylabel = 'Net Moistening '+unit
#fact = 3600
#minm = -12E-8*fact
#maxm = 8E-8*fact
#mind = -4E-8*fact
#maxd = 4E-8*fact



##########################################
varGroup = 'AQVT'
plotName = 'AQVT'
#vars = ['AQVT_TOT', 'AQVT_ADV', 'AQVT_TURB', 'AQVT_MIC']
vars = ['AQVT_TOT', 'AQVT_ADV', 'AQVT_TURB', 'AQVT_MIC', 'AQVT_HADV']
#ltypes = ['-', '-', ':', '--']
ltypes = ['-', '-', ':', '--', ':']
#lwidths = [1.8,0.8,1,1]
lwidths = [1.8,0.8,1,1,2]
#varLabels = ['TOT', 'ADV', 'TURB', 'MIC']
varLabels = ['TOT', 'ADV', 'TURB', 'MIC', 'HADV']
unit = r'$[h^{-1}]$'
ylabel = 'Net Moistening '+unit
fact = 1
minm = -1*fact
maxm = 1*fact
mind = -1*fact
maxd = 1*fact
##########################################



folder = '../06_bulk/' + path
plotOutDir = '../00_plots/06_bulk/'+path
if not os.path.exists(plotOutDir):
    os.mkdir(plotOutDir)
modeNames = ['SM', 'RAW', 'RAW - SM']

colrs = [(0,0,0), (0,0,1), (1,0,0)]
labelsize = 12
titlesize = 14

import matplotlib
if i_plot > 1:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt

# PLOT
fig,axes = plt.subplots(1,3, figsize=(12,4))


varLegendLines = []
for varI,var in enumerate(vars):
    print(var)

    # PREAPRE DATA FOR PLOTTING
    out = {}
    out['hrs'] = np.arange(0,25)
    max = -np.Inf
    min = np.Inf
    for res in ress:
        print(res)
        for mode in modes[0:2]:
            name = varGroup+'_'+res+mode
            obj = loadObj(folder,name)  
            dates = obj['time'].astype(datetime)


            # MEAN DIURNAL
            vals = obj[var]*fact
            hrs = np.arange(0,24)
            hrVals = np.full(len(hrs), np.nan)
            for hr in hrs:
                inds = [i for i in range(0,len(dates)) if dates[i].hour == hr]
                hrVals[hr] = np.mean(vals[inds])

            hrVals = np.append(hrVals, hrVals[0])
            hrs = np.append(hrs, 25)
            out[res+mode] = hrVals
            out['hrs'] = hrs

        # CALCUALTE DIFFERENCE
        out[res+'d'] = out[res+''] - out[res+'f']
        print(np.nanmean(out[res+'d']))
        print(np.nanmean(out[res+'']))
        print(np.nanmean(out[res+'f']))



    ## PLOT
    #for axI,mode in enumerate(modes):
    #    print(mode)
    #    ax = axes[axI]
    #    lines = []
    #    for resI,res in enumerate(ress):
    #        if mode == 'd' and res == '4.4':
    #            pass
    #        else:
    #            line, = ax.plot(out['hrs'], out[res+mode], linestyle=ltypes[varI],
    #                            color=colrs[resI], lineWidth=lwidths[varI])
    #        lines.append(line)
    #        if (axI == 0) and (resI == 0):
    #            varLegendLines.append(line)

quit()


for axI,mode in enumerate(modes):
    ax = axes[axI]
    if axI == 1:
        ax.legend(lines, labels=ress)
    elif axI == 0:
        leg = ax.legend(varLegendLines, labels=varLabels)
        for i in range(0,len(vars)):
            leg.legendHandles[i].set_color('k')
            leg.legendHandles[i].set_linestyle(ltypes[i])
            leg.legendHandles[i].set_linewidth(lwidths[i])

    ax.axhline(y=0, color='k', lineWidth=1)
    ax.set_xticks([0,6,12,18,24])
    ax.set_xlim((0,24))
   
    #from matplotlib.ticker import FormatStrFormatter
    #ax.yaxis.set_major_formatter(FormatStrFormatter('%.2E'))
    from matplotlib.ticker import ScalarFormatter
    yfmt = ScalarFormatter()
    yfmt.set_powerlimits((-3,3))
    ax.yaxis.set_major_formatter(yfmt)

    if axI == 0:
        ax.set_ylabel(ylabel,fontsize=labelsize)
    ax.set_xlabel('Hour',fontsize=labelsize)

    if axI == 2:
        ax.set_ylim((mind,maxd))
    else:
        ax.set_ylim((minm,maxm))
    ax.grid()
    ax.set_title(modeNames[axI])

#fig.suptitle(var + ' ' + path)
fig.subplots_adjust(wspace=0.23,
        left=0.07, right=0.96, bottom=0.15, top=0.85)



if i_plot == 1:
    plt.show()
    plt.close(fig)
elif i_plot == 2:
    plotPath = plotOutDir + '/' + plotName+'.png'
    plt.savefig(plotPath, format='png', bbox_inches='tight')
    plt.close(fig)
elif i_plot == 3:
    plotPath = plotOutDir + '/' + plotName+'.pdf'
    plt.savefig(plotPath, format='pdf', bbox_inches='tight')
    plt.close('all')

    
        
