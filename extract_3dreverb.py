#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : extract_3dreverb.py
Purpose : Clip reverb intervals from stream of traces using 3d lookup table
Creation Date : 04-01-2018
Last Modified : Thu 01 Feb 2018 10:32:57 AM EST
Created By : Samuel M. Haugland

==============================================================================
'''

from matplotlib import pyplot as plt
import numpy as np
import h5py
import obspy
from sys import argv
from obspy.taup import TauPyModel
import argparse


def main():
    parser = argparse.ArgumentParser(description='Clip/write reverb intervals')
    parser.add_argument('-f','--fname', metavar='H5_FILE',type=str,
                        help='h5 data file')
    parser.add_argument('-l','--lkup3d', metavar='H5_FILE',type=str,
                        help='3d h5 lookup file')
    args = parser.parse_args()

    st = read_stream(args.fname)
    lkup = h5py.File(args.lkup3d,'r',driver='core')
    st.sort(['gcarc'])

    h5f_3d = h5py.File('reverb_3d.h5','w',driver='core')
    h5f_1d = h5py.File('reverb_1d.h5','w',driver='core')
    for tr in st:
        strip_reverb(tr,h5f_3d,h5f_1d,lkup)

    h5f_1d.close()
    h5f_3d.close()

def strip_reverb(tr,h5f_3d,h5f_1d,lkup):
    o = tr.stats.o
    name = tr.stats.network+tr.stats.station+tr.stats.location
    lkup_group = lkup[name]
    h5f_1d.create_group(name)
    h5f_3d.create_group(name)
    h5f_3d.create_dataset(name+'/coords',data=[tr.stats.gcarc,
                                            tr.stats.evdp,
                                            tr.stats.stla,
                                            tr.stats.stlo,
                                            tr.stats.evla,
                                            tr.stats.evlo])
    h5f_1d.create_dataset(name+'/coords',data=[tr.stats.gcarc,
                                            tr.stats.evdp,
                                            tr.stats.stla,
                                            tr.stats.stlo,
                                            tr.stats.evla,
                                            tr.stats.evlo])

    for phase in lkup_group:
        t_3d =  lkup_group[phase]['3d'][0]
        t_1d =  lkup_group[phase]['prem'][0]

        if phase.startswith('S'):
            if phase == 'ScSScS' and tr.stats.gcarc > 55:
                continue
            elif tr.stats.starttime+t_1d+50 >= tr.stats.endtime:
                print(name+'   cutoff')
                continue
            elif tr.stats.starttime+t_3d+50 >= tr.stats.endtime:
                print(name+'   cutoff')
                continue
            else:
                d_3d = tr.slice(tr.stats.starttime+t_3d-500,
                                tr.stats.starttime+t_3d+50).data
                d_1d = tr.slice(tr.stats.starttime+t_1d-500,
                                tr.stats.starttime+t_1d+50).data
                h5f_3d.create_dataset(name+'/'+phase,data=d_3d)
                h5f_1d.create_dataset(name+'/'+phase,data=d_1d)

        elif phase.startswith('s'):

            if phase == 'sScS' and tr.stats.gcarc > 35:
                continue
            elif tr.stats.starttime+t_1d+540 >= tr.stats.endtime:
                print(name+'   cutoff')
                continue
            elif tr.stats.starttime+t_3d+540 >= tr.stats.endtime:
                print(name+'   cutoff')
                continue
            else:
                d_3d = tr.slice(tr.stats.starttime+t_3d-10,
                                tr.stats.starttime+t_3d+540).data
                d_1d = tr.slice(tr.stats.starttime+t_1d-10,
                                tr.stats.starttime+t_1d+540).data
                h5f_3d.create_dataset(name+'/'+phase,data=d_3d)
                h5f_1d.create_dataset(name+'/'+phase,data=d_1d)

def read_stream(path_to_stream):
    st = obspy.read(path_to_stream)
    #st.interpolate(10)
    #st.filter('bandpass',freqmin=1./100,freqmax=1./10,zerophase=True)
    return st



main()




