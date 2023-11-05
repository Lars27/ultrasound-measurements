# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 21:46:41 2022

@author: larsh
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import datetime

#%% Basic utility-functions 
""" 
Next number in an 1-2-5-10 ... sequence, e.g. for scaling axes
"""
def scale125(x):
    val = np.array([1, 2, 5, 10])               # Scale to use
    e   = int( np.floor( np.log10( abs(x)) ) )  # Split number in exponent
    m   = abs(x)/(10**e)                        # and antissa , x=m*10^e   
    pos = val[ np.where( val> m+0.01 ) ]
    mn  = np.min(pos)                           # Lowest allowable number larger than x 
    xn  = mn* 10**e    
        
    return xn

"""
Sub-sample interpolation to find maximum of function y(t)
Finds value of t where y has maximum by parabolic fit
"""
def subsample_peak( y, t, type='max' ):    
    if type=='max':
        km = np.argmax( y ) 
    else:
        km = np.argmin( y ) 
        
    yz = y[ km-1 : km+2 ]           # Maximum and its two neighbour ponts
    
    c  = yz[1]                      # Fit polynomial y=ax^2 + bx + c through three points around maximum
    b  = ( yz[2] - yz[0] )/2;       # Analytic solution maximum relative to center point
    a  = ( yz[2] + yz[0] )/2 - c;   
    ki = -b/(2*a)
    
    dt= ( t[km+1] - t[km-1] )/2     # Sampling interval
    tm = t[km]+ ki*dt;              # Time at maximum
        
    return tm

"""
Define file naming and format 
File names made from date and counter
"""
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
    return [ resultfile, resultpath ]


#%% 
""" 
Define 'waveform'-class, used to handle time traces
One or several channels sampled in time at constqant sample interval
Compatible with previous versions used in e.g. LabVIEW and Matlab 
Adapted from LabVIEW's waveform-type, partly similar to python's mccdaq-library
"""
class waveform    :
    def __init__(self, v=np.zeros((1000,1)), dt=1, t0=0):
        self.v  = v         # [V]  Voltage trace
        if v.ndim == 1:     # Ensure v is 2D array even if only one channel
            self.v = self.v.reshape((1, len(v)))
        self.dt = dt        # [s]  Sample interval
        self.t0 = t0        # [s]  Time of first sample 
                
    def ns(self):           # Number of points in trace
        return len(self.v)   
    
    def t(self):            # [s] Time vector from start time and sample interval
        return np.linspace(self.t0, self.t0+self.dt*self.ns(), self.ns() )
        
    def fs(self):          # [Hz] Sample rate
        return 1/self.dt
     
    def plot( self, ax, timeunit="s", amplitudeunit="V" ):   # Plot time trace, v(t)
        if timeunit == "us":
            mult = 1e6
        elif timeunit == "ms":
            mult = 1e3
        else:
            mult = 1            
        ax.plot( self.t()*mult, self.v )
        ax.set_xlabel( f'Time [{timeunit}]' )
        ax.set_ylabel( f'Ampltude [{amplitudeunit}]' )
        ax.grid(True)
        #plt.show()

        return 0

    def powerspectrum( self, normalise=True, scale="linear", padding=0 ):      # Calculate power spectrum of v
        if padding > 0:                     # Consider replacing with scipy.signal.periodogram
            nfft= int( np.exp2( np.ceil( np.log2(self.ns()) ) + padding-1 ) ) 
        else:
            nfft= self.ns()
            
        # f   = np.arange( 0, nfft/2 )/nfft * self.fs()
        f   = np.fft.fftfreq( nfft, d=self.dt )     # [Hz] Frequency vector
        fv  = np.fft.fft( self.v, n=nfft, axis=0 )  # FFT of v with selected no. of points
        p   = np.abs( fv[0:f.size, :] )             # Absolute value of FFT
        if normalise:
            p = p / p.max( axis=0 )
        if scale.lower() == "db":
            p = 20* np.log10(p)
            
        self.f   = f            
        self.nfft= nfft            
        return p    
    
    def plotspectrum(self, ax, timeunit="s", frequnit="Hz", fmax=None, normalise=True, scale="dB", padding=0 ):       
        if frequnit == "MHz":
            mult = 1e-6
        elif frequnit == "kHz":
            mult = 1e-3
        else:
            mult = 1
            
        ps= self.powerspectrum( normalise, scale, padding )
        ax.plot( self.f*mult, ps )
        ax.set_xlim( (0 , fmax) )
        ax.grid( True )       
        ax.set_xlabel( f'Frequency [{frequnit}]' )
        if scale.lower() == "db":
            ax.set_ylabel('Power [dB re. max]')
            ax.set_ylim( (-40.0 , 0) )
        else:
            ax.set_ylabel('Power')
        return 0    
            
    """ 
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
    """        
    def load(self, filename):   # Load wavefrom-file. 
        with open( filename, 'rb' ) as fid:
            n_hd= int( np.fromfile(fid, dtype='>i4', count=1) )
            hd  = fid.read(n_hd)
            header= hd.decode("utf-8")
            nc  =   int( np.fromfile( fid, dtype='>u4', count= 1) )
            t0  = float( np.fromfile( fid, dtype='>f8', count= 1) )
            dt  = float( np.fromfile( fid, dtype='>f8', count= 1) )
            dtr = float( np.fromfile( fid, dtype='>f8', count= 1) )
            
            v   = np.fromfile( fid, dtype='>f4', count=-1 )
            
            self.sourcefile = filename
            self.header = header
            self.nc = nc
            self.t0 = t0
            self.dt = dt
            self.dtr= dtr     # Normally not used, included for backward compatibility
            self.v  = np.reshape(v, (-1, nc))     
        return 0                               

    def save(self, filename):   
        hd= "<WFM_Python_>f4>"
        n_hd=len(hd)
        with open(filename, 'xb') as fid:
            fid.write( np.array(n_hd).astype('>i4'))
            fid.write( bytes(hd, 'utf-8'))
            fid.write( np.array(self.nc).astype('>u4'))
            fid.write( np.array(self.t0).astype('>f8'))
            fid.write( np.array(self.dt).astype('>f8'))
            fid.write( np.array(self.dtr).astype('>f8'))
            fid.write( self.v.astype('>f4') )
        return 0       
    
    """ 
    Impedance measurement saved as waveform with complex numbers   
    Save result of impedance measurement. 
    Accepts struct with fields f and Z=[Zmag, Zphase] 
    """
    def save_impedance_result( resultfile, Zresult ):
        header   = "<Z_mag_phase_Python_bef4>"
        n_hd     = len( header )       
        meastime = datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
        n_tm     = len( meastime )
        
        f    = np.expand_dims( Zresult.f, axis=1 )        # Frequency formatted as 2D column-vector
        res  = np.concatenate( ( f, Zresult.Z ), axis=1 ) # Result 2D aray, [f Z]
        res  = np.require( res, requirements='C' )        # Ensure 'c-contiguous' array for saving        
        with open(resultfile, 'xb') as fid:
            fid.write( np.array(n_hd).astype('>i4') )     # Header lenght
            fid.write( bytes(header, 'utf-8') )           # Header as string bytes
            fid.write( np.array(n_tm).astype('>i4') )     # Time string lenght
            fid.write( bytes(meastime, 'utf-8') )         # Measurement time as string bytes
            fid.write( np.array( 3 ).astype('>u4') )      # No of channels: freq, Zmag and Zphase
            fid.write( res.astype('>f4') )                # Impedance magnitude and phase
        return 0

                
        
            