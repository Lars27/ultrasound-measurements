
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
import matplotlib.pyplot as plt
import ultrasound_utilities as us
import ps5000a_ultrasound_wrappers as ps

# Initialise instrument variables.
dso = ps.Communication()    # Connection to Picoscope
channel = [ps.Channel(0),
           ps.Channel(1)]   # Vertical channel configuration
trigger = ps.Trigger()      # Trigger configuration
sampling = ps.Horizontal()  # Horisontal configuration (time)

wfm = us.Waveform()         # Result, storing acquired traces
rf_filter = us.WaveformFilter()  # Filtering, for display only
resultfile = us.ResultFile()

# %% Connect oscilloscope. Controlled by dso, run if connected successfully

# Try to close if an old handle is still resident. May not work
try:
    if "openunit" in dso.status:
        if not ("close" in dso.status):
            ps.stop_adc(dso)
            ps.close_adc(dso)
            dso.status = {}
except AttributeError:
    dso.status = {}

dso = ps.open_adc(dso)

if dso.connected:
    # %% Configure oscilloscope
    # Vertical
    channel[0].enabled = True    # Display, traces are always aquired
    channel[0].v_range = 0.5     # Requested vertical range [V]
    channel[0].v_range = channel[0].v_max()  # Adjust to allowed Picoscoperange
    channel[0].coupling = 'DC'   # 'DC', 'AC'
    channel[0].offset = 0.0      # Offset voltage [V]
    channel[0].bwl = True        # Boolean, activates 20 MHz hardware limit

    channel[1].enabled = False
    channel[1].v_range = 0.5
    channel[1].v_range = channel[1].v_max()
    channel[1].coupling = 'DC'
    channel[1].offset = 0.0
    channel[1].bwl = True

    # Trigger
    trigger.source = 'EXT'     # 'A', 'B', 'EXT', 'Internal'
    trigger.enable = trigger.source.lower()[0:3] != 'int'
    trigger.position = 10          # Relative position [%]
    trigger.direction = 'Rising'   # 'Rising', 'Falling'
    trigger.level = 0.5            # Absolute level  [V]
    trigger.delay = 0              # Delay [s]
    trigger.autodelay = 10e-3      # Automatic trigger  [s]

    # Sampling (Horizontal scale)
    sampling.pretrigger = trigger.position  # Samples before trigger
    sampling.timebase = 3      # Sets sample rate, see Picoscope documentation
    sampling.n_samples = 10000  # No. of samples in single teace

    # RF-filter, for display only.Two-way zero-phase Butterworth
    rf_filter.sample_rate = sampling.fs()
    rf_filter.type = 'No'           # 'No', 'AC', 'BPF'
    rf_filter.f_min = 0.5e6         # Lower cutoff, Hz
    rf_filter.f_max = 20e6          # Upper cutoff, Hz
    rf_filter.order = 2

    # %% Send settings to Picoscope and aquire traces
    for k in range(len(channel)):
        channel[k].no = k
        dso.status = ps.set_vertical(dso, channel[k])
        dso.status = ps.set_bwl(dso, channel[k])

    dso.status = ps.set_trigger(dso, trigger, channel, sampling)
    sampling.dt = ps.get_sample_interval(dso, sampling)
    dso = ps.configure_acquisition(dso, sampling)

    wfm.t0 = sampling.t0()
    wfm.dt = sampling.dt
    while (True):
        dso, wfm.y = ps.acquire_trace(dso, sampling, channel)
        wfm_filtered = wfm.filtered(rf_filter)
        wfm_filtered.plot_spectrum(f_max=40e6)
        plt.show()

        if keyboard.is_pressed('s'):
            resultfile = us.find_filename(prefix='ustest',
                                          ext='trc',
                                          resultdir='results')

            wfm.save(resultfile.path)
            print(f'Result saved to {resultfile.name}')

        if keyboard.is_pressed('q'):
            print('Program terminated by user')
            break

    # Close instrument connection
    dso.status = ps.stop_adc(dso)
    dso.status = ps.close_adc(dso)

# %% Exit if unsuccessful
else:
    print('Could not connect to instrument')
