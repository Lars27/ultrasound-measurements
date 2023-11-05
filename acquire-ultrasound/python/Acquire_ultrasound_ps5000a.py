# Acquire ultrasound data from Picoscope 5000
#
# Based on PS5000A BLOCK MODE EXAMPLE from Pico Technology Ltd. 
# 
# Lars Hoff, USN, Sep 2022

import ctypes
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
try:
    if "openunit" in status:
        if not("close" in status):        
            ps.stop_adc(dsohandle, status)
            ps.close_adc(dsohandle, status)
    #status = {}
except NameError:
    status = {}

dsohandle = ctypes.c_int16()
status, adcmax= ps.open_adc(dsohandle, status)

ch = []
ch.append(ps.dso_channel(0, 10, adcmax ))
ch.append(ps.dso_channel(1, 10, adcmax ))

sampling = ps.dso_horizontal()
trigger  = ps.dso_trigger("A", 0.5)
    

#%% Configure ADC
ch[0].vr = 1
ch[1].vr = 10
status, ch[0] = ps.set_vertical(dsohandle, status, ch[0])
status, ch[1] = ps.set_vertical(dsohandle, status, ch[1])

trigger.source = "B"
trigger.level  = 0.5
trigger.adcmax = adcmax
status = ps.set_trigger(dsohandle, status, trigger, ch)

sampling.timebase   = 3
sampling.ns         = 500
sampling.pretrigger = 0.1
#sampling.nmax = sampling.ns
sampling.dt   = ps.get_dt(dsohandle, sampling)


#%% Capture data block
v = np.zeros((sampling.ns, 2))
for k in [0,1]:
    status, v[:,k], n_recorded= ps.acquire_trace(dsohandle, status, sampling, ch[k])
   

#%% Close and disconnect 
status = ps.stop_adc(dsohandle, status)
status = ps.close_adc(dsohandle, status)
print(status)

#%% Plot results
wfm = us.waveform(v, sampling.dt, sampling.t0())
wfm.nfft = 4096

plt.figure(1,(8,8))
wfm.plotspectrum( timescale="us", freqscale="MHz", fmax=10, normalise=True, scale="db" )
