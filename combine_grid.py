#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : combine_grid.py
Purpose : combine grids from multiple events
Creation Date : 15-02-2018
Last Modified : Sun 18 Feb 2018 02:56:11 PM EST
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from subprocess import call
from matplotlib import pyplot as plt
from os import listdir
import h5py
import obspy
import argparse

def main():
    parser = argparse.ArgumentParser(description='sum gridfiles')
    parser.add_argument('-d','--dir_list', metavar='string',type=str,
                       help='comma delimited list of direcories')
    args = parser.parse_args()
    dir_list = args.dir_list.split(',')
    synth_grid_list = []
    data_grid_list = []
    data_gridc_list = []
    synth_gridc_list = []
    for dirname in dir_list:
        print dirname
        sg,dg,sgc,dgc,h,lat,lon=return_grid(dirname)
        plt.imshow(np.mean(dg/dgc,axis=0),
                   aspect='auto',extent=[50,800,0,1])
        plt.show()
        plt.imshow(np.mean(dg/dgc,axis=1),
                   aspect='auto',extent=[50,800,0,1])
        plt.show()
        sg*=1./sgc
        dg*=1./dgc
        synth_grid_list.append(sg)
        data_grid_list.append(dg)
        synth_gridc_list.append(sgc)
        data_gridc_list.append(dgc)

    s = np.zeros(synth_grid_list[0].shape)
    for ii in synth_grid_list:
        s += ii
    s *= 1./len(synth_grid_list)

    sc = np.zeros(synth_gridc_list[0].shape)
    for ii in synth_gridc_list:
        sc += ii

    d = np.zeros(data_grid_list[0].shape)
    for ii in data_grid_list:
        d += ii
    d *= 1./len(data_grid_list)

    dc = np.zeros(data_gridc_list[0].shape)
    for ii in data_gridc_list:
        dc += ii

    syn = h5py.File('synth_grid_sum.h5','w')
    dat = h5py.File('data_grid_sum.h5','w')

    syn.create_dataset('grid',data=s)
    dat.create_dataset('grid',data=d)

    dat.create_dataset('grid_count',data=sc)
    syn.create_dataset('grid_count',data=dc)

    dat.create_dataset('h',data=h)
    dat.create_dataset('lat',data=lat)
    dat.create_dataset('lon',data=lon)

    syn.create_dataset('h',data=h)
    syn.create_dataset('lat',data=lat)
    syn.create_dataset('lon',data=lon)
    syn.close()
    dat.close()

def return_grid(dirname):
    s = h5py.File('./'+dirname+'/synth_grid.h5','r',driver='core')
    d = h5py.File('./'+dirname+'/data_grid.h5','r',driver='core')
    sg = s['grid'][:]
    dg = d['grid'][:]
    sgc = s['grid_count'][:]+1
    dgc = d['grid_count'][:]+1
    h = s['h'][:]
    lat = s['lat'][:]
    lon = s['lon'][:]
    return sg,dg,sgc,dgc,h,lat,lon

main()


