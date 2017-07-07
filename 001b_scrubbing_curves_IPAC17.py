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
