#!/bin/bash

s_bin=/dept/geology/geo/home/tomo_project/Jeannot/China_ScSn_code/
depth=$1

#echo equate_moveout
python $s_bin'equate_metadata.py'

#echo extract_data_reverb.py
python $s_bin'extract_data_reverb.py' -s sts_T_radon.h5 -d st_T_radon.h5

#echo deconvolve data
python $s_bin'/deconvolve.py' -f data_reverb.h5 -d data_deconvolve.h5

python ../China_ScSn_code/grid_1dsum.py -d data_deconvolve.h5 -r ../h5_lookups/pierce_"$depth".h5 -t ../h5_lookups/times_"$depth".h5 -g data_1dgrid.h5
