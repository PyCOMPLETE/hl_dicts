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
from LHC_Heat_load_dict import mask_dict, main_dict as large_hl_dict, arc_list
import dict_utils as du

plt.close('all')



moment = 'scrubbing'
main_dict = du.load_dict('./scrubbing_dict_2017.pkl')
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


fig2 = ms.figure('Arc heat loads')

sp5 = plt.subplot(2,1,1, sharex=None)
sp1 = sp5
sp5.grid('on')
sp5.set_ylim(0,200)

sp6 = plt.subplot(2,1,2, sharex=sp1)
sp6.grid('on')
sp6.set_ylim(0, 6e-13)

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

average, divisor = 0, 0
for key in arc_list:
    hl = main_dict[moment]['heat_load']['arc_averages'][key]
    average += np.nan_to_num(hl)
    divisor += np.isfinite(hl)
average /= divisor

tot_int = main_dict[moment]['intensity']['total']
#~ #plot average
#~ sp5.plot(x_axis, average, plot_fmt, label='Average', color='black', markersize=markersize, linewidth=linewidth)
#~ sp6.plot(x_axis, average/tot_int, plot_fmt, label='Average', color='black', markersize=markersiz, linewidth=linewidth)

for arc_ctr, key in enumerate(arc_list):
    color = colorprog(arc_ctr, 8)
    arc_hl = main_dict[moment]['heat_load']['arc_averages'][key]
    
    #~ #insert interruption between pre-scrubbing and scrubbing
    #~ interr_after_fill = 5728
    #~ n_before = np.sum(main_dict['filln']<=interr_after_fill)
    #~ x_axis_cut = np.array(list(x_axis[:n_before])+[np.nan]+list(x_axis[n_before:]))
    #~ arc_hl_cut = np.array(list(arc_hl[:n_before])+[np.nan]+list(arc_hl[n_before:]))
    #~ tot_int_cut = np.array(list(tot_int[:n_before])+[np.nan]+list(tot_int[n_before:]))
    #~ sp5.plot(x_axis_cut, arc_hl_cut, plot_fmt, label=key, color=color, markersize=markersize, linewidth=linewidth)
    #~ sp6.plot(x_axis_cut, arc_hl_cut/tot_int_cut, plot_fmt, label=key, color=color, markersize=markersize, linewidth=linewidth)
    
    sp5.plot(x_axis, arc_hl, plot_fmt, label=key, color=color, markersize=markersize, linewidth=linewidth)
    sp6.plot(x_axis, arc_hl/tot_int, plot_fmt, label=key, color=color, markersize=markersize, linewidth=linewidth)
    
    sptscrub.plot(t_scrub/3600/24., arc_hl/tot_int, plot_fmt, label=key, color=color, markersize=markersize, linewidth=linewidth)

    integ_hl_this = np.cumsum(main_dict['hl_integrated']['arc_averages'][key])
    
    spinteg.plot(integ_hl_this, arc_hl/tot_int, '.-', color=color, markersize=markersize, linewidth=linewidth)
    
    



arc_average = average


#sp6.legend(bbox_to_anchor=(1.22,1.04))
legend(sp6)
sp5.set_ylabel('Heat load [W/hcell]')
sp6.set_ylabel('Norm. heat load [W/hcell/p+]')
plt.setp(sp5.get_xticklabels(), visible = False)

if date_on_xaxis:
    time_conv.set_x_for_plot(fig2, sp1)
else:
    sp6.set_xlabel('Fill nr')
    
spinteg.set_ylim(0, None)
spinteg.grid('on')
spinteg.set_ylabel('Norm. heat load [W/hcell/p+]')
spinteg.set_xlabel('Integrated heat load [J/hcell]') 
figinteg.subplots_adjust(bottom=.12)


sptscrub.set_ylim(0, None)
sptscrub.grid('on')
sptscrub.set_ylabel('Norm. heat load [W/hcell/p+]')
sptscrub.set_xlabel('Scrubbing time [days]') 
figtscrub.subplots_adjust(bottom=.12)




plt.show()

