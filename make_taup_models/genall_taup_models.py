import numpy as np
from obspy.taup.taup_create import build_taup_model
depths = np.arange(50,1205,5)

for depth in depths:
   build_taup_model('prem{}.tvel'.format(depth))
