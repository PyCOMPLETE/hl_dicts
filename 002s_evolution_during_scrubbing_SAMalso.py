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

plt.close('all')



moment = 'scrubbing'
main_dict = du.load_dict('./scrubbing_dict_2017.pkl')
LHD.replace_full_hldict_with_ldb_naming(main_dict, use_dP=False)


parser = argparse.ArgumentParser()
parser.add_argument('--varlist', help='Variable lists to plot. Choose from %s' % sorted(HL.heat_loads_plot_sets.keys()), 
    default='AVG_ARC')
parser.add_argument('--full-varname-in-legend', help='Do not shorten varnames.', action='store_true')
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

mask = main_dict['filln'] > 5720
main_dict = mask_dict(main_dict,mask)

if date_on_xaxis:
    time_in = 'datetime'
    t_plot_tick_h = None #'4weeks'
    time_conv = TH.TimeConverter(time_in, t_plot_tick_h=t_plot_tick_h)
    tc = time_conv.from_unix
    x_axis = tc(main_dict[moment]['t_stamps'])
else:
    x_axis = main_dict['filln']

# load default plot sets
group_name = args.varlist
dict_hl_groups = HL.heat_loads_plot_sets
varnames = dict_hl_groups[group_name]


fig2 = plt.figure(1, figsize=(8*1.2,6*1.2))
fig2.set_facecolor('w')
sp5 = plt.subplot(2,1,1, sharex=None)
sp1 = sp5
sp5.grid('on')
#sp5.set_ylim(0,200)

sp6 = plt.subplot(2,1,2, sharex=sp1)
sp6.grid('on')
#sp6.set_ylim(0, 6e-13)

#~ sp5.set_title('Arc heat loads')
#~ sp6.set_title('Normalized arc heat loads.')


# plot vs integrated heat load
figinteg = plt.figure(100)
spinteg = plt.subplot(111)
figinteg.set_facecolor('w')


#Plot vs allocated scrubbing time
t_start_prescrubbing_string = '2017_05_29 08:00:00'
t_start_prescrubbing = TH.localtime2unixstamp(t_start_prescrubbing_string)
t_start_scrubbing_string = '2017_06_06 08:00:00'
t_start_scrubbing = TH.localtime2unixstamp(t_start_scrubbing_string)

t_scrub = 0.*main_dict[moment]['t_stamps']
mask_prescrub = main_dict[moment]['t_stamps']<t_start_scrubbing
t_scrub[mask_prescrub] = main_dict[moment]['t_stamps'][mask_prescrub]-t_start_prescrubbing
t_scrub[~mask_prescrub] = main_dict[moment]['t_stamps'][~mask_prescrub]-t_start_scrubbing+24*3600

figtscrub = plt.figure(200)
sptscrub = plt.subplot(111)
figtscrub.set_facecolor('w')


zeros = []


tot_int = main_dict[moment]['intensity']['total']

max_norm = 0.
max_hl = 0.

for arc_ctr, key in enumerate(varnames):
    color = colorprog(arc_ctr, len(varnames))
    this_hl = main_dict[moment]['heat_load']['ldb_naming'][key]

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
        
    sp5.plot(x_axis, this_hl, plot_fmt, label=label, color=color, markersize=markersize, linewidth=linewidth)
    sp6.plot(x_axis, this_hl/tot_int, plot_fmt, label=label, color=color, markersize=markersize, linewidth=linewidth)
    
    sptscrub.plot(t_scrub/3600/24., this_hl/tot_int, plot_fmt, label=label, color=color, markersize=markersize, linewidth=linewidth)

    integ_hl_this = np.cumsum(main_dict['hl_integrated']['ldb_naming'][key])
    
    spinteg.plot(integ_hl_this, this_hl/tot_int, '.-', color=color, markersize=markersize, linewidth=linewidth)

    if np.max(this_hl/tot_int)>max_norm:
        max_norm = np.max(this_hl/tot_int)
    if np.max(this_hl)>max_hl:
        max_hl = np.max(this_hl)
    
if max_norm<10/1e14:
    max_norm = 10/1e14

if max_hl<20:
    max_hl=20

#sp6.legend(bbox_to_anchor=(1.22,1.04))
sp6.set_ylim(0, max_norm*1.05)
legend(sp6)
sp5.set_ylabel('Heat load [W]')
sp6.set_ylabel('Norm. heat load [W/p+]')
plt.setp(sp5.get_xticklabels(), visible = False)
sp5.set_ylim(top=max_hl)

if date_on_xaxis:
    time_conv.set_x_for_plot(fig2, sp1)
else:
    sp6.set_xlabel('Fill nr')
    
spinteg.set_ylim(0, max_norm*1.05)
spinteg.grid('on')
spinteg.set_ylabel('Norm. heat load [W/p+]')
spinteg.set_xlabel('Integrated heat load [J]')
spinteg.ticklabel_format(style='sci', scilimits=(0,0),axis='x') 
figinteg.subplots_adjust(bottom=.12)


sptscrub.set_ylim(0, max_norm*1.05)
sptscrub.grid('on')
sptscrub.set_ylabel('Norm. heat load [W/p+]')
sptscrub.set_xlabel('Scrubbing time [days]') 
figtscrub.subplots_adjust(bottom=.12)

fig2.subplots_adjust(right=.76)

for fig_h in [fig2, figinteg, figtscrub]:
     fig_h.suptitle(group_name)

plt.show()

