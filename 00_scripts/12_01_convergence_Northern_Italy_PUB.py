#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
description	    Investigate diurnal cycle of convergence of moisture over
                Alpine Region. 
author			Christoph Heim
date created    28.05.2019
date changed    02.03.2020
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
from package.utilities import dt64_to_dt, Timer, calc_mean_diurnal_cycle
import matplotlib.pyplot as plt

def unstaggering(field):
    if 'srlon' in field.dims:
        field = field.rename({'srlon':'rlon'})
        field.coords['rlon'].values += np.mean(
                                np.diff(field.coords['rlon'].values))/2
    if 'srlat' in field.dims:
        field = field.rename({'srlat':'rlat'})
        field.coords['rlat'].values += np.mean(
                                np.diff(field.coords['rlat'].values))/2
    field.coords['rlon'].values = np.round(field.coords['rlon'].values,3)
    field.coords['rlat'].values = np.round(field.coords['rlat'].values,3)
    return(field)

    
if __name__ == '__main__':
    ####################### NAMELIST INPUTS FILES #######################
    plot_path = os.path.join('..','00_plots', '14_convergence')
    #resolutions = ['4']
    member_types       = ['RAW', 'SM']


    dx = {'4':4400,'2':2200,'1':1100}

    inp_path = os.path.join('..','02_fields', 'topocut')
    #inp_path_diurnal = os.path.join('..','02_fields', 'diurnal')

    fluxes = {
        'W':{'field':'zU','dir': 1,'mean':'rlon','mean_ind': 0,'sum':'rlat',}, 
        'E':{'field':'zU','dir':-1,'mean':'rlon','mean_ind':-1,'sum':'rlat',}, 
        'S':{'field':'zV','dir': 1,'mean':'rlat','mean_ind': 0,'sum':'rlon',}, 
        'N':{'field':'zV','dir':-1,'mean':'rlat','mean_ind':-1,'sum':'rlon',}, 
    }


    start_time  = datetime(2006,7,11,0)
    end_time    = datetime(2006,7,20,0)

    #start_time  = datetime(2006,7,12,0)
    #end_time    = datetime(2006,7,14,0)


    dom_alpine_region = {
        'code':'alpine_region',
        'label':'Alpine Region',
        #'rlon':(-3.76,3.68),
        #'rlat':(-3.44,1.08),}
        'rlon':(-3.775, 3.705),
        'rlat':(-3.455, 1.105),
        'altitudes':slice(0,2500),}
    dom_northern_italy_0_2 = {
        'code':'northern_italy_0_2',
        'label':'Northern Italy 0-2km',
        'rlon':(-1.695, 0.225),
        'rlat':(-2.495,-1.215),
        'altitudes':slice(0,2000),}
    dom_northern_italy_2_6 = {
        'code':'northern_italy_2_6',
        'label':'Northern Italy 2-6km',
        'rlon':(-1.695, 0.225),
        'rlat':(-2.495,-1.215),
        'altitudes':slice(2000,6000),}
    dom_alpine_ridge_15_25 = {
        'code':'alpine_ridge_15_25',
        'label':'Alpine Ridge 1.5-2.5km',
        'rlon':(-1.375, 0.225),
        'rlat':(-0.695,-0.295),
        #'rlon':(-1.78, 0.625),
        #'rlat':(-1.095,0.095),
        'altitudes':slice(1500,2500),}

    #domain = dom_northern_italy_0_2
    #domain = dom_northern_italy_2_6
    #domain = dom_alpine_region
    domain = dom_alpine_ridge_15_25

    time_chunk = 1

    pickle_save_file    = 'data_12_00/data_12_00_{}.pkl'.format(domain['code'])
    pickle_save_file_2  = 'data_12_00/data_12_00_{}_2.pkl'.format(domain['code'])
    pickle_save_file_3  = 'data_12_00/data_12_00_{}_3.pkl'.format(domain['code'])
    pickle_save_file_4  = 'data_12_00/data_12_00_{}_4.pkl'.format(domain['code'])

    ######PLOTTING
    i_save_fig = 0
    i_plot_fluxes = 1


    mem_keys = ['SM', 'RAW', 'DIFF']
    mem_labels = ['SM', 'RAW', 'RAW - SM']
    y_labels = [r'$q_v$-convergence $[mm$ $h^{-1}]$',
                r'$q_v$-convergence $[mm$ $h^{-1}]$',
                r'$q_v$-convergence $[mm$ $h^{-1}]$']
    if domain['code'] in ['alpine_region']:
        ylims = {'models':(-0.4,0.4),      'diff':(-0.2,0.2)}
    elif domain['code'] in ['alpine_ridge_15_25']:
        ylims = {'models':(-2.5,2.5),      'diff':(-1.0,1.0)}
    elif domain['code'] in ['northern_italy_0_2']:
        ylims = {'models':(-1.2,1.2),      'diff':(-1.2,1.2)}
    elif domain['code'] in ['northern_italy_2_6']:
        ylims = {'models':(-2.0,2.0),      'diff':(-2.0,2.0)}
    else:
        ylims = {'models':(-1.2,1.2),      'diff':(-1.2,1.2)}
    ylims = [ylims, ylims, ylims]
    
    percentiles = [15, 85]
    #percentiles = [20, 80]

    labelsize = 14
    titlesize = 16

    plot_dict = {
        'res_color'         :{'4':'black','2':'blue','1':'red'}, 
        'mem_linestyle'     :{'RAW':'-','SM':'--','DIFF':':'},
        #'flx_linestyle'     :{'N':'--','S':'-', 'W':'--', 'E':'-'},
        'flx_linestyle'     :{'N':'--','S':'-', 'W':':', 'E':'-.'},
    }

    plot_name = 'vapor_convergence2_domain_{}_fluxes_{}'.format(domain['code'],
                    i_plot_fluxes)

    #flx_keys = [['TOT'], ['N', 'S'],['W', 'E']]
    #resolutions = [['4', '2', '1'],['1'],['1']]
    flx_keys = [['TOT'], ['N', 'S', 'W', 'E']]
    resolutions = [['4', '2', '1'],['1']]
    #####################################################################		

    print('run for domain {}'.format(domain['label']))

    dt_range = np.arange(start_time, end_time+timedelta(hours=1),
                        timedelta(hours=1)).tolist()


    timer = Timer()

    #members alpine pumping
    members_ap = pickle.load(open(pickle_save_file, 'rb'))
    #members alpine pumping disaggregated
    members_ap_disagg = pickle.load(open(pickle_save_file_3, 'rb'))

    panel_labels = ['a)','b)', 'c)', 'd)', 'e)', 'f)']
    lind = 0
    #fig,axes = plt.subplots(3,3, figsize=(11,11))

    if i_plot_fluxes:
        fig,axes = plt.subplots(2,3, figsize=(11,7))
        row_range = range(2)
    else:
        fig,axes = plt.subplots(1,3, figsize=(11,3.7))
        axes = np.expand_dims(axes, axis=0)
        row_range = range(1)

    for rowI in row_range:
        print()
        for colI in range(3):
            mem_key = mem_keys[colI]
            mem_label = mem_labels[colI]
            ax = axes[rowI, colI]
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
            if (rowI == 1) or not i_plot_fluxes:
                ax.set_xlabel('Time (UTC)',fontsize=labelsize)

            handles = []
            for res in resolutions[rowI]:
                mem_res_key = mem_key+res
                print(mem_res_key)
                for plot_flux in flx_keys[rowI]:
                    mem_res_key = mem_key+res
                    if mem_key == 'DIFF':
                        key = '{}_'.format(plot_flux)+mem_res_key
                        vals = members_ap[key]
                        vals = np.append(vals, vals[0])
                        vals_disagg = members_ap_disagg[key]
                    else:
                        field = members_ap[mem_res_key][plot_flux]
                        vals = np.append(field.values, field.values[0])
                        vals_disagg = members_ap_disagg[mem_res_key][plot_flux]
                    #hours = np.append(field.coords['diurnal'].values, 24)
                    hours = np.arange(0, 25)
                    if rowI == 0:
                        linestyle = '-'
                        label=mem_res_key
                    else:
                        linestyle = plot_dict['flx_linestyle'][plot_flux]
                        label=plot_flux

                    line, = ax.plot(hours, vals, color=plot_dict['res_color'][res],
                                    label=label, linestyle=linestyle)
                    handles.append(line)

                    if res == '1' and rowI == 0:
                        #print(vals_disagg)
                        day_range = np.arange(start_time, end_time+timedelta(days=1), 
                                                timedelta(days=1))
                        all_days = np.zeros((9,25))
                        hours = np.arange(0, 25)
                        for dayI in range(len(day_range)-2):
                            this_day = '{:%Y-%m-%d}-00'.format(dt64_to_dt(
                                            day_range[dayI]))
                            next_day = '{:%Y-%m-%d}-00'.format(dt64_to_dt(
                                            day_range[dayI+1]))
                            vals = vals_disagg.loc[this_day:next_day].values
                            all_days[dayI,:] = vals
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
                        if mem_key == 'DIFF':
                            for hI in range(len(hours)-1):
                                if test_type == 'ttest':
                                    pval = ttest_1samp(all_days[:,hI], 0).pvalue
                                elif test_type == 'wilcox':
                                    pval = wilcoxon(all_days[:,hI].squeeze()).pvalue
                                #pval = '{:2.2f}'.format(pval)
                                if (pval < 0.05):
                                    plot_hr = hours[hI]
                                    if plot_hr == 0: plot_hr = 24
                                    ax.text(plot_hr-0.5, ax.get_ylim()[1]*0.87,
                                            '*', color='red')

                if (rowI == 0) and (colI < 2):
                    ax.legend(handles=handles) 
                elif (rowI > 0) and (colI == 2):
                    ax.legend(handles=handles) 


            # make panel label
            pan_lab_x = ax.get_xlim()[0]
            pan_lab_y = ax.get_ylim()[1] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05
            ax.text(pan_lab_x,pan_lab_y,panel_labels[lind], fontsize=15, weight='bold')
            lind += 1

    if i_plot_fluxes:
        fig.subplots_adjust(wspace=0.23, hspace=0.3,
                left=0.08, right=0.98, bottom=0.20, top=0.95)
    else:
        fig.subplots_adjust(wspace=0.23, hspace=0.3,
                left=0.08, right=0.98, bottom=0.16, top=0.90)

    plot_path = plot_path + '/' + plot_name
    print('save figure to {}'.format(plot_path))
    if i_save_fig == 1:
        plot_path = plot_path + '.png'
        print(plot_path)
        plt.savefig(plot_path, format='png', bbox_inches='tight')
        plt.close(fig)
    elif i_save_fig == 2:
        plot_path = plot_path + '.pdf'
        print(plot_path)
        plt.savefig(plot_path, format='pdf', bbox_inches='tight')
        plt.close('all')
    else:
        plt.show()
        plt.close(fig)




    timer.print_report()





