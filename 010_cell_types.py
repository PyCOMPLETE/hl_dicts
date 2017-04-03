from __future__ import print_function, division
import operator
import argparse

import matplotlib.pyplot as plt
import numpy as np

import LHCMeasurementTools.mystyle as ms
import LHCMeasurementTools.savefig as sf

from LHC_Heat_load_dict import mask_dict, main_dict
import dict_utils as du
from info_on_half_cells import type_occurence_dict, type_list

try:
    from RcParams import init_pyplot
    init_pyplot()
except ImportError:
    ms.mystyle()

plt.close('all')

moment = 'stop_squeeze'
mask = np.logical_and(main_dict[moment]['n_bunches']['b1'] > 800, main_dict[moment]['n_bunches']['b2'] > 800)
main_dict = du.mask_dict(main_dict,mask)

hl_dict = main_dict[moment]['heat_load']['all_cells']

types = []

filln = main_dict['filln']
for ctr, type_ in enumerate(type_list):
    cells = type_occurence_dict[type_]['cells']

    sp_ctr = ctr % 4 + 1
    if sp_ctr == 1:
        fig = ms.figure('Cell type heat loads')
    sp = plt.subplot(4,1, sp_ctr)
    if sp_ctr == 4:
        sp.set_xlabel('Fill number')
    sp.set_ylabel('Heat loads')
    sp.set_title('Type %s with %i cells' % (type_, len(cells)))

    for arc, cell, cell_ctr in cells:
        arc = arc.replace('S', 'Arc_')
        key = du.arc_cells_dict[arc][cell_ctr]
        print((arc, key, cell, cell_ctr))

        sp.plot(main_dict['filln'], hl_dict[key], '.', markersize=12)

    sp.set_ylim(0,None)


plt.show()

