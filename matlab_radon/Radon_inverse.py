import numpy as np
from scipy.sparse import identity,spdiags
from numpy.linalg import norm,inv,solve

def Radon_inverse(t,delta,M,p,weights,ref_dist,line_model,inversion_model,\
                  hyperparameters):
    '''
    This function inverts move-out data to the Radon domain given the inputs:
     -t        -- vector of time axis.
     -delta    -- vector of distance axis.
     -M        -- matrix of move-out data, ordered
                 size(M)==[length(delta),length(t)].
     -p        -- vector of slowness axis you would like to invert to.
     -weights  -- weighting vector that determines importance of each trace.
                  set vector to ones for no preference.
     -ref_dist -- reference distance the path-function will shift about.

     -line_model, select one of the following options for path integration:
         'linear'     - linear paths in the spatial domain (default)
         'parabolic'  - parabolic paths in the spatial domain.

     -inversion model, select one of the following
                        options for regularization schema:
         'L2'       - Regularized on the L2 norm of the Radon domain (default)
         'L1'       - Non-linear regularization based on L1 norm and iterative
                      reweighted least sqaures (IRLS) see Sacchi 1997.
         'Cauchy'   - Non-linear regularization see Sacchi & Ulrych 1995

     -hyperparameters, trades-off between fitting the data and chosen damping.

    Output radon domain is ordered size(R)==[length(p),length(t)].

    Known limitations:
     - Assumes evenly sampled time axis.
     - Assumes move-out data isn't complex.


     References: Schultz, R., Gu, Y. J., 2012. Flexible, inversion-based Matlab 
                 implementation of the Radon Transform.  Computers and
                 Geosciences [In Preparation]

                 An, Y., Gu, Y. J., Sacchi, M., 2007. Imaging mantle
                 discontinuities using least-squares Radon transform.
                 Journal of Geophysical Research 112, B10303.

     Author: R. Schultz, 2012

     This program is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published
     by the Free Software Foundation, either version 3 of the License, or
     any later version.

     This program is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details: http://www.gnu.org/licenses/

    '''

    # Define some array/matrices lengths.
    def next_power_of_2(x):
            return 1 if x == 0 else 2**(x - 1).bit_length()

    it=len(t)
    iF = np.power(2,int(np.log2(next_power_of_2(it)))+1)
    iDelta=len(delta)
    ip=len(p)
    iw=len(weights)

    # Exit if inconsistent data is input.
    if (iDelta,it) != M.shape:
        print('Dimensions inconsistent!\nsize(M)~=[len(delta),len(t)]\n')
        R=0
        return R

    if iw != iDelta:
        print('Dimensions inconsistent!\nlen(delta)~=len(weights)\n')
        R=0
        return R

    # Exit if improper hyperparameters are entered.
    if inversion_model == 'L1' or inversion_model == 'Cauchy':
        if len(hyperparameters) != 2:
            print('Improper number of trade-off parameters\n')
            R=0
            return R

    if inversion_model == 'L2': # The code's default is L2 inversion.
        if len(hyperparameters) != 1:
            print('Improper number of trade-off parameters\n')
            R=0
            return R

    # Preallocate space in memory.
    R = np.zeros((ip,it),dtype=complex)
    Rfft = np.zeros((ip,iF),dtype=complex)
    A = np.zeros((iDelta,ip),dtype=complex)
    Tshift = A
    AtA = np.zeros((ip,ip),dtype=complex)
    AtM = np.zeros((ip,1),dtype=complex)
    Ident = identity(ip)

    # Define some values.
    Dist_array = delta-ref_dist
    dF = 1./(t[1]-t[2])
    Mfft = np.fft.fft(M,iF,1)
    W = spdiags(weights.T,0,iDelta,iDelta)

    dCOST=0
    COST_cur=0
    COST_prev=0

    # Populate ray parameter then distance data in time shift matrix.
    for j in range(iDelta):
        if line_model =='parabolic':
            Tshift[j,:]=p
        else: # Linear is default.
            Tshift[j,:]=p

    for k in range(ip):
        if line_model == 'parabolic':
            Tshift[:,k]=(2*ref_dist*Tshift[:,k]*Dist_array.T)+\
                    (Tshift[:,k]*(np.pow(Dist_array,2)).T)
        else: # Linear is default.
            Tshift[:,k]=Tshift[:,k]*Dist_array.T

    # Loop through each frequency.
    #for i in range(int(np.floor((iF+1)/2.))):
    for i in range(0,int(np.floor((iF+1)/2.))):
    #for i in range(0,3):
        # Make time-shift matrix, A.
        f=((i)/float(iF))*dF
        A=np.exp((2j*np.pi*f)*Tshift)
        # M = A R  --->  AtM = AtA R
        # Solve the weighted, L2 least-squares problem for an initial solution.
        #AtA=A.T*W*A
        dot = W.dot(A)
        AtA = np.flipud(np.dot(A.T,dot))
        AtM=np.dot(A.T,W.dot(Mfft[:,i-1]))[::-1]
        mu=np.abs(np.trace(AtA))*hyperparameters[0]
        d = AtA+mu*Ident
        Rfft[:,i] = solve(d,AtM)

        # Non-quadratic inversions use IRLS to solve, 
        # iterate until solution convergence.
        if inversion_model == 'Cauchy' or inversion_model == 'L1':

            # Initialize hyperparameters.
            b=hyperparameters[1]
            lamb=mu*b

            # Initialize cost functions.
            dCOST=inf
            if inversion_model == 'Cauchy':
                COST_prev=norm(Mfft[:,i-1]-A*Rfft[:,i-1],2)+\
                           lamb*np.sum(np.log(np.pow(np.abs(Rfft[:,i-1]),2)+b))
            elif inversion_model == 'L1':
                COST_prev=norm(Mfft[:,i-1]-A*Rfft[:,i-1],2)+\
                           lamb*norm(np.abs(Rfft[:,i-1])+b,1)
            iterat=1

            # Iterate until negligible change to cost function.
            while dCOST > 0.001 and iterat<20:

                # Setup inverse problem.
                if inversion_model == 'Cauchy':
                    Q=spdiags(1./(np.abs(np.pow(Rfft[:,i-1]),2)+b),0,ip,ip)
                elif inversion_model == 'L1':
                    Q=spdiags(1./(np.abs(Rfft[:,i-1])+b),0,ip,ip)

                Rfft[:,i]=(lamb*Q+AtA)/AtM

                # Determine change to cost function.
                if inversion_model == 'Cauchy':
                    COST_cur=norm(Mfft[:,i-1]-A*Rfft[:,i-1],2)+\
                             lamb*np.sum(log(np.abs(np.pow(Rfft[:,i-1]),2)+b)-\
                             np.log(b))
                elif inversion_model == 'L1':
                    COST_cur=norm(Mfft[:,i-1]-A*Rfft[:,i-1],2)+\
                           lamb*norm(np.abs(Rfft[:,i-1])+b,1)
                dCOST=2*np.abs(COST_cur-COST_prev)/\
                        (np.abs(COST_cur)+np.abs(COST_prev))
                COST_prev=COST_cur

                iterat=iterat+1

        # Assuming Hermitian symmetry of the fft make negative 
        # frequencies the complex conjugate of current solution.
        if i != 0:
            Rfft[:,iF-i]=np.conjugate(Rfft[:,i])

    R = np.fft.ifft(Rfft,iF,1)
    R=R[:,0:it]
    return R



