import numpy as np
from matplotlib import pyplot as plt

def Radon_forward(t,p,R,delta,ref_dist,line_model):
    #This function applies the time-shift Radon operator A, to the Radon 
    #domain.  Will calculate the move-out data, given the inputs:
    # -t        -- vector of time axis.
    # -p        -- vector of slowness axis you would like to invert to.
    # -R        -- matrix of Radon data, ordered size(R)==[length(p),length(t)].
    # -delta    -- vector of distance axis.
    # -ref_dist -- reference distance the path-function will shift about.
    #
    # -line_model, select one of the following options for path integration:
    #     'linear'     - linear paths in the spatial domain (default)
    #     'parabolic'  - parabolic paths in the spatial domain.
    #
    #Output spatial domain is ordered size(M)==[length(delta),length(t)].
    #
    #Known limitations:
    # - Assumes evenly sampled time axis.
    # - Assumes Radon data isn't complex.
    #
    #
    # References: Schultz, R., Gu, Y. J., 2012. Flexible, inversion-based Matlab 
    #             implementation of the Radon Transform.  Computers and 
    #             Geosciences [In Preparation]
    #
    #             An, Y., Gu, Y. J., Sacchi, M., 2007. Imaging mantle 
    #             discontinuities using least-squares Radon transform. 
    #             Journal of Geophysical Research 112, B10303.
    #
    # Author: R. Schultz, 2012
    #
    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published
    # by the Free Software Foundation, either version 3 of the License, or
    # any later version.
    #
    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details: http://www.gnu.org/licenses/
    #

    # Define some array/matrices lengths.
    def next_power_of_2(x):
            return 1 if x == 0 else 2**(x - 1).bit_length()

    it = len(t)
    iF = np.power(2,int(np.log2(next_power_of_2(it)))+1) #Double length
    iDelta = len(delta)
    ip = len(p)
    # Exit if inconsistent data is input.
    #print ip,it,R.size
    if (ip,it) != R.shape:
        print('Dimensions inconsistent!\nsize(R)~=[length(p),length(t)]\n')
        M=0
        return M

    # Preallocate space in memory.
    Mfft = np.zeros((iDelta, iF),dtype=complex)
    A = np.zeros((iDelta,ip),dtype=complex)
    Tshift = A

    # Define some values.
    Dist_array = delta-ref_dist
    dF = int(1./(t[1]-t[2]))
    # fft on every row
    Rfft = np.fft.fft(R,iF,1)

    # Populate ray parameter then distance data in time shift matrix.
    for j in range(iDelta):
        if line_model == 'parabolic':
            Tshift[j,:]=p
        else: # Linear is default.
            Tshift[j,:]=p

    for k in range(ip):
        if line_model == 'parabolic':
            Tshift[:,k]=(2*ref_dist*Tshift[:,k]*Dist_array.T)+\
                        (Tshift[:,k]*(Dist_array**2).T)
        else: # Linear is default.
            Tshift[:,k]=Tshift[:,k]*Dist_array.T

    # Loop through each frequency.
    for i in range(int(np.floor((iF+1)/2.))):
        # Make time-shift matrix, A.
        f=(i/float(iF))*dF
        A=np.exp((2j*np.pi*f)*Tshift)
        # Apply Radon operator.
        Mfft[:,i]=np.dot(A,Rfft[:,i])
        # Assuming Hermitian symmetry of the fft, make negative frequencies
        # the complex conjugate of current solution.
        if i != 0:
            Mfft[:,iF-i]=np.conj(Mfft[:,i])

    #M=np.ifft(Mfft,iF,1,'symmetric');
    M=np.fft.ifft(Mfft,iF,1)
    M=M[:,0:it]

    return M




