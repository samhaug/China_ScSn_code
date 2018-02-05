#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : moveout_correction.py
Purpose : Apply moveout correction to deconvolved data using lookup table.
          lookup table made make_lookup.py
Creation Date : 15-01-2018
Last Modified : Mon 05 Feb 2018 11:05:21 AM EST
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

    mvout = h5py.File('3dmvt_correct.h5','w',driver='core')
    d = h5py.File(args.deconvolve,'r',driver='core')
    l = h5py.File(args.lkup_table,'r',driver='core')

    for dkeys in d:
        gcarc = round(d[dkeys]['coords'][0])
        mvout.create_dataset(dkeys+'/coords',data=d[dkeys]['coords'][...])
        try:
            for lkeys in d[dkeys]:
                if not lkeys.startswith('c'):
                    print dkeys,lkeys
                    mapping_lkup = l[dkeys][lkeys]
                    for ckeys in mapping_lkup:
                        if ckeys.startswith('S') or ckeys.startswith('s'):
                            d_map = mapping_lkup[ckeys]['depth']
                            t_map = mapping_lkup[ckeys]['3d_time']
                            data = d[dkeys][lkeys][:]
                            data = np.roll(data,-1*np.argmax(np.abs(data)))

                            f = interp1d(mapping[1,0:len(data)],data)
                            abs_depth = np.linspace(mapping[1,0],
                                        mapping[1,0:len(data)].max(),
                                        num=int(2*mapping[1,len(data)]))
                            mv_data = f(abs_depth)
                            mv_data *= 1./np.abs(mv_data).max()
                            mvout.create_dataset(dkeys+'/'+lkeys,
                                        data=np.vstack((abs_depth,mv_data)))
        except KeyError:
            continue
    mvout.close()
    d.close()
    l.close()

main()





