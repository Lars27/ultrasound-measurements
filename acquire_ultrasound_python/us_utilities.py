# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 21:46:41 2022

@author: larsh
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import datetime

#%% Smaller utility-functions 

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

def find_filename( prefix='US', ext='wfm', resultdir=[] ):
    counterfile= f'{prefix}.cnt'
    if os.path.isfile(counterfile):
        with open(counterfile, 'r') as fid:
            n= int( fid.read( ) )
    else:
        n=0
            
    datecode   = datetime.date.today().strftime('%Y_%m_%d')
    ext        = ext.split('.')[-1]
    file_exists= True
    while file_exists:
        n+=1
        resultfile = prefix + '_' + datecode + '_' + f'{n:04d}' + '.' + ext
        file_exists= os.path.isfile(resultfile)
    
    with open(counterfile, 'wt') as fid:
        fid.write( f'{n:d}' ) 
        
    return resultfile   

#%%
""" waveform-class. Used to store traces sampled in time, one or several channels. 
    Compatible with previous versions used in e.g. LabVIEW and Matlab 
    Adapted from LabVIEW's waveform-type, similar to python's mccdaq-library"""

class waveform    :
    def __init__(self, v=np.zeros((1000,1)), dt=1, t0=0):
        self.v  = v
        if v.ndim == 1:    # Ensure v is 2D
            self.v = self.v.reshape((1, len(v)))
        self.dt   = dt
        self.t0   = t0    
                
    def ns(self):
        return len(self.v)
    
    def t(self):
        return np.linspace(self.t0, self.t0+self.dt*self.ns(), self.ns() )
    
    def plot(self, timeunit=""):
        if timeunit == "us":
            mult = 1e6
        else:
            mult = 1            
        plt.plot(self.t()*mult, self.v)
        plt.xlabel(f'Time [{timeunit}]')
        plt.ylabel('Ampltude')
        plt.grid(True)
        #plt.show()
        
    def fs(self):
        return 1/self.dt

    def powerspectrum(self, normalise=True, scale="linear", padding=0 ):
        if padding > 0:
            nfft= int( np.exp2( np.ceil( np.log2(self.ns()) ) +padding-1 ) ) 
        else:
            nfft= self.ns()
            
        f   = np.arange( 0, nfft/2 )/nfft * self.fs()
        fv  = np.fft.fft(self.v, n=nfft, axis=0)
        p   = np.abs( fv[0:f.size, :] )
        if normalise:
            p = p/p.max(axis=0)
        if scale.lower() == "db":
            p = 20*np.log10(p)
            
        self.f   = f            
        self.nfft= nfft            
        return p
    
    
    def plotspectrum(self, timeunit="s", frequnit="Hz", fmax=None, normalise=True, scale="dB", padding=0 ):
        plt.subplot(2,1,1)
        self.plot(timeunit)
        
        plt.subplot(2,1,2)
        if frequnit == "MHz":
            mult = 1e-6
        else:
            mult = 1
            
        ps= self.powerspectrum( normalise, scale, padding )
        plt.plot(self.f*mult, ps )
        plt.xlabel(f'Frequency [{frequnit}]')
        plt.grid(True)       
        plt.xlim((0 , fmax))
        if scale.lower() == "db":
            plt.ylabel('Power [dB re. max]')
            plt.ylim((-40.0 , 0))
        else:
            plt.ylabel('Power')
            
            
    def load(self, filename):   # Load wavefrom-file. Compatible with older file format used in e.g. LabVIEW
        with open(filename, 'rb') as fid:
            n_hd= int( np.fromfile(fid, dtype='>i4', count=1) )
            hd  = fid.read(n_hd)
            header= hd.decode("utf-8")
            nc  = int( np.fromfile(fid, dtype='>u4', count= 1) )
            t0  = float( np.fromfile(fid, dtype='>f8', count= 1) )
            dt  = float( np.fromfile(fid, dtype='>f8', count= 1) )
            dtr = float( np.fromfile(fid, dtype='>f8', count= 1) )
            
            v   = np.fromfile(fid, dtype='>f4', count=-1)
            
            self.sourcefile = filename
            self.header = header
            self.nc = nc
            self.t0 = t0
            self.dt = dt
            self.dtr= dtr     # Normally not used, included for backward compatibility
            self.v  = np.reshape(v, (-1, nc))                        
            

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
            
                
        
            