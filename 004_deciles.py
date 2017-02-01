from __future__ import print_function, division
import operator

import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker
import numpy as np
import operator

import LHCMeasurementTools.mystyle as ms
#import LHCMeasurementTools.TimestampHelpers as TH
#import LHCMeasurementTools.LHC_Heatloads as hl
from LHC_Heat_load_dict import mask_dict, main_dict, arc_list
import dict_utils as du

plt.close('all')
moment = 'stop_squeeze'
mask = np.logical_and(main_dict[moment]['n_bunches']['b1'] > 800, main_dict[moment]['n_bunches']['b2'] > 800)
main_dict = mask_dict(main_dict,mask)
x_axis = main_dict['filln']
tot_int = main_dict[moment]['intensity']['total']


figures = []
def hl_normalized_delta(input_arrays, average, title, labels, suptitle=False):
    ms.figure(title, figures)
    if suptitle:
        plt.suptitle(suptitle, fontsize=20)
    sp1 = None
    sp5 = plt.subplot(3,1,1, sharex=sp1)
    sp6 = plt.subplot(3,1,2, sharex=sp1)
    sp_avg = plt.subplot(3,1,3, sharex=sp1)
    sp5.set_ylabel('Cell heat loads [W/m]')
    sp6.set_ylabel('Cell heat loads [W/m/p+]')
    sp_avg.set_ylabel('Cell heat loads [W/m/p+]')
    sp5.grid(True)
    sp6.grid(True)
    sp_avg.grid(True)

    sp5.set_title('Heat loads')
    sp6.set_title('Normalized by intensity')
    sp_avg.set_title('Delta to average')

    for ctr, (arr, label) in enumerate(zip(input_arrays, labels)):
        color = ms.colorprog(ctr, input_arrays)
        sp5.plot(x_axis, arr, '.', color=color, markersize=12)
        sp6.plot(x_axis, arr/tot_int, '.', color=color, markersize=12, label=label)
        sp_avg.plot(x_axis, (arr-average)/tot_int, '.', color=color, markersize=12)

    sp5.plot(x_axis, average,'.', color='black', markersize=12)
    sp6.plot(x_axis, average/tot_int,'.', color='black', markersize=12, label='Average')
    sp_avg.plot(x_axis, np.zeros_like(average),'.', color='black', markersize=12)

    plt.setp(sp5.get_xticklabels(), visible = False)
    plt.setp(sp6.get_xticklabels(), visible = False)
    sp6.legend(bbox_to_anchor=(1.10, 1.04))
    return sp5, sp6, sp_avg


recalc_dict = main_dict[moment]['heat_load_re']
n_bins = 10+1

arc_cell_hls = []
for arc, cell_dict in recalc_dict.iteritems():
    for cell, hl_arr in cell_dict.iteritems():
        arc_cell_hls.append((arc, cell, np.mean(hl_arr[-10:])))

arc_cell_hls = filter(lambda x: x[2] > 0, arc_cell_hls)
arc_cell_hls.sort(key=operator.itemgetter(2))

complete_hl = np.zeros((len(hl_arr), len(arc_cell_hls)), float)
for ctr, (arc, cell, _) in enumerate(arc_cell_hls):
    complete_hl[:,ctr] = recalc_dict[arc][cell]
cell_average = np.nanmean(complete_hl, axis=1)

indices = map(int, np.linspace(0, len(arc_cell_hls), n_bins))

binned_arrays = []
labels = []
for ctr in xrange(len(indices)-1):
    arr = 0
    start, stop = indices[ctr:ctr+2]
    divisor = 0
    for ctr2 in xrange(start, stop):
        arc, cell, _ = arc_cell_hls[ctr2]
        this_hl = recalc_dict[arc][cell]
        divisor += np.array(np.isfinite(this_hl), int)
        arr += np.nan_to_num(this_hl)
    arr /= divisor
    binned_arrays.append(arr)
    labels.append('%i0%% decile %i cells' %(ctr+1,stop-start))

hl_normalized_delta(binned_arrays, cell_average, 'All cells at %s' % moment, labels)

selected, labels = [], []
for i in xrange(0,len(arc_cell_hls), 50):
    arc, cell, _ = arc_cell_hls[i]
    selected.append(recalc_dict[arc][cell])
    labels.append(cell)


hl_normalized_delta(selected, cell_average, 'Selected cells at %s' % moment, labels)

min_hl, max_hl = arc_cell_hls[0][2], arc_cell_hls[-1][2]

delta_hl = (max_hl - min_hl) / (n_bins-2)
bins = []
ref_hl = min_hl
for arc, cell, hl in arc_cell_hls:
    if hl == min_hl or hl > ref_hl:
        bin_ = []
        bins.append(bin_)
        ref_hl += delta_hl
    bin_.append((arc,cell))


dict_stop_squeeze   = main_dict['stop_squeeze']['heat_load_re']
dict_start_ramp     = main_dict['start_ramp']['heat_load_re']
dict_diff           = du.operate_on_dicts(dict_stop_squeeze, dict_start_ramp, operator.sub)

titles = ('At stop_squeeze', 'At start ramp', 'Difference after ramp')

arcs = []
for arc in arc_list:
    this_arc = []
    arcs.append(this_arc)
    cells = recalc_dict[arc].keys()
    for cell in cells:
        this_arc.append((arc, cell))


for arr_list, big_title in zip((bins, arcs), ('Bins', 'Arcs')):
    for recalc_dict,title in zip((dict_stop_squeeze, dict_start_ramp, dict_diff), titles):
        binned_arrays = []
        labels = []
        tot_average = 0
        for arr_ctr, bin_ in enumerate(arr_list):
            arr = 0
            divisor = 0
            for arc, cell in bin_:
                this_hl = recalc_dict[arc][cell]
                divisor += np.array(np.isfinite(this_hl), int)
                arr += np.nan_to_num(this_hl)
            arr /= divisor
            tot_average += arr
            binned_arrays.append(arr)
            if arr_list is bins:
                labels.append('%i cells' % len(bin_))
            else:
                labels.append(arc_list[arr_ctr])
        tot_average /= len(arr_list)

        title = ' '.join((big_title, title))
        sp5, sp6, sp_avg = hl_normalized_delta(binned_arrays, tot_average, title, labels, suptitle=title)
        if recalc_dict is dict_diff:
            sp5.set_ylim(-10, 80)
            sp6.set_ylim(-.5e-13,2.5e-13)
            sp_avg.set_ylim(-1e-13,1e-13)

plt.show()
