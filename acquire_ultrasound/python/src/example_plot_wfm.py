"""Analysis program made for USN ultrasound lab.

Load and display waveform measurement
Basic script, no GUI

"""

# %% Libraries
import numpy as np
import matplotlib.pyplot as plt
import ultrasound_utilities as us

wfm = us.Waveform()              # Result, storing acquired traces
resultfile = us.ResultFile()

filename = "../results/ustest_2024_12_02_0014.trc"
wfm.load(filename)

ax = wfm.plot_spectrum(time_unit="ms", ch=[0])
ax[1].set_xlim(0, 1)
