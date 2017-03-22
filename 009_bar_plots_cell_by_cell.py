import numpy as np
import matplotlib.pyplot as plt
import argparse

import dict_utils as du
from LHC_Heat_load_dict import main_dict

import LHCMeasurementTools.mystyle as ms
import LHCMeasurementTools.savefig as sf

parser = argparse.ArgumentParser()
parser.add_argument('--savefig', help='Save in pdijkstadir.', action='store_true')
args = parser.parse_args()

ms.mystyle()

plt.close('all')
moment ='stop_squeeze'

fills = [5219, 5222, 5223]

mask = np.array(map(lambda x: x in fills, main_dict['filln']), bool)

main_dict = du.mask_dict(main_dict, mask)
cell_dict = main_dict[moment]['heat_load']['all_cells']
hl_model = main_dict[moment]['heat_load']['total_model']
hl_sr = main_dict[moment]['heat_load']['sr']['total']*53.45
hl_imp = main_dict[moment]['heat_load']['imp']['total']*53.45

for ctr, (arc, cells) in enumerate(sorted(du.arc_cells_dict.iteritems())):
    sp_ctr = ctr%2 + 1
    if sp_ctr == 1:
        fig = ms.figure('At %s' % (moment))
    sp = plt.subplot(2,1,sp_ctr)
    sp.set_ylabel('Heat load [W/hcell]')
    sp.set_title(arc.replace('_',' '))
    sp.grid(True)

    xx = []
    xx_labels = []
    xx_ctr = 1
    for cell_ctr, cell in enumerate(cells):
        hl_cell_fills = cell_dict[cell] - hl_sr - hl_imp
        xx.append(xx_ctr+len(fills)/2.)
        xx_labels.append(cell[:4])
        for fill_ctr, filln in enumerate(fills):
            color = ms.colorprog(fill_ctr, fills)

            label, label_i, label_s = None, None, None
            if cell_ctr == 0:
                label = filln
                if fill_ctr == 0:
                    label_i, label_s = 'Imp.', 'SR'

            hl_cell_fill = hl_cell_fills[fill_ctr]
            sp.bar(xx_ctr, hl_sr[fill_ctr], color='0.5', label=label_s, bottom=0)
            sp.bar(xx_ctr, hl_imp[fill_ctr], color='green', alpha=0.5, label=label_i, bottom=hl_sr[fill_ctr])
            sp.bar(xx_ctr, hl_cell_fill, color=color, label=label, bottom=hl_sr[fill_ctr]+hl_imp[fill_ctr])
            xx_ctr += 1
        xx_ctr += 1

    sp.legend(loc=1)
    sp.set_xticks(xx)
    sp.set_xticklabels(xx_labels, fontsize=10)
    sp.set_xlim(0, xx_ctr)
    sp.set_ylim(0,250)

if args.savefig:
    fact = 3
    sf.saveall_pdijksta(figsize=(10*fact,5*fact))

plt.show()
