from __future__ import print_function, division
import operator
import argparse
import os

import matplotlib.pyplot as plt
import numpy as np

import LHCMeasurementTools.mystyle as ms
import LHCMeasurementTools.savefig as sf
import LHC_Heat_load_dict as LHd

import dict_utils as du

large_hl_dict = LHd.get_full_heatload_dictionary()

parser = argparse.ArgumentParser()
parser.add_argument('--pdsave', help='Save plots in pdijksta plot dir.', action='store_true')
parser.add_argument('--savefig', help='Save plots with specified name.')
parser.add_argument('--noshow', help='Do not call plt.show.', action='store_true')
parser.add_argument('--scrubbing', help='Use scrubbing dict', action='store_true')
parser.add_argument('--celltypes', action='store_true')
parser.add_argument('--diffene', help='Plot difference between injection and high energy', action='store_true')
args = parser.parse_args()

ms.mystyle(12)
plt.rcParams['lines.markersize'] = 7

plt.close('all')

if args.scrubbing:
    moment = 'scrubbing'
    main_dict = du.load_dict('./scrubbing_dict_2017.pkl')
    plot_fmt = '.-'
else:
    moment = 'stop_squeeze'
    main_dict = large_hl_dict
    mask = np.logical_and(main_dict[moment]['n_bunches']['b1'] > 800, main_dict[moment]['n_bunches']['b2'] > 800)
    main_dict = du.mask_dict(main_dict,mask)
    plot_fmt = '.'

x_axis = main_dict['filln']
tot_int = main_dict[moment]['intensity']['total']


# general plotting function
figures = []
def hl_normalized_delta(input_arrays, average, title, labels, suptitle=False, legend_title=None):
    figures.append(ms.figure(title, figures))
    if suptitle:
        plt.suptitle(suptitle)
    sp5 = plt.subplot(3,1,1)
    sp6 = plt.subplot(3,1,2, sharex=sp5)
    sp_avg = plt.subplot(3,1,3, sharex=sp5)
    sp5.set_ylabel('Cell heat loads [W/hc]')
    sp6.set_ylabel('Cell heat loads [W/hc/p+]')
    sp_avg.set_ylabel('Cell heat loads [W/hc/p+]')
    sp_avg.set_xlabel('Fill number')
    sp5.grid(True)
    sp6.grid(True)
    sp_avg.grid(True)

    sp5.set_title('Heat loads')
    sp6.set_title('Normalized by intensity')
    sp_avg.set_title('Delta to average')

    for ctr, (arr, label) in enumerate(zip(input_arrays, labels)):
        color = ms.colorprog(ctr, input_arrays)
        sp5.plot(x_axis, arr, plot_fmt, color=color)
        sp6.plot(x_axis, arr/tot_int, plot_fmt, color=color, label=label)
        sp_avg.plot(x_axis, (arr-average)/tot_int, plot_fmt, color=color)

    sp5.plot(x_axis, average,plot_fmt, color='black')
    sp6.plot(x_axis, average/tot_int,plot_fmt, color='black', label='Average')
    sp_avg.plot(x_axis, np.zeros_like(average),plot_fmt, color='black')

    plt.setp(sp5.get_xticklabels(), visible = False)
    plt.setp(sp6.get_xticklabels(), visible = False)
    sp6.legend(bbox_to_anchor=(1, 1), loc='upper left', title=legend_title)
    return sp5, sp6, sp_avg


recalc_dict = main_dict[moment]['heat_load']['all_cells']
n_bins = 10+1

arc_cell_hls0 = []
for arc, cell_list in du.arc_cells_dict.iteritems():
    for cell in cell_list:
        hl_arr = recalc_dict[cell]
        arc_cell_hls0.append((arc, cell, np.mean(hl_arr[-10:])))

arc_cell_hls = filter(lambda x: x[2] > 0, arc_cell_hls0)
arc_cell_hls.sort(key=operator.itemgetter(2))

complete_hl = np.zeros((len(hl_arr), len(arc_cell_hls)), float)
for ctr, (arc, cell, _) in enumerate(arc_cell_hls):
    complete_hl[:,ctr] = recalc_dict[cell]
cell_average = np.nanmean(complete_hl, axis=1)

indices = map(int, np.linspace(0, len(arc_cell_hls), n_bins))

binned_arrays = []
labels = []
binned_cells = [[]]
for ctr in xrange(len(indices)-1):
    arr = 0
    start, stop = indices[ctr:ctr+2]
    divisor = 0
    cells = []
    for ctr2 in xrange(start, stop):
        arc, cell, _ = arc_cell_hls[ctr2]
        this_hl = recalc_dict[cell]
        divisor += np.array(np.isfinite(this_hl), int)
        arr += np.nan_to_num(this_hl)
        cells.append((arc,cell))
    binned_cells.append(cells)
    arr /= divisor
    binned_arrays.append(arr)
    labels.append('%i0%%' %(ctr+1))

hl_normalized_delta(binned_arrays, cell_average, 'All cells at %s' % moment, labels, legend_title='HL ranking')

selected, labels = [], []
for i in xrange(0,len(arc_cell_hls), 50):
    arc, cell, _ = arc_cell_hls[i]
    selected.append(recalc_dict[cell])
    labels.append(cell)


hl_normalized_delta(selected, cell_average, 'Selected cells at %s' % moment, labels)

min_hl, max_hl = arc_cell_hls[0][2], arc_cell_hls[-1][2]

# Bins
delta_hl = (max_hl-min_hl) / (n_bins-2)
bins = []
ref_hl = min_hl
for arc, cell, hl in arc_cell_hls:
    if hl == min_hl or hl > ref_hl:
        bin_ = []
        bins.append(bin_)
        ref_hl += delta_hl
    bin_.append((arc,cell))


if not args.scrubbing and args.diffene:

    dict_stop_squeeze   = main_dict['stop_squeeze']['heat_load']['all_cells']
    dict_start_ramp     = main_dict['start_ramp']['heat_load']['all_cells']
    dict_diff           = du.operate_on_dicts(dict_stop_squeeze, dict_start_ramp, operator.sub)

    titles = ('At stop_squeeze', 'At start ramp', 'Difference after ramp')

    # Arcs
    arcs = []
    for arc, cells in sorted(du.arc_cells_dict.iteritems()):
        this_arc = []
        arcs.append(this_arc)
        for cell in cells:
            this_arc.append((arc, cell))

    # Cell types
    if args.celltypes:
        from info_on_half_cells import type_occurence_dict, type_list
        types = []
        for type_ in type_list:
            cells = type_occurence_dict[type_]['cells']
            list_ = []
            for arc, cell, cell_ctr in cells:
                arc = arc.replace('S', 'Arc_')
                key = du.arc_cells_dict[arc][cell_ctr]
                list_.append((arc, key))
            types.append(list_)

    arr_titles = [
            (bins, 'Bins'),
            (arcs, 'Arcs'),
            (binned_cells, 'Deciles'),
            ]
    if args.celltypes:
        arr_titles.append((types, 'Types'))


    for arr_list, big_title in arr_titles:
        for recalc_dict,title in zip((dict_stop_squeeze, dict_start_ramp, dict_diff), titles):
            binned_arrays = []
            labels = []
            tot_average = 0
            tot_divisor = 0
            for arr_ctr, bin_ in enumerate(arr_list):
                if len(bin_) < 5:
                    continue
                arr = 0
                divisor = 0
                for arc, cell in bin_:
                    this_hl = recalc_dict[cell]
                    divisor += np.array(np.isfinite(this_hl), int)
                    arr += np.nan_to_num(this_hl)
                    tot_average += arr
                    tot_divisor += divisor
                arr /= divisor
                binned_arrays.append(arr)
                if arr_list is bins:
                    labels.append('%i cells' % len(bin_))
                elif arr_list is arcs:
                    labels.append(sorted(du.arc_cells_dict.keys())[arr_ctr])
                elif arr_list is binned_cells:
                    labels.append('%i0%%' % (arr_ctr))
                elif arr_list is types:
                    labels.append('%s %i cells' % (type_list[arr_ctr], len(bin_)))
            tot_average /= tot_divisor

            title = ' '.join((big_title, title))
            sp5, sp6, sp_avg = hl_normalized_delta(binned_arrays, tot_average, title, labels, suptitle=title)
            if recalc_dict is dict_diff:
                sp5.set_ylim(-10, 80)
                sp6.set_ylim(-.5e-13,2.5e-13)
                sp_avg.set_ylim(-1e-13,1e-13)


if args.pdsave:
    sf.pdijksta(figures)
elif args.savefig:
    for num in plt.get_fignums():
        fig = plt.figure(num)
        if args.noshow:
            plt.suptitle('')
        fig.subplots_adjust(left=0.1,right=0.75, wspace=0.75, hspace=.38)
        fig.savefig(os.path.expanduser(args.savefig) + '_%i.png' % num)

if not args.noshow:
    plt.show()
