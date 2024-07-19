# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 22:20:43 2022

@author: larsh

Analysis program made for USN ultrasound lab

Investigate and save traces from single-element ultrasound transducers using 
Picoscope 5000-series osciloscopes.
GUI interface made in Qt Designer, ver. 5.
Based on earlier NI LabWindows, LabVIEW and Matlab programs. Formats of 
result files should be compatible with these, but smaller modifications may be 
required in some cases.

Sets up a GUI to control the system
Continously reads traces from the oscilloscope
Function generator to be implemented soon
"""

#%% Libraries

# General
import sys
#import time
from PyQt5 import QtWidgets, uic
import matplotlib.pyplot as plt
import numpy as np
import matplotlib                        # For setup with Qt

# USN ultrasound lab specific
import us_utilities as us                # Utilities for USN ultrasound lab
import ps5000a_ultrasound_wrappers as ps # Interface to Picoscope c-style library

# Constants
WARNING= ["white", "red"]
OK= ["white", "darkgreen"]
NEUTRAL= ["black", "white"]

TIMESCALE = 1E-6      # Display time in us
FREQUENCYSCALE= 1E6   # Display frequency in MHz


#%% Set up GUI from Qt5
matplotlib.use('Qt5Agg')
oscilloscope_main_window, QtBaseClass = uic.loadUiType(
    'aquire_ultrasound_gui.ui')


#%% Classes  
    
class Display:
    '''
    Settings for display on screen during runtime
    '''    
    t_min= 0               # [s] Zoomed section of trace (pulse to be analysed)
    t_max= 10              # [s] 
    channel = [True, True] # Channels to display on screen
    

class AcquisitionControl:  
    '''
    Status flags to control running of program
    '''
    ready = False     # Osciloscope configured and ready to start
    finished = False  # Acquisition finished
    stop = False      # Stop data acquisition, do not quit program
       
        
class ReadUltrasound(QtWidgets.QMainWindow, oscilloscope_main_window):
    '''
    Starts GUi and initialises system
    '''
    def __init__(self):

        # Set up GUI, following example 
        QtWidgets.QMainWindow.__init__(self)
        oscilloscope_main_window.__init__(self)     # Qt GUI window
        self.setupUi(self)

        self.runstate = AcquisitionControl()

        # Initialise instrument variables. 
        # Interface to oscilloscope. From ps5000a_ultrasound_wrappers.py
        self.dso= ps.Communication()   # Instrument connection and status. 
        self.ch= []
        self.ch.append(ps.Channel(0))   # Vertical channel configuration
        self.ch.append(ps.Channel(1))        
        self.trigger= ps.Trigger()     # Trigger configuration
        self.sampling= ps.Horizontal() # Horisontal configuration (time)  
        
        # Ultrasound pulse data (us_utilities_py)        
        self.wfm= us.Waveform()             # Result, storing acquired traces
        self.pulse= us.Pulse()              # Pulse for function generator output
        self.pulse.dt = 1/ps.DAC_SAMPLERATE 
        self.rf_filter = us.WaveformFilter() # Filtering, for display only

        # Display of results 
        self.display= Display()        # Scaling and display options       

        # Connect functions to elements from GUI-file. QT naming convention
        # Display
        self.zoomStartSpinBox.valueChanged.connect(self.update_display)
        self.zoomEndSpinBox.valueChanged.connect(self.update_display)
        self.zoomFminSpinBox.valueChanged.connect(self.update_display)
        self.zoomFmaxSpinBox.valueChanged.connect(self.update_display)
        self.dbMinSpinBox.valueChanged.connect(self.update_display)

        # RF filter 
        self.filterComboBox.activated.connect(self.update_rf_filter)
        self.fminSpinBox.valueChanged.connect(self.update_rf_filter)
        self.fmaxSpinBox.valueChanged.connect(self.update_rf_filter)
        self.filterOrderSpinBox.valueChanged.connect(self.update_rf_filter)
               
        # Oscilloscope configuration
        # Vertical, 2 channels, A and B (Voltage)
        self.chButton= [self.chAButton, 
                         self.chBButton]
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
        self.displayrangeComboBox= [self.displayrangeAComboBox, 
                                    self.displayrangeBComboBox ]
        
        # Group channels
        for k in range(len(self.chButton)):
            self.rangeComboBox[k].activated.connect(self.update_vertical)
            self.couplingComboBox[k].activated.connect(self.update_vertical)
            self.offsetSpinBox[k].valueChanged.connect(self.update_vertical)
            self.couplingComboBox[k].activated.connect(self.update_vertical)
            self.bwlComboBox[k].activated.connect(self.update_vertical)
            self.chButton[k].clicked.connect(self.update_display)
            self.displayrangeComboBox[k].activated.connect(self.update_display)
        
        # Trigger 
        self.triggerSourceComboBox.activated.connect(self.update_trigger)      
        self.triggerPositionSpinBox.valueChanged.connect(self.update_trigger)
        self.triggerModeComboBox.activated.connect(self.update_trigger)
        self.triggerLevelSpinBox.valueChanged.connect(self.update_trigger)       
        self.triggerDelaySpinBox.valueChanged.connect(self.update_trigger)
        self.triggerAutoDelaySpinBox.valueChanged.connect(self.update_trigger)
        self.internalTriggerDelaySpinBox.valueChanged.connect(self.update_trigger)       

        # Horizontal (Time)
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
        
        # Initialise result graph  
        ch_names = ['a','b']
        color = {'a':'C0', 'b':'C1', 
                 'awg':'C2', 'awg_background': 'mintcream',
                 'marker':'darkslategrey', 'patch':'azure'}
        plt.ion()               # Does not seem to make any difference?
        
        # Result grapphs layout
        fig, ax = plt.subplot_mosaic([['trace', 'trace', 'trace'],
                                      ['awg', 'zoom', 'zoom'],
                                      ['awgspec', 'spectrum', 'spectrum']],
                                      figsize=(16, 12))
        
        # Set x-axis scales and labels
        # Time traces
        for g in ['trace', 'zoom', 'awg']:
            ax[g].set_xlabel('Time [us]')
            ax[g].set_ylabel('Voltage [V]')
            ax[g].set_xlim(-100, 100)   
            ax[g].grid(True)       
        
        # Power spectra
        for g in ['spectrum', 'awgspec']:
            ax[g].set_xlabel('Frequency [MHz]')
            ax[g].set_ylabel('Power [dB re. max]')
            ax[g].set_xlim(0, 10)   
            ax[g].grid(True)    

        # Bckground  color 
        for g in [ 'awg', 'awgspec']:
            ax[g].set_facecolor(color['awg_background'])

        for g in [ 'zoom', 'spectrum']:
            ax[g].set_facecolor(color['patch'])

        # Dual y-axis for two channels
        ax['trace'] = [ax['trace'], ax['trace'].twinx()]    
        ax['zoom'] = [ax['zoom'], ax['zoom'].twinx()]
        ax['spectrum'] = [ax['spectrum'], ax['spectrum'].twinx()]

        ch_no = 0
        for ch in ch_names:   # Label and color dual axis graphs
            for g in ['trace', 'zoom']:                                
                ax[g][ch_no].set_ylabel('Voltage [V]')
            ax['spectrum'][ch_no].set_ylabel('Power [dB re. max]')

            for g in ['trace', 'zoom', 'spectrum']:                         
                ax[g][ch_no].yaxis.label.set_color(color[ch])
                ax[g][ch_no].tick_params(axis='y', colors= color[ch])
            ch_no+=1
            
        # Define empty graphs to be updated with data during measurement
        graph = {}

        # Marker for zoom
        graph['marker'] = ax['trace'][0].plot([], [], [], [], color=color['marker'])
        zoomed_area = matplotlib.patches.Rectangle((0,0), 0, 0, color=color['patch'], alpha=1)
        graph['patch']= ax['trace'][0].add_patch(zoomed_area)

        # Single graph plots
        graph['awg'] = ax['awg'].plot([], [], color=color['awg'])[0]
        graph['awgspec'] = ax['awgspec'].plot([], [], color=color['awg'])[0]

        # Two channels plots
        ch_no = 0
        for ch in ch_names: 
            graph[ch] = []
            graph[ch].append(
                ax['trace'][ch_no].plot([], [], color=color[ch])[0])     
            graph[ch].append(
                ax['zoom'][ch_no].plot([], [], color=color[ch])[0])    
            graph[ch].append(
                ax['spectrum'][ch_no].plot([], [], color=color[ch])[0])
            ch_no+=1
           
        fig.show()   
        
        # Make axes and graphs available for class
        self.graph = graph        
        self.ax = ax
        self.fig = fig      

        # Initialise GUI with messages    
        self.update_connected_box("Not connected", WARNING)
        
        # Enable or disable buttons according to state
        self.acquireButton.setEnabled(False)   
        self.saveButton.setEnabled(False)
        self.connectButton.setEnabled(True)

        self.statusBar.showMessage('Program started')
        
        self.dso = ps.Communication() # Interface to c-style wrappers 
        self.status = {}               # Instrument status via c-style wrappers
        self.status["initialisation"]= 0


#%% Functions to interact with instrument 

    def connect_dso(self):                                         
        '''
        Connect, configure and start instrument  
        '''
        self.statusBar.showMessage('Connecting instrument')
        errorcode = 0      
        
        # Try to close if an old handle is still resident. May not work
        try:
            if "openunit" in self.status:
                if not("close" in self.status):        
                    ps.stop_adc(dso, self.status)
                    ps.close_adc(dso, self.status)
            #self.status = {}
        except NameError:
            self.status = {}
        
        # Connect and initialise instrument
        self.status, self.dso = ps.open_adc(self.dso, self.status) 
        self.dso.connected = True
        
        # Send initial configuration to oscilloscope
        self.status = self.update_vertical()
        self.status = self.update_trigger()
        
        # Update configuration parameters
        self.update_sampling()
        self.update_pulser()
        self.update_rf_filter()
        self.update_display()
        
        # Update GUI status
        self.acquireButton.setEnabled(True)
        self.saveButton.setEnabled(False)
        self.connectButton.setEnabled(False)

        self.statusBar.showMessage("Instrument connected")
        self.update_connected_box("Connected", OK)

        self.runstate.finished= True
        self.runstate.ready=True
        self.runstate.stop= False

        return errorcode 


    def close_connection(self):
        '''
        Close instrument connection, does not stop program    
        '''
        self.statusBar.showMessage("Closing")
        plt.close(self.fig)
        try:
            self.status=  ps.close_adc(self.dso, self.status)
            errorcode= 0
        except:
            errorcode=-1
        finally:
            self.close()       

        self.statusBar.showMessage('Closed')

        return self.status, errorcode 
    

    def update_vertical(self):
        '''
        Read vertical settings from GUI and send to instrument      
        '''
        self.ch[0].enabled= True  # Display or not, traces are always aquired 
        self.ch[1].enabled= True 
        
        for k in range(len(self.ch)):
            self.ch[k].v_range= self.read_scaled_value(
                                  self.rangeComboBox[k].currentText())
            self.ch[k].v_range= self.ch[k].v_max()
            self.ch[k].coupling= self.couplingComboBox[k].currentText()
            self.ch[k].offset= self.offsetSpinBox[k].value()
            self.ch[k].bwl= self.bwlComboBox[k].currentText()        
        
        if self.dso.connected: 
            for k in range(len(self.ch)):
                self.ch[k].no= k
                self.status= ps.set_vertical(self.dso, self.status, self.ch[k])

        return self.status           
    
    
    def update_trigger(self):
        '''
        Read trigger settings from GUI and send to instrument    
        '''
        self.trigger.source = self.triggerSourceComboBox.currentText()    
        self.trigger.enable = self.trigger.source.lower()[0:3] != 'int'
        self.trigger.position = self.triggerPositionSpinBox.value()
        self.trigger.direction = self.triggerModeComboBox.currentText()
        self.trigger.level = self.triggerLevelSpinBox.value()
        self.trigger.delay = self.triggerDelaySpinBox.value()*TIMESCALE
        self.trigger.autodelay = self.triggerAutoDelaySpinBox.value()*1e-3
        self.trigger.internal = self.internalTriggerDelaySpinBox.value()*1e-3        
        self.sampling.pretrigger= self.trigger.position/100  # Convert % 
        
        if self.dso.connected: 
            self.status = ps.set_trigger(self.dso, self.status, self.trigger, 
                                         self.ch, self.sampling)

        return self.status  
    
    
    def update_sampling(self):
        '''
        Read trace length from GUI and set sample rate. 
        No communication with instrument
        '''
        self.sampling.timebase = 3
        self.sampling.n_samples = int(self.nSamplesSpinBox.value()*1e3)
        if self.dso.connected: 
            self.sampling.dt = ps.get_dt(self.dso, self.sampling)
            self.samplerateSpinBox.setValue(self.sampling.fs()/FREQUENCYSCALE)
        
        return 0
    
    
    def update_pulser(self):
        '''
        Read settings for arbitrary waveform generator (awg)
        Plot pulse and send to instrument
        '''
       
        self.pulse.on = self.transmitButton.isChecked()
        
        self.pulse.envelope= self.pulseEnvelopeComboBox.currentText()
        self.pulse.shape= self.pulseShapeComboBox.currentText()
        self.pulse.f0= self.pulseFrequencySpinBox.value()*FREQUENCYSCALE
        self.pulse.n_cycles= self.pulseDurationSpinBox.value()
        self.pulse.phase= self.pulsePhaseSpinBox.value()
        self.pulse.a= self.pulseAmplitudeSpinBox.value()
     
        t_max = self.pulse.duration()/TIMESCALE;
        vlim = 1.1 * self.pulse.a
        self.graph['awg'].set_data(self.pulse.t()/TIMESCALE, self.pulse.y())
        self.ax['awg'].set_xlim(0, t_max )
        self.ax['awg'].set_ylim(-vlim, vlim)              
 
        f, psd = self.pulse.powerspectrum()
        self.graph['awgspec'].set_data(f/FREQUENCYSCALE, psd)
         
        ps.set_signal( self.dso, self.status, self.sampling, self.pulse)
         
        for g in ['awg', 'awgspec']:
            if self.pulse.on:
                self.graph[g].set_linestyle("solid")           
            else:
                self.graph[g].set_linestyle("dotted")                    
         
        self.update_display()
        self.update_transmit_box(self.pulse.on)

        return 0
    
    
    def update_rf_filter(self):
        '''
        Read RF noise filter settings from GUI 
        '''
        self.rf_filter.sample_rate = self.sampling.fs()

        self.rf_filter.type = self.filterComboBox.currentText() 
        self.rf_filter.f_min = self.fminSpinBox.value()*FREQUENCYSCALE
        self.rf_filter.f_max = self.fmaxSpinBox.value()*FREQUENCYSCALE
        self.rf_filter.order = self.filterOrderSpinBox.value()
        
        return 0
    
#%% Read and save results

    def control_acquisition(self):
        ''' 
        Acquire data from oscilloscope
        '''
        if self.acquireButton.isChecked():
            self.acquire_trace()
        else:
            self.stop_acquisition()
        
        return 0

    # 
    def acquire_trace(self):      
        '''
        Acquire trace from instrument
        '''
        if self.runstate.ready:
            self.runstate.ready = False
            self.update_status_box("Acquiring", OK)
            self.statusBar.showMessage("Acquiring data ...")
            self.closeButton.setEnabled(False)
            self.saveButton.setEnabled(True)
            while not(self.runstate.stop):
                self.status, self.dso = ps.configure_acquisition(
                    self.dso, self.status, self.sampling)        
                self.status, self.dso, y = ps.acquire_trace(
                    self.dso, self.status, self.sampling, self.ch)
                
                self.wfm.y = y
                self.wfm.dt = self.sampling.dt
                self.wfm.t0 = self.sampling.t0()
                
                self.plot_result()
        
        self.update_status_box("Stopped", WARNING)
        self.statusBar.showMessage("Ready")       
        self.runstate.stop = False
        return 0
        
    
    def stop_acquisition(self): 
        '''
        Stop acquisition of traces, does not close instrument connection
        '''        
        if not(self.runstate.stop):
            self.runstate.stop = True
            self.statusBar.showMessage("Stopping")
            self.update_status_box("Stopping", WARNING)

        self.runstate.stop = True
        self.runstate.finished = True            
        self.runstate.ready = True            
        self.closeButton.setEnabled(True)
        self.saveButton.setEnabled(False)

        return 0        


    def plot_result(self, time_unit="us"):
        '''
        Plot measured trace on screen
        '''        
        wfm_filtered= self.wfm.filtered(self.rf_filter) 
        wfm_zoomed= wfm_filtered.zoomed([self.display.t_min, 
                                         self.display.t_max ])         
        
        f, psd = wfm_zoomed.powerspectrum(scale="dB", normalise="True")
        
        channel_name = ['a','b']
        k=0
        for ch in channel_name:
            if self.display.channel[k]:
                self.graph[ch][0].set_data(wfm_filtered.t()/TIMESCALE, 
                                           wfm_filtered.y[:,k]) 
                self.graph[ch][1].set_data(wfm_zoomed.t()/TIMESCALE, 
                                           wfm_zoomed.y[:,k])
                self.graph[ch][2].set_data(f/FREQUENCYSCALE, 
                                           psd[:,k])
            else:
                self.graph[ch][0].set_data([],[]) # Full trace
                self.graph[ch][1].set_data([],[]) # Selected interval       
                self.graph[ch][2].set_data([],[]) # Power spectrum
            k+=1
        
        #self.fig.canvas.draw()            # --- TRY: Probably necessary
        self.fig.canvas.flush_events()    # --- TRY: Probably unnecessary 
        self.update_display()
                
        return 0

        
    def save_result(self):
        '''
        Save measured traces and parameters to binary file with 
        automatically generated filename
        '''
        self.statusBar.showMessage("Saving results ...")

        resultpath, resultdir, resultfile, n_result = us.find_filename(
            prefix='US', ext='trc', resultdir='results')
        self.wfm.save(resultpath)
        self.filecounterSpinBox.setValue(n_result) 
        self.resultfileEdit.setText(resultfile) 
        self.resultpathEdit.setText(resultpath) 
        
        self.statusBar.showMessage(f'Result saved to {resultfile}')
        return 0
    
       
#%% General GUI read and write

    def update_status(self, message, append=False):
        '''
        Status field, at bottom of window
        '''
        if append:
            old_message = self.status_textEdit.toPlainText()
            message += old_message
        self.status_textEdit.setText(message)  
        return message    


    def update_status_box(self, message, color=NEUTRAL):
        '''
        Write message to status box, optional colours  
        '''
        self.statusEdit.setText(message)
        self.statusEdit.setStyleSheet(
            f"color:{color[0]}; background-color:{color[1]}")
        return 0


    def update_connected_box(self, message, color=NEUTRAL):
        '''
        Write connected status  
        '''
        self.connectedEdit.setText(message)
        self.connectedEdit.setStyleSheet(
            f"color:{color[0]}; background-color:{color[1]}")
        return 0

    def update_transmit_box(self, transmitting=False ):
        '''
        Write connected status  
        '''
        if transmitting:
            message = "ON"
            color = OK
        else:
            message = "OFF"
            color = WARNING
                
        self.transmitStatusEdit.setText(message)
        self.transmitStatusEdit.setStyleSheet(
            f"color:{color[0]}; background-color:{color[1]}")
        return 0
    

    def read_scaled_value(self, prefix): 
        '''
        Interpret a text as a scaled value (milli, kilo, Mega etc.)
        '''
        prefix= prefix.split(' ')     
        if len(prefix) == 1:
            multiplier = 1
        else:
            if prefix[1]== 'u':
                multiplier = 1e-6;
            if prefix[1]== 'm':
                multiplier = 1e-3;
            elif prefix[1] == 'k':
                multiplier = 1e3;
            elif prefix[1] == 'M':
                multiplier = 1e6
            elif prefix[1] == 'G':
                multiplier = 1e9
            else:
                multiplier = 1
        value = float(prefix[0]) * multiplier
        
        return value
    
    
    def find_voltagescale(self, vmax):
        '''
        Find scale for voltage axis based on maximum value
        '''
        if vmax<1e-3:
            voltage_scale= 1e-6
            unit= "uV"
        elif vmax<1:
            voltage_scale= 1e-3
            unit= "mV"
        else:
            voltage_scale= 1
            unit= "V"

        return voltage_scale, unit
                        
    
    def update_display(self,time_unit="us"):                
        '''
        Update values and markers on screen
        '''

        # Full trace time-axis
        self.ax["trace"][0].set_xlim(self.sampling.t0()/TIMESCALE, 
                                     self.sampling.t_max()/TIMESCALE)    
        
        # Selected interval, 'zoom'
        tlim = [ self.zoomStartSpinBox.value(), self.zoomEndSpinBox.value()] 

        for k in range(len(self.graph['marker'])):
            self.graph['marker'][k].set_data(
                np.full((2,1), tlim[k]), np.array([-100, 100])) 
        
        self.graph['patch'].set_bounds(tlim[0], -20, tlim[1]-tlim[0], 40 )
      
        self.ax["zoom"][0].set_xlim(min(tlim), max(tlim) )

        self.display.t_min= min(tlim)*TIMESCALE
        self.display.t_max= max(tlim)*TIMESCALE
        
        # Vertical scale
        dbmin = self.dbMinSpinBox.value()        
        for k in range(len(self.display.channel)):
            self.display.channel[k] = not self.chButton[k].isChecked()

            vzoom= self.read_scaled_value(
                self.displayrangeComboBox[k].currentText())        
            #voltage_scale, voltage_unit = self.find_voltagescale(vzoom)
            
            self.ax["zoom"][k].set_ylim(-vzoom, vzoom)
            self.ax["trace"][k].set_ylim(-self.ch[k].v_max(), 
                                          self.ch[k].v_max())
            self.ax["spectrum"][k].set_ylim(dbmin, 0)

        self.ax["awgspec"].set_ylim(dbmin, 0)

        # Frequency axes
        flim = [self.zoomFminSpinBox.value(), 
                self.zoomFmaxSpinBox.value()]  
        self.ax["spectrum"][0].set_xlim(min(flim), max(flim))
        self.ax["awgspec"].set_xlim(min(flim), max(flim))
        
        self.fig.canvas.draw()
        
        return 0    

#%% Main function

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ReadUltrasound()
    window.show()
    sys.exit(app.exec_())
