from __future__ import division, print_function
import cPickle
import re
import time
import os
import sys
import argparse

import numpy as np

import LHCMeasurementTools.TimberManager as tm
from LHCMeasurementTools.LHC_FBCT import FBCT
from LHCMeasurementTools.LHC_BCT import BCT
from LHCMeasurementTools.LHC_BQM import blength
from LHCMeasurementTools.LHC_Energy import energy

sys.path.append('..')
import HeatLoadCalculators.impedance_heatload as hli
import HeatLoadCalculators.synchrotron_radiation_heatload as hls

import GasFlowHLCalculator.qbs_fill as qf

# Config
subtract_offset = True
average_offset_seconds = 60
#hrs_after_sb = 24
hl_dict_dir = './'

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('--input', help='Input file', default='./scrubbing_fills_2017.txt')
parser.add_argument('-o', help='Force output filename', type=str, default='scrubbing_dict_2017.pkl')
parser.add_argument('--debug', help='Print debug info', action='store_true')
args = parser.parse_args()

if args.debug:
    debugf = open('debug.txt', 'w')

# Add current version of this script to output meta data
with open(__file__.replace('.pyc', '.py'), 'r') as f:
    script = f.read()

fills_time_offset = []
with open(args.input, 'r') as f:
    lines = f.readlines()
for line in lines:
    if line[0] != '#':
        filln, tt_hrs, tt_offset = line.split()
        fills_time_offset.append((int(filln), float(tt_hrs), float(tt_offset)))

pkl_file_name = hl_dict_dir + args.o

logfile = pkl_file_name + '.log'

base_folder = '/afs/cern.ch/work/l/lhcscrub/LHC_2017_operation/'
child_folders = ['./']
fills_bmodes_file = base_folder + '/fills_and_bmodes.pkl'
csv_file_names = ['fill_basic_data_csvs/basic_data_fill_%d.csv',
        'fill_bunchbybunch_data_csvs/bunchbybunch_data_fill_%d.csv']
filling_pattern_csv = '/afs/cern.ch/work/l/lhcscrub/LHC_fullRun2_analysis_scripts/filling_patterns_2017.csv'

if os.path.isfile(pkl_file_name):
    if int(input('Delete %s? Enter 0/1.' % pkl_file_name)) == 1:
        os.remove(pkl_file_name)
    else:
        raise ValueError('Pkl file already exists!')

# Filling pattern and bpi
re_bpi = re.compile('_(\d+)bpi')
filling_pattern_raw = tm.parse_timber_file(filling_pattern_csv, verbose=False)
key = filling_pattern_raw.keys()[0]
filling_pattern_ob = filling_pattern_raw[key]

# Other functions
def add_to_dict(dictionary, value, keys, zero=False):
    if args.debug:
        print((value, keys), file=debugf)
    if zero:
        value = 0
    for nn, key in enumerate(keys):
        if nn == len(keys)-1:
            if key not in dictionary:
                dictionary[key] = []
            dictionary[key].append(value)
        else:
            if key not in dictionary:
                dictionary[key] = {}
            dictionary = dictionary[key]

def cast_to_na_recursively(dictionary, assure_length=None):
    for key, item in dictionary.iteritems():
        if type(item) is dict:
            cast_to_na_recursively(item, assure_length)
        elif type(item) is list:
            dictionary[key] = np.array(item)
            if assure_length is not None and len(dictionary[key]) != assure_length:
                log_print('Expected length: %i, Actual length: %i for key %s' % (assure_length, len(dictionary[key]), key))
        else:
            log_print('Unexpected type in dictionary for key %s' % key)

def data_integration(timestamps, values, key):
    # Trapezoidal integration
    output = 0.
    nan = np.isnan(values)
    values[nan] = 0.
    #if np.sum(nan) > 0:
        #log_print('Fill %i: There have been nan values for var %s' % (filln,key))
    for i in xrange(len(values)-1):
        output += (timestamps[i+1] - timestamps[i])*(values[i] + values[i+1])/2.
    return output

def log_print(*args, **kwargs):
    with open(logfile, 'a') as f:
        print(*args, file=f, **kwargs)
    print(*args, **kwargs)
log_print('%s' % time.ctime())
log_print('Offset is subtracted?: %s' % subtract_offset)
log_print('Offset is the average of %i seconds around specified offset time' % average_offset_seconds)

# Time keys
time_key_list = ['scrubbing']

# Filling numbers
with open(fills_bmodes_file, 'r') as f:
    fills_and_bmodes = cPickle.load(f)

# Model heat load calculators
imp_calc = hli.HeatLoadCalculatorImpedanceLHCArc()
sr_calc = hls.HeatLoadCalculatorSynchrotronRadiationLHCArc()

# Main loop
output_dict = {}

for filln, time_hrs, offset_time in fills_time_offset:
    process_fill = True

    # Check if this fill reached stable beams
    t_start_fill = fills_and_bmodes[filln]['t_startfill']
    time_values = t_start_fill + time_hrs*3600
    time_offset = t_start_fill + offset_time*3600

    # Check if all files exist and store their paths
    if process_fill:
        this_files = []
        for f in csv_file_names:
            f = f % filln
            for child in child_folders:
                path = base_folder + child + f
                if os.path.isfile(path):
                    this_files.append(path)
                    break
            else:
                log_print('Fill %i: %s does not exist' % (filln,f))
                process_fill = False
                break

    # Read csv and h5 files
    if process_fill:
        fill_dict = {}
        try:
            for f in this_files:
                if '.csv' in f:
                    fill_dict.update(tm.parse_timber_file(f, verbose=False))
                elif '.h5' in f:
                    fill_dict.update(tm.timber_variables_from_h5(f))
                else:
                    raise ValueError('Fill %i: Error: Unknown file type for %s.' % f)
        except IOError as e:
            log_print('Fill %i is skipped: %s!' % (filln,e))
            process_fill = False

    # Use recalculated data
    if process_fill:
        qbs_ob = {}
        for use_dP in (True, False):
            n_tries = 0
            while process_fill and n_tries < 5:
                n_tries += 1
                try:
                    qbs_ob[use_dP] = qf.compute_qbs_fill(filln, recompute_if_missing=False, use_dP=use_dP)
                    break
                except IOError as e:
                    log_print('Fill %i: No recomputed data: %s!' % (filln,e))
                    # Suspicious fails of read attempts -> try once more
                    time.sleep(5)
            else:
                process_fill = False
                log_print('Fill %i: Recomputed data read attempt failed!' % filln)

    # Special cells
    if process_fill:
        n_tries = 0
        while n_tries < 5:
            n_tries += 1
            try:
                qbs_ob_special = qf.special_qbs_fill_aligned(filln, recompute_if_missing=False)
                break
            except IOError as e:
                log_print('Fill %i: No special cell recomputed data: %s!' % (filln,e))
                # Suspicious fails of read attempts -> try once more
                time.sleep(5)
        else:
            process_fill = False
            log_print('Fill %i: Recomputed special cell data read attempt failed!' % filln)

    if process_fill:
        arc_averages = {}
        for use_dP in (True, False):
            arc_averages[use_dP] = qf.compute_qbs_arc_avg(qbs_ob[use_dP])

    ## Allocate objects that are used later
    if process_fill:
        bct_bx, blength_bx, fbct_bx = {}, {}, {}
        try:
            en_ob      = energy(fill_dict, beam=1)
            for beam_n in (1,2):
                bct_bx[beam_n] = BCT(fill_dict, beam=beam_n)
                blength_bx[beam_n] = blength(fill_dict, beam=beam_n)
                fbct_bx[beam_n] = FBCT(fill_dict, beam=beam_n)
        except ValueError as e:
            log_print('Fill %i: %s' % (filln, e))
            process_fill = False

    # Main part - obtain and store the variables of interest
    if process_fill:
        log_print('Fill %i is being processed.' % filln)

        ## Populate output dict

        # Fill Number
        add_to_dict(output_dict, filln, ['filln'])

        # Filling pattern and bpi
        pattern = filling_pattern_ob.nearest_older_sample(time_values)[0]
        add_to_dict(output_dict, pattern, ['filling_pattern'])
        bpi_info = re.search(re_bpi, pattern)
        if bpi_info is not None:
            bpi = int(bpi_info.group(1))
        else:
            bpi = -1
        add_to_dict(output_dict, bpi, ['bpi'])

        # Energy, only one per fill
        fill_energy = en_ob.nearest_older_sample(time_values)
        add_to_dict(output_dict, fill_energy, ['energy'])

        # offset and integrated heat load
        offset_dict = {}
        objects = [qbs_ob[True], arc_averages[True], qbs_ob_special, qbs_ob[False], arc_averages[False]]
        main_keys = ['all_cells', 'arc_averages', 'special_cells', 'all_cells_no_dP', 'arc_averages_no_dP']
        for obj, main_key in zip(objects, main_keys):
            mask_offset = np.logical_and(obj.timestamps < time_offset + average_offset_seconds/2, obj.timestamps > time_offset - average_offset_seconds/2)
            offset_dict[main_key] = dd = {}
            for key, arr in obj.dictionary.iteritems():
                offset = np.mean(arr[mask_offset])
                integrated_hl = data_integration(obj.timestamps, arr-offset, key)
                add_to_dict(output_dict, offset, ['hl_subtracted_offset', main_key, key])
                add_to_dict(output_dict, integrated_hl, ['hl_integrated', main_key, key])
                dd[key] = offset


        for kk, time_key in enumerate(time_key_list):
            tt = time_values
            # zero controls if calculations for output are performed.
            # If zero is True, then only 0s are stored in the output_dict
            zero = False
            this_add_to_dict = lambda x, keys: add_to_dict(output_dict, x, [time_key]+keys, zero=zero)

            # t_stamps
            this_add_to_dict(tt, ['t_stamps'])

            # intensity
            tot_int = 0
            int_bx = {}
            for beam in (1,2):
                if zero:
                    this_int = 0
                else:
                    this_int = float(bct_bx[beam].nearest_older_sample(tt))
                this_add_to_dict(this_int, ['intensity', 'b%i' % beam])
                int_bx[beam] = this_int
                tot_int += this_int
            this_add_to_dict(tot_int, ['intensity', 'total'])

            # Bunch length
            tot_avg, tot_var = 0, 0
            this_blength_bx = {}
            for beam in (1,2):
                if zero:
                    avg, sig = 0, 0
                else:
                    all_blen = blength_bx[beam].nearest_older_sample(tt)
                    mask_nonzero = all_blen != 0
                    if sum(mask_nonzero) == 0:
                        avg, sig = 0, 0
                    else:
                        avg = np.mean(all_blen[mask_nonzero])
                        sig = np.std(all_blen[mask_nonzero])
                this_blength_bx[beam] = avg
                this_add_to_dict(avg, ['blength', 'b%i' % beam, 'avg'])
                this_add_to_dict(sig, ['blength', 'b%i' % beam, 'sig'])
                tot_avg += avg
                tot_var += sig**2
            this_add_to_dict(tot_avg, ['blength', 'total', 'avg'])
            this_add_to_dict(np.sqrt(0.5*tot_var), ['blength', 'total', 'sig'])

            # Number of bunches
            n_bunches_bx = {}
            for beam in (1,2):
                if zero:
                    n_bunches = 0
                else:
                    bint = fbct_bx[beam].nearest_older_sample(tt)
                    min_int = 0.1 * max(bint)
                    mask_filled = bint > min_int
                n_bunches = sum(mask_filled)
                n_bunches_bx[beam] = n_bunches
                this_add_to_dict(n_bunches, ['n_bunches', 'b%i' % beam])

            # Imp / SR
            tot_imp, tot_sr = 0, 0
            for beam in (1,2):
                beam_int = int_bx[beam]
                n_bunches = n_bunches_bx[beam]
                sigma_t = this_blength_bx[beam]/4.
                if n_bunches != 0 and sigma_t != 0 and not zero:
                    imp = imp_calc.calculate_P_Wm(beam_int/n_bunches, sigma_t, fill_energy, n_bunches)
                    sr = sr_calc.calculate_P_Wm(beam_int/n_bunches, sigma_t, fill_energy, n_bunches)
                else:
                    imp, sr = 0, 0
                tot_imp += imp
                this_add_to_dict(imp, ['heat_load', 'imp', 'b%i' % beam])
                tot_sr += sr
                this_add_to_dict(sr, ['heat_load', 'sr', 'b%i' % beam])
            this_add_to_dict(tot_imp, ['heat_load', 'imp', 'total'])
            this_add_to_dict(tot_sr, ['heat_load', 'sr', 'total'])
            this_add_to_dict(tot_imp+tot_sr, ['heat_load', 'total_model'])

            # Heat loads
            for obj, main_key in zip(objects, main_keys):
                index = np.argmin(np.abs(obj.timestamps - tt))
                dd = offset_dict[main_key]
                for key, arr in obj.dictionary.iteritems():
                    if subtract_offset:
                        hl = arr[index] - dd[key]
                    else:
                        hl = arr[index]
                    this_add_to_dict(hl, ['heat_load', main_key, key])

if args.debug:
    debugf.close()

# Lists to np arrays
n_fills = len(output_dict['filln'])
cast_to_na_recursively(output_dict, assure_length=n_fills)

# Metadata
with open(logfile, 'r') as f:
    metadata = '%s\n' % sys.argv
    metadata += f.read()
    output_dict['LOGFILE'] = metadata
    output_dict['SCRIPT'] = script

# Save dict to pkl
with open(pkl_file_name, 'w') as f:
    cPickle.dump(output_dict, f, protocol=-1)

log_print('\nSuccess!')
log_print('Saved to %s\n' % pkl_file_name)

