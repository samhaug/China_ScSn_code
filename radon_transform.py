#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : radon_transform.py
Purpose : apply radon transform to trace.
Creation Date : 19-03-2018
Last Modified : Tue 20 Mar 2018 10:33:20 AM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
import h5py
import obspy
import argparse
import seispy
import Radon

def main():
    parser = argparse.ArgumentParser(description='Radon transform')
    parser.add_argument('-f','--stream', metavar='H5_FILE',type=str,
                        help='h5 stream')
    parser.add_argument('--save', metavar='bool',type=str,
                        help='save vespagram',default=False)
    parser.add_argument('--read', metavar='bool',type=str,
                        help='read vespagram',default=False)
    args = parser.parse_args()
    st = obspy.read(args.stream)
    st = block_stream(st)
    t,delta,M,p,weights,ref_dist = prepare_input(st)

    if args.read != False:
        R = np.genfromtxt(args.read)
    else:
        R = Radon.Radon_inverse(t,delta,M,p,weights,
                                ref_dist,'Linear','L2',[5e2])
        if args.save == True:
            np.savetxt('Radon.dat',R)

    plt.imshow(np.log10(np.abs(R)),aspect='auto')
    plt.show()

    d = Radon.Radon_forward(t,p,R,delta,ref_dist,'Linear')
    stc = st.copy()
    for idx,tr in enumerate(stc):
        stc[idx].data = d[idx]
    #seispy.plot.simple_h5_section(stc)
    stc.write('st_T_radon.h5',format='H5')

def prepare_input(st):
    p = np.arange(-8.0,8.1,0.1)
    delta = []
    M = []
    for tr in st:
        delta.append(tr.stats.gcarc)
        M.append(tr.data)
    M = np.array(M)
    delta = np.array(delta)
    weights = np.ones(len(delta))
    ref_dist = np.mean(delta)
    t = np.linspace(0,4000,num=st[0].stats.npts)
    return t,delta,M,p,weights,ref_dist

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
        st[idx].data = tr.data[0:40000]
    return st

main()



