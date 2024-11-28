"""Analysis program made for USN ultrasound lab.

Investigate and save traces from single-element ultrasound transducers using
Picoscope 2000-series osciloscopes.
Basic script, no GIU

Operation
    Initialise Picoscope
    Loop:
        Sample traces
        Display in graph
    Close Picoscope
"""

# %% Libraries
import keyboard
import matplotlib.pyplot as plt
import ultrasound_utilities as us
import ps2000a_ultrasound_wrappers as ps

print()
print("Starting program")

# Initialise instrument variables.
dso = ps.Communication()    # Connection to Picoscope

channel = [ps.Channel(k) for k in range(ps.N_CHANNELS)]  # Vertical
trigger = ps.Trigger()           # Trigger
sampling = ps.Horizontal()       # Horisontal (time)

wfm = us.Waveform()              # Result, storing acquired traces
rf_filter = us.WaveformFilter()  # Filter, for display only
resultfile = us.ResultFile()     # Filename for results,
pulse = us.Pulse()               # Signal generator (AWG)


# %% Open and configure oscilloscope
print("Connecting instrument")
dso = ps.open_adc(dso)          # Instument connection

if dso.connected:
    print("Connecton ok. Configuring instrument")

    # Vertical
    channel[0].v_range = 10e-3
    channel[1].v_range = 0.1
    channel[2].v_range = 0.1
    channel[3].v_range = 10e-3

    channel[0].enabled = True
    channel[1].enabled = True
    channel[2].enabled = True
    channel[3].enabled = True

    # Trigger
    trigger.source = "B"           # 'A', 'B', 'C', 'D', 'Internal'
    trigger.direction = 'Rising'   # 'Rising', 'Falling'
    trigger.level = 0.1            # Absolute level  [V]
    trigger.delay = 0              # Delay [s]
    trigger.autodelay = 10e-3      # Automatic trigger  [s]

    # Sampling (Horizontal scale)
    fs_requested = 20e3   # [Hz] Sample rate will be modified to permitted
    timebase, fs_actual = ps.find_timebase(fs_requested)
    print(f"Sample rate {fs_actual*1e-3:.2f} kHz")

    sampling.trigger_position = 10  # Relative position [%]
    sampling.timebase = timebase   # Defines sample rate, see documentation
    sampling.n_samples = 10000   # No. of samples in single trace

    # RF-filter, for display only.Two-way zero-phase Butterworth
    rf_filter.type = 'No'       # 'No', 'AC', 'BPF'
    rf_filter.f_min = 10         # Lower cutoff, Hz
    rf_filter.f_max = 4e3        # Upper cutoff, Hz
    rf_filter.order = 1

    # Check for signal generator
    dso = ps.check_awg(dso)

    # %% Send settings to Picoscope and aquire traces
    print("Setting vertical resolution")
    channel_display = []
    for k in range(len(channel)):
        channel[k].no = k
        dso.status = ps.set_vertical(dso, channel[k])

        if channel[k].enabled:
            channel_display.append(k)

    # Trigger
    print("Setting trigger")
    dso.status = ps.set_trigger(dso, trigger, channel, sampling)
    sampling.dt = ps.get_sample_interval(dso, sampling)
    rf_filter.sample_rate = sampling.fs()

    # Acquisition
    print("Setting up acquisition")

    dso = ps.configure_acquisition(dso, sampling)

    wfm.t0 = sampling.t0()
    wfm.dt = sampling.dt

    # %% Define figure and format axes
    plt.ion()   # Interactive on, may not make a difference
    fig = plt.figure(figsize=[16, 6])

    ax_time = [fig.add_subplot(2, ps.N_CHANNELS, 1+k)
               for k in range(ps.N_CHANNELS)]

    ax_spectrum = [fig.add_subplot(2, ps.N_CHANNELS, ps.N_CHANNELS+1+k)
                   for k in range(ps.N_CHANNELS)]

    for k in range(ps.N_CHANNELS):
        y_max = channel[k].v_range
        ax_time[k].set(title=f"Channel {channel[k].name()}",
                       xlabel="Time [s]",
                       ylim=(-y_max, y_max))
        ax_time[k].grid(True)

        ax_spectrum[k].set(xlabel="Frequency [Hz]",
                           xlim=(0, 1000),
                           ylim=(-40, 0))
        ax_spectrum[k].grid(True)

    ax_time[0].set(ylabel="Voltage [V]")
    ax_spectrum[0].set(ylabel="dB re. max")
    fig.show()

    # %% Loop to acquire pulses
    print("Acquiring results. Press'q' to stop")

    first = True
    while (True):
        # Acquire and filter results
        dso, wfm.y = ps.acquire_trace(dso, sampling, channel)

        wfm_filtered = wfm.filtered(rf_filter)
        t = wfm_filtered.t()
        y = wfm_filtered.y
        f, psd = wfm_filtered.powerspectrum(normalise=True,
                                            scale="dB", upsample=2)
        # Display results
        if first:   # Create list of plots from first measurement

            time_plot = [ax_time[k].plot(t, y[:, k])[0]
                         for k in range(ps.N_CHANNELS)]

            psd_plot = [ax_spectrum[k].plot(f, psd[:, k])[0]
                        for k in range(ps.N_CHANNELS)]

            first = False
        else:   # Update existing figure with new values
            for k in range(ps.N_CHANNELS):
                time_plot[k].set_xdata(t)
                time_plot[k].set_ydata(y[:, k])

                psd_plot[k].set_xdata(f)
                psd_plot[k].set_ydata(psd[:, k])

        fig.canvas.draw()
        fig.canvas.flush_events()

        # Check for keyboard commands
        if keyboard.is_pressed('s'):
            resultfile = us.find_filename(prefix='ustest',
                                          ext='trc',
                                          resultdir='results')

            wfm.save(resultfile.path)
            print(f'Result saved to {resultfile.name}')

        if keyboard.is_pressed('q'):
            print('Program terminated by user')
            print('')
            break

    # Close instrument connection
    dso.status = ps.stop_adc(dso)
    dso.status = ps.close_adc(dso)

# %% Exit if unsuccessful
else:
    print('Could not connect to instrument')
