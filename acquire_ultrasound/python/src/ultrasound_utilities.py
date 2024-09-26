"""Utility functions for ultrasound measurement systems at USN IMS.

Based on former systems in LabVIEW and Matlab

coding: utf-8 -*-
@author: larsh
Created on Tue Sep 13 21:46:41 2022
"""

import copy
# from math import pi, radians, cos, log10, floor, frexp
from math import pi, radians, log10, floor, frexp
import numpy as np
from scipy import signal
from scipy.signal import windows
import matplotlib.pyplot as plt
import os
import datetime


# %% Classes

class Waveform:
    """Measurement results as 1D time-traces.

    Used to store traces sampled in time.
    Compatible with previous versions used in e.g. LabVIEW and Matlab
    Adapted from LabVIEW's waveform-type, similar to python's mccdaq-library

    Attributes
    ----------
    t0  double    Start time
    dt  double    Sample interval
    dtr  double   Interval between sample blocks. Rarely used
    y   2D array  Results. Each column is a channel, samples as rows

    Methods
    -------
    n_channels  int         Number of data channels
    n_samples   int         Number of samples per channel
    t           1D array    Time vector
    fs          float       Sample rate
    n_fft       int         Number of points used to calculate spectrum
    f           1D array    Frequency vector
    powerspectrum 1D array  Powerspecrum of traces
    filtered    Waveform    Bandpass filtered traces, all else equal
    zoomed      Waveform    Zoomed to specified interval, all else identtical
    plot                    Plots result in figure
    plot_spectrum           Plots traces and spectrum
    save                    Loads Waveform from binary file
    load                    Saves Waveform to binary file
    """

    def __init__(self, y=np.zeros((100, 1)), dt=1, t0=0):
        """Initialise to ensure correct shapes."""
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

    def t(self):
        """Return time vector [s].

        Calculated from start time and sample interval [s]
        """
        return np.linspace(self.t0,
                           self.t0+self.dt*self.n_samples(),
                           self.n_samples())

    def fs(self):
        """Return sample rate [Hz]."""
        return 1/self.dt

    def n_fft(self, upsample=2):
        """Return number of points used to calculate spectrum.

        Always a power of 2, zeros padded if needed.
        upsample : Number of extra powers of 2 to add
        """
        upsample = max(round(upsample), 0)
        m, e = frexp(self.n_samples())
        n = 2**(e+upsample)
        # n = 2**(self.n_samples().bit_length() +upsample)  # Next power of 2
        return max(n, 2048)

    def f(self):
        """Return frequency vector [Hz]."""
        return np.arange(0, self.n_fft()/2)/self.n_fft() * self.fs()

    def powerspectrum(self, normalise=False, scale="linear", upsample=2):
        """Calculate power spectrum of time trace.

        Arguments
        ---------
        normalise Boolean   Normalise to 1 (0 dB) as maximum
        scale     String    Linear (Power)  or dB
        upsample  Int       Interpolate spectrum by padding to next power of 2
        """
        f, psd = powerspectrum(self.y,
                               self.dt,
                               n_fft=self.n_fft(upsample=2),
                               scale=scale,
                               normalise=normalise)
        return f, psd

    def filtered(self, filter):
        """Return bandpass filtered trace.

        Arguments
        ---------
        filter  WaveformFilter  Filter specification
        """
        wfm = copy.deepcopy(self)
        match(filter.type[0:2].lower()):
            case "no":
                wfm.y = self.y
            case "ac":
                dc_level = self.y.mean(axis=0)
                wfm.y = self.y - dc_level
            case _:
                b, a = filter.coefficients()
                wfm.y = signal.filtfilt(b, a, self.y, axis=0)
        return wfm

    def zoomed(self, tlim):
        """Extract copy of trace from interval in specified by tlim.

        Arguments
        ---------
        tlim = [tmin tmax]  Start and en of interval to select
        """
        wfm = copy.deepcopy(self)
        nlim = np.flatnonzero((self.t() >= min(tlim))
                              & (self.t() <= max(tlim)))

        wfm.t0 = self.t()[np.min(nlim)]
        wfm.y = self.y[nlim]
        return wfm

    def plot(self, time_unit="us", ch=[0, 1], y_max=None):
        """Plot time traces using unit time_unit.

        Arguments
        ---------
        time_unit   String      Unit to plot tim in, 's', 'ms', 'us'
        ch          List on int Channels to plot
        y_max       Float       Max. scale on amplitude-axis
        """
        plot_pulse(self.t(), self.y[ch], time_unit, y_max)

        return 0

    def plot_spectrum(self, time_unit="s", ch=[0, 1], y_max=None, f_max=None,
                      normalise=True, scale="dB", db_min=-40, ):
        """Plot trace and power spectrum in one graph.

        Arguments
        ---------
        time_unit   String      Unit to plot tim in, 's', 'ms', 'us'
        ch          List of int Channels to plot
        y_max       Float       Max. scale on amplitude-axis
        f_max       Float       Max. scale on frequency axis
        normalise   Boolean     Normalise power spectrum plot  to 1 (0 dB)
        scale       String      Linear (Power) or dB
        db_min      Float       Dynamic range on dB-plot
        """
        plot_spectrum(self.t(), self.y[:, ch], time_unit=time_unit,
                      y_max=y_max, f_max=f_max, n_fft=self.n_fft(),
                      normalise=normalise, scale=scale, db_min=db_min)
        return 0

    def save(self, filename):
        """Save 'Waveform' variable to binary file, as 4-byte (sgl) floats.

        Compatible with internal format used since 1990s on a variety of
        platforms (LabWindows, C, LabVIEW, Matlab)
        Uses 'c-order' of arrays and IEEE big-endian byte order
        Complements save()

        Arguments
        ---------
        filename    String  Full path of file to save data in

        Contents of file
        ----------------
        hd  String  Header, informative text
        nc  Int     Number of channels
        t0  Float   Start time
        dt  Float   Sample interval
        dtr Float   Interval between blocks. Used only in special cases
        v   2D array of sgl     Data points (often voltage)
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

    def load(self, filename):
        """Load 'Waveform' files from binary file, as 4-byte (sgl) floats.

        Compatible with internal format used since 1990s on a variety of
        platforms (LabWindows, C, LabVIEW, Matlab)
        Uses 'c-order' of arrays and IEEE big-endian byte order
        Complements save()

        Arguments
        ---------
        filename    String  Full path of file lo load
        """
        with open(filename, 'rb') as fid:
            n_header = int(np.fromfile(fid, dtype='>i4', count=1))
            header_bytes = fid.read(n_header)
            self.header = header_bytes.decode("utf-8")

            n_ch = int(np.fromfile(fid, dtype='>u4', count=1))
            self.t0 = float(np.fromfile(fid, dtype='>f8', count=1))
            self.dt = float(np.fromfile(fid, dtype='>f8', count=1))
            self.dtr = float(np.fromfile(fid, dtype='>f8', count=1))
            y = np.fromfile(fid, dtype='>f4', count=-1)   # Traces, 2D array
            self.y = np.reshape(y, (-1, n_ch))

            self.sourcefile = filename
        return 0


# %% Generated signals

class Pulse:
    """Create standardised theoretical ultrasound pulses.

    For simulations or transfer to a signal generator.
    Defines a standard pulse from given attributes

    Attributes
    ----------
    envelope    String    Pulse envelope: rect, hann, tukey, ...
    shape       String    Carrier wave: sine, square, triangle, ...
    f0          Float     Carrier wave frequency
    n_cycles    Float     Pulse length as number of cycles
    phase       Float     Phase of carrier wave in degrees, ref. cosine
    a           Float     Amplitude
    dt          Float     Sample interval
    alpha       Float     Tukey window cosine-fraction, alpha = 0 ... 1

    Methods
    -------
    t           1D array    Time vector
    y           1D array    Pulse time trace
    period      Float       Carrier wave period
    duration    Float       Pulse duration, seconds
    n_samples   Int         Number of samples in pulse
    n_fft       int         Number of points used to calculate spectrum
    powerspectrum 1D array  Powerspectrum of pulse
    time_unit   String      Appropriate unit for time-trace plot, from f0
    plot                    Plots result in figure
    plot_spectrum           Plots traces and spectrum
    """

    shape = "sine"
    envelope = "rectangular"
    n_cycles = 2.0
    f0 = 2.0e6
    a = 1.0
    phase = 0.0
    dt = 8e-9
    alpha = 0.5
    trigger_source = 1
    on = False

    def t(self):
        """Return time vector [s]."""
        return np.arange(0, self.duration(), self.dt)

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
                s = np.cos(arg)
        y = self.a*win*s
        y[-1] = 0         # Avoid DC-level after pulse is over
        return y

    def period(self):
        """Return period of carrier wave [s]."""
        return 1/self.f0

    def duration(self):
        """Return duration of pulse [s]."""
        return self.period()*self.n_cycles

    def n_samples(self):
        """Return number of samples in pulse."""
        return len(self.t())

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

    def n_fft(self):
        """Find number of points to calculate spectrum.

        Always as power of 2, zeros padded at end
        """
        m, e = frexp(self.n_samples())
        n = 2**(e+3)
        # n = 2**(3+(self.n_samples()-1).bit_length())
        return max(n, 2048)

    def powerspectrum(self):
        """Calculate power spectrum of trace.

        Return
        ------
        f   1D array    Frequency vector
        psd 1D array    Power spectral density
        """
        f, psd = powerspectrum(self.y(), self.dt, n_fft=self.n_fft(),
                               scale="dB", normalise=True)
        return f, psd

    def plot(self):
        """Plot pulse in time domain."""
        plot_pulse(self.t(), self.y(), self.time_unit())
        return 0

    def plot_spectrum(self):
        """Plot trace and power spectrum."""
        f_max = scale_125(3*self.f0)
        plot_spectrum(self.t(), self.y(), time_unit=self.time_unit(),
                      f_max=f_max, n_fft=self.n_fft(),
                      normalise=True, scale="db")
        return 0


# %% Utility classes

class WaveformFilter:
    """Definition of digital filter for "Waveform" class.

    Attributes
    ----------
    type    String  Type filter: "None", "AC", "BPF" (Bandpass)
    f_min   Float   Lower cutoff frequency
    f_max   Float   Upper cutoff frequency
    order   Int     Filter order
    fs      Float   Sample rate

    Methods
    -------
    wc      List    Cutoff-frequencies normalised to sample rate
    coefficients    Filter coefficients, b and a
    """

    type = "No"          # Filter type: 'NO, 'AC', 'BPF'
    f_min = 100e3        # [Hz] Lower cutoff frequency
    f_max = 10e6         # [Hz] Upper cutoff frequency
    order = 2            # Filter order
    fs = 100e6  # Sample rate

    def wc(self):      # Cutoff normalised to Nyquist-frequency
        """Return normalised cutoff-frequencies."""
        return np.array([self.f_min, self.f_max])/(self.fs/2)

    def coefficients(self):
        """Return filter coefficients from filter description, (b,a)-form."""
        b, a = signal.butter(self.order,
                             self.wc(),
                             btype='bandpass',
                             output='ba')
        return b, a


class ResultFile:
    """Path, name and counter for resultfile."""

    prefix = 'test'
    ext = 'trc'
    path = ''
    directory = ''
    name = ''
    counter = 0


# %% Utility functions

def scale_125(x):
    """Find next number in an 1-2-5-10-20 ... sequence.

    Argumments
    ----------
    x   Float   Reference value, positive or negative

    Outputs
    -------
    xn Float    Next number in 1-2-5-10 sequence greater than magnitude of x
    """
    prefixes = np.array([1, 2, 5, 10])
    exponent = int(floor(log10(abs(x))))
    mant = abs(x) / (10**exponent)
    valid = np.where(prefixes >= mant-0.001)
    mn = np.min(prefixes[valid])
    xn = mn*10**exponent
    return xn


def find_timescale(time_unit="s"):
    """Return time and frequency axis scaling based on time unit.

    Arguments
    ---------
    time_unit   String  Time unit used in plots: "s", "ms", "us", "ns"

    Outputs
    -------
    multiplier  Float   Multiplier for time to get requested unit
    freq_unit   String  Corresponting Frequency unit
    """
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


def read_scaled_value(quantity):
    """Interpret a text as a scaled value (milli, kilo, Mega etc.).

    Arguments
    ---------
    quantity    String  Value as "number unit", e.g. "3.4 MHz"

    Outputs
    -------
    value      Value scaled with unit, e.g. 3 400 000 or 3.4e6
    """
    quantity = quantity.split(' ')   # Split in number and unit at space
    if len(quantity) == 1:
        multiplier = 1
    else:
        number = float(quantity[0])
        prefix = quantity[1][0]    # First letter of unit gives scale
        if prefix == 'u':
            multiplier = 1e-6
        elif prefix == 'm':
            multiplier = 1e-3
        elif prefix == 'k':
            multiplier = 1e3
        elif prefix == 'M':
            multiplier = 1e6
        elif prefix == 'G':
            multiplier = 1e9
        else:
            multiplier = 1
    value = number * multiplier
    return value


def find_filename(prefix='test', ext='trc', resultdir="..\\results"):
    """Find new file name from date and counter.

    Finds next free file name on format prefix_yyyy_mm_dd_nnnn.ext where
    yyyy_mm_dd is the date and nnnn is a counter.
    Saves to directory resultdir.
    Last counter value is saved in the counter file prefix.cnt.
    Starts looking for next free finelame after value in counter file
    Defining this methods in the RsultFile-class was too complicated due to
    the cross-checking and creation of new directory

    Arguments
    ---------
    prefix      String  Code that characterises measurement type
    ext         String  File Extension
    resultdir   String  Directory for results

    Outputs
    -------
    resultfile  ResultFile()    Result-fil name, path, counter, etc.
    """
    resultfile = ResultFile()

    prefix = prefix.lower()
    ext = ext.lower()

    if not (os.path.isdir(resultdir)):     # Create result directory if needed
        os.mkdir(resultdir)

    counterfile = os.path.join(os.getcwd(), resultdir, f'{prefix}.cnt')
    if os.path.isfile(counterfile):    # Read existing counter file
        with open(counterfile, 'r') as fid:
            counter = int(fid.read())
    else:
        counter = 0   # Set counter to 0 if no counter file exists

    datecode = datetime.date.today().strftime('%Y_%m_%d')
    ext = ext.split('.')[-1]
    resultdir = os.path.abspath(os.path.join(os.getcwd(), resultdir))
    file_exists = True
    while file_exists:   # Find lowest free file number
        counter += 1
        filename = (prefix + '_' + datecode + '_'
                    + f'{counter:04d}' + '.' + ext)
        resultpath = os.path.join(resultdir, filename)
        file_exists = os.path.isfile(resultpath)
    with open(counterfile, 'wt') as fid:    # Write counter to counter file
        fid.write(f'{counter:d}')

    resultfile.prefix = prefix
    resultfile.counter = counter
    resultfile.ext = ext
    resultfile.directory = resultdir
    resultfile.name = filename
    resultfile.path = resultpath

    return resultfile


def plot_pulse(t, x, time_unit="s", y_max=None):
    """Plot pulse as time-trace in standardised graph.

    Arguments
    ---------
    t   1D array        Time vector
    x   1D or 2D array  Vector of values to plot
    time_unit   String  Unit for scaling time axis

    """
    multiplier, freq_unit = find_timescale(time_unit)
    plt.plot(t*multiplier, x)
    plt.xlabel(f'Time [{time_unit}]')
    plt.ylabel('Ampltude')
    plt.grid(True)
    if y_max is not None:
        plt.ylim(y_max*np.array([-1, 1]))
    return 0


def powerspectrum(y, dt, n_fft=None,
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
    f, psd = signal.periodogram(y, fs=1/dt, nfft=n_fft, detrend=False)
    psd = psd.transpose()

    if normalise:
        if psd.ndim == 1:
            psd = psd/psd.max()
        else:
            n_ch = psd.shape[1]
            for k in range(n_ch):
                psd[:, k] = psd[:, k]/psd[:, k].max()
    if scale.lower() == "db":
        psd = 10*np.log10(psd)
    return f, psd


def plot_spectrum(t, x, time_unit="s",
                  y_max=None, f_max=None, n_fft=None,
                  scale="dB", normalise=True, db_min=-40):
    """Plot time trace and power spectrum on standardised format.

    Requires evenly sampled points

    Arguments
    ---------
    t           1D array        Time vector
    x           1D or 2D array  Values, time trace(s)
    time_unit   String          Unit for time axis, also for frequency scale
    f_max       Float           Max. frequency to plot
    n_fft       Int             No of points in FFT
    scale       String          Linear (Power)  or dB
    normalise   Boolean         Normalise to 1 (0 dB) as maximum
    db_min      Float           Minimum on dB-scale, re. max.
    """
    # Pulse in time-domain
    plt.subplot(2, 1, 1)
    plot_pulse(t, x, time_unit, y_max)

    # Power spectrum
    plt.subplot(2, 1, 2)
    dt = t[1] - t[0]   # Assumes even sampling
    multiplier, freq_unit = find_timescale(time_unit)
    f, psd = powerspectrum(x, dt, n_fft=n_fft,
                           scale=scale, normalise=normalise)
    plt.plot(f/multiplier, psd)
    plt.xlabel(f'Frequency [{freq_unit}]')
    plt.grid(True)
    if f_max is None:
        f_max = f.max()
    db_lim = psd.max() + np.array([db_min, 0])

    plt.xlim((0, f_max/multiplier))

    if (scale.lower() == "db"):
        plt.ylim(db_lim)
        if normalise:
            plt.ylabel('Power [dB re. max]')
        else:
            plt.ylabel('Power [dB]')
    else:
        plt.ylabel('Power')
    return 0
