#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
title			convergence_PUB.py
description	    Investigate diurnal cycle of convergence of moisture over
                Alpine Region. 
author			Christoph Heim
date created    20190528 
date changed    20190606
usage			no args
notes			
python_version	3.7.1
==============================================================================
"""
import os, time, pickle
import xarray as xr
import numpy as np
from datetime import time as dttime
from datetime import datetime,timedelta
os.chdir('00_scripts/')
from package.plot_functions import PlotOrganizer
from package.functions import calc_mean_diurnal_cycle
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
    i_recompute = 0
    pickle_save_file = 'data_12_00.pkl'
    i_plot = 1
    i_save_fig = 2
    plot_path = os.path.join('..','00_plots', '14_convergence')
    resolutions = ['4', '2', '1']
    #resolutions = ['4', '2']
    #resolutions = ['4']
    member_types       = ['RAW', 'SM']
    plot_name = 'vapor_convergence'

    dx = {'4':4400,'2':2200,'1':1100}

    plot_dict = {
        'res_color'         :{'4':'black','2':'blue','1':'red'}, 
        'mem_linestyle'     :{'RAW':'-','SM':'--','DIFF':':'},
    }
    axes_dicts = {
        'W':{'col_ind':1,'row_ind':0},
        'E':{'col_ind':1,'row_ind':1},
        'N':{'col_ind':0,'row_ind':0},
        'S':{'col_ind':0,'row_ind':1},
        'TOT':{'col_ind':2,'row_ind':0},
        'DIFF':{'col_ind':2,'row_ind':1},
    }

    inp_path = os.path.join('..','02_fields', 'topocut')

    fluxes = {
        'W':{'field':'zU','dir': 1,'mean':'rlon','mean_ind': 0,'sum':'rlat',}, 
        'E':{'field':'zU','dir':-1,'mean':'rlon','mean_ind':-1,'sum':'rlat',}, 
        'S':{'field':'zV','dir': 1,'mean':'rlat','mean_ind': 0,'sum':'rlon',}, 
        'N':{'field':'zV','dir':-1,'mean':'rlat','mean_ind':-1,'sum':'rlon',}, 
    }

    altitudes = slice(0,2500)

    start_time  = datetime(2006,7,11,1)
    end_time    = datetime(2006,7,20,00)
    #end_time    = datetime(2006,7,13,00)

    ylims = (-0.4,0.3) 
    labelsize = 12
    titlesize = 14
    var_label = r'Lateral Vapor Convergence $[mm$ $h^{-1}]$'

    dom_alpine_region = {
        'label':'Alpine Region',
        'rlon':(-3.76,3.68),
        'rlat':(-3.44,1.08),}
    domain = dom_alpine_region

    time_chunk = 1


    #####################################################################		

    dt_range = np.arange(start_time, end_time+timedelta(hours=1),
                        timedelta(hours=1)).tolist()


    if i_recompute:
        t_start = time.time()
        print('Loading')
        members = {}
        for res in resolutions:

            # get area of domain
            path = os.path.join(inp_path, 'RAW'+str(res), 'zQV.nc')
            qv = xr.open_dataset(path, )['QV']
            qv = qv.sel(rlon=slice(domain['rlon'][0],domain['rlon'][1]),
                        rlat=slice(domain['rlat'][0],domain['rlat'][1]))
            area = len(qv.coords['rlon']) * len(qv.coords['rlat']) * dx[res]**2

            # load all members
            for member_type in member_types:
                member_str = member_type+str(res)
                print(member_str)
                all_fields = []
                for flx_key,flx_dict in fluxes.items():
                    #print(flx_key)
                    path = os.path.join(inp_path, 
                                member_str, flx_dict['field']+'.nc')
                    field = xr.open_dataset(path, 
                                chunks={'time':time_chunk})[flx_dict['field'][1:]]
                    path = os.path.join(inp_path, 
                                member_str, 'zRHO.nc')
                    rho = xr.open_dataset(path, 
                                chunks={'time':time_chunk})['RHO']
                    path = os.path.join(inp_path, 
                                member_str, 'zQV.nc')
                    qv = xr.open_dataset(path, 
                                chunks={'time':time_chunk})['QV']

                    # rename staggered dimensions
                    field = unstaggering(field)
                    rho = unstaggering(rho)
                    qv = unstaggering(qv)

                    # compute mass flux
                    field = field * rho * qv

                    # select time and altitue
                    field = field.sel(time=slice(start_time,end_time),
                                      altitude=altitudes)

                    # select directional and perpendicular dimension 
                    ds = 0.01
                    kwargs = {flx_dict['mean']:slice(
                            domain[flx_dict['mean']][flx_dict['mean_ind']]-2*ds,
                            domain[flx_dict['mean']][flx_dict['mean_ind']]+ds),
                              flx_dict['sum']:slice(
                            domain[flx_dict['sum']][0], domain[flx_dict['sum']][1]),}
                    field   = field.sel(**kwargs)
                    print(field.values.shape)

                    # aggregate in directional dimesion
                    field   = field.mean(dim=flx_dict['mean'])
                    # aggregate in perpendicular dimesion
                    field   = field.sum(dim=flx_dict['sum'])*dx[res]
                    # aggreagte vertically
                    field = field.integrate(dim=['altitude'])
                    # multiply with unit vector of direction
                    field.values = field.values * flx_dict['dir']
                    # convert to [mm h-1] within domain
                    field.values = field.values / area * 3600

                    #calculate diurnal cycle and store
                    field = calc_mean_diurnal_cycle(field)
                    field = field.rename(flx_key)
                    all_fields.append(field)

                all_fields = xr.merge(all_fields)
                members[member_str] = all_fields

        # Calculate total flux over all edges
        for res in resolutions:
            for member_type in member_types:
                member_str = member_type+str(res)
                fields = members[member_str]
                fields['TOT'] = (fields['W'] + fields['E'] + 
                                 fields['N'] + fields['S'] )
                members[member_str] = fields

        # Calculate total flux difference between RAW and SM
        for res in resolutions:
            RAW_str = 'RAW'+str(res)
            SM_str = 'SM'+str(res)
            fields = members[RAW_str]
            fields['DIFF'] = members[RAW_str]['TOT'] - members[SM_str]['TOT']
            members[RAW_str] = fields

        pickle.dump(members, open(pickle_save_file, 'wb'))

        t_end = time.time()
        print('Computation complete. Took ' + 
                str(round(t_end - t_start,0)) + ' sec.')

    else:
        members = pickle.load(open(pickle_save_file, 'rb'))


    if i_plot: 
        #name_dict = {'':'new_eval'}
        #PO = PlotOrganizer(i_save_fig, path=plot_path, name_dict=name_dict)
        #PO.initialize_plot(nrow=2, ncol=3)
        ##PO.fig.set_size_inches(2*stretchCol,1*stretchRow)

        #for flx_key,ax_dict in axes_dicts.items():
        #    print(flx_key)
        #    ax = PO.axes[ax_dict['row_ind'],ax_dict['col_ind']]
        #    for member_type in member_types:
        #        for res in resolutions:
        #            if flx_key == 'DIFF' and member_type != 'RAW':
        #                print(flx_key + member_type + str(res))
        #                continue
        #            member_str = member_type+str(res)
        #            field = members[member_str][flx_key]

        #            hours = np.append(field.coords['diurnal'].values, 24)
        #            vals = np.append(field.values, field.values[0])
        #            line, = ax.plot(hours, vals, color=plot_dict['res_color'][res],
        #                    linestyle=plot_dict['mem_linestyle'][member_type],
        #                    label=member_type)

        #            ax.set_title(flx_key)
        #            if flx_key == 'W':
        #                PO.handles.append(line)
        #            ax.axhline(y=0, color='grey')
        #            ax.set_xlim((0,24))
        #            #ax.set_ylim((-5E9,5E9))
        #            ax.set_xlabel('Hour')
        #            ax.set_ylabel('Mass flux [kg s-1]')

        #PO.fig.tight_layout()
        #plt.legend(handles=PO.handles) 
        #print(PO.handles)
        #PO.finalize_plot()



        # PLOT
        axes_config = {
            0:{'mem':'SM'},
            1:{'mem':'RAW'},
            2:{'mem':'RAW - SM'},
        }
        fig,axes = plt.subplots(1,3, figsize=(11,4))
        lines = []
        for axI in range(3):
            ax = axes[axI]
            member_type = axes_config[axI]['mem']
            ax.set_ylim(ylims)
            ax.axhline(y=0, color='k', lineWidth=1)
            ax.set_xticks([0,6,12,18,24])
            ax.set_xlim((0,24))
            ax.set_xlabel('Hour',fontsize=labelsize)
            ax.grid()
            ax.set_title(member_type,fontsize=titlesize)
            if axI == 0:
                ax.set_ylabel(var_label,fontsize=labelsize)

            for res in resolutions:
                if member_type == 'RAW - SM':
                    raw = members['RAW'+res]['TOT']
                    sm = members['SM'+res]['TOT']
                    field = raw - sm
                else:
                    field = members[member_type+res]['TOT']
                hours = np.append(field.coords['diurnal'].values, 24)
                vals = np.append(field.values, field.values[0])
                line, = ax.plot(hours, vals, color=plot_dict['res_color'][res],
                        label=res)
                if axI == 0:
                    lines.append(line)


        axes[0].legend(handles=lines)
        fig.subplots_adjust(wspace=0.23,
                left=0.07, right=0.95, bottom=0.15, top=0.85)

        if i_save_fig == 1:
            plot_path = plot_path + '/' + plot_name+'.png'
            plt.savefig(plot_path, format='png', bbox_inches='tight')
            plt.close(fig)
        elif i_save_fig == 2:
            plot_path = plot_path + '/' + plot_name+'.pdf'
            plt.savefig(plot_path, format='pdf', bbox_inches='tight')
            plt.close('all')
        else:
            plt.show()
            plt.close(fig)

    




