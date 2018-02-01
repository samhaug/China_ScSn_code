# China_ScSn_code

#1D workflow#
make\_lookup.py makes an h5 lookup table for a specific event depth. You must make a separate lookup table for each event. Station information is not
necessary.

extract\_reverb.py needs a filtered and processed h5 stream. It creates an h5 file
of clipped reverberative intervals.

deconvolve.py reads the h5 file made by extract reverb and deconvolves the parent phase from the reverberative interval. It saves the deconvolved traces as an h5 file.

make\_reflection\_points.py makes an h5 lookup table of reflection coordinates
using the output of deconvolve.py

moveout\_correction.py reads the lookup table and the deconvolved h5 file and performs the moveout correction into depth domain. Then writes to another h5 file.

#3D workflow#
make\_3dlookup.py will make a moveout lookup table for a 3D tomographic model

extract\_3dreverb.py will use the 3d lookup table to clip reverberative 
intervals from data. 

Use deconvolve.py the same as in the 1D workflow

moveout\_3dcorrection.py uses the 3d lookup table to perform the moveout 
correction


