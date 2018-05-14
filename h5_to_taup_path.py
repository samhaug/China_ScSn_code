#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : h5_to_taup_path.py
Purpose : turn deconvolve.h5 into input station file for taup
Creation Date : 11-05-2018
Last Modified : Fri 11 May 2018 01:08:31 PM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from os import listdir
import h5py
import argparse

def main():
    parser = argparse.ArgumentParser(
                       description='make input file for taup_path')
    parser.add_argument('-f','--stream', metavar='H5_FILE',type=str,
                        help='deconvole.h5')
    args = parser.parse_args()
    f = h5py.File(args.stream,'r')
    taup = open('taup_input','w')
    for idx,keys in enumerate(f):
        c = f[keys]['coords'][:]
        if idx == 0:
            evla,evlo = c[4],c[5]
            stla,stlo = c[2],c[3]
            taup.write('e\n')
            taup.write('{} {}\n'.format(evla,evlo))
            taup.write('s\n')
            taup.write('{} {}\n'.format(stla,stlo))
        else:
            stla,stlo = c[2],c[3]
            taup.write('s\n')
            taup.write('{} {}\n'.format(stla,stlo))

    taup.write('q')

main()
