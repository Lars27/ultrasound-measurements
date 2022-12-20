function Picoscope5000a_SetChannel(ps5000aDeviceObj,ch)
% function ADCresolution = Picoscope5000a_SetChannel(ps5000aDeviceObj,ch)
%
% Configure acquisition channel of Picoscope 5000 ADC 
% 
% Input
%   ps5000aDeviceObj : Picoscope ddevice object defined in Matlab's
%                      Instrument Control Toolbox
%                ch  : Channel configureation as struct
%                      Fields
%                            no : Channel no (0 ... 3)
%                       enabled : Channel enabled for acquisition
%                      coupling : Channel coupling. 0: AC, 1: DC
%                         range : Vertical (voltage) range no.
%                        offset : Offset voltage [V]

% Adapted from examples given by Pico Technology
% Lars Hoff, USN, Nov 2020

[status.setChC] = invoke(ps5000aDeviceObj, 'ps5000aSetChannel', ch.no, ...
                           ch.enabled, ch.coupling, ch.range, ch.offset);

end

