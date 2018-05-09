#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : equate_metadata.py
Purpose : ---
Creation Date : 01-05-2018
Last Modified : Tue 01 May 2018 06:14:43 PM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import obspy
#import argparse

def main():

    #parser = argparse.ArgumentParser(description='Radon transform')
    #parser.add_argument('-s','--synth', metavar='H5_FILE',type=str,
    #                    help='h5 stream')
    #parser.add_argument('-d','--data', metavar='H5_FILE',type=str,
    #                    help='h5 stream')
    #parser.add_argument('--read', metavar='T/F',type=str,
    #                    help='read from existing radon datfile',default='False')
    #args = parser.parse_args()

    #std = obspy.read(args.data)
    #sts = obspy.read(args.synth)
    sts = obspy.read('sts_T_radon.h5')
    st = obspy.read('st_T_radon.h5')
    for idx,tr in enumerate(sts):
        sts[idx].stats.station = st[idx].stats.station
        sts[idx].stats.network = st[idx].stats.network
        sts[idx].stats.location = st[idx].stats.location
    sts.write('sts_T_radon.h5',format='H5')
    st.write('st_T_radon.h5',format='H5')

main()
