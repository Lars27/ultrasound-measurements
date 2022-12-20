function Hscale=Picoscope5000a_SetTimebase(ps5000aDeviceObj,Hscale)
% function DSO=Picoscope5000a_SetTimebase(ps5000aDeviceObj,Hscale)
%
% Find and configure sample rate of Picoscope 5000 ADC 
% 
% Input
%   ps5000aDeviceObj : Picoscope ddevice object defined in Matlab's
%                      Instrument Control Toolbox
%            Hscale  : Oscilloscope horizontal scale as struct
%                      Fields
%                       fs  : Requested sample rate [S/s]
% Output
%            Hscale  : Struct DSO updated with actual settings
%                      Fields
%                        fs : Actual sample rate [S/s]
%                        dt : Actual sample interval [s]
%                  timebase : Timebase no. corresponding to actual fs
%
% See documentation in "PicoScope® 5000 Series Programmer's Guide" under
% "Timebase"

% Adapted from examples given by Pico Technology
% Lars Hoff, USN, Nov 2020

%%
% Find timebase with sample rate equal or greater than requested fs
fs0=125e6;
dtmax=1/Hscale.fs;
n= floor(dtmax*fs0)+2;

if n<3   % Values fixed for 2 channels at 15 bit resolution
    warndlg('Requested sample rate too high', 'Sample Rate')
    n=3;
end
dt=(n-2)/fs0;


% Update struct and configure instrument
Hscale.dt= dt;
Hscale.fs= 1/dt;
Hscale.timebase= n;

set(ps5000aDeviceObj, 'timebase', Hscale.timebase);

end

