# This script is intended to give a sample of applications for the Radon
# transform.
import numpy as np
from matplotlib import pyplot as plt
import Radon

# Load variables.
t = np.genfromtxt('t.dat',delimiter=',')
Delta = np.genfromtxt('Delta.dat',delimiter=',')
M = np.genfromtxt('M.dat',delimiter=',')
indicies = np.genfromtxt('indicies.dat',delimiter=',')
# t        - time axis.
# Delta    - distance (offset) axis.
# M        - Amplitudes of phase arrivals.
# indicies - list of indicies relevent to the S670S phase.

# Define some variables for RT.
mu=[5e-2]
#P_axis=-1:0.01:1
P_axis=np.arange(-1,1.01,0.01)
delta=np.mean(Delta)

# Invert to Radon domain using unweighted L2 inversion, linear path
# functions and an average distance parameter.
plt.imshow(M,aspect='auto')
plt.colorbar()
plt.show()
R=Radon.Radon_inverse(t,Delta,M,P_axis,np.ones(Delta.size),\
                      delta,'Linear','L2',mu)

plt.imshow(R.real,aspect='auto')
plt.colorbar()
plt.show()
plt.imshow(R.imag,aspect='auto')
plt.colorbar()
plt.show()
# Mute all phases except the S670S arrival.
#R670=np.zeros(R.shape)
#R670[indicies]=1
#R670=R*R670
R670 = np.genfromtxt('R670_mask.dat',delimiter=',')
plt.imshow(R670,aspect='auto')
plt.colorbar()
plt.show()

# Apply forward operator to the muted Radon domain.
start = np.floor(np.min(Delta))
stride = int((np.ceil(np.max(Delta))-np.floor(np.min(Delta)))/20.)
end = np.ceil(np.max(Delta))
Delta_resampled = np.arange(start,end+stride,stride)
M670 = Radon.Radon_forward(t,P_axis,R670,Delta_resampled,delta,'Linear')
plt.imshow(M670.real,aspect='auto')
plt.colorbar()
plt.show()

plt.imshow(M670.imag,aspect='auto')
plt.colorbar()
plt.show()

# Plot figures.
#figure(2); clf;

#subplot(221); imagesc(t,Delta,M);
#title('Aligned SS'); xlabel('Time (s)'); ylabel('Distance (deg)');

#subplot(223); imagesc(t, P_axis,  abs(hilbert(R'))');
#title('L2 Radon Inversion (Instantaneous Amplitude)'); ylabel('Ray Parameter (s/deg)'); xlabel('Time (s)');

#subplot(224); imagesc(t, P_axis,  abs(hilbert(R670'))');
#title('Muted Radon Domain (Instantaneous Amplitude)'); ylabel('Ray Parameter (s/deg)'); xlabel('Time (s)');

#subplot(222); imagesc(t,Delta_resampled, M670);
#title('S670S Seismic Energy'); xlabel('Time (s)'); ylabel('Distance (deg)');

