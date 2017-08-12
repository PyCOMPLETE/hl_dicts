from __future__ import print_function, division

import os
import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker
import numpy as np
import argparse

import LHCMeasurementTools.mystyle as ms
import LHCMeasurementTools.savefig as sf
from LHCMeasurementTools.mystyle import colorprog
import LHCMeasurementTools.TimestampHelpers as TH
import LHCMeasurementTools.LHC_Heatloads as HL
from LHC_Heat_load_dict import mask_dict, main_dict
import dict_utils as du
import LHC_Heat_load_dict as LHD
pl = plt

from blacklists import device_blacklist


plt.close('all')


moment = 'scrubbing'
main_dict = du.load_dict('./scrubbing_dict_2017.pkl')
LHD.replace_full_hldict_with_ldb_naming(main_dict, use_dP=False)


parser = argparse.ArgumentParser()
parser.add_argument('--varlist', help='Variable lists to plot. Choose from %s' % sorted(HL.heat_loads_plot_sets.keys()), 
    default='AVG_ARC')
parser.add_argument('--full-varname-in-legend', help='Do not shorten varnames.', action='store_true')
parser.add_argument('--filln-on-x', help='Plot vs fill number.', action='store_true')
parser.add_argument('--ignore-device-blacklist', help='Use pressure drop for recalculated data.', action='store_true')
parser.add_argument('--colormap', help='chose between hsv and rainbow', default='hsv')




args = parser.parse_args()

plot_fmt = '.-'

def legend(sp, bbox_to_anchor=(1,1), loc='upper left', **kwargs):
    sp.legend(bbox_to_anchor=bbox_to_anchor, loc=loc, **kwargs)

date_on_xaxis = False
filln_range = None # Tuple of min / max fill

fontsz = 16
markersize = 10
linewidth = 3
ms.mystyle_arial(fontsz=fontsz, dist_tick_lab=5)

# mask fill nrs
#remove very first injection test
mask = main_dict['filln'] > 5720
main_dict = mask_dict(main_dict,mask)


# load default plot sets
group_name = args.varlist
dict_hl_groups = HL.heat_loads_plot_sets
varnames = dict_hl_groups[group_name]

# Prepare figure and subplots
fig_h = pl.figure(1, figsize=(8*2, 6*1.4))
fig_h.patch.set_facecolor('w')
spint = pl.subplot2grid((10,2),(0,0), rowspan=4, colspan=1)
sp1 = spint
spnorm = pl.subplot2grid((10,2),(5,0), rowspan=5, colspan=1, sharex=sp1)
sphlcell = pl.subplot2grid((10,2),(0,1), rowspan=4, colspan=1, sharex=sp1)
spinteg = pl.subplot2grid((10,2),(5,1), rowspan=5, colspan=1)
    
fig_offeset_h = pl.figure(100, figsize=(8, 6))
fig_offeset_h.patch.set_facecolor('w')
spoffs = pl.subplot(1,1,1, sharex=sp1)


# Plot vs allocated scrubbing time
t_start_prescrubbing_string = '2017_05_29 08:00:00'
t_start_prescrubbing = TH.localtime2unixstamp(t_start_prescrubbing_string)
t_start_scrubbing_string = '2017_06_06 08:00:00'
t_start_scrubbing = TH.localtime2unixstamp(t_start_scrubbing_string)

# Build scrubbing time axis
t_scrub = 0.*main_dict[moment]['t_stamps']
mask_prescrub = main_dict[moment]['t_stamps']<t_start_scrubbing
t_scrub[mask_prescrub] = main_dict[moment]['t_stamps'][mask_prescrub]-t_start_prescrubbing
t_scrub[~mask_prescrub] = main_dict[moment]['t_stamps'][~mask_prescrub]-t_start_scrubbing+24*3600

#~ if date_on_xaxis:
    #~ time_in = 'datetime'
    #~ t_plot_tick_h = None #'4weeks'
    #~ time_conv = TH.TimeConverter(time_in, t_plot_tick_h=t_plot_tick_h)
    #~ tc = time_conv.from_unix
    #~ x_axis = tc(main_dict[moment]['t_stamps'])
#~ else:
    #~ x_axis = main_dict['filln']

if args.filln_on_x:
    x_axis = main_dict['filln']
    x_axis_label = 'Fill number'
else:
    x_axis= t_scrub/3600/24. 
    x_axis_label = 'Scrubbing time [days]'


spint.plot(x_axis, main_dict[moment]['n_bunches']['b2'], '.r', markersize=markersize)
spint.plot(x_axis, main_dict[moment]['n_bunches']['b1'], '.b', markersize=markersize) 


zeros = []


tot_int = main_dict[moment]['intensity']['total']

max_norm = 0.
max_hl = 0.

for arc_ctr, key in enumerate(varnames):
    color = colorprog(arc_ctr, len(varnames), cm=args.colormap)
    this_hl = main_dict[moment]['heat_load']['ldb_naming'][key]
    
    if key in device_blacklist and not args.ignore_device_blacklist:
            continue

    # prepare label
    if args.full_varname_in_legend:
        label = key
    else:
        label = ''
        for st in key.split('.POSST')[0].split('_'):
            if 'QRL' in st or 'QBS' in st or 'AVG' in st or 'ARC' in st:
                pass
            else:
                label += st + ' '
        label = label[:-1]
    
    sphlcell.plot(x_axis, this_hl, plot_fmt, label=label, color=color, markersize=markersize, linewidth=linewidth)
    spnorm.plot(x_axis, this_hl/tot_int, plot_fmt, label=label, color=color, markersize=markersize, linewidth=linewidth)
    
    #~ sptscrub.plot(t_scrub/3600/24., this_hl/tot_int, plot_fmt, label=label, color=color, markersize=markersize, linewidth=linewidth)

    integ_hl_this = np.cumsum(main_dict['hl_integrated']['ldb_naming'][key])
    
    spinteg.plot(integ_hl_this, this_hl/tot_int, '.-', color=color, markersize=markersize, linewidth=linewidth)

    if np.max(this_hl/tot_int)>max_norm:
        max_norm = np.max(this_hl/tot_int)
    if np.max(this_hl)>max_hl:
        max_hl = np.max(this_hl)
        
    spoffs.plot(x_axis, main_dict['hl_subtracted_offset']['ldb_naming'][key], '.-', color=color, markersize=markersize, label=label, linewidth=linewidth)
    
if max_norm<10/1e14:
    max_norm = 10/1e14

if max_hl<20:
    max_hl=20
    
fig_h.subplots_adjust(hspace=.21, right=.8, top=.92, bottom=.10, left=.08, wspace=.24)
for sp in [spint, sphlcell, spinteg, spnorm]:
    sp.grid('on')
    sp.set_ylim(bottom=0)    

spinteg.set_ylabel('Normalized heat load [W/p+]')
spinteg.set_xlabel('Integrated heat load [J]')

spint.set_ylabel('Number of bunches')
spnorm.set_ylabel('Normalized heat load [W/p+]')
sphlcell.set_ylabel('Heat load [W]')

for sp in [spint, sphlcell, spnorm, spoffs]:
    sp.grid('on')
    sp.set_xlabel(x_axis_label)
    
sphlcell.legend(prop={'size':fontsz}, bbox_to_anchor=(1.05, 1.035),  loc='upper left')
spoffs.set_ylabel('Subtracted offset [W]')

spinteg.ticklabel_format(style='sci', scilimits=(0,0),axis='x')

#~ spnorm.set_ylim(0, max_norm*1.05)
#~ sphlcell.set_ylim(top=max_hl)
#~ spinteg.set_ylim(0, max_norm*1.05)
#~ spinteg.set_ylim(0, max_norm*1.05)

def save_evol(infolder='./'):
    strfile = 'scrubbing_run_heatload'
    fig_h.savefig(infolder+'/'+strfile+'_evol_'+fig_h._suptitle.get_text().replace(' ', '__')+'.png',  dpi=200)

def save_offset(infolder='./'):
    fig_offeset_h.savefig(infolder+'/'+'scrubbing_run_hloffset_'+fig_h._suptitle.get_text().replace(' ', '__')+'.png',  dpi=200)




fig_h.suptitle(group_name)

plt.show()

