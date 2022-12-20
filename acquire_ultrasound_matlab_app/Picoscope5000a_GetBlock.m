function wfm= Picoscope5000a_GetBlock(blockGroupObj,DSO)
% function wfm= Picoscope5000a_GetBlock(ps5000aDeviceObj,DSO)
%
% Read data from Picoscope 5000, as specified in struct DSO
%
% Input
%   ps5000aDeviceObj : Picoscope ddevice object defined in Matlab's
%                      Instrument Control Toolbox
%                DSO : nConfiguration of the Picoscope 5000 digital storage oscilloscope
% Output
%        wfm : All data read from oscilloscope organized in struct.
%              Data oganized as in previous programs written in LabVIEW 
%              Fields          
%          header [string]: Short text identifying measurement type
%                N: [dbl] : Number of data channels 
%               t0: [dbl] : Start time of measurement, seconds following LabVIEW's standard
%               dt: [dbl] : Sample interval [s]
%              dtr: [dbl] : Not used in this configuration, otherwise interval between records
%                v: [dbl] : Recorded data values, as scaled by recording program
%               Np: [dbl] : No. of sample points per channel
%               overflow  : ADC saturation occured, 

% Adapted from examples given by Pico Technology
% Lars Hoff, USN, Nov 2020

%% 
% Configure and read data block
% blockGroupObj = get(ps5000aDeviceObj, 'Block');
% blockGroupObj = blockGroupObj(1);

[status.runBlock] = invoke(blockGroupObj, 'runBlock', 0);
[N, overflow, chA, chB] = invoke(blockGroupObj, 'getBlockData', 0, 0, 1, 0);

% Organize results in satruct 'wfm'
wfm.header= 'Traces from Picoscope 5000-series. Matlab Instrument Control TB';
wfm.N  = 2;
wfm.dt = DSO.horiz.dt;
wfm.dtr= [];
wfm.t0 = DSO.horiz.t0;
wfm.v  = [chA chB]*1e-3;
wfm.Np = double(N);
wfm.overflow=overflow;

end

