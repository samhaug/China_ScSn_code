#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : make_lookup.py
Purpose : Make h5 lookup table of reverberation traveltimes
Creation Date : 20-12-2017
Last Modified : Wed 17 Jan 2018 02:02:39 PM EST
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
from obspy.taup import TauPyModel
from subprocess import call
import h5py
from scipy.interpolate import interp1d
import re
mod = TauPyModel(model='prem50')

def main():
    h5f = h5py.File('mvt_lkup.h5','w')
    evdp = 598.2
    phase_lists = [['sScSScS','sSvXSScSScS'],
                  ['sScSScSScS','sSvXSScSScSScS'],
                  ['ScSScS','ScS^XScS'],
                  ['ScSScSScS','ScS^XScSScS']]

    make_lookup(phase_lists,h5f,evdp)
    h5f.close()

def make_lookup(phase_lists,h5f,evdp):
    cdp = np.arange(50,1800,100)
    for phase_list in phase_lists:

        print 'Computing '+phase_list[0]

        master_time = []
        master_depth = []

        if phase_list[0][0].startswith('s'):
            print('s')
            for ii in cdp:
                time_list,depth_list,gcarc_list = top_depth_times(evdp,
                                                         ii,phase_list)
                master_time.append(time_list)
                master_depth.append(depth_list)
        elif phase_list[0][0].startswith('S'):
            print('S')
            for ii in cdp:
                time_list,depth_list,gcarc_list = bot_depth_times(evdp,
                                                         ii,phase_list)
                master_time.append(time_list)
                master_depth.append(depth_list)

        master_time = np.array(master_time)
        master_time = np.vstack((np.zeros(master_time.shape[1]),master_time))
        master_depth = np.array(master_depth)
        master_depth = np.vstack((np.zeros(master_depth.shape[1]),master_depth))

        for idx,ii in enumerate(gcarc_list):
            f = interp1d(master_time[:,idx],master_depth[:,idx])
            tnew = np.arange(master_time[0,idx],master_time[-1,idx],0.1)
            dnew = f(tnew)
            h5f.create_dataset(phase_list[0]+'/'+str(ii),
                               data=np.vstack((tnew,dnew)))

def top_depth_times(evdp,cdp,phase_list_in):
    phase_list = phase_list_in[:]
    phase_list[1] = phase_list[1].replace('X',str(cdp))
    time_list = []
    depth_list = []
    gcarc_list = np.linspace(0,90,num=91)

    for ii in gcarc_list:
        arr = mod.get_travel_times(source_depth_in_km=evdp,
                                   distance_in_degree=ii,
                                   phase_list=phase_list)
        pure_depth = float(re.findall('\d+',arr[1].purist_name)[0])
        time = arr[1].time-arr[0].time
        time_list.append(time)
        depth_list.append(pure_depth)

    return time_list,depth_list,gcarc_list

def bot_depth_times(evdp,cdp,phase_list_in):
    phase_list = phase_list_in[:]
    phase_list[1] = phase_list[1].replace('X',str(cdp))
    time_list = []
    depth_list = []
    gcarc_list = np.linspace(0,90,num=91)

    for ii in gcarc_list:
        arr = mod.get_travel_times(source_depth_in_km=evdp,
                                   distance_in_degree=ii,
                                   phase_list=phase_list)
        pure_depth = float(re.findall('\d+',arr[0].purist_name)[0])
        time = arr[1].time-arr[0].time
        time_list.append(time)
        depth_list.append(pure_depth)

    return time_list,depth_list,gcarc_list

main()


