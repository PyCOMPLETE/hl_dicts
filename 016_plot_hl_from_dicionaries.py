import numpy as np
import dict_utils as du
import argparse

import LHC_Heat_load_dict as LHD
import LHCMeasurementTools.LHC_Heatloads as HL
import LHCMeasurementTools.mystyle as ms

import matplotlib.pyplot as pl


# load heat load dictionary
hldict = LHD.get_full_heatload_dictionary_ldb_naming()

# extract moment list
list_moments = []
for kk in hldict.keys():
    if type(hldict[kk]) is dict:
        if 'heat_load' in hldict[kk].keys():
            list_moments.append(kk)


parser = argparse.ArgumentParser(description='Plot the heat loads from heat load dictionary')
parser.add_argument('--varlists', help='Variable lists to plot. Choose from %s' % sorted(HL.heat_loads_plot_sets.keys()), nargs='+', default=['AVG_ARC'])
parser.add_argument('--moment', help='Sample at %s' % sorted(list_moments))
parser.add_argument('--custom_vars', help='Custom list of variables to plot', nargs='+', default=[])
parser.add_argument('--colormap', help='chose between hsv and rainbow', default='hsv')
parser.add_argument('--full-varname-in-legend', help='Do not shorten varnames.', action='store_true')
parser.add_argument('--savein', help='Specify folder to save the output', default='cell_by_cell_plots')
parser.add_argument('--with_press_drop', help='Use pressure drop for recalculated data.', action='store_true')

parser.add_argument('--min_nbun', help='Remove fills with less than given number of bunches per beam', type=int)


args = parser.parse_args()

group_names = args.varlists
# handle custom list
if len(args.custom_vars)>0:
    group_names.append('Custom')
    dict_hl_groups['Custom'] = args.custom_vars

moment=args.moment


# reload the dictionary to include press drop
if args.with_press_drop:
    hldict = LHD.get_full_heatload_dictionary_ldb_naming(use_dP=args.with_press_drop)

# mask load dictionary
if args.min_nbun is not None:
    mask = (hldict[moment]['n_bunches']['b1']+hldict[moment]['n_bunches']['b2'])/2. > args.min_nbun
    hldict = du.mask_dict(hldict,mask)


# load default plot sets
dict_hl_groups = HL.heat_loads_plot_sets


x_axis = hldict['filln']



markersize = 8
fontsz = 16


pl.close('all')
ms.mystyle_arial(fontsz=fontsz, dist_tick_lab=8)

N_figures = len(group_names)
figs = []
figs_integ = []
figs_offset = []
sp1 = None
for ii, group_name in enumerate(group_names):
    fig_h = pl.figure(ii, figsize=(8*2, 6*1.4))
    figs.append(fig_h)
    fig_h.patch.set_facecolor('w')
        
    spint = pl.subplot2grid((10,2),(0,0), rowspan=4, colspan=1, sharex=sp1)
    sp1 = spint
    spnorm = pl.subplot2grid((10,2),(5,0), rowspan=5, colspan=1, sharex=sp1)
    sphlcell = pl.subplot2grid((10,2),(0,1), rowspan=4, colspan=1, sharex=sp1)
    spinteg = pl.subplot2grid((10,2),(5,1), rowspan=5, colspan=1)
    
    
    # figinteg_h = pl.figure(100+ii, figsize=(8, 6))
    # figs_integ.append(figinteg_h)
    # figinteg_h.patch.set_facecolor('w')
    # spinteg = pl.subplot(1,1,1)

    fig_offeset_h = pl.figure(200+ii, figsize=(8, 6))
    figs_offset.append(fig_offeset_h)
    fig_offeset_h.patch.set_facecolor('w')
    spoffs = pl.subplot(1,1,1, sharex=sp1)
    #plot n bunches
    spint.plot(x_axis, hldict[moment]['n_bunches']['b2'], '.r', markersize=markersize)
    spint.plot(x_axis, hldict[moment]['n_bunches']['b1'], '.b', markersize=markersize) 
    
    
    varnames = dict_hl_groups[group_name]
     
    for i_var, var in enumerate(varnames):
        colorcurr = ms.colorprog(i_prog=i_var, Nplots=len(varnames), cm=args.colormap)
        
        # prepare label
        if args.full_varname_in_legend:
            label = var
        else:
            label = ''
            for st in var.split('.POSST')[0].split('_'):
                if 'QRL' in st or 'QBS' in st or 'AVG' in st or 'ARC' in st:
                    pass
                else:
                    label += st + ' '
            label = label[:-1]
        
        
        
        # compute normalized heat load
        normhl = hldict[moment]['heat_load']['ldb_naming'][var]/(hldict[moment]['intensity']['b1']+\
                        hldict[moment]['intensity']['b2'])

        # plot heatload
        sphlcell.plot(x_axis, hldict[moment]['heat_load']['ldb_naming'][var], '.', color = colorcurr, markersize=markersize, label=label)
        spnorm.plot(x_axis, normhl, '.', color = colorcurr, markersize=markersize, label=label)
        
        #plot integrated
        integ_hl_this = np.cumsum(hldict['hl_integrated']['ldb_naming'][var])
        spinteg.plot(integ_hl_this, normhl, '.', color=colorcurr, markersize=markersize, label=label)
        
        spoffs.plot(x_axis, hldict['hl_subtracted_offset']['ldb_naming'][var], '.', color=colorcurr, markersize=markersize, label=label)


    spinteg.set_ylabel('Normalized heat load [W/p+]')
    spinteg.set_xlabel('Integrated heat load [J]')

    spint.set_ylabel('Number of bunches')
    spnorm.set_ylabel('Normalized heat load [W/p+]')
    sphlcell.set_ylabel('Heat load [W]')
    spnorm.set_xlabel('Fill number')
    sphlcell.legend(prop={'size':fontsz}, bbox_to_anchor=(1.05, 1.035),  loc='upper left')
    
    sphlcell.set_xlim(np.min(x_axis)+50, np.max(x_axis)+50)

    for sp in [spint, sphlcell, spinteg, spnorm]:
        sp.grid('on')
        sp.set_ylim(bottom=0)
        
    spoffs.grid('on')
    spoffs.set_ylabel('Subtracted offset [W]')

    fig_h.subplots_adjust(hspace=.20, right=.8, top=.92, bottom=.10, left=.08)
    
    
    for fig in [fig_h, fig_offeset_h]:
        fig.suptitle(group_name+' at '+moment)#+'\n'+{True: 'with_dP', False: 'no_dP'}[args.with_press_drop])
        

def save_evol(infolder='./'):
    strfile = 'heatload'
    for fig in figs:
        fig.savefig(infolder+'/'+strfile+'_evol_'+fig._suptitle.get_text().replace(' ', '__')+'.png',  dpi=200)

def save_offset(infolder='./'):
    for fig in figs_offset:
        fig.savefig(infolder+'/'+'hloffset_'+fig._suptitle.get_text().replace(' ', '__')+'.png',  dpi=200)



pl.show()

