from netCDF4 import Dataset
import numpy as np

day0 = 11
#day0 = 12
day1 = 19 
#day1 = 12 
ress = [4.4, 2.2, 1.1]
#ress = [2.2]
modes = ['', 'f']
i_plot = 1
plotOutDir = '00_plots/08_cloud_cluster'
plotName = 'cloud_size_absFreq_dist_and_diff_NEW'
nbins = 40
i_subdomain = 1
from ncClasses.subdomains import setSSI
ssI, domainName = setSSI(i_subdomain, {'4.4':{}, '2.2':{}, '1.1':{}}) 

colrs = [(0,0,0), (0,0,1), (1,0,0)]
labelsize = 12
titlesize = 14

import matplotlib
if i_plot > 1:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt

days = np.repeat(np.arange(day0,day1+1),24)
hours = np.tile(np.arange(0,24),day1-day0+1)


allSizes = []
outRess = []
outModes = []
labels = []

for res in ress:
    xmin = ssI[str(res)]['rlon'][0]
    xmax = ssI[str(res)]['rlon'][-1]
    ymin = ssI[str(res)]['rlat'][0]
    ymax = ssI[str(res)]['rlat'][-1]
    for mode in modes:
        print(str(res)+mode)
        inpPath = '01_rawData/cloud_cluster/'+str(res)+mode
        sizes = []
        for i in range(0,len(days)):
            file = 'lffd200607'+str(days[i]).zfill(2) + str(hours[i]).zfill(2) + 'z.nc'
            fullPath = inpPath + '/' + file
            nc = Dataset(fullPath, 'r')

            factor = np.power(res,2)

            xc = nc['XCENTER'][:]
            yc = nc['YCENTER'][:]
            mask = np.argwhere((
                (xc >= xmin) & (xc <= xmax) & (
                yc >= ymin) & (yc <= ymax)).squeeze()).squeeze()

            inp = nc['SC'][:].squeeze()
            if inp.ndim > 0:
                size = inp[mask]*factor
            else:
                size = np.asarray([])
            #size = factor*nc['SC'][:].squeeze()
            size = [size] if size.ndim == 0 else size
            sizes.extend(size)
        sizes = np.asarray(sizes)
        print('n clouds: ' + str(sizes.shape[0]))
        allSizes.append(sizes)
        outRess.append(str(res))
        outModes.append(mode)
        labels.append(str(res)+mode)

bins = np.logspace(0,5,num=nbins)
binsCentred = bins[0:(len(bins)-1)] + np.diff(bins)/2

# CREATE HISTOGRAMS
nclouds = []
freqs = []
for sizes in allSizes:
    hist = np.histogram(sizes, bins=bins)
    ncloud = hist[0]
    freq = ncloud/len(sizes)
    nclouds.append(ncloud)
    freqs.append(freq)


#### Relative cloud size frequency distribution
#fig = plt.figure(figsize=(6,7))
#handles = []
#for i in range(0,len(freqs)):
#    if outModes[i] == 'f':
#        lstyle = '--'
#    else:
#        lstyle = '-'
#    line, = plt.loglog(binsCentred, freqs[i], lstyle) 
#    handles.append(line)
#plt.legend(handles, labels)
#plt.xlabel('cloud size [$km^2$]')
#plt.ylabel('relative frequency')
#plt.xlim((2E0,1E5))
#plt.ylim((5E-6,2E-1))
#plt.title('Relative Cloud Size Frequency Distribution')
#plt.grid()
#if i_save:
#    outName = 'cloud_size_relFreq_dist.png'
#    plt.savefig(outPath + outName)
#else:
#    plt.show()
#plt.close(fig)

### Absolute cloud number distribution
colrs = [(0,0,0), (0,0,1), (1,0,0)]
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(11,4))
handles = []
modeStrings = ['SM', 'RAW', '(RAW - SM)/SM']
#modes.append('d')
#for mI,mode in enumerate(modes):
#    for rI,res in enumerate(ress):
#        print(str(res)+mode)
#        ax = axes[mI]

for i in range(0,len(ress)):


    # ABSOLUTE VALUES
    nClRaw = nclouds[i*2]
    nClSmo = nclouds[i*2+1]
    line, = axes[0].loglog(binsCentred, nClSmo, '-', color=colrs[i]) 
    axes[1].loglog(binsCentred, nClRaw, '-', color=colrs[i]) 
    handles.append(line)

    if i == 2:
        axes[0].legend(handles, ress)


    for j in range(0,3):
        ax = axes[j]
        ax.set_xlabel('Cloud Size [$km^2$]',fontsize=labelsize)
        if j == 0:
            ax.set_ylabel('Number of Clouds',fontsize=labelsize)
        #elif j == 2:
        #    ax.set_ylabel('Ratio',fontsize=labelsize)
        ax.set_xlim((1E0,1E5))
        if j < 2:
            ax.set_ylim((1E0,1E5))
        elif j == 2:
            ax.set_ylim((-0.6,0.6))
            #ax.set_ylim((-1,1))
            ax.axhline(y=0, color='k', lineWidth=0.5)
        ax.set_title(modeStrings[j],fontsize=titlesize)
        ax.grid()

    # MASKING OF VALUES WITH SMALL AMOUNT OF CLOUDS
    minNClouds = 30
    mask = np.full(len(nClRaw),1)
    mask[nClRaw < minNClouds] = 0
    mask[nClSmo < minNClouds] = 0


    # RELATIVE DIFFERENCE 
    ax = axes[2]
    raw = nclouds[i*2].astype(np.float)
    sm = nclouds[i*2+1].astype(np.float)
    raw[raw == 0] = np.nan
    sm[sm == 0] = np.nan
    ratio = (raw - sm)/sm
    ratio[mask == 0] = np.nan
    line, = ax.semilogx(binsCentred, ratio, '-', color=colrs[i]) 
    sumRaw = np.sum(nclouds[i*2])
    sumSmoothed = np.sum(nclouds[i*2+1])
    sumRatio = sumRaw/sumSmoothed
    #ax.text(2E0, 0.8, 'raw/smoothed: '+str(np.round(sumRatio,2)))

    # LABELS
    ax = axes[1]
    x = 1.5
    yTop = 3E1
    ry = 0.42
    size = 13
    if i == 0:
        ax.text(x, yTop, 'RAW/SM:', size=size,
                bbox=dict(boxstyle='square',ec=(1,1,1,0.5),fc=(1,1,1,0.5)))
    ax.text(x, yTop*(ry**(i+1)), '{:3.2f}'.format(sumRatio,2), size=size, color=colrs[i],
            bbox=dict(boxstyle='square',ec=(1,1,1,0.5),fc=(1,1,1,0.5)))


#plt.suptitle('Absolute Cloud Size Distribution and Relative Difference')
#plt.subplots_adjust(left=0.07, right=0.95, top=0.92, bottom=0.08, wspace=0.27, hspace=0.33)
fig.subplots_adjust(wspace=0.23,left=0.07, right=0.95, bottom=0.15, top=0.85)

if i_plot == 1:
	plt.show()
elif i_plot == 2:
    plotPath = plotOutDir + '/' + plotName+'.png'
    plt.savefig(plotPath, format='png', bbox_inches='tight')
    plt.close('all')
elif i_plot == 3:
    plotPath = plotOutDir + '/' + plotName+'.pdf'
    plt.savefig(plotPath, format='pdf', bbox_inches='tight')
    plt.close('all')

		  
