from __future__ import division
import re
import argparse

import numpy as np
import matplotlib.pyplot as plt

import dict_utils as du

from LHC_Heat_load_dict import main_dict
from LHCMeasurementTools.mystyle import colorprog
import LHCMeasurementTools.mystyle as ms
import LHCMeasurementTools.savefig as sf


parser = argparse.ArgumentParser()
parser.add_argument('--pdsave', help='Save plots in pdijksta plot dir.', action='store_true')
args = parser.parse_args()


ms.mystyle()
plt.rcParams['lines.markersize'] = 10
plt.close('all')
bbox_to_anchor=(1.3,1)

moment = 'stable_beams'
# remove 36b fills
mask = np.array(map(lambda s: not(s.endswith('_36')), main_dict['filling_pattern']))
main_dict = du.mask_dict(main_dict,mask)

# remove low intensity fills
mask = main_dict[moment]['n_bunches']['b1'] > 400
main_dict = du.mask_dict(main_dict,mask)

heat_load_dict = main_dict[moment]['heat_load']
tot_int = main_dict[moment]['intensity']['total']

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
figs = []
fig = ms.figure('Integrated heat load', figs)
fig.subplots_adjust(left=.06, right=.84, top=.93, hspace=.38, wspace=.42)

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
        sp2.plot(main_dict['filln'], arr/main_dict[moment]['intensity']['total'], '.', color=color)
    sp.legend(bbox_to_anchor=bbox_to_anchor)
sp.set_xlabel('Fill #')

fig = ms.figure('Integrated heat load 2', figs)
fig.subplots_adjust(left=.06, right=.84, top=.93, hspace=.38, wspace=.42)

sp = None
ylim_list = [(0,None), (0, 1e-12)]
for ctr, (good_keys,main_key, title, ylim) in enumerate(zip(good_keys_list, main_keys, title_list, ylim_list)):
    this_dict = heat_load_dict[main_key]

    sp = plt.subplot(2,2,ctr+1, sharex=sp)
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
        #sp.axvline(year_change, color=color, lw=2, label=label)
    sp.legend(bbox_to_anchor=bbox_to_anchor)
    sp.set_ylim(*ylim)
    sp.set_xlim(0,None)
sp.set_xlabel('Cumulated HL [J]')

#Bins
cell_dict = main_dict[moment]['heat_load']['all_cells']
cell_int_dict = main_dict['hl_integrated']['all_cells']
n_bins = 10

cell_hls = []
for cell, hl_arr in cell_dict.iteritems():
    cell_hls.append((cell, np.mean(hl_arr[-10:])))

cell_hls = filter(lambda x: x[1] > 0, cell_hls)
cell_hls.sort(key=lambda x: x[1])
min_hl, max_hl = cell_hls[0][1], cell_hls[-1][1]
delta_hl = (max_hl - min_hl) / (n_bins -1)
bins = [[]]
bin_ = bins[0]
for cell, hl in cell_hls:
    if hl > min_hl + delta_hl:
        min_hl += delta_hl
        bin_ = []
        bins.append(bin_)
    bin_.append(cell)

sp = plt.subplot(2,2,3, sharex=sp)
sp.set_xlabel('Integrated heat load ')
sp.set_ylabel('Normalized HL [W/p+]')
sp.set_title('Bins')
sp.grid(True)

tot_arr, tot_divisor = 0, 0
tot_int_arr, tot_int_divisor = 0, 0
for ctr, bin_ in enumerate(bins):
    color = colorprog(ctr, bins)
    label = '%i cells' % len(bin_)
    bin_arr, bin_divisor = 0, 0
    bin_int_arr, bin_int_divisor = 0, 0
    for cell in bin_:
        bin_int_arr += np.nan_to_num(cell_int_dict[cell])
        bin_int_divisor += np.isfinite(cell_int_dict[cell])
        bin_arr += np.nan_to_num(cell_dict[cell])
        bin_divisor += np.isfinite(cell_dict[cell])

    tot_arr += bin_arr
    tot_divisor += bin_divisor
    tot_int_arr += bin_int_arr
    tot_int_divisor += bin_int_divisor

    bin_hl = bin_arr/bin_divisor
    bin_int_hl = bin_int_arr / bin_int_divisor
    int_hl = np.cumsum(bin_hl)

    sp.plot(np.cumsum(bin_int_hl), bin_hl/tot_int, '.', color=color, label=label)

tot_hl = tot_arr / tot_divisor
tot_int_hl = tot_int_arr / tot_int_divisor
sp.plot(np.cumsum(tot_int_hl), tot_hl/tot_int, '.', color='black', label='Average')

sp.legend(bbox_to_anchor=bbox_to_anchor)
sp.set_xlim(0,None)


sp = plt.subplot(2,2,4)
sp.set_xlabel('Integrated heat load ')
sp.set_ylabel('Normalized HL [W/p+]')
sp.set_title('Special cell dipoles')
sp.grid(True)

special_dict = main_dict[moment]['heat_load']['special_cells']
re_special_dipole = re.compile('^.*_D[234]$')
special_dip_keys = filter(re_special_dipole.match, special_dict.keys())
for ctr, key in enumerate(special_dip_keys):
    if key in ('33L5_D4', '33L5_D3'): continue

    norm_hl = special_dict[key] / tot_int
    int_hl = int_dict['special_cells'][key]
    color=ms.colorprog(ctr, special_dip_keys)
    sp.plot(np.cumsum(int_hl), norm_hl, '.', label=key, color=color)

sp.set_ylim(-0.1e-13,None)
sp.legend(bbox_to_anchor=bbox_to_anchor)

fig = ms.figure('Standalone D3 in LSS 45', figs)
sp = plt.subplot(2,2,1)
sp.set_xlabel('Integrated heat load ')
sp.set_ylabel('Normalized HL [W/p+]')
sp.set_title('Standalone D3 in LSS 45')
sp.grid(True)

cells_dict = main_dict[moment]['heat_load']['all_cells']

ctr = 0
for key, hl in cells_dict.iteritems():
    if key[:4] in ('05L4', '05R4') and not key.endswith('_2'):
        label = key[:4]+'_standalone'
        color = ['black', 'red'][ctr]
        norm_hl = hl / tot_int
        int_hl = int_dict['all_cells'][key]
        if not np.all(np.isnan(hl)):
            sp.plot(np.cumsum(int_hl), norm_hl, '.', label=label, color=color)
        ctr += 1

if args.pdsave:
    sf.pdijksta(figs)

plt.show()
