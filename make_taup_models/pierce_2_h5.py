#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : time_2_array.py
Purpose : turn output of taup_time command into simple ascii table
Creation Date : 07-05-2018
Last Modified : Tue 08 May 2018 11:55:46 AM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from os import listdir
from sys import argv
import h5py
from glob import glob

def main():
    flist = glob('./pierce/*gmt')
    for ii in flist:
        if 'PURE' in ii:
            flist.remove(ii)
    f = h5py.File('pierce_lookup.h5','w')

    f.create_group('ScS2')
    f.create_group('ScS3_1')
    f.create_group('ScS3_2')
    f.create_group('sScS_1')
    f.create_group('sScS_2')
    f.create_group('sScS2_1')
    f.create_group('sScS2_2')
    f.create_group('sScS2_3')
    f.create_group('sScS3_1')
    f.create_group('sScS3_2')
    f.create_group('sScS3_3')
    f.create_group('sScS3_4')

    f.create_dataset('PURE_ScS2', data=np.genfromtxt('./pierce/PURE_ScS2.gmt'))
    f.create_dataset('PURE_ScS3', data=np.genfromtxt('./pierce/PURE_ScS3.gmt'))
    f.create_dataset('PURE_sScS', data=np.genfromtxt('./pierce/PURE_sScS.gmt'))
    f.create_dataset('PURE_sScS2',data=np.genfromtxt('./pierce/PURE_sScS2.gmt'))
    f.create_dataset('PURE_sScS3',data=np.genfromtxt('./pierce/PURE_sScS3.gmt'))

    for ii in flist:
        c = ii.split('/')[-1].split('.')[0]
        deg_list = []
        time_list = []
        if c.split('_')[0] == 'ScS2':
            depth = float(c.split('_')[1])
            group = 'ScS2'
            f['ScS2'].create_group(str(int(depth)))
        else:
            depth = float(ii.split('/')[-1].split('.')[0].split('_')[-1])
            group = c.split('_')[0]+'_'+c.split('_')[1]
            f[group].create_group(str(int(depth)))

        a = open(ii).readlines()
        for jj in a:
            if jj[0] == '>':
                continue
            elif float(jj.split()[0]) < 0:
                continue
            elif float(jj.split()[1]) == depth:
                deg_list.append(float(jj.split()[0]))
                time_list.append(float(jj.split()[2]))
        if len(deg_list) != 181 or len(time_list) != 181:
            print ii,' Length != 181'
        f[group][str(int(depth))].create_dataset('deg',
                                  data=np.array(deg_list))
        f[group][str(int(depth))].create_dataset('time',
                                  data=np.array(time_list))
    f.close()

main()



