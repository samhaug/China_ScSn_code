#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : combine_grid.py
Purpose : combine grids from multiple events
Creation Date : 15-02-2018
Last Modified : Thu 15 Feb 2018 07:01:44 PM EST
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from subprocess import call
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
        sg,dg,sgc,dgc=return_grid(dirname)
        sg*=1./sgc
        dg*=1./dgc
        synth_grid_list.append(sg)
        data_grid_list.append(dg)
        synth_gridc_list.append(sgc)
        data_gridc_list.append(dgc)
    s = np.zeros(synth_grid_list[0].shape)
    for ii in synth_grid_list:
        s += ii
    d = np.zeros(synth_grid_list[0].shape)
    for ii in data_grid_list:
        d += ii
    f = h5py.File('grid_sum.h5','w')
    f.create_dataset('sgrid',data=s)
    f.create_dataset('dgrid',data=d)
    #f.create_dataset('sgridc',data=sgridc_sum)
    #f.create_dataset('dgridc',data=dgridc_sum)
    f.close()

def return_grid(dirname):
    s = h5py.File('./'+dirname+'/synth_grid.h5','r',driver='core')
    d = h5py.File('./'+dirname+'/data_grid.h5','r',driver='core')
    sg = s['grid'][:]
    dg = d['grid'][:]
    sgc = s['grid_count'][:]+1
    dgc = d['grid_count'][:]+1
    return sg,dg,sgc,dgc

main()


