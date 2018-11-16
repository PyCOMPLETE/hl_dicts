import os
import cPickle
import dict_utils as du
import LHCMeasurementTools.LHC_Heatloads as HL

arc_list = 'S12 S23 S34 S45 S56 S67 S78 S81'.split()

# For imports from this module
merge_dicts = du.merge_dicts
mask_dict = du.mask_dict

def get_full_heatload_dictionary():
    iter_dict = None
    this_directory = os.path.dirname(os.path.abspath(__file__))
    for yy in [2015, 2016, 2017, 2018]:
        #print yy
        path = this_directory + '/large_heat_load_dict_%d_latest.pkl'%yy
        with open(path, 'r') as f:
            this_dict = cPickle.load(f)
        #print this_dict['filln']
        if iter_dict is None:
            iter_dict = this_dict
        else:
            iter_dict = du.merge_dicts(iter_dict, this_dict)
    return iter_dict

main_dict = get_full_heatload_dictionary()


#LDB naming
def replace_single_hld_with_ldb_naming(thishld, use_dP):
    if use_dP:
        strdp = ''
    else:
        strdp = '_no_dP'

    output = {}

    # start from arc averages
    for ss in HL.sector_list():
        key = 'S%d_QBS_AVG_ARC.POSST' % ss
        output[key] = thishld['arc_averages'+strdp]['S%d'%ss]

    #others
    varlist_tmb = []
    for kk in HL.variable_lists_heatloads.keys():
        varlist_tmb+=HL.variable_lists_heatloads[kk]
    varlist_tmb+=HL.arcs_varnames_static
    varlist_tmb+=HL.other_varnames_static

    for varname in varlist_tmb:
        special_id = varname.split('.POSST')[0][-3:]
        if special_id in('_Q1', '_D2', '_D3', '_D4'):
            cell = varname.split('_')[1]
            kkk = cell+special_id
            output[varname] = thishld['special_cells'][kkk]
            output[varname+'_B1'] = thishld['special_cells'][kkk+'_1']
            output[varname+'_B2'] = thishld['special_cells'][kkk+'_2']
        elif varname.startswith('QRLEB_05L4'):
            output[varname] = thishld['all_cells']['05L4_947_comb']
        elif varname.startswith('QRLEB_05R4'):
            output[varname] = thishld['all_cells']['05R4_947_comb']
        elif varname.startswith('QRLFF_05L4'):
            output[varname] = thishld['all_cells']['05L4_947_quad']
        elif varname.startswith('QRLFE_05R4'):
            output[varname] = thishld['all_cells']['05R4_947_quad']
        elif '_QBS9' in varname:
            firstp, lastp = tuple(varname.split('_QBS'))
            kkk = firstp.split('_')[-1]+'_'+lastp.split('.')[0]
            output[varname] = thishld['all_cells'+strdp][kkk]
        elif 'QBS_AVG_ARC' in varname or 'QBS_CALCULATED_ARC' in varname:
            continue

    for kk in ['all_cells', 'arc_averages', 'arc_averages_no_dP', 'all_cells_no_dP', 'special_cells']:
        del(thishld[kk])

    thishld['ldb_naming'] = output

def replace_full_hldict_with_ldb_naming(main_dict, use_dP):

    replace_single_hld_with_ldb_naming(main_dict['hl_subtracted_offset'], use_dP)
    replace_single_hld_with_ldb_naming(main_dict['hl_integrated'], use_dP)

    for kk in main_dict.keys():
        if type(main_dict[kk]) is dict:
            if 'heat_load' in main_dict[kk]:
                replace_single_hld_with_ldb_naming(main_dict[kk]['heat_load'], use_dP)


def get_full_heatload_dictionary_ldb_naming(use_dP=False):
    hldict = get_full_heatload_dictionary()
    replace_full_hldict_with_ldb_naming(hldict, use_dP)

    return hldict


