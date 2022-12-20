function status=Picoscope5000a_ConfigureAWG(Device,AWG)
%function status=Picoscope5000a_ConfigureAWG(Device,AWG)
%
% Configure arbitrary waveform generator of Picoscope 5000a
% Based on PS5000A_ID_Sig_Gen_Example from Pico Technology 
%
%  Device : Signal generator object of PicoScpoe 5000
%  AWG  : Configuration of arbitrary waveform generator
%         Fields
%           T   : Pulse duration [s]
%           Vpp : Voltage peak-to-peak [V]
%           v   : Pulse shape (voltage) scaled -1 to +1
%           TriggerSource : Trigger sourde for AWG, see documentation for
%                           description

% Adapted from examples given by Pico Technology
% Lars Hoff, USN, Nov 2020

%%

AWGObj = get(Device, 'Signalgenerator');
AWGObj = AWGObj(1);

f= 1/AWG.T;   % 'Frequency' is in this definition the duration of the pulse

if AWG.Transmit
    set(AWGObj, 'startFrequency', f );
    set(AWGObj, 'stopFrequency',  f );
    set(AWGObj, 'offsetVoltage',  0 );
    set(AWGObj, 'peakToPeakVoltage', AWG.Vpp*1e3);    
    status = invoke(AWGObj, 'setSigGenArbitrary', 0, 0, AWG.v, 0, 0, 0, 1, 0, 0, AWG.TriggerSource, 0);
else
    invoke(AWGObj, 'setSigGenOff');
end

end   