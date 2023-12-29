# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 21:46:41 2022

@author: larsh
"""

import copy 
import numpy as np
import matplotlib.pyplot as plt
import os
import datetime


#%% Smaller utility-functions 

milli = 1e-3

""" Next number in an 1-2-5-10 ... sequence, e.g. for scaling axes"""
def scale125(x):
    val = np.array([1, 2, 5, 10])
    e   =  int(np.floor(np.log10(abs(x))))    
    m   = abs(x)/(10**e)    
    sa  = np.sign(val-m+0.01)
    pos = val[np.where(sa>0)]
    mn  = np.min(pos)    
    xn = mn*10**e    
        
    return xn

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
""" waveform-class. Used to store traces sampled in time, one or several channels. 
    Compatible with previous versions used in e.g. LabVIEW and Matlab 
    Adapted from LabVIEW's waveform-type, similar to python's mccdaq-library"""

class waveform:    
    def __init__(self, y=np.zeros((1000,1)), dt=1, t0=0):
        self.y  = y          # [V]  Voltage trace
        if y.ndim == 1:      # Ensure v is 2D
            self.y = self.y.reshape((1, len(y)))
        self.dt = dt         # [s]  Sample interval
        self.t0 = t0         # [s]  Time of first sample 
                
    def ns(self):   
        return len( self.y )   # Number of points in trace
    
    def nfft(self):
        return 2**(3+( self.ns()-1 ).bit_length() )
    
    def t(self):             # [s] Time vector from start time and sample interval
        return np.linspace(self.t0, self.t0+self.dt*self.ns(), self.ns() )
        
    def fs(self):          # [Hz]   Sample rate
        return 1/self.dt   
    
    def plot ( self, timeunit="" ):
        if timeunit == "us":
            mult = 1e6
        else:
            mult = 1
            
        plt.plot(self.t()*mult, self.y)
        plt.xlabel(f'Time [{timeunit}]')
        plt.ylabel('Ampltude')
        plt.grid(True)
        #plt.show()
        
    def f ( self ):
        return np.arange( 0, self.nfft()/2 )/self.nfft() * self.fs()
    
    def powerspectrum ( self, normalise=True, scale="linear" ):
        nf   = len(self.f())   
        y_ft = np.fft.fft( self.y, n=nf, axis=0)
        psd  = 1/( self.fs()*nf ) * np.abs( y_ft[ 0:nf, :])**2 
        psd[2:] *=2 
        if normalise:
            psd = psd/psd.max(axis=0)
        if scale.lower() == "db":
            psd = 20*np.log10(psd)
        return psd
    
    def plotspectrum ( self, timeunit="s", frequnit="Hz", fmax=None, normalise=True, scale="dB" ):
        plt.subplot(2,1,1)
        self.plot(timeunit)
        
        plt.subplot(2,1,2)
        if frequnit == "MHz":
            mult = 1e-6
        else:
            mult = 1
        plt.plot(self.f()*mult, self.powerspectrum( normalise, scale ) )
        plt.xlabel(f'Frequency [{frequnit}]')
        plt.grid(True)       
        plt.xlim((0 , fmax))
        if scale.lower() == "db":
            plt.ylabel('Power [dB re. max]')
            plt.ylim((-40.0 , 0))
        else:
            plt.ylabel('Power')
            
            
    def load ( self, filename ):   # Load wavefrom-file. Compatible with older file format used in e.g. LabVIEW
        with open(filename, 'rb') as fid:
            n_hd= int( np.fromfile(fid, dtype='>i4', count=1) )
            hd  = fid.read(n_hd)
            header= hd.decode("utf-8")
            nc  = int( np.fromfile(fid, dtype='>u4', count= 1) )
            t0  = float( np.fromfile(fid, dtype='>f8', count= 1) )
            dt  = float( np.fromfile(fid, dtype='>f8', count= 1) )
            dtr = float( np.fromfile(fid, dtype='>f8', count= 1) )
            
            y   = np.fromfile(fid, dtype='>f4', count=-1)
            
            self.sourcefile = filename
            self.header = header
            self.t0 = t0
            self.dt = dt
            self.dtr= dtr     # Normally not used, included for backward compatibility
            self.y  = np.reshape(y, (-1, nc))  
            
    def zoom (self, tlim ):
        wfm  = copy.deepcopy(self)
        nlim = np.flatnonzero ( ( self.t() >= min(tlim) ) & ( self.t() <= max(tlim) ) )
        
        t0   = self.t()[np.min(nlim)]
        y    = self.y[nlim]
        
        wfm.t0 = t0
        wfm.y  = y
        
        return wfm
            
                
        
            