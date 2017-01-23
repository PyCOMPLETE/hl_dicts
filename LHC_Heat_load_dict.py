import os
import cPickle
from dict_utils import *

this_directory = os.path.dirname(os.path.abspath(__file__))
dict_file_2016 = this_directory + '/large_heat_load_dict_2016_latest.pkl'
dict_file_2015 = this_directory + '/large_heat_load_dict_2015_latest.pkl'

with open(dict_file_2016, 'r') as f:
    main_dict_2016 = cPickle.load(f)
with open(dict_file_2015, 'r') as f:
    main_dict_2015 = cPickle.load(f)

main_dict = merge_dicts(main_dict_2015, main_dict_2016)
hl_dict = main_dict

del f, this_directory, dict_file_2016, dict_file_2015
