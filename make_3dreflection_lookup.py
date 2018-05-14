#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : make_3dreflection_lookup.py
Purpose : Make 3d lookup table of ScS reflection points for an event.
Creation Date : 19-01-2018
Last Modified : Sat 05 May 2018 01:35:32 PM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from scipy.signal import argrelextrema
from subprocess import call
import h5py
import obspy
import argparse
from obspy.taup import TauPyModel
#from deco import concurrent,synchronized

def main():
    parser = argparse.ArgumentParser(description='Make \
                                     lookup table of ScS reflection points')
    parser.add_argument('-f','--fname', metavar='H5_FILE',type=str,
                    help='Any h5 data file with cooords dict (deconvolve.h5)')
    parser.add_argument('-s','--stride', metavar='int',type=int,
                    help='stride integer',default=1)
    args = parser.parse_args()
    stride = args.stride

    family_dict = make_families()
    try:
        r = h5py.File('3dreflection_points.h5','w',driver='core')
    except IOError:
        call('rm 3dreflection_points.h5',shell=True)
        r = h5py.File('3dreflection_points.h5','w',driver='core')

    f = h5py.File(args.fname,'r',driver='core')

    run(r,f,family_dict,stride)
    r.close()
    f.close()

def run(r,f,family_dict,stride):
    c_depths = np.arange(50,905,5)
    for idx,ikeys in enumerate(f):
        if idx%stride != 0:
            continue
        else:
            print ikeys,round(float(idx)/len(f.keys())*100.,2),'%'
            r.create_group(ikeys)
            coords = f[ikeys]['coords']
            r[ikeys].create_dataset('coords',data=coords)
            for jkeys in f[ikeys]:
                if not jkeys.startswith('c'):
                    r[ikeys].create_group(jkeys)
                    for c_depth in c_depths:
                        phase_family = [i.replace('X',str(c_depth)) for i in \
                                        family_dict[jkeys]]
                        reflect_coords,arr_name = find_reflect_coord(coords,
                                                                     phase_family,
                                                                     c_depth)
                        for idx,phase in enumerate(arr_name):
                            try:
                                r[ikeys][jkeys].create_dataset(phase,
                                                          data=reflect_coords[idx])
                            except RuntimeError:
                                continue

def make_families():
    family_dict = {'sScS':['sSvXSScS','sScSSvXS'],
                   'ScSScS':['ScS^XScS'],
                   'sScSScS':['sSvXSScSScS','sScSSvXSScS','sScSScSSvXS'],
                   'ScSScSScS':['ScS^XScSScS','ScSScS^XScS'],
                   'sScSScSScS':['sSvXSScSScSScS','sScSSvXSScSScS',
                                 'sScSScSSvXSScS','sScSScSScSSvXS']}
    return family_dict

def find_reflect_coord(coords,phase_family,c_depth):
    model = TauPyModel(model='prem'+str(c_depth))
    arr = model.get_pierce_points_geo(source_depth_in_km=coords[1],
                               source_latitude_in_deg=coords[4],
                               source_longitude_in_deg=coords[5],
                               receiver_latitude_in_deg=coords[2],
                               receiver_longitude_in_deg=coords[3],
                               phase_list=phase_family)

    reflect_coords = []
    arr_name = []
    for arrivals in arr:
        a = np.array([[jj for jj in ii] for ii in arrivals.pierce])
        if 'v' in phase_family[0]:
            #ex = argrelextrema(a[:-3],np.greater)[0]
            ex = argrelextrema(a,np.greater)[0]
            for ii in ex:
                if a[ii,-3] != c_depth:
                    continue
                else:
                   arr_name.append(arrivals.name)
                   reflect_coords.append([a[ii,-2],a[ii,-1]])

        if '^' in phase_family[0]:
            #ex = argrelextrema(a[:-3],np.less)[0]
            ex = argrelextrema(a,np.less)[0]
            for ii in ex:
                if a[ii,-3] != c_depth:
                    continue
                else:
                   arr_name.append(arrivals.name)
                   reflect_coords.append([a[ii,-2],a[ii,-1]])

    return reflect_coords,arr_name

main()
