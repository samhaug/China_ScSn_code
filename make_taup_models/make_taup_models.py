#!/home/samhaug/anaconda2/bin/python

import numpy as np
from models_1d import write_prem_tvel
#depths = np.arange(200,1205,5)
depths = np.arange(50,1805,5)

for depth in depths:
   write_prem_tvel('prem.nd','prem{}.tvel'.format(depth),depth)
