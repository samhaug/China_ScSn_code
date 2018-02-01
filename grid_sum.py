#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : grid_sum.py
Purpose : Sum reverberations over grid.
Creation Date : 22-01-2018
Last Modified : Thu 01 Feb 2018 04:20:06 PM EST
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from subprocess import call
from os import listdir
import h5py
import argparse
from geopy.distance import vincenty
from scipy.signal import gaussian
from scipy.spatial import KDTree
from matplotlib import pyplot as plt

def main():
    parser = argparse.ArgumentParser(description='perform grid')
    parser.add_argument('-r','--reflection', metavar='H5_FILE',type=str,
                       help='h5 reflection point file')
    parser.add_argument('-m','--mvout', metavar='H5_FILE',type=str,
                        help='h5 moveout corrected deconvolved data')
    args = parser.parse_args()
    m = h5py.File(args.mvout,'r',driver='core')
    r = h5py.File(args.reflection,'r',driver='core')

    lon_a,lat_a,h_a,grid = make_grid_coordinates()
    grid_count = np.zeros(grid.shape)
    x,y = np.meshgrid(lon_a,lat_a)
    x = x.ravel()
    y = y.ravel()
    coords = zip(x,y)
    tree = KDTree(coords)

    for h in h_a:
        print 'Depth: {} km'.format(h)
        h_idx= np.abs(h_a-h).argmin()
        for ikeys in r.keys():
            for phase in r[ikeys]:
                if not phase.startswith('c'):
                    r_coord = r[ikeys][phase][str(h)]
                    for ii in r_coord:
                        i = tree.query_ball_point((ii[1],ii[0]),2.0)
                        for jj in i:
                            lon_idx = np.abs(lon_a-x[jj]).argmin()
                            lat_idx = np.abs(lat_a-y[jj]).argmin()
                            grid_count[lon_idx,lat_idx,h_idx]+=1.
                            v = find_reverb_value(m,h,ikeys,phase)
                            grid[lon_idx,lat_idx,h_idx]+=v

    r.close()
    m.close()

    try:
        g = h5py.File('grid_sum.h5','w',driver='core')
    except IOError:
        call('rm -rf grid_sum.h5',shell=True)
        g = h5py.File('grid_sum.h5','w',driver='core')

    g.create_dataset('grid',data=grid)
    g.create_dataset('grid_count',data=grid_count)
    g.create_dataset('lat',data=lat_a)
    g.create_dataset('lon',data=lon_a)
    g.create_dataset('h',data=h_a)
    g.close()

def find_reverb_value(m,h,ikey,phase):
    depth = m[ikey][phase][0,:]
    data = m[ikey][phase][1,:]
    return data[np.abs(depth-h).argmin()]

def make_grid_coordinates():
    lonmin,lonmax = 80,150
    latmin,latmax = -10,50
    hmin,hmax = 50,800
    lon = np.linspace(lonmin,lonmax,num=int(2*(lonmax-lonmin)))
    lat = np.linspace(latmin,latmax,num=int(2*(latmax-latmin)))
    h = np.arange(hmin,hmax+5,5)
    grid = np.zeros((len(lon),len(lat),len(h)))
    return lon,lat,h,grid


main()


