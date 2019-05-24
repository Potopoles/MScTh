#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
title			proc_radar.py
description	    Process nTOT_PREC fields of radar and model.
author			Christoph Heim
date created    20190522 
date changed    20190524
usage			no args
notes			
python_version	3.7.1
==============================================================================
"""
import os
import xarray as xr
import numpy as np
from datetime import time as dttime
from datetime import datetime,timedelta
os.chdir('00_scripts/')
i_plot = 1 # 0 = no plot, 1 = show plot, 2 = save plot
import matplotlib
if i_plot == 2:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt

    

def calc_mean_diurnal_cycle(field_hourly, aggreg_type='MEAN'):
    """
    Calculates the mean diurnal cycle for the input field.
    Removes dimension 'time' and introduces new dimension
    'diurnal' ranging from 0 to 23.
    """
    hr_fields = []
    for hour in range(0,24):
        this_hr_field = field_hourly.sel(time=dttime(hour))
        this_hr_field = this_hr_field.assign_coords(diurnal=hour)
        hr_fields.append(this_hr_field)

    field_diurn = xr.concat(hr_fields, dim='diurnal')
    if aggreg_type == 'MEAN':
        field_diurn = field_diurn.mean(dim='time')
    else:
        raise NotImplementedError()

    return(field_diurn)





if __name__ == '__main__':
    ####################### NAMELIST INPUTS FILES #######################
    resolutions = [4, 2, 1]
    member_types       = ['RAW', 'SM', 'OBS']
    model_member_types = ['RAW', 'SM']

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
        # mask and store in input ncfile.
        for member_type in model_member_types:
            member_str = member_type+str(res)
            members[member_str] = members[member_str].where(
                            ~np.isnan(members['OBS'+str(res)]), np.nan)


        fig = plt.figure()

        for member_type in member_types:
            member_str = member_type+str(res)
            members[member_str] = members[member_str].mean(dim=['rlat','rlon'])
            members[member_str] = calc_mean_diurnal_cycle(members[member_str])

            path = os.path.join(out_path, member_str,
                                field_name+'.nc')
            members[member_str].to_netcdf(path)
            plt.plot(members[member_str])
        plt.show()


