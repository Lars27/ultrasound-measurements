# Acquire ultrasound data from Picoscope 5000
#
# Based on PS5000A BLOCK MODE EXAMPLE from Pico Technology Ltd. 
# 
# Lars Hoff, USN, Sep 2022

import ctypes
import time
import numpy as np
import matplotlib.pyplot as plt
import ps5000a_ultrasound_wrappers as ps
import us_utilities as us
      
def plot_trace(t,v):
    plt.plot(t*1e6, v)
    plt.xlabel('Time [us]')
    plt.ylabel('Voltage [V]')
    plt.grid(True)
 

#%% Initialise and open 
dso =ps.communication( ) 

try:
    if "openunit" in status:
        if not("close" in status):        
            ps.stop_adc(dso.handle, status)
            ps.close_adc(dso.handle, status)
    #status = {}
except NameError:
    status = {}

#dsohandle = ctypes.c_int16()
status, dso = ps.open_adc(dso, status)

ch = []
ch.append(ps.channel( 0 ) )
ch.append(ps.channel( 1 ) )

sampling = ps.horizontal()
trigger  = ps.trigger()
    

#%% Configure ADC
ch[0].vr = 100e-3
ch[1].vr = 10e-3
status = ps.set_vertical( dso.handle, status, ch[0] )
status = ps.set_vertical( dso.handle, status, ch[1] )

trigger.source = "A"
trigger.level  = 0.5
trigger.adcmax = dso.maxADC
status = ps.set_trigger( dso.handle, status, trigger, ch, sampling )

sampling.timebase   = 3
sampling.ns         = 20000
sampling.pretrigger = 0.0
sampling.dt   = ps.get_dt(dso.handle, sampling)


#%% Capture data block
v = np.zeros((sampling.ns, 2))
status, dso = ps.configure_acquisition( dso, status, sampling )

print( 'Picoscope configured. Starting sampling' )
for k in range(10):
    print ( k )
    status, dso, v = ps.acquire_trace(dso, status, sampling, ch )

    wfm    = us.waveform()
    wfm.y  = v
    wfm.dt = sampling.dt
    wfm.t0 = sampling.t0()
    
    wfm.nfft = 2048
    
    plt.figure(1,(8,8))
    wfm.plot( timeunit="us" )
    plt.show()

#%% Close and disconnect 
status = ps.stop_adc ( dso.handle, status )
status = ps.close_adc( dso.handle, status )
print( 'Instrument closed' )

