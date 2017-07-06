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

parser = argparse.ArgumentParser()
parser.add_argument('--pdsave', help='Save plots in pdijksta plot dir.', action='store_true')
parser.add_argument('--savefig', help='Save plots with specified name.')
parser.add_argument('--noshow', help='Do not call plt.show.', action='store_true')
parser.add_argument('--scrubbing', help='Use scrubbing dict', action='store_true')
args = parser.parse_args()

if args.scrubbing:
    moment = 'scrubbing'
    main_dict = du.load_dict('./scrubbing_dict_2017.pkl')
    plot_fmt = '.-'
else:
    moment = 'stop_squeeze'
    main_dict = large_hl_dict
    mask = np.logical_and(main_dict[moment]['n_bunches']['b1'] > 800, main_dict[moment]['n_bunches']['b2'] > 800)
    main_dict = mask_dict(main_dict,mask)
    plot_fmt = '.'


def legend(sp, bbox_to_anchor=(1,1), loc='upper left', **kwargs):
    sp.legend(bbox_to_anchor=bbox_to_anchor, loc=loc, **kwargs)

date_on_xaxis = True
filln_range = None # Tuple of min / max fill

fontsz = 12
markersize = 6
ms.mystyle_arial(fontsz=fontsz)#, dist_tick_lab=10)

# mask fill nrs
if filln_range is not None:
    mask = np.logical_and(main_dict['filln'] > filln_range[0], main_dict['filln'] < filln_range[1])
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

sp5 = plt.subplot(3,1,1, sharex=None)
sp1 = sp5
sp5.grid('on')
sp5.set_ylim(0,200)

sp6 = plt.subplot(3,1,2, sharex=sp1)
sp6.grid('on')
sp6.set_ylim(0, 6e-13)

sp_avg = plt.subplot(3,1,3, sharex=sp1)
sp_avg.grid('on')

sp5.set_title('Arc heat loads')
sp6.set_title('Normalized arc heat loads.')
sp_avg.set_title('Normalized arc heat loads - Delta to average')

fig3 = ms.figure('Intensity - heat load fit')

sp7 = plt.subplot(1,1,1)
sp7.grid('on')
sp7.set_ylim(0,350)
sp7.set_xlim(0,2.5)

zeros = []

average, divisor = 0, 0
for key in arc_list:
    hl = main_dict[moment]['heat_load']['arc_averages'][key]
    average += np.nan_to_num(hl)
    divisor += np.isfinite(hl)
average /= divisor

tot_int = main_dict[moment]['intensity']['total']
sp5.plot(x_axis, average, plot_fmt, label='Average', color='black', markersize=markersize)
sp6.plot(x_axis, average/tot_int, plot_fmt, label='Average', color='black', markersize=markersize)
sp_avg.plot(x_axis, np.zeros_like(average), plot_fmt, label='Average', color='black', markersize=markersize)

for arc_ctr, key in enumerate(arc_list):
    color = colorprog(arc_ctr, 8)
    arc_hl = main_dict[moment]['heat_load']['arc_averages'][key]

    sp5.plot(x_axis, arc_hl, plot_fmt, label=key, color=color, markersize=markersize)
    sp6.plot(x_axis, arc_hl/tot_int, plot_fmt, label=key, color=color, markersize=markersize)
    sp_avg.plot(x_axis, (arc_hl-average)/tot_int, plot_fmt, label=key, color=color, markersize=markersize)

    xx = tot_int/(main_dict[moment]['n_bunches']['b1']+main_dict[moment]['n_bunches']['b2'])/1e11
    yy = arc_hl - main_dict[moment]['heat_load']['total_model']*53.45
    fit = np.polyfit(xx,yy,1)
    yy_fit = np.poly1d(fit)
    xx_fit = np.arange(0.4, 2.5, 0.1)
    zeros.append(-fit[1]/fit[0])

    sp7.plot(xx, yy, plot_fmt, label=key, color=color, markersize=markersize)
    #sp7.plot(xx, main_dict[moment]['heat_load']['total_model']*53.45, plot_fmt, ls='--', color=color, markersize=markersize)
    sp7.plot(xx_fit, yy_fit(xx_fit), color=color, lw=3)
    if arc_ctr == 0:
        sp7.axhline(160, color='black', lw=3)

arc_average = average


#sp6.legend(bbox_to_anchor=(1.22,1.04))
legend(sp6)
sp5.set_ylabel('Heat load [W/hcell]')
sp6.set_ylabel('Norm. heat load [W/hcell/p+]')
sp_avg.set_ylabel('$\Delta$ norm. HL [W/hcell/p+]')
sp7.set_ylabel('Heat load [W/hcell]')
sp7.set_xlabel('Bunch intensity [1e11]')
legend(sp7)
plt.setp(sp5.get_xticklabels(), visible = False)

if date_on_xaxis:
    time_conv.set_x_for_plot(fig2, sp1)
else:
    sp6.set_xlabel('Fill nr')

# Quads
all_cells_dict = main_dict[moment]['heat_load']['all_cells']
quad_keys = du.q6_keys_list(main_dict)
def get_len(q6_str):
    q6_nr = int(q6_str[3])
    return HL.magnet_length['Q6s_IR%i' % q6_nr][0]
quad_lens = map(get_len, quad_keys)

fig4 = ms.figure('Quad heat loads')
sp5 = plt.subplot(3,1,1, sharex=sp1)
sp6 = plt.subplot(3,1,2, sharex=sp1)
sp_avg = plt.subplot(3,1,3, sharex=sp1)

sp5.set_title('Quad heat loads')
sp6.set_title('Normalized quad heat loads.')
sp_avg.set_title('Normalized quad heat loads - Delta to average')

sp5.set_ylabel('Quad heat loads [W/m]')
sp6.set_ylabel('Quad heat loads [W/m/p+]')
sp_avg.set_ylabel('Quad heat loads [W/m/p+]')

fig5 = ms.figure('Quad intensity fit')
sp7 = plt.subplot(1,1,1)
sp7.grid('on')

for sp in sp5, sp6, sp_avg:
    sp.grid(True)

average, divsior = 0,0
for key, len_ in zip(quad_keys, quad_lens):
    hl = all_cells_dict[key]/len_
    average += np.nan_to_num(hl)
    divsior += np.isfinite(hl)
average /= divisor

sp5.plot(x_axis, average, plot_fmt, label='Average', color='black', markersize=markersize)
sp6.plot(x_axis, average/tot_int, plot_fmt, label='Average', color='black', markersize=markersize)
sp_avg.plot(x_axis, np.zeros_like(average), plot_fmt, label='Average', color='black', markersize=markersize)

for ctr, (key, len_) in enumerate(zip(quad_keys, quad_lens)):
    color = colorprog(ctr, quad_keys)
    this_hl = all_cells_dict[key]/len_

    sp5.plot(x_axis, this_hl, plot_fmt, label=key, color=color, markersize=markersize)
    sp6.plot(x_axis, this_hl/tot_int, plot_fmt, label=key, color=color, markersize=markersize)
    sp_avg.plot(x_axis, (this_hl-average)/tot_int, plot_fmt, label=key, color=color, markersize=markersize)

    xx = tot_int/(main_dict[moment]['n_bunches']['b1']+main_dict[moment]['n_bunches']['b2'])/1e11
    yy = this_hl - main_dict[moment]['heat_load']['total_model']
    fit = np.polyfit(xx,yy,1)
    yy_fit = np.poly1d(fit)
    xx_fit = np.arange(0.4, 2.5, 0.1)
    zeros.append(-fit[1]/fit[0])

    sp7.plot(xx, yy, plot_fmt, label=key, color=color, markersize=markersize)
    #sp7.plot(xx, main_dict[moment]['heat_load']['total_model']*53.45, plot_fmt, ls='--', color=color, markersize=markersize)
    sp7.plot(xx_fit, yy_fit(xx_fit), color=color, lw=3)

plt.setp(sp5.get_xticklabels(), visible = False)
plt.setp(sp6.get_xticklabels(), visible = False)
legend(sp6)
legend(sp7)


for fig in [fig2, fig3, fig4, fig5]:
    fig.suptitle('At '+moment)
    fig.subplots_adjust(right=0.7, left=0.15)

if args.pdsave:
    sf.pdijksta(figs)
elif args.savefig:
    for num in plt.get_fignums():
        fig = plt.figure(num)
        plt.suptitle('')
        fig.subplots_adjust(right=0.85, wspace=0.75, hspace=.38, bottom=0.1)
        fig.savefig(os.path.expanduser(args.savefig) + '_%i.png' % num)

if not args.noshow:
    plt.show()

