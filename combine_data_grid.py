#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : combine_grid.py
Purpose : combine grids from multiple events
Creation Date : 15-02-2018
Last Modified : Fri 11 May 2018 03:21:33 PM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from subprocess import call
from matplotlib import pyplot as plt
from os import listdir
from os.path import exists
import h5py
import obspy
import argparse
from glob import glob


def main():
    parser = argparse.ArgumentParser(description='sum gridfiles')
    #parser.add_argument('-d','--dir_list', metavar='string',type=str,
    #                   help='comma delimited list of direcories')
    parser.add_argument('-f','--files', metavar='string',type=str,
                       help='glob compatable path to files')
    args = parser.parse_args()
    #dir_list = args.dir_list.split(',')
    dir_list = glob(args.files)
    print dir_list
    data_grid_list = []
    data_grid_list_2 = []
    data_gridc_list = []
    data_gridc_list_2 = []
    for dirname in dir_list:
        if not exists(dirname+'/'+'data_grid.h5'):
            continue
        try:
            dg,dgc,dg2,dgc2,h,lat,lon = return_grid(dirname)
        except KeyError:
            continue
        dg*=1./dgc
        dg2*=1./dgc2
        data_grid_list.append(dg)
        data_grid_list_2.append(dg2)
        data_gridc_list.append(dgc)
        data_gridc_list_2.append(dgc2)

    d = np.zeros(data_grid_list[0].shape)
    for ii in data_grid_list:
        d += ii
    d *= 1./len(data_grid_list)

    dc = np.zeros(data_gridc_list[0].shape)
    for ii in data_gridc_list:
        dc += ii

    d2 = np.zeros(data_grid_list_2[0].shape)
    for ii in data_grid_list_2:
        d2 += ii
    d2 *= 1./len(data_grid_list_2)

    dc2 = np.zeros(data_gridc_list_2[0].shape)
    for ii in data_gridc_list_2:
        dc2 += ii


    #syn2 = h5py.File('synth_grid_sum_ScS2.h5','w')
    dat = h5py.File('data_grid_sum.h5','w')
    #dat2 = h5py.File('data_grid_sum_ScS2.h5','w')

    dat.create_dataset('grid',data=d)
    dat.create_dataset('grid_ScS2',data=d2)

    dat.create_dataset('grid_count',data=dc)
    dat.create_dataset('grid_count_ScS2',data=dc2)

    dat.create_dataset('h',data=h)
    dat.create_dataset('lat',data=lat)
    dat.create_dataset('lon',data=lon)

    dat.close()

def return_grid(dirname):
    d = h5py.File('./'+dirname+'/data_grid.h5','r',driver='core')


    dg = d['grid'][:]
    dg2 = d['grid_ScS2'][:]


    dgc = d['grid_count'][:]+1
    dgc2 = d['grid_count_ScS2'][:]+1

    h = d['h'][:]
    lat = d['lat'][:]
    lon = d['lon'][:]
    d.close()
    return dg,dgc,dg2,dgc2,h,lat,lon

main()


