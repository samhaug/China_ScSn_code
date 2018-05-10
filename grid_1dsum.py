#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : grid_1dsum.py
Purpose : Sum reverberations over grid. Use 1d moveout correction lkup table
Creation Date : 22-01-2018
Last Modified : Thu 10 May 2018 10:50:30 AM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from subprocess import call
from os import listdir
import h5py
import argparse
from scipy.interpolate import interp1d
from geopy.distance import vincenty
from geopy.distance import VincentyDistance
from geopy import Point
from scipy.signal import gaussian
from scipy.spatial import KDTree
from matplotlib import pyplot as plt
from obspy.geodetics import gps2dist_azimuth
import re

def main():
    parser = argparse.ArgumentParser(description='perform grid')
    parser.add_argument('-r','--reflection', metavar='H5_FILE',type=str,
                        help='h5 1d reflection lookup table made with taup')
    parser.add_argument('-t','--time', metavar='H5_FILE',type=str,
                        help='h5 1d time lookup table made with taup')
    parser.add_argument('-d','--deconvolve', metavar='H5_FILE',type=str,
                        help='h5 deconvolved data')
    parser.add_argument('-g','--grid', metavar='H5_FILE',type=str,
                        help='optional name of output grid file',
                        default='grid_1dsum.h5')
    args = parser.parse_args()

    r = h5py.File(args.reflection,'r',driver='core')
    t = h5py.File(args.time,'r',driver='core')
    d = h5py.File(args.deconvolve,'r',driver='core')

    lon_a,lat_a,h_a,grid = make_grid_coordinates()
    grid_count = np.zeros(grid.shape)
    grid_count_s2 = np.zeros(grid.shape)
    grid_s2 = np.zeros(grid.shape)
    x,y = np.meshgrid(lon_a,lat_a)
    x = x.ravel()
    y = y.ravel()
    coords = zip(x,y)
    tree = KDTree(coords)
    gauss_cap = gaussian(424,90)[212::]
    origin = Point(d[d.keys()[0]]['coords'][4],
                         d[d.keys()[0]]['coords'][5])

    def sum_grid(rkey,tkey,t_pure,waveform,gcarc_id,az):
        km = r[rkey][str(int(h))]['deg'][gcarc_id]*111.19
        time  = t[tkey][str(int(h))][gcarc_id]
        dest = VincentyDistance(kilometers=km).destination(origin,az)
        lon_idx = np.argmin(np.abs(lon_a-dest.longitude))
        lat_idx = np.argmin(np.abs(lat_a-dest.latitude))
        stack_d = waveform[int(np.abs(time-t_pure)*10)+500]
        i = tree.query_ball_point((dest.longitude,dest.latitude),2.0)
        for jj in i:
            lon_idx = np.abs(lon_a-x[jj]).argmin()
            lat_idx = np.abs(lat_a-y[jj]).argmin()
            grid_count[lon_idx,lat_idx,h_idx]+=1.
            grid[lon_idx,lat_idx,h_idx]+=stack_d


    #for each depth in grid
    for dkeys in d:
        data_dict = {}
        print dkeys
        b = d[dkeys]['coords'][:]
        gcarc_id = int(round(b[0]*2.))
        az = gps2dist_azimuth(b[2],b[3],b[4],b[5])[2]
        t_ScSScS     = t['ScSScS']['PURE'][gcarc_id]
        t_ScSScSScS  = t['ScSScSScS']['PURE'][gcarc_id]
        t_sScS       = t['sScS']['PURE'][gcarc_id]
        t_sScSScS    = t['sScSScS']['PURE'][gcarc_id]
        t_sScSScSScS = t['sScSScSScS']['PURE'][gcarc_id]
        #plt.scatter(b[3],b[2],color='k')
        #plt.scatter(b[5],b[4],color='r')
        for pkeys in d[dkeys]:
            if pkeys == 'coords':
                continue
            else:
                data = d[dkeys][pkeys][:]
                data *= 1./np.max(np.abs(data))
                data_dict[pkeys] = data

        for h_idx,h in enumerate(h_a):
            for keys in data_dict:
                waveform = data_dict[keys]

                if keys == 'ScSScS':
                    tkey = 'ScSScS'
                    sum_grid('ScS2',tkey,t_ScSScS,waveform,gcarc_id,az)

                if keys == 'ScSScSScS':
                    tkey = 'ScSScSScS'
                    sum_grid('ScS3_1',tkey,t_ScSScSScS,waveform,gcarc_id,
                             az)
                    sum_grid('ScS3_2',tkey,t_ScSScSScS,waveform,gcarc_id,
                             az)

                if keys == 'sScS':
                    tkey = 'sScS'
                    sum_grid('sScS_1',tkey,t_sScS,waveform,gcarc_id,
                             az)
                    sum_grid('sScS_2',tkey,t_sScS,waveform,gcarc_id,
                             az)

                if keys == 'sScSScS':
                    tkey = 'sScSScS'
                    sum_grid('sScS2_1',tkey,t_sScSScS,waveform,gcarc_id,
                             az)
                    sum_grid('sScS2_2',tkey,t_sScSScS,waveform,gcarc_id,
                             az)
                    sum_grid('sScS2_3',tkey,t_sScSScS,waveform,gcarc_id,
                             az)

                if keys == 'sScSScSScS':
                    tkey = 'sScSScSScS'
                    sum_grid('sScS3_1',tkey,t_sScSScSScS,waveform,gcarc_id,
                             az)
                    sum_grid('sScS3_2',tkey,t_sScSScSScS,waveform,gcarc_id,
                             az)
                    sum_grid('sScS3_3',tkey,t_sScSScSScS,waveform,gcarc_id,
                             az)
                    sum_grid('sScS3_4',tkey,t_sScSScSScS,waveform,gcarc_id,
                             az)


    plt.show()

    r.close()
    t.close()
    d.close()
    #plt.show()

    try:
        g = h5py.File(args.grid,'w',driver='core')
    except IOError:
        call('rm -rf '+args.grid,shell=True)
        g = h5py.File(args.grid,'w',driver='core')

    g.create_dataset('grid',data=grid)
    g.create_dataset('grid_count',data=grid_count)
    g.create_dataset('grid_ScS2',data=grid_s2)
    g.create_dataset('grid_count_ScS2',data=grid_count_s2)
    g.create_dataset('lat',data=lat_a)
    g.create_dataset('lon',data=lon_a)
    g.create_dataset('h',data=h_a)
    g.close()


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




