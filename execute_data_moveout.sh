#!/bin/bash

s_bin=/dept/geology/geo/home/tomo_project/Jeannot/China_ScSn_code/

#echo equate_moveout
#python $s_bin'equate_metadata.py'

#echo extract_data_reverb.py
#python $s_bin'extract_data_reverb.py' -s sts_T_radon.h5 -d st_T_radon.h5

#echo deconvolve data
#python $s_bin'/deconvolve.py' -f data_reverb.h5 -d data_deconvolve.h5

#echo make_3dlookup.py
#python $s_bin'/make_3dlookup.py' -f data_deconvolve.h5 

echo make_3dreflection_lookup.py
python $s_bin'/make_3dreflection_lookup.py' -f data_deconvolve.h5 

echo data grid
python $s_bin'/grid_3dsum.py' -d data_deconvolve.h5 -l 3dmvt_lkup.h5 -r 3dreflection_points.h5 -g data_grid.h5 

