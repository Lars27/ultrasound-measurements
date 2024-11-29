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
import pdb


# %% Classes

class Waveform:
    """Measurement results as 1D time-traces.

    Used to store traces sampled in time.
    Compatible with previous versions used in e.g. LabVIEW and Matlab
    Adapted from LabVIEW's waveform-type, similar to python's mccdaq-library

    Attributes
    ----------
    t0 : float
        Start time
    dt : float
        Sample interval
    dtr :float
        interval between sample blocks. Rarely used
    y : 2D array of float
        Results. Each column is a channel, samples as rows

    Methods
    -------
    n_channels : int
        Number of data channels
    n_samples : int
        Number of samples per channel
    t : 1D array of float
        Time vector
    fs : float
        Sample rate
    n_fft : int
        Number of points used to calculate spectrum
    f : 1D array of float
        Frequency vector
    powerspectrum : 1D array of float
        Powerspectrum of traces
    filtered : Waveform class
        Bandpass filtered traces, all else equal
    zoomed : Waveform class
        Zoomed to specified interval, all else identtical
    plot : function
        Plots result in figure
    plot_spectrum : function
        Plots traces and spectrum
    save : function
        Loads Waveform from binary file
    load : function
        Saves Waveform to binary file
    """

    def __init__(self, y=np.zeros((100, 1)), dt=1, t0=0):
        """Initialise to ensure correct shapes."""
        self.y = y              # Voltage traces as 2D numpy array
        if y.ndim == 1:         # Ensure v is 2D
            self.y = self.y.reshape((1, len(y)))
        self.dt = dt             # [s]  Sample interval
        self.t0 = t0             # [s]  Time of first sample
        self.dtr = 0             # [s]  interval between blocks. Obsolete

    def n_channels(self):
        """Find number of data channels in trace."""
        return self.y.shape[1]

    def n_samples(self):
        """Find number of points in trace."""
        return self.y.shape[0]

    def t(self):
        """Time vector [s].

        Calculated from start time and sample interval [s]
        """
        return np.linspace(self.t0,
                           self.t0+self.dt*self.n_samples(),
                           self.n_samples())

    def fs(self):
        """Sample rate [Hz]."""
        return 1/self.dt

    def n_fft(self, upsample=0):
        """Set number of points used to calculate spectrum.

        Always a power of 2, zeros padded if needed.

        Parameters
        ----------
        upsample : int
            Number of extra powers of 2 to add
        """
        upsample = max(round(upsample), 0)
        m, e = frexp(self.n_samples())
        n = 2**(e+upsample)
        # n = 2**(self.n_samples().bit_length() +upsample)  # Next power of 2
        return max(n, 2048)

    def f(self):
        """Frequency vector [Hz]."""
        return np.arange(0, self.n_fft()/2)/self.n_fft() * self.fs()

    def powerspectrum(self, normalise=False, scale="linear", upsample=2):
        """Calculate power spectrum of time trace.

        Parameters
        ----------
        normalise : bool
            Normalise to 1 (0 dB) as maximum
        scale : str
            Linear (Power)  or dB
        upsample : int
            interpolate spectrum by padding to next power of 2

        Returns
        -------
        f : 1D array
            Frequency vector
        psd : 2D array
            Power spectral density
        """
        f, psd = powerspectrum(self.y,
                               self.dt,
                               n_fft=self.n_fft(upsample=2),
                               scale=scale,
                               normalise=normalise)
        return f, psd

    def filtered(self, filter):
        """Bandpass filtered trace.

        Parameters
        ----------
        filter : WaveformFilter
            Filter specification

        Returns
        -------
        wfm : Waveform
            Copy of original waveform with filtered data
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

        Parameters
        ----------
        tlim : List of float
            Start and end of interval to select

        Returns
        -------
        wfm : Waveform class
            Copy of original waveform zommed to interval

        """
        wfm = copy.deepcopy(self)
        nlim = np.flatnonzero((self.t() >= min(tlim))
                              & (self.t() <= max(tlim)))

        wfm.t0 = self.t()[np.min(nlim)]
        wfm.y = self.y[nlim]
        return wfm

    def plot(self, time_unit="us", ch=[0, 1], y_max=None):
        """Plot time traces using unit time_unit.

        Parameters
        ----------
        time_unit : str
            Unit to plot tim in, 's', 'ms', 'us'
        ch : List of int
            Channels to plot
        y_max : float
            Max. scale on amplitude-axis
        """
        plot_pulse(self.t(), self.y[ch], time_unit, y_max)

        return 0

    def plot_spectrum(self, time_unit="s", ch=[0, 1], y_max=None, f_max=None,
                      normalise=True, scale="dB", db_min=-40, ax=None):
        """Plot trace and power spectrum in one graph.

        Parameters
        ----------
        time_unit : str
            Unit to plot tim in, 's', 'ms', 'us'
        ch : List of int
            Channels to plot
        y_max : float
            Max. scale on amplitude-axis
        f_max : float
            Max. scale on frequency axis
        normalise : bool
            Normalise power spectrum plot  to 1 (0 dB)
        scale : str
            Linear (Power) or dB
        db_min : float
            Dynamic range on dB-plot
        ax :List of axis objects
            Axes to plot time trace and spectrum
        """
        plot_spectrum(self.t(), self.y[:, ch], time_unit=time_unit,
                      y_max=y_max, f_max=f_max, n_fft=self.n_fft(),
                      normalise=normalise, scale=scale, db_min=db_min, ax=ax)
        return 0

    def save(self, filename):
        """Save 'Waveform' variable to binary file, as 4-byte (sgl) floats.

        Compatible with internal format used since 1990s on a variety of
        platforms (LabWindows, C, LabVIEW, Matlab)
        Uses 'c-order' of arrays and IEEE big-endian byte order
        Complements load()

        Parameters
        ----------
        filename    str  Full path of file to save data in

        Contents of file
        ----------------
        hd : str
            Header, informative text
        nc : int
            Number of channels
        t0 : float
            Start time
        dt : float
            Sample interval
        dtr : float
            interval between blocks. Used only in special cases
        v : 2D array of float
            Data points (often voltages)
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

        Loads contents of file into the variable.
        Compatible with internal format used since 1990s on a variety of
        platforms (LabWindows, C, LabVIEW, Matlab)
        Uses 'c-order' of arrays and IEEE big-endian byte order.
        Complements save()

        Parameters
        ----------
        filename : str
            Full path of file to load
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
    envelope : str
        Pulse envelope: rect, hann, tukey, ...
    shape :  str
        Carrier wave: sine, square, triangle, ...
    f0 : float
        Carrier wave frequency
    n_cycles : float
        Pulse length as number of cycles
    phase : float
        Phase of carrier wave in degrees, ref. cosine
    a : float
        Amplitude
    dt : float
        Sample interval
    alpha : float
        Tukey window cosine-fraction, alpha = 0 ... 1
    trigger_source
        Not implemented yet
    status: str
        Pulser status, "ON", "OFF", "UNAVAILABLE"

    Methods
    -------
    t  : 1D array of float
        Time vector
    y : 1D array of float
        Pulse time trace
    period : float
        Carrier wave period
    duration : float
        Pulse duration, seconds
    n_samples : int
        Number of samples in pulse
    n_fft : int         ,
        Number of points used to calculate spectrum
    powerspectrum : 1D array of float
        Powerspectrum of pulse
    time_unit : str
        Appropriate unit for time-trace plot, from f0
    plot : Function
        Plots result in figure
    plot_spectrum : Function
        Plots traces and spectrum
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
    available = False
    on = False

    def t(self):
        """Time vector [s]."""
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
        y[-1] = 0    # Remove residue DC-level after pulse is over
        return y

    def period(self):
        """Period of carrier wave [s]."""
        return 1/self.f0

    def duration(self):
        """Duration of pulse [s]."""
        return self.period()*self.n_cycles

    def n_samples(self):
        """Find number of samples in pulse."""
        return len(self.t())

    def time_unit(self):
        """Set unit for time trace plot, based on cantre frequency."""
        if self.f0 > 1e9:
            return "ns"
        if self.f0 > 1e6:
            return "us"
        elif self.f0 > 1e3:
            return "ms"
        else:
            return "s"

    def n_fft(self):
        """Set number of points to calculate spectrum.

        Always as power of 2, zeros padded at end
        """
        m, e = frexp(self.n_samples())
        n = 2**(e+3)
        # n = 2**(3+(self.n_samples()-1).bit_length())
        return max(n, 2048)

    def powerspectrum(self):
        """Calculate power spectrum of trace.

        Returns
        -------
        f : 1D array of float
            Frequency vector
        psd : 1D array of float
            Power spectral density
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
    type : str
        Type filter: "None", "AC", "BPF" (Bandpass)
    f_min : float
        Lower cutoff frequency
    f_max : float
        Upper cutoff frequency
    order :  int
        Filter order
    fs : float
        Sample rate

    Methods
    -------
    wc : 1D array of float
        Cutoff-frequencies normalised to sample rate
    coefficients : 1D array of float
        Filter coefficients, b and a
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
    x : float
        Reference value, positive or negative

    Returns
    -------
    xn : float
        Next number in 1-2-5-10 sequence greater than magnitude of x
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

    Parameters
    ----------
    time_unit : str
        Time unit used in plots: "s", "ms", "us", "ns"

    Returns
    -------
    multiplier : float
        Multiplier for time to get requested unit
    freq_unit : str
        Corresponting Frequency unit
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
    """Minimum and maximum values as numpy array.

    Parameters
    ----------
    limits : 1Darray of floats
        Requested limits
    min_diff : float
        Minimum difference between min and max

    Returns
    -------
    [min, max] : 1D array of float
        Actual limits
    """
    min_value = min(limits)
    max_value = max(max(limits), min_value+min_diff)
    return np.array([min_value, max_value])


def read_scaled_value(quantity):
    """Interpret a text as a scaled value (milli, kilo, Mega etc.).

    Parameters
    ----------
    quantity : str
        Value as "number unit", e.g. "3.4 MHz"

    Returns
    -------
    value : float
        Value scaled with unit, e.g. 3 400 000 or 3.4e6
    """
    quantity = quantity.split(' ')   # Split in number and unit at space
    number = float(quantity[0])
    if len(quantity) == 1:
        multiplier = 1
    else:
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

    Parameters
    ----------
    prefix :str
        Code that characterises measurement type
    ext : str
        File Extension
    resultdir : str
        Directory for results

    Returns
    -------
    resultfile : ResultFile class
        Result-file parameteres: name, path, counter, etc.
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


def plot_pulse(ax, t, x, time_unit="s", y_max=None):
    """Plot pulse as time-trace in standardised graph.

    Parameters
    ----------
    t : 1D array of float
        Time vector
    x : 1D or 2D array of float
        Vector of values to plot
    time_unit : str
        Unit for scaling time axis
    """
    multiplier, freq_unit = find_timescale(time_unit)
    ax.plot(t*multiplier, x)

    ax.set(xlabel=f"Time [{time_unit}]",
           ylabel="Ampltude")
    ax.grid(True)

    if y_max is not None:
        ax.set_ylim(y_max*np.array([-1, 1]))

    return 0


def powerspectrum(y, dt, n_fft=None,
                  scale="linear", normalise=False, transpose=True):
    """Calculate power spectrum of pulse. Finite length signal, no window.

    Datapoints in rows (dimension 0)
    Channels in (dimension 1)
    Transposed to fit definition of periodogram function in SciPy

    Parameters
    ----------
    x : 1D array of float
        Time trace
    dt : float
        Sample interval
    n_fft : int
        Number of points in FFT
    scale : str
        Linear (power) or dB
    normalise : Booloean
        Normalise spectrum to max value

    Returns
    -------
    f : 1D array of float
        Frequency vector
    psd : 2D aray of float
        Power spectral density
    """
    y = y.transpose()
    f, psd = signal.periodogram(y, fs=1/dt, nfft=n_fft, detrend=False)
    psd = psd.transpose()  # Periodogram function calculates along dimension 1

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
                  scale="dB", normalise=True, db_min=-40, ax=None):
    """Plot time trace and power spectrum on standardised format.

    Requires evenly sampled points

    Parameters
    ----------
    t : 1D array of float
        Time vector
    x : 1D or 2D array of float
        Values, time trace(s)
    time_unit : str
        Unit for time axis, also for frequency scale
    f_max : float
        Max. frequency to plot
    n_fft : int
        No of points in FFT
    scale : str
        Linear (Power)  or dB
    normalise : bool
        Normalise to 1 (0 dB) as maximum
    db_min : float
        Minimum on dB-scale, re. max.
    """
    # Pulse in time-domain
    if ax is None:
        fig = plt.figure(figsize=[10, 10])
        ax = [fig.add_subplot(2, 1, 1), fig.add_subplot(2, 1, 2)]

    plot_pulse(ax[0], t, x, time_unit, y_max)

    # Power spectrum
    dt = t[1] - t[0]   # Assumes even sampling

    f, psd = powerspectrum(x, dt, n_fft=n_fft,
                           scale=scale, normalise=normalise)

    multiplier, freq_unit = find_timescale(time_unit)

    if f_max is None:
        f_max = f.max()

    if (scale.lower() == "db"):
        db_lim = np.array([db_min, 0])
        if not np.any(np.isnan(psd)):
            db_lim = psd.max() + db_lim
        ax[1].set_ylabel(db_lim)

        if normalise:
            spectrumlabel = "Power [dB re. max]"
        else:
            spectrumlabel = "Power [dB]"
    else:
        spectrumlabel('Power')

    ax[1].plot(f/multiplier, psd)
    ax[1].set(xlabel=f"Frequency [{freq_unit}]",
              xlim=(0, f_max/multiplier),
              ylabel=spectrumlabel)
    ax[1].grid(True)

    return 0
