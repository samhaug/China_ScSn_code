# China_ScSn_code

Workflow:

1. Use radon\_transform.py to create radon.h5 stream files. These are used for migration

2. Use extract\_data\_reverb.py to make a reverb.h5 files. This code needs a synthetic and data h5 stream file. It uses cross correlation to find the reverb intervals in the data.

3. Use deconvolve.py on each of the reverb.h5 files. This code needs to be run ffor synthetic and data. Name the output files synth\_deconvolve.h5 and data\_deconvolve.h5 as a convention.

Steps 4 and five can be done in any order, but they need to read a deconvolve.h5 file. I run them at the same time, one reading synth\_deconvolve.h5, the other reading data\_deconvolve.h5

4. Run make\_3dreflection\_lookup.py to make a lookup table of reflection points. This code needs a deconvolve.h5 file to make a lookup table for corresponding reverb intervals

5. Run make\_3d\_lookup.py to make a lookup table for the moveout corrections. This code needs a deconvolve.h5 file to make a lookup table for corresponding reverb intervals

6. grid\_3dsum.py takes both lookup tables, a deconvolve.h5 file, and the name of the output grid. Do this for both data and synthetic deconvolve files.

7. Use combine\_grid.py to combine grid.h5 files from grid\_3dsum.py for many different events.

