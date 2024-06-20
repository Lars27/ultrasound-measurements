# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 22:20:43 2022

@author: larsh

Contol and read data from Picoscope 5000-series osciloscopes

GUI interface made in Qt Designer, ver. 5

Sets up a GUI to control the system
Continously reads traces from the oscilloscope
Function generator will be implemented
"""

#%% Libraries

import sys
import time
from PyQt5 import QtWidgets, uic
import matplotlib.pyplot as plt
import numpy as np
import matplotlib                        # For setup with Qt
import us_utilities as us                # Utilities for USN ultrasound lab
import ps5000a_ultrasound_wrappers as ps # Interface to Picoscope c-style library


#%% Set up GUI from Qt5
matplotlib.use('Qt5Agg')
oscilloscope_main_window, QtBaseClass = uic.loadUiType(
    'aquire_ultrasound_gui.ui')


#%% Classes

class DsoFilter:  
    '''
    Digital filtering before display
    '''
    type = "No filter" # Filter type: None, AC removal, bandpass, ...
    f_min = 100        # [Hz] Lower cutoff frequency
    f_max = 10e6       # [Hz] Upper cutoff frequency
    order = 2          # Filter order
    
    
class Display:
    '''
    Settings for display on screen during runtime
    '''    
    t_min= 0               # [s] Zoomed section of trace (pulse to be analysed)
    t_max= 10              # [s] 
    channel = [True, True] # Channels to display on screen

class AcquisitionControl:  
    '''
    Control running of program
    '''
    finished = False  # Acquisition finished
    stop = False      # Stop data acquisition but not program
    ready = False     # Osciloscope configured and ready to start
       
        
class ReadUltrasound(QtWidgets.QMainWindow, oscilloscope_main_window):
    '''
    Starts GIU, initialises system
    '''
    def __init__(self):

        # Set up GUI, following example 
        QtWidgets.QMainWindow.__init__(self)
        oscilloscope_main_window.__init__(self)     # Qt GUI window
        self.setupUi(self)

        self.runstate = AcquisitionControl()

        # Initialise instrument variables. From ps5000a_ultrasound_wrappers.py 
        self.dso = ps.Communication()   # Instrument connection and status. 
        self.ch = []
        self.ch.append(ps.Channel(0))   # Vertical channel configuration
        self.ch.append(ps.Channel(1))        
        self.trigger = ps.Trigger()     # Trigger configuration
        self.sampling = ps.Horizontal() # Horisontal configuration (time)  
        
        self.rf_filter = DsoFilter()    # Filtering of acquired data

        self.wfm = us.Waveform()        # Result, storing acquired traces
        self.pulse = us.Pulse()         # Pulse for function generator output
        self.display = Display()        # Scaling and display options       

        # Connect functions to elements from GUI-file aquire_ultrasound_gui.ui
        self.zoom_start_spinBox.valueChanged.connect(self.update_display)
        self.zoom_end_spinBox.valueChanged.connect(self.update_display)
        self.zoom_fmin_spinBox.valueChanged.connect(self.update_display)
        self.zoom_fmax_spinBox.valueChanged.connect(self.update_display)
        self.zoom_dbmin_spinBox.valueChanged.connect(self.update_display)

        self.ch_pushButton = [self.ch_a_pushButton, 
                              self.ch_b_pushButton]
        self.range_comboBox = [self.range_a_comboBox, 
                               self.range_b_comboBox]  
        self.coupling_comboBox = [self.coupling_a_comboBox, 
                                  self.coupling_b_comboBox]
        self.offset_spinBox = [self.offset_a_spinBox, 
                               self.offset_b_spinBox]
        self.coupling_comboBox = [self.coupling_a_comboBox, 
                                  self.coupling_b_comboBox]
        self.bwl_comboBox = [self.bwl_a_comboBox, 
                             self.bwl_b_comboBox]
        self.zoom_vertical_comboBox= [self.zoom_vertical_a_comboBox, 
                                      self.zoom_vertical_b_comboBox ]
        
        for k in range(2):
            self.range_comboBox[k].activated.connect(self.update_vertical)
            self.coupling_comboBox[k].activated.connect(self.update_vertical)
            self.offset_spinBox[k].valueChanged.connect(self.update_vertical)
            self.coupling_comboBox[k].activated.connect(self.update_vertical)
            self.bwl_comboBox[k].activated.connect(self.update_vertical)
            self.ch_pushButton[k].clicked.connect(self.update_display)
            self.zoom_vertical_comboBox[k].activated.connect(self.update_display)
        
        # Trigger settings
        self.trigger_source_comboBox.activated.connect(self.update_trigger)      
        self.trigger_position_spinBox.valueChanged.connect(self.update_trigger)
        self.trigger_mode_comboBox.activated.connect(self.update_trigger)
        self.trigger_level_spinBox.valueChanged.connect(self.update_trigger)       
        self.trigger_delay_spinBox.valueChanged.connect(self.update_trigger)
        self.trigger_auto_delay_spinBox.valueChanged.connect(self.update_trigger)
        self.internal_trigger_delay_spinBox.valueChanged.connect(self.update_trigger)       

        # Horizontal settings (Time)
        self.sample_rate_spinBox.valueChanged.connect(self.update_sampling)      
        self.no_samples_spinBox.valueChanged.connect(self.update_sampling) 

        # Pulse genarator (awg)
        self.pulse_envelope_comboBox.activated.connect(self.update_pulser)
        self.pulse_shape_comboBox.activated.connect(self.update_pulser)
        self.pulse_frequency_spinBox.valueChanged.connect(self.update_pulser)
        self.pulse_duration_spinBox.valueChanged.connect(self.update_pulser)
        self.pulse_phase_spinBox.valueChanged.connect(self.update_pulser)
        self.pulse_amplitude_spinBox.valueChanged.connect(self.update_pulser)        

        # RF filter 
        self.filter_comboBox.activated.connect(self.update_rf_filter)
        self.fmin_spinBox.valueChanged.connect(self.update_rf_filter)
        self.fmax_spinBox.valueChanged.connect(self.update_rf_filter)
        self.filter_order_spinBox.valueChanged.connect(self.update_rf_filter)
               
        self.connect_button.clicked.connect(self.connect_dso)
        self.acquire_button.clicked.connect(self.control_acquisition)
        self.save_button.clicked.connect(self.save_result)      
        self.close_button.clicked.connect(self.close_connection)
        
        # Initialise result graph  
        col = ['C0','C1','C8']  # Colors for the two channels and the pulser
        plt.ion()               # Does not seem to make any difference?
        
        fig, ax = plt.subplot_mosaic([['trace', 'trace', 'trace'],
                                      ['awg', 'zoom', 'zoom'],
                                      ['awgspec', 'spectrum', 'spectrum']],
                                      figsize=(16, 12))
        
        # Set x-axis scales and labels
        for g in ['trace', 'zoom', 'awg']:
            ax[g].set_xlabel('Time [us]')
            ax[g].set_ylabel('Voltage [V]')
            ax[g].set_xlim(-100, 100)   
            ax[g].grid(True)       
        
        for g in ['spectrum', 'awgspec']:
            ax[g].set_xlabel('Frequency [MHz]')
            ax[g].set_ylabel('Power [dB re. max]')
            ax[g].set_xlim(0, 10)   
            ax[g].grid(True)    

        for g in [ 'awg', 'awgspec']:
            ax[g].set_facecolor("aliceblue")

        # Create dual y-axis 
        ax['trace'] = [ax['trace'], ax['trace'].twinx()]    
        ax['zoom'] = [ax['zoom'], ax['zoom'].twinx()]
        ax['spectrum'] = [ax['spectrum'], ax['spectrum'].twinx()]

        for k in range(2):
            for g in ['trace', 'zoom']:                                
                ax[g][k].set_ylabel('Voltage [V]')
            ax['spectrum'][k].set_ylabel('Power [dB re. max]')

            for g in ['trace', 'zoom', 'spectrum']:                         
                ax[g][k].yaxis.label.set_color(col[k])
                ax[g][k].tick_params(axis='y', colors= col[k])
            
        # Define empty graphs to be filled with data
        graph = {}
        ch_name = ['a','b']
        for k in range(2): 
            graph[ch_name[k]] = []
            graph[ch_name[k]].append(
                ax['trace'][k].plot([], [], color=col[k])[0])     
            graph[ch_name[k]].append(
                ax['zoom'][k].plot([], [], color=col[k])[0])    
            graph[ch_name[k]].append(
                ax['spectrum'][k].plot([], [], color=col[k])[0])
        
        graph['marker'] = ax['trace'][0].plot([], [], [], [], color='C7')
        graph['awg'] = ax['awg'].plot([], [], color=col[2])[0]
        graph['awgspec'] = ax['awgspec'].plot([], [], color=col[2])[0]

        fig.show()   
        
        # Make axes and graphs available for class
        self.graph = graph        
        self.ax = ax
        self.fig = fig      

        # Initialise GUI with messages    
        self.update_connected_box(
            "Not connected", background_color="red", text_color="white")
        
        # Enable or disable buttons according to state
        self.acquire_button.setEnabled(False)   
        self.save_button.setEnabled(False)
        self.connect_button.setEnabled(True)

        self.statusBar.showMessage('Program started')
        
        self.dso = ps.Communication() # Interface to c-style wrappers 
        self.status = {}               # Instrument status via c-style wrappers
        self.status["initialisation"]= 0

#%% Functions to interact with instrument 

    def connect_dso(self):                                         
        '''
        Connect, configure and start instrument  
        '''
        self.statusBar.showMessage('Connecting instrument ...')
        errorcode = 0        
        try:
            # Close if old handle is resident. Probably not possible
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
        self.update_sampling()
        self.update_pulser()
        self.update_rf_filter()
        self.update_display()
        
        self.acquire_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.connect_button.setEnabled(False)

        self.statusBar.showMessage("Instrument connected")
        self.update_connected_box(
            "Connected", background_color="darkgreen", text_color="white")

        self.runstate.finished = True
        self.runstate.ready = True
        self.runstate.stop = False

        return errorcode 


    def close_connection(self):
        '''
        Close instrument connection, does not stop program    
        '''
        self.statusBar.showMessage("Closing ...")
        plt.close(self.fig)
        try:
            self.status =  ps.close_adc(self.dso, self.status)
            errorcode = 0
        except:
            errorcode =-1
        finally:
            self.close()       

        self.statusBar.showMessage('Closed')

        return self.status, errorcode 
    

    def update_vertical(self):
        '''
        Read vertical settings from GUI and send to instrument      
        '''

        self.ch[0].enabled = True  # Display only , traces are always aquired 
        self.ch[1].enabled = True 
        
        for k in range(2):
            self.ch[k].v_range = self.read_scaled_value(
                self.range_comboBox[k].currentText())
            self.ch[k].v_range = self.ch[k].v_max()
            self.ch[k].coupling = self.coupling_comboBox[k].currentText()
            self.ch[k].offset = self.offset_spinBox[k].value()
            self.ch[k].bwl = self.bwl_comboBox[k].currentText()        
        
        if self.dso.connected: 
            for k in range(0,2):
                self.ch[k].no = k
                self.status = ps.set_vertical(self.dso, self.status, self.ch[k])

        return self.status           
    
    
    def update_trigger(self):
        '''
        Read trigger settings from GUI and send to instrument    
        '''
        self.trigger.source = self.trigger_source_comboBox.currentText()    
        self.trigger.enable = self.trigger.source.lower()[0:3] != 'int'
        self.trigger.position = self.trigger_position_spinBox.value()
        self.trigger.direction = self.trigger_mode_comboBox.currentText()
        self.trigger.level = self.trigger_level_spinBox.value()
        self.trigger.delay = self.trigger_delay_spinBox.value()*1e-6
        self.trigger.autodelay = self.trigger_auto_delay_spinBox.value()*1e-3
        self.trigger.internal = self.internal_trigger_delay_spinBox.value()*1e-3
        
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
        self.sampling.ns = int(self.no_samples_spinBox.value()*1e3)
        if self.dso.connected: 
            self.sampling.dt = ps.get_dt(self.dso, self.sampling)
            self.sample_rate_spinBox.setValue(self.sampling.fs() * 1e-6)
        
        return 0
    
    
    def update_pulser(self):
        '''
        Read settings for arbitrary waveform generator (awg)
        Plot pulse and send to instrument
        '''
        self.pulse.envelope = self.pulse_envelope_comboBox.currentText()
        self.pulse.shape = self.pulse_shape_comboBox.currentText()
        self.pulse.f0 = self.pulse_frequency_spinBox.value()*1e6
        self.pulse.n_cycles = self.pulse_duration_spinBox.value()
        self.pulse.phase = self.pulse_phase_spinBox.value()
        self.pulse.a = self.pulse_amplitude_spinBox.value()
        
        t_end = self.pulse.t_end() *1e6;
        vlim = 1.2 * self.pulse.a
        self.graph['awg'].set_data(self.pulse.t()*1e6, self.pulse.x())
        self.ax['awg'].set_xlim(-0.2*t_end, 1.2*t_end )
        self.ax['awg'].set_ylim(-vlim, vlim)              

        f, psd = self.pulse.powerspectrum(scale= "dB")
        self.graph['awgspec'].set_data(f/1e6, psd)

        return 0
    
    def update_rf_filter(self):
        '''
        Read RF noise filter settings from GUI 
        '''
        self.rf_filter.type = self.trigger_source_comboBox.currentText() 
        self.rf_filter.fmin = self.fmin_spinBox.value()
        self.rf_filter.fmax = self.fmax_spinBox.value()
        self.rf_filter.order = self.filter_order_spinBox.value()
        
        return 0
    
#%% Read and save results

    def control_acquisition(self):
        ''' 
        Acquire data from oscilloscope
        '''
        if self.acquire_button.isChecked():
            self.acquire_trace()
        else:
            self.stop_acquisition()
        
        return 0

    # 
    def acquire_trace(self):      
        '''
        Acquire trace from instrument, scaled in mV
        '''
        if self.runstate.ready:
            self.runstate.ready = False
            self.update_status_box(
                "Acquiring", background_color="darkgreen", text_color="white")
            self.statusBar.showMessage("Acquiring data ...")
            self.close_button.setEnabled(False)
            self.save_button.setEnabled(True)
            while not(self.runstate.stop):
                self.status, self.dso = ps.configure_acquisition(
                    self.dso, self.status, self.sampling)        
                self.status, self.dso, y = ps.acquire_trace(
                    self.dso, self.status, self.sampling, self.ch)
                
                self.wfm.y = y
                self.wfm.dt = self.sampling.dt
                self.wfm.t0 = self.sampling.t0()
                
                self.plot_result()
        
        self.update_status_box(
            "Stopped", background_color="darkred", text_color="white")
        self.statusBar.showMessage("Ready")       
        self.runstate.stop = False
        return 0
        
    
    def stop_acquisition(self): 
        '''
        Stop acquisition of traces, does not close instrument connection
        '''
        
        if not(self.runstate.stop):
            self.runstate.stop = True
            self.statusBar.showMessage("Stopping acquisition")
            self.update_status_box("Stopping acquisition", "darkred", "white")

        self.runstate.stop = True
        self.runstate.finished = True            
        self.runstate.ready = True            
        self.close_button.setEnabled(True)
        self.save_button.setEnabled(False)

        return 0        


    def plot_result(self):
        '''
        Plot measured trace on screen
        '''
        wfm_zoom= self.wfm.zoom([self.display.tmin, self.display.tmax ]) 
        
        chname = ['a','b']
        for k in range(2): 
            if self.display.ch[k]:
                self.graph[chname[k]][0].set_data(
                    self.wfm.t()*1e6, self.wfm.x[:,k]) 
                self.graph[chname[k]][1].set_data(
                    wfm_zoom.t()*1e6, wfm_zoom.y[:,k])
                f, psd = wfm_zoom.powerspectrum(scale="dB")
                self.graph[chname[k]][2].set_data(f/1e6, psd[:,k])
            else:
                self.graph[chname[k]][0].set_data([],[]) # Full trace
                self.graph[chname[k]][1].set_data([],[]) # Selected interval       
                self.graph[chname[k]][2].set_data([],[]) # Power spectrum
        
        self.fig.canvas.draw()            # --- TRY: Probably necessary
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
        self.filecounter_spinBox.setValue(n_result) 
        self.resultfile_Edit.setText(resultfile) 
        self.resultpath_Edit.setText(resultpath) 
        
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


    def update_status_box(self, message, background_color='white', 
                          text_color='black'):
        '''
        Write message to status box, optional colours  
        '''
        self.status_Edit.setText(message)
        self.status_Edit.setStyleSheet(
            f"background-color : {background_color}; color : {text_color}")
        return 0


    def update_connected_box(self, message, 
                             background_color='white', text_color='black'):
        '''
        Write connected status  
        '''
        self.connected_Edit.setText(message)
        self.connected_Edit.setStyleSheet(
            f"background-color : {background_color}; color : {text_color}")
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
    
    
    def update_display(self):                
        '''
        Update values and markers on screen
        '''

        # Full trace time-axis
        self.ax["trace"][0].set_xlim(self.sampling.t0()*1e6, self.sampling.tmax()*1e6)    
        
        # Selected interval, 'zoom'
        tlim = [ self.zoom_start_spinBox.value(), self.zoom_end_spinBox.value()] 
        for k in range(2):
            self.graph['marker'][k].set_data(np.full((2,1), tlim[k]), np.array([-100, 100])) 

        self.display.tmin = min(tlim)*1e-6    
        self.display.tmax = max(tlim)*1e-6       
        self.ax["zoom"][0].set_xlim(min(tlim), max(tlim) )
        
        # Vertical scale
        dbmin = self.zoom_dbmin_spinBox.value()        
        for k in range(2):
            self.display.ch[k] = not self.ch_pushButton[k].isChecked()

            vzoom= self.read_scaled_value(self.zoom_vertical_comboBox[k].currentText())        
            self.ax["zoom"][k].set_ylim(-vzoom, vzoom)
            self.ax["trace"][k].set_ylim(-self.ch[k].vmax(), self.ch[k].vmax())
            self.ax["spectrum"][k].set_ylim(dbmin, 0)

        self.ax["awgspec"].set_ylim(dbmin, 0)

        # Frequency axes
        flim = [ self.zoom_fmin_spinBox.value(), self.zoom_fmax_spinBox.value() ]  
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
