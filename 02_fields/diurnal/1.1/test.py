import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

k = 2
i = 10
j = 10


data = xr.open_dataset('zFQVy.nc')
new = data['FQVy']
new = new.isel(altitude=slice(k,k+1))#, rlon=slice(i,i+1), rlat=slice(j,j+1))
print(new)
data = xr.open_dataset('zFQVy.nc.old')
old = data['FQVy']
old = old.isel(altitude=slice(k,k+1))#, rlon=slice(i,i+1), rlat=slice(j,j+1))
print(old)
print()


n = 2
new = new.isel(time=slice(n,n+1))
old = old.isel(diurnal=slice(n,n+1))
print(new.shape)
print(old.shape)
diff = old.values - new.values

#plt.contourf(diff.squeeze())
new.values[new.values > 1E30] = np.nan
plt.contourf(new.squeeze())
plt.colorbar()
plt.show()
