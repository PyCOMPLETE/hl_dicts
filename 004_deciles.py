from __future__ import print_function, division
import operator

import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker
import numpy as np

import LHCMeasurementTools.mystyle as ms
#import LHCMeasurementTools.TimestampHelpers as TH
#import LHCMeasurementTools.LHC_Heatloads as hl
from LHC_Heat_load_dict import mask_dict, main_dict, arc_list

plt.close('all')
moment = 'stop_squeeze'
mask = np.logical_and(main_dict[moment]['n_bunches']['b1'] > 800, main_dict[moment]['n_bunches']['b2'] > 800)
main_dict = mask_dict(main_dict,mask)
x_axis = main_dict['filln']
tot_int = main_dict[moment]['intensity']['total']


figures = []
def hl_normalized_delta(input_arrays, title, labels):
    ms.figure(title, figures)
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
        sp_avg.plot(x_axis, (arr-cell_average)/tot_int, '.', color=color, markersize=12)

    sp5.plot(x_axis, cell_average,'.', color='black', markersize=12)
    sp6.plot(x_axis, cell_average/tot_int,'.', color='black', markersize=12, label='Average')
    sp_avg.plot(x_axis, np.zeros_like(cell_average),'.', color='black', markersize=12)

    plt.setp(sp5.get_xticklabels(), visible = False)
    plt.setp(sp6.get_xticklabels(), visible = False)
    sp6.legend(bbox_to_anchor=(1.10, 1.04))


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

hl_normalized_delta(binned_arrays, 'All cells', labels)

selected, labels = [], []
for i in xrange(0,len(arc_cell_hls), 50):
    arc, cell, _ = arc_cell_hls[i]
    selected.append(recalc_dict[arc][cell])
    labels.append(cell)


hl_normalized_delta(selected, 'Selected cells', labels)

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

binned_arrays = []
labels = []
for bin_ in bins:
    arr = 0
    divisor = 0
    for arc, cell in bin_:
        this_hl = recalc_dict[arc][cell]
        divisor += np.array(np.isfinite(this_hl), int)
        arr += np.nan_to_num(this_hl)
    arr /= divisor
    binned_arrays.append(arr)
    labels.append('%i cells' % len(bin_))

cell_average = np.nanmean(complete_hl, axis=1)
hl_normalized_delta(binned_arrays, 'Bins', labels)



for fig in figures:
    fig.suptitle('At '+moment, fontsize=20)
plt.show()
