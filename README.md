# China_ScSn_code

make_lookup.py makes an h5 lookup table for a specific event depth. You must
make a separate lookup table for each event. Station information is not
necessaray.

Extract reverb needs a filtered and processed h5 stream. It creates an h5 file
 of clipped reverberative intervals.

 Deconvolve reads the h5 file made by extract reverb and deconvolves the parent
 phase from the reverberative interval. It saves the deconvolved traces as an
 h5 file.

moveout_correction.py reads the lookup table and the deconvolved h5 file 
and performs the moveout correction into depth domain. Then writes to another h5 file.
