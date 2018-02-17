#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : moveout_correction.py
Purpose : Apply moveout correction to deconvolved data using lookup table.
          lookup table made make_lookup.py
Creation Date : 15-01-2018
Last Modified : Mon 05 Feb 2018 01:09:16 PM EST
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
        mvout.create_group(dkeys)
        mvout[dkeys].create_dataset('coords',data=d[dkeys]['coords'][...])
        try:
            for lkeys in d[dkeys]:
                #go through parents
                if not lkeys.startswith('c'):
                    mvout[dkeys].create_dataset
                    print dkeys,lkeys
                    mapping_lkup = l[dkeys][lkeys]
                    t_3d = mapping_lkup[ckeys]['3d_time'][0]
                    #t_1d = mapping_lkup[ckeys]['1d_time'][0]
                    for ckeys in mapping_lkup:
                        if ckeys.startswith('S') or ckeys.startswith('s'):
                            d_map = mapping_lkup[ckeys]['depth'][:,0]
                            t3d_map = mapping_lkup[ckeys]['3d_time'][:,0]
                            t3d_map[1::] = np.abs(t3d_map[1::]-t_3d)
                            t3d_map = np.round(t3d_map,1)
                            #t1d_map = mapping_lkup[ckeys]['1d_time'][:,0]
                            #t1d_map[1::] = np.abs(t1d_map[1::]-t_1d)
                            data = d[dkeys][lkeys][:]
                            #make parent at zero time
                            data = np.roll(data,-1*np.argmax(np.abs(data)))

                            f = interp1d(d_map,t3d_map)
                            d_new = np.arange(d_map[0],d_map[-1]+5,5)
                            t_new = f(d_new)

                            mvout.create_dataset(dkeys+'/'+lkeys,
                                        data=np.vstack((abs_depth,mv_data)))
        except KeyError:
            continue
    mvout.close()
    d.close()
    l.close()

main()





