#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
title			pressure_drag.py
description	    Investigate pressure drag over Alpine Region
author			Christoph Heim
date created    20190603
date changed    20190603
usage			no args
notes			
python_version	3.7.1
==============================================================================
"""
import os, time
import xarray as xr
import numpy as np
from datetime import time as dttime
from datetime import datetime,timedelta
os.chdir('00_scripts/')
from package.plot_functions import PlotOrganizer
from package.functions import calc_mean_diurnal_cycle
import matplotlib.pyplot as plt

def rename_staggered_dims(field):
    if 'srlon' in field.dims:
        field = field.rename({'srlon':'rlon'})
    if 'srlat' in field.dims:
        field = field.rename({'srlat':'rlat'})
    return(field)

    
if __name__ == '__main__':
    ####################### NAMELIST INPUTS FILES #######################
    i_plot = 1
    i_save_fig = 0
    plot_path = os.path.join('..','00_plots', '15_pressure_drag')
    resolutions = ['4', '2', '1']
    #resolutions = ['4', '2']
    #resolutions = ['4']
    member_types       = ['RAW', 'SM']

    dx = {'4':4400,'2':2200,'1':1100}

    plot_dict = {
        'res_color'         :{'4':'black','2':'blue','1':'red'}, 
        'mem_linestyle'     :{'RAW':'-','SM':'--','DIFF':':'},
    }

    ana_fields = {
        'HSURF' :{'prefx':'c', 'chunks':{}},
        'PS'    :{'prefx':'n', 'chunks':{'time':5}},
    }

    inp_path = os.path.join('..','02_fields', 'topocut')

    start_time  = datetime(2006,7,11,1)
    end_time    = datetime(2006,7,13,00)

    dom_alpine_region = {
        'label':'Alpine Region',
        'rlon':slice(-3.76,3.68),
        'rlat':slice(-3.44,1.08),}
    domain = dom_alpine_region

    #dom_alpine_region_sf = {
    #    'label':'Alpine Region',
    #    'rlon':slice(-3.76,3.68),
    #    'rlat':slice(-3.44,-1.08),}
    #domain = dom_alpine_region_sf

    #####################################################################		

    dt_range = np.arange(start_time, end_time+timedelta(hours=1),
                        timedelta(hours=1)).tolist()

    t_start = time.time()

    print('Loading')
    members = {}
    for res in resolutions:
        # load all members
        for member_type in member_types:
            member_str = member_type+str(res)
            print(member_str)

            fields = {}
            for field_name,field_dict in ana_fields.items():
                path = os.path.join(inp_path, member_str,
                                field_dict['prefx']+field_name+'.nc')
                FIELD = xr.open_dataset(path, chunks=field_dict['chunks'])[field_name]
                FIELD   = FIELD.sel(rlon=domain['rlon'], rlat=domain['rlat'])
                fields[field_name] = FIELD

            hthresh = 2000

            h = fields['HSURF'].values[0,:,:]
            ps = fields['PS'].values[:,:,:]

            # mask altitudes > hthresh
            h[h > hthresh] = np.nan


            #plt.contourf(h)
            #plt.show()

            ## mask southern alpine flank
            for i in range(h.shape[1]):
                j = h.shape[0]-1
                #while h[j,i] < hthresh and j < h.shape[0]-1:
                while h[j,i] < hthresh and j > 0:
                    j -= 1
                    if j == 0:
                        h[:,i] = np.nan
                h[:j,i] = np.nan
            #plt.contourf(h)
            #plt.show()
            #quit()


            hStY = 0.5 * (h[1:,:] + h[0:-1,:])
            hStX = 0.5 * (h[:,1:] + h[:,0:-1])
            dhdx = (hStY[:,1:] - hStY[:,0:-1])/dx[res]
            dhdy = (hStX[1:,:] - hStX[0:-1,:])/dx[res]
            A = dx[res]**2

            Dts = np.zeros(len(dt_range))
            for tI in range(len(dt_range)):
                psC = 0.25 * ( ps[tI,0:-1,0:-1] + ps[tI,0:-1,1:] +
                               ps[tI,1:,0:-1]   + ps[tI,1:,1:] )

                DxC = psC * dhdx * A
                DyC = psC * dhdy * A
                #DxC = dhdx
                #DyC = dhdy
                #DxC = psC
                #DyC = psC

                Dx = 0.25 * ( DxC[0:-2,0:-2] + DxC[0:-2,1:-1] +
                              DxC[1:-1,0:-2] + DxC[1:-1,1:-1] )
                Dy = 0.25 * ( DyC[0:-2,0:-2] + DyC[0:-2,1:-1] +
                              DyC[1:-1,0:-2] + DyC[1:-1,1:-1] )
                Dx = np.nansum(Dx)
                Dy = np.nansum(Dy)
                D  = np.sqrt(Dx**2 + Dy**2)
                Dts[tI] = D
            print(np.mean(Dts))
            #quit()

            ## rename staggered dimensions
            #field = rename_staggered_dims(field)

            ## compute mass flux
            #flux = field * rho 
            ##flux.name = 'mass flux '+field.name

            ## select time and altitue
            #field = field.sel(time=slice(start_time,end_time),
            #                  altitude=altitudes)

            ## select directional and perpendicular dimension 
            #ds = 0.020
            #kwargs = {flx_dict['mean']:slice(
            #        domain[flx_dict['mean']][flx_dict['mean_ind']]-2*ds,
            #        domain[flx_dict['mean']][flx_dict['mean_ind']]+ds),
            #          flx_dict['sum']:slice(
            #        domain[flx_dict['sum']][0], domain[flx_dict['sum']][1]),}
            #field   = field.sel(**kwargs)
            #print(field.values.shape)

            ## aggregate in directional dimesion
            #field   = field.mean(dim=flx_dict['mean'])
            ## aggregate in perpendicular dimesion
            #field   = field.sum(dim=flx_dict['sum'])*dx[res]
            ## aggreagte vertically
            #field = field.integrate(dim=['altitude'])

            ## multiply with unit vector of direction
            #field.values = field.values * flx_dict['dir']

            ##calculate diurnal cycle and store
            #field = calc_mean_diurnal_cycle(field)
            #field = field.rename(flx_key)
            #all_fields.append(field)

            #members[member_str] = all_fields

    quit()


    t_end = time.time()
    print('Computation complete. Took ' + 
            str(round(t_end - t_start,0)) + ' sec.')

    if i_plot: 
        name_dict = {'':'new_eval'}
        PO = PlotOrganizer(i_save_fig, path=plot_path, name_dict=name_dict)
        PO.initialize_plot(nrow=2, ncol=3)
        #PO.fig.set_size_inches(2*stretchCol,1*stretchRow)

        for flx_key,ax_dict in axes_dicts.items():
            print(flx_key)
            ax = PO.axes[ax_dict['row_ind'],ax_dict['col_ind']]
            for member_type in member_types:
                for res in resolutions:
                    if flx_key == 'DIFF' and member_type != 'RAW':
                        print(flx_key + member_type + str(res))
                        continue
                    member_str = member_type+str(res)
                    field = members[member_str][flx_key]

                    hours = np.append(field.coords['diurnal'].values, 24)
                    vals = np.append(field.values, field.values[0])
                    line, = ax.plot(hours, vals, color=plot_dict['res_color'][res],
                            linestyle=plot_dict['mem_linestyle'][member_type],
                            label=member_type)

                    ax.set_title(flx_key)
                    if flx_key == 'W':
                        PO.handles.append(line)
                    ax.axhline(y=0, color='grey')
                    ax.set_xlim((0,24))
                    ax.set_ylim((-5E9,5E9))
                    ax.set_xlabel('Hour')
                    ax.set_ylabel('Mass flux [kg s-1]')

        PO.fig.tight_layout()
        plt.legend(handles=PO.handles) 
        print(PO.handles)
        PO.finalize_plot()

