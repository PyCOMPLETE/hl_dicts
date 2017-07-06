from __future__ import division
import os
import re
import argparse

import numpy as np
import matplotlib.pyplot as plt

import dict_utils as du

from LHC_Heat_load_dict import main_dict
from LHCMeasurementTools.mystyle import colorprog
import LHCMeasurementTools.mystyle as ms
import LHCMeasurementTools.savefig as sf
import LHCMeasurementTools.LHC_Heatloads as HL


parser = argparse.ArgumentParser()
parser.add_argument('--pdsave', help='Save plots in pdijksta plot dir.', action='store_true')
parser.add_argument('--savefig', help='Save plots with specified name.')
parser.add_argument('--noshow', help='Do not call plt.show.', action='store_true')
args = parser.parse_args()


x_label='Integrated HL [J]'
ms.mystyle_arial(18)
plt.rcParams['lines.markersize'] = 7
plt.close('all')
bbox_to_anchor=(1.4,1)
def legend(sp, bbox_to_anchor=(1,1), loc='upper left', **kwargs):
    sp.legend(bbox_to_anchor=bbox_to_anchor, loc=loc, **kwargs)

moment = 'stop_squeeze'
# remove 36b fills
mask = np.array(map(lambda s: not(s.endswith('_36')), main_dict['filling_pattern']))
main_dict = du.mask_dict(main_dict,mask)

# remove low intensity fills
mask = np.logical_and(main_dict[moment]['n_bunches']['b1'] > 800, main_dict[moment]['n_bunches']['b2'] > 800)
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
good_keys_list = [heat_load_dict[main_keys[0]].keys()]#, du.q6_keys_list(main_dict)]

int_dict = main_dict['hl_integrated']
sp = None
figs = []
#~ fig = ms.figure('Integrated heat load', figs)
#~ #fig.subplots_adjust(left=.06, right=.84, top=.93, hspace=.38, wspace=.42)

#~ for ctr, (good_keys,main_key, title, ylim) in enumerate(zip(good_keys_list, main_keys, title_list, ylim_list)):
    #~ this_dict = heat_load_dict[main_key]

    #~ sp = plt.subplot(2,1,ctr+1, sharex=sp)
    #~ if title == 'Arcs':
        #~ sp.set_ylabel('Integrated HL [J]')
    #~ else:
        #~ sp.set_ylabel('Norm. int. HL [J/m]')
    #~ sp.set_title(title)
    #~ sp.grid(True)

    #~ sp2 = sp.twinx()
    #~ sp2.set_ylabel('Normalized HL [W/p+]')
    #~ sp2.set_ylim(*ylim)
    #~ for key_ctr, (key, arr) in enumerate(this_dict.iteritems()):
        #~ if key not in good_keys:
            #~ continue

        #~ item = int_dict[main_key][key]
        #~ nan = np.isnan(item)
        #~ item[nan] = 0
        #~ color = colorprog(key_ctr,8)
        #~ sp.plot(main_dict['filln'], np.cumsum(item), label=key, color=color)
        #~ sp2.plot(main_dict['filln'], arr/main_dict[moment]['intensity']['total'], '.', color=color)
    #~ legend(sp)
#~ sp.set_xlabel('Fill #')

#~ fig = ms.figure('Integrated heat load 2', figs)
fig = plt.figure(1)
fig.set_facecolor('w')
#fig.subplots_adjust(left=.06, right=.84, top=.93, hspace=.38, wspace=.42)

# Arcs and Quads 
sp = None
ylim_list = [(0,None), (0, None)]
for ctr, (good_keys,main_key, title, ylim) in enumerate(zip(good_keys_list, main_keys, title_list, ylim_list)):# this loop is fake
    this_dict = heat_load_dict[main_key]

    sp = plt.subplot(1,1,1)
    if title == 'Arcs':
        sp.set_ylabel('Normalized heat load [W/hc/p+]')
        sp.set_xlabel(x_label)
    else:
        sp.set_ylabel('Normalized HL [W/p+/m]')
        sp.set_xlabel('Norm. Int. HL [J/m]')
        
    #sp.set_title(title)
    sp.grid(True)

    for key_ctr, (key, arr) in enumerate(sorted(this_dict.iteritems())):
        if key not in good_keys:
            continue
        item = int_dict[main_key][key]
        nan = np.isnan(item)
        item[nan] = 0

        if title == 'Arcs':
            len_ = 1.
        else:
            len_ = HL.magnet_length['Q6s_IR'+key[3]][0]


        year_change = np.sum(item[:index_2016])
        color = colorprog(key_ctr,8)
        norm_hl = this_dict[key]/main_dict[moment]['intensity']['total']

        if title == 'Q6 Quads':
            label = key[:4]
        else:
            label = key.replace('_',' ')
        sp.plot(np.cumsum(item)/len_, norm_hl/len_,'.', label=label, color=color)
        if key_ctr == 0:
            label = 'Begin of 2016'
        else:
            label = None
        #sp.axvline(year_change, color=color, lw=2, label=label)
    sp.legend(loc='upper right', prop={'size':18}, ncol=2)
    sp.set_ylim(*ylim)
    sp.set_xlim(0,None)
    
fig.subplots_adjust(bottom=.14)

#~ #Bins
#~ cell_dict = main_dict[moment]['heat_load']['all_cells']
#~ cell_int_dict = main_dict['hl_integrated']['all_cells']
#~ n_bins = 10

#~ cell_hls = []
#~ for cell, hl_arr in cell_dict.iteritems():
    #~ cell_hls.append((cell, np.mean(hl_arr[-10:])))

#~ cell_hls = filter(lambda x: x[1] > 0, cell_hls)
#~ cell_hls.sort(key=lambda x: x[1])
#~ min_hl, max_hl = cell_hls[0][1], cell_hls[-1][1]
#~ delta_hl = (max_hl - min_hl) / (n_bins -1)
#~ bins = [[]]
#~ bin_ = bins[0]
#~ for cell, hl in cell_hls:
    #~ if hl > min_hl + delta_hl:
        #~ min_hl += delta_hl
        #~ bin_ = []
        #~ bins.append(bin_)
    #~ bin_.append(cell)

#~ deciles = [[]]
#~ decil = deciles[0]
#~ max_ctr = 0 + len(cell_hls)/10.
#~ for ctr, (cell, _) in enumerate(cell_hls):
    #~ if ctr > max_ctr:
        #~ max_ctr += len(cell_hls)/10.
        #~ decil = []
        #~ deciles.append(decil)
    #~ decil.append(cell)

#~ if True:
    #~ title = 'Deciles'
    #~ bins = deciles
    #~ get_label = lambda x, y: '%i0%%' % (x+1)
    #~ legend_title = None
#~ else:
    #~ title = 'Bins'
    #~ get_label = lambda x, y: '%i cells' % len(y)
    #~ legend_title = 'Number of cells'


#~ sp = plt.subplot(2,2,3)
#~ sp.set_xlabel(x_label)
#~ sp.set_ylabel('Normalized HL [W/p+]')
#~ sp.set_title(title)
#~ sp.grid(True)

#~ tot_arr, tot_divisor = 0, 0
#~ tot_int_arr, tot_int_divisor = 0, 0
#~ for ctr, bin_ in enumerate(bins):
    #~ color = colorprog(ctr, bins)
    #~ label = get_label(ctr, bin_)
    #~ bin_arr, bin_divisor = 0, 0
    #~ bin_int_arr, bin_int_divisor = 0, 0
    #~ for cell in bin_:
        #~ bin_int_arr += np.nan_to_num(cell_int_dict[cell])
        #~ bin_int_divisor += np.isfinite(cell_int_dict[cell])
        #~ bin_arr += np.nan_to_num(cell_dict[cell])
        #~ bin_divisor += np.isfinite(cell_dict[cell])

    #~ tot_arr += bin_arr
    #~ tot_divisor += bin_divisor
    #~ tot_int_arr += bin_int_arr
    #~ tot_int_divisor += bin_int_divisor

    #~ bin_hl = bin_arr/bin_divisor
    #~ bin_int_hl = bin_int_arr / bin_int_divisor
    #~ int_hl = np.cumsum(bin_hl)

    #~ sp.plot(np.cumsum(bin_int_hl), bin_hl/tot_int, '.', color=color, label=label)

#~ tot_hl = tot_arr / tot_divisor
#~ tot_int_hl = tot_int_arr / tot_int_divisor
#~ sp.plot(np.cumsum(tot_int_hl), tot_hl/tot_int, '.', color='black', label='Average')

#~ legend(sp, title=legend_title)
#~ sp.set_xlim(0,None)


#~ # Special cells
#~ sp = plt.subplot(1,1,1)
#~ sp.set_xlabel(x_label)
#~ sp.set_ylabel('Normalized HL [W/p+]')
#~ sp.set_title('Special cell dipoles')
#~ sp.grid(True)

#~ special_dict = main_dict[moment]['heat_load']['special_cells']
#~ re_special_dipole = re.compile('^.*_D[234]$')
#~ special_dip_keys = filter(re_special_dipole.match, special_dict.keys())
#~ for ctr, key in enumerate(special_dip_keys):
    #~ if key in ('33L5_D4', '33L5_D3'): continue

    #~ norm_hl = special_dict[key] / tot_int
    #~ int_hl = int_dict['special_cells'][key]
    #~ color=ms.colorprog(ctr, special_dip_keys)
    #~ label = key.replace('_', ' ')
    #~ sp.plot(np.cumsum(int_hl), norm_hl, '.', label=key, color=color)

#~ sp.set_ylim(-0.1e-13,None)
#~ legend(sp)

#~ fig = ms.figure('Standalone D3 in LSS 45', figs)
#~ sp = plt.subplot(2,2,1)
#~ sp.set_xlabel(x_label)
#~ sp.set_ylabel('Normalized HL [W/p+]')
#~ sp.set_title('Standalone D3 in LSS 45')
#~ sp.grid(True)

#~ cells_dict = main_dict[moment]['heat_load']['all_cells']

#~ ctr = 0
#~ for key, hl in cells_dict.iteritems():
    #~ if key[:4] in ('05L4', '05R4') and not key.endswith('_2'):
        #~ label = key[:4]+'_standalone'
        #~ color = ['black', 'red'][ctr]
        #~ norm_hl = hl / tot_int
        #~ int_hl = int_dict['all_cells'][key]
        #~ if not np.all(np.isnan(hl)):
            #~ sp.plot(np.cumsum(int_hl), norm_hl, '.', label=label, color=color)
        #~ ctr += 1

if args.pdsave:
    sf.pdijksta(figs)
elif args.savefig:
    for num in plt.get_fignums():
        fig = plt.figure(num)
        plt.suptitle('')
        fig.subplots_adjust(right=0.85, wspace=0.75, hspace=.38)
        fig.savefig(os.path.expanduser(args.savefig) + '_%i.png' % num)

if not args.noshow:
    plt.show()
