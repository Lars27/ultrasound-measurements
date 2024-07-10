'''
Acquire ultrasound data from Picoscope 5000
Wrappers for c-style function calls to DLLs

Based on example program from Picotech
  PS5000A BLOCK MODE EXAMPLE, # Copyright (C) 2018-2022 Pico Technology Ltd. 
  See LICENSE file for terms.
    
Reference 
  PicoScope 5000 Series (A API) - Programmer's Guide. Pico Tecknology Ltd, 2018
    
Wraps c-style commands (ctypes.xx) to standard Python variables and sets 
scaling constants, ranges etc. spscific for the instrument.

The classes and functions in this file shall provide an easy interface to 
Picoscope 5000a from any standard Pyton environment

Lars Hoff, USN, Sep 2022
        Modified June 2024 to better follow PEP-8 style guide


=== UNTESTED =====================================================

'''

import time
import ctypes
import numpy as np
from picosdk.ps5000a import ps5000a as picoscope
from picosdk.functions import adc2mV, assert_pico_ok #, mV2adc


#%% Classes
    
class Status:
    '''
    Instrument connection status monitoring
    '''
    handle = ctypes.c_int16()
    connected = False        
    status = {}    
     
     
class Channel:
    '''
    Osciloscope vertical (voltage) channel settings and status
    '''     
    def __init__(self, no ):
        self.no = no

    v_range = 1       # [V] Requested full scale voltage
    adc_max = 32767   #     Picoscope 5000a, 12 to 16 bit resolution. Incorrcet for 8 bit
    offset = 0        # [V] Offset voltage
    enabled = True    #     Channel enabled or not
    coupling = "DC"   #     Oscilloscope coupling mode
    bwl = 0           #     Bandwidth limit
        
    def v_max(self):     # [V] Find allowed voltage range from requested range
        vm=find_scale(self.v_range)
        if vm <= 10e-3:
            vm = 10e-3
        if vm>50:
            vm = 50
        return vm   

    def name(self):             
        return channel_no_to_name(self.no)
         
    def coupling_code(self):
        return  picoscope.PS5000A_COUPLING[f"PS5000A_{self.coupling}"]
                
    def adc_range(self):
        if self.v_max()<1:
            adc_range_name= f"PS5000A_{int(self.v_max()*1000)}MV"           
        else:
            adc_range_name= f"PS5000A_{int(self.v_max())}V"                              
        return picoscope.PS5000A_RANGE[adc_range_name]


class Trigger:
    '''
    Osciloscope trigger settings and status
    '''        
    source = "A"
    enable = True
    level = 0.5       # [V]
    direction = "Rising"
    position = 0.0    # Trigger position in % of trace length
    delay = 0         # [s]
    autodelay = 1e-3  # [s]
    internal = 0      # Internal or external trigger
    adc_max = 0       # Meaningless value, will be imported later


class Horizontal:
    '''
    Osciloscope horizontal (time) scale settings status 
    '''         
    timebase = 3       #     Oscilloscope internal timebase no
    n_samples = 1000   #     Number of samples
    dt = 8e-9          # [s] Sample interval
    pretrigger = 0     # [%] Samples before trigger
    
    def fs(self):      # [S/s] Sample rate
        return 1/self.dt
    
    def n_pretrigger(self):   # No. of samples before trigger
        return int(self.n_samples * self.pretrigger)
    
    def n_posttrigger(self):  # No. of samples after trigger
        return int(self.n_samples - self.n_pretrigger())
    
    def t0(self):             # Time of first sample 
        return -self.n_pretrigger() * self.dt    
    
    def t_max(self):          # Time of last sample
        return (self.n_samples - self.n_pretrigger() - 1) * self.dt    


class Communication:
    '''
    Communications with osciloscope 
    c-type variables for calling c-style functions from DLLs in Pico SDK
    '''
    connected = False  
    status = {}    
    handle = ctypes.c_int16(0)
    max_adc = ctypes.c_int16(0)   
    overflow = ctypes.c_int16(0)
    max_samples = ctypes.c_int32(0)  
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    channel = 'A'
    buffer_a = ( ctypes.c_int16 * 10 )()
    buffer_b = ( ctypes.c_int16 * 10 )() 
      
    
#%% 
'''
Wrappers for original c-style library functions
Instrument is controlled from Python using the function calls listed below
Data are exchanged using the classes defined above
'''


def open_adc(dso, status):    
    ''' 
    Open connection to oscilloscope. Resolution fixed to 15 bit, 2-channels  
    '''
    resolution =picoscope.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_15BIT"]   
    status["openunit"] = picoscope.ps5000aOpenUnit(ctypes.byref(dso.handle), 
                                                   None, resolution)
    try:
        assert_pico_ok(status["openunit"])
    except: # PicoNotOkError:
        power_status = status["openunit"]
        if power_status in [282, 286]:
            status["changePowerSource"] = picoscope.ps5000aChangePowerSource(
                dso.handle, power_status)
        else:
            raise

        assert_pico_ok(status["changePowerSource"])
        
        status["maximumValue"] = picoscope.ps5000aMaximumValue(
            dso.handle, ctypes.byref(dso.max_adc))
        
        assert_pico_ok(status["maximumValue"])        
    
    return status, dso


def stop_adc(dso, status):
    ''' 
    Stop oscilloscope. Only applicable when in streaming mode 
    '''
    status["stop"] = picoscope.ps5000aStop(dso.handle)
    assert_pico_ok(status["stop"])
    
    return status


def close_adc(dso, status):
    ''' 
    Close connection to ocsiloscope 
    '''
    status["close"] = picoscope.ps5000aCloseUnit(dso.handle)
    assert_pico_ok(status["close"])
        
    return status


def set_vertical(dso, status, ch):
    '''
    Set vertical scale in oscilloscope (Voltage range)
    '''
    name= channel_no_to_name(ch.no)
    status_name = f"setCh{name}"  
        
    status[status_name] = picoscope.ps5000aSetChannel(
        dso.handle, ch.no, ch.enabled, ch.coupling_code(), ch.adc_range(), ch.offset)
    assert_pico_ok(status[status_name])    
    
    return status 


def set_trigger(dso, status, trigger, ch, sampling):
    '''
    Configure trigger
    '''
    if trigger.source=="EXT":
        source = picoscope.PS5000A_CHANNEL["PS5000A_EXTERNAL"]
        relative_level = np.clip(trigger.level / 5.0, -1, 1)
        threshold = int(relative_level * trigger.adc_max)
    elif trigger.source in ("A", "B"):
        source = picoscope.PS5000A_CHANNEL[f"PS5000A_CHANNEL_{trigger.source}"]
        no = channel_name_to_no(trigger.source)
        relative_level = np.clip( trigger.level / ch[no].v_max(), -1, 1)       
        threshold = int( relative_level * ch[no].adc_max )
    else:
        status["trigger"] = -1
        return status

    # Only the two basic trigger modes implemented: Rising or falling edge
    if trigger.direction.lower()[0:4] == 'fall':  
        mode = 3   # Trigger mode "Falling"          
    else:
        mode = 2   # Trigger mode "Rising"
        
    enable = int( trigger.enable )
    delay_pts = int( trigger.delay/sampling.dt )
    autodelay_ms = int( trigger.autodelay * 1e3 )
         
    status["trigger"] = picoscope.ps5000aSetSimpleTrigger(
        dso.handle, enable, source, threshold, mode, delay_pts, autodelay_ms)
    assert_pico_ok( status["trigger"] )
    return status


def get_dt(dso, sampling):
    '''
    Get actual sample interval from osciloscope
    '''
    timeIntervalns = ctypes.c_float()
    returnedMaxSamples = ctypes.c_int32()
    
    ok = picoscope.ps5000aGetTimebase2(
        dso.handle, sampling.timebase, sampling.n_samples, 
        ctypes.byref(timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
    assert_pico_ok(ok)
   
    sample_interval =  timeIntervalns.value * 1e-9    
    return sample_interval 


def configure_acquisition(dso, status, sampling):
    '''
    Configure acquisition of data from oscilloscope
    '''    
    dso.max_samples.value = sampling.n_samples
    dso.buffer_a = (ctypes.c_int16 *sampling.n_samples)()
    dso.buffer_b = (ctypes.c_int16 *sampling.n_samples)()

    status["setDataBuffersA"] = picoscope.ps5000aSetDataBuffer(
        dso.handle, 0, ctypes.byref( dso.buffer_a ), sampling.n_samples, 0, 0)
    assert_pico_ok(status["setDataBuffersA"])
    status[ "setDataBuffersB" ] = picoscope.ps5000aSetDataBuffer(
        dso.handle, 1, ctypes.byref( dso.buffer_b ), sampling.n_samples, 0, 0)
    assert_pico_ok( status[ "setDataBuffersB" ] )

    return status, dso
    

def acquire_trace(dso, status, sampling, ch):
    '''
    Acuire voltage trace from oscilloscope
    '''
    status["runBlock"] = picoscope.ps5000aRunBlock(
        dso.handle, sampling.n_pretrigger(), sampling.n_posttrigger(), 
        sampling.timebase, None, 0, None, None)
    assert_pico_ok(status["runBlock"])

    # Check for data collection to finish using ps5000aIsReady
    # Primitive polling, consider replacing with ps5000aIsReady 
    dso.ready.value = 0
    dso.check.value = 0
    while dso.ready.value == dso.check.value:
        status["isReady"] = picoscope.ps5000aIsReady(
            dso.handle, ctypes.byref(dso.ready))
        time.sleep(0.01)

    # Transfer data values
    status["getValues"] = picoscope.ps5000aGetValues(
        dso.handle, 0, ctypes.byref(dso.max_samples), 0, 0, 0, 
        ctypes.byref( dso.overflow))
    assert_pico_ok(status["getValues"])
    
    # Convert ADC counts data to Volts
    mv_a = adc2mV( dso.buffer_a, ch[0].adc_range(), dso.max_adc)
    mv_b = adc2mV( dso.buffer_b, ch[1].adc_range(), dso.max_adc)
    
    v = 1e-3*np.column_stack( [mv_a, mv_b] )    

    return status, dso, v


def set_signal(dso, status, sampling, pulse):  
    '''
    Send pulse to arbitrary waveform generator 
    UNTESTED
    '''
    vpp_uV = ctypes.c_uint32(int(2*pulse.a))
    ns     = ctypes.c_int32(pulse.ns())
    triggersource = 1     # Use scope trigger, always
    
    awgBuffer = pulse.x()
    awgbufferPointer = awgBuffer.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))

    status["setSigGenArbitrary"] = picoscope.ps5000aSetSigGenArbitrary(
        dso.handle, 0, vpp_uV, 0, 0, 0, 0, 
        awgbufferPointer, ns, 0, 0, 0, 0, 0, 0, triggersource, 0)
    assert_pico_ok(status["setSigGenArbitrary"])
    
    return status

#%% Utility functions

def channel_no_to_name(no):
    '''
    Convert number to Picoscope channel name ('A', 'B', etc. ) 
    '''
    return chr( ord("A")+no )


def channel_name_to_no(name):
    '''
    Convert Picoscope channel name ('A', 'B', etc. ) to number 
    '''
    return ord(name)-ord("A")


def find_scale(x):
    '''
    Find next number in an 1-2-5-10-20 ... sequence, selected to match 
    oscilloscope ranges
    '''
    prefixes = np.array([1, 2, 5, 10])
    exp = int(np.floor(np.log10(abs(x))))    
    mant= abs(x) / (10**exp)    
    valid = np.where(prefixes >= mant-0.001)
    mn = np.min(prefixes[valid])    
    xn = mn*10**exp    
        
    return xn