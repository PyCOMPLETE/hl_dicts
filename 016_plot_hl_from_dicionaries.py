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


parser = argparse.ArgumentParser(description='Plot the heat loads for one LHC fill')
parser.add_argument('--varlists', help='Variable lists to plot. Choose from %s' % sorted(HL.heat_loads_plot_sets.keys()), nargs='+', default=['AVG_ARC'])
parser.add_argument('--moment', help='Sample at %s' % sorted(list_moments))
parser.add_argument('--custom_vars', help='Custom list of variables to plot', nargs='+', default=[])
parser.add_argument('--colormap', help='chose between hsv and rainbow', default='hsv')
parser.add_argument('--normtointensity', help='Normalize to beam intensity', action='store_true')

parser.add_argument('--min_nbun', help='Remove fills with less than given number of bunches per beam', type=int)


args = parser.parse_args()

group_names = args.varlists
# handle custom list
if len(args.custom_vars)>0:
    group_names.append('Custom')
    dict_hl_groups['Custom'] = args.custom_vars






# mask load dictionary
if args.min_nbun is not None:
    mask = (hldict[moment]['n_bunches']['b1']+hldict[moment]['n_bunches']['b2'])/2. > args.min_nbun
    hldict = du.mask_dict(hldict,mask)


# load default plot sets
dict_hl_groups = HL.heat_loads_plot_sets


x_axis = hldict['filln']



markersize = 12
fontsz = 16


pl.close('all')
ms.mystyle_arial(fontsz=fontsz, dist_tick_lab=5)

N_figures = len(group_names)
figs = []
figs_integ = []
sp1 = None
for ii, group_name in enumerate(group_names):
    fig_h = pl.figure(ii, figsize=(8*1.6, 6*1.6))
    figs.append(fig_h)
    fig_h.patch.set_facecolor('w')
        
    spint = pl.subplot(3,1,1, sharex=sp1)
    sp1 = spint
    sphlcell = pl.subplot2grid((3,1),(1,0), rowspan=2, colspan=1, sharex=sp1)
    
    
    figinteg_h = pl.figure(100+ii, figsize=(8, 6))
    figs_integ.append(figinteg_h)
    figinteg_h.patch.set_facecolor('w')
    spinteg = pl.subplot(1,1,1)
    
    
    #plot n bunches
    spint.plot(x_axis, hldict[moment]['n_bunches']['b2'], '.r', markersize=markersize)
    spint.plot(x_axis, hldict[moment]['n_bunches']['b2'], '.b', markersize=markersize) 
    
    
    varnames = dict_hl_groups[group_name]
     
    for i_var, var in enumerate(varnames):
        colorcurr = ms.colorprog(i_prog=i_var, Nplots=len(varnames), cm=args.colormap)
        
        normhl = hldict[moment]['heat_load']['ldb_naming'][var]/(hldict[moment]['intensity']['b1']+\
                        hldict[moment]['intensity']['b2'])
        
        if args.normtointensity:
            to_plot = normhl
        else:
            to_plot = hldict[moment]['heat_load']['ldb_naming'][var]

        # plot heatload
        sphlcell.plot(x_axis, to_plot, '.', color = colorcurr, markersize=markersize)
        
        #plot integrated
        integ_hl_this = np.cumsum(hldict['hl_integrated']['ldb_naming'][var])
        spinteg.plot(integ_hl_this, normhl, '.', color=colorcurr, markersize=markersize)
        

    


for sp in [spint, sphlcell, spinteg]:
    sp.grid('on')
    sp.set_ylim(bottom=0)


pl.show()
