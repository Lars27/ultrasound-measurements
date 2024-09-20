# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 16:29:01 2024

@author: lah
"""

import keyboard
import matplotlib.pyplot as plt
import ultrasound_utilities as us
import sounddevice as sd

wfm = us.Waveform()         # Result, storing acquired traces
rf_filter = us.WaveformFilter()  # Filtering, for display only
resultfile = us.ResultFile()

# %% Set up recording
devices = sd.query_devices()  # Returnl ist of available devices

fs = 8000  # [Hz] Sample rate
duration = 0.5  # [s] Duration of each recording
f_max = 1000  # Max. frequwncy to display

sd.default.device = 1    # Device to record from, see list in devices
sd.default.samplerate = fs
sd.default.channels = 1  # Chech that this is available, see list in devices

# RF-filter, for display only.Two-way zero-phase Butterworth
rf_filter.sample_rate = fs
rf_filter.type = 'AC'           # 'No', 'AC', 'BPF'
rf_filter.f_min = 0.5e6         # Lower cutoff, Hz
rf_filter.f_max = 20e6          # Upper cutoff, Hz
rf_filter.order = 2

# %% Acquire from sound card to Waveform variable
wfm.dt = 1/fs
wfm.t0 = 0
while (True):
    wfm.y = sd.rec(int(duration * fs))
    sd.wait()  # Wait until recording is finished

    wfm_filtered = wfm.filtered(rf_filter)
    wfm_filtered.plot_spectrum(time_unit="s", f_max=f_max,
                               normalise=True, scale="dB", db_min=-40)
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
