#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : reverb_time_table.py
Purpose : Make lookup table of reverberation traveltimes
Creation Date : 20-12-2017
Last Modified : Sun 14 Jan 2018 06:00:40 PM EST
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
from obspy.taup import TauPyModel
from subprocess import call
mod = TauPyModel(model='prem50')

def main():
    conv = np.arange(50,950,50)
    master_time = []
    master_depth = []
    for ii in conv:
        time_list,depth_list = top_depth_times(100,ii)
        master_time.append(time_list)
        master_depth.append(depth_list)
    np.savetxt('time_table.txt',np.array(master_time).T,fmt='%5.2f')
    np.savetxt('depth_table.txt',np.array(master_depth).T,fmt='%5.2f')

def top_depth_times(depth,conv):
    conv = str(conv)
    time_list = []
    depth_list = []
    for ii in np.linspace(0,80,num=60):
        arr = mod.get_travel_times(source_depth_in_km=depth,
                                   distance_in_degree=ii,
                                   phase_list=['sScS','sSv'+conv+'SScS'])
        pure_depth = float(arr[-1].purist_name[3:-4])
        time = arr[1].time-arr[0].time
        time_list.append(time)
        depth_list.append(pure_depth)
    return time_list,depth_list

def bot_depth_times(depth,conv):
    conv = str(conv)
    time_list = []
    for ii in np.linspace(0,80,num=160):
        arr = mod.get_travel_times(source_depth_in_km=depth,
                                   distance_in_degree=ii,
                                   phase_list=['ScSScS','ScS^'+conv+'ScS'])
        time = arr[1].time-arr[0].time
        time_list.append(time)



main()
