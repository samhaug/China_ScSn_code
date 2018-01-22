import numpy as np
from seis_tools.models.models_1d import write_prem_tvel
#depths = np.arange(200,1205,5)
depths = np.arange(50,1205,5)

for depth in depths:
   write_prem_tvel('/geo/home/romaguir/seis_tools/models/model_files_1d/prem.nd','prem{}.tvel'.format(depth),depth)
