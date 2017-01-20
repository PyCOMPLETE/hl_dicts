# hl_dicts
Excerpt of all the data stored for the lhc

This repository contains python dictionaries stored as pickles and tools to load and process them.
It relies on the LHCMeasurementTools repository.

- LHC_Heat_load_dict.py:
  - Loads the heat load dictionaries of 2016 and 2015 and combines them.

- dict_utils.py:
  - More general functions to merge and mask dictionaries.
 
- large_hl_dict_201[56].pkl:
  - Created by 025\_ script.
  
  Content:
  - Numpy arrays
  - Fill max energy
  - Fill number
  - Filling pattern
  - BPI (if possible)
  - At start_ramp, stop_squeeze, stable_beams and every hour after stable_beams (max 24)
    - Intensity: per beam and total
    - Heat loads : Impedance, SR, total Model, arcs, quads, bunch length, number of bunches
    - Filled with zeros after the end of the fill
