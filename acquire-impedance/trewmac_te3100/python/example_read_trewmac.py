# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 14:17:40 2022

@author: lah
"""

import numpy as np
import matplotlib.pyplot as plt
import trewmac300x_serial as te


port   = 'COM7'
fmin   = 100e3
fmax   = 15e6
npts   = 100
avg    = 16
output = 50
z0     = 50

# plt.figure(1,(8,8))

# fig, (ax1) = plt.subplots(1, 1)
# #ax1 = plt.axes(xlim=( 0, 1.1*fmax/1e6 ), ylim=(-1, 1))
# magplot= ax1.plot( [1,2], [3,4] )
# ax1.set_xlabel( 'Frequency [MHz]' )
# ax1.set_ylabel( 'Impedance magnitude [Ohm]')
# ax1.grid(True)
# plt.show()
# #fig.canvas.draw()

# =============================================================================
# phaseplot= ax2.plot( [0], [0] )
# ax2.xlim( 0, fmax/1e6 )
# ax2.ylim( -90, 90)
# ax2.xlabel( 'Frequency [MHz]' )
# ax2.ylabel( 'Impedance phase [Deg]')
# ax2.grid(True)
# ax2.show()
# =============================================================================

#%%
analyser  = te.te300x()
errorcode = analyser.connect( port = 'COM7', timeout = 5 )
ver       = analyser.read_version()
frange_ok = analyser.set_frequencyrange( fmin, fmax, npts )
avg       = analyser.set_averaging ( avg )
output    = analyser.set_output ( output )
z0        = analyser.set_z0 ( z0 )
sweep_ok  = analyser.read_sweep()

res = analyser.res

ok = analyser.close()

