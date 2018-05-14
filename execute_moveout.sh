#!/bin/bash

s_bin=/dept/geology/geo/home/tomo_project/Jeannot/China_ScSn_code

echo extract_data_reverb.py
python $s_bin'/extract_data_reverb.py' -s sts_T_radon.h5 -d st_T_radon.h5

echo deconvolve data
python $s_bin'/deconvolve.py' -f data_reverb.h5 -d data_deconvolve.h5
echo deconvolve synth
python $s_bin'/deconvolve.py' -f synth_reverb.h5 -d synth_deconvolve.h5

echo make_3dlookup.py
python $s_bin'/make_3dlookup.py' -f synth_deconvolve.h5
echo make_3dreflection_lookup.py
python $s_bin'/make_3dreflection_lookup.py' -f synth_deconvolve.h5

echo synth_grid
python $s_bin'/grid_3dsum.py' -d synth_deconvolve.h5 -l 3dmvt_lkup.h5 -r 3dreflection_points.h5 -g synth_grid.h5

echo data grid
python $s_bin'/grid_3dsum.py' -d data_deconvolve.h5 -l 3dmvt_lkup.h5 -r 3dreflection_points.h5 -g data_grid.h5

