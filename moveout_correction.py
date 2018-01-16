#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : moveout_correction.py
Purpose : Apply moveout correction to deconvolved data using lookup table.
          lookup table made make_lookup.py
Creation Date : 15-01-2018
Last Modified : Tue 16 Jan 2018 11:32:56 AM EST
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
from subprocess import call
from os import listdir
import h5py
import argparse
from scipy.interpolate import interp1d

def main():
    parser = argparse.ArgumentParser(description='Clip/write reverb intervals')
    parser.add_argument('-l','--lkup_table', metavar='H5_FILE',type=str,
                        help='h5 lookup table')
    parser.add_argument('-d','--deconvolve', metavar='H5_FILE',type=str,
                        help='h5 file of deconvolved reverberations')
    args = parser.parse_args()

    mvout = h5py.File('mvout_corrected.h5','w')
    d = h5py.File(args.deconvolve,'r')
    l = h5py.File(args.lkup_table,'r')

    for keys in d:
        mvout.create_group(keys)
        gcarc = round(d[keys]['coords'][0])
        mvout.create_dataset(keys+'/coords',data=d[keys]['coords'][...])
        mapping = l[str(gcarc)][...]
        data = d[keys]['sScSScS'][...]
        data = np.roll(data,-1*np.argmax(np.abs(data)))

        f = interp1d(mapping[1,0:len(data)],data)
        abs_depth = np.linspace(mapping[1,0],
                                mapping[1,0:len(data)].max(),
                                num=int(2*mapping[1,len(data)]))
        mv_data = f(abs_depth)

        mvout.create_dataset(keys+'/sScSScS',data=np.vstack((abs_depth,mv_data)))
    mvout.close()
    d.close()
    l.close()

main()





