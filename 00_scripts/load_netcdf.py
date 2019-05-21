from netCDF4 import Dataset
import xarray as xr

nc_file = 'input.nc'
field_name = 'TOT_PREC'

### BASIC VERSION
ncf = Dataset(nc_file,'r')
field = ncf[field_name]
array = field[:]
first_timestep = field[0,:,:]

print(ncf)
print(field)
#print(array)
#print(first_timestep)




### RECOMMENDED VERSION
ncf = xr.open_dataset(nc_file)
print(ncf)
field = ncf[field_name]
print(field)

# you rarely need to access the actual array values because
# most of the operations can be done 'on the level of the field.'
array = field.values

# for instance select subdomain
lat_slice = field.sel(rlat=slice(0,1), rlon=slice(0,1))
print(lat_slice)
# or integrate over latitude
lat_integ = field.integrate(dim='rlat')
print(lat_integ)
