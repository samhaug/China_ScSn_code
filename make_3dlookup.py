#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : make_3dlookup.py
Purpose : Make h5 lookup table of reverberation traveltimes for 3d model
Creation Date : 20-12-2017
Last Modified : Sat 03 Feb 2018 05:41:13 PM EST
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
                        help='h5 stream object')
    args = parser.parse_args()
    int_3d = interp_netcdf_3d()
    st = obspy.read(args.fname)

    try:
        h5f = h5py.File('3dmvt_lkup.h5','w',driver='core')
    except IOError:
        call('rm 3dmvt_lkup.h5',shell=True)
        h5f = h5py.File('3dmvt_lkup.h5','w',driver='core')

    evdp = st[0].stats.evdp
    phase_lists = [['sScS','sSvXSScS'],
                  ['sScSScS','sSvXSScSScS'],
                  ['sScSScSScS','sSvXSScSScSScS'],
                  ['ScSScS','ScS^XScS'],
                  ['ScSScSScS','ScS^XScSScS']]

    make_lookup(phase_lists,h5f,st,evdp,int_3d)
    h5f.close()

def interp_netcdf_3d():
    dataset = Dataset('/home/samhaug/work1/China_ScSn_code/3D_model/3D2016-09Sv-depth.nc')
    lat = dataset.variables['latitude'][::-1]
    lon = dataset.variables['longitude'][:]
    h = dataset.variables['depth'][:]
    h = np.hstack((0,h))
    dvs = dataset.variables['dvs'][:].data
    top = np.zeros((1,dvs.shape[1],dvs.shape[2]))
    dvs = np.vstack((top,dvs))
    for ii in range(17,len(dvs)):
        dvs[ii] = np.zeros(dvs[ii].shape)
    #We use 1-(dvs/100.) to adjust ttimes
    #plt.imshow(dvs[2],aspect='auto',extent=[lon[0],lon[-1],lat[0],lat[-1]])
    int_3d = RegularGridInterpolator((h,lat,lon),dvs)
    #plt.show()
    return int_3d

def make_lookup(phase_lists,h5f,st,evdp,int_3d):
    cdp = np.arange(50,1800,10)
    for phase_list in phase_lists:
        print 'Computing '+phase_list[0]
        for idx,tr in enumerate(st):
            name = tr.stats.network+tr.stats.station+tr.stats.location
            print name

            master_time = []
            master_time_3d = []
            master_depth = []

            #get time of main phase in 3d
            mod = TauPyModel('prem')
            arr = mod.get_ray_paths_geo(source_depth_in_km=evdp,
                                source_latitude_in_deg=tr.stats.evla,
                                source_longitude_in_deg=tr.stats.evlo,
                                receiver_latitude_in_deg=tr.stats.stla,
                                receiver_longitude_in_deg=tr.stats.stlo,
                                phase_list=[phase_list[0]])
            main_path = np.array([list((i[3],-i[4],i[5])) for i in arr[0].path])
            main_trace = 1-(int_3d(main_path)[1::]*0.01)
            main_dt = np.diff(np.array([i[1] for i in arr[0].path]))
            time_3d = np.sum(main_dt*main_trace)

            h5f.create_dataset(name+'/'+phase_list[0]+'/prem',
                               data=np.array([arr[0].time]))
            h5f.create_dataset(name+'/'+phase_list[0]+'/3d',
                               data=np.array([time_3d]))

            if phase_list[0][0].startswith('s'):
                for ii in cdp:
                    time_list,time_list_3d,depth_list = top_depth_times(evdp,
                                                      ii,phase_list,tr,int_3d)
                    master_time.append(time_list)
                    master_time_3d.append(time_list_3d)
                    master_depth.append(depth_list)

            elif phase_list[0][0].startswith('S'):
                for ii in cdp:
                    time_list,time_list_3d,depth_list = bot_depth_times(evdp,
                                                      ii,phase_list,tr,int_3d)
                    master_time.append(time_list)
                    master_time_3d.append(time_list_3d)
                    master_depth.append(depth_list)

            master_time = np.array(master_time)
            master_time = np.vstack((0,master_time))
            master_time_3d = np.array(master_time_3d)
            master_time_3d = np.vstack((0,master_time_3d))
            master_depth = np.array(master_depth)
            master_depth = np.vstack((0,master_depth))

            h5f.create_dataset(name+'/'+phase_list[0]+'/time',
                               data=master_time)
            h5f.create_dataset(name+'/'+phase_list[0]+'/time_3d',
                               data=master_time_3d)
            h5f.create_dataset(name+'/'+phase_list[0]+'/depth',
                               data=master_depth)

def top_depth_times(evdp,cdp,phase_list_in,tr,int_3d):
    mod = TauPyModel(model='prem'+str(int(cdp)))
    phase_list = phase_list_in[:]
    phase_list[1] = phase_list[1].replace('X',str(cdp))
    depth_list = []
    time_list = []
    time_list_3d = []


    arr = mod.get_ray_paths_geo(source_depth_in_km=evdp,
                                source_latitude_in_deg=tr.stats.evla,
                                source_longitude_in_deg=tr.stats.evlo,
                                receiver_latitude_in_deg=tr.stats.stla,
                                receiver_longitude_in_deg=tr.stats.stlo,
                                phase_list=phase_list)

    pure_depth = float(re.findall('\d+',arr[1].purist_name)[0])
    depth_list.append(pure_depth)
    time = arr[1].time-arr[0].time
    time_list.append(time)
    main_path = np.array([list((i[3],-i[4],i[5])) for i in arr[0].path])
    rev_path = np.array([list((i[3],-i[4],i[5])) for i in arr[1].path])
    main_trace = 1-(int_3d(main_path)[1::]*0.01)
    rev_trace = 1-(int_3d(rev_path)[1::]*0.01)
    main_dt = np.diff(np.array([i[1] for i in arr[0].path]))
    rev_dt = np.diff(np.array([i[1] for i in arr[1].path]))
    time_list_3d.append(np.sum(rev_dt*rev_trace)-np.sum(main_dt*main_trace))

    return time_list,time_list_3d,depth_list

def bot_depth_times(evdp,cdp,phase_list_in,tr,int_3d):
    mod = TauPyModel(model='prem'+str(int(cdp)))
    phase_list = phase_list_in[:]
    phase_list[1] = phase_list[1].replace('X',str(cdp))
    depth_list = []
    time_list = []
    time_list_3d = []

    arr = mod.get_ray_paths_geo(source_depth_in_km=evdp,
                                source_latitude_in_deg=tr.stats.evla,
                                source_longitude_in_deg=tr.stats.evlo,
                                receiver_latitude_in_deg=tr.stats.stla,
                                receiver_longitude_in_deg=tr.stats.stlo,
                                phase_list=phase_list)
    pure_depth = float(re.findall('\d+',arr[0].purist_name)[0])
    depth_list.append(pure_depth)
    time = arr[1].time-arr[0].time
    time_list.append(time)
    main_path = np.array([list((i[3],-i[4],i[5])) for i in arr[1].path])
    rev_path = np.array([list((i[3],-i[4],i[5])) for i in arr[0].path])
    main_trace = 1-(int_3d(main_path)[1::]*0.01)
    rev_trace = 1-(int_3d(rev_path)[1::]*0.01)
    main_dt = np.diff(np.array([i[1] for i in arr[1].path]))
    rev_dt = np.diff(np.array([i[1] for i in arr[0].path]))
    time_list_3d.append(np.sum(main_dt*main_trace-np.sum(rev_dt*rev_trace)))

    return time_list,time_list_3d,depth_list

main()


