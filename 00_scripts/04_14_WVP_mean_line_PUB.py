#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
description	    Plot diurnal cycle of water vapor path over Po Valley.
author			Christoph Heim
date created    03.03.2020
date changed    03.03.2020
usage			no args
"""
##############################################################################
import os
os.chdir('00_scripts/')

i_resolutions = 3 # 1 = 4.4, 2 = 4.4 + 2.2, 3 = ...
i_plot = 1 # 0 = no plot, 1 = show plot, 2 = save plot
i_info = 0

import matplotlib.pyplot as plt
import ncClasses.analysis as analysis
from datetime import datetime, timedelta
from functions import *
import xarray as xr
from package.domains import *
from package.utilities import calc_mean_diurnal_cycle, dt64_to_dt
####################### NAMELIST INPUTS FILES #######################
# directory of input model folders
#inpPath = '../02_fields/topocut'
#WVP_heights = '0_10'
WVP_heights = '0_2'
##WVP_heights = '2_4'
##WVP_heights = '4_10'
##WVP_heights = '2_10'
plotName = 'WVP_line_'+WVP_heights
var_name = 'WVP_'+WVP_heights

if i_resolutions == 3:
    ress = ['4', '2', '1']
elif i_resolutions == 2:
    ress = ['4', '2']
elif i_resolutions == 1:
    ress = ['4']
elif i_resolutions == 5:
    ress = ['1']
cols = {'4':'black','2':'blue','1':'red'}
mkeys = ['SM', 'RAW', 'RAW - SM']
dom = dom_northern_italy

start_time = datetime(2006,7,11)
end_time = datetime(2006,7,19)
percentiles = [15, 85]

labelsize = 14
titlesize = 16

members = {}
members_diurn = {}
for res in ress:
    for mkey in ['RAW', 'SM']:
        skey = '{}{}'.format(mkey, res)
        input_file = os.path.join('..','01_rawData','topocut',skey,
                                'calc',var_name+'.nc')
        with xr.open_dataset(input_file) as ds:
            ds = ds.sel(rlon=dom['lon'], rlat=dom['lat'])
            ds = ds.mean(dim=['rlon','rlat'])
            ds = ds.isel(time=range(1,len(ds.time.values)))
            var = ds[var_name]
            #plt.plot(var.values)
            #plt.show()
            var_diurn = calc_mean_diurnal_cycle(var)
            members[skey] = var
            members_diurn[skey] = var_diurn


# compute diff
for res in ress:
    diff_key = 'RAW - SM{}'.format(res)
    raw_key = 'RAW{}'.format(res)
    sm_key = 'SM{}'.format(res)
    members[diff_key] = members[raw_key] - members[sm_key]
    members_diurn[diff_key] = members_diurn[raw_key] - members_diurn[sm_key]

hours = np.arange(0,25)
fig,axes = plt.subplots(1,3, figsize=(11,3.7))

plot_out_dir = '../00_plots/04_coldPools/wvp_heights'

for colI in range(3):
    mkey = mkeys[colI]
    ax = axes[colI]
    handles = []
    for res in ress:
        skey = '{}{}'.format(mkey, res)
        vals = members[skey]
        vals_diurn = members_diurn[skey]
        vals_diurn = np.append(vals_diurn, vals_diurn[0])
        
        line, = ax.plot(hours, vals_diurn, label=skey, color=cols[res])
        handles.append(line)

    ax.set_xlim((0,24))
    ax.set_xticks(np.arange(0,24.1,6))
    if colI < 2:
        pass
        ax.set_ylim((0,18))
        #ax.set_yticks(np.arange(-0.05,0.16,0.05))
    else:
        pass
        #ax.set_ylim((-0.04,0.06))

    if res == '1':
        day_range = np.arange(start_time, end_time+timedelta(days=1), 
                                timedelta(days=1))
        all_days = np.zeros((9,25))
        for dayI in range(len(day_range)-2):
            this_day = '{:%Y-%m-%d}-00'.format(dt64_to_dt(
                            day_range[dayI]))
            next_day = '{:%Y-%m-%d}-00'.format(dt64_to_dt(
                            day_range[dayI+1]))
            day_vals = vals.loc[this_day:next_day].values
            times = vals.loc[this_day:next_day].time.values
            if (len(day_vals) == 24) and (dt64_to_dt(times[0]).hour == 1):
                day_vals = np.append(day_vals[-1], day_vals)
            all_days[dayI,:] = day_vals
        #for dayI in range(len(day_range)-1):
        #    ax.plot(hours, all_days[dayI,:], color=plot_dict['res_color'][res],
        #            label=mem_res_key, linewidth=0.5)
        quantiles = np.percentile(all_days, percentiles, axis=0)
        ax.fill_between(hours, quantiles[0,:], quantiles[1,:], color='red',
                        alpha=0.2, edgecolor='')
        # significance testing
        #test_type = 'ttest'
        test_type = 'wilcox'
        if test_type == 'ttest':
            from scipy.stats import ttest_1samp
        if test_type == 'wilcox':
            from scipy.stats import wilcoxon
        if mkey == 'RAW - SM':
            for hI in range(len(hours)-1):
                if test_type == 'ttest':
                    pval = ttest_1samp(all_days[:,hI], 0).pvalue
                elif test_type == 'wilcox':
                    pval = wilcoxon(all_days[:,hI].squeeze()).pvalue
                #pval = '{:2.2f}'.format(pval)
                if (pval < 0.05):
                    plot_hr = hours[hI]
                    if plot_hr == 0: plot_hr = 24
                    ax.text(plot_hr-0.5, ax.get_ylim()[1]*0.92,
                            '*', color='red')

    if colI < 2:
        ax.legend(handles=handles)
    if colI == 0:
        ax.set_ylabel('Vertical integral of $q_v$ $[kg$ $m^{-2}]$',
                        fontsize=labelsize)
    ax.set_xlabel('Time (UTC)',fontsize=labelsize)
    ax.text(0,ax.get_ylim()[1] + (ax.get_ylim()[1] - ax.get_ylim()[0])*0.03,
            ['d)','e)','f)'][colI], weight='bold', fontsize=15)
    ax.grid()
    ax.axhline(y=0, color='k')
    #ax.set_title(mkey,fontsize=titlesize)



#fig.set_size_inches((12,4))
fig.subplots_adjust(wspace=0.23, hspace=0.3,
        left=0.08, right=0.98, bottom=0.16, top=0.90)
plt.savefig('{}/{}.pdf'.format(plot_out_dir,plotName), format='pdf')
plt.savefig('{}/{}.png'.format(plot_out_dir,plotName), format='png')
plt.show()
