#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : deconvolve.py
Purpose : deconvolve strips from h5 file. Write to h5
Creation Date : 14-01-2018
Last Modified : Thu 01 Feb 2018 02:39:15 PM EST
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
from scipy.signal import tukey,cosine,blackmanharris
from sys import argv
import h5py
import argparse

def main():
    parser = argparse.ArgumentParser(description='deconvolve reverb and write')
    parser.add_argument('-f','--fname', metavar='H5_FILE',type=str,
                        help='h5 file output from extract_reverb.py')
    args = parser.parse_args()

    f = h5py.File(args.fname,'r',driver='core')
    f_dec = h5py.File('deconvolve.h5','w',driver='core')

    for keys in f:
        f_dec.create_group(keys)
        for items in f[keys]:
            phase = f[keys][items].name
            if phase.split('/')[-1] == 'coords':
                f_dec.create_dataset(phase,data=f[keys][items][...])
            else:
                data = f[keys][items][...]
                data *= 1./data.max()
                phase_name = f[keys][items].name.split('/')[-1]
                mask = mask_data(data,phase_name)
                t,rf = water_level(data,mask)
                if phase.split('/')[-1].startswith('s'):
                    rf = np.roll(rf,500)
                    rf = -1*np.roll(rf,500-np.argmax(rf))
                elif phase.split('/')[-1].startswith('S'):
                    rf = np.roll(rf,-500)[::-1]
                    rf = np.roll(rf,500-np.argmax(rf))
                f_dec.create_dataset(phase,data=rf)
    f.close()
    f_dec.close()

def mask_data(data,phase):
    mask = np.zeros(len(data))
    sr = 10
    mask[int(0*sr):int(100*sr)] = tukey(int(100*sr),0.6)
    if phase.startswith('S'):
        mask = mask[::-1]*data
    elif phase.startswith('s'):
        mask *= data
    return mask

def water_level(a,b,alpha=0.1,plot=False):
    t = np.linspace(0,len(a)*10.,len(a))

    #Convert to frequency domain-------------------------------
    a_omega = np.fft.fft(a)
    b_omega = np.fft.fft(b)

    #Perform division------------------------------------------
    F_omega = b_omega*b_omega.conjugate()
    Phi_ss  = np.maximum(F_omega,alpha*(np.amax(F_omega)))
    try:
        H_omega = ((a_omega*b_omega.conjugate())/Phi_ss)
    except RuntimeWarning:
        return np.zeros(len(a))

    #Convert back to time domain-------------------------------
    #rf = np.zeros(len(H_omega))
    rf = np.fft.ifft(H_omega)

    #Plots-----------------------------------------------------
    if plot==True:
        fig,ax = plt.subplots(2,1)
        ax[0].plot(t,a)
        ax[0].plot(t,b)
        ax[1].plot(t,rf)
        plt.show()

    #roll = int(10*50-np.argmax(rf))
    #rf = np.roll(rf,roll)
    return t,np.real(rf)

main()
