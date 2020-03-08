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
    i_recompute_1 = 1
    i_recompute_2 = 0
    plot_path = os.path.join('..','00_plots', '14_convergence')
    resolutions = ['4', '2', '1']
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
    i_plot = 0
    i_save_fig = 0

    plot_flux = 'TOT'
    #plot_flux = 'E'
    #plot_flux = 'W'
    #plot_flux = 'S'
    #plot_flux = 'N'

    mem_keys = ['SM', 'RAW', 'DIFF']
    mem_labels = ['SM', 'RAW', 'RAW - SM']
    #y_labels = [r'Lateral Vapor Convergence $[mm$ $h^{-1}]$',
    #            r'Surface Pressure Anomalies $[Pa]$',
    #            r'Temperature Anomalies $[K]$']
    y_labels = [r'$q_v$-convergence $[mm$ $h^{-1}]$',
                r'Pressure Anomaly $[Pa]$',
                r'Temp. Anomaly $[K]$']
    if domain['code'] in ['alpine_region']:
        ylims = [{'models':(-0.4,0.4),      'diff':(-0.2,0.2)},
                 {'models':(-200,200),        'diff':(-40,40)},
                 {'models':(-2.0,2.0),         'diff':(-0.40,0.40)}]
    elif domain['code'] in ['alpine_ridge_15_25']:
        ylims = [{'models':(-2.5,2.5),      'diff':(-1.0,1.0)},
                 {'models':(-200,200),        'diff':(-40,40)},
                 {'models':(-2.0,2.0),         'diff':(-0.40,0.40)}]
    elif domain['code'] in ['northern_italy_0_2']:
        ylims = [{'models':(-1.2,1.2),      'diff':(-1.2,1.2)},
                 {'models':(-200,200),        'diff':(-40,40)},
                 {'models':(-2.0,2.0),         'diff':(-0.40,0.40)}]
    else:
        ylims = [{'models':(-1.2,1.2),      'diff':(-1.2,1.2)},
                 {'models':(-200,200),        'diff':(-40,40)},
                 {'models':(-2.0,2.0),         'diff':(-0.40,0.40)}]
    
    percentiles = [15, 85]
    #percentiles = [20, 80]

    labelsize = 12
    titlesize = 14

    plot_dict = {
        'res_color'         :{'4':'black','2':'blue','1':'red'}, 
        'mem_linestyle'     :{'RAW':'-','SM':'--','DIFF':':'},
    }
    #axes_dicts = {
    #    'W':{'col_ind':1,'row_ind':0},
    #    'E':{'col_ind':1,'row_ind':1},
    #    'N':{'col_ind':0,'row_ind':0},
    #    'S':{'col_ind':0,'row_ind':1},
    #    'TOT':{'col_ind':2,'row_ind':0},
    #    'DIFF':{'col_ind':2,'row_ind':1},
    #}

    plot_name = 'vapor_convergence_domain_{}_flux_{}'.format(domain['code'],
                                                             plot_flux)

    ds = 0.015

    #####################################################################		

    print('run for domain {}'.format(domain['label']))

    dt_range = np.arange(start_time, end_time+timedelta(hours=1),
                        timedelta(hours=1)).tolist()


    timer = Timer()

    t_start = time.time()
    print('Loading')
    if i_recompute_1:
        timer.start('compute 1')

        ##################################
        members = {}
        # non diurnally aggregated:
        members_disagg = {}
        for res in resolutions:

            # get area of domain
            path = os.path.join(inp_path, 'RAW'+str(res), 'zQV.nc')
            qv = xr.open_dataset(path, )['QV']
            qv = qv.sel(rlon=slice(domain['rlon'][0],domain['rlon'][1]),
                        rlat=slice(domain['rlat'][0],domain['rlat'][1]))
            area = len(qv.coords['rlon']) * len(qv.coords['rlat']) * dx[res]**2

            # load all members
            n_nan_members = {}
            for member_type in member_types:
                member_str = member_type+str(res)
                print(member_str)
                all_fields = []
                all_fields_disagg = []
                n_nan = {}
                for flx_key,flx_dict in fluxes.items():
                    print('\t {}'.format(flx_key))

                    timer.start('loading')
                    path = os.path.join(inp_path, 
                                member_str, flx_dict['field']+'.nc')
                    #field = xr.open_dataset(path, 
                    #            chunks={'time':time_chunk})[flx_dict['field'][1:]]
                    #field = xr.open_dataset(path, chunks={})[flx_dict['field'][1:]]
                    field = xr.open_dataset(path)[flx_dict['field'][1:]]

                    path = os.path.join(inp_path, 
                                member_str, 'zRHO.nc')
                    #rho = xr.open_dataset(path, 
                    #            chunks={'time':time_chunk})['RHO']
                    #rho = xr.open_dataset(path, chunks={})['RHO']
                    rho = xr.open_dataset(path)['RHO']

                    path = os.path.join(inp_path, 
                                member_str, 'zQV.nc')
                    #qv = xr.open_dataset(path, 
                    #            chunks={'time':time_chunk})['QV']
                    #qv = xr.open_dataset(path, chunks={})['QV']
                    qv = xr.open_dataset(path)['QV']
                    timer.stop('loading')

                    timer.start('altsel')
                    # select time and altitue
                    field = field.sel(time=slice(start_time,end_time),
                                      altitude=domain['altitudes'])
                    timer.stop('altsel')

                    # rename staggered dimensions
                    timer.start('unstagger')
                    field = unstaggering(field)
                    rho = unstaggering(rho)
                    qv = unstaggering(qv)
                    field = field.sel(time=slice(start_time,end_time),
                                  altitude=domain['altitudes'],
                                  rlat=slice(domain['rlat'][0]-3*ds,
                                             domain['rlat'][1]+3*ds),
                                  rlon=slice(domain['rlon'][0]-3*ds,
                                             domain['rlon'][1]+3*ds))
                    rho = rho.sel(time=slice(start_time,end_time),
                                  altitude=domain['altitudes'],
                                  rlat=slice(domain['rlat'][0]-3*ds,
                                             domain['rlat'][1]+3*ds),
                                  rlon=slice(domain['rlon'][0]-3*ds,
                                             domain['rlon'][1]+3*ds))
                    qv = qv.sel(time=slice(start_time,end_time),
                                  altitude=domain['altitudes'],
                                  rlat=slice(domain['rlat'][0]-3*ds,
                                             domain['rlat'][1]+3*ds),
                                  rlon=slice(domain['rlon'][0]-3*ds,
                                             domain['rlon'][1]+3*ds))
                    timer.stop('unstagger')

                    # compute mass flux
                    timer.start('mult')
                    field = field * rho * qv
                    #field = field * rho
                    timer.stop('mult')

                    # select directional and perpendicular dimension 
                    kwargs = {flx_dict['mean']:slice(
                            domain[flx_dict['mean']][flx_dict['mean_ind']]-2*ds,
                            domain[flx_dict['mean']][flx_dict['mean_ind']]+ds),
                              flx_dict['sum']:slice(
                            domain[flx_dict['sum']][0], domain[flx_dict['sum']][1]),}
                    timer.start('sel')
                    field   = field.sel(**kwargs)
                    timer.stop('sel')
                    print('\t\t {}'.format(field.values.shape))

                    timer.start('aggreg')
                    # aggregate in directional dimesion
                    field   = field.mean(dim=flx_dict['mean'])
                    n_nan[flx_key] = np.sum(np.isnan(field.isel(time=0).values))
                    # aggregate in perpendicular dimesion
                    field   = field.sum(dim=flx_dict['sum'])*dx[res]
                    # aggreagte vertically
                    field = field.integrate(dim=['altitude'])
                    timer.stop('aggreg')
                    timer.start('integ')
                    # multiply with unit vector of direction
                    field.values = field.values * flx_dict['dir']
                    # convert to [mm h-1] within domain
                    field.values = field.values / area * 3600
                    print('\t\t\t {}'.format(field.mean().values))
                    timer.stop('integ')

                    # label according to flux name
                    field = field.rename(flx_key)

                    all_fields_disagg.append(copy.copy(field))
                    #calculate diurnal cycle and store
                    field = calc_mean_diurnal_cycle(field)
                    all_fields.append(field)


                n_nan_members[member_str] = n_nan
                print(n_nan_members)

                all_fields = xr.merge(all_fields)
                all_fields_disagg = xr.merge(all_fields_disagg)
                members[member_str] = all_fields
                members_disagg[member_str] = all_fields_disagg 

        print(n_nan_members)

        # Calculate total flux over all edges
        for res in resolutions:
            for member_type in member_types:
                member_str = member_type+str(res)
                # diurnal
                fields = members[member_str]
                fields['TOT'] = (fields['W'] + fields['E'] + 
                                 fields['N'] + fields['S'] )
                members[member_str] = fields
                # disaggregated
                fields = members_disagg[member_str]
                fields['TOT'] = (fields['W'] + fields['E'] + 
                                 fields['N'] + fields['S'] )
                members_disagg[member_str] = fields

        # Calculate total flux difference between RAW and SM
        for flux_key in ['TOT', 'S', 'N', 'E', 'W']:
            for res in resolutions:
                RAW_str = 'RAW'+str(res)
                SM_str = 'SM'+str(res)
                DIFF_str = '{}_DIFF'.format(flux_key)+str(res)
                # diurnal
                diff = members[RAW_str][flux_key] - members[SM_str][flux_key]
                members[DIFF_str] = diff
                # disaggregated
                diff = members_disagg[RAW_str][flux_key] - members_disagg[SM_str][flux_key]
                members_disagg[DIFF_str] = diff

        pickle.dump(members, open(pickle_save_file, 'wb'))
        pickle.dump(members_disagg, open(pickle_save_file_3, 'wb'))

        timer.stop('compute 1')
        #########################################

    if i_recompute_2:
        timer.start('compute 2')
        members = {}
        # non diurnally aggregated:
        members_disagg = {}
        for res in resolutions:

            # load all members
            for member_type in member_types:
                member_str = member_type+str(res)
                print(member_str)

                all_fields = {}
                all_fields_disagg = {}

                path = os.path.join(inp_path, member_str, 'nPS.nc')
                ps = xr.open_dataset(path, )['PS']
                ps = ps.sel(rlon=slice(domain['rlon'][0],domain['rlon'][1]),
                            rlat=slice(domain['rlat'][0],domain['rlat'][1]))

                path = os.path.join(inp_path, member_str, 'zT.nc')
                temp = xr.open_dataset(path, )['T']
                temp = temp.sel(rlon=slice(domain['rlon'][0],domain['rlon'][1]),
                                rlat=slice(domain['rlat'][0],domain['rlat'][1]),
                                altitude=domain['altitudes'])

                # select time
                ps = ps.sel(time=slice(start_time,end_time))
                temp = temp.sel(time=slice(start_time,end_time))

                # aggregate
                ps      = ps.mean(dim=['rlon', 'rlat'])
                temp   = temp.mean(dim=['rlon', 'rlat', 'altitude'])
                #from scipy import signal
                #plt.plot(temp)
                #old_mean = np.mean(temp.values)
                #temp.values = signal.detrend(temp.values)
                #temp.values = temp.values + old_mean
                #plt.plot(temp)
                #plt.show()
                #quit()

                # calculate anomalies
                ps = ps - ps.mean()
                temp = temp - temp.mean()

                all_fields_disagg['PS'] = ps
                all_fields_disagg['T'] = temp

                #calculate diurnal cycle and store
                ps = calc_mean_diurnal_cycle(ps).values
                ps = np.append(ps, ps[0])
                temp = calc_mean_diurnal_cycle(temp).values
                temp = np.append(temp, temp[0])

                all_fields['PS'] = ps
                all_fields['T'] = temp
                members[member_str] = all_fields
                members_disagg[member_str] = all_fields_disagg

        # Calculate total flux difference between RAW and SM
        for res in resolutions:
            RAW_str = 'RAW'+str(res)
            SM_str = 'SM'+str(res)
            DIFF_str = 'DIFF'+str(res)
            # diurnal
            members[DIFF_str] = {}
            members[DIFF_str]['PS'] = members[RAW_str]['PS'] - members[SM_str]['PS']
            members[DIFF_str]['T'] = members[RAW_str]['T'] - members[SM_str]['T']

            members_disagg[DIFF_str] = {}
            members_disagg[DIFF_str]['PS'] = (members_disagg[RAW_str]['PS'] - 
                                                    members_disagg[SM_str]['PS'])
            members_disagg[DIFF_str]['T']  = (members_disagg[RAW_str]['T'] -
                                                    members_disagg[SM_str]['T'])

        pickle.dump(members, open(pickle_save_file_2, 'wb'))
        pickle.dump(members_disagg, open(pickle_save_file_4, 'wb'))
        timer.stop('compute 2')

    #members alpine pumping
    members_ap = pickle.load(open(pickle_save_file, 'rb'))
    #members alpine pumping disaggregated
    members_ap_disagg = pickle.load(open(pickle_save_file_3, 'rb'))
    #members surface pressure and temperature
    members_tp = pickle.load(open(pickle_save_file_2, 'rb'))
    #members surface pressure and temperature disaggregated
    members_tp_disagg = pickle.load(open(pickle_save_file_4, 'rb'))

    t_end = time.time()
    print('Computation complete. Took ' + 
            str(round(t_end - t_start,0)) + ' sec.')

    timer.start('plot')
    if i_plot == 1: 
        panel_labels = ['a)','d)', 'g)', 'b)', 'e)', 'h)', 'c)', 'f)', 'i)']
        lind = 0
        fig,axes = plt.subplots(3,3, figsize=(11,11))
        for colI in range(3):
            mem_key = mem_keys[colI]
            mem_label = mem_labels[colI]
            for rowI in range(3):
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
                    if rowI == 0:
                        if mem_key == 'DIFF':
                            key = '{}_'.format(plot_flux)+mem_res_key
                            vals = members_ap[key]
                            vals = np.append(vals, vals[0])
                            vals_disagg = members_ap_disagg[key]
                        else:
                            field = members_ap[mem_res_key][plot_flux]
                            vals = np.append(field.values, field.values[0])
                            vals_disagg = members_ap_disagg[mem_res_key][plot_flux]
                    elif rowI == 1:
                        vals = members_tp[mem_res_key]['PS']
                        vals_disagg = members_tp_disagg[mem_res_key]['PS']
                    elif rowI == 2:
                        vals = members_tp[mem_res_key]['T']
                        vals_disagg = members_tp_disagg[mem_res_key]['T']
                    #hours = np.append(field.coords['diurnal'].values, 24)
                    hours = np.arange(0, 25)
                    line, = ax.plot(hours, vals, color=plot_dict['res_color'][res],
                                    label=mem_res_key)
                    handles.append(line)

                    if (res == '1'):
                        #print(vals_disagg)
                        day_range = np.arange(start_time, end_time+timedelta(days=1),
                                              timedelta(days=1))
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
                                    print(plot_hr)
                                    ax.text(plot_hr-0.6, ax.get_ylim()[1]*0.87,
                                            '*', color='red')

                if (rowI == 0) and (colI < 2):
                    ax.legend(handles=handles) 


                # make panel label
                pan_lab_x = ax.get_xlim()[0]
                pan_lab_y = ax.get_ylim()[1] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.05
                ax.text(pan_lab_x,pan_lab_y,panel_labels[lind], fontsize=15, weight='bold')
                lind += 1

        fig.subplots_adjust(wspace=0.23, hspace=0.3,
                left=0.08, right=0.98, bottom=0.20, top=0.95)

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


    timer.stop('plot')
    timer.print_report()
    




