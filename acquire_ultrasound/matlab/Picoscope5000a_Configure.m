function ps5000aDeviceObj = Picoscope5000a_Configure(ps5000aDeviceObj)
% function ps5000aDeviceObj = Picoscope5000a_Configure(ps5000aDeviceObj)
% 
% Configure and connect Picoscope 5000a
% Based on PS5000A_ID_Block_Example from Pico Technology 
%
%   ps5000aDeviceObj : Picoscope ddevice object defined in Matlab's
%                      Instrument Control Toolbox
%

% Adapted from examples given by Pico Technology
% Lars Hoff, USN, Nov 2020


PS5000aConfig;  % Load configuration information

% Disconnect if an Instrument session using |ps5000aDeviceObj| is still open
if (exist('ps5000aDeviceObj', 'var') && ps5000aDeviceObj.isvalid && strcmp(ps5000aDeviceObj.status, 'open'))
        disconnect(ps5000aDeviceObj);
        delete(ps5000aDeviceObj);       
end

% Create a device object. 
disp('Finding ...')
ps5000aDeviceObj = icdevice('picotech_ps5000a_generic', ''); 

% Connect device object to hardware.
disp('Connecting ...')
connect(ps5000aDeviceObj);
disp('connected')

end

