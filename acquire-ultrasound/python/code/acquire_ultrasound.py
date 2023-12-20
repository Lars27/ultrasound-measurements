# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 22:20:43 2022

@author: larsh

Contol and read data from Trewmax TE300x impedance analyser
Using serial interface libraries in 'trewmac300x_serial.py'

GUI interface made in Qt Designer, ver. 5

Sets up a GUI to control the system
Communicates using an emulated  COM-port on the computer, default COM7
Reads, plots and saves a complex impedance spectrum (f,Z).
Results are read and saved as frequency, abs(Z) and arg(Z), where Z(f) is complex impedance
"""

#%% Libraries
import sys
from PyQt5 import QtWidgets, uic
import matplotlib.pyplot as plt     # For plotting
import matplotlib                   # For setup with Qt
import us_utilities as us           # Utilities made fro USN ultrasound lab
import trewmac300x_serial as te     # Serial inerface to Trewmac analysers

#%% Set up GUI from Qt5
matplotlib.use('Qt5Agg')
analyser_main_window, QtBaseClass = uic.loadUiType('aquire_ultrasound_gui.ui')


class acquisition_control:  
    def __init__( self ):
        self.finished = False
       
        
#%% Class and defs
class read_analyser(QtWidgets.QMainWindow, analyser_main_window):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        analyser_main_window.__init__(self)
        self.setupUi(self)

        # Initialise instrument
        self.runstate = acquisition_control()
        self.analyser = te.te300x()
        
        # Connect GUI elements
        self.run_button.clicked.connect( self.connect_dso )
        
        self.fmin_SpinBox.valueChanged.connect( self.set_filter )
        self.fmax_SpinBox.valueChanged.connect( self.set_filter )
        self.filter_order_spinBox.valueChanged.connect( self.set_filter )
        self.filter_comboBox.valueChanged.connect( self.set_filter )
        
        self.ch_a_pushButton.valueChanged.connect( self.enable_channel, ch = 'A' )
        self.ch_b_pushButton.valueChanged.connect( self.enable_channel, ch = 'B' )
        
        self.np_SpinBox.valueChanged.connect( self.set_frequency_range )
        self.average_SpinBox.valueChanged.connect( self.set_average )
        self.z0_SpinBox.valueChanged.connect(self.set_z0)       
        self.output_SpinBox.valueChanged.connect( self.set_output )
        self.fscalemin_SpinBox.valueChanged.connect( self.set_f_scale )
        self.fscalemax_SpinBox.valueChanged.connect( self.set_f_scale )       
        self.Zscalemin_comboBox.activated.connect( self.set_Z_scale )
        self.Zscalemax_comboBox.activated.connect( self.set_Z_scale )
        self.connect_button.clicked.connect( self.connect_analyser )
        self.acquire_button.clicked.connect( self.acquire_trace )
        self.save_button.clicked.connect( self.save_results ) 
        self.stop_button.clicked.connect( self.stop_acquisition ) 
        self.close_button.clicked.connect( self.close_app ) 
        
        # Initialise result graph
        #plt.ion()         # Does not seem to make any difference
        fig, axs = plt.subplots( nrows=2, ncols=1, figsize=(8, 12) )       
        for k in range( 0, 2):   # Commpn for both subplots
            axs[k].set_xlabel('Frequency [MHz]')
            axs[k].set_xlim(0 , 20)   
            axs[k].grid( True )              
        axs[0].grid( visible=True, which='minor', axis='y' )
        axs[0].set_ylabel('|Z| [Ohm]')
        axs[1].set_ylabel('arg(Z) [Deg]')       
        axs[0].set_ylim( 1, 1e6 )
        axs[1].set_ylim( -90, 90 )

        # Create handle to datapoints, empty so far
        graphs=[ axs[0].semilogy( [], [] )[0], axs[1].plot( [], [] )[0] ]         
        fig.show()        
        self.graph= graphs
        self.axs  = axs
        self.fig  = fig      

        # Initialise GUI with messages         
        self.enable_controls( state=False, active='connect' )                
        self.statusBar().showMessage('Program started')
        

    #%% Program run 
    
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

        dsohandle = ctypes.c_int16()
        status, adcmax= ps.open_adc( dsohandle, status )  # Connect and initialise instrument

        # Define vaariables for oscilloscope configuration
        sampling = ps.dso_horizontal()                  # Horizontal (time) configuration
        trigger  = ps.dso_trigger( "A", 0.5 )           # Trigger configuration

        ch = []                                         # Vertical (Volt) configuration as array with each channel
        ch.append( ps.dso_channel ( 0, 10, adcmax ) )
        ch.append( ps.dso_channel ( 1,  1, adcmax ) )
        
        # ch[0].vr = 1
        # ch[1].vr = 10
        
        # Send initial configuration to oscilloscope
        status, ch[0] = ps.set_vertical(dsohandle, status, ch[0])
        status, ch[1] = ps.set_vertical(dsohandle, status, ch[1])

        trigger.source = "B"
        trigger.level  = 0.5
        trigger.adcmax = adcmax
        status = ps.set_trigger(dsohandle, status, trigger, ch)

        sampling.timebase   = 3
        sampling.ns         = 500
        sampling.pretrigger = 0.1
        #sampling.nmax = sampling.ns
        sampling.dt   = ps.get_dt(dsohandle, sampling)

        return errorcode 
    
    
    def set_trigger( self ):
        trigger.source   = self.trigger_source_comboBox.value() 
        trigger.position = self.trigger_position_SpinBox.value()
        z0 = self.analyser.set_z0 ( z0 )
        self.update_status( f'Z0 = {z0:.1f} Ohm\n', append=True )
        self.statusBar().showMessage( f'Reference inpedance changed to {z0:.1f} Ohm' )        
        return z0

        
        
    def close_app(self):
        self.statusBar().showMessage( 'Closing' )
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
        self.statusBar().showMessage( 'Stopping acquisition' )
        self.update_status_box( 'acquisition', 'Finishing', 'orange', 'white' )
        return 0
        
    def save_results( self ):
        [ resultfile, resultpath ] = us.find_filename(prefix='US', ext='trc', resultdir='results')
        us.save_impedance_result( resultpath, self.analyser.res )
        self.resultfile_Edit.setText( resultfile ) 
        self.resultpath_Edit.setPlainText( resultpath ) 
        self.statusBar().showMessage( f'Result saved to {resultfile}' )
        return 0
    
    def update_status( self, message, append = False ):
        if append:
            old_message = self.status_textEdit.toPlainText()
            message += old_message
        self.status_textEdit.setText(message)  
        return message    
    
    def update_status_box( self, message_type, message, background_color='white', text_color='black' ):
        match message_type.lower():
            case 'connection':
                box = self.portstatus_Edit
            case 'acquisition':
                box = self.acquisitionstatus_Edit 
        box.setText( message )
        box.setStyleSheet(f"background-color : {background_color}; color : {text_color}")
        return 0

    def enable_controls( self, state=False, active='connect' ):
        self.main_tabWidget.setTabEnabled(0, state)
        self.main_tabWidget.setTabEnabled(1, state )
        self.acquire_button.setEnabled( state )
        match active.lower():
            case 'control':
                self.main_tabWidget.setCurrentIndex( 0 )
            case 'connect':
                self.main_tabWidget.setCurrentIndex( 2 )
            case 'scale':
                self.main_tabWidget.setCurrentIndex( 3 )        
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
   

    #%% Instrument interaction

            

        #%% Configure ADC

    
    #%%    
    def set_filter ( self ):
        fmin  = self.fmin_spinBox.value()
        fmax  = self.fmax_spinBox.value()
        order = self.filter_order_spinBox.value()
        filter = self.filter_comboBox.value()
                
        return 0
    
    def enable_channel( self, ch ):
        
        
    def set_average( self ):
        average = self.average_SpinBox.value()
        average = self.analyser.set_averaging ( average )
        self.update_status( f'average = {average:3d}\n', append=True )
        self.statusBar().showMessage( f'Averaging changed to {average:3d}' )
        return average
        
    def set_output( self ):
        output = self.output_SpinBox.value()
        output = self.analyser.set_output ( output )
        self.update_status( f'Output = {output:.0f} %\n', append=True )
        self.statusBar().showMessage( f'Output level changed to {output:.0f} %' )        
        return output
    
    def set_z0( self ):
        z0 = self.z0_SpinBox.value()
        z0 = self.analyser.set_z0 ( z0 )
        self.update_status( f'Z0 = {z0:.1f} Ohm\n', append=True )
        self.statusBar().showMessage( f'Reference inpedance changed to {z0:.1f} Ohm' )        
        return z0

    def acquire_trace( self ):
        self.resultfile_Edit.setText('Not saved')        
        self.runstate.finished = False
        self.enable_controls( state=False, active='scale' )       
        self.update_status_box( 'acquisition', 'Acquiring', 'green', 'white'  )
        while not( self.runstate.finished):
            self.statusBar().showMessage( 'Reading data from analyser' )        
            self.update_status( 'Reading data from analyser ... \n', append=True )
            self.analyser.read_sweep_point_by_point( self.graph , self.fig )
            self.update_status( 'Finished\n', append=True )                
            self.fig.canvas.draw()          # --- TRY: Probably not sufficient
            self.fig.canvas.flush_events()  # --- TRY: Probably good            
        self.statusBar().showMessage( 'Reading from analyser finished' )     
        self.enable_controls( state=True, active='control' )
        self.update_status_box( 'acquisition', 'Finished'  )
        return 0

    def set_f_scale( self ):
        fmin = self.fscalemin_SpinBox.value()
        fmax = self.fscalemax_SpinBox.value()
        if fmin<fmax:
            self.axs[0].set_xlim( fmin, fmax )
            self.axs[1].set_xlim( fmin, fmax )            
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()  
            self.statusBar().showMessage( 'Frequency axis changed' ) 
        return 0
        
    def set_Z_scale( self ):
        Zstr = self.Zscalemin_comboBox.currentText()
        Zmin = self.read_scaled_value ( Zstr )
        Zmax = self.read_scaled_value ( self.Zscalemax_comboBox.currentText() )
        if Zmin<Zmax:
            self.axs[0].set_ylim( Zmin, Zmax )        
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()        
            self.statusBar().showMessage( 'Impedance axis changed' ) 
        return 0

#%% Main function
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = read_analyser()
    window.show()
    sys.exit(app.exec_())
