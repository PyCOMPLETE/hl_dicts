import re
import copy
import cPickle
from config_qbs import config_qbs as cq

import numpy as np

def load_dict(filename):
    with open(filename, 'r') as f:
        return cPickle.load(f)

def mask_dict(dictionary, mask):
    new_dict = copy.deepcopy(dictionary)

    def _mask_recursively(dictionary, mask):
        for key, value in dictionary.iteritems():
            if type(value) is dict:
                _mask_recursively(value,mask)
            elif type(value) is str:
                pass
            else:
                dictionary[key] = value[mask]

    _mask_recursively(new_dict,mask)
    return new_dict


def operate_on_dicts(dict1, dict2, operator):
    new_dict = copy.deepcopy(dict1)

    def recurse(dict1, dict2, new_dict):
        for key in dict1:
            tt = type(dict1[key])
            if tt == dict:
                recurse(dict1[key],dict2[key], new_dict[key])
            elif tt == np.ndarray:
                new_dict[key] = operator(dict1[key], dict2[key])
            elif tt == str:
                pass
            else:
                raise ValueError('Unexpected type %s behind key %s!' % (tt, key))
    recurse(dict1, dict2, new_dict)
    return new_dict

def merge_dicts(dict1, dict2):
    return operate_on_dicts(dict1, dict2, lambda x,y: np.concatenate([x,y]))


re_sb = re.compile('^sb\+(\d+)_hrs$')
def values_over_time(hl_dict, *keys):

    tt_keys = ['stable_beams']
    hrs = [0]
    for key in hl_dict:
        info = re_sb.search(key)
        if info != None:
            tt_keys.append(key)
            hrs.append(int(info.group(1)))
    hrs_keys = zip(hrs, tt_keys)
    hrs_keys.sort(key=lambda x: x[0])

    output = []
    for fill_ctr, fill in enumerate(hl_dict['filln']):
        xx, yy = [], []
        for hr, key in hrs_keys:
            dd = hl_dict[key]
            for kk in keys:
                dd = dd[kk]
            if hl_dict[key]['t_stamps'][fill_ctr] != 0.:
                val = dd[fill_ctr]
                xx.append(hr)
                yy.append(val)
        output.append(np.array([xx,yy]))
    return output


def get_matching_keys(hl_dict, regex):
    hl_dict = hl_dict['hl_integrated']['all_cells']
    list_ = filter(regex.match, hl_dict.keys())
    return list_

def q6_keys_list(hl_dict):
    re_q6 = re.compile('^06[LR][1528]_\d{3}')
    return get_matching_keys(hl_dict, re_q6)
def q5_keys_list(hl_dict):
    re_q5 = re.compile('^05[LR][1528]_\d{3}')
    return get_matching_keys(hl_dict, re_q5)
def q4_keys_list(hl_dict):
    re_q4 = re.compile('^04[LR][1528]_\d{3}')
    return get_matching_keys(hl_dict, re_q4)

arc_cells_dict = {}
arc_cells_dict_nods = {}
for cell, type_, sector, len_ in zip(cq.Cell_list, cq.Type_list, cq.Sector_list, cq.L_list):
    sector_str = 'Arc_' + sector
    if sector_str not in arc_cells_dict:
        arc_cells_dict[sector_str] =  []
        arc_cells_dict_nods[sector_str] = []
    if type_ == 'ARC':
        arc_cells_dict[sector_str].append(cell)
        if len_ == 53:
            arc_cells_dict_nods[sector_str].append(cell)
del cell, type_, sector,  cq, sector_str


