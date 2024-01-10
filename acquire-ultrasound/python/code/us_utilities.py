# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 21:46:41 2022

Utility functions for ultrasound measurement systems at USN IMS
Based on former systems in LAbVIEW and Matlab

@author: larsh
"""

import copy 
import numpy as np
from scipy import signal
from scipy.signal import windows
import matplotlib.pyplot as plt
import os
import datetime


#%% 
'''
General constants
micro = 1e-6
milli = 1e-3
'''

'''
Find next number in an 1-2-5-10-20 ... sequence
Used for e.g. for scaling axes.
'''
def scale125(x):
    val = np.array([1, 2, 5, 10])
    e   =  int(np.floor(np.log10(abs(x))))    
    m   = abs(x)/(10**e)    
    sa  = np.sign(val-m+0.01)
    pos = val[np.where(sa>0)]
    mn  = np.min(pos)    
    xn = mn*10**e    
        
    return xn

'''
Automatically set file name
Inputs:     prefix : Characterises measurement type
            ext    : File Extension
Finds next free file name on format prefix_yyyy_mm_dd_nnnn.ext
where yyyy_mm_dd is the date and nnnn is a counter
Saves to subdirectory results
Last counter is saved in file prefix.cnt.
Reads from last counter file and checks that this file is really free
'''
def find_filename( prefix='US', ext='wfm', resultdir=[] ):   
    if not(os.path.isdir( resultdir ) ):     # Create result directory if it does not exist
        os.mkdir( resultdir )         
    counterfile= os.path.join( os.getcwd(), resultdir, f'{prefix}.cnt' )
    
    if os.path.isfile(counterfile):         # Read existing counter file
        with open(counterfile, 'r') as fid:
            n= int( fid.read( ) )  
    else:
        n=0                                 # Set counter to 0 if no counter file exists            
    datecode   = datetime.date.today().strftime('%Y_%m_%d')
    ext        = ext.split('.')[-1]
    
    file_exists= True
    while file_exists:                      # Find lowest number of file not in use
        n+=1
        resultfile  = prefix + '_' + datecode + '_' + f'{n:04d}' + '.' + ext
        resultpath  = os.path.join( os.getcwd(), resultdir, resultfile )
        file_exists = os.path.isfile( resultpath )    
    with open(counterfile, 'wt') as fid:    # Write counter of last result file to counter file
        fid.write( f'{n:d}' ) 
        
    return resultfile, resultpath, n


#%%
'''
Waveform-class. Used to store traces sampled in time, one or several channels. 
Compatible with previous versions used in e.g. LabVIEW and Matlab 
Adapted from LabVIEW's waveform-type, similar to python's mccdaq-library
The fundametal parts are 
    t0  Scalar      Start time
    dt  Scalar      Sample interval
    y   2D array    Each column is a channel
                    Samples as rows
                    
Other parameteres are methods calculated from these ( time vector, 
no. of channels, no. of points, sample rate, ...)
plot()              Plots the traces at standardised format
powerspectrum()     Returns frequency and power spectral density
zoom()              Picks a selected interval
load() and save()   Load from and save to binary format, backwards compatible 
                    to formet LabVIEW and Matlab formats
'''

class waveform:    
    def __init__(self, y=np.zeros( (100,1) ), dt=1, t0=0):
        self.y  = y          # Voltage trace
        if y.ndim == 1:      # Ensure v is 2D
            self.y = self.y.reshape( ( 1, len(y) ) )
        self.dt  = dt         # [s]  Sample interval
        self.t0  = t0         # [s]  Time of first sample 
        self.dtr = 0          # [s]  Interval between measurement blocks.Rarely used
              
    def nc(self):
        return self.y.shape[1]   # Number of channels
    
    def ns(self):   
        return self.y.shape[0]   # Number of points in trace
    
    def nfft(self):
        return 2**(2+( self.ns()-1 ).bit_length() )     # Interpolate spectum by padding zeros
    
    def t(self):             # [s] Time vector from start time and sample interval
        return np.linspace(self.t0, self.t0+self.dt*self.ns(), self.ns() )
        
    def fs(self):          # [Hz]   Sample rate
        return 1/self.dt   
    
    def plot ( self, timeunit="" ):
        if timeunit == "us":
            mult = 1e6
        else:
            mult = 1
            
        plt.plot   ( self.t()*mult, self.y )
        plt.xlabel ( f'Time [{timeunit}]' )
        plt.ylabel ( 'Ampltude' )
        plt.grid   ( True )
        #plt.show()
        
    def f ( self ):
        return np.arange( 0, self.nfft()/2 )/self.nfft() * self.fs()
    
    def powerspectrum ( self, normalise=True, scale="linear" ):
        f, psd = signal.periodogram( self.y, 1/self.dt, nfft=self.nfft(), detrend=False, axis=0 )
        
        if normalise:
            psd = psd/psd.max(axis=0)
            
        if scale.lower() == "db":
                psd = 10*np.log10(psd)
        
        return f, psd
        
    
    def plotspectrum ( self, timeunit="s", frequnit="Hz", fmax=None, normalise=True, scale="dB" ):
        plt.subplot(2,1,1)
        self.plot(timeunit)
        
        plt.subplot(2,1,2)
        if frequnit == "MHz":
            mult = 1e-6
        else:
            mult = 1

        f, psd = self.powerspectrum ( normalise, scale )

        plt.plot( f, psd )
        plt.xlabel( f'Frequency [{frequnit}]' )
        plt.grid  ( True )       
        plt.xlim  ( (0 , fmax) )
        
        if scale.lower() == "db":
            plt.ylabel('Power [dB re. max]')
            plt.ylim((-40.0 , 0))
        else:
            plt.ylabel('Power')
            
        return 0
 
            
    def zoom (self, tlim ):
        wfm  = copy.deepcopy(self)
        nlim = np.flatnonzero ( ( self.t() >= min(tlim) ) & ( self.t() <= max(tlim) ) )       
        t0   = self.t()[np.min(nlim)]
        y    = self.y[nlim]
        
        wfm.t0 = t0
        wfm.y  = y
        
        return wfm
    

    '''
    Load and save 'waveform' files in binary format 
    Data points saved as 4-byte sgl-values
    Format used since 1990s on a variety of platforms (LabWindows, C, LabVIEW, Matlab)
    Uses 'c-order' of arrays and IEEE big-endian byte order
        hd  Header, informative text
        nc  Number of channels
        t0  Start time
        dt  Sample interval
        dtr Interval between blocks. Used only in special cases
        v   Data points (often voltage)
    '''
    def load ( self, filename ):   
        with open(filename, 'rb') as fid:
            n_hd  = int( np.fromfile(fid, dtype='>i4', count=1) )
            hd    = fid.read(n_hd)                                   # Header identifier string
            header= hd.decode("utf-8")              
            
            nc  = int( np.fromfile(fid, dtype='>u4', count= 1) )    # No. of channels            
            t0  = float( np.fromfile(fid, dtype='>f8', count= 1) )  # Start time 
            dt  = float( np.fromfile(fid, dtype='>f8', count= 1) )  # sample interval
            dtr = float( np.fromfile(fid, dtype='>f8', count= 1) )  # Interval between blocks. Raraly used            
            y   = np.fromfile(fid, dtype='>f4', count=-1)           # Traces ar 2D array of float32
            
            self.sourcefile = filename
            self.header = header
            self.t0 = t0
            self.dt = dt
            self.dtr= dtr     # Normally not used, included for backward compatibility
            self.y  = np.reshape(y, (-1, nc))  
            
        return 0
    
    def save(self, filename):   
        header = "<WFM_Python_>f4>"    # Header gives source and data format
        n_hd   = len(header)        
        #y = np.require( self.v, requirements='C' )
        with open(filename, 'xb') as fid:
            fid.write( np.array(n_hd).astype('>i4') )
            fid.write( bytes(header, 'utf-8') )
            fid.write( np.array( self.nc() ).astype('>u4')  )
            fid.write( np.array( self.t0 ).astype('>f8')  )
            fid.write( np.array( self.dt ).astype('>f8')  )
            fid.write( np.array( self.dtr ).astype('>f8') )
            fid.write( self.y.astype('>f4')  )
        return 0                  
                
    
#%%
'''
pulse-class. USed for standardised ultrasound pulses for e.g. trasmitter
Defines a standard pulse from 
    Envelope, from bulit-in window functions
    Shape, as sine, square, triangle, ...
    Centre frequency
    Length as number of cycles
    Phase in degrees
    Amplitude
    Sample interval    
'''
  
class pulse:
    envelope = "rectangular"
    shape    = "sine"
    f0       = 2.0e6    
    nc       = 2.0    
    phi      = 0.0    
    a        = 1.0    
    dt       = 8e-9
    
    def T0 ( self ):
        return 1/self.f0
    
    def Tp ( self ):
        return self.T0() * self.nc
    
    def t ( self):
        return np.arange ( 0, self.Tp(), self.dt )
    
    def ns ( self ):
        return ( len( self.t() ) )
    
    def nfft(self):
        return 2**(3+( self.ns()-1 ).bit_length() )     # Interpolate spectum by padding zeros
    
    def x ( self ):
        match ( self.envelope[0:3].lower() ):
            case "rec":
                win = windows.boxcar( self.ns() )
            case "han":
                win = windows.hann( self.ns() )
            case "ham":
                win = windows.hamming( self.ns() )
            case "tri":
                win = windows.triang( self.ns() )
            case "tri":
                win = windows.triang( self.ns() )
            case "tuk":
                win = windows.tukey( self.ns(), alpha=0.5  )
            case _:
               win = windows.boxcar( self.ns() )

        arg = 2*np.pi *self.f0 *self.t() + np.radians( self.phi )
        match ( self.shape.lower()[0:3] ):
            case "squ":
                y = 1/2* signal.square  ( arg, duty  = 0.5 )  
            case "tri":
                y = 1/2* signal.sawtooth( arg, width = 0.5 )  
            case "saw":
                y = 1/2* signal.sawtooth( arg, width = 1 )  
            case _:
                y = np.cos ( arg ) 
          
        return self.a * win * y
    
    def powerspectrum ( self, scale="linear" ):
        f, psd = signal.periodogram( self.x(), fs=1/self.dt, nfft=self.nfft(), detrend=False )
        psd = psd/psd.max()
        if scale.lower() == "db":
            psd = 10*np.log10(psd)
        return f, psd
            
            