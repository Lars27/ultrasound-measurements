# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 21:46:41 2022

Utility functions for ultrasound measurement systems at USN IMS
Based on former systems in LabVIEW and Matlab

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
class Waveform:    
    '''
    Used to store traces sampled in time, one or several channels. 
    Compatible with previous versions used in e.g. LabVIEW and Matlab 
    Adapted from LabVIEW's waveform-type, similar to python's mccdaq-library
    The fundametal parts are 
        t0  Scalar      Start time
        dt  Scalar      Sample interval
        x   2D array    Results. Each column is a channel, samples as rows
                    
    Other parameters are methods calculated from these: time vector, 
    no. of channels, no. of points, sample rate, etc.

    Other methods 
    plot()              Plots the traces at standardised format
    powerspectrum()     Returns frequency and power spectral density
    zoom()              Picks a selected interval
    load() and save()   Load from and save to binary format, backwards 
                        compatible to formats used with e.g. LabVIEW and Matlab 
    '''
    
    def __init__(self, x=np.zeros((100,1)), dt=1, t0=0):
        self.x = x        # Voltage traces as 2D numpy array
        if x.ndim == 1:   # Ensure v is 2D
            self.x = self.x.reshape((1, len(x)))
        self.dt = dt      # [s]  Sample interval
        self.t0 = t0      # [s]  Time of first sample 
        self.dtr= 0       # [s]  Interval between blocks.Rarely used
              
    
    def n_channels(self):
        ''' # Number of channels in trace '''
        return self.y.shape[1]   
    
    def n_samples(self):   
        ''' Number of points in trace '''
        return self.y.shape[0]   
    
    
    def n_fft(self):
        ''' Number of points to calculate spectrum, interpolated by padding zeros '''
        n_up = 2**(1+self.n_samples()-1).bit_length()  # Next power of 2
        return max(n_up, 1024)

    
    def t(self):             
        '''Time vector calculated from start time and sample interval [s] '''
        return np.linspace(self.t0, self.t0+self.dt*self.ns(), self.ns() )

        
    def fs(self):          
        ''' Sample rate [Hz] '''
        return 1/self.dt   

    
    def plot(self, time_unit="s"):
        ''' Unit for plotting time traces, also used to scale spectra '''
        plot_pulse(self.t(), self.y, time_unit=time_unit)    

        
    def f (self):
        ''' Frequency vector [Hz] '''
        return np.arange( 0, self.n_fft()/2 )/self.n_fft() * self.fs()

    
    def powerspectrum (self, normalise=False, scale="linear"):
        ''' Calculate power spectrum of trace '''
        f, psd = powerspectrum( self.x, self.dt, nfft=self.n_fft(), 
                               scale=scale, normalise=normalise)       
        return f, psd      

    
    def plot_spectrum ( self, time_unit="s", frequnit="Hz", fmax=None, 
                      normalise=True, scale="dB" ):
        ''' Plot trace and power spectrum '''        
        plot_spectrum ( self.t(), self.x, time_unit=time_unit, f_max=None, 
                       nfft=self.n_fft(), normalise=normalise, scale=scale)            
        return 0

            
    def zoom (self, tlim ):  
        ''' Extract copy of trace from specified interval '''
        wfm  = copy.deepcopy(self)
        nlim = np.flatnonzero((self.t() >= min(tlim)) 
                              & (self.t() <= max(tlim)))       
        t0= self.t()[np.min(nlim)]
        y = self.y[nlim]
        
        wfm.t0= t0
        wfm.y = y
        
        return wfm
    

    def load(self, filename):   
        '''
        Load 'Waveform' files in binary format as 4-byte (sgl) floats
        Compatible with internal format used since 1990s on a variety of 
        platforms (LabWindows, C, LabVIEW, Matlab)
        Uses 'c-order' of arrays and IEEE big-endian byte order
            hd  Header, informative text
            nc  Number of channels
            t0  Start time
            dt  Sample interval
            dtr Interval between blocks. Used only in special cases
            v   Data points (often voltage)
            
        Companion to save()    
        '''        
        with open(filename, 'rb') as fid:
            n_header= int(np.fromfile(fid, dtype='>i4', count=1))
            header_bytes = fid.read(n_header)       
            header = header_bytes.decode("utf-8")              
            
            n_ch= int(np.fromfile(fid, dtype='>u4', count= 1))  # No. of channels            
            t0 = float(np.fromfile(fid, dtype='>f8', count= 1)) # Start time 
            dt = float(np.fromfile(fid, dtype='>f8', count= 1)) # sample interval
            dtr= float(np.fromfile(fid, dtype='>f8', count= 1)) # Block interval, raraly used            
            x  = np.fromfile(fid, dtype='>f4', count=-1)   # Traces, 2D array of float32
            
            self.sourcefile = filename
            self.header = header
            self.t0 = t0
            self.dt = dt
            self.dtr= dtr     # Rarely used, for backward compatibility
            self.x  = np.reshape(x, (-1, n_ch))  
            
        return 0
    

    def save(self, filename):   
        '''
        Load 'Waveform' files in binary format as 4-byte (sgl) floats
        Compatible with internal format used since 1990s on a variety of 
        platforms (LabWindows, C, LabVIEW, Matlab)
        Uses 'c-order' of arrays and IEEE big-endian byte order
            hd  Header, informative text
            nc  Number of channels
            t0  Start time
            dt  Sample interval
            dtr Interval between blocks. Used only in special cases
            v   Data points (often voltage)
            
        Companion to load()    
        '''        
        header = "<WFM_Python_>f4>"    # Header gives source and data format
        n_header   = len(header)        
        #y = np.require( self.v, requirements='C' )
        with open(filename, 'xb') as fid:
            fid.write(np.array(n_header).astype('>i4') )
            fid.write(bytes(header, 'utf-8') )
            fid.write(np.array(self.n_ch()).astype('>u4'))
            fid.write(np.array(self.t0).astype('>f8'))
            fid.write(np.array(self.dt).astype('>f8'))
            fid.write(np.array(self.dtr).astype('>f8'))
            fid.write(self.x.astype('>f4')  )
        return 0                  
    
#%%
  
class Pulse:
    '''
    Pulse-class. Used for standardised theoretical ultrasound pulses
    For testing or transfering to a signal generator.
    Defines a standard pulse from 
        envelope  Envelope from built-in window functions
        shape     sine, square, triangle, ...
        f0        Centre frequency
        n_cycles  Length as number of cycles
        phase     Phase in degrees
        a         Amplitude
        dt        Sample interval    
    '''    
    shape = "sine"
    envelope = "rectangular"
    n_cycles= 2.0  #       No. of cycles  
    f0 = 2.0e6     # [Hz]  Centre frequency
    a  = 1.0       #       Amplitude
    phase= 0.0     # [deg] Phase, rel. cosine
    dt = 8e-9      # [s]   Sample interval
    alpha = 0.5    #       Tukey window cosine-fraction
    
    
    def period(self):
        ''' Period of carrier wave [s]'''
        return 1/self.f0
    
    
    def t_end(self):
        ''' Time of last sample [s] '''
        return self.period() * self.n_cycles
    
    
    def t(self):
        ''' Time vector [s] '''
        return np.arange(0, self.t_end(), self.dt)
    
    
    def time_unit(self):        
        if self.f0 > 1e9:
            return "ns"
        if self.f0 > 1e6:
            return "us"
        elif self.f0 > 1e3:
            return "ms"
        else:
            return "s"

    
    def n_samples(self):
        ''' No. of samples in pulse '''
        return(len(self.t()))
    
    
    def n_fft(self):  
        ''' Number of points to calculate spectrum, zeros padded'''
        n_up = 2**(2+(self.n_samples()-1).bit_length())
        return max(n_up, 2048)
    
    
    def x(self):  
        ''' Create pulse from input specification '''
        match(self.envelope[0:3].lower()):
            case "rec":  
                win = windows.boxcar(self.n_samples())
            case "han":  
                win = windows.hann(self.n_samples())
            case "ham":  
                win = windows.hamming(self.n_samples())
            case "tri":  
                win = windows.triang(self.n_samples())
            case "tuk":
                win = windows.tukey( self.n_samples(), self.alpha  )
            case _:
               win = windows.boxcar( self.n_samples() )

        arg = 2*np.pi * self.f0 * self.t() + np.radians(self.phase)
        match(self.shape.lower()[0:3]):
            case "squ":
                y = 1/2*signal.square(arg, duty=0.5)
            case "tri":
                y = 1/2*signal.sawtooth(arg, width=0.5)  
            case "saw":
                y = 1/2*signal.sawtooth(arg, width=1)  
            case _:
                y = np.cos(arg)
          
        return self.a * win * y

    
    def plot(self):
        ''' Plot pulse in time domain '''
            
        plot_pulse (self.t(), self.x(), self.time_unit() )
        return 0    
    

    def powerspectrum(self):
        ''' Calculate power spectrum of trace '''
        f, psd = powerspectrum(self.x(), self.dt, nfft=self.n_fft(), 
                               scale="dB", normalise=True)
        
        return f, psd


    def plot_spectrum(self):   
        ''' Plot trace and power spectrum '''        
        f_max = scale_125(3*self.f0)       
        plot_spectrum ( self.t(), self.x(), time_unit=self.time_unit(), f_max=f_max, 
                       n_fft=self.n_fft(), normalise=True, scale="db")
        
        return 0
    
#%% Utility functions    

def scale_125(x):
    '''
    Find next number in an 1-2-5-10-20 ... sequence, e.g. for scaling axes.
    Input  x  : Number, positive or negative
    Output xn : Next number in 1-2-5-10 sequence greater than magnitude of x 
    '''
    prefixes = np.array([1, 2, 5, 10])
    exp = int(np.floor(np.log10(abs(x))))    
    mant= abs(x) / (10**exp)    
    valid = np.where((prefixes-mant+0.001) > 0) 
    mn = np.min(prefixes[valid])    
    xn = mn*10**exp    
        
    return xn


def find_filename( prefix='us', ext='wfm', resultdir= "..\\results" ):   
    '''
    Automatically set file name
    Finds next free file name on format prefix_yyyy_mm_dd_nnnn.ext where 
    yyyy_mm_dd is the date and nnnn is a counter.
    Saves to directory resultdir. 
    Last counter value is saved in the counter file prefix.cnt.
    Starts looking for next free finelame after value in counter file
    Inputs      prefix    : Characterises measurement type
                ext       : File Extension
                resultdir : Directory for results
                
    Outputs     resultpath : Full path to resultfile
                resultdir  : Full path to result directory
                resultfile : Name of result file (no path)
                n_result   : Number of result file             
    '''
    if not(os.path.isdir(resultdir)):     # Create result directory if needed
        os.mkdir(resultdir)         
    counterfile = os.path.join(os.getcwd(), resultdir, f'{prefix}.cnt')
    
    if os.path.isfile(counterfile):    # Read existing counter file
        with open(counterfile, 'r') as fid:
            n_result = int(fid.read())  
    else:
        n_result = 0              # Set counter to 0 if no counter file exists            
    datecode = datetime.date.today().strftime('%Y_%m_%d')
    ext = ext.split('.')[-1]
    
    resultdir = os.path.abspath(os.path.join(os.getcwd(), resultdir))
    file_exists = True
    while file_exists:   # Find lowest free file number 
        n_result += 1
        resultfile= prefix +'_' + datecode + '_' + f'{n_result:04d}' + '.' + ext
        resultpath= os.path.join(resultdir, resultfile)
        file_exists= os.path.isfile(resultpath)    
    with open(counterfile, 'wt') as fid:    # Write counter to counter file
        fid.write( f'{n_result:d}' ) 
        
    return resultpath, resultdir, resultfile, n_result


def plot_pulse(t, x, time_unit="s"):
    '''
    Plot pulse on standardised graph
    Inputs      t : Time vector
                x : Vector of values to plot
        time_unit : Unit for scaling time axis
        
    Outputs     0     
    '''
    
    match(time_unit):
        case "ns":
            mult= 1e9
        case "us":
            mult= 1e6
        case "ms":
            mult= 1e3
        case _:
            mult= 1
            
    plt.plot(t*mult, x)
    plt.xlabel(f'Time [{time_unit}]')
    plt.ylabel('Ampltude')
    plt.grid(True)
    #plt.show()    
    return 0    


def powerspectrum(x, dt, nfft=None, scale="linear", normalise=False): 
    '''
    Calculate power spectrum of pulse. Finite length signal, no window    
    Inputs     x  : Time trace
              dt : Sample interval
            nfft : No of points in FFT,, zero-padding
           scale : Linear or dB
       normalise : Normalise spectrum to max value 
       
    Outputs    0   
    
    '''
    f, psd= signal.periodogram(x, fs=1/dt, nfft=nfft, detrend=False)

    if normalise:
        psd = psd/psd.max(axis=0)

    if scale.lower() == "db":
        psd = 10*np.log10(psd)

    return f, psd    


def plot_spectrum(t, x, time_unit="s", f_max=None, n_fft=None, 
                  scale="dB", normalise=True):
    '''
    Plot time trace and power spectrum on standardised format
    Requires evenly sampled points
    Inputs    t  : Time vector 
              x  : Time trace
       time_unit : Unit for scaling time and frequency axes
           f_max : Max. frequency to plot
           n_fft : No of points in FFT,, zero-padding
           scale : Linear or dB
       normalise : Normalise spectrum to max value 
       
    Outputs    0   
    '''

    # Plot pulse in time-domain
    plt.subplot(2, 1, 1)    
    plot_pulse(t, x, time_unit)
        
    # Plot power spectrum
    plt.subplot (2, 1, 2)     
    dt = t[1]-t[0]   # Assumes even sampling 

    match(time_unit):
        case "ns":
            freq_unit = "GHz"
            freq_mult = 1e-9
        case "us":
            freq_unit = "MHz"
            freq_mult = 1e-6
        case "ms":
            freq_unit = "kHz"
            freq_mult = 1e-3
        case _:
            freq_unit = "Hz"
            freq_mult = 1
            
    f, psd = powerspectrum (x, dt, nfft=n_fft, normalise=normalise, scale=scale)
    
    plt.plot(f*freq_mult, psd)
    plt.xlabel(f'Frequency [{freq_unit}]')
    plt.grid(True)       
    plt.xlim((0, f_max*freq_mult))
        
    if scale.lower() == "db":
        plt.ylabel('Power [dB re. max]')
        plt.ylim((-40.0 , 0))
    else:
        plt.ylabel('Power')
            
    return 0
            

    
    
            
    
