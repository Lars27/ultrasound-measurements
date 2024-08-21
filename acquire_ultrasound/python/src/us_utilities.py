"""Utility functions for ultrasound measurement systems at USN IMS.

Based on former systems in LabVIEW and Matlab

coding: utf-8 -*-
@author: larsh
Created on Tue Sep 13 21:46:41 2022
"""

import copy
from math import pi, radians, cos, log10, floor, frexp
import numpy as np
from scipy import signal
from scipy.signal import windows
import matplotlib.pyplot as plt
import os
import datetime


# %% Classes

class Waveform:
    """Measurement results as 1D time-traces.

    Used to store traces sampled in time, one or several channels.
    Compatible with previous versions used in e.g. LabVIEW and Matlab
    Adapted from LabVIEW's waveform-type, similar to python's mccdaq-library
    The fundametal parts are
        t0  Scalar      Start time
        dt  Scalar      Sample interval
        y   2D array    Results. Each column is a channel, samples as rows

    Other parameters are methods calculated from these: time vector,
    no. of channels, no. of points, sample rate, etc.

    Other methods
    plot()              Plots the traces at standardised format
    powerspectrum()     Returns frequency and power spectral density
    load() and save()   Load from and save to binary format, backwards
                        compatible to formats used with e.g. LabVIEW and Matlab
    """

    def __init__(self, y=np.zeros((100, 1)), dt=1, t0=0):
        self.y = y              # Voltage traces as 2D numpy array
        if y.ndim == 1:         # Ensure v is 2D
            self.y = self.y.reshape((1, len(y)))
        self.dt = dt             # [s]  Sample interval
        self.t0 = t0             # [s]  Time of first sample
        self.dtr = 0             # [s]  Interval between blocks. Obsolete

    def n_channels(self):
        """Return number of data channels in trace."""
        return self.y.shape[1]

    def n_samples(self):
        """Return number of points in trace."""
        return self.y.shape[0]

    def n_fft(self, upsample=2):
        """Return number of points used to calculate spectrum.

        Always a power of 2, zeros are padded if needed.
        upsample : Extra powers of 2 added
        """
        m, e = frexp(self.n_samples())
        n = 2**(e+upsample)
        # n = 2**(self.n_samples().bit_length() +upsample)  # Next power of 2
        return max(n, 2048)

    def t(self):
        """Return time vector [s].

        Calculated from start time and sample interval [s]
        """
        return np.linspace(self.t0,
                           self.t0+self.dt*self.n_samples(),
                           self.n_samples())

    def f(self):
        """Return frequency vector [Hz]."""
        return np.arange(0, self.n_fft()/2)/self.n_fft() * self.fs()

    def fs(self):
        """Return sample rate [Hz]."""
        return 1/self.dt

    def filtered(self, filter):
        """Return bandpass filtered trace."""
        wfm = copy.deepcopy(self)
        match(filter.type[0:2].lower()):
            case "no":
                y = self.y
            case "ac":
                dc_level = self.y.mean(axis=0)
                y = self.y - dc_level
            case _:
                b, a = filter.coefficients()
                y = signal.filtfilt(b, a, self.y, axis=0)
        wfm.y = y
        return wfm

    def zoomed(self, tlim):
        """Extract copy of trace from interval in specified by tlim."""
        wfm = copy.deepcopy(self)
        nlim = np.flatnonzero((self.t() >= min(tlim))
                              & (self.t() <= max(tlim)))

        t0 = self.t()[np.min(nlim)]
        y = self.y[nlim]
        wfm.t0 = t0
        wfm.y = y
        return wfm

    def plot(self, time_unit="us", filtered=True):
        """Plot time traces using unit time_unit."""
        plot_pulse(self.t(), self.y(), self.time_unit())
        return 0

    def powerspectrum(self, normalise=False, scale="linear", upsample=2):
        """Calculate power spectrum of time trace.

        normalise : Normalise to 1 (0 dB) as maximum
        scale : linear (W)  or dB
        upsample: Interpolate spectrum by padding zeros to next power of 2
        """
        f, psd = powerspectrum(self.y,
                               self.dt,
                               nfft=self.n_fft(upsample=2),
                               scale=scale,
                               normalise=normalise)
        return f, psd

    def plot_spectrum(self, time_unit="s", f_max=None,
                      normalise=True, scale="dB"):
        """Plot trace and power spectrum in one graph.

        time_unit :  Unit in time trace plot
        f_max : Maximum frequency to plot
        normalise : Normalise powwer spectrum plot 1 (0 dB)
        scale : Linear (Watt) or dB
        """
        plot_spectrum(self.t(), self.y, time_unit=time_unit, f_max=f_max,
                      nfft=self.n_fft(), normalise=normalise, scale=scale)
        return 0

    def load(self, filename):
        """Load 'Waveform' files in binary format as 4-byte (sgl) floats.

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
        """
        with open(filename, 'rb') as fid:
            n_header = int(np.fromfile(fid, dtype='>i4', count=1))
            header_bytes = fid.read(n_header)
            header = header_bytes.decode("utf-8")
            n_ch = int(np.fromfile(fid, dtype='>u4', count=1))
            t0 = float(np.fromfile(fid, dtype='>f8', count=1))
            dt = float(np.fromfile(fid, dtype='>f8', count=1))
            dtr = float(np.fromfile(fid, dtype='>f8', count=1))
            x = np.fromfile(fid, dtype='>f4', count=-1)   # Traces, 2D array

            self.sourcefile = filename
            self.header = header
            self.t0 = t0
            self.dt = dt
            self.dtr = dtr     # Rarely used, for backward compatibility
            self.y = np.reshape(x, (-1, n_ch))
        return 0

    def save(self, filename):
        """Save 'Waveform' files in binary format as 4-byte (sgl) floats.

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
        """
        header = "<WFM_Python_>f4>"    # Header gives source and data format
        n_header = len(header)
        # y = np.require( self.v, requirements='C' )
        with open(filename, 'xb') as fid:
            fid.write(np.array(n_header).astype('>i4'))
            fid.write(bytes(header, 'utf-8'))
            fid.write(np.array(self.n_channels()).astype('>u4'))
            fid.write(np.array(self.t0).astype('>f8'))
            fid.write(np.array(self.dt).astype('>f8'))
            fid.write(np.array(self.dtr).astype('>f8'))
            fid.write(self.y.astype('>f4'))
        return 0


# %% Generated signals

class Pulse:
    """Create standardised theoretical ultrasound pulses.

    For testing or transfering to a signal generator.
    Defines a standard pulse from
        envelope  Envelope from built-in window functions
        shape     sine, square, triangle, ...
        f0        Centre frequency
        n_cycles  Length as number of cycles
        phase     Phase in degrees
        a         Amplitude
        dt        Sample interval
    """

    shape = "sine"
    envelope = "rectangular"
    n_cycles = 2.0      # No. of cycles
    f0 = 2.0e6          # [Hz]  Centre frequency
    a = 1.0             # [V]   Amplitude
    phase = 0.0         # [deg] Phase, rel. cosine
    dt = 8e-9           # [s]   Sample interval
    alpha = 0.5         # Tukey window cosine-fraction
    trigger_source = 1  # Use osciloscope trigger, always
    on = False

    def period(self):
        """Return period of carrier wave [s]."""
        return 1/self.f0

    def duration(self):
        """Returnd duration of pulse [s]."""
        return self.period()*self.n_cycles

    def t(self):
        """Return time vector [s]."""
        return np.arange(0, self.duration(), self.dt)

    def time_unit(self):
        """Return unit for time trace plot, based on cantre frequency."""
        if self.f0 > 1e9:
            return "ns"
        if self.f0 > 1e6:
            return "us"
        elif self.f0 > 1e3:
            return "ms"
        else:
            return "s"

    def n_samples(self):
        """Return number of samples in pulse."""
        return len(self.t())

    def n_fft(self):
        """Find number of points to calculate spectrum.

        Always as power of 2, zeros padded at end
        """
        m, e = frexp(self.n_samples())
        n = 2**(e+3)
        # n = 2**(3+(self.n_samples()-1).bit_length())
        return max(n, 2048)

    def y(self):
        """Create pulse from input specification."""
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
                win = windows.tukey(self.n_samples(), self.alpha)
            case _:
                win = windows.boxcar(self.n_samples())
        arg = 2*pi*self.f0 * self.t() + radians(self.phase)
        match(self.shape.lower()[0:3]):
            case "squ":
                s = 1/2*signal.square(arg, duty=0.5)
            case "tri":
                s = 1/2*signal.sawtooth(arg, width=0.5)
            case "saw":
                s = 1/2*signal.sawtooth(arg, width=1)
            case _:
                s = cos(arg)
        y = self.a*win*s
        y[-1] = 0         # Avoid DC-level after pulse is over
        return y

    def plot(self):
        """Plot pulse in time domain."""
        plot_pulse(self.t(), self.y(), self.time_unit())
        return 0

    def powerspectrum(self):
        """Calculate power spectrum of trace."""
        f, psd = powerspectrum(self.y(), self.dt, nfft=self.n_fft(),
                               scale="dB", normalise=True)
        return f, psd

    def plot_spectrum(self):
        """Plot trace and power spectrum."""
        f_max = scale_125(3*self.f0)
        plot_spectrum(self.t(),
                      self.y(),
                      time_unit=self.time_unit(),
                      f_max=f_max,
                      n_fft=self.n_fft(),
                      normalise=True, scale="db")
        return 0


# %% Utility classes

class WaveformFilter:
    """Parameteres of digital filter for "Waveform" class."""

    type = "No filter"        # Filter type: None, AC removal, bandpass, ...
    f_min = 100e3             # [Hz] Lower cutoff frequency
    f_max = 10e6              # [Hz] Upper cutoff frequency
    order = 2                 # Filter order
    sample_rate = 100e6       # Sample rate

    def wc(self):      # Cutoff normalised to Nyquist-frequency
        """Return normalised cutoff-frequencies."""
        return np.array([self.f_min, self.f_max])/(self.sample_rate/2)

    def coefficients(self):
        """Return filter coefficients (b,a) from filter description."""
        b, a = signal.butter(self.order,
                             self.wc(),
                             btype='bandpass',
                             output='ba')
        return b, a


# %% Utility functions

def scale_125(x):
    """Find next number in an 1-2-5-10-20 ... sequence.

    Input  x  : Number, positive or negative
    Output xn : Next number in 1-2-5-10 sequence greater than magnitude of x
    """
    prefixes = np.array([1, 2, 5, 10])
    exponent = int(floor(log10(abs(x))))
    mant = abs(x) / (10**exponent)
    valid = np.where(prefixes >= mant-0.001)
    mn = np.min(prefixes[valid])
    xn = mn*10**exponent
    return xn


def find_timescale(time_unit="s"):
    """Return time and frequency axis scaling based on time unit."""
    match(time_unit):
        case "ns":
            multiplier = 1e9
            freq_unit = "GHz"
        case "us":
            multiplier = 1e6
            freq_unit = "MHz"
        case "ms":
            multiplier = 1e3
            freq_unit = "kHz"
        case _:
            multiplier = 1
            freq_unit = "Hz"
    return multiplier, freq_unit


def find_limits(limits, min_diff=1):
    """Return minimum and maximum values as numpy array."""
    min_value = min(limits)
    max_value = max(max(limits), min_value+min_diff)
    return np.array([min_value, max_value])


def read_scaled_value(prefix):
    """Interpret a text as a scaled value (milli, kilo, Mega etc.)."""
    prefix = prefix.split(' ')
    if len(prefix) == 1:
        multiplier = 1
    else:
        if prefix[1] == 'u':
            multiplier = 1e-6
        if prefix[1] == 'm':
            multiplier = 1e-3
        elif prefix[1] == 'k':
            multiplier = 1e3
        elif prefix[1] == 'M':
            multiplier = 1e6
        elif prefix[1] == 'G':
            multiplier = 1e9
        else:
            multiplier = 1
    value = float(prefix[0]) * multiplier
    return value


def find_filename(prefix='us', ext='wfm', resultdir="..\\results"):
    """Find new file name from date and counter.

    Finds next free file name on format prefix_yyyy_mm_dd_nnnn.ext where
    yyyy_mm_dd is the date and nnnn is a counter.
    Saves to directory resultdir.
    Last counter value is saved in the counter file prefix.cnt.
    Starts looking for next free finelame after value in counter file
    Inputs      prefix    : Characterises measurement type
                ext       : File Extension
                resultdir : Directory for results

    Outputs     resultpath    : Full path to resultfile
                resultdir     : Full path to result directory
                resultfile    : Name of result file (no path)
                result_counter: Number of result file
    """
    if not (os.path.isdir(resultdir)):     # Create result directory if needed
        os.mkdir(resultdir)

    counterfile = os.path.join(os.getcwd(), resultdir, f'{prefix}.cnt')
    if os.path.isfile(counterfile):    # Read existing counter file
        with open(counterfile, 'r') as fid:
            result_counter = int(fid.read())
    else:
        result_counter = 0   # Set counter to 0 if no counter file exists

    datecode = datetime.date.today().strftime('%Y_%m_%d')
    ext = ext.split('.')[-1]
    resultdir = os.path.abspath(os.path.join(os.getcwd(), resultdir))
    file_exists = True
    while file_exists:   # Find lowest free file number
        result_counter += 1
        resultfile = (prefix + '_' + datecode + '_'
                      + f'{result_counter:04d}' + '.' + ext)
        resultpath = os.path.join(resultdir, resultfile)
        file_exists = os.path.isfile(resultpath)
    with open(counterfile, 'wt') as fid:    # Write counter to counter file
        fid.write(f'{result_counter:d}')
    return resultpath, resultdir, resultfile, result_counter


def plot_pulse(t, x, time_unit="us"):
    """Plot pulse in standardised graph.

    Inputs      t : Time vector
                x : Vector of values to plot
        time_unit : Unit for scaling time axis

    Outputs     0
    """
    multiplier, freq_unit = find_timescale(time_unit)
    plt.plot(t*multiplier, x)
    plt.xlabel(f'Time [{time_unit}]')
    plt.ylabel('Ampltude')
    plt.grid(True)
    return 0


def powerspectrum(y, dt, nfft=None,
                  scale="linear", normalise=False, transpose=True):
    """Calculate power spectrum of pulse. Finite length signal, no window.

    Inputs     x  : Time trace
              dt : Sample interval
            nfft : No of points in FFT, zero-padding
           scale : Linear or dB
       normalise : Normalise spectrum to max value

    Outputs
               f : Frequency vector
             psd : Power spectral density

    Datapoints in rows (dimension 0),columns (dimension 1) are channels
    The periodogram function calculates FT along dimension 1.
    """
    y = y.transpose()
    f, psd = signal.periodogram(y, fs=1/dt, nfft=nfft, detrend=False)
    psd = psd.transpose()

    if normalise:
        if psd.ndim == 1:
            psd = psd/psd.max()
        else:
            n_ch = psd.shape[1]
            for k in range(n_ch):
                psd[:, k] = psd[:, k]/psd[:, k].max()
    if scale.lower() == "db":
        psd = 10*log10(psd)
    return f, psd


def plot_spectrum(t, x, time_unit="s", f_max=None, n_fft=None,
                  scale="dB", normalise=True):
    """Plot time trace and power spectrum on standardised format.

    Requires evenly sampled points
    Inputs    t  : Time vector
              x  : Time trace
       time_unit : Unit for scaling time and frequency axes
           f_max : Max. frequency to plot
           n_fft : No of points in FFT,, zero-padding
           scale : Linear or dB
       normalise : Normalise spectrum to max value

    Outputs    0
    """
    # Pulse in time-domain
    plt.subplot(2, 1, 1)
    plot_pulse(t, x, time_unit)

    # Power spectrum
    plt.subplot(2, 1, 2)
    dt = t[1] - t[0]   # Assumes even sampling
    multiplier, freq_unit = find_timescale(time_unit)
    f, psd = powerspectrum(x, dt, nfft=n_fft, normalise=normalise, scale=scale)
    plt.plot(f/multiplier, psd)
    plt.xlabel(f'Frequency [{freq_unit}]')
    plt.grid(True)
    plt.xlim((0, f_max/multiplier))
    if scale.lower() == "db":
        plt.ylabel('Power [dB re. max]')
        plt.ylim((-40.0, 0))
    else:
        plt.ylabel('Power')
    return 0
