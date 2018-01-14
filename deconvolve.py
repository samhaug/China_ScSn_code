#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : deconvolve.py
Purpose : deconvolve strips from h5 file. Write to h5
Creation Date : 14-01-2018
Last Modified : Sun 14 Jan 2018 02:15:20 PM EST
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
import h5py

def main():


def mask_trace(data,phase):
    if phase.startswith('s'):
    mask = np.zeros(len(data))
    mask[int(20*sr):int(100*sr)] = boxcar(int(100*sr))
    mask = tr.data*mask
    return mask

def water_level(a,b,alpha=0.1,plot=False):
    t = np.linspace(0,a.stats.npts*a.stats.sampling_rate,a.stats.npts)

    #Convert to frequency domain-------------------------------
    a_omega = np.fft.fft(a.data)
    b_omega = np.fft.fft(b)

    #Perform division------------------------------------------
    F_omega = b_omega*b_omega.conjugate()
    Phi_ss  = np.maximum(F_omega,alpha*(np.amax(F_omega)))
    try:
        H_omega = ((a_omega*b_omega.conjugate())/Phi_ss)
    except RuntimeWarning:
        return np.zeros(len(a.data))

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

    return np.real(rf)



main()
