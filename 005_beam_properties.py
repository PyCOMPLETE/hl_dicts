from __future__ import print_function, division

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

import LHCMeasurementTools.mystyle as ms
import LHCMeasurementTools.TimestampHelpers as TH
from LHC_Heat_load_dict import mask_dict, main_dict

plt.close('all')
moment = 'stop_squeeze'
mask = np.logical_and(main_dict[moment]['n_bunches']['b1'] > 800, main_dict[moment]['n_bunches']['b2'] > 800)
main_dict = mask_dict(main_dict,mask)

date_on_xaxis = True
filln_range = None # Tuple of min / max fill
fontsz = 16
markersize = 10
ms.mystyle_arial(fontsz=fontsz)#, dist_tick_lab=10)

if date_on_xaxis:
    time_in = 'datetime'
    t_plot_tick_h = None #'4weeks'
    time_conv = TH.TimeConverter(time_in, t_plot_tick_h=t_plot_tick_h)
    tc = time_conv.from_unix
    x_axis = tc(main_dict[moment]['t_stamps'])
else:
    x_axis = main_dict['filln']

fig1 = ms.figure('Beam properties')
sp1 = plt.subplot(4,1,1)
sp1.plot(x_axis, main_dict[moment]['n_bunches']['b1'],'.', markersize=markersize)
sp1.plot(x_axis, main_dict[moment]['n_bunches']['b2'],'r.', markersize=markersize)
sp1.set_ylabel('N bunches')
sp1.set_ylim(800, 2400)

sp2 = plt.subplot(4,1,2,sharex=sp1)
sp2.plot(x_axis, main_dict['bpi'],'.', markersize=markersize)
sp2.set_ylabel('Bpi')
sp2.set_ylim(60, 150)

sp3 = plt.subplot(4,1,3, sharex=sp1)
sp3.plot(x_axis, main_dict[moment]['intensity']['b1']/main_dict[moment]['n_bunches']['b1'],'b.', markersize=markersize)
sp3.plot(x_axis, np.array(main_dict[moment]['intensity']['b2'])\
/np.array(main_dict[moment]['n_bunches']['b2']),'r.', markersize=markersize)
sp3.set_ylabel('Bunch Intensity')
sp3.set_ylim(0.6e11, 1.3e11)

sp4 = plt.subplot(4,1,4, sharex=sp1)
sp4.plot(x_axis, main_dict[moment]['blength']['b1']['avg'],'b.', markersize=markersize)
sp4.plot(x_axis, main_dict[moment]['blength']['b2']['avg'],'r.', markersize=markersize)
sp4.set_ylabel('Bunch length')
sp4.set_ylim(1e-9, 1.4e-9)

if date_on_xaxis:
    time_conv.set_x_for_plot(fig1, sp1)
else:
    sp4.set_xlabel('Fill nr')
    sp4.xaxis.set_major_locator(ticker.MultipleLocator(100))

for sp in (sp1,sp2,sp3):
    plt.setp(sp.get_xticklabels(), visible = False)

sp1.grid('on')
sp2.grid('on')
sp3.grid('on')
sp4.grid('on')


fig1.suptitle('At '+moment)
fig1.subplots_adjust(right=0.7, left=0.15)

plt.show()
