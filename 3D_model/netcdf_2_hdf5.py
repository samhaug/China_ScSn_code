#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : netcdf_2_hdf5.py
Purpose : convert netcdf model to h5py file model.
Creation Date : 29-01-2018
Last Modified : Mon 29 Jan 2018 04:00:43 PM EST
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
#from matplotlib import pyplot as plt
import h5py
from netCDF4 import Dataset


dataset = Dataset('3D2016-09Sv-depth.nc')
lat = dataset.variables['latitude'][:]
lon = dataset.variables['longitude'][:]
h = dataset.variables['depth'][:]
dvs = dataset.variables['dvs'][:].data
#plt.imshow(dvs[1],aspect='auto',extent=[lon.min(),lon.max(),lat.min(),lat.max()])
#plt.show()

f = h5py.File('3D2016.h5','w',driver='core')
f.create_dataset('lat',data=lat)
f.create_dataset('lon',data=lon)
f.create_dataset('h',data=h)
f.create_dataset('dvs',data=dvs)


