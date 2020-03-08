from datetime import datetime, timedelta
import numpy as np
import os
os.chdir('00_newScripts/')

from functions import loadObj 

ress = ['4', '2', '1']
#ress = ['4', '2']
#ress = ['4']
modes = ['SM', 'RAW', 'RAW-SM']
#i_variables = 'QV' # 'QV' or 'T'
#i_variables = 'T' # 'QV' or 'T'

region = 'Alpine_Region'
#region = 'Northern_Italy'
#region = 'Northern_Italy2'
#region = 'Alpine_Ridge'

#altitudes = '0_1500'
#altitudes = '0_2000'
#altitudes = '2000_6000'
#altitudes = '1500_3000'
#altitudes = '1500_3000'
altitudes = '0_2500'

path = 'alts_'+altitudes+'_'+region
folder = '../06_bulk/vertSlab/' + path
plotOutDir = '../00_plots/06_bulk'
if not os.path.exists(plotOutDir):
    os.mkdir(plotOutDir)

i_plot = 1


modeNames = ['SM', 'RAW', 'RAW - SM']

i_walls = ['left', 'right', 'top', 'bottom']
i_walls = ['bottom', 'top']
i_MODE = 'SUM'
#i_MODE = 'bottom'
#i_MODE = 'top'
#i_MODE = 'left'
#i_MODE = 'right'

if i_MODE == 'SUM':
    plotName = 'vertSlab_'+path+'_all'
else:
    plotName = 'vertSlab_'+path+'_'+i_MODE

import matplotlib
if i_plot == 2:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt

var = 'Fqv' 
titleVar = 'WV Flux'
#unit = r'Vapor Flux $[10^6$ $kg$ $s^{-1}]$'
unit = r'Vapor Flux $[mm$ $h^{-1}]$'

colrs = [(0,0,0), (0,0,1), (1,0,0)]
labelsize = 12
titlesize = 14

Area = None

# PREAPRE DATA FOR PLOTTING
out = {}
out['hrs'] = np.arange(0,25)
max = -np.Inf
min = np.Inf
for res in ress:
    for mode in modes[0:2]:
        if i_MODE == 'SUM':
            vals = None
            for i_wall in i_walls:
                name = var+'_'+i_wall+'_'+res+mode
                obj = loadObj(folder,name)  
                if res == '4' and Area is None:
                    #print(obj)
                    Area = obj['Area']*1E6
                if vals is None:
                    #vals = obj[var]/1E6
                    vals = obj[var]/Area*3600
                else:
                    #vals = vals + obj[var]/1E6
                    #if (i_wall == 'top') or (i_wall == 'bottom'):
                    #    vals = vals + obj[var]/Area*3600
                    #else:
                    vals = vals + obj[var]/Area*3600
        else:
            name = var+'_'+i_MODE+'_'+res+mode
            obj = loadObj(folder,name)  
            vals = obj[var]/1E6

        dates = obj['time'].astype(datetime)

        # MEAN DIURNAL
        #vals = obj[var]
        hrs = np.arange(0,24)
        hrVals = np.full(len(hrs), np.nan)
        for hr in hrs:
            inds = [i for i in range(0,len(dates)) if dates[i].hour == hr]
            hrVals[hr] = np.mean(vals[inds])

        hrVals = np.append(hrVals, hrVals[0])
        out[res+mode] = hrVals
        max = np.max(hrVals) if np.max(hrVals) > max else max
        min = np.min(hrVals) if np.min(hrVals) < min else min
    
    # CALCUALTE DIFFERENCE
    increase = np.abs(max-min)*0.03
    max = max+increase
    min = min-increase
    diff_key = res+'RAW-SM'
    out[diff_key] = out[res+'RAW'] - out[res+'SM']
    maxd = np.max(out[diff_key])
    mind = np.min(out[diff_key])
    max = np.max(out[diff_key]) if np.max(out[diff_key]) > max else max
    min = np.min(out[diff_key]) if np.min(out[diff_key]) < min else min
    #min = -40
    #max = 30
    #min = -0.4
    #max = 0.3


# PLOT
fig,axes = plt.subplots(1,3, figsize=(11,4))
for axI,mode in enumerate(modes):
    ax = axes[axI]
    lines = []
    for resI,res in enumerate(ress):
        line, = ax.plot(out['hrs'], out[res+mode], color=colrs[resI])
        lines.append(line)

    if axI == 0:
        ax.legend(lines, labels=ress)
    ax.axhline(y=0, color='k', lineWidth=1)
    ax.set_xticks([0,6,12,18,24])
    ax.set_xlim((0,24))
    ax.set_xlabel('Hour',fontsize=labelsize)
    if axI == 0:
        ax.set_ylabel(unit,fontsize=labelsize)
    if mode != 'd':
        ax.set_ylim((min,max))
    else:
        #centre = (max + min)*0.5
        #centred = (maxd + mind)*0.5
        #d = centred - centre
        #ax.set_ylim((min+d, max+d))
        ax.set_ylim((min,max))
    ax.grid()
    ax.set_title(modeNames[axI],fontsize=titlesize)


    #day_range = np.arange(start_time, end_time+timedelta(days=1), timedelta(days=1))
    #all_days = np.zeros((9,25))
    #hours = np.arange(0, 25)
    #for dayI in range(len(day_range)-1):
    #    this_day = '{:%Y-%m-%d}-00'.format(dt64_to_dt(day_range[dayI]))
    #    next_day = '{:%Y-%m-%d}-00'.format(dt64_to_dt(day_range[dayI+1]))
    #    vals = vals_disagg.loc[this_day:next_day].values
    #    all_days[dayI,:] = vals
    ##for dayI in range(len(day_range)-1):
    ##    ax.plot(hours, all_days[dayI,:], color=plot_dict['res_color'][res],
    ##            label=mem_res_key, linewidth=0.5)
    #quantiles = np.percentile(all_days, percentiles, axis=0)
    #ax.fill_between(hours, quantiles[0,:], quantiles[1,:], color='red',
    #                alpha=0.2, edgecolor='')
    ## t-test
    ##test_type = 'ttest'
    #test_type = 'wilcox'
    #if test_type == 'ttest':
    #    from scipy.stats import ttest_1samp
    #if test_type == 'wilcox':
    #    from scipy.stats import wilcoxon
    #if mem_key == 'DIFF':
    #    for hI in range(len(hours)-1):
    #        if test_type == 'ttest':
    #            pval = ttest_1samp(all_days[:,hI], 0).pvalue
    #        elif test_type == 'wilcox':
    #            pval = wilcoxon(all_days[:,hI].squeeze()).pvalue
    #        #pval = '{:2.2f}'.format(pval)
    #        if pval < 0.05:
    #            ax.text(hours[hI]-0.5, 0.15, '*')


#if i_MODE == 'SUM':
#    fig.suptitle(titleVar + ' into '+ obj['domainName'] + ' through all sidewalls between ' + altitudes + ' m.')
#else:
#    fig.suptitle(titleVar + ' into '+ obj['domainName'] + ' through '+i_MODE+' sidewall between ' + altitudes + ' m.')
fig.subplots_adjust(wspace=0.23,
        left=0.07, right=0.95, bottom=0.15, top=0.85)

plotPath = plotOutDir + '/' + plotName
print('plot path {}'.format(plotPath))
if i_plot == 1:
    plt.show()
    plt.close(fig)
elif i_plot == 2:
    plt.savefig('{}.png'.format(plotPath), format='png', bbox_inches='tight')
    plt.close(fig)
elif i_plot == 3:
    plt.savefig('{}.pdf'.format(plotPath), format='pdf', bbox_inches='tight')
    plt.close('all')

    
