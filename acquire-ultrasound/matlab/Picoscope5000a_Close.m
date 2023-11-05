function ps5000aDeviceObj=Picoscope5000a_Close(ps5000aDeviceObj)
%function Picoscope5000a_Close(ps5000aDeviceObj)
% 
% Disconnect and delete connection to Picoscope 5000a
% Based on PS5000A_ID_Block_Example from Pico Technology 
%
%   ps5000aDeviceObj : Picoscope ddevice object defined in Matlab's
%                      Instrument Control Toolbox

% Adapted from examples given by Pico Technology
% Lars Hoff, USN, Nov 2020


if (ps5000aDeviceObj.isvalid && strcmp(ps5000aDeviceObj.status, 'open'))   
        disconnect(ps5000aDeviceObj);
        delete(ps5000aDeviceObj);
end

