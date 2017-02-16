import sys
import numpy as np
import matplotlib.pyplot as plt
import re

import dict_utils as du

from LHC_Heat_load_dict import main_dict
from LHCMeasurementTools.mystyle import colorprog

plt.rcParams['lines.markersize'] = 10
plt.close('all')

moment = 'stable_beams'
heat_load_dict = main_dict[moment]['heat_load']

first_fill_2016 = 4857
for ctr, fill in enumerate(main_dict['filln']):
    if fill > 4857:
        index_2016 = ctr
        break

title_list = ['Arcs', 'Q6 Quads']
ylim_list = [(0,1.5e-12), (0,3.5e-13)]
main_keys = ['arc_averages', 'all_cells']
good_keys_list = [heat_load_dict[main_keys[0]].keys(), du.q6_keys_list(main_dict)]

int_dict = main_dict['hl_integrated']
sp = None
fig = plt.figure(figsize = (8*1.5,6*1.5))
fig.set_facecolor('w')
fig.canvas.set_window_title('Integrated heat load')

for ctr, (good_keys,main_key, title, ylim) in enumerate(zip(good_keys_list, main_keys, title_list, ylim_list)):
    this_dict = heat_load_dict[main_key]

    sp = plt.subplot(2,1,ctr+1, sharex=sp)
    sp.set_title('Integrated heat load')
    sp.set_ylabel('Cumulated HL [J]')
    sp.set_title(title)
    sp.grid(True)

    sp2 = sp.twinx()
    sp2.set_ylabel('Normalized HL [W/p+]')
    sp2.set_ylim(*ylim)
    for key_ctr, (key, arr) in enumerate(this_dict.iteritems()):
        if key not in good_keys:
            continue
        item = int_dict[main_key][key]
        nan = np.isnan(item)
        item[nan] = 0
        color = colorprog(key_ctr,8)
        sp.plot(main_dict['filln'], np.cumsum(item), label=key, color=color)
        sp2.plot(main_dict['filln'], \
                arr/main_dict[moment]['intensity']['total'],\
                '.', color=color)
    sp.legend(bbox_to_anchor=(1.15,1))
sp.set_xlabel('Fill #')
fig.subplots_adjust(left=.06, right=.84, top=.93, hspace=.38, wspace=.42)

fig = plt.figure(figsize = (8*1.5,6*1.5))
fig.set_facecolor('w')
fig.canvas.set_window_title('Integrated heat load 2')

ylim_list = [(0,1e-12), (0, .5e-12)]
for ctr, (good_keys,main_key, title, ylim) in enumerate(zip(good_keys_list, main_keys, title_list, ylim_list)):
    this_dict = heat_load_dict[main_key]

    sp = plt.subplot(2,1,ctr+1)
    sp.set_title('Integrated heat load')
    sp.set_ylabel('Normalized HL [W/p+]')
    sp.set_title(title)
    sp.grid(True)

    for key_ctr, (key, arr) in enumerate(this_dict.iteritems()):
        if key not in good_keys:
            continue
        item = int_dict[main_key][key]
        nan = np.isnan(item)
        item[nan] = 0

        year_change = np.sum(item[:index_2016])
        color = colorprog(key_ctr,8)
        norm_hl = this_dict[key]/main_dict[moment]['intensity']['total']
        sp.plot(np.cumsum(item), norm_hl,'.', label=key, color=color)
        if key_ctr == 0:
            label = 'Begin of 2016'
        else:
            label = None
        sp.axvline(year_change, color=color, lw=2, label=label)
    sp.legend(bbox_to_anchor=(1.15,1))
    sp.set_ylim(*ylim)
    sp.set_xlim(0,None)
sp.set_xlabel('Cumulated HL [J]')

fig.subplots_adjust(left=.06, right=.84, top=.93, hspace=.38, wspace=.42)
plt.show()
