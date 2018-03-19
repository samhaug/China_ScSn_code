#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : radon_transform.py
Purpose : apply radon transform to trace.
Creation Date : 19-03-2018
Last Modified : Mon 19 Mar 2018 04:07:18 PM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
import h5py
import obspy
import argparse
import seispy

def main():
    parser = argparse.ArgumentParser(description='Radon transform')
    parser.add_argument('-f','--stream', metavar='H5_FILE',type=str,
                        help='h5 stream')
    args = parser.parse_args()
    st = obspy.read(args.stream)
    st = block_stream(st)
    seispy.plot.simple_h5_section(st)

def block_stream(st):
    for idx,tr in enumerate(st):
        if tr.stats.o <= 0:
            z = np.zeros(int(np.abs(tr.stats.o)*10))
            st[idx].data = np.hstack((z,tr.data))
        elif tr.stats.o > 0:
            d = tr.data[int(tr.stats.o*10)::]
            st[idx].data = d
        st[idx].stats.starttime += st[idx].stats.o
        l = tr.stats.endtime-tr.stats.starttime
        if l <= 4000:
            z = np.zeros(int(10*(4000-l)))
            st[idx].data = np.hstack((tr.data,z))
        elif l > 4000:
            st[idx].data = tr.data[0:40000]
    return st


main()
