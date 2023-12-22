# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 11:57:49 2023

@author: lah
"""



import ps5000a_ultrasound_wrappers as ps

ch=[]
ch.append( ps.dso_channel ( 0 ) )
ch.append( ps.dso_channel ( 1 ) )

trigger  = ps.dso_trigger()            # Trigger configuration
sampling = ps.dso_horizontal()         # Horisontal configuration (time sampling)  

handle = ps.ctypes.c_int16()
status = {}
status, adcmax= ps.open_adc( handle, status )
status = ps.set_vertical( handle, status, ch[0])
status = ps.set_vertical( handle, status, ch[1])
status = ps.set_trigger( handle, status, trigger, ch, sampling )

status


