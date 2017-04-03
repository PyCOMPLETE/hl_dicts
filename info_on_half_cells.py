from __future__ import division
import sys
import os
import re
import argparse

import numpy as np
import matplotlib.pyplot as plt

import LHCMeasurementTools.mystyle as ms
from twiss_file_utils import TfsLine, HalfCell


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--show', help='Show plot', action='store_true')
    args = parser.parse_args()
    show_plot = args.show
else:
    show_plot = False

# Config
correct_length = False
vkicker_is_hkicker = True
#show_plot = True
twiss_file_name_tfs = os.path.dirname(os.path.abspath(__file__)) + '/twiss_lhcb1_2.tfs'

re_arc_start = re.compile('(S)\.ARC\.(\d\d)\.B1')
re_arc_end = re.compile('E\.ARC\.\d\d\.B1')
re_sbend_hc = re.compile('^"MB\.[ABC](\d+[LR]\d+)\.B1"$')

re_ds_start = re.compile('(S)\.DS\.([RL]\d)\.B1')
re_ds_end = re.compile('E\.DS\.([RL]\d)\.B1')

# State Machine
look_for_arc = 0
in_arc = 1
in_prefix = 2
in_ds = 3
look_for_ds = 4
status = in_prefix

hc_name = ''
arc = None
half_cell = None
arc_hc_dict = {}
tfs_file = open(twiss_file_name_tfs, 'r')


if False:
    for line_n, line in enumerate(iter(tfs_file), 1):
        split = line.split()
        if status == in_prefix:
            if '$' in line:
                status = look_for_ds
        elif status == look_for_ds:
            if re_ds_start.search(line):
                print(line_n, 'ds start')
                status = in_arc
                second_ds = False
                arc_half_cells = []
                this_hc = HalfCell(None)
        elif status == in_arc:
            if re_arc_start.search(line):
                print(line_n, 'arc start')
                arc = ''.join(re_arc_start.search(line).groups())
                arc_hc_dict[arc] = arc_half_cells
            elif re_ds_end.search(line):
                if second_ds:
                    print(line_n, 'ds end')
                    status = look_for_ds
                else:
                    second_ds = True
            else:
                this_name = split[0]
                info = re_sbend_hc.search(this_name)
                if info is not None:
                    hc_name = info.group(1)
                    if hc_name != this_hc.name:
                        #print this_hc.length
                        #import pdb ; pdb.set_trace()
                        if 1 < this_hc.length < 53:
                            print('length smaller than 53', line_n, this_hc.name, this_hc.length)
                        this_hc = HalfCell(hc_name, correct_length)
                        arc_half_cells.append(this_hc)
                this_line = TfsLine(line, vkicker_is_hkicker)
                this_hc.add_line(this_line)

                if this_hc.length > 54:
                    print('length larger than 54:', line_n, hc_name, this_hc.length)

else:
    for line_n, line in enumerate(iter(tfs_file)):
        split = line.split()
        if status == in_prefix:
            if '$' in line:
                status = look_for_arc
        elif status == look_for_arc:
            if re_arc_start.search(line):
                status = in_arc
                arc = ''.join(re_arc_start.search(line).groups())
                arc_half_cells = []
                this_hc = HalfCell(None)
                arc_hc_dict[arc] = arc_half_cells
        elif status == in_arc:
            if re_arc_end.search(line) is not None:
                status = look_for_arc
            else:
                this_name = split[0]
                info = re_sbend_hc.search(this_name)
                if info is not None:
                    hc_name = info.group(1)
                    if hc_name != this_hc.name:
                        if 1 < this_hc.length < 53:
                            print('length smaller than 53', line_n, this_name)
                        this_hc = HalfCell(hc_name, correct_length)
                        arc_half_cells.append(this_hc)
                this_line = TfsLine(line, vkicker_is_hkicker)
                this_hc.add_line(this_line)
    
                if this_hc.length > 54:
                    print('length larger than 54:', line_n, this_name)
    

tfs_file.close()

# Find out how often each half cell type appears in the LHC
type_occurence_dict = {}
for arc, arc_half_cells in arc_hc_dict.iteritems():
    print(arc, len(arc_half_cells))
    for cell_ctr, hc in enumerate(arc_half_cells):
        hc.create_dict()
        hc.round_dict(precision=2)
        #print(hc.length, (hc.lines[-1].s_end - hc.lines[0].s_begin))
        for key, subdict in type_occurence_dict.iteritems():
            if hc.len_type_dict == subdict['dict']:
                subdict['n'] += 1
                subdict['cells'].append((arc, hc.name, cell_ctr))
                break
        else:
            type_occurence_dict[hc.name] = {
                    'dict': hc.len_type_dict,
                    'n': 1, 'cell': hc,
                    'cells': [(arc, hc.name, cell_ctr)]}

type_list = type_occurence_dict.keys()
type_list.sort(key=lambda item: type_occurence_dict[item]['n'], reverse=True)

# More information on cells
no_oct_ctr, oct_ctr = 0, 0
n_multip_dict = {}
oct_quad_len_dict = {}

mag_len_dict = {}
show_4, show_2 = True, True
for arc, arc_half_cells in arc_hc_dict.iteritems():
    for hc in arc_half_cells:
        if 'OCTUPOLE' in hc.len_type_dict:
            oct_ctr += 1
        else:
            no_oct_ctr += 1
        
        oct_quad_len = 0
        for key in ['QUADRUPOLE', 'OCTUPOLE']:
            if key in hc.len_type_dict:
                oct_quad_len += hc.len_type_dict[key]
        if oct_quad_len in oct_quad_len_dict:
            oct_quad_len_dict[oct_quad_len] += 1
        else:
            oct_quad_len_dict[oct_quad_len] = 1

        for key, length in hc.len_type_dict.iteritems():
            if type(length) is not list:
                if key not in mag_len_dict:
                    mag_len_dict[key] = {}
                if length not in mag_len_dict[key]:
                    mag_len_dict[key][length] = 0
                mag_len_dict[key][length] += 1

        n_multip = hc.len_type_dict['order'].count('MULTIPOLE')
        if show_4 and n_multip == 4:
            show_4 = False
            #print(hc.len_type_dict)
        elif show_2 and n_multip == 2:
            show_2 = False
            #print(hc.len_type_dict)

        if n_multip in n_multip_dict:
            n_multip_dict[n_multip] += 1
        else:
            n_multip_dict[n_multip] = 1

#        for line in hc.lines:
#            if line.type == 'OCTUPOLE':
#                print('%s %e %e %e %e' % (line.type, line.k1l, line.k2l, line.k3l, line.k4l))


if __name__ == '__main__':
    print('Out of %i cells, %i are with octupoles and %i without.' % (oct_ctr+no_oct_ctr, oct_ctr, no_oct_ctr))
    print('Occurences of multipoles: %s' % n_multip_dict)
    print('Combined length of quad and oct: %s' % oct_quad_len_dict)

    if show_plot:
        myfontsz = 16
        ms.mystyle_arial(fontsz=myfontsz, dist_tick_lab=6)

        plt.close('all')

        n_sps = 5
        n_cells = 5 * n_sps
        sp = None
        fig_ctr = 0
        for ctr, key in enumerate(type_list[:n_cells]):
            sp_ctr = ctr % n_sps + 1
            if sp_ctr == 1:
                fig = plt.figure()
                fig.set_facecolor('w')
                fig_ctr += 1
                fig.canvas.set_window_title('Arc half cell types %i' % fig_ctr)
                fig.subplots_adjust(right=0.85, left=0.04, top=0.91, wspace=0.39, hspace=0.39, bottom=0.05)

            cell = type_occurence_dict[key]['cell']

            sp = plt.subplot(n_sps, 1, sp_ctr, sharex=sp)
            sp.set_title('Cell %s occured %i times. s_0: %i' % (cell.name,type_occurence_dict[key]['n'], cell.get_s_begin()))
            sp.set_ylim(-3,3)
            sp.set_xlim(-1,55)
            sp.get_xaxis().get_major_formatter().set_useOffset(False)
            sp.set_yticks([])
            labelled_types = []
            for line in cell.lines:
                type_name = line.type
                name = line.name
                s_diff = line.s_end - line.s_begin

                if s_diff != 0 and 'DRIFT' not in type_name:
                    if type_name in labelled_types:
                        label = None
                    else:
                        labelled_types.append(type_name)
                        label = type_name

                    if 'SBEND' in type_name:
                        color = 'blue'
                        top, bottom = 1, 0
                    elif 'QUADRUPOLE' in type_name:
                        color = 'red'
                        top, bottom = 1, -1
                    elif 'KICKER' in type_name:
                        color = 'green'
                        top, bottom = 1, 0
                    elif 'OCTUPOLE' in type_name:
                        color = 'black'
                        top, bottom = 1, -1
                    elif 'SEXTUPOLE' in type_name:
                        color = 'brown'
                        top, bottom = 1.5, -1.5
                    elif 'PLACEHOLDER' in type_name:
                        color = 'black'
                        top, bottom = 1, -1
                    else:
                        color = 'orange'
                        top, bottom = 2, -2
                    yy = np.array([bottom,top, top, bottom, bottom])
                    xx = np.array([line.s_begin, line.s_begin, line.s_end, line.s_end, line.s_begin]) - cell.get_s_begin()
                    sp.plot(xx, yy,label=label, color=color)

            sp.legend(bbox_to_anchor=(1.15,1))
            if sp_ctr == n_sps:
                sp.set_xlabel('s [m]')

        sp.set_xlabel('s [m]')
        plt.show()
