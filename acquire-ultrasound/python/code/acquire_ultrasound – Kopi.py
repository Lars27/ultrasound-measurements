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
import matplotlib.pyplot as plt            # For plotting
import numpy as np
import matplotlib                          # For setup with Qt
import us_utilities as us                  # Utilities made for USN ultrasound lab
import ps5000a_ultrasound_wrappers as ps   # Interface to Picoscope c-style library

#%% Set up GUI from Qt5
matplotlib.use('Qt5Agg')
oscilloscope_main_window, QtBaseClass = uic.loadUiType('aquire_ultrasound_gui.ui')

# Classes
class dso_filter:   # Digital filtering before display
    type  = "No filter"       # Filter type: None, AC removal, bandpass, ...
    fmin  = 100               # [Hz] Lower cutoff frequency
    fmax  = 10e6              # [Hz] Upper cutoff frequency
    order = 2                 # Filter order
    
class display:                # Settings for display on screen during runtime
    tmin = 0                  # [s] Start zoomed section of trace (pulse to be analysed)
    tmax = 10                 # [s] End zoomed section of trace
    ch   = [ True, True ]     # Channels to diaplay on screen

class acquisition_control:    # Control running of program
    finished = False          # Acquisition finished
    stop     = False          # Stop data acquisition (but not program) 
    ready    = False          # Osciloscope configured and ready to start
       
        
#%% Main classes with defs
class read_ultrasound( QtWidgets.QMainWindow, oscilloscope_main_window ):
    def __init__(self):

        # Set up GUI, following example 
        QtWidgets.QMainWindow.__init__(self)
        oscilloscope_main_window.__init__(self)     # Qt GUI window
        self.setupUi(self)

        self.runstate = acquisition_control()

        # Initialise instrument variables
        self.dso = ps.communication()       # Instrument connection and status. From ps5000a_ultrasound_wrappers.py 
        self.ch  = []
        self.ch.append( ps.channel ( 0 ) )  # Vertical channel configuration
        self.ch.append( ps.channel ( 1 ) )
        
        self.trigger  = ps.trigger()        # Trigger configuration
        self.sampling = ps.horizontal()     # Horisontal configuration (time sampling)  
        self.rf_filter= dso_filter()        # Filtering of acquired data
        self.wfm      = us.waveform( )      # Result, storing acquired traces
        self.pulse    = us.pulse( )         # Pulse for function generator output
        self.display  = display()           # Scaling and diplay options
        
        # Connect functions to elements from GUI-file (aquire_ultrasound_gui.ui)
        self.connect_button.clicked.connect( self.connect_dso )
        self.acquire_button.clicked.connect( self.acquire_trace )
        
        self.zoom_start_spinBox.valueChanged.connect   ( self.update_display )    # Display
        self.zoom_end_spinBox.valueChanged.connect     ( self.update_display )
        self.zoom_vertical_a_comboBox.activated.connect( self.update_display )
        self.zoom_vertical_b_comboBox.activated.connect( self.update_display )
        self.zoom_fmin_spinBox.valueChanged.connect    ( self.update_display )
        self.zoom_fmax_spinBox.valueChanged.connect    ( self.update_display )
        self.zoom_dbmin_spinBox.valueChanged.connect   ( self.update_display )

        self.ch_a_pushButton.clicked.connect( self.update_display )
        self.ch_b_pushButton.clicked.connect( self.update_display )
        
        self.range_a_comboBox.activated.connect   ( self.update_vertical )      # Vertical osciloscope settings (Voltage)
        self.coupling_a_comboBox.activated.connect( self.update_vertical )
        self.offset_a_spinBox.valueChanged.connect( self.update_vertical )
        self.coupling_a_comboBox.activated.connect( self.update_vertical )
        self.bwl_a_comboBox.activated.connect     ( self.update_vertical )
        self.range_b_comboBox.activated.connect   ( self.update_vertical )
        self.coupling_b_comboBox.activated.connect( self.update_vertical )
        self.offset_b_spinBox.valueChanged.connect( self.update_vertical )
        self.coupling_b_comboBox.activated.connect( self.update_vertical )
        self.bwl_b_comboBox.activated.connect     ( self.update_vertical )

        self.trigger_source_comboBox.activated.connect          ( self.update_trigger )      # Osciloscope trigger settings
        self.trigger_position_spinBox.valueChanged.connect      ( self.update_trigger )
        self.trigger_mode_comboBox.activated.connect            ( self.update_trigger )
        self.trigger_level_spinBox.valueChanged.connect         ( self.update_trigger )       
        self.trigger_delay_spinBox.valueChanged.connect         ( self.update_trigger )
        self.trigger_auto_delay_spinBox.valueChanged.connect    ( self.update_trigger )
        self.internal_trigger_delay_spinBox.valueChanged.connect( self.update_trigger )

<<<<<<< HEAD
        self.sample_rate_spinBox.valueChanged.connect( self.update_sampling )
        self.no_samples_spinBox.valueChanged.connect( self.update_sampling )
        
        self.pulse_envelope_comboBox.activated.connect    ( self.update_pulser )
        self.pulse_shape_comboBox.activated.connect       ( self.update_pulser )
        self.pulse_frequency_spinBox.valueChanged.connect ( self.update_pulser )
        self.pulse_duration_spinBox.valueChanged.connect  ( self.update_pulser )
        self.pulse_phase_spinBox.valueChanged.connect     ( self.update_pulser )
        self.pulse_amplitude_spinBox.valueChanged.connect ( self.update_pulser )        
=======
        self.sample_rate_spinBox.valueChanged.connect( self.update_sampling )      # Horizontal  osciloscope settings (Time)
        self.no_samples_spinBox.valueChanged.connect ( self.update_sampling ) 
>>>>>>> 5dc11c8976bd8195c83b23c9998d9ffb4239ce9f

        self.filter_comboBox.activated.connect( self.update_rf_filter )            # Display filter settings
        self.fmin_spinBox.valueChanged.connect( self.update_rf_filter )
        self.fmax_spinBox.valueChanged.connect( self.update_rf_filter )
        self.filter_order_spinBox.valueChanged.connect( self.update_rf_filter )
               
        self.acquire_button.clicked.connect( self.acquire_trace )                # Control buttons
        self.save_button.clicked.connect   ( self.save_results )      
        self.stop_button.clicked.connect   ( self.stop_acquisition ) 
        self.close_button.clicked.connect  ( self.close_app ) 
        
        # Initialise result graph
<<<<<<< HEAD
        plt.ion()         # Does not seem to make any difference
        #fig = plt.figure( figsize=(12, 12) )
        
        fig, ax = plt.subplot_mosaic( [ ['trace', 'trace'    , 'trace'    ],
                                        ['pulse', 'zoom'     , 'zoom'     ],
                                        ['pspec', 'spectrum' , 'spectrum' ] ],
                                         figsize=(16, 12))
        
        ax_main = ax['trace']
        ax_zoom = ax['zoom']
        ax_spectrum = ax['spectrum']
        ax_pulse = ax['pulse']
        ax_pulse_spectrum = ax['pspec']
        
        col = [ 'C0' , 'C1' ]   # Colors for the two channels

        ax_main.set_xlabel('Time [us]')
        ax_main.set_xlim (-200 , 200 )   
        ax_main.grid  ( True )

        ax_zoom.set_xlabel('Time [us]')
        ax_zoom.set_xlim (  10,   20 )   
        ax_zoom.grid  ( True )

        ax_spectrum.set_xlabel('Frequency [MHz]')
        ax_spectrum.set_xlim (  0 , 10 )   
        ax_spectrum.set_ylim (-40 ,  0 )   
        ax_spectrum.grid( True )    

        ax_pulse.set_xlim (  0 , 10 )   
        ax_pulse.set_ylim (-10 , 10 )   
        ax_pulse.set_xlabel('Time [us]')
        ax_pulse.set_ylabel('Voltage [us]')
        ax_pulse.grid( True )    
        ax_pulse.set_facecolor("aliceblue")
        
        ax_pulse_spectrum.set_xlim (  0 , 10 )   
        ax_pulse_spectrum.set_ylim (-40 ,  0 )   
        ax_pulse_spectrum.grid ( True )   
        ax_pulse_spectrum.set_xlabel('Frequency [MHz]')
        ax_pulse_spectrum.set_ylabel('Power [dB re. max]')
        ax_pulse_spectrum.set_facecolor("aliceblue")
        
        ax_main    = [ ax_main,     ax_main.twinx()     ]    # Creat duale y-axis for all plots
        ax_zoom    = [ ax_zoom,     ax_zoom.twinx()     ]
        ax_spectrum= [ ax_spectrum, ax_spectrum.twinx() ]

        for k in range(2):
            ax_main[k].tick_params    ( labelcolor= col[k] )
            ax_zoom[k].tick_params    ( labelcolor= col[k] )
            ax_spectrum[k].tick_params( labelcolor= col[k] )
            
        for k in range(2):
            ax_main[k].set_ylabel('Voltage [V]',            color= col[k] )
            ax_zoom[k].set_ylabel('Voltage [V]',            color= col[k] )
            ax_spectrum[k].set_ylabel('Power [dB re. max]', color= col[k] )

        graph_left  = []        # Create handles to datapoints, empty so far
        graph_right = []
        graph_marker = []

        graph_left.append ( ax_main[0].plot     ( [], [], color= col[0] )[0] )     # Empty placeholder for datapoints
        graph_left.append ( ax_zoom[0].plot     ( [], [], color= col[0] )[0] )    
        graph_left.append ( ax_spectrum[0].plot ( [], [], color= col[0] )[0] )

        graph_right.append ( ax_main[1].plot     ( [], [], color= col[1] )[0] )   
        graph_right.append ( ax_zoom[1].plot     ( [], [], color= col[1] )[0] )   
        graph_right.append ( ax_spectrum[1].plot ( [], [], color= col[1] )[0] )
        
        graph_marker = ax_main[0].plot ( [], [], [], [], color='C7' )        # Extra plots for interval markers
        
        self.graph_pulse = ax_pulse.plot( [], [], color=col[0] )[0]
        self.graph_pulse_spectrum = ax_pulse_spectrum.plot( [], [], color=col[0] )[0]
=======
        plt.ion()         # Does not seem to make any difference, 
        fig, ax_left = plt.subplots( nrows=3, ncols=1, figsize=(8, 12) )       # Define result figure with axes

        for k in range( 0, 2):                      # Configure time trace graphs 
             ax_left[k].set_xlabel('Time [us]')
             ax_left[k].grid( True )                      
        ax_left[0].set_xlim (-200 , 200 )   
        ax_left[1].set_xlim (  10,   20 )           
        
        ax_left[2].set_xlabel('Frequency [MHz]')    # Configure spectrum display
        ax_left[2].grid( True )         
        ax_left[2].set_xlim (  0 , 10 )   
        ax_left[2].set_ylim (-40 ,  0 )   

        ax_right     = []        # Create dual y-axis (left and right) with handles to (empty) datapoints
        graph_left   = []        # Left y-axis for Ch A. Full trace, zoomed section, and spectrum
        graph_right  = []        # Right y-axis for Ch B
        graph_marker = []        # Markers to indicate zoomed part
        
        for k in range(3):       # Loop over full trace, zoomed section, and spectrum
            ax_right.append( ax_left[k].twinx() )
            ax_left[k].tick_params ( labelcolor='C0' )
            ax_right[k].tick_params( labelcolor='C1' )
            graph_left.append ( ax_left[k].plot ( [], [], color='C0' )[0] )     # Empty placeholder for datapoints
            graph_right.append( ax_right[k].plot( [], [], color='C1' )[0] )

        graph_marker = ax_left[0].plot ( [], [], [], [], color='C7' )        # Extra plots for interval markers
>>>>>>> 5dc11c8976bd8195c83b23c9998d9ffb4239ce9f

        for k in range(2):       # Loop over full trace, zoomed section, and spectrum
             ax_left[k].set_ylabel ( 'Voltage [V]', color='C0' )
             ax_right[k].set_ylabel( 'Voltage [V]', color='C1' )
             
        ax_left[2].set_ylabel ( 'Power [dB re. max]', color='C0' )
        ax_right[2].set_ylabel( 'Power [dB re. max]', color='C1' )        

        fig.show()   
        
        self.graph_left  = graph_left        # Make axes and graphs available for class
        self.graph_right = graph_right
        self.graph_marker= graph_marker
<<<<<<< HEAD
        self.ax_main     = ax_main
        self.ax_zoom     = ax_zoom
        self.ax_spectrum = ax_spectrum
        self.ax_pulse    = ax_pulse
        self.ax_pulse_spectrum = ax_pulse_spectrum
=======
        self.ax_left     = ax_left
        self.ax_right    = ax_right
>>>>>>> 5dc11c8976bd8195c83b23c9998d9ffb4239ce9f
        self.fig         = fig      

        # Initialise GUI with messages         
        self.update_connected_box( "Not connected", background_color="red", text_color="white" )
        
        self.acquire_button.setEnabled( False )   # Enable or disable buttons according to state
        self.save_button.setEnabled   ( False )
        self.connect_button.setEnabled( True )

        self.statusBar.showMessage('Program started')
        
        self.dso =ps.communication( )       # Interface to c-style wrappers from manufacturer
        self.status = {}                    # Status messages from instrument via c-style wrappers
        self.status["initialisation"]= 0

    #%% Interact with instrument 

    # Connect, configure and start instrument
    def connect_dso( self ):                                         
        self.statusBar.showMessage('Connecting instrument ...')
        errorcode = 0        
        try:
            if "openunit" in self.status:         # Close if an old handle is resident. Probably not possible
                if not("close" in self.status ):        
                    ps.stop_adc( dso.handle, self.status )
                    ps.close_adc( dso.handle, self.status )
            #self.status = {}
        except NameError:
            self.status = {}
        
        # Connect and initialise instrument
        self.status, self.dso = ps.open_adc( self.dso, self.status ) 
        self.dso.connected = True
        
        # Send initial configuration to oscilloscope
        self.status = self.update_vertical()
        self.status = self.update_trigger()
        self.update_sampling()
        self.update_pulser()
        self.update_rf_filter()
        self.update_display()
        
        self.acquire_button.setEnabled( True )
        self.save_button.setEnabled   ( False )
        self.connect_button.setEnabled( False )

        self.statusBar.showMessage('Instrument connected')
        self.update_connected_box( "Connected", background_color="darkgreen", text_color="white" )

        self.runstate.finished = True
        self.runstate.ready    = True
        self.runstate.stop     = False

        return errorcode 

    # Read vertical settings from GUI and send to instrument    
    def update_vertical( self ):
        self.ch[0].enabled   = True # not self.ch_a_pushButton.isChecked()     # Always aquire, may not display
        self.ch[0].vr        = self.read_scaled_value ( self.range_a_comboBox.currentText() )
        self.ch[0].vr        = self.ch[0].vmax()
        self.ch[0].coupling  = self.coupling_a_comboBox.currentText()
        self.ch[0].offset    = self.offset_a_spinBox.value()
        self.ch[0].bwl       = self.bwl_a_comboBox.currentText()        

        self.ch[1].enabled   = True # not self.ch_b_pushButton.isChecked() 
        self.ch[1].vr        = self.read_scaled_value ( self.range_b_comboBox.currentText() )
        self.ch[1].vr        = self.ch[1].vmax()
        self.ch[1].coupling  = self.coupling_b_comboBox.currentText()
        self.ch[1].offset    = self.offset_b_spinBox.value()
        self.ch[1].bwl       = self.bwl_b_comboBox.currentText()    
        
        if self.dso.connected: 
            for k in range(0, 2):
                self.ch[k].no = k
                self.status   = ps.set_vertical(self.dso.handle, self.status, self.ch[k])

        return self.status           
    
    # Read trigger settings from GUI and send to instrument    
    def update_trigger( self ):
        self.trigger.source     = self.trigger_source_comboBox.currentText()    
        self.trigger.enable     = self.trigger.source.lower()[0:3] != 'int'          # Disable trigger if set to internal
        self.trigger.position   = self.trigger_position_spinBox.value()
        self.trigger.direction  = self.trigger_mode_comboBox.currentText()
        self.trigger.level      = self.trigger_level_spinBox.value()
        self.trigger.delay      = self.trigger_delay_spinBox.value()*1e-6
        self.trigger.autodelay  = self.trigger_auto_delay_spinBox.value()*1e-3
        self.trigger.internal   = self.internal_trigger_delay_spinBox.value()*1e-3
        
        self.sampling.pretrigger= self.trigger.position/100                         # Convert from percent to fraction
        
        if self.dso.connected: 
            self.status = ps.set_trigger( self.dso.handle, self.status, self.trigger, self.ch, self.sampling )

        return self.status  
    
    # Read trace length from GUI and set sample rate. No comuincation with instrument
    def update_sampling ( self ):
        self.sampling.timebase  = 3
        self.sampling.ns        = int( self.no_samples_spinBox.value()*1e3 )    # Trace length in kpts
        if self.dso.connected: 
            self.sampling.dt  = ps.get_dt( self.dso.handle, self.sampling)
            self.sample_rate_spinBox.setValue( self.sampling.fs() * 1e-6 )      # Sample rate in MS/s
        
        return 0
    
    def update_pulser( self ):
        self.pulse.envelope = self.pulse_envelope_comboBox.currentText()
        self.pulse.shape    = self.pulse_shape_comboBox.currentText()
        self.pulse.f0       = self.pulse_frequency_spinBox.value()*1e6
        self.pulse.nc       = self.pulse_duration_spinBox.value()
        self.pulse.phi      = self.pulse_phase_spinBox.value()
        self.pulse.a        = self.pulse_amplitude_spinBox.value()
        
        Tp   = self.pulse.Tp()*1e6;
        vlim = 1.2*self.pulse.a
        self.graph_pulse.set_data( self.pulse.t()*1e6, self.pulse.x() )
        self.ax_pulse.set_xlim( -0.2*Tp, 1.2*Tp )
        self.ax_pulse.set_ylim( -vlim,   vlim   )              

        f, psd = self.pulse.powerspectrum( scale= "dB" )
        self.graph_pulse_spectrum.set_data( f/1e6, psd )
        
        # ps.set_signal ( self.dso, self.status, self.sampling,self.pulse )

        return 0
    
    # Read RF noise filter settings from GUI 
    def update_rf_filter ( self ):
        self.rf_filter.type  = self.trigger_source_comboBox.currentText() 
        self.rf_filter.fmin  = self.fmin_spinBox.value()
        self.rf_filter.fmax  = self.fmax_spinBox.value()
        self.rf_filter.order = self.filter_order_spinBox.value()
        
        return 0
    
    #%% Read and save results
    
    # Acquire scaled trace from instrument 
    def acquire_trace( self ):      
        if self.runstate.ready:
            self.runstate.ready = False
            self.update_status_box( "Acquiring data", background_color="darkgreen", text_color="white" )
            self.statusBar.showMessage('Acquiring data ...')
            self.close_button.setEnabled( False )
            self.acquire_button.setEnabled( False )
            self.save_button.setEnabled   ( True )
            while not( self.runstate.stop):
                self.status, self.dso     = ps.configure_acquisition( self.dso, self.status, self.sampling )        
                self.status, self.dso, v  = ps.acquire_trace( self.dso, self.status, self.sampling, self.ch )
                
                self.wfm.v  = v
                self.wfm.dt = self.sampling.dt
                self.wfm.t0 = self.sampling.t0()
                
                self.plot_result()
        
        self.update_status_box( "Stopped", background_color="darkred", text_color="white" )
        self.statusBar.showMessage( 'Ready' )       
        self.runstate.stop = False
        return 0
    

    def plot_result ( self ):
        wfmz= self.wfm.zoom( [ self.display.tmin, self.display.tmax ] )
        
        # Temporary, Should be replaved by organising graphs in lists
        if self.display.ch[0]:
            self.graph_left[0].set_data ( self.wfm.t()*1e6, self.wfm.v[:,0] )                  # Full trace
            self.graph_left[1].set_data (     wfmz.t()*1e6,     wfmz.v[:,0] )                  # Selected interval       
            self.graph_left[2].set_data ( wfmz.f()/1e6, wfmz.powerspectrum(scale="dB")[:,0] )  # Power spectrum
        else:
            self.graph_left[0].set_data ( [], [] )   # Full trace
            self.graph_left[1].set_data ( [], [] )   # Selected interval       
            self.graph_left[2].set_data ( [], [] )   # Power spectrum

        if self.display.ch[1]:
            self.graph_right[0].set_data( self.wfm.t()*1e6, self.wfm.v[:,1] )                  
            self.graph_right[1].set_data(     wfmz.t()*1e6,     wfmz.v[:,1] )                  
            self.graph_right[2].set_data( wfmz.f()/1e6, wfmz.powerspectrum(scale="dB")[:,1] )  
        else:
            self.graph_right[0].set_data ( [], [] )   # Full trace
            self.graph_right[1].set_data ( [], [] )   # Selected interval       
            self.graph_right[2].set_data ( [], [] )   # Power spectrum
            
        self.fig.canvas.draw()            # --- TRY: Probably necessary
        self.fig.canvas.flush_events()    # --- TRY: Probably unnecessary if called in program                 
        self.update_display( )
                
        return 0
        
    # Save result to binary file, automatically generated filename
    def save_results( self ):
        self.statusBar.showMessage('Saving results ...')

        resultfile, resultpath, n = us.find_filename(prefix='US', ext='trc', resultdir='results')
        self.wfm.save( resultpath )
        self.filecounter_spinBox.setValue( n ) 
        self.resultfile_Edit.setText( resultfile ) 
        self.resultpath_Edit.setText( resultpath ) 
        
        self.statusBar.showMessage( f'Result saved to {resultfile}' )
        return 0
        
    # Close instrument connection    
    def close_app(self):
        self.statusBar.showMessage( 'Closing ...' )
        plt.close(self.fig)
        try:
            self.status  =  ps.close_adc( self.dso.handle, self.status )
            errorcode = 0
        except:
            errorcode =-1
        finally:
            self.close()       

        self.statusBar.showMessage( 'Closed' )

        return self.status, errorcode 
    
    # Stop acquisition without closing
    def stop_acquisition( self ): 
        if not(self.runstate.stop ):
            self.runstate.stop = True
            self.statusBar.showMessage( 'Stopping acquisition' )
            self.update_status_box( 'Stopping acquisition', 'darkred', 'white' )

        self.runstate.stop     = True
        self.runstate.finished = True            
        self.runstate.ready    = True            
        self.close_button.setEnabled  ( True )
        self.save_button.setEnabled   ( False )
        self.acquire_button.setEnabled( True )

        return 0        
    
    #%% General GUI read and write
    
    # Update status field on GUI
    def update_status( self, message, append = False ):
        if append:
            old_message = self.status_textEdit.toPlainText()
            message += old_message
        self.status_textEdit.setText(message)  
        return message    
    
    # Write message to status box, optional colours
    def update_status_box( self, message, background_color='white', text_color='black' ):
        self.status_Edit.setText( message )
        self.status_Edit.setStyleSheet(f"background-color : {background_color}; color : {text_color}")
        return 0

    def update_connected_box( self, message, background_color='white', text_color='black' ):
        self.connected_Edit.setText( message )
        self.connected_Edit.setStyleSheet(f"background-color : {background_color}; color : {text_color}")
        return 0
    
    # Interpret a text as a scaled value ( milli, kilo, Mega etc. )
    def read_scaled_value (self, valuestr ): # Read value as number with SI-prefix
        valuestr= valuestr.split(' ')     
        if len(valuestr) == 1:
            mult = 1
        else:
            if   valuestr[1]== 'm':
                mult = 1e-3;
            elif   valuestr[1]== 'k':
                mult = 1e3;
            elif valuestr[1]== 'M':
                mult = 1e6
            elif valuestr[1]== 'G':
                mult = 1e9
            else:
                mult = 1
        value = float( valuestr[0] ) * mult
        return value
       
    def update_display( self ):
        self.display.ch[0] = not self.ch_a_pushButton.isChecked()
        self.display.ch[1] = not self.ch_b_pushButton.isChecked()
        
        tmin   = self.zoom_start_spinBox.value()  # Display in us, calculations in s
        tmax   = self.zoom_end_spinBox.value()        
        vzoom_a= self.read_scaled_value ( self.zoom_vertical_a_comboBox.currentText() )        
        vzoom_b= self.read_scaled_value ( self.zoom_vertical_b_comboBox.currentText() )        
        fmin   = self.zoom_fmin_spinBox.value()  
        fmax   = self.zoom_fmax_spinBox.value()  
        dbmin  = self.zoom_dbmin_spinBox.value()
        
        self.ax_main[0].set_xlim( self.sampling.t0()*1e6, self.sampling.tmax()*1e6 )
        if tmax>tmin:
            self.ax_zoom[0].set_xlim( tmin, tmax  )
            
        self.ax_spectrum[0].set_xlim   ( fmin, fmax  )
        self.ax_pulse_spectrum.set_xlim( fmin, fmax  )
        
        self.ax_main[0].set_ylim ( -self.ch[0].vmax(), self.ch[0].vmax() )
        self.ax_main[1].set_ylim ( -self.ch[1].vmax(), self.ch[1].vmax() )
        self.ax_zoom[0].set_ylim ( -vzoom_a , vzoom_a )
        self.ax_zoom[1].set_ylim ( -vzoom_b , vzoom_b )
        self.ax_spectrum[0].set_ylim   ( dbmin , 0 )
        self.ax_spectrum[1].set_ylim   ( dbmin , 0 )
        self.ax_pulse_spectrum.set_ylim( dbmin , 0 )

        self.graph_marker[0].set_data ( np.full( (2,1), tmin ) , np.array( [ -100, 100 ] ) ) 
        self.graph_marker[1].set_data ( np.full( (2,1), tmax ) , np.array( [ -100, 100 ] ) ) 

        self.display.tmin = tmin*1e-6    
        self.display.tmax = tmax*1e-6       
        
        self.fig.canvas.draw()
        
        return 0
    

#%% Main function
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = read_ultrasound()
    window.show()
    sys.exit(app.exec_())
