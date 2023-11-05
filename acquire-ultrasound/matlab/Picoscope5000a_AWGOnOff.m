function Picoscope5000a_AWGOnOff(Device,on)
% function Picoscope5000a_AWGOnOff(Device,on)
%
% Turn Picoscope 5000a arbitrary waveform on or off
%
%  Device : Signal generator object of PicoScope 5000
%      on : Turn generator on (True) or off (False)

% Adapted from examples given by Pico Technology
% Lars Hoff, USN, Nov 2020

%%

AWGObj= get(Device, 'Signalgenerator');
AWGObj= AWGObj(1);

if on, invoke(AWGObj, 'setSigGenOn');
else,  invoke(AWGObj, 'setSigGenOff');
end

end   