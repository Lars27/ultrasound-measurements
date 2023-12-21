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
from PyQt5 import QtWidgets, uic
import matplotlib.pyplot as plt            # For plotting
import numpy as np
import matplotlib                          # For setup with Qt
import us_utilities as us                  # Utilities made for USN ultrasound lab
import ps5000a_ultrasound_wrappers as ps   # Interface to Picoscope c-style library

#%% Set up GUI from Qt5
matplotlib.use('Qt5Agg')
oscilloscope_main_window, QtBaseClass = uic.loadUiType('aquire_ultrasound_gui.ui')

class dso_filter:   # Digital oscilloscope trigger settings
    type  = "No filter"
    fmin  = 100
    fmax  = 10e6
    order = 2

class acquisition_control:  
    def __init__( self ):
        self.finished = False
       
        
#%% Classes and defs
class read_ultrasound( QtWidgets.QMainWindow, oscilloscope_main_window ):
    def __init__(self):

        QtWidgets.QMainWindow.__init__(self)
        oscilloscope_main_window.__init__(self)
        self.setupUi(self)

        self.runstate = acquisition_control()

        # Initialise instrument variables
        self.ch = []
        self.ch.append( ps.dso_channel ( 0 ) )  # Vertical channel configuration
        self.ch.append( ps.dso_channel ( 1 ) )
        
        self.trigger  = ps.dso_trigger()            # Trigger configuration
        self.sampling = ps.dso_horizontal()         # Horisontal configuration (time sampling)  
        self.rf_filter= dso_filter()             # Filtering of acquired data
        self.wfm      = us.waveform( )              # Result, storing acquired traces
        
        # Connect GUI elements
        self.run_button.clicked.connect( self.connect_dso )
        
        self.ch_a_pushButton.clicked.connect( self.set_vertical )
        self.range_a_comboBox.activated.connect( self.set_vertical )
        self.coupling_a_comboBox.activated.connect( self.set_vertical )
        self.offset_a_spinBox.valueChanged.connect( self.set_vertical )
        self.coupling_a_comboBox.activated.connect( self.set_vertical )

        self.ch_b_pushButton.clicked.connect( self.set_vertical )
        self.range_b_comboBox.activated.connect( self.set_vertical )
        self.coupling_b_comboBox.activated.connect( self.set_vertical )
        self.offset_b_spinBox.valueChanged.connect( self.set_vertical )
        self.coupling_b_comboBox.activated.connect( self.set_vertical )

        self.trigger_source_comboBox.activated.connect( self.set_trigger )
        self.trigger_position_spinBox.valueChanged.connect( self.set_trigger )
        self.trigger_mode_comboBox.activated.connect( self.set_trigger )
        self.trigger_delay_spinBox.valueChanged.connect( self.set_trigger )
        self.trigger_auto_delay_spinBox.valueChanged.connect( self.set_trigger )
        self.internal_trigger_delay_spinBox.valueChanged.connect( self.set_trigger )

        self.sample_rate_spinBox.valueChanged.connect( self.set_sampling )
        self.no_samples_spinBox.valueChanged.connect( self.set_sampling )

        self.filter_comboBox.activated.connect( self.set_rf_filter )
        self.fmin_spinBox.valueChanged.connect( self.set_rf_filter )
        self.fmax_spinBox.valueChanged.connect( self.set_rf_filter )
        self.filter_order_spinBox.valueChanged.connect( self.set_rf_filter )
               
        self.acquire_button.clicked.connect( self.acquire_trace )
        self.save_button.clicked.connect( self.save_results ) 
        self.stop_button.clicked.connect( self.stop_acquisition ) 
        self.close_button.clicked.connect( self.close_app ) 
        
        # Initialise result graph
        plt.ion()         # Does not seem to make any difference
        fig, axs = plt.subplots( nrows=3, ncols=1, figsize=(8, 12) )       
        for k in range( 0, 2):   # Commpn for both subplots
             axs[k].set_xlabel('Time [us]')
             axs[k].set_ylabel('Voltage [V]')
             #axs[k].set_xlim(0 , 20)   
             axs[k].grid( True )              
        
        axs[2].set_xlabel('Frequency [MHz]')
        axs[2].set_ylabel('Power [dB re. max]')
        axs[2].set_xlim(0 , 10)   
        axs[2].grid( True )              

        # Create handle to datapoints, empty so far
        graphs=[ axs[0].plot( [], [] )[0] , axs[1].plot( [], [] )[0], axs[2].plot( [], [] )[0] ]         
        fig.show()        
        self.graph= graphs
        self.axs  = axs
        self.fig  = fig      

        # Initialise GUI with messages         
        self.enable_controls( state=True, active='connect' )                
        self.statusBar.showMessage('Program started')
        

    #%% Interact with instrument 
    
    def connect_dso( self ):            # Connect, configure and start instrument
        errorcode = 0        
        try:
            if "openunit" in status:    # Close if an old handle is resident
                if not("close" in status):        
                    ps.stop_adc( dsohandle, status )
                    ps.close_adc( dsohandle, status )
            #status = {}
        except NameError:
            status = {}

        self.dsohandle = ps.ctypes.c_int16()
        status, adcmax= ps.open_adc( self.dsohandle, status )  # Connect and initialise instrument

        # Send initial configuration to oscilloscope
        status = self.set_vertical( )
        status = self.set_trigger(  )
        self.set_sampling( )
        self.set_rf_filter()

        return errorcode 
    
    
    def set_vertical( self ):
        self.ch[0].enabled   = not self.ch_a_pushButton.isChecked() 
        self.ch[0].vr        = self .read_scaled_value ( self.range_a_comboBox.currentText() )
        self.ch[0].coupling  = self.coupling_a_comboBox.currentText()
        self.ch[0].offset    = self.offset_a_spinBox.value()
        self.ch[0].bwl       = self.bwl_a_comboBox.currentText()        

        self.ch[1].enabled   = not self.ch_b_pushButton.isChecked() 
        self.ch[1].vr        = self.read_scaled_value ( self.range_b_comboBox.currentText() )
        self.ch[1].coupling  = self.coupling_b_comboBox.currentText()
        self.ch[1].offset    = self.offset_b_spinBox.value()
        self.ch[1].bwl       = self.bwl_b_comboBox.currentText()    
        
        for k in range(0, 2):
            self.ch[k].no      = k
            status, self.ch[k] = ps.set_vertical(self.dsohandle, self.status, self.ch[k])

        return status
    
    
    def set_trigger( self ):
        self.trigger.source  = self.trigger_source_comboBox.currentText()    
        self.trigger.enable  = self.trigger.source.lower()[0:3] != 'int'          # Disable trigger if set to internal
        self.trigger.level   = self.trigger_level_spinBox.value()
        self.trigger.position= self.trigger_position_spinBox.value()
        self.trigger.mode    = self.trigger_mode_comboBox.currentText()
        self.trigger.delay   = self.trigger_delay_spinBox.value()*1e-6
        self.trigger.auto    = self.trigger_auto_delay_spinBox.value()*1e-3
        
        status = ps.set_trigger( self.dsohandle, self.status, self.trigger, self.ch )
        
        return status
    
    
    def set_sampling ( self ):
        self.sampling.timebase  = 3
        self.sampling.ns        = self.no_samples_spinBox.value()*1e3
        self.sampling.pretrigger= self.trigger.position*1e-2
        self.sampling.dt        = ps.get_dt( self.dsohandle, self.sampling)
        self.sampling.fs        = 1/self.sampling.dt

        self.sample_rate_spinBox.setValue( self.sampling.fs*1e-6 )
        
        return 0
    
    
    def set_rf_filter ( self ):
        self.rf_filter.type  = self.trigger_source_comboBox.currentText() 
        self.rf_filter.fmin  = self.fmin_spinBox.value()
        self.rf_filter.fmax  = self.fmax_spinBox.value()
        self.rf_filter.order = self.filter_order_spinBox.value()
        
        return 0
    
    #%% Read and save results
    
    def acquire_trace( self ):
        v = np.zeros( shape=( self.sampling.ns, 2) )
        for k in [0,1]:
            status, v[:,k], n_recorded= ps.acquire_trace( self.dsohandle, self.status, self.sampling, self.ch[k] )
        
        self.wfm.v  = v
        self.wfm.dt = self.sampling.dt
        self.wfm.t0 = self.sampling.t0
        self.wfm.t0 = self.sampling.t0

        self.wfm.plot()        

        return 0

    def save_results( self ):
        [ resultfile, resultpath ] = us.find_filename(prefix='US', ext='trc', resultdir='results')
        us.save_impedance_result( resultpath, self.analyser.res )
        self.resultfile_Edit.setText( resultfile ) 
        self.resultpath_Edit.setPlainText( resultpath ) 
        self.statusBar().showMessage( f'Result saved to {resultfile}' )
        return 0
        
        
    def close_app(self):
        self.statusBar.showMessage( 'Closing' )
        plt.close(self.fig)
        try:
            self.analyser.close()
            errorcode = 0
        except:
            errorcode =-1
        finally:
            self.close()       
        return errorcode 
    
    def stop_acquisition( self ): 
        self.runstate.finished = True
        self.statusBar.showMessage( 'Stopping acquisition' )
        self.update_status_box( 'Finishing', 'orange', 'white' )
        return 0
        
    
    #%% General GUI read and write
    
    def update_status( self, message, append = False ):
        if append:
            old_message = self.status_textEdit.toPlainText()
            message += old_message
        self.status_textEdit.setText(message)  
        return message    
    
    def update_status_box( self, message, background_color='white', text_color='black' ):
        self.status_Edit.setText( message )
        self.status_Edit.setStyleSheet(f"background-color : {background_color}; color : {text_color}")
        return 0
            
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
                print('valuestr M')
            elif valuestr[1]== 'G':
                mult = 1e9
            else:
                mult = 1
        value = float( valuestr[0] ) * mult
        return value
    
    def enable_controls( self, state=False, active='connect' ):
        self.acquisition_tabWidget.setTabEnabled( 0, state )
        self.acquisition_tabWidget.setTabEnabled( 1, state )
        self.acquisition_tabWidget.setTabEnabled( 2, state )
        self.acquisition_tabWidget.setTabEnabled( 3, state )
        self.acquire_button.setEnabled( state )
        match active.lower():
            case 'control':
                self.acquisition_tabWidget.setCurrentIndex( 0 )
            case 'connect':
                self.acquisition_tabWidget.setCurrentIndex( 2 )
            case 'scale':
                self.acquisition_tabWidget.setCurrentIndex( 3 )        
        return 0


    

#%% Main function
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = read_ultrasound()
    window.show()
    sys.exit(app.exec_())
