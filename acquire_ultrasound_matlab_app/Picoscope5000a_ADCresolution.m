function ADCresolution = Picoscope5000a_ADCresolution(ps5000aDeviceObj,nbits)
% function ADCresolution = Picoscope5000a_ADCresolution(ps5000aDeviceObj,nbits)
%
% Set resolution of Picoscope 5000 ADC in bits
% See Picoscope documentation for allowed values
%
%   ps5000aDeviceObj : Picoscope ddevice object defined in Matlab's
%                      Instrument Control Toolbox
%   nbits            : ADC resolution in bits. Normally set to 15, see 
%                      Picoscope documentation for allowed values 
%

% Adapted from examples given by Pico Technology
% Lars Hoff, USN, Nov 2020

[status.setResolution, ADCresolution] = invoke(ps5000aDeviceObj, 'ps5000aSetDeviceResolution', nbits);

end

