function Vrange= Picoscope5000a_FindVrange(V,PS5000ARanges)
% function Vrange= Picoscope5000a_FindVrange(V,PS5000ARanges)
%
% Identify Find voltage scale of Picoscope 5000 ADC covering requested voltage span
%
%             V : Max. input voltage
% PS5000ARanges : Voltage ranges defined by PicoScope.
%                 See Picoscope documentation for definition

% Adapted from examples given by Pico Technology
% Lars Hoff, USN, Nov 2020
%

% Adapted from examples given by Pico Technology
% Lars Hoff, USN, Nov 2020

Vranges = Picoscope5000a_GetVranges(PS5000ARanges);
k=find([Vranges.v]>=V, 1);

Vrange=Vranges(k);

end

