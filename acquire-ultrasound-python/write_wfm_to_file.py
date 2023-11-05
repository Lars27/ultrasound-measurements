# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 22:07:23 2022

@author: larsh
"""
import us_utilities as us
import numpy as np


srcname="US_2020_06_26_0240.wfm"
wfm=us.waveform(np.zeros((1000,2)), 1)
wfm.load(srcname)

hd= "<WFM_Python_>f4>"
n_hd=len(hd)

fid=open('testfile.xx', 'wb')
fid.write( np.array(n_hd).astype('>i4'))
fid.write( bytes(hd, 'utf-8'))
fid.write( np.array(wfm.nc).astype('>u4'))
fid.write( np.array(wfm.t0).astype('>f8'))
fid.write( np.array(wfm.dt).astype('>f8'))
fid.write( np.array(wfm.dtr).astype('>f8'))
fid.write( wfm.y.astype('>f4') )
fid.close()