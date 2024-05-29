'''
Acquire ultrasound data from Picoscope 5000
Wrappers for c-style function calls to DLLs

Based on example program from Picotech: 
    PS5000A BLOCK MODE EXAMPLE, # Copyright (C) 2018-2022 Pico Technology Ltd. See LICENSE file for terms.
 
    Ref: PicoScope 5000 Series (A API) - Programmer's Guide. Pico Tecknology Ltd, 2018
    
Lars Hoff, USN, Sep 2022
'''

import time
import ctypes
import numpy as np
from picosdk.ps5000a import ps5000a as picoscope
from picosdk.functions import adc2mV, assert_pico_ok #, mV2adc
import us_utilities as us

#%% Classes
    
'''
Instrument connection status
'''
class status:
     handle = ctypes.c_int16()
     connected = False
     status = {}    
     
'''
Osciloscope vertical (vlotage) channel settings and status
'''     
class channel:    # Digital oscilloscope vertical settings (Volts)
    def __init__(self, no ):
        self.no    = no

    vr      = 1 
    adcmax  = 32767  # Fixed in Picoscope 5000a for 12 to 16 bit resolution, incorrcet for 8 bit
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
        return channel_no_to_name(self.no)
         
    def coupling_code(self):
        return  picoscope.PS5000A_COUPLING[f"PS5000A_{self.coupling}"]
                
    def adcrange(self):
        if self.vmax()<1:
            adcrangename= f"PS5000A_{int(self.vmax()*1000)}MV"           
        else:
            adcrangename= f"PS5000A_{int(self.vmax())}V"                              
        return picoscope.PS5000A_RANGE[adcrangename]

'''
Osciloscope trigger settings and status
'''        
class trigger:   # Digital oscilloscope trigger settings
    source      = "A"
    enable      = True
    level       = 0.5
    direction   = "Rising"
    position    = 0.0
    delay       = 0
    autodelay   = 1e-3     
    internal    = 0
    adcmax      = 0         # Meaningless value, placeholder

'''
Osciloscope horisontal (time) scale settings status 
'''         
class horizontal:   # Digital oscilloscope horizontal settings (Time)
    timebase = 3
    ns   = 1000
    dt   = 8e-9
    #nmax = 1000
    pretrigger = 0
    
    def fs ( self ):
        return 1/self.dt
    def npre ( self ):
        return int(self.ns*self.pretrigger)
    def npost ( self ):
        return int( self.ns - self.npre() )
    def t0 ( self ):
        return -self.npre() * self.dt    
    def tmax ( self ):
        return ( self.ns - self.npre() -1 ) *self.dt    

'''
Communications with osciloscope 
c-type variables for calling c-style functions in DLLs
'''
class communication:
    connected   = False  
    status      = {}    
    handle      = ctypes.c_int16(0)
    maxADC      = ctypes.c_int16(0)   
    overflow    = ctypes.c_int16(0)
    maxSamples  = ctypes.c_int32(0)  
    ready       = ctypes.c_int16(0)
    check       = ctypes.c_int16(0)
    ch          = 'A'
    bufferA      = ( ctypes.c_int16 * 10 )()    # Buffer for Picoscope data, could not make this a method
    bufferB      = ( ctypes.c_int16 * 10 )()    # Buffer for Picoscope data, could not make this a method
      
    
#%% 
'''
Wrappers for original c-style library functions
Instrument is controlled from Python using the funsction calls listed below
Data are exchanged using the classes defined above
'''

''' Open connection to oscilloscope '''
def open_adc(dso, status):    
    resolution =picoscope.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_15BIT"]   # Resolution fixed to 15 bit for 2-channel acquisition
    status["openunit"] = picoscope.ps5000aOpenUnit(ctypes.byref(dso.handle), None, resolution)
    try:
        assert_pico_ok(status["openunit"])
    except: # PicoNotOkError:
        powerStatus = status["openunit"]
        if powerStatus == 286:
            status["changePowerSource"] = picoscope.ps5000aChangePowerSource(dso.handle, powerStatus)
        elif powerStatus == 282:
            status["changePowerSource"] = picoscope.ps5000aChangePowerSource(dso.handle, powerStatus)
        else:
            raise

        assert_pico_ok(status["changePowerSource"])
        
        status["maximumValue"] = picoscope.ps5000aMaximumValue(dso.handle, ctypes.byref(dso.maxADC))
        assert_pico_ok(status["maximumValue"])        
    
    return status, dso

''' Stop oscilloscope. Only applicable when in streaming mode '''
def stop_adc(dsohandle, status):
    status["stop"] = picoscope.ps5000aStop(dsohandle)
    assert_pico_ok(status["stop"])
    
    return status

''' Close connection to ocsiloscope '''
def close_adc(dsohandle, status):
    status["close"]=picoscope.ps5000aCloseUnit(dsohandle)
    assert_pico_ok(status["close"])
        
    return status

''' Set vertical scale in oscilloscope (Voltage range) '''
def set_vertical( dsohandle, status, ch ):
    name= channel_no_to_name(ch.no)
    statusname = f"setCh{name}"  
        
    status[statusname ] = picoscope.ps5000aSetChannel( dsohandle, ch.no, ch.enabled, ch.coupling_code() , ch.adcrange(), ch.offset )
    assert_pico_ok( status[ statusname ] )    
    
    return status 

''' Configure trigger '''
def set_trigger(dsohandle, status, trigger, ch, sampling ):
    if trigger.source=="EXT":
        source = picoscope.PS5000A_CHANNEL["PS5000A_EXTERNAL"]
        vrel   = np.clip( trigger.level / 5.0, -1, 1)
        threshold = int( trigger.level/5.0 * trigger.adcmax )
    elif trigger.source in ("A", "B"):
        source = picoscope.PS5000A_CHANNEL[f"PS5000A_CHANNEL_{trigger.source}"]
        no   = channel_name_to_no(trigger.source)
        vrel = np.clip( trigger.level / ch[no].vmax(), -1, 1)       
        threshold = int( vrel * ch[no].adcmax )
    else:
        status["trigger"]=-1
        return status
    
    if trigger.direction.lower()[0:4] == 'fall':  # Trigger mode "Falling"
        mode = 3
    else:
        mode = 2                           # Trigger mode "Rising"
        
    enable       = int( trigger.enable )
    delay_pts    = int( trigger.delay/sampling.dt )
    autodelay_ms = int( trigger.autodelay * 1e3 )
         
    status["trigger"] = picoscope.ps5000aSetSimpleTrigger( dsohandle, enable, source, threshold, mode, delay_pts, autodelay_ms )
    assert_pico_ok( status["trigger"] )
    return status

''' Get actual sample interval from osciloscope '''
def get_dt(dsohandle, sampling):
    timeIntervalns = ctypes.c_float()
    returnedMaxSamples = ctypes.c_int32()
    
    ok = picoscope.ps5000aGetTimebase2(dsohandle, sampling.timebase, sampling.ns, ctypes.byref(timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
    ok = picoscope.ps5000aGetTimebase2(dsohandle, sampling.timebase, sampling.ns, ctypes.byref(timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
    assert_pico_ok(ok)
   
    return timeIntervalns.value*1e-9

''' Configure acquisition of data from oscilloscope '''    
def configure_acquisition( dso, status, sampling ):
    dso.maxSamples.value  = sampling.ns
    dso.bufferA           = ( ctypes.c_int16 *sampling.ns )()
    dso.bufferB           = ( ctypes.c_int16 *sampling.ns )()

    status[ "setDataBuffersA" ] = picoscope.ps5000aSetDataBuffer( dso.handle, 0, ctypes.byref( dso.bufferA ), sampling.ns, 0, 0)
    assert_pico_ok( status[ "setDataBuffersA" ] )
    status[ "setDataBuffersB" ] = picoscope.ps5000aSetDataBuffer( dso.handle, 1, ctypes.byref( dso.bufferB ), sampling.ns, 0, 0)
    assert_pico_ok( status[ "setDataBuffersB" ] )

    return status, dso
    
''' Acuire voltage trace from oscilloscope '''
def acquire_trace( dso, status, sampling, ch ):
    status["runBlock"] = picoscope.ps5000aRunBlock( dso.handle, sampling.npre(), sampling.npost(), sampling.timebase, None, 0, None, None)
    assert_pico_ok(status["runBlock"])

    # Check for data collection to finish using ps5000aIsReady
    dso.ready.value = 0
    dso.check.value = 0
    while dso.ready.value == dso.check.value:
        status["isReady"] = picoscope.ps5000aIsReady( dso.handle, ctypes.byref( dso.ready ) )
        time.sleep(0.01)

    # Transfer data values
    status["getValues"] = picoscope.ps5000aGetValues(dso.handle, 0, ctypes.byref( dso.maxSamples ), 0, 0, 0, ctypes.byref( dso.overflow ) )
    assert_pico_ok(status["getValues"])
    
    # Convert ADC counts data to Volts
    mV_a =  adc2mV( dso.bufferA, ch[0].adcrange(), dso.maxADC )
    mV_b =  adc2mV( dso.bufferB, ch[1].adcrange(), dso.maxADC )
    
    v = 1e-3*np.column_stack( [mV_a, mV_b] )    

    return status, dso, v

''' Send pulse to arbitrary waveform generator '''
def set_signal ( dso, status, sampling, pulse ):    # Send signal to arbitrary waveform generator
    vpp_uV = ctypes.c_uint32( int(2*pulse.a) )
    ns     = ctypes.c_int32 ( pulse.ns() )
    triggersource = 1     # Use scope trigger, always
    
    awgBuffer = pulse.x()
    awgbufferPointer = awgBuffer.ctypes.data_as(ctypes.POINTER(ctypes.c_int16))

    status["setSigGenArbitrary"] = picoscope.ps5000aSetSigGenArbitrary(dso.handle, 0, vpp_uV, 0, 0, 0, 0, awgbufferPointer, ns, 0, 0, 0, 0, 0, 0, triggersource, 0)
    assert_pico_ok(status["setSigGenArbitrary"])
    
    return status

''' Utility functions '''
def channel_no_to_name(no):
    return chr( ord("A")+no )

def channel_name_to_no(name):
    return ord(name)-ord("A")
    





