#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : extract_data_reverb.py
Purpose : Clip reverb intervals from stream of traces using synth cross_corr
Creation Date : 04-01-2018
Last Modified : Thu 01 Feb 2018 12:10:22 PM EST
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
model = TauPyModel(model='prem')


def main():
    parser = argparse.ArgumentParser(description='Clip/write reverb intervals')
    parser.add_argument('-s','--synth', metavar='H5_FILE',type=str,
                        help='h5 synth file')
    parser.add_argument('-d','--data', metavar='H5_FILE',type=str,
                        help='h5 data file')
    args = parser.parse_args()

    sts = obspy.read(args.synth)
    std = obspy.read(args.data)
    sts,std = remove_excess(sts,std)
    for idx,tr in enumerate(sts):
        corr_reverb(sts[idx],std[idx],'ScSScS')

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
    ts = round((len(d)/2.-argmax(correl))/samp,2)
    return ts

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

    return st

def corr_reverb(trs,trd,phase):
    so = trs.stats.o
    do = trd.stats.o
    sname = trs.stats.network+trs.stats.station+trs.stats.location
    dname = trd.stats.network+trd.stats.station+trd.stats.location
    print(phase,sname)
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
            s_dat = trs.slice(trs.stats.starttime+time-500,
                             trs.stats.starttime+time+50).data
            s_dat *= 1./np.abs(s_dat.max())
            d_dat = trd.slice(trd.stats.starttime+time-500,
                             trd.stats.starttime+time+50).data
            d_dat *= 1./np.abs(d_dat.max())
            plt.plot(s_dat)
            plt.plot(d_dat)
            plt.show()

    elif phase.startswith('s'):

	if phase == 'sScS' and tr.stats.gcarc > 35:
            return False
	elif tr.stats.starttime+t_1d+540 >= tr.stats.endtime:
            print(name+'   cutoff')
            return False
	elif tr.stats.starttime+t_3d+540 >= tr.stats.endtime:
            print(name+'   cutoff')
            return False
	else:
            s_dat = trs.slice(trs.stats.starttime+time-10,
                             trs.stats.starttime+time+540).data
            s_dat *= 1./np.abs(s_dat.max())
            d_dat = trd.slice(trd.stats.starttime+time-10,
                             trd.stats.starttime+time+540).data
            d_dat *= 1./np.abs(d_dat.max())
            plt.plot(s_dat)
            plt.plot(d_dat)
            plt.show()

main()




