"""Analysis program made for USN ultrasound lab.

Investigate and save traces from single-element ultrasound transducers using
Picoscope 5000-series osciloscopes.
GUI interface made in Qt Designer, ver. 5.
Based on earlier NI LabWindows, LabVIEW and Matlab programs. Result file format
is compatible with these, but smaller modifications may be
required in some cases.

Operation
    Sets up a GUI to control the system
    Continously reads traces from the oscilloscope
    Includes an arbitrary waveform generator to transmit shaped pulses

coding: utf-8 -*-
Created on Tue Dec 20 22:20:43 2022
@author: larsh

"""

# %% Libraries

# General
import sys
from PyQt5 import QtWidgets, uic           # For setup with Qt
import numpy as np
import matplotlib
import matplotlib.colors as mcolors
import ultrasound_utilities as us         # USN ultrasound lab specific
import ps5000a_ultrasound_wrappers as ps  # Interface to Pico c-style library


# Constants
COLOR_WARNING = ["white", "red"]    # [Text, Background]
COLOR_OK = ["white", "darkgreen"]
COLOR_NEUTRAL = ["black", "white"]
COLOR_CH = [mcolors.TABLEAU_COLORS['tab:blue'],
            mcolors.TABLEAU_COLORS['tab:red']]
COLOR_AWG = mcolors.TABLEAU_COLORS['tab:green']
COLOR_MARKER = mcolors.TABLEAU_COLORS['tab:cyan']
COLOR_MARKER_PATCH = mcolors.CSS4_COLORS['azure']
COLOR_AWG_BACKGROUND = mcolors.CSS4_COLORS['mintcream']

TIMESCALE = 1E-6      # Display scales for time and frequency
FREQUENCYSCALE = 1E6

V_MAX = 20           # Absolute maximum voltage scale


# %% Set up GUI from Qt5
matplotlib.use('Qt5Agg')
oscilloscope_main_window, QtBaseClass = uic.loadUiType(
    'aquire_ultrasound_gui.ui')


# %% Classes

class Display:
    """Settings for display on screen during runtime."""

    t_min = 0               # [s] Zoomed section, pulse to be analysed
    t_max = 10              # [s]
    channel = [True, True]  # Channels to display on screen


class AcquisitionControl:
    """Flags to control running of program."""

    oscilloscope_ready = False   # Osciloscope connected and ready to acquire
    stop_acquisition = False     # Stop data acquisition, do not quit program
    sampling_changed = True      # Sampling updated


class ReadUltrasound(QtWidgets.QMainWindow, oscilloscope_main_window):
    """Start GUI and initialise system."""

    def __init__(self):
        """Set up GUI and initialise classes and variables."""
        QtWidgets.QMainWindow.__init__(self)
        oscilloscope_main_window.__init__(self)     # Qt GUI window
        self.setupUi(self)

        # Initialise instrument variables.
        self.runstate = AcquisitionControl()
        self.display = Display()         # Scaling and display options
        self.dso = ps.Communication()    # Instrument connection and status.
        self.channel = [ps.Channel(0),
                        ps.Channel(1)]        # Vertical channel configuration
        self.trigger = ps.Trigger()      # Trigger configuration
        self.sampling = ps.Horizontal()  # Horisontal configuration (time)
        self.wfm = us.Waveform()         # Result, storing acquired traces
        self.pulse = us.Pulse()          # Pulse for function generator output
        self.rf_filter = us.WaveformFilter()  # Filtering, for display only
        self.pulse.dt = 1/ps.DAC_SAMPLERATE

        # OPen gui and connect initailse graphs
        self.connect_gui()
        fig, axis, graph = self.define_graphs()
        self.fig = fig
        self.axis = axis
        self.graph = graph

        self.update_connected_box("Not Connected", COLOR_WARNING)
        self.acquireButton.setEnabled(False)
        self.transmitButton.setEnabled(False)
        self.saveButton.setEnabled(False)

# %% Connect and disconnect oscilloscope

    def connect_dso(self):
        """Connect, configure and start instrument."""
        self.statusBar.showMessage('Connecting instrument')
        errorcode = 0

        # Try to close if an old handle is still resident. May not work
        try:
            if "openunit" in self.dso.status:
                if not ("close" in self.dso.status):
                    ps.stop_adc(self.dso, self.dso.status)
                    ps.close_adc(self.dso, self.dso.status)
            self.dso.status = {}
        except AttributeError:
            self.dso.status = {}

        # Connect and initialise instrument
        self.dso = ps.open_adc(self.dso)

        if self.dso.connected:
            # Send initial configuration to oscilloscope
            self.dso.status = self.update_vertical()
            self.dso.status = self.update_trigger()

            # Update configuration parameters
            self.update_sampling()
            self.update_pulser()
            self.update_rf_filter()
            self.update_display()

            # Update GUI status
            self.acquireButton.setEnabled(True)
            self.saveButton.setEnabled(False)
            self.connectButton.setEnabled(False)
            self.transmitButton.setEnabled(False)

            self.statusBar.showMessage("Instrument connected")
            self.update_connected_box("Connected",  COLOR_OK)
            self.runstate.oscilloscope_ready = True
            self.runstate.stop_acquisition = False
            errorcode = 0
        else:
            self.statusBar.showMessage("Instrument not connected")
            self.update_connected_box("Not Connected", COLOR_WARNING)
            self.runstate.oscilloscope_ready = False
            self.runstate.stop_acquisition = False
            errorcode = -1
        return errorcode

    def close_connection(self):
        """Close instrument connection, does not stop program."""
        self.statusBar.showMessage("Closing")
        matplotlib.pyplot.close(self.fig)
        try:
            self.dso.status = ps.close_adc(self.dso)
            errorcode = 0
        except ValueError:
            errorcode = -1
        finally:
            self.close()

        self.statusBar.showMessage('Closed')
        return self.dso.status, errorcode

# %% Update oscilloscope settings

    def update_vertical(self):
        """Read vertical settings from GUI and send to instrument."""
        self.channel[0].enabled = True  # Both traces are always aquired
        self.channel[1].enabled = True

        for k in range(len(self.channel)):
            self.channel[k].v_range = us.read_scaled_value(
                                      self.rangeComboBox[k].currentText())
            self.channel[k].v_range = self.channel[k].v_max()
            self.channel[k].coupling = self.couplingComboBox[k].currentText()
            self.channel[k].offset = self.offsetSpinBox[k].value()

            bwl = self.bwlComboBox[k].currentText()
            self.channel[k].bwl = bwl.lower()[0:2] != 'no'

        if self.dso.connected:
            for k in range(len(self.channel)):
                self.channel[k].no = k
                self.dso.status = ps.set_vertical(self.dso, self.channel[k])
                self.dso.status = ps.set_bwl(self.dso, self.channel[k])

        return self.dso.status

    def update_trigger(self):
        """Read trigger settings from GUI and send to instrument."""
        self.trigger.source = self.triggerSourceComboBox.currentText()
        self.trigger.enable = self.trigger.source.lower()[0:3] != 'int'
        self.trigger.position = self.triggerPositionSpinBox.value()
        self.trigger.direction = self.triggerModeComboBox.currentText()
        self.trigger.level = self.triggerLevelSpinBox.value()
        self.trigger.delay = self.triggerDelaySpinBox.value()*TIMESCALE
        self.trigger.autodelay = self.triggerAutoDelaySpinBox.value()*1e-3
        self.sampling.pretrigger = self.trigger.position/100  # Convert %

        if self.dso.connected:
            self.dso.status = ps.set_trigger(self.dso, self.trigger,
                                             self.channel, self.sampling)
        return self.dso.status

    def update_sampling(self):
        """Read trace length from GUI and set sample rate.

        This function does not communicate with instrument
        """
        self.sampling.timebase = 3
        self.sampling.n_samples = int(self.nSamplesSpinBox.value()*1e3)
        if self.dso.connected:
            self.sampling.dt = ps.get_sample_interval(self.dso, self.sampling)
            self.samplerateSpinBox.setValue(self.sampling.fs()/FREQUENCYSCALE)

        self.runstate.sampling_changed = True
        return 0

    def update_pulser(self):
        """Send pluse to arbitrary waveform generator.

        Read settings for arbitrary waveform generator (awg)
        Plot pulse and send to instrument
        """
        self.pulse.on = self.transmitButton.isChecked()
        self.pulse.envelope = self.pulseEnvelopeComboBox.currentText()
        self.pulse.shape = self.pulseShapeComboBox.currentText()
        self.pulse.f0 = self.pulseFrequencySpinBox.value()*FREQUENCYSCALE
        self.pulse.n_cycles = self.pulseDurationSpinBox.value()
        self.pulse.phase = self.pulsePhaseSpinBox.value()
        self.pulse.a = self.pulseAmplitudeSpinBox.value()

        t_max = self.pulse.duration() / TIMESCALE
        vlim = 1.1 * self.pulse.a
        f, psd = self.pulse.powerspectrum()
        self.graph['awg'].set_data(self.pulse.t()/TIMESCALE, self.pulse.y())
        self.axis['awg'].set_xlim(0, t_max)
        self.axis['awg'].set_ylim(-vlim, vlim)
        self.graph['awgspec'].set_data(f/FREQUENCYSCALE, psd)

        ps.set_signal(self.dso, self.sampling, self.pulse)
        for g in ['awg', 'awgspec']:
            if self.pulse.on:
                self.graph[g].set_linestyle("solid")
            else:
                self.graph[g].set_linestyle("dotted")
        self.update_display()
        self.update_transmit_box(self.pulse.on)

        return 0

    def update_rf_filter(self):
        """Read RF noise filter settings from GUI."""
        self.rf_filter.sample_rate = self.sampling.fs()
        self.rf_filter.type = self.filterComboBox.currentText()
        self.rf_filter.f_min = self.fminSpinBox.value()*FREQUENCYSCALE
        self.rf_filter.f_max = self.fmaxSpinBox.value()*FREQUENCYSCALE
        self.rf_filter.order = self.filterOrderSpinBox.value()
        return 0

# %% Acquire, display, and save results

    def control_acquisition(self):
        """Control data acquisition from oscilloscope."""
        if self.acquireButton.isChecked():
            self.acquire_trace()
        else:
            self.stop_acquisition()
        return 0

    def acquire_trace(self):
        """Acquire trace from instrument."""
        if self.runstate.oscilloscope_ready:
            self.runstate.oscilloscope_ready = False
            self.runstate_sampling_changed = True
            self.transmitButton.setEnabled(True)
            self.saveButton.setEnabled(True)
            self.closeButton.setEnabled(False)
            self.update_status_box("Acquiring", COLOR_OK)
            self.statusBar.showMessage("Acquiring data ...")
            while not (self.runstate.stop_acquisition):
                if self.runstate.sampling_changed:
                    self.dso = ps.configure_acquisition(self.dso,
                                                        self.sampling)
                    self.runstate.sampling_changed = False
                self.dso, self.wfm.y = ps.acquire_trace(self.dso,
                                                        self.sampling,
                                                        self.channel)
                self.wfm.dt = self.sampling.dt
                self.wfm.t0 = self.sampling.t0()
                self.plot_result()
        self.update_status_box("Stopped", COLOR_WARNING)
        self.statusBar.showMessage("Ready")
        self.runstate.stop_acquisition = False
        return 0

    def stop_acquisition(self):
        """Stop acquisition of traces without closing instrument connection."""
        if not (self.runstate.stop_acquisition):
            self.statusBar.showMessage("Stopping")
            self.update_status_box("Stopping", COLOR_WARNING)
        self.runstate.stop_acquisition = True
        self.runstate.oscilloscope_ready = True
        self.closeButton.setEnabled(True)
        self.saveButton.setEnabled(False)
        return 0

    def plot_result(self, time_unit="us"):
        """Plot measured trace on screen."""
        wfm_filtered = self.wfm.filtered(self.rf_filter)
        wfm_zoomed = wfm_filtered.zoomed(self.display.t_lim)
        f, psd = wfm_zoomed.powerspectrum(scale="dB", normalise="True")
        ch_no = 0
        for ch_name in ps.CH_NAMES:
            if self.display.channel[ch_no]:
                self.graph[ch_name][0].set_data(wfm_filtered.t()/TIMESCALE,
                                                wfm_filtered.y[:, ch_no])
                self.graph[ch_name][1].set_data(wfm_zoomed.t()/TIMESCALE,
                                                wfm_zoomed.y[:, ch_no])
                self.graph[ch_name][2].set_data(f/FREQUENCYSCALE,
                                                psd[:, ch_no])
            else:
                self.graph[ch_name][0].set_data([], [])  # Full trace
                self.graph[ch_name][1].set_data([], [])  # Selected interval
                self.graph[ch_name][2].set_data([], [])  # Power spectrum
            ch_no += 1
        # self.fig.canvas.draw()            # --- TRY: Probably necessary
        self.fig.canvas.flush_events()    # --- TRY: Probably unnecessary
        self.update_display()
        return 0

    def save_result(self):
        """Save measured traces and parameters to binary file.

        The filename is generated automatically from a short description,
        the date, and a counter.
        The file format is compatible with older LabVIEW and Matlab systems
        """
        self.statusBar.showMessage("Saving results ...")

        resultpath, resultdir, resultfile, n_result = us.find_filename(
                                                        prefix='US',
                                                        ext='trc',
                                                        resultdir='results')
        resultfile = us.find_filename(prefix='us',
                                      ext='trc',
                                      resultdir='results')

        self.wfm.save(resultfile.path)
        self.filecounterSpinBox.setValue(n_result)
        self.resultfileEdit.setText(resultfile)
        self.resultpathEdit.setText(resultpath)
        self.statusBar.showMessage(f'Result saved to {resultfile}')
        return 0

# %% General GUI read and write

    def update_status(self, message, append=False):
        """Update a the short status message field at the bottom of window."""
        if append:
            old_message = self.status_textEdit.toPlainText()
            message += old_message
        self.status_textEdit.setText(message)
        return message

    def update_status_box(self, message, color=COLOR_NEUTRAL):
        """Write message to status box, in optional colours."""
        self.statusEdit.setText(message)
        self.statusEdit.setStyleSheet(
            f"color:{color[0]}; background-color:{color[1]}")
        return 0

    def update_connected_box(self, message, color=COLOR_NEUTRAL):
        """Write status of the instrument connection."""
        self.connectedEdit.setText(message)
        self.connectedEdit.setStyleSheet(
           f"color:{color[0]}; background-color:{color[1]}")
        return 0

    def update_transmit_box(self, transmitting=False):
        """Write whether the waveform generator is transmitting pulses."""
        if transmitting:
            message = "Transmitting"
            color = COLOR_OK
        else:
            message = "OFF"
            color = COLOR_WARNING

        self.transmitStatusEdit.setText(message)
        self.transmitStatusEdit.setStyleSheet(
            f"color:{color[0]}; background-color:{color[1]}")
        return 0

    def find_voltagescale(self, vmax):
        """Find scale for voltage axis based on maximum value."""
        if vmax < 1e-3:
            voltage_scale = 1e-6
            unit = "uV"
        elif vmax < 1:
            voltage_scale = 1e-3
            unit = "mV"
        else:
            voltage_scale = 1
            unit = "V"
        return voltage_scale, unit

    def update_display(self, time_unit="us"):
        """Update values and markers on screen."""
        # Full trace
        self.axis["trace"][0].set_xlim(self.sampling.t0()/TIMESCALE,
                                       self.sampling.t_max()/TIMESCALE)

        # Selected interval, 'zoom'
        t_lim = us.find_limits([self.zoomStartSpinBox.value(),
                                self.zoomEndSpinBox.value()],
                               min_diff=0.1)
        for k in range(len(self.graph['marker'])):
            self.graph['marker'][k].set_data(np.full((2, 1),
                                             t_lim[k]),
                                             np.array([-V_MAX, V_MAX]))
        self.graph['patch'].set_bounds(t_lim[0],
                                       -V_MAX,
                                       t_lim[1]-t_lim[0],
                                       2*V_MAX)
        self.axis["zoom"][0].set_xlim(t_lim)
        self.display.t_lim = t_lim*TIMESCALE

        # Vertical scale
        db_lim = us.find_limits([self.dbMinSpinBox.value(),
                                self.dbMaxSpinBox.value()])
        for k in range(len(self.display.channel)):
            self.display.channel[k] = not self.chButton[k].isChecked()
            vzoom = us.read_scaled_value(
                                self.displayrangeComboBox[k].currentText())
            self.axis["zoom"][k].set_ylim(-vzoom, vzoom)
            self.axis["trace"][k].set_ylim(-self.channel[k].v_max(),
                                           self.channel[k].v_max())
            self.axis["spectrum"][k].set_ylim(db_lim)
        self.axis["awgspec"].set_ylim(db_lim)

        # Frequency axis
        f_lim = us.find_limits([self.zoomFminSpinBox.value(),
                               self.zoomFmaxSpinBox.value()],
                               min_diff=0.1)
        self.axis["spectrum"][0].set_xlim(f_lim)
        self.axis["awgspec"].set_xlim(f_lim)

        self.fig.canvas.draw()
        return 0

# %% Conect GUI to functions

    def connect_gui(self):
        """Connect functions to elements from GUI-file.

        The GUI elements use the QT naming convention (camelCase)
        """
        # Display
        self.zoomStartSpinBox.valueChanged.connect(self.update_display)
        self.zoomEndSpinBox.valueChanged.connect(self.update_display)
        self.zoomFminSpinBox.valueChanged.connect(self.update_display)
        self.zoomFmaxSpinBox.valueChanged.connect(self.update_display)
        self.dbMinSpinBox.valueChanged.connect(self.update_display)
        self.dbMaxSpinBox.valueChanged.connect(self.update_display)

        # RF filter
        self.filterComboBox.activated.connect(self.update_rf_filter)
        self.fminSpinBox.valueChanged.connect(self.update_rf_filter)
        self.fmaxSpinBox.valueChanged.connect(self.update_rf_filter)
        self.filterOrderSpinBox.valueChanged.connect(self.update_rf_filter)

        # Oscilloscope vertical, 2 channels, A and B
        self.chButton = [self.chAButton, self.chBButton]
        self.chLabel = [self.chALabel, self.chBLabel]
        self.displayrangeComboBox = [self.displayrangeAComboBox,
                                     self.displayrangeBComboBox]
        self.rangeComboBox = [self.rangeAComboBox,
                              self.rangeBComboBox]
        self.couplingComboBox = [self.couplingAComboBox,
                                 self.couplingBComboBox]
        self.offsetSpinBox = [self.offsetASpinBox,
                              self.offsetBSpinBox]
        self.couplingComboBox = [self.couplingAComboBox,
                                 self.couplingBComboBox]
        self.bwlComboBox = [self.bwlAComboBox,
                            self.bwlBComboBox]

        for k in range(len(self.chButton)):
            self.rangeComboBox[k].activated.connect(self.update_vertical)
            self.couplingComboBox[k].activated.connect(self.update_vertical)
            self.offsetSpinBox[k].valueChanged.connect(self.update_vertical)
            self.couplingComboBox[k].activated.connect(self.update_vertical)
            self.bwlComboBox[k].activated.connect(self.update_vertical)
            self.chButton[k].clicked.connect(self.update_display)
            self.displayrangeComboBox[k].activated.connect(self.update_display)

        # Oscilloscope trigger
        self.triggerSourceComboBox.activated.connect(self.update_trigger)
        self.triggerPositionSpinBox.valueChanged.connect(self.update_trigger)
        self.triggerModeComboBox.activated.connect(self.update_trigger)
        self.triggerLevelSpinBox.valueChanged.connect(self.update_trigger)
        self.triggerDelaySpinBox.valueChanged.connect(self.update_trigger)
        self.triggerAutoDelaySpinBox.valueChanged.connect(self.update_trigger)

        # Oscilloscope horizontal (Time)
        self.samplerateSpinBox.valueChanged.connect(self.update_sampling)
        self.nSamplesSpinBox.valueChanged.connect(self.update_sampling)

        # Pulse generator (awg)
        self.transmitButton.clicked.connect(self.update_pulser)
        self.pulseEnvelopeComboBox.activated.connect(self.update_pulser)
        self.pulseShapeComboBox.activated.connect(self.update_pulser)
        self.pulseFrequencySpinBox.valueChanged.connect(self.update_pulser)
        self.pulseDurationSpinBox.valueChanged.connect(self.update_pulser)
        self.pulsePhaseSpinBox.valueChanged.connect(self.update_pulser)
        self.pulseAmplitudeSpinBox.valueChanged.connect(self.update_pulser)

        # Program flow
        self.connectButton.clicked.connect(self.connect_dso)
        self.acquireButton.clicked.connect(self.control_acquisition)
        self.saveButton.clicked.connect(self.save_result)
        self.closeButton.clicked.connect(self.close_connection)

        self.chButton = [self.chAButton, self.chBButton]
        for k in range(len(self.chButton)):
            self.chButton[k].setStyleSheet(
                        f"color:white; background-color:{COLOR_CH[k]}")
            self.chLabel[k].setStyleSheet(
                        f"color:white; background-color:{COLOR_CH[k]}")
            # self.displayrangeComboBox[k].setStyleSheet(
            #             f"color:white; background-color:{COLOR_CH[k]}")
            self.displayrangeComboBox[k].setStyleSheet(
                        f"color:{COLOR_CH[k]}")
        return 0

# %% Define graphs
    def define_graphs(self):
        """Initialise result graphs, layout, titles, scales, colours etc."""
        matplotlib.pyplot.ion()   # Does not seem to make any difference?

        # Figure layout
        fig, axis = matplotlib.pyplot.subplot_mosaic(
                        [['trace', 'trace', 'trace', 'trace'],
                         ['awg', 'zoom', 'zoom', 'zoom'],
                         ['awgspec', 'spectrum', 'spectrum', 'spectrum']],
                        figsize=(16, 12))

        # Axes
        axis['trace'].set_title('Acquired traces', loc='left')
        axis['zoom'].set_title('Selected interval', loc='left')
        axis['awg'].set_title('Pulser', loc='left')
        for g in ['trace', 'zoom', 'awg']:
            axis[g].set_xlabel('Time [us]')
            axis[g].set_ylabel('Voltage [V]')
            axis[g].set_xlim(0, 1)
            axis[g].grid(True)
        for g in ['spectrum', 'awgspec']:
            axis[g].set_xlabel('Frequency [MHz]')
            # axis[g].set_ylabel('Power [dB re. max]')
            axis[g].set_xlim(0, 1)
            axis[g].grid(True)
        for g in ['zoom', 'spectrum']:
            axis[g].set_facecolor(COLOR_MARKER_PATCH)
        for g in ['awg', 'awgspec']:
            axis[g].set_facecolor(COLOR_AWG_BACKGROUND)

        # Dual y-axis for two channels
        axis['trace'] = [axis['trace'], axis['trace'].twinx()]
        axis['zoom'] = [axis['zoom'], axis['zoom'].twinx()]
        axis['spectrum'] = [axis['spectrum'], axis['spectrum'].twinx()]

        ch_no = 0
        for ch in ps.CH_NAMES:   # Label and color dual axis graphs
            for g in ['trace', 'zoom']:
                axis[g][ch_no].set_ylabel('Voltage [V]')
            axis['spectrum'][ch_no].set_ylabel('Power [dB re. max]')
            for g in ['trace', 'zoom', 'spectrum']:
                axis[g][ch_no].yaxis.label.set_color(COLOR_CH[ch_no])
                axis[g][ch_no].tick_params(axis='y', colors=COLOR_CH[ch_no])
            ch_no += 1

        # Graphs, updated with data during measurement
        graph = {}
        zoomed_area = matplotlib.patches.Rectangle(
                            (0, 0), 0, 0, color=COLOR_MARKER_PATCH, alpha=1)
        graph['patch'] = axis['trace'][0].add_patch(zoomed_area)
        graph['marker'] = axis['trace'][0].plot([], [], COLOR_MARKER,
                                                [], [], COLOR_MARKER)
        graph['awg'] = axis['awg'].plot([], [], COLOR_AWG)[0]
        graph['awgspec'] = axis['awgspec'].plot([], [], COLOR_AWG)[0]

        # Two channels plots
        ch_no = 0
        for ch_name in ps.CH_NAMES:
            graph_color = COLOR_CH[ch_no]
            graph[ch_name] = [
                axis['trace'][ch_no].plot([], [], color=graph_color)[0],
                axis['zoom'][ch_no].plot([], [], color=graph_color)[0],
                axis['spectrum'][ch_no].plot([], [], color=graph_color)[0]]
            ch_no += 1

        fig.show()
        return fig, axis, graph


# %% Main function

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ReadUltrasound()
    window.show()
    sys.exit(app.exec_())
