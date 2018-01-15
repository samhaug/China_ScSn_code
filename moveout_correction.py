#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : moveout_correction.py
Purpose : Apply moveout correction to deconvolved data using lookup table.
          lookup table made make_lookup.py
Creation Date : 15-01-2018
Last Modified : Mon 15 Jan 2018 02:34:28 PM EST
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
from subprocess import call
from os import listdir
import h5py
import argparse

def main():
    parser = argparse.ArgumentParser(description='Clip/write reverb intervals')
    parser.add_argument('-l','--lkup_table', metavar='H5_FILE',type=str,
                        help='h5 lookup table')
    parser.add_argument('-d','--deconvolve', metavar='H5_FILE',type=str,
                        help='h5 file of deconvolved reverberations')
    args = parser.parse_args()
    d = h5py.File(args.deconvolve,'r')
    l = h5py.File(args.lkup_table,'r')
    for keys in d:
        gcarc = round(d[keys]['coords'][0])
        map = l[str(gcarc)][...]

main()
