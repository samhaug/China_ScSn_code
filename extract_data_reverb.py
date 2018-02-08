#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : extract_data_reverb.py
Purpose : Clip reverb intervals from stream of traces using synth cross_corr
Creation Date : 04-01-2018
Last Modified : Thu 08 Feb 2018 01:18:07 PM EST
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
#import seispy
from subprocess import call
from scipy.signal import correlate
model = TauPyModel(model='prem')


def main():
    parser = argparse.ArgumentParser(description='Clip/write reverb intervals')
    parser.add_argument('-s','--synth', metavar='H5_FILE',type=str,
                        help='h5 obspy stream synth file')
    parser.add_argument('-d','--data', metavar='H5_FILE',type=str,
                        help='h5 obspy stream data file')
    args = parser.parse_args()
    try:
        h5f_d = h5py.File('data_reverb.h5','w',driver='core')
    except IOError:
        call('rm data_reverb.h5',shell=True)
        h5f_d = h5py.File('data_reverb.h5','w',driver='core')
    try:
        h5f_s = h5py.File('synth_reverb.h5','w',driver='core')
    except IOError:
        call('rm synth_reverb.h5',shell=True)
        h5f_s = h5py.File('synth_reverb.h5','w',driver='core')

    sts = obspy.read(args.synth)
    std = obspy.read(args.data)
    sts,std = remove_excess(sts,std)

    phase_list =['sScS','ScSScS','sScSScS','ScSScSScS','sScSScSScS']

    for idx,tr in enumerate(sts):
        #print tr.stats.gcarc,tr.stats.evdp,std[idx].stats.o
        name = tr.stats.network+tr.stats.station+tr.stats.location
        for phase in phase_list:
            dat = corr_reverb(sts[idx],std[idx],phase)
            if type(dat) != bool:
                try:
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
                except ValueError:
                    continue
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
    std.filter('bandpass',freqmin=1./100,freqmax=1./10,zerophase=True)
    #seispy.plot.simple_h5_section(sts)
    #seispy.plot.simple_h5_section(std)

    return sts,std

def npcorr(s,d,samp):
    correl = correlate(s,d,mode='same')
    ts = round((len(d)/2.-np.argmax(correl))/samp,2)
    return ts

def corr_reverb(trs_in,trd_in,phase,cutoff=0.5):
    trs = trs_in.copy()
    trd = trd_in.copy()
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
    ts = np.linspace(-so,float(trs.stats.npts)/trs.stats.sampling_rate,
                     num=trs.stats.npts)
    td = np.linspace(-do,float(trd.stats.npts)/trd.stats.sampling_rate,
                     num=trd.stats.npts)
    #plt.plot(ts,trs.data/trs.data.max())
    #plt.plot(td,trd.data/trd.data.max())
    #plt.show()

    if phase.startswith('S'):
	#if phase == 'ScSScS' and trs.stats.gcarc > 55:
        #    print('out of range')
        #    return False
	if trs.stats.starttime+time+50+so >= trs.stats.endtime:
            print(name+'   cutoff')
            return False
	elif trd.stats.starttime+time+50+do >= trd.stats.endtime:
            print(name+'   cutoff')
            return False
	else:
            try:
                s_dat = trs.slice(trs.stats.starttime+time-500+so,
                                 trs.stats.starttime+time+50+so).data
                s_dat *= 1./np.abs(s_dat).max()
                trd_mv = trd.copy()
                d_dat = trd.slice(trd.stats.starttime+time-500+do,
                                 trd.stats.starttime+time+50+do).data
                d_dat *= 1./np.abs(d_dat).max()
                ts = npcorr(s_dat,d_dat,trs.stats.sampling_rate)
                if np.abs(ts) >= 15:
                    print 'alignment error ',ts
                    return False
                #adjust window
                d_dat = trd_mv.slice(trd.stats.starttime+time-500+ts+do,
                                 trd.stats.starttime+time+50+ts+do).data
                d_dat *= 1./np.abs(d_dat).max()
            except RuntimeError:
                return False
            if np.max(np.abs(d_dat[0:4000])) > cutoff \
                    or np.isnan(np.sum(d_dat)):
                return False
            else:
                return d_dat,s_dat

    elif phase.startswith('s'):
	#if phase == 'sScS' and trs.stats.gcarc > 35:
        #    print('out of range')
        #    return False
	if trs.stats.starttime+time+540 >= trs.stats.endtime:
            print(name+'   cutoff')
            return False
	elif trd.stats.starttime+time+540 >= trd.stats.endtime:
            print(name+'   cutoff')
            return False
	else:
            try:
                s_dat = trs.slice(trs.stats.starttime+time-10+so,
                                 trs.stats.starttime+time+540+so).data
                s_dat *= 1./np.abs(s_dat).max()
                trd_mv = trd.copy()
                d_dat = trd.slice(trd.stats.starttime+time-10+do,
                                 trd.stats.starttime+time+540+do).data
                d_dat *= 1./np.abs(d_dat).max()
                ts = npcorr(s_dat,d_dat,trs.stats.sampling_rate)
                if np.abs(ts) >= 15:
                    print 'alignment error ',ts
                    return False
                #adjust window
                d_dat = trd_mv.slice(trd.stats.starttime+time-10+ts+do,
                                 trd.stats.starttime+time+540+ts+do).data
                d_dat *= 1./np.abs(d_dat).max()
            except RuntimeError:
                return False
            if np.max(np.abs(d_dat[1000::])) > cutoff \
                    or np.isnan(np.sum(d_dat)):
                return False
            else:
                return d_dat,s_dat

main()




