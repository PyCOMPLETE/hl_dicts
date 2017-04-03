import numpy as np
import matplotlib.pyplot as plt

import dict_utils as du
from LHC_Heat_load_dict import main_dict

import LHCMeasurementTools.mystyle as ms

plt.close('all')
ms.mystyle()
moment = 'stop_squeeze'

files_old = ['./large_heat_load_dict_2015_13.pkl', './large_heat_load_dict_2016_11.pkl']
dicts_old = map(du.load_dict, files_old)

old_dict = du.merge_dicts(*dicts_old)

fig = ms.figure('Comparison of versions 6 and 7')

sp_hl = plt.subplot(3,1,1)
sp_hl.set_ylabel('Heat load [W]')

sp_norm = plt.subplot(3,1,2, sharex=sp_hl)
sp_norm.set_ylabel('Heat load normalized [W/p+]')

sp_diff = plt.subplot(3,1,3, sharex=sp_hl)
sp_norm.set_ylabel('Delta_hl')


for dict_, title, marker in zip((main_dict, old_dict), ('v7', 'v6'), ('o', 'x')):

    mask = dict_[moment]['n_bunches']['b1'] > 400
    dict_ = du.mask_dict(dict_,mask)
    hl_dict = dict_[moment]['heat_load']['arc_averages']
    tot_int = dict_[moment]['intensity']['total']
    filln = dict_['filln']
    print(len(filln))

    for ctr, (arc, arr) in enumerate(sorted(hl_dict.items())):
        color = ms.colorprog(ctr, hl_dict)
        label=arc+' '+title
        sp_hl.plot(filln, arr, '.', color=color, label=label, markersize=6, marker=marker)
        sp_norm.plot(filln, arr/tot_int, '.', color=color, label=label, markersize=8, marker=marker)



hl_dict_main = main_dict[moment]['heat_load']['arc_averages']
hl_dict_old = old_dict[moment]['heat_load']['arc_averages']
delta_dict = du.operate_on_dicts(hl_dict_main, hl_dict_old, lambda x,y: x-y)

for key, arr in delta_dict.iteritems():
    if np.any(arr != hl_dict_main[key] - hl_dict_old[key]):
        print 'Wrong', key

#delta_dict = du.mask_dict(delta_dict, mask)



for ctr, (arc, arr) in enumerate(sorted(delta_dict.items())):
        color = ms.colorprog(ctr, delta_dict)
        label=arc
        sp_diff.plot(main_dict['filln'], arr, '.', color=color, label=label, markersize=6)



for sp in sp_hl, sp_norm:
    sp.set_xlabel('Fill Number')
    sp.grid(True)
sp_hl.legend(bbox_to_anchor=(1.1,1))

plt.show()
