#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : grid_sum.py
Purpose : Sum reverberations over grid.
Creation Date : 22-01-2018
Last Modified : Mon 30 Apr 2018 03:08:12 PM EDT
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
from scipy.signal import gaussian
from scipy.spatial import KDTree
from matplotlib import pyplot as plt
from geopy.distance import vincenty
import re

def main():
    parser = argparse.ArgumentParser(description='perform grid')
    parser.add_argument('-r','--reflection', metavar='H5_FILE',type=str,
                        help='h5 reflection point file')
    parser.add_argument('-l','--lkup', metavar='H5_FILE',type=str,
                        help='h5 3d moveout lookup table')
    parser.add_argument('-d','--deconvolve', metavar='H5_FILE',type=str,
                        help='h5 deconvolved data')
    parser.add_argument('-g','--grid', metavar='H5_FILE',type=str,
                        help='optional name of output grid file',
                         default='grid_sum.h5')
    args = parser.parse_args()
    print args.grid

    l = h5py.File(args.lkup,'r',driver='core')
    r = h5py.File(args.reflection,'r',driver='core')
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

    #for each depth in grid
    for h in h_a:
        print 'Depth: {} km'.format(h)
        h_idx= np.abs(h_a-h).argmin()
        #for each station name in the reflection lookup
        for rkeys in r:
            #for each parent phase accepted for the station
            for phase in r[rkeys]:
                #As long as it's not the coordinate info list
                if not phase.startswith('c'):
                    data,lkup_dict = prepare_data_lookup(d,l,rkeys,phase)
                    conv_list = make_pierce_coord(phase,str(h))
                    #For each coordinate in pierce_coord
                    #for pierce_coord in r[rkeys][phase]:
                    for pierce_coord in conv_list:
                        try:
                        #print pierce_coord
                            depth = int(re.findall('\d+',pierce_coord)[0])
                            pc = r[rkeys][phase][pierce_coord][:]
                            dl,tl = lkup_dict[pierce_coord.replace(str(depth),
                                              'X')]
                            #Get data value closest to time. 
                            #assume samp_rate=10
                            v = data[int(tl[np.argmin(np.abs(h-dl))]*10)]
                            i = tree.query_ball_point((pc[1],pc[0]),2.0)
                            for jj in i:
                            #    dist = vincenty((pc[0],pc[1]),(y[jj],x[jj])).km
                            #    try:
                            #        v *= gauss_cap[int(dist)]
                            #    except IndexError:
                            #        v *= gauss_cap[-1]
                                lon_idx = np.abs(lon_a-x[jj]).argmin()
                                lat_idx = np.abs(lat_a-y[jj]).argmin()
                                grid_count[lon_idx,lat_idx,h_idx]+=1.
                                grid[lon_idx,lat_idx,h_idx]+=v
                                if phase == 'ScSScS':
                                    grid_count_s2[lon_idx,lat_idx,h_idx]+=1.
                                    grid_s2[lon_idx,lat_idx,h_idx]+=v
                        except KeyError:
                            continue
    r.close()
    l.close()

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

def make_pierce_coord(phase,depth):
    phase_families = {'sScS':['sSvXSScS','sScSSvXS'],
                     'sScSScS':['sSvXSScSScS','sScSSvXSScS','sScSScSSvXS'],
                     'sScSScSScS':['sSvXSScSScSScS','sScSSvXSScSScS',
                                   'sScSScSSvXSScS','sScSScSScSSvXS'],
                     'ScSScS':['ScS^XScS'],
                     'ScSScSScS':['ScS^XScSScS','ScScS^XScS']}
    conv = phase_families[phase]
    conv_list = [i.replace('X',depth) for i in conv]
    return conv_list

def prepare_data_lookup(d,l,rkeys,phase):
    data = d[rkeys][phase][:]
    data *= 1./np.max(np.abs(data))
    data = np.roll(data,-1*np.argmax(np.abs(data)))
    time_3d = l[rkeys][phase]['1d_time'][0]
    lkup_dict = {}
    for keys in l[rkeys][phase]:
        if not keys[0].isdigit():
            tspace = l[rkeys][phase][keys]['1d_time'][:,0]
            dspace = l[rkeys][phase][keys]['depth'][:,0]
            tspace[1::] = np.abs(tspace[1::]-time_3d)
            f = interp1d(dspace,tspace)
            d_new = np.arange(dspace[0],dspace[-1]+5,5)
            t_new = f(d_new)
            lkup_dict[keys] = [d_new,t_new]
    return data,lkup_dict

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




