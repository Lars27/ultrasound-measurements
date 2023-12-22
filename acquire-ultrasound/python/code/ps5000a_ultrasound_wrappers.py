# Acquire ultrasound data from Picoscope 5000
#
#
# Based on PS5000A BLOCK MODE EXAMPLE, # Copyright (C) 2018-2022 Pico Technology Ltd. See LICENSE file for terms.
# 
# Lars Hoff, USN, Sep 2022

import time
import ctypes
import numpy as np
from picosdk.ps5000a import ps5000a as ps
from picosdk.functions import adc2mV, assert_pico_ok #, mV2adc
import us_utilities as us

#%% Classes
    
class dso_status:
     handle = ctypes.c_int16()
     connected = False
    
class dso_channel:    # Digital oscilloscope vertical settings (Volts)
    def __init__(self, no ):
        self.no    = no

    vr      = 1 
    adcmax  = 2**14    
    offset  = 0
    enabled = True
    coupling= "DC"
    bwl     = 0
        
    def vmax(self):
        vm=us.scale125(self.vr)
        if vm <= 10e-3:
            vm = 10e-3
        if vm>50:
            vm = 50
        return vm
    

    def name(self):
        channel_name= channel_no_to_name(self.no)
        return f"Channel {channel_name}"
    
        
    def coupling_code(self):
        return  ps.PS5000A_COUPLING[f"PS5000A_{self.coupling}"]
                
    def adcrange(self):
        if self.vmax()<1:
            adcrangename= f"PS5000A_{int(self.vmax()*1000)}MV"           
        else:
            adcrangename= f"PS5000A_{int(self.vmax())}V"           
                   
        return ps.PS5000A_RANGE[adcrangename]

    
class dso_trigger:   # Digital oscilloscope trigger settings
    source      = "A"
    enable      = True
    level       = 0.5
    direction   = "Rising"
    position    = 0.0
    delay       = 0
    autodelay   = 3000     
    internal    = 0

    
class dso_horizontal:   # Digital oscilloscope horizontal settings (Time)
    timebase = 3
    ns   = 1000
    dt   = 8e-9
    #nmax = 1000
    pretrigger = 0
    
    def npre ( self ):
        return int(self.ns*self.pretrigger)
    def npost ( self ):
        return int( self.ns - self.npre() )
    def t0 ( self ):
        return -self.npre() * self.dt    
    def tmax ( self ):
        return ( self.ns - self.npre() -1 ) *self.dt    
    
#%% Functions    
# =============================================================================
#     def dt(dso_handle, self):
#         timeIntervalns = ctypes.c_float()
#         returnedMaxSamples = ctypes.c_int32()
#         
#         ok= ps.ps5000aGetTimebase2(dso_handle, self.timebase, self.Ns, ctypes.byref(timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
#         assert_pico_ok(ok)
#         
#         return timeIntervalns.value*1e-9
# 
# =============================================================================

# Wrappers for original c-style library functions   
def set_trigger(dsohandle, status, trigger, ch):
    if trigger.source=="EXT":
        source = ps.PS5000A_CHANNEL["PS5000A_EXTERNAL"]
        threshold = int(trigger.level/5.0*32767)
    elif trigger.source in ("A", "B"):
        source = ps.PS5000A_CHANNEL[f"PS5000A_CHANNEL_{trigger.source}"]
        no  = channel_name_to_no(trigger.source)
        ref = ch[no].vmax()
        threshold = int(trigger.level/ref*trigger.adcmax)
    else:
        status["trigger"]=-1
        return status
    
    if trigger.direction.lower()[0:4] == 'fall':  # Trigger mode "Falling"
        mode = 3
    else:
        mode= 2                           # Trigger mode "Rising"
           
    status["trigger"] = ps.ps5000aSetSimpleTrigger(dsohandle, int(trigger.enable), source, threshold, mode, trigger.delay, trigger.autodelay )
    assert_pico_ok(status["trigger"])
    
    return status


def get_dt(dsohandle, sampling):
    timeIntervalns = ctypes.c_float()
    returnedMaxSamples = ctypes.c_int32()
    
    ok = ps.ps5000aGetTimebase2(dsohandle, sampling.timebase, sampling.ns, ctypes.byref(timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
    ok = ps.ps5000aGetTimebase2(dsohandle, sampling.timebase, sampling.ns, ctypes.byref(timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
    assert_pico_ok(ok)
   
    return timeIntervalns.value*1e-9


def set_vertical(dsohandle,status, ch):
    name= channel_no_to_name(ch.no)
    statusname = f"setCh{name}"  
        
    status[statusname ] = ps.ps5000aSetChannel(dsohandle, ch.no, ch.enabled, ch.coupling_code() , ch.adcrange(), ch.offset)
    assert_pico_ok(status[statusname ])    
    
    return status, ch
    

def open_adc(dsohandle, status):    
    resolution =ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_15BIT"]
    status["openunit"] = ps.ps5000aOpenUnit(ctypes.byref(dsohandle), None, resolution)
    try:
        assert_pico_ok(status["openunit"])
    except: # PicoNotOkError:
        powerStatus = status["openunit"]
        if powerStatus == 286:
            status["changePowerSource"] = ps.ps5000aChangePowerSource(dsohandle, powerStatus)
        elif powerStatus == 282:
            status["changePowerSource"] = ps.ps5000aChangePowerSource(dsohandle, powerStatus)
        else:
            raise

        assert_pico_ok(status["changePowerSource"])
        
        maxADC = ctypes.c_int16()
        status["maximumValue"] = ps.ps5000aMaximumValue(dsohandle, ctypes.byref(maxADC))
        assert_pico_ok(status["maximumValue"])
        
        adc_max = maxADC.value
    
    return status, adc_max


def acquire_trace(dsohandle, status, sampling, ch):
    maxADC = ctypes.c_int16()
    maxADC.value= ch.adcmax     # Convert to c-tyoe object to use in function call
    
    overflow = ctypes.c_int16()
    cmaxSamples = ctypes.c_int32(sampling.ns)
    
    name = channel_no_to_name(ch.no)    
    source = ps.PS5000A_CHANNEL[f"PS5000A_CHANNEL_{name}"]
    statusname = f"setDataBuffers{name}"

    status["runBlock"] = ps.ps5000aRunBlock(dsohandle, sampling.npre(), sampling.npost(), sampling.timebase, None, 0, None, None)
    assert_pico_ok(status["runBlock"])

    # Check for data collection to finish using ps5000aIsReady
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status["isReady"] = ps.ps5000aIsReady(dsohandle, ctypes.byref(ready))
        time.sleep(0.01)

    # Create buffers ready for assigning pointers for data collection
    buffer = (ctypes.c_int16 * sampling.ns)()
    status[statusname] = ps.ps5000aSetDataBuffer(dsohandle, source, ctypes.byref(buffer), sampling.ns, 0, 0)
    assert_pico_ok(status[statusname])
    
    status["getValues"] = ps.ps5000aGetValues(dsohandle, 0, ctypes.byref(cmaxSamples), 0, 0, 0, ctypes.byref(overflow))
    assert_pico_ok(status["getValues"])
    n_recorded = cmaxSamples.value

    # convert ADC counts data to mV
    mV =  adc2mV(buffer, ch.adcrange(), maxADC)
    v  =  1e-3*np.array(mV)

    return status, v, n_recorded


def stop_adc(dsohandle, status):
    status["stop"] = ps.ps5000aStop(dsohandle)
    assert_pico_ok(status["stop"])
    
    return status


def close_adc(dsohandle, status):
    status["close"]=ps.ps5000aCloseUnit(dsohandle)
    assert_pico_ok(status["close"])
        
    return status


def channel_no_to_name(no):
    return chr( ord("A")+no )


def channel_name_to_no(name):
    return ord(name)-ord("A")
    





