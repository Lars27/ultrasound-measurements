# -*- coding: utf-8 -*-
"""
Load and interpret ultrasound traces from USN ultrasound lab
Estimate time delay between echoes by autocorrelation
- Missing: Sub-sample interpolation

2 channels saved in internal 'wfm' format
Classes and methods loaded from 'us_utilities' file
Input file and calculation parameters specified in source code in beginning of file

Function
- Load data from specified measurement file. Only first channel is used
- Select an interval to use in calculations
- Estimate delay between echoes from maximum in autocorrelation 

Created on Wed Oct 18 16:03:05 2023

@author: lah
"""

#%% Import libraries
import us_utilities as us
import matplotlib.pyplot as plt 
import numpy as np
from scipy import signal 

#%%
"""
Part to be changed before running
- Name of measurement file to analyse
- Start and stop of interval to search for echoes
"""

resultfile  = 'US_2023_10_20_0051.wfm'   # Name of resultfile

tmin   =  2          # [us] Start of interval to extract 
tmax   = 12          # [us] End of interval to extract
tcstart=  1.5        # [us] Start search for max autocorrelation 
tcmax =   8          # [us] Display length of correlation plot 

autocorrelation_magnitude = False     # Show autocorrelation as magnitude
intervalcolor= 'darkgreen'  # Colour of lines to mark intervals 
markercolor  = 'maroon'     # Colour of lines to mark results etc.

figuresize = (20, 30 )                  # Size of result figure 
plt.rcParams.update({'font.size': 20})  # Default font size in result figure

figformats = ["none", "png", "pdf"]     # Save figure to file
figformat  = figformats[1]

filterorder = 2             # Lowpass noise filter order
fhigh = 10                  # [MHz] Upper cut-off frequency

"""
End of part to be changed by user
"""

#%% Load result
wfm = us.waveform()       # Define wfm class
wfm.load( resultfile )    # Load measurement from source file

#%% Select interval to investigate
b,a = signal.butter( filterorder, fhigh*1e6 , btype='lowpass', fs=wfm.fs() )   # Filter to remove noise
vf  = signal.filtfilt(b, a, wfm.v[:,0] ) # Filter to remove noise

nmin = np.max( np.where( wfm.t() < tmin*1e-6 ) )
nmax = np.min( np.where( wfm.t() > tmax*1e-6 ) )
t = wfm.t()[ nmin:nmax ]       # [us] Time interval to analyse
v = vf[ nmin:nmax ]            # Voltages in interval to analyse

#%% Find time-shift from autocorrelation
ac = np.correlate( v, v,  mode='full' )             # Autocorrelation
ac = ac/ac.max()                                    # Normalise to 1
n0 = int( (ac.size-1)/2 )                           # Center index of autocorrelation,where t=0
tc = np.linspace(-n0*wfm.dt, n0*wfm.dt, ac.size )   # [s] Time axis for autocorrelation [us]

ncmin = np.min( np.where( tc > tcstart*1e-6 ) )     # Start of interval to seach for max correlation
ad    = np.amax( np.abs( ac[ ncmin: ] ) )           # Value of maximum correlation
td    = us.subsample_peak( ac[ncmin:], tc[ncmin:], type='min' ) # [s] Estimated delay, time of maximum negative correlation 

#%% Plot results
fig, axs = plt.subplots( nrows=4, ncols=1, figsize=figuresize ) 

# All traces, full length
kp=0
wfm.plot( axs[0], timeunit='us')                                # Plot entire waveform as received. Use plot method in wfm class
ylim= axs[0].get_ylim()                
axs[kp].plot( tmin * np.ones(2), ylim, color=intervalcolor )    # Mark interval used to find autocorrelation
axs[kp].plot( tmax * np.ones(2), ylim, color=intervalcolor )
axs[kp].set_title( 'Full trace' ,loc='right')
axs[kp].set_title( resultfile )

# Selected interval
kp=1
axs[kp].plot( t*1e6, v )                      # Plot selected interval
axs[kp].set_xlim( t.min()*1e6, t.max()*1e6 )  # Format axes and labels
axs[kp].set_xlabel( 'Time [us]' )
axs[kp].set_ylabel( 'Voltage [V]' )
axs[kp].grid( True )                                         
axs[kp].set_title( 'Zoomed interval' ,loc='right')

# Autocorrelation
kp=2    
ycmax = 1.1*ad
tdref = td*1e6 * np.ones(2)       # Delay as 2 element array for marker lines
cdref = ycmax * np.array([-1,1])
if autocorrelation_magnitude:
    axs[kp].plot( tc*1e6, np.abs( ac ) )       
    axs[kp].set_ylim( 0, ycmax )
else:
    axs[kp].plot( tc*1e6, ac )       # Plot autocorrelation function
    axs[kp].set_ylim( ycmax*np.array([-1, 1 ] ) )
    
axs[kp].set_xlim( 0, tcmax )         # Format axes and labels
axs[kp].plot( tdref, cdref, color= markercolor )     # Line at estimated delay
axs[kp].text( td*1e6, -0.9*ycmax, f'  {td*1e6:.3f} us', color=markercolor )  # Write value of delay
axs[kp].set_xlabel( 'Delay [us]' )
axs[kp].set_ylabel( 'Autocorrelation' )      
axs[kp].grid( True )  
axs[kp].set_title( 'Autocorrelation' ,loc='right')

# Time-shifted plots
kp=3
axs[kp].plot(      t*1e6, v )    # Original signal
axs[kp].plot( (t+td)*1e6, v, color=markercolor )    # Time-shifted signal
axs[kp].set_xlim( 0, t.max()*1e6 )                  # Format axes and labels

nmax=np.argmax(v)
tline = t[nmax]*1e6 + np.array( [ 0, td*1e6 ] )
vline = 0.7*v[nmax]* np.ones(2)
axs[kp].plot( tline, vline, color=markercolor, marker = '|')    # Original signal
axs[kp].text( np.mean(tline), vline[0], f'  {td*1e6:.3f} us', color=markercolor )  # Write value of delay
axs[kp].set_xlim( t.min()*1e6, t.max()*1e6 )  # Format axes and labels

axs[kp].set_xlabel( 'Time [us]' )
axs[kp].set_ylabel( 'Voltage [V]' )
axs[kp].grid( True )                                         
axs[kp].set_title( 'Time-shifted trace', loc='right' )

#%% Save figure to pdf-file
if figformat == 'none':
    print ('Figures not saved to file')
else:
    figfile = resultfile.split('.')[0] + "." + figformat
    fig.savefig(figfile , format=figformat, bbox_inches="tight")
    print ('Figures saved to file ' + figfile )
    

