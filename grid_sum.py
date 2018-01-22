#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : grid_sum.py
Purpose : Sum reverberations over grid.
Creation Date : 22-01-2018
Last Modified : Mon 22 Jan 2018 04:42:15 PM EST
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

def main():
    parser = argparse.ArgumentParser(description='perform grid')
    parser.add_argument('-r','--reflection', metavar='H5_FILE',type=str,
                        help='h5 reflection point file')
    parser.add_argument('-m','--mvout', metavar='H5_FILE',type=str,
                        help='h5 moveout corrected data')
    args = parser.parse_args()
    m = h5py.File(args.mvout,'r',driver='core')
    r = h5py.File(args.reflection,'r',driver='core')

    lon_a,lat_a,h_a,grid = make_grid_coordinates()
    h_a = [670,670]

    for idx,lon in enumerate(lon_a):
        for jdx,lat in enumerate(lat_a):
            for kdx,h in enumerate(h_a):
                a = search_for_reflection(lon,lat,h,r,200)
                print a

def search_for_reflection(lon,lat,h,r,dist_cutoff_in_km):
    gl = int(dist_cutoff_in_km)
    gaussian_cap = gaussian(gl,int(gl/6.))[int(gl/2.)::]
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
    #m = Basemap(llcrnrlon=70,llcrnrlat=-20,urcrnrlon=170,
    #        urcrnrlat=60,projection='mill')
    #lonmin,lonmax = 70,170
    #latmin,latmax = -20,60
    #hmin,hmax = 50,750
    lonmin,lonmax = 70,160
    latmin,latmax = 0,60
    hmin,hmax = 50,750
    lon = np.linspace(lonmin,lonmax,num=int(0.1*(lonmax-lonmin)))
    lat = np.linspace(latmin,latmax,num=int(0.1*(latmax-latmin)))
    h = np.arange(hmin,hmax,5)
    grid = np.zeros((len(lon),len(lat),len(h)))
    return lon,lat,h,grid


main()
