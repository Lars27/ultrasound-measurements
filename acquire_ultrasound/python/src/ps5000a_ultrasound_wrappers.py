"""Acquire ultrasound data from Picoscope 5000.

Wrappers to c-style function calls in DLLs from Picoscope SDK.

Wraps c-style commands (ctypes.xx) to standard Python variables and sets
scaling constants, ranges etc. specific for the instrument.

The classes and functions in this file shall provide an easy interface to
Picoscope 5000a from any standard Pyton environment

Based on example program from Picotech
  PS5000A BLOCK MODE EXAMPLE, # Copyright (C) 2018-2022 Pico Technology Ltd.

Reference
  PicoScope 5000 Series (A API) - Programmer's Guide. Pico Tecknology Ltd, 2018

Lars Hoff, USN, Sep 2022
Modified June 2024 to better follow PEP-8 and numpy docstring style guides.
"""

import time
import ctypes
import numpy as np
from picosdk.ps5000a import ps5000a as picoscope
from picosdk.functions import adc2mV, assert_pico_ok

DAC_SAMPLERATE = 500e6   # [Samples/s] Fixed, see Programmer's guide
DAC_MAX_AMPLITUDE = 2.0   # [v] Max. amplitude from signal generator
CH_NAMES = ["A", "B"]


# %% Classes

class Status:
    """Instrument connection status monitoring."""

    handle = ctypes.c_int16()
    connected = False
    status = {}


class Channel:
    """Osciloscope vertical (voltage) channel settings and status."""

    def __init__(self, no):
        """Initialise with default values."""
        self.no = no
        self.v_range = 1       # [V] Requested full scale voltage
        self.adc_max = 32767   # Picoscope 5000a, 12 to 16 bit resolution
        self.offset = 0        # [V] Offset voltage
        self.enabled = True    # hannel enabled or not
        self.coupling = "DC"   # Oscilloscope coupling mode
        self.bwl = 0           # Bandwidth limit

    def v_max(self):
        """[V] Find allowed voltage range from requested range."""
        vm = find_scale(self.v_range)
        return vm

    def channel_name(self):
        """Return Picoscope channel name (A,B, ...) from number (0,1, ...)."""
        return channel_no_to_name(self.no)

    def coupling_code(self):
        """Return Picoscope coupling code from specified name."""
        return picoscope.PS5000A_COUPLING[f"PS5000A_{self.coupling}"]

    def adc_range(self):
        """Return Picoscope range code from specified voltage."""
        if self.v_max() < 1:
            adc_range_name = f"PS5000A_{int(self.v_max()*1000)}MV"
        else:
            adc_range_name = f"PS5000A_{int(self.v_max())}V"
        return picoscope.PS5000A_RANGE[adc_range_name]


class Trigger:
    """Osciloscope trigger settings and status."""

    source = "A"
    enable = True
    level = 0.5           # [V]
    direction = "Rising"
    position = 0.0        # Trigger position in % of trace length
    delay = 0             # [s]
    autodelay = 10e-3     # [s]
    adc_max = 0           # Meaningless value, will be imported later


class Horizontal:
    """Osciloscope horizontal (time) scale settings status."""

    timebase = 3       # Oscilloscope internal timebase no
    n_samples = 1000   # Number of samples
    dt = 8e-9          # [s] Sample interval
    pretrigger = 0     # [%] Samples before trigger

    def fs(self):
        """Return Picoscope samplig rate [S/s]."""
        return 1/self.dt

    def n_pretrigger(self):
        """Return number of samples before trigger."""
        return int(self.n_samples * self.pretrigger)

    def n_posttrigger(self):
        """Return number of samples after trigger."""
        return int(self.n_samples - self.n_pretrigger())

    def t0(self):
        """Return start time, i.e., time of first sample."""
        return -self.n_pretrigger() * self.dt

    def t_max(self):
        """Return end time, i.e., time of last sample.

        Note thet this is not the trace duration, but referred to the trigger
        time. The start time may be negative
        """
        return (self.n_samples - self.n_pretrigger() - 1) * self.dt


class Communication:
    """c-type variables for calling c-style functions in DLLs from Pico SDK."""

    connected = False
    status = {}
    handle = ctypes.c_int16(0)
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
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


def open_adc(dso, status):
    """Open connection to oscilloscope.

    Resolution is fixed to 15 bit and 2-channels
    """
    resolution = picoscope.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_15BIT"]
    status["openunit"] = picoscope.ps5000aOpenUnit(ctypes.byref(dso.handle),
                                                   None,
                                                   resolution)
    try:
        assert_pico_ok(status["openunit"])
    except:  # PicoNotOkError:
        power_status = status["openunit"]
        if power_status in [
                picoscope.PICO_STATUS["PICO_POWER_SUPPLY_NOT_CONNECTED"],
                picoscope.PICO_STATUS["PICO_USB3_0_DEVICE_NON_USB3_0_PORT"]
                ]:
            status["changePowerSource"] = picoscope.ps5000aChangePowerSource(
                                                    dso.handle,
                                                    power_status)
        else:
            raise

        assert_pico_ok(status["changePowerSource"])
        status["maximumValue"] = picoscope.ps5000aMaximumValue(
                                                dso.handle,
                                                ctypes.byref(dso.max_adc))
        assert_pico_ok(status["maximumValue"])
        dso.connected = ((status["changePowerSource"] == 0)
                         and (status["maximumValue"] == 0))
    return status, dso


def stop_adc(dso, status):
    """Stop oscilloscope. Only applicable when in streaming mode."""
    status["stop"] = picoscope.ps5000aStop(dso.handle)
    assert_pico_ok(status["stop"])
    return status


def close_adc(dso, status):
    """Close connection to ocsiloscope."""
    status["close"] = picoscope.ps5000aCloseUnit(dso.handle)
    assert_pico_ok(status["close"])
    return status


def set_vertical(dso, status, channel):
    """Set vertical scale in oscilloscope (Voltage range)."""
    name = channel_no_to_name(channel.no)
    status_name = f"setCh{name}"
    status[status_name] = picoscope.ps5000aSetChannel(
        dso.handle,
        channel.no,
        channel.enabled,
        channel.coupling_code(),
        channel.adc_range(),
        channel.offset)
    assert_pico_ok(status[status_name])
    return status


def set_trigger(dso, status, trigger, channel, sampling):
    """Configure oscilloscope trigger."""
    enable = int(trigger.enable)
    if trigger.source == "EXT":
        source = picoscope.PS5000A_CHANNEL["PS5000A_EXTERNAL"]
        relative_level = np.clip(trigger.level/5.0, -1, 1)
        threshold = int(relative_level*trigger.adc_max)
    elif trigger.source in ("A", "B"):
        source = picoscope.PS5000A_CHANNEL[f"PS5000A_CHANNEL_{trigger.source}"]
        ch_no = channel_name_to_no(trigger.source)
        relative_level = np.clip(trigger.level/channel[ch_no].v_max(), -1, 1)
        threshold = int(relative_level*channel[ch_no].adc_max)
    else:
        status["trigger"] = -1
        return status

    # Only the two basic trigger modes implemented: Rising or falling edge
    if trigger.direction.lower()[0:4] == 'fall':
        mode = 3   # Trigger mode "Falling"
    else:
        mode = 2   # Trigger mode "Rising"

    delay_pts = int(trigger.delay/sampling.dt)
    autotrigger_ms = ctypes.c_int16(int(trigger.autodelay*1e3))
    autotrigger_us = ctypes.c_uint64(int(trigger.autodelay*1e6))
    status["trigger"] = picoscope.ps5000aSetSimpleTrigger(dso.handle,
                                                          enable,
                                                          source,
                                                          threshold,
                                                          mode,
                                                          delay_pts,
                                                          autotrigger_ms)
    assert_pico_ok(status["trigger"])
    status["autoTrigger"] = picoscope.ps5000aSetAutoTriggerMicroSeconds(
                                                    dso.handle,
                                                    autotrigger_us)
    assert_pico_ok(status["autoTrigger"])
    return status


def get_trigger_time_offset(dso, status):
    """Read offset of last trigger."""
    segment_index = 0
    trigger_time = ctypes.c_int64(0)
    time_units = ctypes.c_int32(0)
    status["triggerTimeOffset"] = picoscope.ps5000aGetTriggerTimeOffset64(
                                                    dso.handle,
                                                    ctypes.byref(trigger_time),
                                                    ctypes.byref(time_units),
                                                    segment_index)
    assert_pico_ok(status["triggerTimeOffset"])
    trigger_time_offset = float(trigger_time.value)
    return trigger_time_offset


def get_sample_interval(dso, sampling):
    """Read  actual sample interval from osciloscope."""
    sample_interval_ns = ctypes.c_float(0)
    max_n_samples = ctypes.c_int32(0)
    ok = picoscope.ps5000aGetTimebase2(dso.handle,
                                       sampling.timebase,
                                       sampling.n_samples,
                                       ctypes.byref(sample_interval_ns),
                                       ctypes.byref(max_n_samples),
                                       0)
    assert_pico_ok(ok)
    sample_interval = sample_interval_ns.value*1e-9
    return sample_interval


def configure_acquisition(dso, status, sampling):
    """Configure acquisition of data from oscilloscope."""
    dso.max_samples.value = sampling.n_samples
    segment_index = 0
    downsample_mode = 0
    dso.buffer = []
    dso.buffer.append((ctypes.c_int16*sampling.n_samples)())
    dso.buffer.append((ctypes.c_int16*sampling.n_samples)())
    status_prefix = "setDataBuffers"
    # ch_status_names= ["A","B"]
    ch_no = 0
    for ch_name in CH_NAMES:
        status_name = status_prefix+ch_name
        status[status_name] = picoscope.ps5000aSetDataBuffer(
                                             dso.handle,
                                             ch_no,
                                             ctypes.byref(dso.buffer[ch_no]),
                                             sampling.n_samples,
                                             segment_index,
                                             downsample_mode)
        assert_pico_ok(status[status_name])
        ch_no += 1
    return status, dso


def acquire_trace(dso, status, sampling, ch):
    """Acuire voltage trace from oscilloscope."""
    start_index = 0
    downsample_ratio = 0
    downsample_mode = 0
    segment_index = 0
    status["runBlock"] = picoscope.ps5000aRunBlock(dso.handle,
                                                   sampling.n_pretrigger(),
                                                   sampling.n_posttrigger(),
                                                   sampling.timebase,
                                                   None,
                                                   segment_index,
                                                   None,
                                                   None)
    assert_pico_ok(status["runBlock"])

    # Check for data collection to finish
    # Primitive polling, consider replacing with ps5000aIsReady
    dso.ready.value = 0
    dso.check.value = 0
    while dso.ready.value == dso.check.value:
        status["isReady"] = picoscope.ps5000aIsReady(dso.handle,
                                                     ctypes.byref(dso.ready))
        time.sleep(0.01)

    # Transfer data values
    status["getValues"] = picoscope.ps5000aGetValues(
                                         dso.handle,
                                         start_index,
                                         ctypes.byref(dso.max_samples),
                                         downsample_ratio,
                                         downsample_mode,
                                         segment_index,
                                         ctypes.byref(dso.overflow))
    assert_pico_ok(status["getValues"])

    # Convert ADC counts data to Volts
    n_channels = len(ch)
    v_mv = np.zeros([sampling.n_samples, n_channels])
    for ch_no in range(n_channels):
        v_mv[:, ch_no] = adc2mV(dso.buffer[ch_no],
                                ch[ch_no].adc_range(),
                                dso.max_adc)
    v = 1e-3*v_mv  # np.column_stack([mv_a, mv_b])
    return status, dso, v


def set_signal(dso, status, sampling, pulse):
    """Send pulse to arbitrary waveform generator."""
    if pulse.on:
        amplitude = min(pulse.a, DAC_MAX_AMPLITUDE)
    else:
        amplitude = 0
    status["sigGenArbMinMax"] = picoscope.ps5000aSigGenArbitraryMinMaxValues(
                                            dso.handle,
                                            ctypes.byref(dso.awg_min_value),
                                            ctypes.byref(dso.awg_max_value),
                                            ctypes.byref(dso.awg_min_length),
                                            ctypes.byref(dso.awg_max_length))
    assert_pico_ok(status["sigGenArbMinMax"])

    # Scale pulse for awg buffer
    y_scaled = pulse.y()/pulse.a*dso.awg_max_value
    pulsedata = y_scaled.astype(ctypes.c_int16)
    buffer_length = ctypes.c_uint32(len(pulsedata))
    index_mode = ctypes.c_int32(0)
    delta_phase = ctypes.c_uint32(0)
    status["freqToPhase"] = picoscope.ps5000aSigGenFrequencyToPhase(
                                                dso.handle,
                                                1/pulse.duration(),
                                                index_mode,
                                                buffer_length,
                                                ctypes.byref(delta_phase))
    assert_pico_ok(status["freqToPhase"])

    """
    Settings not in use
    Values passed as c-type variables, type casting not checked for all
    See documentation in Programmer's Guide.
    """
    offset_voltage_uv = ctypes.c_int32(0)
    pp_voltage_uv = ctypes.c_uint32(int(2*amplitude*1e6))  # Peak-to-peak, uV
    trigger_type = ctypes.c_int32(0)
    trigger_source = ctypes.c_int32(pulse.trigger_source)
    shots = ctypes.c_uint32(1)

    # Parameters not used
    delta_phase_increment = ctypes.c_uint32(0)
    dwell_count = ctypes.c_uint32(0)
    sweep_type = ctypes.c_int32(0)
    operation = ctypes.c_int32(0)
    sweeps = ctypes.c_uint32(0)
    ext_in_threshold = ctypes.c_int16(0)
    waveform_length = ctypes.c_int32(len(pulsedata))
    waveform_pointer = pulsedata.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))
    status["setSigGenArbitrary"] = picoscope.ps5000aSetSigGenArbitrary(
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
    assert_pico_ok(status["setSigGenArbitrary"])
    return status


# %% Utility functions

def channel_no_to_name(no):
    """Convert number to Picoscope channel name (A, B, ...)."""
    return chr(ord("A")+no)


def channel_name_to_no(name):
    """Convert Picoscope channel name (A, B, ...) to number."""
    return ord(name)-ord("A")


def find_scale(x):
    """Find next number in an 1-2-5-10-20 ... sequence.

    This sequence matches the oscilloscope ranges.
    """
    if x <= 10e-3:
        xn = 10e-3
    elif x >= 50:
        xn = 50
    else:
        prefixes = np.array([1, 2, 5, 10])
        exp = int(np.floor(np.log10(abs(x))))
        mant = abs(x) / (10**exp)
        valid = np.where(prefixes >= mant-0.001)
        mn = np.min(prefixes[valid])
        xn = mn*10**exp
    return xn
