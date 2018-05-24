import os
import cPickle as pickle
import numpy as np

pkl_names = ['large_heat_load_dict_2015_19.pkl', 'large_heat_load_dict_2016_17.pkl', 'large_heat_load_dict_2017_14.pkl']
new_pkl_names = ['large_heat_load_dict_2015_20.pkl', 'large_heat_load_dict_2016_18.pkl', 'large_heat_load_dict_2017_15.pkl']
latest_pkls = ['large_heat_load_dict_2015_latest.pkl', 'large_heat_load_dict_2016_latest.pkl', 'large_heat_load_dict_2017_latest.pkl']


for pkl_name, new_pkl_name, latest_pkl in zip(pkl_names, new_pkl_names, latest_pkls):

    with open(pkl_name, 'r') as f:
        dict_ = pickle.load(f)

    def recurse(dict_):
        for key in dict_:
            tt = type(dict_[key])
            if tt == dict:
                recurse(dict_[key])
            elif tt == np.ndarray:
                if key in ('05R4_947', '05L4_947_2'):
                    new_key = key[:8] + '_comb'
                    dict_[new_key] = dict_[key]
                    del dict_[key]
                    print('Renamed %s to %s' % (key, new_key))
                elif key in ('05R4_947_2', '05L4_947'):
                    new_key = key[:8] + '_quad'
                    dict_[new_key] = dict_[key]
                    del dict_[key]
                    print('Renamed %s to %s' % (key, new_key))
            elif tt == str:
                pass
            else:
                raise ValueError('Unexpected type %s behind key %s!' % (tt, key))


    recurse(dict_)

    with open(new_pkl_name, 'w') as f:
        pickle.dump(dict_, f, -1)

    os.remove(latest_pkl)
    os.symlink(os.path.basename(new_pkl_name), latest_pkl)


