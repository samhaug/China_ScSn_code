#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : time_2_h5.py
Purpose : turn output of taup_time command into h5_lookup
Creation Date : 07-05-2018
Last Modified : Thu 10 May 2018 10:35:26 AM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from subprocess import call
import h5py
from os import listdir
from glob import glob
from sys import argv

def main():

    depth = argv[1].split('_')[1]
    f = h5py.File('times_{}.h5'.format(depth),'w')
    f.create_group('sScS')
    f.create_group('sScSScS')
    f.create_group('sScSScSScS')
    f.create_group('ScSScS')
    f.create_group('ScSScSScS')
    files = glob(argv[1]+'/*gmt')
    for ii in files:
        #print ii.split('/')[-1]
        if ii.split('/')[-1].startswith('PURE'):
            name ='PURE'
            if ii.split('/')[-1].split('.')[0].split('_')[1] == 'sScS':
                f['sScS'].create_dataset(name,data=np.genfromtxt(ii))
            if ii.split('/')[-1].split('.')[0].split('_')[1] == 'sScS2':
                f['sScSScS'].create_dataset(name,data=np.genfromtxt(ii))
            if ii.split('/')[-1].split('.')[0].split('_')[1] == 'sScS3':
                f['sScSScSScS'].create_dataset(name,data=np.genfromtxt(ii))
            if ii.split('/')[-1].split('.')[0].split('_')[1] == 'ScS2':
                f['ScSScS'].create_dataset(name,data=np.genfromtxt(ii))
            if ii.split('/')[-1].split('.')[0].split('_')[1] == 'ScS3':
                f['ScSScSScS'].create_dataset(name,data=np.genfromtxt(ii))
        else:
            name = ii.split('/')[-1].split('.')[0].split('_')[1]
            #print name
            if ii.split('/')[-1].split('_')[0] == 'sScS':
                f['sScS'].create_dataset(name,data=np.genfromtxt(ii))
            if ii.split('/')[-1].split('_')[0] == 'sScS2':
                f['sScSScS'].create_dataset(name,data=np.genfromtxt(ii))
            if ii.split('/')[-1].split('_')[0] == 'sScS3':
                f['sScSScSScS'].create_dataset(name,data=np.genfromtxt(ii))
            if ii.split('/')[-1].split('_')[0] == 'ScS2':
                f['ScSScS'].create_dataset(name,data=np.genfromtxt(ii))
            if ii.split('/')[-1].split('_')[0] == 'ScS3':
                f['ScSScSScS'].create_dataset(name,data=np.genfromtxt(ii))

main()


