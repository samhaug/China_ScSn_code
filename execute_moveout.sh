#!/bin/bash

python extract_data_reverb.py -s sts_T_radon.h5 -d st_T_radon.h5

python deconvolve.py -f data_reverb.h5 -d data_deconvolve.h5
python deconvolve.py -f synth_reverb.h5 -d synth_deconvolve.h5

python make_3dlookup.py -f synth_deconvolve.h5
python make_3dreflection_lookup.py -f synth_deconvolve.h5

python grid_3dsum.py -d synth_deconvolve.h5 -l 3dmvt_lkup.h5 -r 3dreflection_points.h5 -g synth_grid.h5

python grid_3dsum.py -d data_deconvolve.h5 -l 3dmvt_lkup.h5 -r 3dreflection_points.h5 -g data_grid.h5

