import re
import copy
import cPickle

import numpy as np

def load_dict(filename):
    with open(filename, 'r') as f:
        return cPickle.load(f)

def mask_dict(dictionary, mask):
    new_dict = copy.deepcopy(dictionary)

    def _mask_recursively(dictionary, mask):
        for key in dictionary:
            if type(dictionary[key]) is dict:
                _mask_recursively(dictionary[key],mask)
            else:
                dictionary[key] = dictionary[key][mask]

    _mask_recursively(new_dict,mask)
    return new_dict


def operate_on_dicts(dict1, dict2, operator):
    new_dict = copy.deepcopy(dict1)

    def recurse(dict1, dict2, new_dict):
        for key in dict1:
            tt = type(dict1[key])
            if tt is dict:
                recurse(dict1[key],dict2[key], new_dict[key])
            elif tt is np.ndarray:
                new_dict[key] = operator(dict1[key], dict2[key])
            else:
                raise ValueError('Unexpected type %s behind key %s!' % (tt, key))
    recurse(dict1, dict2, new_dict)
    return new_dict

def merge_dicts(dict1, dict2):
    return operate_on_dicts(dict1, dict2, lambda x,y: np.concatenate([x,y]))


arc_list = ['S%i%i' % (ii,ii+1) for ii in xrange(1,8)]
del ii
arc_list.append('S81')


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
