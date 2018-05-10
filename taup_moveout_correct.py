#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : make_3dlookup.py
Purpose : Make h5 lookup table of reverberation traveltimes for 3d model
Creation Date : 20-12-2017
Last Modified : Thu 10 May 2018 10:24:04 AM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
from obspy.taup import TauPyModel
from subprocess import call
import h5py
from netCDF4 import Dataset
from scipy.interpolate import interp1d
from scipy.interpolate import RegularGridInterpolator
import re
import obspy
import argparse
import obspy

def main():
    parser = argparse.ArgumentParser(
                       description='make lookup table for event in 3d model')
    parser.add_argument('-f','--fname', metavar='H5_FILE',type=str,
                        help='any h5 data file with coords dict (deconvolve.h5)')
    args = parser.parse_args()
    int_3d = interp_netcdf_3d()
    #st = obspy.read(args.fname)
    h5d = h5py.File(args.fname,'r',driver='core')

    try:
        h5f = h5py.File('3dmvt_lkup.h5','w',driver='core')
    except IOError:
        call('rm 3dmvt_lkup.h5',shell=True)
        h5f = h5py.File('3dmvt_lkup.h5','w',driver='core')

    #evdp = st[0].stats.evdp

    phase_families = {'sScS':['sSvXSScS','sScSSvXS'],
                     'sScSScS':['sSvXSScSScS','sScSSvXSScS','sScSScSSvXS'],
                     'sScSScSScS':['sSvXSScSScSScS','sScSSvXSScSScS',
                                   'sScSScSSvXSScS','sScSScSScSSvXS'],
                     'ScSScS':['ScS^XScS'],
                     'ScSScSScS':['ScS^XScSScS','ScScS^XScS']}

    #make_lookup(phase_families,h5f,st,evdp,int_3d)
    make_h5_lookup(phase_families,h5f,h5d,int_3d)
    h5f.close()

def interp_netcdf_3d():
    dataset = Dataset('/home/samhaug/work1/China_ScSn_code/'\
                      '3D_model/3D2016-09Sv-depth.nc')
    lat = dataset.variables['latitude'][::-1]
    lon = dataset.variables['longitude'][:]
    h = dataset.variables['depth'][:]
    h = np.hstack((0,h))
    dvs = dataset.variables['dvs'][:].data
    top = np.zeros((1,dvs.shape[1],dvs.shape[2]))
    dvs = np.vstack((top,dvs))
    dvs[-1] = top
    h[-1] = 2891.
    int_3d = RegularGridInterpolator((h,lat,lon),dvs)
    return int_3d

def make_lookup(phase_families,h5f,st,evdp,int_3d):
    cdp = np.arange(50,1010,20)
    mod = TauPyModel('prem')
    for idx,tr in enumerate(st):
        name = tr.stats.network+tr.stats.station+tr.stats.location
        print name,round(float(idx)/len(f.keys())*100.,2),'%'
        h5f.create_group(name)
        for keys in phase_families:
            h5f[name].create_group(keys)
            arr = mod.get_ray_paths_geo(source_depth_in_km=evdp,
                source_latitude_in_deg=tr.stats.evla,
                source_longitude_in_deg=tr.stats.evlo,
                receiver_latitude_in_deg=tr.stats.stla,
                receiver_longitude_in_deg=tr.stats.stlo,
                phase_list=[keys])
            h5f[name][keys].create_dataset('1d_time',data=[arr[0].time])
            main_path = np.array([list((i[3],-i[4],i[5])) for i in arr[0].path])
            main_trace = 1-(int_3d(main_path)[1::]*0.01)
            main_dt = np.diff(np.array([i[1] for i in arr[0].path]))
            time_3d = np.sum(main_dt*main_trace)
            h5f[name][keys].create_dataset('3d_time',data=[time_3d])

            for phase in phase_families[keys]:

                h5f[name][keys].create_group(phase)
                master_time = []
                master_time_3d = []
                master_depth = []

                if phase.startswith('s'):
                    for ii in cdp:
                        time_list,time_list_3d,depth_list = top_depth_times(
                                                    evdp,ii,phase,tr,int_3d)
                        master_time.append(time_list)
                        master_time_3d.append(time_list_3d)
                        master_depth.append(depth_list)

                elif phase.startswith('S'):
                    for ii in cdp:
                        time_list,time_list_3d,depth_list = bot_depth_times(
                                                    evdp,ii,phase,tr,int_3d)
                        master_time.append(time_list)
                        master_time_3d.append(time_list_3d)
                        master_depth.append(depth_list)

                master_time = np.array(master_time)
                master_time = np.vstack((0,master_time))
                master_time_3d = np.array(master_time_3d)
                master_time_3d = np.vstack((0,master_time_3d))
                master_depth = np.array(master_depth)
                master_depth = np.vstack((0,master_depth))

                h5f[name][keys][phase].create_dataset('1d_time',
                                                      data=master_time)
                h5f[name][keys][phase].create_dataset('3d_time',
                                                      data=master_time_3d)
                h5f[name][keys][phase].create_dataset('depth',
                                                      data=master_depth)

def make_h5_lookup(phase_families,h5f,h5d,int_3d):
    cdp = np.arange(50,1010,20)
    mod = TauPyModel('prem')
    for idx,keys in enumerate(h5d.keys()):
    #for idx,tr in enumerate(st):
        #name = tr.stats.network+tr.stats.station+tr.stats.location
        print keys,round(float(idx)/len(h5d.keys())*100.,2),'%'
        h5f.create_group(keys)
        evdp = h5d[keys]['coords'][1]
        stla = h5d[keys]['coords'][2]
        stlo = h5d[keys]['coords'][3]
        evla = h5d[keys]['coords'][4]
        evlo = h5d[keys]['coords'][5]
        for phase in h5d[keys]:
            if not phase.startswith('c'):
                h5f[keys].create_group(phase)
                arr = mod.get_ray_paths_geo(source_depth_in_km=evdp,
                      source_latitude_in_deg=evla,
                      source_longitude_in_deg=evlo,
                      receiver_latitude_in_deg=stla,
                      receiver_longitude_in_deg=stlo,
                      phase_list=[phase])
                h5f[keys][phase].create_dataset('1d_time',data=[arr[0].time])
                main_path = np.array([list((i[3],-i[4],i[5])) \
                                     for i in arr[0].path])
                main_trace = 1-(int_3d(main_path)[1::]*0.01)
                main_dt = np.diff(np.array([i[1] for i in arr[0].path]))
                time_3d = np.sum(main_dt*main_trace)
                h5f[keys][phase].create_dataset('3d_time',data=[time_3d])

                for iphase in phase_families[phase]:

                    h5f[keys][phase].create_group(iphase)
                    master_time = []
                    master_time_3d = []
                    master_depth = []

                    if iphase.startswith('s'):
                        for ii in cdp:
                            time_list,time_list_3d,depth_list = top_depth_times(
                                                        evdp,ii,iphase,
                                                        stla,stlo,evla,evlo,
                                                        int_3d)
                            master_time.append(time_list)
                            master_time_3d.append(time_list_3d)
                            master_depth.append(depth_list)

                    elif iphase.startswith('S'):
                        for ii in cdp:
                            time_list,time_list_3d,depth_list = bot_depth_times(
                                                        evdp,ii,iphase,
                                                        stla,stlo,evla,evlo,
                                                        int_3d)
                            master_time.append(time_list)
                            master_time_3d.append(time_list_3d)
                            master_depth.append(depth_list)

                    master_time = np.array(master_time)
                    master_time = np.vstack((0,master_time))
                    master_time_3d = np.array(master_time_3d)
                    master_time_3d = np.vstack((0,master_time_3d))
                    master_depth = np.array(master_depth)
                    master_depth = np.vstack((0,master_depth))

                    h5f[keys][phase][iphase].create_dataset('1d_time',
                                                          data=master_time)
                    h5f[keys][phase][iphase].create_dataset('3d_time',
                                                          data=master_time_3d)
                    h5f[keys][phase][iphase].create_dataset('depth',
                                                          data=master_depth)

def top_depth_times(evdp,cdp,phase_list_in,stla,stlo,evla,evlo,int_3d):
    mod = TauPyModel(model='prem'+str(int(cdp)))
    phase_list = phase_list_in
    phase_list = phase_list.replace('X',str(cdp))
    depth_list = []
    time_list = []
    time_list_3d = []

    arr = mod.get_ray_paths_geo(source_depth_in_km=evdp,
                                source_latitude_in_deg=evla,
                                source_longitude_in_deg=evlo,
                                receiver_latitude_in_deg=stla,
                                receiver_longitude_in_deg=stlo,
                                phase_list=[phase_list])

    pure_depth = float(re.findall('\d+',arr[0].purist_name)[0])
    depth_list.append(pure_depth)
    time = arr[0].time
    time_list.append(time)
    rev_path = np.array([list((i[3],-i[4],i[5])) for i in arr[0].path])
    rev_trace = 1-(int_3d(rev_path)[1::]*0.01)
    rev_dt = np.diff(np.array([i[1] for i in arr[0].path]))
    time_list_3d.append(np.sum(rev_dt*rev_trace))

    return time_list,time_list_3d,depth_list

def bot_depth_times(evdp,cdp,phase_list_in,stla,stlo,evla,evlo,int_3d):
    mod = TauPyModel(model='prem'+str(int(cdp)))
    phase_list = phase_list_in
    phase_list = phase_list.replace('X',str(cdp))
    depth_list = []
    time_list = []
    time_list_3d = []

    arr = mod.get_ray_paths_geo(source_depth_in_km=evdp,
                                source_latitude_in_deg=evla,
                                source_longitude_in_deg=evlo,
                                receiver_latitude_in_deg=stla,
                                receiver_longitude_in_deg=stlo,
                                phase_list=[phase_list])
    pure_depth = float(re.findall('\d+',arr[0].purist_name)[0])
    depth_list.append(pure_depth)
    time = arr[0].time
    time_list.append(time)
    rev_path = np.array([list((i[3],-i[4],i[5])) for i in arr[0].path])
    rev_trace = 1-(int_3d(rev_path)[1::]*0.01)
    rev_dt = np.diff(np.array([i[1] for i in arr[0].path]))
    time_list_3d.append(np.sum(np.sum(rev_dt*rev_trace)))

    return time_list,time_list_3d,depth_list

main()


