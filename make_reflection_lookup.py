#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : make_reflection_lookup.py
Purpose : Make lookup table of ScS reflection points for an event.
Creation Date : 19-01-2018
Last Modified : Thu 08 Feb 2018 03:40:42 PM EST
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
from deco import concurrent,synchronized

def main():
    parser = argparse.ArgumentParser(description='Make \
                                     lookup table of ScS reflection points')
    parser.add_argument('-f','--fname', metavar='H5_FILE',type=str,
                    help='Any h5 data file with cooords dict (deconvolve.h5)')
    args = parser.parse_args()

    family_dict = make_families()
    r = h5py.File('reflection_points.h5','w',driver='core')
    f = h5py.File(args.fname,'r',driver='core')

    run(r,f,family_dict)
    r.close()
    f.close()

def run(r,f,family_dict):
    c_depths = np.arange(50,905,5)
    for idx,ikeys in enumerate(f):
        print float(idx)/len(f.keys())
        r.create_group(ikeys)
        coords = f[ikeys]['coords']
        r[ikeys].create_dataset('coords',data=coords)
        for jkeys in f[ikeys]:
            if not jkeys.startswith('c'):
                r[ikeys].create_group(jkeys)
                for c_depth in c_depths:
                    phase_family = [i.replace('#',str(c_depth)) for i in \
                                    family_dict[jkeys]]
                    reflect_coords = find_reflect_coord(coords,
                                                        phase_family,
                                                        c_depth)

                    r[ikeys][jkeys].create_dataset(str(c_depth),
                                                   data=reflect_coords)

def make_families():
    family_dict = {'sScS':['sSv#SScS','sScSSv#S'],
                   'ScSScS':['ScS^#ScS'],
                   'sScSScS':['sSv#SScSScS','sScSSv#SScS','sScSScSSv#S'],
                   'ScSScSScS':['ScS^#ScSScS','ScSScS^#ScS'],
                   'sScSScSScS':['sSv#SScSScSScS','sScSSv#SScSScS',
                                   'sScSScSSv#SScS','sScSScSScSSv#S']}
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
    for arrivals in arr:
        a = np.array([[jj for jj in ii] for ii in arrivals.pierce])
        if 'v' in phase_family[0]:
            ex = argrelextrema(a[:-3],np.greater)[0]
            for ii in ex:
                if a[ii,-3] != c_depth:
                    continue
                else:
                   reflect_coords.append([a[ii,-2],a[ii,-1]])

        if '^' in phase_family[0]:
            ex = argrelextrema(a[:-3],np.less)[0]
            for ii in ex:
                if a[ii,-3] != c_depth:
                    continue
                else:
                   reflect_coords.append([a[ii,-2],a[ii,-1]])

    return reflect_coords

main()
