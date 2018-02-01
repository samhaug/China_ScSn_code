#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : extract_data_reverb.py
Purpose : Clip reverb intervals from stream of traces using synth cross_corr
Creation Date : 04-01-2018
Last Modified : Thu 01 Feb 2018 03:02:54 PM EST
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
from scipy.signal import correlate
model = TauPyModel(model='prem')


def main():
    parser = argparse.ArgumentParser(description='Clip/write reverb intervals')
    parser.add_argument('-s','--synth', metavar='H5_FILE',type=str,
                        help='h5 synth file')
    parser.add_argument('-d','--data', metavar='H5_FILE',type=str,
                        help='h5 data file')
    args = parser.parse_args()
    h5f_d = h5py.File('data_reverb.h5','w',driver='core')
    h5f_s = h5py.File('synth_reverb.h5','w',driver='core')

    sts = obspy.read(args.synth)
    std = obspy.read(args.data)
    sts,std = remove_excess(sts,std)

    phase_list =['sScS','ScSScS','sScSScS','ScSScSScS','sScSScSScS']

    for idx,tr in enumerate(sts):
        name = tr.stats.network+tr.stats.station+tr.stats.location
        h5f_d.create_group(name)
        h5f_d.create_dataset(name+'/coords',data=[tr.stats.gcarc,
                                               tr.stats.evdp,
                                               tr.stats.stla,
                                               tr.stats.stlo,
                                               tr.stats.evla,
                                               tr.stats.evlo])
        h5f_s.create_group(name)
        h5f_s.create_dataset(name+'/coords',data=[tr.stats.gcarc,
                                               tr.stats.evdp,
                                               tr.stats.stla,
                                               tr.stats.stlo,
                                               tr.stats.evla,
                                               tr.stats.evlo])
        for phase in phase_list:
            dat = corr_reverb(sts[idx],std[idx],phase)
            if type(dat) != bool:
                h5f_s.create_dataset(name+'/'+phase,data=dat[1])
                h5f_d.create_dataset(name+'/'+phase,data=dat[0])
    h5f_d.close()
    h5f_s.close()

def remove_excess(sts,std):
    sts_name = []
    std_name = []

    for tr in sts:
        sts_name.append(tr.stats.network+tr.stats.station+tr.stats.location)
    for tr in std:
        std_name.append(tr.stats.network+tr.stats.station+tr.stats.location)
    inter = set(sts_name).intersection(set(std_name))

    for tr in sts:
        if tr.stats.network+tr.stats.station+tr.stats.location not in inter:
            sts.remove(tr)
    for tr in std:
        if tr.stats.network+tr.stats.station+tr.stats.location not in inter:
            std.remove(tr)

    sts.interpolate(10)
    std.interpolate(10)
    sts.filter('bandpass',freqmin=1./100,freqmax=1./10,zerophase=True)
    sts.sort(['gcarc'])
    std.sort(['gcarc'])

    return sts,std

def npcorr(s,d,samp):
    correl = correlate(s,d,mode='same')
    ts = round((len(d)/2.-np.argmax(correl))/samp,2)
    return ts

def corr_reverb(trs,trd,phase,cutoff=0.5):
    so = trs.stats.o
    do = trd.stats.o
    sname = trs.stats.network+trs.stats.station+trs.stats.location
    dname = trd.stats.network+trd.stats.station+trd.stats.location
    if not sname == dname:
        print('mismatch')
        return False

    time = model.get_travel_times(source_depth_in_km=trd.stats.evdp,
                                  distance_in_degree=trd.stats.gcarc,
                                  phase_list=[phase])[0].time

    if phase.startswith('S'):

	if phase == 'ScSScS' and trs.stats.gcarc > 55:
            return False
	elif trs.stats.starttime+time+50 >= trs.stats.endtime:
            print(name+'   cutoff')
            return False
	elif trd.stats.starttime+time+50 >= trd.stats.endtime:
            print(name+'   cutoff')
            return False
	else:
            try:
                s_dat = trs.slice(trs.stats.starttime+time-500,
                                 trs.stats.starttime+time+50).data
                s_dat *= 1./np.abs(s_dat).max()
                d_dat = trd.slice(trd.stats.starttime+time-500,
                                 trd.stats.starttime+time+50).data
                d_dat *= 1./np.abs(d_dat).max()
                ts = npcorr(s_dat,d_dat,trs.stats.sampling_rate)
                #adjust window
                d_dat = trd.slice(trd.stats.starttime+time-500+ts,
                                 trd.stats.starttime+time+50+ts).data
                d_dat *= 1./np.abs(d_dat).max()
            except RuntimeError:
                return False
            if np.max(np.abs(d_dat[0:4000])) > cutoff \
                    or np.isnan(np.sum(d_dat)):
                return False
            else:
                return d_dat,s_dat

    elif phase.startswith('s'):

	if phase == 'sScS' and trs.stats.gcarc > 35:
            return False
	elif trs.stats.starttime+time+540 >= trs.stats.endtime:
            print(name+'   cutoff')
            return False
	elif trd.stats.starttime+time+540 >= trd.stats.endtime:
            print(name+'   cutoff')
            return False
	else:
            try:
                s_dat = trs.slice(trs.stats.starttime+time-10,
                                 trs.stats.starttime+time+540).data
                s_dat *= 1./np.abs(s_dat).max()
                d_dat = trd.slice(trd.stats.starttime+time-10,
                                 trd.stats.starttime+time+540).data
                d_dat *= 1./np.abs(d_dat).max()
                ts = npcorr(s_dat,d_dat,trs.stats.sampling_rate)
                #adjust window
                d_dat = trd.slice(trd.stats.starttime+time-10+ts,
                                 trd.stats.starttime+time+540+ts).data
                d_dat *= 1./np.abs(d_dat).max()
            except RuntimeError:
                return False
            if np.max(np.abs(d_dat[1000::])) > cutoff \
                    or np.isnan(np.sum(d_dat)):
                return False
            else:
                return d_dat,s_dat

main()




