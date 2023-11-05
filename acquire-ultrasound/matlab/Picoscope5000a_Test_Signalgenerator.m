%% Test program for Picoscope 5000 series signal generator as AWG
%
% Based on the example from Picotech
%
%% PicoScope 5000 Series (A API) Instrument Driver Oscilloscope Signal Generator Example
% Code for communicating with an instrument in order to control the
% signal generator.
%  
% This is a modified version of the machine generated representation of 
% an instrument control session using a device object. The instrument 
% control session comprises all the steps you are likely to take when 
% communicating with your instrument. These steps are:
%       
% # Create a device object   
% # Connect to the instrument 
% # Configure properties 
% # Invoke functions 
% # Disconnect from the instrument 
%  
% To run the instrument control session, type the name of the file,
% PS5000A_ID_Sig_Gen_Example, at the MATLAB command prompt.
% 
% The file, PS5000A_ID_SIG_GEN_EXAMPLE.M must be on your MATLAB PATH. For additional information
% on setting your MATLAB PATH, type 'help addpath' at the MATLAB command
% prompt.
%
% *Example:*
%   PS5000A_ID_Sig_Gen_Example;
%
% *Description:*
%     Demonstrates how to set properties and call functions in order to
%     control the signal generator output of a PicoScope 5000 Series
%     Oscilloscope/Mixed Signal Oscilloscope using the 'A' API library
%     functions.
%
% *See also:* <matlab:doc('icdevice') |icdevice|> | <matlab:doc('instrument/invoke') |invoke|>
%
% *Copyright:* © 2013-2018 Pico Technology Ltd. See LICENSE file for terms.

%% Test setup
% For this example the 'Gen' connector of the oscilloscope was connected to
% channel A on another PicoScope oscilloscope running the PicoScope 6
% software application. Images, where shown, depict output, or part of the
% output in the PicoScope 6 display.
%
% *Note:* The various signal generator functions called in this script may
% be combined with the functions used in the various data acquisition
% examples in order to output a signal and acquire data. The functions to
% setup the signal generator should be called prior to the start of data
% collection.

%% Clear command window and close any figures

clc;
close all;
instrreset

%% Connect signal generator
PS5000aConfig;
ps5000aDeviceObj = icdevice('picotech_ps5000a_generic.mdd');
connect(ps5000aDeviceObj);
sigGenGroupObj = get(ps5000aDeviceObj, 'Signalgenerator');
sigGenGroupObj = sigGenGroupObj(1);
awgBufferSize = get(sigGenGroupObj, 'awgBufferSize');
N= awgBufferSize;   % No. of points in trace

%% Define pulse parameters

pulse.envelope= 'hann';
pulse.shape= 'sine';
pulse.f0 = 1e6;
pulse.Nc = 1.0;

T = pulse.Nc/pulse.f0;
dt= T/N;
pulse.fs = 1/dt;
pulse= MakePulse(pulse, 1);
y=pulse.v;

v0=0;
vpp=2e3;
set(sigGenGroupObj, 'startFrequency', 1/T);
set(sigGenGroupObj, 'stopFrequency',  1/T);
set(sigGenGroupObj, 'offsetVoltage', v0);
set(sigGenGroupObj, 'peakToPeakVoltage', vpp);


%% Arbitrary waveform generator - output shots
%triggerType 		= ps5000aEnuminfo.enPS5000ASigGenTrigType.PS5000A_SIGGEN_RISING;
triggerSource 		= ps5000aEnuminfo.enPS5000ASigGenTrigSource.PS5000A_SIGGEN_SCOPE_TRIG;
%triggerSource 		= ps5000aEnuminfo.enPS5000ASigGenTrigSource.PS5000A_SIGGEN_SOFT_TRIG;
extInThresholdMv 	= 0;

[status.setSigGenArbitrary] = invoke(sigGenGroupObj, 'setSigGenArbitrary', 0, 0, y, 0, ...
										0, 0, 1, 0, 0, triggerSource, extInThresholdMv);

% Trigger the AWG

% State : 1 (a non-zero value will trigger the output)
pul[status.sigGenSoftwareControl] = invoke(sigGenGroupObj, 'ps5000aSigGenSoftwareControl', 1);



keyboard


%% Disconnect device
% Disconnect device object from hardware.

disconnect(ps5000aDeviceObj);
delete(ps5000aDeviceObj);
