#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : grid_sum.py
Purpose : Sum reverberations over grid.
Creation Date : 22-01-2018
Last Modified : Mon 22 Jan 2018 02:21:48 PM EST
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
from subprocess import call
from os import listdir
import h5py
import obspy

def main():

def make_grid_coordinates():
    m = Basemap(llcrnrlon=70,llcrnrlat=-20,urcrnrlon=170,
            urcrnrlat=60,projection='mill')
    lonmin,lonmax = 70,170
    latmin,latmax = -20,60
    hmin,hmax = 50,750
    lon = np.linspace(lonmin,lonmax,num=int(2*(lonmax-lonmin)))
    lat = np.linspace(latmin,latmax,num=int(2*(latmax-latmin)))
    h = np.linspace(hmin,hmax,num=int(2*(hmax-hmin)))
    grid = np.zeros(len(lon),len(lat),len(h))
    return lon,lat,h,grid



main()
