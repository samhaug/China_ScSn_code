#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : grid_sum.py
Purpose : Sum reverberations over grid.
Creation Date : 22-01-2018
Last Modified : Tue 23 Jan 2018 02:34:17 PM EST
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
                        help='h5 moveout corrected data')
    parser.add_argument('-d','--depth', metavar='H5_FILE',type=int,default=670,
                        help='conversion depth')
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

    h_idx= np.abs(h_a-args.depth).argmin()
    for ikeys in r.keys()[::10]:
        for phase in r[ikeys]:
            if not phase.startswith('c'):
                r_coord = r[ikeys][phase][str(args.depth)]
                for ii in r_coord:
                    i = tree.query_ball_point((ii[1],ii[0]),2.0)
                    for jj in i:
                        print jj
                        lon_idx = np.abs(lon_a-x[jj]).argmin()
                        lat_idx = np.abs(lat_a-y[jj]).argmin()
                        grid_count[lon_idx,lat_idx,h_idx]+=1.
                        v = find_reverb_value(m,args.depth,ikeys,phase)
                        grid[lon_idx,lat_idx,h_idx]+=v

    r.close()
    m.close()

    plt.imshow(grid[:,:,h_idx]/grid_count[:,:,h_idx],aspect='auto',extent=[lon_a.min(),
                                                          lon_a.max(),
                                                          lat_a.max(),
                                                          lat_a.min()])
    plt.show()

def find_reverb_value(m,h,ikey,phase):
    depth = m[ikey][phase][0,:]
    data = m[ikey][phase][1,:]
    return data[np.abs(depth-h).argmin()]

def search_for_reflection(lon,lat,h,r,dist_cutoff_in_km):
    gl = int(dist_cutoff_in_km)
    gaussian_cap = gaussian(gl*2+10,int(gl/6.))[int(gl/2.)::]
    #r is reflection file

    a = []
    for ikeys in r:
        for phase in r[ikeys]:
            if not phase.startswith('c'):
                for ii in r[ikeys][phase][str(h)][:]:
                    try:
                        d = vincenty((lat,lon),tuple(ii)).kilometers
                    except ValueError:
                        continue
                    if d < dist_cutoff_in_km:
                        cap_factor = gaussian_cap[int(dist_cutoff_in_km-d)]
                        a.append([ikeys,phase,cap_factor])

    return a

def make_grid_coordinates():
    lonmin,lonmax = 75,150
    latmin,latmax = 10,50
    hmin,hmax = 50,750
    lon = np.linspace(lonmin,lonmax,num=int(2*(lonmax-lonmin)))
    lat = np.linspace(latmin,latmax,num=int(2*(latmax-latmin)))
    h = np.arange(hmin,hmax,5)
    grid = np.zeros((len(lon),len(lat),len(h)))
    return lon,lat,h,grid


main()


