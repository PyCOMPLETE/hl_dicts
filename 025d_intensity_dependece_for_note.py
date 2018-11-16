import copy
import os

import matplotlib.pyplot as plt
import numpy as np

import LHCMeasurementTools.mystyle as ms
import LHCMeasurementTools.savefig as sf
from LHCMeasurementTools.mystyle import colorprog
from LHC_Heat_load_dict import mask_dict, main_dict
import dict_utils as du

from LHCMeasurementTools.LHC_Heatloads import magnet_length

moment = 'start_ramp'
subtract_model = False

main_dict_0 = copy.deepcopy(main_dict)
fontsz = 12

plt.close('all')
ms.mystyle_arial(fontsz=fontsz, dist_tick_lab=10)

mask = np.array(map(lambda n: n in [5219, 5222, 5223], main_dict['filln']))
main_dict = mask_dict(main_dict,mask)

# Heat load

#fig = plt.figure(3, figsize = (12,12))
fig = plt.figure(3, figsize = (7,6))
fig.set_facecolor('w')


hl_keys_arcs = sorted(main_dict[moment]['heat_load']['arc_averages'].keys())
hl_keys_quads = du.q6_keys_list(main_dict)
hl_keys_triplets = du.q3_keys_list(main_dict)
hl_keys_special = filter(lambda x: x[-2:] in ('D2', 'D3', 'D4') and x[:4] != '33L5',
                              sorted(main_dict[moment]['heat_load']['special_cells'].keys()))

hl_model_arcs = main_dict[moment]['heat_load']['total_model']
hl_model_quads = main_dict[moment]['heat_load']['imp']['total']

get_len_arcs = lambda x: magnet_length['MODEL'][0]
get_len_special = lambda x: magnet_length['special_HC_D2'][0]
def get_len_quads(key):
    key2 = 'Q' + key[1] + 's_IR' + key[3]
    return magnet_length[key2][0]
def get_len_triplets(key):
    return magnet_length['IT_IR'+key[3]][0]


for ctr, (family, title, hl_keys, model, get_len) in enumerate(zip(
    ['arc_averages'], #, 'all_cells', 'special_cells', 'all_cells'],
    ['Average arc cells'], #, 'Q6 quadrupoles', 'Special dipoles', 'Inner Triplets'],
    [hl_keys_arcs], #, hl_keys_quads, hl_keys_special, hl_keys_triplets],
    [hl_model_arcs], #, hl_model_quads, hl_model_arcs, hl_model_quads],
    [get_len_arcs] #, get_len_quads, get_len_special, get_len_triplets]
)):
    sp_ctr = ctr+1
    # sp = plt.subplot(2,2,sp_ctr)
    sp = plt.subplot(1,1,sp_ctr)
    sp.grid(True)
    sp.set_xlim(0.4,1.3e11)
    sp.set_xlabel('Bunch intensity [p/bunch]')
    sp.set_title(title)
    if subtract_model:
        sp.set_ylabel('Heat load from e-cloud [W/m]')
    else:
        sp.set_ylabel('Total heat load [W/m]')

    xx = main_dict[moment]['intensity']['total']/main_dict[moment]['n_bunches']['b1']/2.
    if not subtract_model:
        if model is hl_model_arcs:
            label = 'Imp.+SR'
        elif model is hl_model_quads:
            label = 'Imp.'
            print model
        sp.plot(xx, model, '.', color='black', label=label, markersize=15)

    for key_ctr, key in enumerate(hl_keys):
        color = colorprog(key_ctr, hl_keys)

        yy = main_dict[moment]['heat_load'][family][key]/get_len(key)
        if subtract_model:
            yy -= model
            print key, get_len(key)

        fit = np.polyfit(xx,yy,1)
        yy_fit = np.poly1d(fit)
        xx_fit = np.arange(0.3e11, 1.31e11, 0.01e11)

        sp.plot(xx, yy, '.', color=color, markersize=15)
        if ctr in (1,3):
            label = key[:4]
        else:
            label = key

        sp.plot(xx_fit, yy_fit(xx_fit), color=color, lw=3, label=label)
        
#    if ctr == 0:
#        sp.axhline(180./get_len(key), lw=3., label='Cryo limit', color='black')

    sp.set_ylim(0,None)
    sp.legend(prop={'size':fontsz}, loc='upper left')

fig.subplots_adjust(bottom=.14, hspace=.35, wspace=.42)

for fig in [fig]:
    fig.suptitle('At '+moment+'. Subtracted model: %s' % subtract_model)

#fig.savefig(os.path.expanduser('~/presentations/md_note_intensity_scan2/ss/evolution.png'))

plt.show()
