"""Acquire ultrasound data from Picoscope 2000.

Wrappers to c-style function calls in DLLs from Picoscope SDK.

Wraps c-style commands (ctypes.xx) to standard Python variables and sets
scaling constants, ranges etc. specific for the instrument.

The classes and functions in this file shall provide an easy interface to
Picoscope 2000a from any standard Pyton environment

Based on example program from Picotech
  PS2000A BLOCK MODE EXAMPLE, # Copyright (C) 2018-2022 Pico Technology Ltd.

Reference
  PicoScope 2000 Series (A API) - Programmer's Guide. Pico Tecknology Ltd, 2022

Lars Hoff, USN, Nov 2024
"""

import time
import ctypes
import numpy as np
from picosdk.ps2000a import ps2000a as picoscope
from picosdk.functions import adc2mV, assert_pico_ok

DAC_SAMPLERATE = 500e6   # [Samples/s] Fixed, see Programmer's guide
DAC_MAX_AMPLITUDE = 2.0   # [v] Max. amplitude from signal generator
DAC_MAX_SAMPLES = 10000
CH_NAMES = ["A", "B", "C", "D"]
N_CHANNELS = len(CH_NAMES)


# %% Classes

class Channel:
    """Osciloscope vertical (voltage) channel settings and status.

    Attributes
    ----------
    no : int
      Channel number
    enabled : bool
        Channel enabled or not
    v_range : float
        Requested full-scale voltage range (plus/minus)
    adc_max : int
          Maximum ADC value, for scaling to voltage
    offset : float
        Offset voltage
    coupling : str
        Channel coupling, "DC"  or "AC"
    bwl : bool
        Bandwidth limiter activated in instrument.
        Not available on PS2000-serias

    Methods
    -------
    name : str
        Name of channel, "A", "B", ...
    v_max: float
        Actual full-scale range of instrument
    adc_range : int
        Instrument ADC range no. for voltage range
    coupling_code : int
        Numerical code corresponding to coupling string
    """

    def __init__(self, no):
        """Initialise with default values."""
        self.no = no
        self.enabled = True
        self.v_range = 1
        self.adc_max = 32512   # See 'Voltage ranges' in documentation
        self.offset = 0
        self.coupling = "DC"
        self.bwl = False

    def name(self):
        """Return Picoscope channel name (A,B, ...) from number (0,1, ...)."""
        return channel_no_to_name(self.no)

    def v_max(self):
        """[V] Find allowed voltage range from requested range."""
        vm = find_scale(self.v_range)
        return vm

    def coupling_code(self):
        """Return Picoscope coupling code from specified name."""
        return picoscope.PS2000A_COUPLING[f"PS2000A_{self.coupling}"]

    def adc_range(self):
        """Return Picoscope range code from specified voltage."""
        if self.v_max() < 1:
            adc_range_name = f"PS2000A_{int(self.v_max()*1000)}MV"
        else:
            adc_range_name = f"PS2000A_{int(self.v_max())}V"
        return picoscope.PS2000A_RANGE[adc_range_name]


class Trigger:
    """Osciloscope trigger settings.

    Attributes
    ----------
    source : str
        Name of source for trigger, "A", "B", "EXT", ...
    level : float
        Trigger level in Volts
    direction : str
        Trigger edge direction, "Rising", "Falling"
    delay : float
        Trigger delay [seconds]
    autodelay : float
        Wait time for auto trigger [seconds]
    adc_max : float
        Instrument ADC maximum value, for scaling

    Methods
    -------
    enabled : bool
        External trigger enabled or internal trigger
    """

    source = "A"
    level = 0.5           # [V]
    direction = "Rising"
    delay = 0             # [s]
    autodelay = 10e-3     # [s]
    adc_max = 0           # Meaningless value, will be imported later

    def enabled(self):
        """Dectivate trigger if source is 'Internal'."""
        return (self.source.lower()[0:3] != 'int')


class Horizontal:
    """Osciloscope horizontal (time) scale.

    Attributes
    ----------
    timebase : int
        Number defining oscilloscope sample rate
    n_samples : int
        Number of samples to aquire per channel
    dt : float
        Oscilloscope sampling interval
    trigger_position : float
        Trigger position in % of trace length

    Methods
    -------
    fs : float
        Sample rate
    n_pretrigger : int
        Number of sample points before trigger
    n_posttrigger : int
        Number of sample points after trigger
    t0 : float
        Time of first sample point
    t_max : float
        Time of last sample point
    """

    timebase = 3
    n_samples = 1000
    dt = 1                  # Dummy, read from intrument
    trigger_position = 0.0  # Trigger position in % of trace length

    def fs(self):
        """Return Picoscope samplig rate [S/s]."""
        return 1/self.dt

    def n_buffer(self):
        """No. of samples per channel."""
        if self.n_samples < 1:
            n = 1
        elif self.n_samples > DAC_MAX_SAMPLES:
            n = DAC_MAX_SAMPLES
        else:
            n = self.n_samples

        return n

    def n_pretrigger(self):
        """Return number of samples before trigger."""
        return int(self.n_buffer() * self.trigger_position/100)

    def n_posttrigger(self):
        """Return number of samples after trigger."""
        return int(self.n_buffer() - self.n_pretrigger())

    def t0(self):
        """Return start time, i.e., time of first sample."""
        return -self.n_pretrigger() * self.dt

    def t_max(self):
        """Return end time, i.e., time of last sample.

        Note thet this is not the trace duration, but referred to the trigger
        time. The start time may be negative
        """
        return (self.n_buffer() - self.n_pretrigger() - 1) * self.dt


class Communication:
    """c-type variables for calling c-style functions in DLLs from Pico SDK.

    Handle to and information about the istrument (oscilloscope)
    The SK for communication with the instrument uses c-type function calls.
    This requres use of c-type variables. This function provides an interface
    from Python to these functions.
    The c-type variables are only used inside this function.

    Attributes
    ----------
    handle : ctypes.c_int16
        Handle to instument , identifier
    connected : bool
        Is the instrument connected?
    signal_generator : bool
        Does the instrument contains an arbitrary waveform generator?
    status : dictionary of str
        Status messages for instrument
    acqusition_ready : ctypes.c_int16
        Instument acquisition finished
    max_samples : ctypes.c_int32
        Max. no of samples to acquire
    max_adc : ctypes.c_int16
        Maximum value for instument ADC
    overflow : ctypes.c_int16
        Overflow detected in input data
    channel : str
        Channel name, 'A', 'B', ...
    buffer : List of pointers
        Buffer for acquired data ponts
    awg_max_value : ctypes.c_int16
        Max value for arbitrary waveform generator
    awg_min_value : ctypes.c_int16
        Min value for arbitrary waveform generator
    awg_min_length : ctypes.c_int32
        Min. no of points for arbitrary waveform generator
    awg_max_length : ctypes.c_int32
        Max. no of points for arbitrary waveform generator
    """

    handle = ctypes.c_int16(0)
    connected = False
    signal_generator = False
    status = {}
    acqusition_ready = ctypes.c_int16(0)
    max_samples = ctypes.c_int32(0)
    max_adc = ctypes.c_int16(0)
    overflow = ctypes.c_int16(0)
    channel = 'A'
    buffer = []
    awg_max_value = ctypes.c_int16(0)
    awg_min_value = ctypes.c_int16(0)
    awg_min_length = ctypes.c_int32(0)
    awg_max_length = ctypes.c_int32(0)


# %%
"""
Wrappers for original c-style library functions
Instrument is controlled from Python using the function calls listed below
Data are exchanged using the classes defined above
"""


def open_adc(dso):
    """Open connection to oscilloscope.

    Argument and output
    -------------------
    dso : Communication class
        Communication status for instrument
    """
    dso.status["openunit"] = picoscope.ps2000aOpenUnit(
                                ctypes.byref(dso.handle),
                                None)
    try:
        assert_pico_ok(dso.status["openunit"])
        dso.connected = True
    except:  # PicoNotOkError:
        power_state = dso.status["openunit"]
        if power_state in [
                picoscope.PICO_STATUS["PICO_POWER_SUPPLY_NOT_CONNECTED"],
                picoscope.PICO_STATUS["PICO_USB3_0_DEVICE_NON_USB3_0_PORT"]
                ]:
            dso.status["changePowerSource"] \
                = picoscope.ps2000aChangePowerSource(dso.handle, power_state)
        else:
            raise

        assert_pico_ok(dso.status["changePowerSource"])
        dso.connected = (dso.status["changePowerSource"] == 0)

    dso.status["maximumValue"] = picoscope.ps2000aMaximumValue(
                                             dso.handle,
                                             ctypes.byref(dso.max_adc))
    assert_pico_ok(dso.status["maximumValue"])

    dso.connected = (dso.connected and (dso.status["maximumValue"] == 0))
    return dso


def stop_adc(dso):
    """Stop oscilloscope. Only applicable when in streaming mode.

    Argument
    --------
    dso : Communication class
        Communication status for instrument

    Output
    ------
    dso.status : dictionary of str
        Status messages for instrument
    """
    dso.status["stop"] = picoscope.ps2000aStop(dso.handle)
    assert_pico_ok(dso.status["stop"])
    return dso.status


def close_adc(dso):
    """Close connection to ocsiloscope.

    Argument
    --------
    dso : Communication class
        Communication status for instrument

    Output
    ------
    dso.status : dictionary of str
        Status messages for instrument
    """
    dso.status["close"] = picoscope.ps2000aCloseUnit(dso.handle)
    assert_pico_ok(dso.status["close"])
    return dso.status


def set_vertical(dso, channel):
    """Set vertical scale in oscilloscope (Voltage range).

    Argument
    --------
    dso : Communication class
        Communication status for instrument
    channel : Channel class
        Oscilloscope channel settings

    Output
    ------
    dso.status  dictionary of str
        Status messages for instrument
    """
    name = channel_no_to_name(channel.no)
    status_name = f"setCh{name}"
    dso.status[status_name] = picoscope.ps2000aSetChannel(
        dso.handle,
        channel.no,
        channel.enabled,
        channel.coupling_code(),
        channel.adc_range(),
        channel.offset)
    assert_pico_ok(dso.status[status_name])
    return dso.status


def set_trigger(dso, trigger, channel, sampling):
    """Configure oscilloscope trigger.

    Arguments
    ---------
    dso : Communication class
        Communication status for instrument
    trigger : Trigger class
        Settings for oscilloscope trigger
    channel : Channel class
        Settings for oscilloscope vertical scale
    sampling : Horizontal class
        Settings for oscilloscope horizontal scale

    Output
    ------
    dso.status  dictionary of str
        Status messages for instrument
    """
    enabled = int(trigger.enabled())

    if trigger.source.lower()[0] in ("a", "b", "c", "d"):
        source = picoscope.PS2000A_CHANNEL[f"PS2000A_CHANNEL_{trigger.source}"]
        ch_no = channel_name_to_no(trigger.source)
        relative_level = np.clip(trigger.level/channel[ch_no].v_max(), -1, 1)
        threshold = int(relative_level*channel[ch_no].adc_max)
    else:
        dso.status["trigger"] = -1
        return dso.status

    # Only the two basic trigger modes implemented: Rising or falling edge
    if trigger.direction.lower()[0:4] == 'fall':
        mode = 3   # Trigger mode "Falling"
    else:
        mode = 2   # Trigger mode "Rising"

    delay_pts = int(trigger.delay/sampling.dt)
    autotrigger_ms = ctypes.c_int16(int(trigger.autodelay*1e3))

    dso.status["trigger"] = picoscope.ps2000aSetSimpleTrigger(dso.handle,
                                                              enabled,
                                                              source,
                                                              threshold,
                                                              mode,
                                                              delay_pts,
                                                              autotrigger_ms)
    assert_pico_ok(dso.status["trigger"])

    return dso.status


def get_trigger_time_offset(dso):
    """Read offset of last trigger.

    Arguments
    ---------
    dso : Communication class
        Communication status for instrument

    Output
    ------
    trigger_time_offset : float
        Time from trigger to first sample point
    """
    segment_index = 0
    trigger_time = ctypes.c_int64(0)
    time_units = ctypes.c_int32(0)
    dso.status["triggerTimeOffset"] = picoscope.ps2000aGetTriggerTimeOffset64(
                                                    dso.handle,
                                                    ctypes.byref(trigger_time),
                                                    ctypes.byref(time_units),
                                                    segment_index)
    assert_pico_ok(dso.status["triggerTimeOffset"])
    trigger_time_offset = float(trigger_time.value)

    return trigger_time_offset


def get_sample_interval(dso, sampling):
    """Read  actual sample interval from osciloscope.

    Arguments
    ---------
    dso : Communication class
        Communication status for instrument
    sampling : Horizontal class
        Settings for oscilloscope horizontal scale

    Output
    ------
    sample_interval : float
        Sampling interval for acquired trace
    """
    sample_interval_ns = ctypes.c_float(0)
    max_n_samples = ctypes.c_int32(0)
    oversample = ctypes.c_int16(0)

    ok = picoscope.ps2000aGetTimebase2(dso.handle,
                                       sampling.timebase,
                                       sampling.n_buffer(),
                                       ctypes.byref(sample_interval_ns),
                                       oversample,
                                       ctypes.byref(max_n_samples),
                                       0)
    assert_pico_ok(ok)
    sample_interval = sample_interval_ns.value*1e-9
    return sample_interval


def configure_acquisition(dso, sampling):
    """Configure acquisition of data from oscilloscope.

    Configures oscilloscope and sets up buffers fro input data

    Arguments
    ---------
    dso : Communication class
        Communication status for instrument
    sampling : Horizontal class
        Oscilloscope horizontal settings

    Output
    ------
    dso : Communication class
        Communication status for instrument
    """
    dso.max_samples.value = sampling.n_buffer()
    segment_index = 0
    downsample_mode = 0

    dso.buffer = [(ctypes.c_int16*sampling.n_buffer())()
                  for k in range(N_CHANNELS)]

    status_prefix = "setDataBuffers"
    ch_no = 0
    for ch_name in CH_NAMES:
        status_name = status_prefix+ch_name
        dso.status[status_name] = picoscope.ps2000aSetDataBuffer(
                                             dso.handle,
                                             ch_no,
                                             ctypes.byref(dso.buffer[ch_no]),
                                             sampling.n_buffer(),
                                             segment_index,
                                             downsample_mode)
        assert_pico_ok(dso.status[status_name])
        ch_no += 1

    return dso


def acquire_trace(dso, sampling, ch):
    """Acuire voltage trace from oscilloscope.

    Arguments
    ---------
    dso : Communication class
        Communication status for instrument
    ch : List of string
        Names of channels to acquire
    sampling : Horizontal class
        Settings for oscilloscope horizontal scale

    Output
    ------
    dso.status : dictionary of str
          Status message for operation
    v  : 2D array of float
        Acquired traces, scaled in Volts
    """
    start_index = 0
    downsample_ratio = 0
    downsample_mode = 0
    oversample = 0
    segment_index = 0
    dso.status["runBlock"] = picoscope.ps2000aRunBlock(
                                    dso.handle,
                                    sampling.n_pretrigger(),
                                    sampling.n_posttrigger(),
                                    sampling.timebase,
                                    oversample,
                                    None,
                                    segment_index,
                                    None,
                                    None)
    assert_pico_ok(dso.status["runBlock"])

    # Check for data collection to finish
    # Primitive polling, consider replacing ps2000aIsReady
    dso.acqusition_ready.value = 0
    while dso.acqusition_ready.value == 0:
        dso.status["isReady"] = picoscope.ps2000aIsReady(
                                        dso.handle,
                                        ctypes.byref(dso.acqusition_ready))
        time.sleep(0.01)

    # Transfer data values
    dso.status["getValues"] = picoscope.ps2000aGetValues(
                                         dso.handle,
                                         start_index,
                                         ctypes.byref(dso.max_samples),
                                         downsample_ratio,
                                         downsample_mode,
                                         segment_index,
                                         ctypes.byref(dso.overflow))
    assert_pico_ok(dso.status["getValues"])

    # Convert ADC counts data to Volts
    v_mv = np.zeros([sampling.n_buffer(), N_CHANNELS])
    for ch_no in range(N_CHANNELS):
        v_mv[:, ch_no] = adc2mV(dso.buffer[ch_no],
                                ch[ch_no].adc_range(),
                                dso.max_adc)
    v = 1e-3*v_mv  # np.column_stack([mv_a, mv_b])

    return dso, v


def check_awg(dso):
    """Check whether the oscilloscope has a waveform generator.

    No dedicated function for this was found in the documentation.
    Uses instead a call to the simplest signal generator fubnction and
    checks for error.

    Arguments
    ---------
    dso : Communication class
        Communication status for instrument

    Output
    ------
    dso : Communication class
        Communication status for instrument
    """
    dso.status["sigGenArbMinMax"] \
        = picoscope.ps2000aSigGenArbitraryMinMaxValues(
                                            dso.handle,
                                            ctypes.byref(dso.awg_min_value),
                                            ctypes.byref(dso.awg_max_value),
                                            ctypes.byref(dso.awg_min_length),
                                            ctypes.byref(dso.awg_max_length))
    try:
        assert_pico_ok(dso.status["sigGenArbMinMax"])
        dso.signal_generator = True
    except:   # PicoSDKCtypesError
        dso.signal_generator = False

    return dso


def set_signal(dso, sampling, pulse):
    """Send pulse to arbitrary waveform generator.

    Arguments
    ---------
    dso : Communication class
        Communication status for instrument
    sampling : Horizontal class
        Settings for oscilloscope horizontal scale
    pulse : Pulse class
        Defnition of pulse for AWG

    Output
    ------
    dso : Communication class
        Communication status for instrument
    """
    if pulse.on:
        amplitude = min(pulse.a, DAC_MAX_AMPLITUDE)
    else:
        amplitude = 0
    dso.status["sigGenArbMinMax"] \
        = picoscope.ps2000aSigGenArbitraryMinMaxValues(
                                            dso.handle,
                                            ctypes.byref(dso.awg_min_value),
                                            ctypes.byref(dso.awg_max_value),
                                            ctypes.byref(dso.awg_min_length),
                                            ctypes.byref(dso.awg_max_length))
    try:
        assert_pico_ok(dso.status["sigGenArbMinMax"])
        dso.signal_generator = True
    except:   # PicoSDKCtypesError
        dso.signal_generator = False
        return dso

    # Scale pulse for awg buffer
    y_scaled = pulse.y()/pulse.a*dso.awg_max_value
    pulsedata = y_scaled.astype(ctypes.c_int16)
    buffer_length = ctypes.c_uint32(len(pulsedata))
    index_mode = ctypes.c_int32(0)
    delta_phase = ctypes.c_uint32(0)
    dso.status["freqToPhase"] = picoscope.ps2000aSigGenFrequencyToPhase(
                                                dso.handle,
                                                1/pulse.duration(),
                                                index_mode,
                                                buffer_length,
                                                ctypes.byref(delta_phase))
    assert_pico_ok(dso.status["freqToPhase"])

    # Values passed as c-type variables, type casting not checked for all
    # See documentation in Programmer's Guide.
    offset_voltage_uv = ctypes.c_int32(0)
    pp_voltage_uv = ctypes.c_uint32(int(2*amplitude*1e6))  # Peak-to-peak, uV
    trigger_type = ctypes.c_int32(0)
    trigger_source = ctypes.c_int32(pulse.trigger_source)
    shots = ctypes.c_uint32(1)

    waveform_length = ctypes.c_int32(len(pulsedata))
    waveform_pointer = pulsedata.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))

    # Parameters not in use
    delta_phase_increment = ctypes.c_uint32(0)
    dwell_count = ctypes.c_uint32(0)
    sweep_type = ctypes.c_int32(0)
    operation = ctypes.c_int32(0)
    sweeps = ctypes.c_uint32(0)
    ext_in_threshold = ctypes.c_int16(0)

    dso.status["setSigGenArbitrary"] = picoscope.ps2000aSetSigGenArbitrary(
                                                dso.handle,
                                                offset_voltage_uv,
                                                pp_voltage_uv,
                                                delta_phase.value,
                                                delta_phase.value,
                                                delta_phase_increment,
                                                dwell_count,
                                                waveform_pointer,
                                                waveform_length,
                                                sweep_type,
                                                operation,
                                                index_mode,
                                                shots,
                                                sweeps,
                                                trigger_type,
                                                trigger_source,
                                                ext_in_threshold)
    assert_pico_ok(dso.status["setSigGenArbitrary"])
    return dso


# %% Utility functions

def channel_no_to_name(no):
    """Convert number to Picoscope channel name (A, B, ...)."""
    return chr(ord("A")+no)


def channel_name_to_no(name):
    """Convert Picoscope channel name (A, B, ...) to number."""
    return ord(name)-ord("A")


def find_timebase(fs_requested):
    """Find instrument timebase based on requested sample rate.

    Arguments
    ---------
    fs_requested : float
        Requested sample rate

    Outputs
    -------
    timebase: int
        Oscilloscope timbase closest to requested sample rate
    fs_actual: float
        Actual sample sate for timebase
    """
    fs_max = 125e6
    timebase = int(fs_max/fs_requested)+2  # See documentation for 'Timebases'
    timebase = max(timebase, 3)            # Min. allowed timebase is 3

    dt = (timebase-2)/fs_max
    fs_actual = 1/dt

    return timebase, fs_actual


def find_scale(x):
    """Find oscilloscope vertical range (Volts).

    Arguments
    ---------
    x : float
        Requested maximum range

    Outputs
    -------
    xn :float
        Next ooscilloscope range larger than x
    """
    vmin = 20e-3
    vmax = 20
    if x <= vmin:
        xn = vmin
    elif x >= vmax:
        xn = vmax
    else:
        prefixes = np.array([1, 2, 5, 10])
        exp = int(np.floor(np.log10(abs(x))))
        mant = abs(x) / (10**exp)
        valid = np.where(prefixes >= mant-0.001)  # Tiny margin for roundoff
        mn = np.min(prefixes[valid])
        xn = mn*10**exp
    return xn
