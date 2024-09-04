
"""Analysis program made for USN ultrasound lab.

Investigate and save traces from single-element ultrasound transducers using
Picoscope 5000-series osciloscopes.
Basic script, no GIU

Operation
    Initialise Picoscope
    Sample one trace and display in grapg
    Close Picoscope

coding: utf-8 -*-
Created on Tue Dec 20 22:20:43 2022
@author: larsh

"""

# %% Libraries

import keyboard
import us_utilities as us
import ps5000a_ultrasound_wrappers as ps

# Initialise instrument variables.
dso = ps.Communication()    # Instrument connection and status.
ch = [ps.Channel(0),
      ps.Channel(1)]        # Vertical channel configuration
trigger = ps.Trigger()      # Trigger configuration
sampling = ps.Horizontal()  # Horisontal configuration (time)

wfm = us.Waveform()         # Result, storing acquired traces
rf_filter = us.WaveformFilter()  # Filtering, for display only
resultfile = us.ResultFile()

# Connect oscilloscope
# Controlled by dso
# Try to close if an old handle is still resident. May not work
try:
    if "openunit" in status:
        if not ("close" in status):
            ps.stop_adc(dso, status)
            ps.close_adc(dso, status)
            status = {}
except AttributeError:
    status = {}

if dso.connected:
    # Configure vertical settings
    # Controlled by ch
    ch[0].enabled = True  # Display or not, traces are always aquired
    ch[0].v_range = 1.0            # Requested vertical range in Volts
    ch[0].v_range = ch[0].v_max()  # Adjust to allowed range in Picoscope
    ch[0].coupling = 'DC'          # 'DC', 'AC'
    ch[0].offset = 0.0         # 'None','20 MHz', bandwidth limit in Picoscope
    ch[0].bwl = 'None'

    ch[1].enabled = True
    ch[1].v_range = 1.0
    ch[1].v_range = ch[1].v_max()
    ch[1].coupling = 'DC'
    ch[1].offset = 0.0
    ch[1].bwl = 'None'

    # Configure trigger settings
    trigger.source = 'EXT'     # 'A', 'B', 'EXT', 'Internal'
    trigger.enable = trigger.source.lower()[0:3] != 'int'
    trigger.position = 10          # Relative position in %
    trigger.direction = 'Rising'   # 'Rising', 'Falling'
    trigger.level = 0.5            # Absolute level, Volts
    trigger.delay = 0              # Delay in s
    trigger.autodelay = 10e-3      # Automatic trigger, s

    # Configure sampling (Horizontal scale)
    sampling.pretrigger = trigger.position/100  # Convert from %
    sampling.timebase = 3      # Sets sample rate, see Picoscope documentation
    sampling.n_samples = 20e3  # No. of samples in single teace

    # Configure RF-filter, for display only
    # Two-way zero-phase Butterworth filter
    rf_filter.sample_rate = sampling.fs()
    rf_filter.type = 'No filter'    # 'No filter', 'AC', 'Bandpass'
    rf_filter.f_min = 0.5e6         # Lower cutoff, Hz
    rf_filter.f_max = 20e6          # Upper cutoff, Hz
    rf_filter.order = 2

    # Find filename for saving results

    # Send settings to Picoscope
    for k in range(len(ch)):
        ch[k].no = k
        status = ps.set_vertical(dso, status, ch[k])

    status = ps.set_trigger(dso, status, trigger, ch, sampling)
    sampling.dt = ps.get_sample_interval(dso, sampling)
    status, dso = ps.configure_acquisition(dso, status, sampling)

    # Acquire traces
    wfm.t0 = sampling.t0()
    wfm.dt = sampling.dt
    while (True):
        status, dso, wfm.y = ps.acquire_trace(dso, status, sampling, ch)
        wfm.plot_spectrum(f_max=10e6)

        if keyboard.is_pressed('s'):
            resultfile = us.find_filename(prefix='ustest',
                                          ext='trc',
                                          resultdir='results')

            wfm.save(resultfile.path)

        if keyboard.is_pressed('q'):
            print('Program terminated by user')
            break

    # Close instrument connection
    status = ps.close_adc(dso, status)
else:
    print('Could not connect to instrument')
