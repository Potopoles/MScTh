#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
description	    Diurnal cycle of precip plot final for publication
author			Christoph Heim
date created    29.01.2020
date changed    24.06.2020 
usage			no args
notes			Figure 11 in paper.
==============================================================================
"""
import os, time, pickle, copy
import xarray as xr
import numpy as np
from datetime import time as dttime
from datetime import datetime,timedelta
os.chdir('00_scripts/')
from package.utilities import dt64_to_dt, calc_mean_diurnal_cycle
import matplotlib.pyplot as plt


    
if __name__ == '__main__':
    ####################### NAMELIST INPUTS FILES #######################
    i_recompute_AR = 1
    #i_recompute_2 = 0
    pickle_save_file_AR  = 'data_15_AR.pkl'
    #pickle_save_file_2  = 'data_12_00_2.pkl'
    #pickle_save_file_3  = 'data_12_00_3.pkl'
    #pickle_save_file_4  = 'data_12_00_4.pkl'
    i_plot = 1
    i_save_fig = 0
    plot_path = os.path.join('..','00_plots', '15_precip_final')
    resolutions = ['4', '2', '1']
    #resolutions = ['4']
    member_types       = ['RAW', 'SM']
    #plot_name = 'diurnal_cycle_precip'


    ##dx = {'4':4400,'2':2200,'1':1100}

    #axes_dicts = {
    #    'W':{'col_ind':1,'row_ind':0},
    #    'E':{'col_ind':1,'row_ind':1},
    #    'N':{'col_ind':0,'row_ind':0},
    #    'S':{'col_ind':0,'row_ind':1},
    #    'TOT':{'col_ind':2,'row_ind':0},
    #    'DIFF':{'col_ind':2,'row_ind':1},
    #}

    inp_path = os.path.join('..','02_fields', 'topocut')

    start_time  = datetime(2006,7,11,0)
    end_time    = datetime(2006,7,20,0)

    labelsize = 12
    titlesize = 14

    dom_alpine_region = {
        'label':'Alpine Region',
        'rlon':(-3.76,3.68),
        'rlat':(-3.44,1.08),}


    #################### plotting
    plot_rows = [{'data_src':pickle_save_file_AR}]
    mem_keys = ['SM', 'RAW', 'DIFF']
    mem_labels = ['SM', 'RAW', 'RAW - SM']
    y_labels = [r'$q_v$-convergence $[mm$ $h^{-1}]$',
                r'Pressure Anomaly $[Pa]$',
                r'Temp. Anomaly $[K]$']
    ylims = [{'models':(-0.3,0.3),      'diff':(-0.3,0.3)},
             {'models':(-0.3,0.3),      'diff':(-0.3,0.3)},
             {'models':(-0.3,0.3),      'diff':(-0.3,0.3)}]
    
    percentiles = [15, 85]
    #percentiles = [20, 80]
    plot_dict = {
        'res_color'         :{'4':'black','2':'blue','1':'red'}, 
        'mem_linestyle'     :{'RAW':'-','SM':'--','DIFF':':'},
    }

    #time_chunk = 1


    #####################################################################		

    dt_range = np.arange(start_time, end_time+timedelta(hours=1),
                        timedelta(hours=1)).tolist()


    t_start = time.time()
    print('Loading')
    if i_recompute_AR:
        domain = dom_alpine_region

        ##################################
        members = {}
        # non diurnally aggregated:
        members_disagg = {}
        for res in resolutions:

            # load all members
            #n_nan_members = {}
            for member_type in member_types:
                member_str = member_type+str(res)
                print(member_str)
                path = os.path.join(inp_path, 'RAW'+str(res), 'nTOT_PREC.nc')
                field = xr.open_dataset(path, )['TOT_PREC']
                field = field.sel(rlon=slice(domain['rlon'][0],domain['rlon'][1]),
                                rlat=slice(domain['rlat'][0],domain['rlat'][1]))

                # select time and altitue
                field = field.sel(time=slice(start_time,end_time))

                # aggregate in horizontal dimesions
                field   = field.mean(dim=['rlon', 'rlat'])
                members_disagg[member_str] = field 

                #calculate diurnal cycle and store
                field = calc_mean_diurnal_cycle(field)
                members[member_str] = field

        # Calculate difference between RAW and SM
        for res in resolutions:
            RAW_str = 'RAW'+str(res)
            SM_str = 'SM'+str(res)
            DIFF_str = 'DIFF'+str(res)
            # diurnal
            diff = members[RAW_str] - members[SM_str]
            members[DIFF_str] = diff
            # disaggregated
            diff = members_disagg[RAW_str] - members_disagg[SM_str]
            members_disagg[DIFF_str] = diff

        data = {'disagg':members_disagg, 'agg':members}
        pickle.dump(data, open(pickle_save_file_AR, 'wb'))

        #########################################


    t_end = time.time()
    print('Computation complete. Took ' + 
            str(round(t_end - t_start,0)) + ' sec.')

    if i_plot: 
        hours = np.arange(0, 25)

        # 2 panels
        panel_labels = ['a)','d)', 'b)', 'e)', 'c)', 'f)', 'g)', 'h)', 'i)']
        # 3 panels
        panel_labels = ['a)','d)', 'g)', 'b)', 'e)', 'h)', 'c)', 'f)', 'i)']
        lind = 0
        #fig,axes = plt.subplots(1,3, figsize=(11,4))
        # 2 panels
        #fig,axes = plt.subplots(2,3, figsize=(11,7))
        # 3 panels
        fig,axes = plt.subplots(3,3, figsize=(11,11))
        for rowI,row_dict in enumerate(plot_rows):
            print(row_dict)
            # load data
            data = pickle.load(open(row_dict['data_src'], 'rb'))
            for colI in range(3):
                mem_key = mem_keys[colI]
                mem_label = mem_labels[colI]
                #print(y_labels[rowI])
                ax = axes[rowI, colI]
                #member_type = axes_config[axI]['mem']
                if colI == 2:
                    ax.set_ylim(ylims[rowI]['diff'])
                else:
                    ax.set_ylim(ylims[rowI]['models'])
                ax.axhline(y=0, color='k', lineWidth=1)
                ax.set_xticks([0,6,12,18,24])
                ax.set_xlim((0,24))
                ax.grid()
                if colI == 0:
                    ax.set_ylabel(y_labels[rowI],fontsize=labelsize)
                if rowI == 0:
                    ax.set_title(mem_label,fontsize=titlesize)
                elif rowI == 1:
                    ax.set_xlabel('Time (UTC)',fontsize=labelsize)

                handles = []
                for res in resolutions:
                    mem_res_key = mem_key+res
                    vals = data['agg'][mem_res_key].values
                    vals = np.append(vals[-1], vals)
                    vals_disagg = data['disagg'][mem_res_key].values
                    vals_disagg = np.append(vals_disagg[-1], vals_disagg)
                    line, = ax.plot(hours, vals, color=plot_dict['res_color'][res],
                                    label=mem_res_key)
                    handles.append(line)

                    if (res == '1'):
                        #print(vals_disagg)
                        day_range = np.arange(start_time, end_time+timedelta(days=1), timedelta(days=1))
                        all_days = np.zeros((9,25))
                        hours = np.arange(0, 25)
                        for dayI in range(len(day_range)-1):
                            this_day = '{:%Y-%m-%d}-00'.format(dt64_to_dt(day_range[dayI]))
                            next_day = '{:%Y-%m-%d}-00'.format(dt64_to_dt(day_range[dayI+1]))
                            vals = vals_disagg.loc[this_day:next_day].values
                            all_days[dayI,:] = vals
                        #for dayI in range(len(day_range)-1):
                        #    ax.plot(hours, all_days[dayI,:], color=plot_dict['res_color'][res],
                        #            label=mem_res_key, linewidth=0.5)
                        quantiles = np.percentile(all_days, percentiles, axis=0)
                        ax.fill_between(hours, quantiles[0,:], quantiles[1,:], color='red',
                                        alpha=0.2, edgecolor='')
                        # t-test
                        #test_type = 'ttest'
                        test_type = 'wilcox'
                        if test_type == 'ttest':
                            from scipy.stats import ttest_1samp
                        if test_type == 'wilcox':
                            from scipy.stats import wilcoxon
                        if mem_key == 'DIFF':
                            for hI in range(len(hours)-1):
                                if test_type == 'ttest':
                                    pval = ttest_1samp(all_days[:,hI], 0).pvalue
                                elif test_type == 'wilcox':
                                    pval = wilcoxon(all_days[:,hI].squeeze()).pvalue
                                #pval = '{:2.2f}'.format(pval)
                                if pval < 0.05:
                                    ax.text(hours[hI]-0.5, 0.15, '*')

                if (rowI == 0) and (colI < 2):
                    ax.legend(handles=handles) 


                # make panel label
                pan_lab_x = ax.get_xlim()[0]
                pan_lab_y = ax.get_ylim()[1] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05
                ax.text(pan_lab_x,pan_lab_y,panel_labels[lind], fontsize=15, weight='bold')
                lind += 1

        fig.subplots_adjust(wspace=0.23, hspace=0.3,
                left=0.08, right=0.98, bottom=0.20, top=0.95)

        if i_save_fig == 1:
            plot_path = plot_path + '/' + plot_name+'.png'
            print(plot_path)
            plt.savefig(plot_path, format='png', bbox_inches='tight')
            plt.close(fig)
        elif i_save_fig == 2:
            plot_path = plot_path + '/' + plot_name+'.pdf'
            print(plot_path)
            plt.savefig(plot_path, format='pdf', bbox_inches='tight')
            plt.close('all')
        else:
            plt.show()
            plt.close(fig)

    




