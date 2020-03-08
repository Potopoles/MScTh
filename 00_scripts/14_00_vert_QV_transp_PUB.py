import os, copy, pickle
import numpy as np
from package.domains import dom_alpine_region
from package.functions import calc_mean_diurnal_cycle
from package import nl_plot_global
import xarray as xr
import matplotlib.pyplot as plt

diurnal_data = '02_fields/topocut'
file_name = 'tmp.pkl'

#models = ['RAW1', 'SM1']
#models = ['RAW4', 'SM4']
models = ['RAW4', 'SM4', 'RAW2', 'SM2', 'RAW1', 'SM1']
#alts = [500, 1000, 1500, 2000, 2500, 3000, 4000, 5000]
alts = [2000, 2500]
i_recompute = 0
plot_out_dir = '00_plots/15_vert_QV_transp'

if i_recompute:
    model_data = {}
    for model in models:
        print(model)

        rho_path = os.path.join(diurnal_data, model, 'zRHO.nc')
        #rho = xr.open_dataset(qv_path, chunks={'time':24})['RHO']
        rho = xr.open_dataset(rho_path)['RHO']
        rho = rho.sel(rlon=dom_alpine_region['lon'],
                    rlat=dom_alpine_region['lat'], altitude=alts)

        qv_path = os.path.join(diurnal_data, model, 'zQV.nc')
        #qv = xr.open_dataset(qv_path, chunks={'time':24})['QV']
        qv = xr.open_dataset(qv_path)['QV']
        qv = qv.sel(rlon=dom_alpine_region['lon'],
                    rlat=dom_alpine_region['lat'], altitude=alts)

        qc_path = os.path.join(diurnal_data, model, 'zQC.nc')
        #qc = xr.open_dataset(qc_path, chunks={'time':24})['qc']
        qc = xr.open_dataset(qc_path)['QC']
        qc = qc.sel(rlon=dom_alpine_region['lon'],
                    rlat=dom_alpine_region['lat'], altitude=alts)


        w_path = os.path.join(diurnal_data, model, 'zW.nc')
        #w = xr.open_dataset(w_path, chunks={'time':24})['W']
        w = xr.open_dataset(w_path)['W']
        w = w.sel(rlon=dom_alpine_region['lon'],
                    rlat=dom_alpine_region['lat'], altitude=alts)

        qv_flux = w * qv * rho
        qv_flux = qv_flux.mean(dim=['rlon', 'rlat'])
        qv_flux = calc_mean_diurnal_cycle(qv_flux)

        qc_flux = w * qc * rho
        qc_flux = qc_flux.mean(dim=['rlon', 'rlat'])
        qc_flux = calc_mean_diurnal_cycle(qc_flux)

        model_data['QV_{}'.format(model)] = qv_flux
        model_data['QC_{}'.format(model)] = qc_flux

    pickle.dump(model_data, open(file_name, 'wb'))


model_data = pickle.load(open(file_name, 'rb'))
hours = np.arange(0,25)
fig,axes = plt.subplots(nrows=1, ncols=3)

alt = 2000
var_name = 'QV'
ress = ['4', '2', '1']
cols = {'4':'black','2':'blue','1':'red'}
mkeys = ['SM', 'RAW']
for colI in range(3):
    ax = axes[colI]
    handles = []
    for res in ress:
        if colI < 2:
            vals = model_data['{}_{}{}'.format(
                            var_name, mkeys[colI], res)].sel(altitude=alt).values
            plot_vals = copy.copy(vals)*1000
            label = '{}{}'.format(mkeys[colI],res)
            title = mkeys[colI]
        else:
            vals = model_data['{}_{}{}'.format(
                            var_name, 'RAW', res)].sel(altitude=alt).values -  \
                    model_data['{}_{}{}'.format(
                            var_name, 'SM', res)].sel(altitude=alt).values
            plot_vals = copy.copy(vals)*1000
            #label = '{}{} - {}{}'.format('RAW',res,'SM',res)
            title = 'RAW - SM'
        plot_vals = np.append(plot_vals, plot_vals[0])

        line, = ax.plot(hours, plot_vals, label=label, color=cols[res])
        handles.append(line)
    if colI < 2:
        ax.legend(handles=handles)
    if colI == 0:
        if var_name == 'QV':
            ax.set_ylabel('Vertical q$_v$-flux $[g$ $m^{-2}$ $s^{-1}]$')
        elif var_name == 'QC':
            ax.set_ylabel('Vertical q$_c$-flux $[g$ $m^{-2}$ $s^{-1}]$')
    ax.set_xlabel('Time (UTC)')
    ax.set_xlim((0,24))
    ax.set_xticks(np.arange(0,24.1,6))
    if colI < 2:
        if var_name == 'QV':
            ax.set_ylim((-0.05,0.15))
            ax.set_yticks(np.arange(-0.05,0.16,0.05))
        elif var_name == 'QC':
            ax.set_ylim((-0.01,0.01))
            #ax.set_yticks(np.arange(-0.05,0.16,0.05))
    else:
        if var_name == 'QV':
            ax.set_ylim((-0.04,0.06))
        elif var_name == 'QC':
            ax.set_ylim((-0.01,0.01))
    ax.text(0,ax.get_ylim()[1] + (ax.get_ylim()[1] - ax.get_ylim()[0])*0.03, ['a)','b)','c)'][colI],
            weight='bold')
    ax.grid()
    ax.axhline(y=0, color='k')
    ax.set_title(title)

fig.set_size_inches((12,4))
fig.subplots_adjust(left=0.10, right=0.98, bottom=0.15, top=0.91,
                        wspace=0.25)
plt.savefig('{}/vert_{}_transport.pdf'.format(plot_out_dir,var_name), format='pdf')
plt.savefig('{}/vert_{}_transport.png'.format(plot_out_dir,var_name), format='png')
plt.show()
