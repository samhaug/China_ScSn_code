#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : extract_reverb.py
Purpose : Clip reverb intervals from stream of traces
Creation Date : 04-01-2018
Last Modified : Sun 14 Jan 2018 04:49:33 PM EST
Created By : Samuel M. Haugland

==============================================================================
'''

from matplotlib import pyplot as plt
import numpy as np
import h5py
import obspy
from sys import argv
from obspy.taup import TauPyModel
model = TauPyModel('prem')
import argparse


def main():
    parser = argparse.ArgumentParser(description='Clip/write reverb intervals')
    parser.add_argument('-f','--fname', metavar='H5_FILE',type=str,
                        help='h5 data file')
    args = parser.parse_args()

    st = read_stream(args.fname)

    if 'T' in args.fname:
        h5f = h5py.File('reverb_T.h5','w')
    elif 'R' in args.fname:
        h5f = h5py.File('reverb_R.h5','w')
    for tr in st:
        name = tr.stats.network+tr.stats.station+tr.stats.location
        strip_reverb(tr,h5f)
    h5f.close()

def strip_reverb(tr,h5f):
    o = tr.stats.o
    p,dp = get_travel_times(tr)
    name = tr.stats.network+tr.stats.station+tr.stats.location
    h5f.create_group(name)
    h5f.create_dataset(name+'/coords',data=[tr.stats.gcarc,
                                            tr.stats.evdp,
                                            tr.stats.stla,
                                            tr.stats.stlo,
                                            tr.stats.evla,
                                            tr.stats.evlo])

    for ii in p:
        t = ii.time
        phase_name = ii.name
        if phase_name == 'ScSScS' and tr.stats.gcarc > 45:
            continue
        elif tr.stats.starttime+t+50 >= tr.stats.endtime:
            print(name+'   cutoff')
            continue
        else:
            b = tr.slice(tr.stats.starttime+t-500,tr.stats.starttime+t+50).data
            h5f.create_dataset(name+'/'+phase_name,data=b)

    for ii in dp:
        t = ii.time
        phase_name = ii.name
        if phase_name == 'sScS' and tr.stats.gcarc > 25:
            continue
        elif tr.stats.starttime+t+540 >= tr.stats.endtime:
            print(name+'   cutoff')
            continue
        else:
            b = tr.slice(tr.stats.starttime+t-10,tr.stats.starttime+t+540).data
            h5f.create_dataset(name+'/'+phase_name,data=b)

def read_stream(path_to_stream):
    st = obspy.read(path_to_stream)
    st.interpolate(10)
    st.filter('bandpass',freqmin=1./100,freqmax=1./10,zerophase=True)
    return st

def get_travel_times(tr):
    gcarc = tr.stats.gcarc
    h = tr.stats.evdp
    phase_list = ['ScSScS','ScSScSScS']
    depth_phase_list = ['sScS','sScSScS','sScSScSScS']
    p =  model.get_travel_times(h,gcarc,phase_list)
    dp = model.get_travel_times(h,gcarc,depth_phase_list)
    return p,dp


main()




