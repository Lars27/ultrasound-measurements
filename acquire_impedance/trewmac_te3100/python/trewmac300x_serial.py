# -*- coding: utf-8 -*-
"""
Libraries for communication with Trewmac TE300x network/impedance analysers 
using serial ports.

Open and configure a port
Send commands to configure the analyser
Read results and settings from analyser
Close port

Created on Mon Dec 12 11:36:32 2022

@author: larsh
"""

import serial    # Uses serial communication (COM-ports)
import numpy as np
import time
# import os
# import datetime

terminator=b'\r'

#%% Result structure
class te_result:  # Initialise with impossible values. To be set at object creation
    def __init__( self ):
        self.fmin  = 0.0
        self.fmax  = 0.0
        self.npts    = 0
        
        self.averaging =-1.0
        self.z0        =-1.0
        self.output    =-1.0
        
        self.format = 'undefined'
        self.mode   = 'undefined'
        self.baudrate = 0.0
        
        self.f     = np.zeros( 2 )        
        self.Z     = np.zeros( (2,2) )       
        
#%% Methods
class te300x:
    def __init__( self ):
        self.res  = te_result()
        return       
        
    def connect( self, port = 'COM1', timeout = 5 ):
        try:
            self.port = serial.Serial( port, 115200, timeout = timeout )    
            self.port.set_buffer_size(rx_size = 100000, tx_size = 100000)
            self.set_frequencyrange( fmin= 300e3, fmax= 20e6, npts= 500 )
            self.set_averaging ( avg = 16 )
            self.set_z0 ( z0 = 50 )
            self.set_output ( output = 100 )
            self.set_format( dataformat = 'polZ' )
            self.set_mode ( mode = 'T' )
            errorcode = 0
        except: #serial.SerialException:
            self.port = -1            
            errorcode = -1
        return errorcode    
            
    def close(self):
        self.port.close()
        return 0      

    #%% Utilities
    def read_text( self, max_length = 1000 ):
        rep = self.port.read_until( expected= terminator, size= max_length )
        return rep.removesuffix( terminator ).decode()
        
    def read_values( self, max_length = 1000 ):
        rep = self.port.read_until( expected= terminator, size= max_length )
        rep = rep.split(b',')
        rep = list(map(float, rep))
        return rep
    
    def read_sweep_values(self):     
        finished = False
        val=b''
        while not(finished):  # Read multiple times until all data acquired
            val = val + self.port.read_until( expected = b'END\r' )   
            finished = (self.port.in_waiting == 0)
        return val.decode()
    
    def read_sweep_line(self):
        f   = Zmag = Zphi = 0
        val = self.read_text()           
        finished = (val=='END') 
        if not(finished):
            line= val.split(',')
            f    = float( line[0] )
            Zmag = float( line[1] )
            Zphi = float( line[2] )            
        return [f, Zmag, Zphi, finished ]                             

    #%%
    """
    Command references found in Trewmac TE 30000/30001 Hardvare guide, 
    TM1227, ver. 10.0, Oct 2013
    """
    # Read device information   
    def read_version(self):
        self.port.write(b'V')
        return self.read_text()
    
    def read_format(self):
        self.port.write(b'I')
        return self.read_text()
    
    def send_configure ( self, parameter, value ):    # Send instrument configuration command
        command = f'C{parameter}'
        fullcommand =  command.encode() + terminator + value.encode() + terminator
        self.port.write( fullcommand )
        return self.read_text()

    def send_freqrange ( self, parameter, value ):    # Send instrument frequency range command
        fullcommand =  parameter.encode() + value.encode() + terminator
        self.port.write( fullcommand )
        response = self.read_text()
        return float( response.split('=')[1] )

    def set_frequencyrange( self, fmin= 300e3, fmax= 20e6, npts= 801 ):
        self.res.fmin = self.send_freqrange ( 'S', f'{fmin/1e6:.2f}'  )  
        self.res.fmax = self.send_freqrange ( 'E', f'{fmax/1e6:.2f}'  )
        npts          = self.send_freqrange ( 'P', f'{npts:d}'  ) 
        self.res.npts = int (npts )                             
        return 0
    
    def set_format( self, dataformat = 'polZ' ):   # Measurement format fixed to polar impedance
        result = self.send_configure ( 'format', dataformat )      
        self.res.format = result.split('=')[1] 
        return self.res.format 
    
    def set_averaging ( self, avg = 64 ):         
        result = self.send_configure ( 'averaging', f'{avg:d}' )       
        self.res.averaging = int( result.split('=')[1] )
        return self.res.averaging

    def set_output ( self, output = 100 ):  
        result = self.send_configure ( 'output', f'{output:.0f}' )      
        value  = result.split('=')[1]
        self.res.output  = float( value.split('%')[0] )
        return self.res.output  
    
    def set_z0 ( self, z0 = 50 ):  
        result = self.send_configure ( 'zo', f'{z0:0.1f}' )    
        self.res.z0  = float( result.split('=')[1] )
        return self.res.z0
    
    def set_mode ( self, mode = 'T' ):  
        if mode.lower()[0] == 't':
            value = 'S11'
        else:
            value= 'S21'
        result = self.send_configure ( 'mode', value )      
        self.res.mode  = result.split('=')[1]
        return self.res.mode 

    def set_baudrate( self, baud = 115200 ):  
        if baud > 10000:
            baud = 115200
        else:
            baud = 9600        
        result = self.send_configure( 'baud', f'{baud:d}' )      
        self.res.baudrate  = result.split(' ')[2]
        return self.res.baudrate            
    
    #%% Read results
    def read_single( self, freq ):
        f_command= f'F{freq/1e6:.2f}\r'.encode()   # Command to read single frequency. Ref. Trewmac Hardvare guide, TM1227
        self.port.write( f_command )
        rep = self.read_values()
        self.res.f    = np.array( rep[0] )
        self.res.Z    = np.stack( ( np.array(rep[0]) , np.array(rep[1]) ) ) 
        return rep
   
    def read_sweep_point_by_point( self, resultgraph = [], resultfig = [] ):  
        n_old = len(self.res.f)
        if n_old == self.res.npts:
            f      = self.res.f.copy()
            Zmag   = self.res.Z[:,0].copy()
            Zphase = self.res.Z[:,1].copy()    
        else:
            f     = np.full( self.res.npts, np.nan )
            Zmag  = np.full( self.res.npts, np.nan )
            Zphase= np.full( self.res.npts, np.nan )
        
        self.port.write(b'N')  # Command to read frequency scan. Ref. Trewmac Hardvare guide, TM1227
        header   = self.read_text()
        finished = False
        nf       = 0
        while not(finished):               
            ret= self.read_sweep_line()
            finished = ret[3] or (nf >= self.res.npts )
            if not(finished):
                f[nf]     = ret[0] 
                Zmag[nf]  = ret[1] 
                Zphase[nf]= np.radians(ret[2])   # Phase is saved as radians but plotted as degrees
                if resultgraph and resultfig:
                    resultgraph[0].set_data( f/1e6, Zmag ) 
                    resultgraph[1].set_data( f/1e6, np.degrees( Zphase ) ) 
                    resultfig.canvas.draw()            # --- TRY: Probably necessary
                    resultfig.canvas.flush_events()    # --- TRY: Probably unnecessary if called in program                
                nf+=1
        Z = np.stack(( np.array(Zmag), np.array(Zphase) ))
        Z = np.require( Z.T, requirements='C' )   # Transpose and ensure 'c-contiguous' array
        self.res.f  = f.copy()
        self.res.Z  = Z.copy()
        self.res.nf = nf
        return 0    
