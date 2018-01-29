#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : make_3dlookup.py
Purpose : Make h5 lookup table of reverberation traveltimes for 3d model
Creation Date : 20-12-2017
Last Modified : Mon 29 Jan 2018 06:37:48 PM EST
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
from obspy.taup import TauPyModel
from subprocess import call
import h5py
from scipy.interpolate import interp1d
from scipy.interpolate import RegularGridInterpolator
import re
import obspy
import argparse
import obspy
#mod = TauPyModel(model='prem50')

def main():
    parser = argparse.ArgumentParser(
                       description='make lookup table for event in 3d model')
    parser.add_argument('-f','--fname', metavar='H5_FILE',type=str,
                        help='h5 stream object')
    parser.add_argument('-m','--mod', metavar='H5_FILE',type=str,
                        help='h5 3d model')
    args = parser.parse_args()

    int_3d = interp_3d(args.mod)
    st = obspy.read(args.fname)

    f = h5py.File(args.fname,'r')
    h5f = h5py.File('3dmvt_lkup.h5','w')
    evdp = st[0].stats.evdp
    phase_lists = [['sScS','sSvXSScS'],
                  ['sScSScS','sSvXSScSScS'],
                  ['sScSScSScS','sSvXSScSScSScS'],
                  ['ScSScS','ScS^XScS'],
                  ['ScSScSScS','ScS^XScSScS']]

    make_lookup(phase_lists,h5f,st,evdp,int_3d)
    h5f.close()

def interp_3d(mod):
    mod = h5py.File(mod,'r')
    dvs = mod['dvs'][:]
    top = np.zeros((1,dvs.shape[1],dvs.shape[2]))
    dvs = np.vstack((top,dvs))
    h = mod['h'][:]
    h = np.hstack((0,h))
    lat = mod['lat'][:]
    lat = lat[::-1]
    lon = mod['lon'][:]
    int_3d = RegularGridInterpolator((h,lat,lon),dvs)
    mod.close()
    return int_3d

def make_lookup(phase_lists,h5f,st,evdp,int_3d):
    cdp = np.arange(50,1800,10)
    for phase_list in phase_lists:
        for tr in st:
            print 'Computing '+phase_list[0]

            master_time = []
            master_depth = []

            if phase_list[0][0].startswith('s'):
                for ii in cdp:
                    time_list,depth_list,gcarc_list = top_depth_times(evdp,
                                                      ii,phase_list,tr,int_3d)
                    master_time.append(time_list)
                    master_depth.append(depth_list)
            elif phase_list[0][0].startswith('S'):
                for ii in cdp:
                    time_list,depth_list,gcarc_list = bot_depth_times(evdp,
                                                      ii,phase_list)
                    master_time.append(time_list)
                    master_depth.append(depth_list)

            master_time = np.array(master_time)
            master_time = np.vstack((np.zeros(master_time.shape[1]),
                                     master_time))
            master_depth = np.array(master_depth)
            master_depth = np.vstack((np.zeros(master_depth.shape[1]),
                                     master_depth))

            for idx,ii in enumerate(gcarc_list):
                f = interp1d(master_time[:,idx],master_depth[:,idx])
                tnew = np.arange(master_time[0,idx],master_time[-1,idx],0.1)
                dnew = f(tnew)
                h5f.create_dataset(phase_list[0]+'/'+str(ii),
                                   data=np.vstack((tnew,dnew)))

def top_depth_times(evdp,cdp,phase_list_in,tr,int_3d):
    mod = TauPyModel(model='prem'+str(int(cdp)))
    phase_list = phase_list_in[:]
    phase_list[1] = phase_list[1].replace('X',str(cdp))
    time_list = []
    depth_list = []

    arr = mod.get_ray_paths_geo(source_depth_in_km=evdp,
                               source_latitude_in_deg=tr.stats.evla,
                               source_longtude_in_deg=tr.stats.evlo,
                               receiver_latitude_in_deg=tr.stats.stla,
                               receiver_longitude_in_deg=tr.stats.stlo,
                               phase_list=phase_list)

    pure_depth = float(re.findall('\d+',arr[1].purist_name)[0])
    time = arr[1].time-arr[0].time
    time_list.append(time)
    paths = np.array([list((i[3],i[4],i[5])) for i in arr.path])
    depth_list.append(pure_depth)

    r = np.array([list(i) for i in arr[0].path])

    return time_list,depth_list,gcarc_list

def bot_depth_times(evdp,cdp,phase_list_in):
    mod = TauPyModel(model='prem'+str(int(cdp)))
    phase_list = phase_list_in[:]
    phase_list[1] = phase_list[1].replace('X',str(cdp))
    time_list = []
    depth_list = []
    gcarc_list = np.linspace(0,90,num=91)

    for ii in gcarc_list:
        arr = mod.get_ray_paths(source_depth_in_km=evdp,
                                   distance_in_degree=ii,
                                   phase_list=phase_list)
        pure_depth = float(re.findall('\d+',arr[0].purist_name)[0])
        time = arr[1].time-arr[0].time
        time_list.append(time)
        depth_list.append(pure_depth)

    return time_list,depth_list,gcarc_list

main()


