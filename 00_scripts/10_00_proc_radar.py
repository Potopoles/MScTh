#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
title			proc_radar.py
description	    Process nTOT_PREC fields of radar and model.
author			Christoph Heim
date created    20190522 
date changed    20190528
usage			no args
notes			
python_version	3.7.1
==============================================================================
"""
import os
import xarray as xr
import numpy as np
from datetime import datetime,timedelta
os.chdir('00_scripts/')
from package.plot_functions import PlotOrganizer
from package.functions import calc_mean_diurnal_cycle
#i_plot = 0 # 0 = no plot, 1 = show plot, 2 = save plot
#import matplotlib
#if i_plot == 2:
#    matplotlib.use('Agg')
import matplotlib.pyplot as plt



if __name__ == '__main__':
    ####################### NAMELIST INPUTS FILES #######################
    i_recompute = 0
    i_plot = 1
    i_save_fig = 0
    plot_path = os.path.join('..','00_plots', '10_evaluation')
    resolutions = [4, 2, 1]
    member_types       = ['RAW', 'SM', 'OBS']
    model_member_types = ['RAW', 'SM']

    plot_dict = {
        'res_color'         :{4:'black',2:'blue',1:'red'}, 
        'mem_ax_col_ind'    :{'RAW':1,'SM':0},
    }

    inp_path = os.path.join('..','02_fields', 'topocut')
    out_path = os.path.join('..','02_fields', 'radar_diurn')

    field_name = 'nTOT_PREC'

    start_time  = datetime(2006,7,11,1)
    end_time    = datetime(2006,7,20,00)

    dom_alpine_region = {
        'label':'Alpine Region',
        'rlon':(-3.76,3.68),
        'rlat':(-3.44,1.08),}
    domain = dom_alpine_region

    #####################################################################		

    dt_range = np.arange(start_time, end_time+timedelta(hours=1),
                        timedelta(hours=1)).tolist()

    for res in resolutions:
        print(res)

        if i_recompute:
            print('Mask model to OBS.')
            # load all members
            members = {}
            for member_type in member_types:
                member_str = member_type+str(res)
                path = os.path.join(inp_path, member_str,
                                    field_name+'.nc')
                field = xr.open_dataset(path, chunks={'time':5})[field_name[1:]]
                if member_type == 'OBS':
                    field = field.rename({'x_1':'rlon','y_1':'rlat'})
                field = field.sel(time=slice(start_time,end_time))
                members[member_str] = field
             
            # fix unequal dimension issue due to numerical precision
            members['OBS'+str(res)].coords['rlat'].values = \
                                    members['RAW'+str(res)].coords['rlat'].values
            members['OBS'+str(res)].coords['rlon'].values = \
                                    members['RAW'+str(res)].coords['rlon'].values

            for member_type in member_types:
                member_str = member_type+str(res)
                members[member_str] = members[member_str].sel(
                                rlat=slice(domain['rlat'][0],domain['rlat'][1]),
                                rlon=slice(domain['rlon'][0],domain['rlon'][1]))

            # mask model members according to OBS 
            for member_type in model_member_types:
                member_str = member_type+str(res)
                members[member_str] = members[member_str].where(
                                ~np.isnan(members['OBS'+str(res)]), np.nan)

            print('Calc diurnal and store.')
            # calc diurnal and store in out_path ncfiles.
            for member_type in member_types:
                member_str = member_type+str(res)
                members[member_str] = members[member_str].mean(dim=['rlat','rlon'])
                members[member_str] = calc_mean_diurnal_cycle(members[member_str])

                path = os.path.join(out_path, member_str,
                                    field_name+'.nc')
                members[member_str].to_netcdf(path)


    if i_plot: 
        name_dict = {'':'new_eval'}
        PO = PlotOrganizer(i_save_fig, path=plot_path, name_dict=name_dict)
        PO.initialize_plot(nrow=1, ncol=2)

        stretchCol = 3.8*1.3
        stretchRow = 3.8*1.3
        PO.fig.set_size_inches(2*stretchCol,1*stretchRow)

        # sum label settings
        x = 3
        yTop = 0.25
        dy = 0.18
        size = 12

        members = {}
        for member_type in model_member_types:
            ax = PO.axes[plot_dict['mem_ax_col_ind'][member_type]]
            for res in resolutions:
                member_str = member_type+str(res)
                path = os.path.join(out_path, member_str,
                                    field_name+'.nc')
                field = xr.open_dataset(path)[field_name[1:]]
                members[member_str] = field

                hours = np.append(field.coords['diurnal'].values, 24)
                TOT_PREC = np.append(field.values, field.values[0])
                ax.plot(hours, TOT_PREC, color=plot_dict['res_color'][res])

            #ax.text(x, yTop+dy, 'Sum:', size=size,
            #        bbox=dict(boxstyle='square',ec=(1,1,1,0.5),fc=(1,1,1,0.5)))
            ax.set_xlabel('Hour',fontsize=12)
            ax.set_xticks([0,6,12,18,24])
            ax.set_xlim([0,24])
            ax.set_ylim([0.,0.3])
            ax.set_ylabel(r'Rain Rate $[mm$ $h^{-1}]$',fontsize=12)
            ax.grid()

        for ax in PO.axes:
            path = os.path.join(out_path, 'OBS4',
                                field_name+'.nc')
            field = xr.open_dataset(path)[field_name[1:]]

            hours = np.append(field.coords['diurnal'].values, 24)
            TOT_PREC = np.append(field.values, field.values[0])
            ax.plot(hours, TOT_PREC, color='grey')
        
        PO.finalize_plot()
