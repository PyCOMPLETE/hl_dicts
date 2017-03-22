import matplotlib.pyplot as plt
import numpy as np

from LHC_Heat_load_dict import main_dict
import dict_utils as du

from LHCMeasurementTools import mystyle as ms
from LHCMeasurementTools import savefig as sf

plt.close('all')
ms.mystyle()

moment = 'stop_squeeze'

filln = main_dict['filln']
hl_dict_pd = main_dict[moment]['heat_load']['arc_averages']
hl_dict_no_dp = main_dict[moment]['heat_load']['arc_averages_no_dP']

fig = ms.figure('Effect of pressure drop')

sp = plt.subplot(3,1,1)
sp.grid(True)
sp.set_ylabel('Heat Load [W/hc]')
sp.set_xlabel('Fill number')

sp2 = plt.subplot(3,1,2)
sp2.grid(True)
sp2.set_ylabel('Heat Load [W/hc]')
sp2.set_xlabel('Fill number')

for ctr, key in enumerate(hl_dict_pd):
    hl_dp = hl_dict_pd[key]
    hl_no_dp = hl_dict_no_dp[key]
    color = ms.colorprog(ctr, hl_dict_pd)

    sp.plot(filln, hl_dp,'.', label=key, color=color)
    if ctr == 0:
        label = 'no_dP'
    else:
        label = None
    sp.plot(filln, hl_no_dp,'x', label=label, color=color)

    sp2.plot(filln, hl_dp - hl_no_dp, '.', label=key, color=color)

sp.legend(bbox_to_anchor=(1.1,1))

diff_dict = du.operate_on_dicts(hl_dict_pd, hl_dict_no_dp, lambda x, y: x - y)

hl_dict_pd = main_dict[moment]['heat_load']['all_cells']
hl_dict_no_dp = main_dict[moment]['heat_load']['all_cells_no_dP']

filln = 5219
index = np.argwhere(main_dict['filln'] == filln)
for ctr, (arc, cells) in enumerate(du.arc_cells_dict.iteritems()):
    sp_ctr = ctr % 4 + 1
    if sp_ctr % 4 == 1:
        fig = ms.figure('Effect of pressure drop cell by cell for Fill %i' % filln)
        fig.subplots_adjust(hspace=0.34)
    sp = plt.subplot(4,1,sp_ctr)
    sp.set_title(arc)
    sp.set_ylabel('Heat load [W/hc]')
    sp.set_xlabel('Cell')
    xlabels, xticks = [], []
    for cell_ctr, cell in enumerate(cells):
        hl  = hl_dict_pd[cell][index]
        hl2 = hl_dict_no_dp[cell][index]

        if cell_ctr == 0:
            label1, label2 = 'With dP', 'Without dP'
        else:
            label1, label2 = None, None

        sp.bar(3*cell_ctr, hl, color='red', label=label1)
        sp.bar(3*cell_ctr+1, hl2, color='blue', label=label2)
        xlabels.append(cell[:4])
        xticks.append(3*cell_ctr+1)
    sp.set_xticks(xticks)
    sp.set_xticklabels(xlabels, fontsize=10)

    if sp_ctr == 1:
        sp.legend(bbox_to_anchor=(1.1,1))

plt.show()
